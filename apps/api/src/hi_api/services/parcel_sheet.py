"""The sheet of one parcel of Madrid capital for whoever builds (D-250).

1. The parcel's reference: given (`rc`), at a point (`lat`, `lon`: the Catastro) or at an address
   (`address`: CartoCiudad, and the Catastro's street index when it fails). An address that
   matches several portals is never picked: 422 AMBIGUOUS_INPUT with the candidates.
2. The parcel (Catastro) and its planning (Ayuntamiento), from the cache or the services; the
   official buildable m² of the parcel (VEDA, Portal del Suelo) from hi_domain.parcel_data.
3. The buildability the calculator starts from (hi_domain.parcels), always editable.
4. The barrio (PostGIS, read only): a pilot barrio brings its whole investor sheet (D-248);
   outside the pilot, its district's figures, and it says so.

A failed Ayuntamiento leaves the sheet without planning (`degraded`); a failed Catastro serves
the saved demo sheet when the parcel is one of the four, otherwise 503. With PARCEL_UPSTREAMS
off (offline demo, e2e), only the demo parcels are served, from their saved sheets. The address
typed is never logged nor kept: only the reference, the kind of input and the times.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field, replace
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, NamedTuple

from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, HttpUrl
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from hi_api.services.gaps import zone_ref
from hi_api.services.investors import (
    DistrictPlace,
    Place,
    offline_defaults,
    pilot_codes,
    place_sheet,
)
from hi_api.services.parcels import (
    MALFORMED_CODES,
    MISSING_CODES,
    ON_THE_STREET,
    SHAPE_ERRORS,
    SIGMA,
    Candidates,
    CatastroAnswerError,
    CatastroParcel,
    ClientHolder,
    OutOfMadridError,
    PlanningRecord,
    UpstreamError,
    fetch_parcel,
    fetch_planning,
    geocode,
    parcel_at,
    parcels_at_number,
    parcels_near,
    repairable,
    to_lonlat,
    to_metres,
)
from hi_api.services.upstream_guard import MISSING, TTLCache, UpstreamGuard
from hi_api.settings import ApiSettings
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.pro.investors import (
    AmbitPhase,
    AmbitStatus,
    Buildability,
    BuildabilityKind,
    DegradedPart,
    LandItem,
    NormaZonal,
    ParcelBlock,
    ParcelCandidate,
    ParcelCaution,
    ParcelCautionKey,
    ParcelContext,
    ParcelInput,
    ParcelSheet,
    ParcelSource,
    ParcelUnits,
    PlanningBlock,
    PlanningInstrument,
    PlanUseFigure,
    PowerEstimate,
    ProtectedBuilding,
    UnitUse,
    UseFigure,
)
from hi_contracts.public import ZoneRef
from hi_domain import ambit_status
from hi_domain import parcel_data as pd
from hi_domain import viability as v
from hi_domain.parcels import (
    LOOKUP_BUDGET_S,
    PHASE_LABELS,
    PLAN_USES_AS_OF,
    AmbitState,
    CatalogEntry,
    ExistingBuilding,
    OfficialFigure,
    ambit_state,
    classify_planning,
    classify_use,
    in_madrid_bbox,
    initial_buildability,
    normalize_rc,
    parcel_cautions,
    parse_address,
    plan_use,
    same_street,
    street_address,
    typed_number,
)
from hi_domain.supplies import power_estimate
from hi_domain.zonal_norms import NNUU_CITATION, RULES

log = logging.getLogger(__name__)

DAY_S = 86_400
# The whole lookup: past it, the Catastro counts as failed and the planning as not read (R-06)
BUDGET_S = LOOKUP_BUDGET_S
TTL_S = {"catastro": 7 * DAY_S, "planning": DAY_S, "geocoder": 30 * DAY_S, "point": 7 * DAY_S}
CACHE = TTLCache(maxsize=2000)
CLIENTS = ClientHolder()
DEMO_PATH = Path(__file__).with_name("parcel_demo.json")

PLANNING_NOTICE = (
    "Información urbanística sin valor jurídico (Ayuntamiento de Madrid). "
    "Consulte la ficha oficial."
)
PARCEL_NOTICES = (
    PLANNING_NOTICE,
    "Los datos de la parcela los elabora Vida Fácil a partir de los de la Dirección General del "
    "Catastro: para cualquier trámite, consulta la Sede Electrónica del Catastro.",
    "Una edificabilidad «supuesta» aplica la norma a la superficie del Catastro: no es la de un "
    "proyecto ni la de una licencia. Compruébala en la ficha oficial.",
    *v.NOTICES,
)
OUTSIDE_PILOT = (
    "Este barrio está fuera del piloto (Madrid capital dentro de la M-40): las cifras son del "
    "distrito de {district} o de toda la ciudad."
)
VIEWER = (
    "https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/visor_ide.iam?ArcGIS="
    f"{SIGMA}/DESARROLLO_URBANO_ACTUALIZADO/USOS_SUELO/MapServer"
    "&center={lon},{lat}&level=18&marker={lon},{lat}"
)
CC_BY = "Creative Commons Reconocimiento 4.0 (CC BY 4.0)"
CC_BY_URL = HttpUrl("https://creativecommons.org/licenses/by/4.0/legalcode.es")


def es_date(day: date) -> str:
    return day.strftime("%d/%m/%Y")


def catastro_source(day: date) -> ParcelSource:
    return ParcelSource(
        source_id="catastro_ovc",
        name="Sede Electrónica del Catastro: servicios web libres",
        publisher="Dirección General del Catastro",
        license="Licencia de acceso y uso de los servicios y conjuntos de datos INSPIRE de la "
        "DGC (v1.0, julio 2016): uso, también comercial, de la información transformada",
        license_url=HttpUrl(
            "https://www.catastro.hacienda.gob.es/webinspire/documentos/Licencia.pdf"
        ),
        attribution="Elaborado por Vida Fácil a partir de datos de la Dirección General del "
        f"Catastro (Sede Electrónica del Catastro), consultados el {es_date(day)}.",
        url=HttpUrl("https://www.sedecatastro.gob.es/"),
        accessed_at=day,
    )


def planning_source(day: date) -> ParcelSource:
    return ParcelSource(
        source_id="ayuntamiento_madrid_urbanismo_sigma",
        name="Urbanismo. Destino urbanístico del suelo, y Planeamiento y desarrollos del PGOUM",
        publisher="Ayuntamiento de Madrid (Área de Urbanismo)",
        license=CC_BY,
        license_url=CC_BY_URL,
        attribution="Origen de los datos: Ayuntamiento de Madrid (Área de Urbanismo; Geoportal y "
        f"datos.madrid.es), CC BY 4.0. Consultado el {es_date(day)}. Información urbanística sin "
        "valor jurídico.",
        url=HttpUrl("https://datos.madrid.es/dataset/300744-0-usos-suelo-urbanismo"),
        accessed_at=day,
    )


AMBITS_SOURCE = ParcelSource(
    source_id="ayto_pgoum_desarrollo_ambitos",
    name="PGOUM 97. Estado de desarrollo de los ámbitos, y edificabilidad remanente en ámbitos",
    publisher="Ayuntamiento de Madrid (Área de Urbanismo)",
    license=CC_BY,
    license_url=CC_BY_URL,
    attribution="Origen de los datos: Ayuntamiento de Madrid (datos.madrid.es), CC BY 4.0. Estado "
    f"de desarrollo a {es_date(date.fromisoformat(ambit_status.AS_OF))}.",
    url=HttpUrl("https://datos.madrid.es/dataset/203200-0-desarrollo-ambitos"),
    accessed_at=date.fromisoformat(ambit_status.AS_OF),
)


CATALOG_SOURCE = ParcelSource(
    source_id="ayto_edificios_protegidos",
    name="Catálogo de edificios protegidos",
    publisher="Ayuntamiento de Madrid (Dirección General de Planeamiento)",
    license=CC_BY,
    license_url=CC_BY_URL,
    attribution="Origen de los datos: Ayuntamiento de Madrid (datos.madrid.es), CC BY 4.0. "
    "Catálogo de edificios protegidos, en el punto de la parcela.",
    url=HttpUrl("https://datos.madrid.es/dataset/300158-0-edificios-protegidos"),
)


GEOCODER_SOURCE = ParcelSource(
    source_id="ign_cartociudad",
    name="CartoCiudad (geocodificación de direcciones)",
    publisher="Instituto Geográfico Nacional (IGN)",
    license="CC BY 4.0 scne.es",
    license_url=HttpUrl("https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf"),
    attribution="Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), "
    "CC BY 4.0 scne.es.",
    url=HttpUrl("https://www.cartociudad.es/"),
)
OFFICIAL_SOURCES = {
    pd.VEDA_DATASET: ParcelSource(
        source_id="ayuntamiento_madrid_ckan",
        name="VEDA Madrid: parcelas con edificabilidad (julio de 2026)",
        publisher="Ayuntamiento de Madrid (Departamento de Análisis Urbano)",
        license=CC_BY,
        license_url=CC_BY_URL,
        attribution="Origen de los datos: Ayuntamiento de Madrid (Visor de Edificabilidad VEDA, "
        "julio de 2026), CC BY 4.0.",
        url=HttpUrl("https://datos.madrid.es/dataset/203182-0-ambitos-remanente"),
        accessed_at=date.fromisoformat(pd.VEDA_CONSULTED),
    ),
    pd.PORTAL_DATASET: ParcelSource(
        source_id="comunidad_madrid_ckan",
        name="Parcelas publicadas en el Portal del Suelo 4.0",
        publisher="Comunidad de Madrid (Dirección General de Suelo)",
        license=CC_BY,
        license_url=CC_BY_URL,
        attribution="Fuente: Comunidad de Madrid — Portal de Datos Abiertos "
        "(datos.comunidad.madrid), CC BY 4.0.",
        url=HttpUrl("https://datos.comunidad.madrid/dataset/parcelas_portal_suelo"),
        accessed_at=date.fromisoformat(pd.PORTAL_CONSULTED),
    ),
}


def norms_source(buildability: Buildability) -> ParcelSource:
    return ParcelSource(
        source_id="ayuntamiento_madrid_nnuu",
        name="Normas Urbanísticas del Plan General de Ordenación Urbana de Madrid de 1997",
        publisher="Ayuntamiento de Madrid (Dirección General de Planeamiento)",
        license="Texto normativo oficial",
        attribution=f"{NNUU_CITATION}, art. {buildability.article}.",
        url=buildability.article_url,
    )


# --- Errors, settings and the guard ---


class ParcelLookupError(Exception):
    """A lookup that ends in an HTTP error with our error code."""

    def __init__(
        self,
        status: int,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


@lru_cache(maxsize=1)
def settings() -> ApiSettings:
    return ApiSettings()


@lru_cache(maxsize=1)
def guards() -> tuple[UpstreamGuard, UpstreamGuard]:
    """Per IP and minute: lookups that call the Catastro or the Ayuntamiento, and CartoCiudad."""
    s = settings()
    return UpstreamGuard(s.parcel_guard_per_minute), UpstreamGuard(s.geocoder_guard_per_minute)


@dataclass
class Lookup:
    """One request: who asks (for the guard) and what it spent, counted once per service."""

    ip: str
    spent: set[str] = field(default_factory=set[str])
    upstream_ms: int = 0

    def spend(self, which: str = "upstream") -> None:
        if which in self.spent:
            return
        upstream, geocoder = guards()
        (geocoder if which == "geocoder" else upstream).take(self.ip)
        self.spent.add(which)


@dataclass(frozen=True)
class ParcelQuery:
    kind: ParcelInput
    rc: str | None = None
    lat: float | None = None
    lon: float | None = None
    address: str | None = None


def catastro_failure(exc: CatastroAnswerError) -> Exception:
    """The HTTP error of a Catastro code; a code we do not expect is the service failing."""
    if exc.code in MALFORMED_CODES:
        return ParcelLookupError(
            422, ErrorCode.OUT_OF_COVERAGE, "The cadastral reference is not well formed"
        )
    if exc.code in MISSING_CODES:
        return ParcelLookupError(404, ErrorCode.NOT_FOUND, "No parcel with that reference")
    return UpstreamError("catastro", f"code {exc.code}")


async def timed(lookup: Lookup, awaitable: Any) -> Any:
    started = time.perf_counter()
    try:
        return await awaitable
    finally:
        lookup.upstream_ms += round((time.perf_counter() - started) * 1000)


# --- 1. The reference ---


def checked_rc(raw: str) -> str:
    try:
        return normalize_rc(raw)
    except ValueError as exc:
        raise ParcelLookupError(
            422,
            ErrorCode.OUT_OF_COVERAGE,
            "A cadastral reference has 14, 18 or 20 letters and digits",
        ) from exc


_IN_MADRID = text(
    """
    SELECT EXISTS (
      SELECT 1 FROM geo_admin_unit
       WHERE level = 'municipio' AND code_official = '28079'
         AND ST_Contains(geom_25830, ST_SetSRID(ST_MakePoint(:x, :y), 25830)))
    """
)


def point_in_madrid(engine: Engine, x: float, y: float) -> bool | None:
    """Whether the point is in the municipio of Madrid; None when the database cannot say."""
    try:
        with engine.connect() as conn:
            return bool(conn.execute(_IN_MADRID, {"x": x, "y": y}).scalar())
    except (SQLAlchemyError, OSError):
        return None


OUT_OF_MADRID = ParcelLookupError(
    422, ErrorCode.OUT_OF_COVERAGE, "The parcel search covers Madrid capital only"
)


async def rc_at_point(lat: float, lon: float, lookup: Lookup, engine: Engine) -> str:
    if not in_madrid_bbox(lat, lon):
        raise OUT_OF_MADRID
    x, y = to_metres(lon, lat)
    if await run_in_threadpool(point_in_madrid, engine, x, y) is False:
        raise OUT_OF_MADRID
    key = ("point", round(lat, 5), round(lon, 5))
    if (cached := CACHE.get(key)) is not MISSING:
        return cached
    lookup.spend()
    client = CLIENTS.get()
    try:
        rc14 = await timed(lookup, parcel_at(client, lat, lon))
    except CatastroAnswerError as exc:
        if exc.code != ON_THE_STREET:
            raise catastro_failure(exc) from exc
        try:
            nearest = await timed(lookup, parcels_near(client, lat, lon))
        except (UpstreamError, CatastroAnswerError):
            nearest = []
        raise ParcelLookupError(
            404,
            ErrorCode.NOT_FOUND,
            "No parcel at that point: it falls on the street",
            {"nearest": [n.model_dump(mode="json") for n in nearest]},
        ) from exc
    CACHE.set(key, rc14, TTL_S["point"])
    return rc14


def query_key(query: str) -> str:
    return " ".join(query.lower().split())


def geocoder_key(query: str) -> tuple[str, str]:
    """The cache key of a typed address: a hash of the normalised text, never the text itself."""
    return ("geocoder", hashlib.sha256(query_key(query).encode()).hexdigest()[:24])


async def address_candidates(query: str, lookup: Lookup) -> Candidates:
    """CartoCiudad's portals for a typed address (cached); UpstreamError when it fails, and then
    nothing is cached («no portals» is never a failure's answer)."""
    key = geocoder_key(query)
    if (cached := CACHE.get(key)) is not MISSING:
        return cached
    lookup.spend("geocoder")
    found = await timed(lookup, geocode(CLIENTS.get(), query_key(query)))
    CACHE.set(key, found, TTL_S["geocoder"])
    return found


def ambiguous(candidates: list[ParcelCandidate], message: str) -> ParcelLookupError:
    return ParcelLookupError(
        422,
        ErrorCode.AMBIGUOUS_INPUT,
        message,
        {"candidates": [c.model_dump(mode="json") for c in candidates]},
    )


async def rc_at_address(address: str, lookup: Lookup) -> str:
    try:
        found = await address_candidates(address, lookup)
    except UpstreamError:
        return await rc_by_street_index(address, lookup)
    number = typed_number(address)
    if len(found.portals) == 1:
        only = found.portals[0]
        if number and only.number == number and same_street(address, only.candidate.address):
            return only.candidate.rc14
    if not found.portals:
        raise ParcelLookupError(
            404,
            ErrorCode.NOT_FOUND,
            "No portal of Madrid capital matches the address",
            {"needs_number": found.streets_only},
        )
    portals = [c.candidate for c in found.portals]
    raise ambiguous(portals, "The address matches several portals: pick one")


async def rc_by_street_index(address: str, lookup: Lookup) -> str:
    """CartoCiudad failed: the Catastro's street index, with the street type, name and number."""
    parsed = parse_address(address)
    if parsed is None:
        raise ambiguous([], "Write the street type, its name and the number")
    lookup.spend()
    try:
        found = await timed(lookup, parcels_at_number(CLIENTS.get(), parsed))
    except CatastroAnswerError as exc:
        raise catastro_failure(exc) from exc
    if len(found) == 1:
        return found[0]
    if not found:
        raise ParcelLookupError(404, ErrorCode.NOT_FOUND, "No parcel at that number")
    label = street_address(parsed.street_type, parsed.street, str(parsed.number), None) or ""
    raise ambiguous(
        [ParcelCandidate(address=label, rc14=rc) for rc in found],
        "The number has several parcels: pick one",
    )


async def resolve(query: ParcelQuery, lookup: Lookup, engine: Engine) -> str:
    if query.kind is ParcelInput.RC and query.rc is not None:
        return checked_rc(query.rc)
    if query.kind is ParcelInput.POINT and query.lat is not None and query.lon is not None:
        return await rc_at_point(query.lat, query.lon, lookup, engine)
    if query.kind is ParcelInput.ADDRESS and query.address is not None:
        return await rc_at_address(query.address, lookup)
    raise ParcelLookupError(422, ErrorCode.OUT_OF_COVERAGE, "Nothing to look up")


# --- 2. The parcel and its planning ---


async def catastro_parcel(rc14: str, lookup: Lookup) -> CatastroParcel:
    key = ("catastro", rc14)
    if (cached := CACHE.get(key)) is not MISSING:
        return cached
    lookup.spend()
    try:
        parcel = await timed(lookup, fetch_parcel(CLIENTS.get(), rc14))
    except CatastroAnswerError as exc:
        raise catastro_failure(exc) from exc
    except OutOfMadridError as exc:
        raise OUT_OF_MADRID from exc
    if parcel.x is not None and parcel.y is not None:  # without its point, asked again next time
        CACHE.set(key, parcel, TTL_S["catastro"])
    return parcel


async def planning_record(
    parcel: CatastroParcel, lookup: Lookup, deadline: float | None = None
) -> PlanningRecord | None:
    """The planning at the parcel's point; UpstreamError when the Ayuntamiento fails. Kept by
    parts (D-252b): a record with a secondary part failed is kept too, and the next lookup asks
    only that part again. Nothing incomplete reaches the CDN (the route's Cache-Control)."""
    if parcel.x is None or parcel.y is None:
        return None
    key = ("planning", parcel.rc14)
    cached = CACHE.get(key)
    if cached is not MISSING and (cached is None or cached.complete):
        return cached if cached is None else replace(cached, timings=())  # nothing asked now
    # A kept record is repaired by parts; one that cannot be (no UBOV_ID) is asked again whole
    base = None if cached is MISSING or not repairable(cached) else cached
    lookup.spend()
    record = await timed(
        lookup,
        fetch_planning(CLIENTS.get(), parcel.x, parcel.y, deadline, base=base),
    )
    # A full answer gets a fresh TTL; a repair still incomplete keeps the kept one's expiry
    if base is None or record is None or record.complete or not CACHE.update(key, record):
        CACHE.set(key, record, TTL_S["planning"])
    return record


def parcel_block(parcel: CatastroParcel) -> ParcelBlock:
    lon, lat = to_lonlat(parcel.x, parcel.y) if parcel.x and parcel.y else (None, None)
    units = parcel.units
    return ParcelBlock(
        rc14=parcel.rc14,
        address=parcel.address,
        postal_code=parcel.postal_code,
        lat=lat,
        lon=lon,
        area_m2=parcel.area_m2,
        rustic=parcel.rustic,
        is_vacant=parcel.is_vacant,
        horizontal_division=parcel.horizontal_division,
        units=None
        if units is None
        else ParcelUnits(
            total=units.total,
            by_use=[UnitUse(use=g.use, count=g.count, built_m2=g.built_m2) for g in units.by_use],
        ),
        built_m2=parcel.built_m2,
        year_built=parcel.year_built,
        current_use=parcel.current_use,
        official_url=HttpUrl(parcel.official_url) if parcel.official_url else None,
        observed_at=parcel.observed_at,
    )


def plan_uses(record: PlanningRecord) -> list[PlanUseFigure] | None:
    """D-252: tables 4 and 5 as our figures; None when they did not answer."""
    if record.plan_rows is None:
        return None
    figures = []
    for row in record.plan_rows:
        found = plan_use(row.use, row.value, row.unit, row.principal, record.urban_parcel_area_m2)
        if found is not None:
            figures.append(
                PlanUseFigure(
                    use=found.use,
                    use_class=found.use_class,
                    use_ownership=found.use_ownership,
                    principal=found.principal,
                    value_m2=found.value_m2,
                    coefficient=found.coefficient,
                    assumed=found.assumed,
                )
            )
    return figures


def ambit_block(state: AmbitState | None) -> AmbitStatus | None:
    if state is None:
        return None
    phases = [] if state.phases is None else list(zip(PHASE_LABELS, state.phases, strict=True))
    return AmbitStatus(
        code=state.code,
        tracked=state.tracked,
        pending=state.pending,
        phases=[AmbitPhase(label=label, state=phase) for label, phase in phases],
        veda_stage=state.veda_stage,  # pyright: ignore[reportArgumentType]
        as_of=date.fromisoformat(ambit_status.AS_OF),
        url=HttpUrl(ambit_status.DEVELOPMENT_URL),
    )


def protected_building(record: PlanningRecord) -> ProtectedBuilding | None:
    """D-253: the catalogued building at the parcel's point, with its level (NNUU art. 4.3.4)."""
    row = record.catalog
    if row is None:
        return None
    entry = CatalogEntry(row.number, row.name, row.protection, row.url)
    return ProtectedBuilding(
        number=row.number,
        name=row.name,
        protection=row.protection,
        level=entry.level,
        url=HttpUrl(row.url) if row.url else None,
    )


def planning_block(record: PlanningRecord, lat: float, lon: float) -> PlanningBlock:
    kind, zone = classify_planning(record.code)
    sheet_url, sheet_label = None, None
    if record.instrument_url:
        sheet_url = record.instrument_url
        sheet_label = f"Ficha del expediente {record.figure or ''}".strip()
    elif zone is not None:
        article = RULES[zone.nz].article
        sheet_url = article.url
        sheet_label = f"Artículo {article.number} de las Normas Urbanísticas"
    has_instrument = any((record.figure, record.instrument_name, record.file_number))
    use_class, use_ownership = classify_use(record.use)
    return PlanningBlock(
        code=record.code,
        name=record.name,
        kind=kind,
        norma_zonal=None
        if zone is None
        else NormaZonal(nz=zone.nz, grado=zone.grado, nivel=zone.nivel, name=RULES[zone.nz].name),
        use=record.use,
        use_class=use_class,
        use_ownership=use_ownership,
        urban_parcel=" · ".join(p for p in (record.urban_parcel, record.zone_name) if p) or None,
        urban_parcel_area_m2=record.urban_parcel_area_m2,
        plan_uses=plan_uses(record),
        plan_uses_as_of=date.fromisoformat(PLAN_USES_AS_OF),
        plan_use_without_figure=record.use_without_figure,
        ambit=ambit_block(ambit_state(record.code)),
        protected_building=protected_building(record),
        instrument=PlanningInstrument(
            figure=record.figure,
            name=record.instrument_name,
            file_number=record.file_number,
            url=HttpUrl(record.instrument_url) if record.instrument_url else None,
        )
        if has_instrument
        else None,
        sheet_url=HttpUrl(sheet_url) if sheet_url else None,
        sheet_label=sheet_label,
        viewer_url=HttpUrl(VIEWER.format(lon=lon, lat=lat)),
        notice=PLANNING_NOTICE,
        observed_at=record.observed_at,
    )


def official_figures(rc14: str) -> list[OfficialFigure]:
    figures = []
    if (veda := pd.VEDA_PARCELS.get(rc14)) is not None:
        figures.append(OfficialFigure(veda[0], pd.VEDA_SOURCE, pd.VEDA_DATASET, veda[3]))
    if (portal := pd.PORTAL_PARCELS.get(rc14)) is not None:
        figures.append(OfficialFigure(portal[0], pd.PORTAL_SOURCE, pd.PORTAL_DATASET, portal[3]))
    return figures


def buildability(
    rc14: str, parcel: ParcelBlock, planning: PlanningBlock | None, coef_z: float | None
) -> Buildability:
    result = initial_buildability(
        area_m2=parcel.area_m2,
        planning_code=None if planning is None else planning.code,
        use=None if planning is None else planning.use,
        rustic=parcel.rustic,
        official=official_figures(rc14),
        coef_z=coef_z,
        ambit=None if planning is None else ambit_state(planning.code),
    )
    return Buildability(
        value_m2=result.value_m2,
        kind=result.kind,
        source=result.source,
        article=result.article,
        article_url=HttpUrl(result.article_url) if result.article_url else None,
        coefficient=result.coefficient,
        formula=result.formula,
        note=result.note,
        assumed_m2=result.assumed_m2,
        dataset_ids=list(result.dataset_ids),
        by_use=[
            UseFigure(
                use_class=f.use_class,
                use=f.use,
                value_m2=f.value_m2,
                source=f.source,
                dataset_id=f.dataset_id,
                residential=f.residential,
            )
            for f in result.by_use
        ],
    )


class Parts(NamedTuple):
    """What the sheet says of the parcel itself: live or from the saved demo sheet."""

    parcel: ParcelBlock
    planning: PlanningBlock | None
    buildability: Buildability
    degraded: list[DegradedPart]
    # D-252b: «stage:ErrorClass:ms» of each part that failed, for the logs (no address, no point)
    failures: tuple[str, ...] = ()
    # D-252c: «stage:ms» of every stage, failed or not (catastro, planning and its layers)
    stages: tuple[str, ...] = ()


async def live_parts(rc14: str, lookup: Lookup, deadline: float | None = None) -> Parts:
    """The parcel (the Catastro) and its planning (the Ayuntamiento), within the deadline: a
    Catastro out of time is UpstreamError (demo sheet or 503); an Ayuntamiento out of time, or
    one of its layers failing, degrades the sheet."""
    started = time.perf_counter()
    try:
        async with asyncio.timeout_at(deadline):
            parcel = await catastro_parcel(rc14, lookup)
    except TimeoutError as exc:
        raise UpstreamError("catastro", "out of the time budget") from exc
    stages = [f"catastro:{round((time.perf_counter() - started) * 1000)}"]
    try:
        block = parcel_block(parcel)
    except SHAPE_ERRORS as exc:  # a coordinate or link out of the contract
        raise UpstreamError("catastro", f"unexpected answer ({type(exc).__name__})") from exc
    degraded: list[DegradedPart] = []
    failures: list[str] = []
    started = time.perf_counter()
    try:
        async with asyncio.timeout_at(deadline):
            record = await planning_record(parcel, lookup, deadline)
    except (UpstreamError, TimeoutError) as exc:
        record = None
        degraded.append("planning")
        # Review of #111, R-03: the deadline running out says TimeoutError, not its CancelledError
        cause = exc if isinstance(exc, TimeoutError) else (exc.__cause__ or exc)
        ms = round((time.perf_counter() - started) * 1000)
        failures.append(f"planning:{type(cause).__name__}:{ms}")
    stages.append(f"planning:{round((time.perf_counter() - started) * 1000)}")
    if record is not None:
        failures.extend(f"{stage}:{error}:{ms}" for stage, error, ms in record.failures)
        stages.extend(f"{stage}:{ms}" for stage, ms in record.timings)
    planning = None
    if record is not None and block.lat is not None and block.lon is not None:
        try:
            planning = planning_block(record, block.lat, block.lon)
        except SHAPE_ERRORS:
            record = None
            degraded.append("planning")
    if record is not None and record.instrument_failed:
        degraded.append("planning")
    if record is not None and record.z_failed:
        degraded.append("buildability")
    if record is not None and record.uses_failed:
        degraded.append("plan_uses")
    if record is not None and record.catalog_failed:
        degraded.append("catalog")
    coef_z = None if record is None else record.coef_z
    built = buildability(rc14, block, planning, coef_z)
    return Parts(block, planning, built, degraded, tuple(failures), tuple(stages))


# --- The demo sheets ---


class DemoParcel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parcel: ParcelBlock
    planning: PlanningBlock | None
    buildability: Buildability


class DemoSnapshot(BaseModel):
    """The four demo parcels (spike §7), already transformed: our fields, never the Catastro's
    answers. Written by scripts/parcel_demo_snapshot.py."""

    model_config = ConfigDict(extra="forbid")

    observed_at: date
    method: str
    parcels: list[DemoParcel]


@lru_cache(maxsize=1)
def demo_snapshot() -> DemoSnapshot:
    return DemoSnapshot.model_validate(json.loads(DEMO_PATH.read_text(encoding="utf-8")))


def demo_parts(rc14: str | None) -> Parts | None:
    for demo in demo_snapshot().parcels if rc14 else []:
        if demo.parcel.rc14 == rc14:
            return Parts(demo.parcel, demo.planning, demo.buildability, [])
    return None


def demo_rcs() -> list[str]:
    return [d.parcel.rc14 for d in demo_snapshot().parcels]


# --- 4. The barrio ---

_BARRIO_AT = text(
    """
    SELECT b.code_official AS code, d.code_official AS district_code
      FROM geo_admin_unit b
      JOIN geo_admin_unit d ON d.admin_unit_id = b.parent_admin_unit_id
     WHERE b.level = 'barrio' AND d.level = 'distrito'
       AND ST_Contains(b.geom_25830, ST_SetSRID(ST_MakePoint(:x, :y), 25830))
     LIMIT 1
    """
)


class Context(NamedTuple):
    barrio: ZoneRef | None
    district: ZoneRef | None
    context: ParcelContext | None
    warnings: list[str]
    data_version: str | None


def read_context(engine: Engine, x: float, y: float) -> Context:
    """The barrio and district of the point and their sheet (read only)."""
    with engine.connect() as conn:
        row = conn.execute(_BARRIO_AT, {"x": x, "y": y}).mappings().first()
        if row is None:
            return Context(None, None, None, ["OUT_OF_COVERAGE: the point is in no barrio"], None)
        barrio = zone_ref(conn, TerritoryLevel.BARRIO, row["code"])
        district = zone_ref(conn, TerritoryLevel.DISTRITO, row["district_code"])
        in_pilot = row["code"] in pilot_codes()
        kind = Place if in_pilot else DistrictPlace
        sheet, warnings, version = place_sheet(conn, kind(row["code"], row["district_code"]))
    context = ParcelContext(
        level=TerritoryLevel.BARRIO if in_pilot else TerritoryLevel.DISTRITO,
        in_pilot=in_pilot,
        note=None if in_pilot else OUTSIDE_PILOT.format(district=district.name),
        sheet=sheet,
    )
    return Context(barrio, district, context, warnings, version)


async def context_at(engine: Engine, parcel: ParcelBlock) -> Context | None:
    if parcel.lat is None or parcel.lon is None:
        return None
    x, y = to_metres(parcel.lon, parcel.lat)
    try:
        return await run_in_threadpool(read_context, engine, x, y)
    except (SQLAlchemyError, OSError) as exc:
        log.warning("parcel context: database error %s", type(exc).__name__)
        return None


# --- 5. The sheet ---


def sources_of(kind: ParcelInput, parts: Parts) -> list[ParcelSource]:
    sources = [catastro_source(parts.parcel.observed_at)]
    if parts.planning is not None:
        sources.append(planning_source(parts.planning.observed_at))
        if parts.planning.ambit is not None and parts.planning.ambit.tracked:
            sources.append(AMBITS_SOURCE)
        if "catalog" not in parts.degraded:  # review of #110, R-06: CC BY, cited when read
            sources.append(CATALOG_SOURCE)
    sources.extend(
        OFFICIAL_SOURCES[d] for d in parts.buildability.dataset_ids if d in OFFICIAL_SOURCES
    )
    if parts.buildability.article and parts.buildability.kind is not BuildabilityKind.OFICIAL:
        sources.append(norms_source(parts.buildability))
    if kind is ParcelInput.ADDRESS:
        sources.append(GEOCODER_SOURCE)
    return sources


def cautions_of(parcel: ParcelBlock, planning: PlanningBlock | None) -> list[ParcelCaution]:
    """D-252, D-253: what keeps the figures from passing for free housing ready to build."""
    use = None if planning is None else planning.use
    ambit = None if planning is None else ambit_state(planning.code)
    found = None if planning is None else planning.protected_building
    catalog = None
    if found is not None:
        url = str(found.url) if found.url else None
        catalog = CatalogEntry(found.number, found.name, found.protection, url)
    building = None
    if parcel.built_m2:
        units = parcel.units.total if parcel.horizontal_division and parcel.units else None
        building = ExistingBuilding(parcel.built_m2, parcel.year_built, units)
    return [
        ParcelCaution(key=ParcelCautionKey(key), text=text)
        for key, text in parcel_cautions(
            use, official_figures(parcel.rc14), ambit, catalog=catalog, building=building
        )
    ]


def power_of(buildability: Buildability) -> PowerEstimate | None:
    """D-253: the least power the starting buildable m² need (ITC-BT-10), an assumption."""
    found = power_estimate(buildability.value_m2)
    if found is None:
        return None
    return PowerEstimate(
        homes=found.homes,
        simultaneity=found.simultaneity,
        kw_per_home=found.kw_per_home,
        kw=found.kw,
        over_transformer_threshold=found.over_transformer_threshold,
    )


def public_land_of(rc14: str, context: ParcelContext | None) -> LandItem | None:
    """D-252: the parcel among its barrio's public land (Portal del Suelo), by its reference."""
    ref = pd.PORTAL_REFS.get(rc14)
    if ref is None or context is None:
        return None
    return next((item for item in context.sheet.land.parcels if item.code == ref), None)


def assemble(
    kind: ParcelInput, parts: Parts, context: Context | None, fallback: bool
) -> tuple[ParcelSheet, list[str], str | None]:
    degraded: list[DegradedPart] = [*parts.degraded, *([] if context else ["context"])]
    warnings = [f"SOURCE_DEGRADED: {part}" for part in degraded]
    if fallback:
        day = demo_snapshot().observed_at.isoformat()
        warnings.append(f"SOURCE_DEGRADED: served from the demo snapshot of {day}")
    if context is not None:
        warnings.extend(context.warnings)
    barrio = None if context is None else context.context
    sheet = ParcelSheet(
        input=kind,
        parcel=parts.parcel,
        planning=parts.planning,
        buildability=parts.buildability,
        barrio=None if context is None else context.barrio,
        district=None if context is None else context.district,
        context=None if context is None else context.context,
        defaults=offline_defaults() if barrio is None else barrio.sheet.defaults,
        sources=sources_of(kind, parts),
        notices=list(PARCEL_NOTICES),
        degraded=degraded,
        cautions=cautions_of(parts.parcel, parts.planning),
        power=power_of(parts.buildability),
        public_land=public_land_of(parts.parcel.rc14, barrio),
        fallback="demo_snapshot" if fallback else None,
    )
    return sheet, warnings, None if context is None else context.data_version


async def parcel_sheet(
    query: ParcelQuery, ip: str, engine: Engine
) -> tuple[ParcelSheet, list[str], str | None]:
    """The sheet; raises ParcelLookupError, RateLimitedError or UpstreamError (no demo sheet)."""
    started = time.perf_counter()
    lookup = Lookup(ip)
    rc14: str | None = None
    fallback = False
    try:
        if not settings().parcel_upstreams:  # offline: only a reference, only a demo sheet
            rc14 = checked_rc(query.rc) if query.rc is not None else None
            raise UpstreamError("catastro", "upstreams off (PARCEL_UPSTREAMS)")
        deadline = asyncio.get_running_loop().time() + BUDGET_S
        try:
            async with asyncio.timeout_at(deadline):
                rc14 = await resolve(query, lookup, engine)
        except TimeoutError as exc:
            raise UpstreamError("catastro", "out of the time budget") from exc
        parts = await live_parts(rc14, lookup, deadline)
    except Exception as exc:
        # A failed source serves the demo sheet; a client over its limit gets its 429 (R-09)
        demo = demo_parts(rc14) if isinstance(exc, UpstreamError) else None
        if demo is None:
            log.info(
                "parcel input=%s rc14=%s error=%s ms=%d",
                query.kind.value,
                rc14,
                type(exc).__name__,
                round((time.perf_counter() - started) * 1000),
            )
            raise
        parts, fallback = demo, True
    context = await context_at(engine, parts.parcel)
    sheet, warnings, version = assemble(query.kind, parts, context, fallback)
    log.info(
        "parcel input=%s rc14=%s fallback=%s degraded=%s ms=%d upstream_ms=%d parts=%s stages=%s",
        query.kind.value,
        rc14,
        fallback,
        ",".join(sheet.degraded) or "-",
        round((time.perf_counter() - started) * 1000),
        lookup.upstream_ms,
        ",".join(parts.failures) or "-",
        ",".join(parts.stages) or "-",
    )
    return sheet, warnings, version


async def candidates_for(query: str, ip: str) -> tuple[Candidates, int]:
    """The portals for the address box; UpstreamError or RateLimitedError. Logs no text."""
    if not settings().parcel_upstreams:
        raise UpstreamError("geocoder", "upstreams off (PARCEL_UPSTREAMS)")
    started = time.perf_counter()
    lookup = Lookup(ip)
    found = await address_candidates(query, lookup)
    ms = round((time.perf_counter() - started) * 1000)
    upstream = lookup.upstream_ms
    log.info("parcel candidates=%d ms=%d upstream_ms=%d", len(found.portals), ms, upstream)
    return found, ms
