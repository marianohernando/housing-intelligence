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
from dataclasses import dataclass, field
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
    to_lonlat,
    to_metres,
)
from hi_api.services.upstream_guard import MISSING, TTLCache, UpstreamGuard
from hi_api.settings import ApiSettings
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.pro.investors import (
    Buildability,
    BuildabilityKind,
    DegradedPart,
    NormaZonal,
    ParcelBlock,
    ParcelCandidate,
    ParcelContext,
    ParcelInput,
    ParcelSheet,
    ParcelSource,
    ParcelUnits,
    PlanningBlock,
    PlanningInstrument,
    UnitUse,
)
from hi_contracts.public import ZoneRef
from hi_domain import parcel_data as pd
from hi_domain import viability as v
from hi_domain.parcels import (
    OfficialFigure,
    classify_planning,
    in_madrid_bbox,
    initial_buildability,
    normalize_rc,
    parse_address,
    same_street,
    street_address,
    typed_number,
)
from hi_domain.zonal_norms import NNUU_CITATION, RULES

log = logging.getLogger(__name__)

DAY_S = 86_400
# The whole lookup: past it, the Catastro counts as failed and the planning as not read (R-06)
BUDGET_S = 15.0
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


async def planning_record(parcel: CatastroParcel, lookup: Lookup) -> PlanningRecord | None:
    """The planning at the parcel's point (cached); UpstreamError when the Ayuntamiento fails."""
    if parcel.x is None or parcel.y is None:
        return None
    key = ("planning", parcel.rc14)
    if (cached := CACHE.get(key)) is not MISSING:
        return cached
    lookup.spend()
    record = await timed(lookup, fetch_planning(CLIENTS.get(), parcel.x, parcel.y))
    if record is None or record.complete:  # a secondary layer that failed is asked again
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
    return PlanningBlock(
        code=record.code,
        name=record.name,
        kind=kind,
        norma_zonal=None
        if zone is None
        else NormaZonal(nz=zone.nz, grado=zone.grado, nivel=zone.nivel, name=RULES[zone.nz].name),
        use=record.use,
        urban_parcel=" · ".join(p for p in (record.urban_parcel, record.zone_name) if p) or None,
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
    )


class Parts(NamedTuple):
    """What the sheet says of the parcel itself: live or from the saved demo sheet."""

    parcel: ParcelBlock
    planning: PlanningBlock | None
    buildability: Buildability
    degraded: list[DegradedPart]


async def live_parts(rc14: str, lookup: Lookup, deadline: float | None = None) -> Parts:
    """The parcel (the Catastro) and its planning (the Ayuntamiento), within the deadline: a
    Catastro out of time is UpstreamError (demo sheet or 503); an Ayuntamiento out of time, or
    one of its layers failing, degrades the sheet."""
    try:
        async with asyncio.timeout_at(deadline):
            parcel = await catastro_parcel(rc14, lookup)
    except TimeoutError as exc:
        raise UpstreamError("catastro", "out of the time budget") from exc
    try:
        block = parcel_block(parcel)
    except SHAPE_ERRORS as exc:  # a coordinate or link out of the contract
        raise UpstreamError("catastro", f"unexpected answer ({type(exc).__name__})") from exc
    degraded: list[DegradedPart] = []
    try:
        async with asyncio.timeout_at(deadline):
            record = await planning_record(parcel, lookup)
    except (UpstreamError, TimeoutError):
        record = None
        degraded.append("planning")
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
    coef_z = None if record is None else record.coef_z
    return Parts(block, planning, buildability(rc14, block, planning, coef_z), degraded)


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
    sources.extend(
        OFFICIAL_SOURCES[d] for d in parts.buildability.dataset_ids if d in OFFICIAL_SOURCES
    )
    if parts.buildability.article and parts.buildability.kind is not BuildabilityKind.OFICIAL:
        sources.append(norms_source(parts.buildability))
    if kind is ParcelInput.ADDRESS:
        sources.append(GEOCODER_SOURCE)
    return sources


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
        "parcel input=%s rc14=%s fallback=%s degraded=%s ms=%d upstream_ms=%d",
        query.kind.value,
        rc14,
        fallback,
        ",".join(sheet.degraded) or "-",
        round((time.perf_counter() - started) * 1000),
        lookup.upstream_ms,
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
