"""Investor version (D-248): the pilot barrios, a barrio's sheet and the viability v0.

Reads only the Feature Store (`feature_value`), the geography and the gap services, as the rest
of the API. Each figure is taken at the finest level that has it (barrio, then district, then
the city) and says which. The figures of line A (commerce, buildable area left, vacant land)
are read by id and come back null with their reason until they are loaded. Nothing here is
used by `/search` or `/gaps`. Parameterised SQL only.
"""

from collections.abc import Iterable, Sequence
from datetime import date
from typing import Any, NamedTuple

from pydantic import HttpUrl
from sqlalchemy import Connection, text

from hi_api.services.gap_map import cached_row_map, data_stamp
from hi_api.services.gaps import ZoneNotFoundError, dataset_refs, zone_gap_list, zone_ref
from hi_api.services.search import fill_detail
from hi_contracts.catalog.enums import GapRowKey, NullReason, TerritoryLevel
from hi_contracts.pro.investors import (
    AssumptionPart,
    DemandBlock,
    DemandOutcome,
    DemandRequest,
    FieldSource,
    GapCount,
    InvestorGaps,
    InvestorZone,
    InvestorZoneList,
    InvestorZoneSummary,
    LandBlock,
    LandItem,
    PricesBlock,
    ScenarioOutcome,
    SourcedValue,
    ValueMark,
    Verdict,
    ViabilityDefaults,
    ViabilityRequest,
    ViabilityResult,
)
from hi_contracts.public import DatasetRef, GapStatus, ZoneRef
from hi_domain import viability as v
from hi_domain.gaps import es_number
from hi_domain.geo.names import display_name
from hi_domain.investors_pilot import PILOT_BARRIOS
from hi_domain.viability_data import PEM_DATASET_URL, PEM_EUR_M2, PEM_YEAR

PILOT_TEXT = "Madrid capital dentro de la M-40"
CITY = "28079"
BARRIO, DISTRITO, MUNICIPIO = (
    TerritoryLevel.BARRIO,
    TerritoryLevel.DISTRITO,
    TerritoryLevel.MUNICIPIO,
)
CCAA, REGION = TerritoryLevel.CCAA, "28"
FINEST_FIRST = (BARRIO, DISTRITO, MUNICIPIO)
LEVEL_WORDS = {
    BARRIO: "del barrio",
    DISTRITO: "del distrito",
    MUNICIPIO: "de toda la ciudad",
    CCAA: "de toda la Comunidad",
}

# The features the sheet reads, by id (the brief: line A's are consumed by their id)
POPULATION = "poblacion_total"
BARRIO_POPULATION = "poblacion_padron_barrio"  # line A (D-247): the barrio's own padrón
HOUSEHOLD_SIZE = "tamano_medio_hogar"
ONE_PERSON = "hogares_unipersonales_pct"
FIVE_PLUS = "hogares_5_mas_pct"
OVER_65 = "poblacion_65_mas_pct"
UNDER_15 = "poblacion_0_14_pct"
INCOME = "renta_neta_media_hogar"
PRICE = "precio_compra_estimado_m2"
RENT = "alquiler_m2_mensual_referencia"
APPRAISAL_NEW = "valor_tasado_vivienda_nueva_m2"
APPRAISAL_ALL = "valor_tasado_vivienda_m2"
PARCELS = "suelo_publico_vivienda_m2"
REMAINING = "edificabilidad_remanente_residencial_m2"  # line A (D-247)
VACANT = "suelo_vacante_unidades"  # line A
COMMERCE = (  # line A, in the order shown
    "comercio_proximidad_1000hab",
    "locales_abiertos_1000hab",
    "locales_cerrados_pct",
    "unidades_comerciales_1000hab",
)
# Their units until line A loads them (then the registry's)
COMMERCE_UNITS = {
    "comercio_proximidad_1000hab": "locales/1000 hab",
    "locales_abiertos_1000hab": "locales/1000 hab",
    "locales_cerrados_pct": "%",
    "unidades_comerciales_1000hab": "unidades/1000 hab",
}
COMMERCE_SUMMARY = "comercio_proximidad_1000hab"
# D-248: the PEM of the permits, loaded from its versioned table (cm_visados_presupuesto_obra);
# until a database has it, the same figure from hi_domain.viability_data
PEM = "pem_visado_vivienda_bloque_m2"
SHEET_FEATURES = (
    PEM,
    BARRIO_POPULATION,
    POPULATION,
    HOUSEHOLD_SIZE,
    ONE_PERSON,
    FIVE_PLUS,
    OVER_65,
    UNDER_15,
    INCOME,
    PRICE,
    RENT,
    APPRAISAL_NEW,
    APPRAISAL_ALL,
    PARCELS,
    REMAINING,
    VACANT,
    *COMMERCE,
)
LIST_FEATURES = (PRICE, RENT, PARCELS, REMAINING, COMMERCE_SUMMARY)
PEM_NOTE = (
    "Visados de obra nueva de viviendas en bloque: presupuesto de ejecución material entre la "
    "superficie a construir"
)
PEM_SOURCE = (
    "Visados de dirección de obra nueva de viviendas en bloque de la Comunidad de Madrid "
    f"({PEM_YEAR}): presupuesto de ejecución material entre la superficie a construir "
    "(Ministerio de Vivienda, en el portal de datos abiertos de la Comunidad)"
)

_UNITS = text(
    """
    SELECT b.code_official AS code, d.code_official AS district_code
      FROM geo_admin_unit b
      JOIN geo_admin_unit d ON d.admin_unit_id = b.parent_admin_unit_id
     WHERE b.level = 'barrio' AND b.code_official = ANY(:codes)
    """
)
_BY_ID = text(
    """
    SELECT b.code_official AS code, d.code_official AS district_code
      FROM geo_admin_unit b
      JOIN geo_admin_unit d ON d.admin_unit_id = b.parent_admin_unit_id
     WHERE b.level = 'barrio' AND b.admin_unit_id = :admin_unit_id
    """
)
_VALUES = text(
    """
    SELECT v.feature_id, v.territory_level, v.territory_code, v.value, v.null_reason,
           v.confidence, v.period_start, v.inputs, r.unit
      FROM feature_value v JOIN feature_registry r USING (feature_id)
     WHERE v.feature_id = ANY(:features)
       AND v.territory_level = ANY(:levels)
       AND v.territory_code = ANY(:codes)
    """
)
_ZONE_REFS = text(
    """
    SELECT u.level, u.admin_unit_id, u.code_official AS code, u.name,
           m.code_official AS municipio_ine, m.name AS municipio_name,
           ST_X(u.c) AS lon, ST_Y(u.c) AS lat
      FROM (SELECT *, ST_PointOnSurface(geom_4326) AS c FROM geo_admin_unit
             WHERE (level = 'barrio' AND code_official = ANY(:barrios))
                OR (level = 'distrito' AND code_official = ANY(:districts))) u
      LEFT JOIN geo_admin_unit m
        ON m.level = 'municipio' AND m.code_official = left(u.code_official, 5)
    """
)
_UNITS_OF = text("SELECT feature_id, unit FROM feature_registry WHERE feature_id = ANY(:ids)")


class Place(NamedTuple):
    """A barrio with the codes of its district and city: the levels a figure may come from."""

    code: str
    district: str

    def codes(self) -> dict[TerritoryLevel, str]:
        return {BARRIO: self.code, DISTRITO: self.district, MUNICIPIO: CITY}


Values = dict[tuple[str, str, str], dict[str, Any]]  # (feature, level, code) -> row


def pilot_codes() -> list[str]:
    return [code for code, _, _ in PILOT_BARRIOS]


def load_values(conn: Connection, features: Sequence[str], places: Iterable[Place]) -> Values:
    codes = sorted({REGION} | {c for p in places for c in p.codes().values()})
    params = {
        "features": list(features),
        "levels": [level.value for level in (*FINEST_FIRST, CCAA)],
        "codes": codes,
    }
    return {
        (r["feature_id"], r["territory_level"], r["territory_code"]): dict(r)
        for r in conn.execute(_VALUES, params).mappings()
    }


def finest(values: Values, feature: str, place: Place) -> dict[str, Any] | None:
    """The finest row with a value; else the finest row (its null and reason); else None."""
    rows = [
        row
        for level, code in place.codes().items()
        if (row := values.get((feature, level.value, code))) is not None
    ]
    return next((r for r in rows if r["value"] is not None), rows[0] if rows else None)


def versions_of(rows: Iterable[dict[str, Any] | None]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for row in rows:
        if row is not None:
            merged.update((row["inputs"] or {}).get("dataset_versions", {}))
    return merged


def publisher(ref: DatasetRef) -> str:
    """«Instituto de Estadística (Comunidad de Madrid)»: who publishes it, and the CM when it
    publishes it in its portal and the name does not say so."""
    if ref.is_cm_open_data and "Comunidad de Madrid" not in ref.publisher:
        return f"{ref.publisher} (Comunidad de Madrid)"
    return ref.publisher


class Sources(NamedTuple):
    """The datasets behind the sheet, to name and link each figure's source."""

    refs: dict[str, DatasetRef]

    def text(self, dataset_ids: Sequence[str]) -> str:
        names = [publisher(self.refs[d]) for d in dataset_ids if d in self.refs]
        unique = list(dict.fromkeys(names))
        return ", ".join(unique) if unique else "Sin fuente cargada"

    def url(self, dataset_ids: Sequence[str]) -> Any:
        primary = [self.refs[d] for d in dataset_ids if d in self.refs]
        cm = [r for r in primary if r.is_cm_open_data]
        chosen = (cm or primary)[:1]
        return chosen[0].url if chosen else None


def period_text(value: Any) -> str | None:
    return str(value.year) if isinstance(value, date) else None


def sourced(
    row: dict[str, Any] | None,
    sources: Sources,
    unit: str,
    *,
    note: str | None = None,
    feature_id: str | None = None,
) -> SourcedValue:
    """A data figure with its source; a missing row is SOURCE_NO_COVERAGE (not loaded)."""
    if row is None:
        return SourcedValue(
            feature_id=feature_id,
            value=None,
            unit=unit,
            mark=ValueMark.DATO,
            null_reason=NullReason.SOURCE_NO_COVERAGE,
            source=FieldSource(text=note or "Aún sin cargar"),
        )
    level = TerritoryLevel(row["territory_level"])
    ids = sorted((row["inputs"] or {}).get("dataset_versions", {}))
    period = period_text(row["period_start"])
    words = [sources.text(ids), *([period] if period else []), f"dato {LEVEL_WORDS[level]}"]
    return SourcedValue(
        feature_id=row["feature_id"],
        value=None if row["value"] is None else float(row["value"]),
        unit=unit,
        mark=ValueMark.DATO,
        null_reason=row["null_reason"],
        confidence=float(row["confidence"]),
        source=FieldSource(
            text=" · ".join(words) + (f". {note}" if note else ""),
            level=level,
            period=period,
            dataset_ids=ids,
            url=sources.url(ids),
        ),
    )


def assumption(value: float, unit: str, source: str) -> SourcedValue:
    return SourcedValue(
        value=value, unit=unit, mark=ValueMark.SUPUESTO, source=FieldSource(text=source)
    )


def parts(items: Iterable[v.Part]) -> list[AssumptionPart]:
    return [
        AssumptionPart(key=p.key, label=p.label, pct=round(p.share * 100, 2), source=p.source)
        for p in items
    ]


# --- List of pilot barrios ---


def district_gaps(conn: Connection, districts: Iterable[str]) -> dict[str, GapCount]:
    """Each district's FALTA and JUSTO rows, from the cached row maps of /gaps (6 rows)."""
    stamp = data_stamp(conn)
    wanted = set(districts)
    found: dict[str, list[tuple[GapStatus, str]]] = {d: [] for d in wanted}
    for row in GapRowKey:
        gap_map, _ = cached_row_map(conn, DISTRITO, row, stamp)
        if gap_map is None:
            continue
        for zone in gap_map.zones:
            if zone.code in wanted:
                found[zone.code].append((zone.status, gap_map.label))
    return {
        code: GapCount(
            falta=sum(s is GapStatus.FALTA for s, _ in rows),
            justo=sum(s is GapStatus.JUSTO for s, _ in rows),
            rows=[label for s, label in rows if s is GapStatus.FALTA]
            + [label for s, label in rows if s is GapStatus.JUSTO],
        )
        for code, rows in found.items()
        if rows
    }


def items_of(row: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    if row is None:
        return None
    detail = (row["inputs"] or {}).get("detail") or {}
    items = detail.get("items")
    return None if items is None else list(items)


def value_of(row: dict[str, Any] | None) -> float | None:
    return None if row is None or row["value"] is None else float(row["value"])


def batch_zone_refs(
    conn: Connection, places: Iterable[Place]
) -> dict[tuple[TerritoryLevel, str], ZoneRef]:
    """The ZoneRef of every barrio and district of the list in one query (zone_ref of
    services/gaps.py, which asks one zone at a time, made ~216 queries for the pilot)."""
    chosen = list(places)
    params = {
        "barrios": sorted({p.code for p in chosen}),
        "districts": sorted({p.district for p in chosen}),
    }
    refs: dict[tuple[TerritoryLevel, str], ZoneRef] = {}
    for row in conn.execute(_ZONE_REFS, params).mappings():
        level = TerritoryLevel(row["level"])
        refs[(level, row["code"])] = ZoneRef(
            level=level,
            code=row["code"],
            admin_unit_id=row["admin_unit_id"],
            name=display_name(row["name"]) if row["name"] else row["code"],
            municipio_ine=row["municipio_ine"],
            municipio_name=display_name(row["municipio_name"]) if row["municipio_name"] else None,
            center_lon=round(row["lon"], 5),
            center_lat=round(row["lat"], 5),
        )
    return refs


def summary(
    code: str,
    place: Place,
    values: Values,
    gaps: dict[str, GapCount],
    refs: dict[tuple[TerritoryLevel, str], ZoneRef],
) -> InvestorZoneSummary:
    parcels_row = values.get((PARCELS, BARRIO.value, code))
    parcels = items_of(parcels_row)
    return InvestorZoneSummary(
        zone=refs[(BARRIO, code)],
        district=refs[(DISTRITO, place.district)],
        gaps=gaps.get(place.district),
        parcels=None if parcels is None else len(parcels),
        parcels_m2=value_of(parcels_row),
        remaining_m2=value_of(values.get((REMAINING, BARRIO.value, code))),
        remaining_shared_areas=shared_areas(values.get((REMAINING, BARRIO.value, code))),
        commerce_per_1000=value_of(values.get((COMMERCE_SUMMARY, BARRIO.value, code))),
        sale_price_m2=value_of(finest(values, PRICE, place)),
        rent_m2_month=value_of(finest(values, RENT, place)),
    )


def pilot_places(conn: Connection, codes: Sequence[str]) -> dict[str, Place]:
    rows = conn.execute(_UNITS, {"codes": list(codes)}).mappings()
    return {r["code"]: Place(r["code"], r["district_code"]) for r in rows}


def zone_list(conn: Connection) -> tuple[InvestorZoneList, list[str], str | None]:
    codes = pilot_codes()
    places = pilot_places(conn, codes)
    missing = [c for c in codes if c not in places]
    warnings = [f"NOT_FOUND: pilot barrio {c} not in the geography" for c in missing]
    if not codes:
        warnings.append("INSUFFICIENT_DATA: the pilot list (D-247) is not loaded yet")
    values = load_values(conn, LIST_FEATURES, places.values())
    gaps = district_gaps(conn, (p.district for p in places.values()))
    refs = batch_zone_refs(conn, places.values())
    zones = [summary(c, places[c], values, gaps, refs) for c in codes if c in places]
    zones.sort(key=lambda z: (z.district.name, z.zone.name))
    data = InvestorZoneList(
        pilot=PILOT_TEXT, zones=zones, datasets=dataset_refs(conn, versions_of(values.values()))
    )
    return data, warnings, data_stamp(conn)[:10] if zones else None


# --- One barrio's sheet ---


def find_place(conn: Connection, admin_unit_id: str) -> Place:
    row = conn.execute(_BY_ID, {"admin_unit_id": admin_unit_id}).mappings().first()
    if row is None or row["code"] not in pilot_codes():
        msg = f"{admin_unit_id} is not a pilot barrio ({PILOT_TEXT})"
        raise ZoneNotFoundError(msg)
    return Place(row["code"], row["district_code"])


def population(values: Values, place: Place, sources: Sources) -> SourcedValue:
    """The barrio's own padrón (line A) when loaded; else the finest of the total population."""
    row = values.get((BARRIO_POPULATION, BARRIO.value, place.code))
    if row is not None and row["value"] is not None:
        return sourced(row, sources, "personas")
    return sourced(finest(values, POPULATION, place), sources, "personas")


def demand_block(values: Values, place: Place, sources: Sources) -> DemandBlock:
    def get(feature: str, unit: str) -> SourcedValue:
        return sourced(finest(values, feature, place), sources, unit)

    return DemandBlock(
        population=population(values, place, sources),
        household_size=get(HOUSEHOLD_SIZE, "personas/hogar"),
        one_person_pct=get(ONE_PERSON, "%"),
        five_plus_pct=get(FIVE_PLUS, "%"),
        over_65_pct=get(OVER_65, "%"),
        under_15_pct=get(UNDER_15, "%"),
        income=get(INCOME, "€/hogar/año"),
    )


def premium(values: Values, sources: Sources) -> SourcedValue:
    """D-241: the appraised value of homes up to 5 years old against all, in the city."""
    new = values.get((APPRAISAL_NEW, MUNICIPIO.value, CITY))
    total = values.get((APPRAISAL_ALL, MUNICIPIO.value, CITY))
    new_value, total_value = value_of(new), value_of(total)
    if new is None or total is None or new_value is None or not total_value:
        return sourced(None, sources, "%", note="Sin el valor tasado de la vivienda nueva")
    figure = sourced(new, sources, "%")
    ids = sorted(set(figure.source.dataset_ids) | set(versions_of([total])))
    return figure.model_copy(
        update={
            "value": round((new_value / total_value - 1) * 100, 1),
            "source": figure.source.model_copy(
                update={
                    "text": "Valor tasado de la vivienda libre de hasta 5 años "
                    f"({es_number(new_value, 0)} €/m²) frente al de toda la vivienda libre "
                    f"({es_number(total_value, 0)} €/m²) en Madrid · {sources.text(ids)}"
                    f" · {figure.source.period}",
                    "dataset_ids": ids,
                }
            ),
        }
    )


def rent_value(values: Values, place: Place, sources: Sources) -> SourcedValue:
    row = finest(values, RENT, place)
    figure = sourced(row, sources, "€/m²/mes", note="Contratos firmados en 2024")
    if row is None:
        return figure
    spread = fill_detail(row["inputs"] or {}).quartiles
    if spread is None:
        return figure
    return figure.model_copy(update={"low": spread[0], "high": spread[1]})


def prices_block(values: Values, place: Place, sources: Sources) -> PricesBlock:
    sale = sourced(
        finest(values, PRICE, place),
        sources,
        "€/m²",
        note="Estimación: el valor tasado de la ciudad repartido por el valor catastral (D-234)",
    )
    extra = premium(values, sources)
    # From the rounded figures on screen, so the calculator (which starts from them) says the same
    new_value = (
        None
        if sale.value is None or extra.value is None
        else round(round(sale.value) * (1 + extra.value / 100))
    )
    new_sale = sale.model_copy(
        update={
            "value": new_value,
            "null_reason": None if new_value is not None else NullReason.SOURCE_MISSING,
            "source": FieldSource(
                text="El precio estimado del barrio con la prima de la vivienda nueva",
                level=sale.source.level,
                dataset_ids=sorted(set(sale.source.dataset_ids) | set(extra.source.dataset_ids)),
            ),
        }
    )
    return PricesBlock(
        sale_m2=sale,
        new_build_premium_pct=extra,
        new_build_sale_m2=new_sale,
        rent_m2_month=rent_value(values, place, sources),
    )


def land_items(row: dict[str, Any] | None, kind: str) -> list[LandItem]:
    return [
        LandItem(
            kind=kind,
            code=item.get("code"),
            name=item.get("name"),
            parcel=item.get("parcel"),
            buildable_m2=item.get("value"),
            regime=item.get("regime"),
            manager=item.get("manager"),
            stage=item.get("stage"),
            use=item.get("use"),
            note=item.get("note"),
            url=item.get("url"),
        )
        for item in items_of(row) or []
    ]


def shared_areas(row: dict[str, Any] | None) -> int | None:
    """Planning areas that also cover other barrios: their note says the share that is here."""
    items = items_of(row)
    return None if items is None else sum(1 for item in items if item.get("note"))


def shared_note(count: int | None) -> str | None:
    """Line A places each area whole in one barrio (D-247): the sum says so when it happens."""
    if not count:
        return None
    areas = "1 ámbito que ocupa" if count == 1 else f"{count} ámbitos que ocupan"
    return (
        f"Incluye {areas} también otros barrios: cuenta{'n' if count > 1 else ''} entero"
        f"{'s' if count > 1 else ''} aquí; la nota de cada uno dice qué parte está en este barrio"
    )


def land_block(values: Values, place: Place, sources: Sources) -> LandBlock:
    parcels = values.get((PARCELS, BARRIO.value, place.code))
    remaining = values.get((REMAINING, BARRIO.value, place.code))
    return LandBlock(
        parcels=land_items(parcels, "parcela"),
        parcels_m2=sourced(parcels, sources, "m²"),
        remaining=land_items(remaining, "ambito"),
        remaining_m2=sourced(remaining, sources, "m²", note=shared_note(shared_areas(remaining))),
        vacant_units=sourced(finest(values, VACANT, place), sources, "unidades"),
    )


def gaps_block(
    conn: Connection, values: Values, place: Place, sources: Sources, units: dict[str, str]
) -> InvestorGaps | None:
    """The district's «Qué falta» (no list by barrio) and the barrio's commerce (line A)."""
    try:
        gaps, warnings, _ = zone_gap_list(conn, DISTRITO, place.district)
    except ZoneNotFoundError:
        return None
    commerce = [
        sourced(finest(values, f, place), sources, units.get(f, COMMERCE_UNITS[f]), feature_id=f)
        for f in COMMERCE
    ]
    return InvestorGaps(
        level=DISTRITO,
        zone_name=gaps.zone.name,
        rows=gaps.rows,
        commerce=commerce,
        warnings=warnings,
    )


def pem_value(values: Values, sources: Sources) -> SourcedValue:
    """The PEM per m² of the permits: the Feature Store's, with its dataset and version; without
    it (a database not loaded yet), the same versioned figure of hi_domain.viability_data."""
    row = values.get((PEM, CCAA.value, REGION))
    if row is not None and row["value"] is not None:
        return sourced(row, sources, "€/m²", note=PEM_NOTE)
    return SourcedValue(
        feature_id=PEM,
        value=float(PEM_EUR_M2),
        unit="€/m²",
        mark=ValueMark.DATO,
        source=FieldSource(
            text=PEM_SOURCE, level=CCAA, period=str(PEM_YEAR), url=HttpUrl(PEM_DATASET_URL)
        ),
    )


def defaults_block(
    prices: PricesBlock, income: SourcedValue, pem: SourcedValue
) -> ViabilityDefaults:
    coefficient = sum(p.share for p in v.COST_PARTS)
    return ViabilityDefaults(
        sale_price_m2=prices.sale_m2,
        new_build_premium_pct=prices.new_build_premium_pct,
        rent_m2_month=prices.rent_m2_month,
        pem_m2=pem,
        cost_coefficient=assumption(
            v.COST_COEFFICIENT,
            "×",
            f"Supuesto: el PEM más un {round(coefficient * 100)} % (gastos generales y "
            "beneficio, honorarios, licencia e ICIO, y otros; desglose debajo)",
        ),
        cost_parts=parts(v.COST_PARTS),
        sales_costs_pct=assumption(
            round(v.SALES_COSTS_SHARE * 100, 2),
            "% de las ventas",
            "Supuesto: comercialización, gestión, notaría, registro e impuestos de la obra nueva",
        ),
        sales_cost_parts=parts(v.SALES_COST_PARTS),
        target_margin_pct=assumption(v.TARGET_MARGIN * 100, "%", v.MARGIN_SOURCE),
        adjust_floor_pct=assumption(v.ADJUST_FLOOR * 100, "%", v.MARGIN_SOURCE),
        household_income=income,
        home_m2=assumption(v.HOME_M2, "m²", v.HOME_M2_SOURCE),
        ltv_pct=assumption(v.LOAN_TO_VALUE * 100, "%", v.LOAN_SOURCE),
        loan_years=assumption(v.LOAN_YEARS, "años", v.LOAN_SOURCE),
        loan_rate_pct=assumption(v.LOAN_RATE * 100, "%", v.LOAN_SOURCE),
        effort_threshold_pct=assumption(v.EFFORT_THRESHOLD * 100, "%", v.EFFORT_SOURCE),
    )


def zone_sheet(conn: Connection, admin_unit_id: str) -> tuple[InvestorZone, list[str], str | None]:
    place = find_place(conn, admin_unit_id)
    values = load_values(conn, SHEET_FEATURES, [place])
    units = {
        r["feature_id"]: r["unit"]
        for r in conn.execute(_UNITS_OF, {"ids": list(SHEET_FEATURES)}).mappings()
    }
    refs = dataset_refs(conn, versions_of(values.values()))
    sources = Sources({r.dataset_id: r for r in refs})
    demand = demand_block(values, place, sources)
    prices = prices_block(values, place, sources)
    gaps = gaps_block(conn, values, place, sources, units)
    warnings = [
        f"INSUFFICIENT_DATA: {f} not loaded yet"
        for f in (REMAINING, VACANT, *COMMERCE)
        if f not in units
    ]
    sheet = InvestorZone(
        zone=zone_ref(conn, BARRIO, place.code),
        district=zone_ref(conn, DISTRITO, place.district),
        demand=demand,
        prices=prices,
        gaps=gaps,
        land=land_block(values, place, sources),
        defaults=defaults_block(prices, demand.income, pem_value(values, sources)),
        notices=list(v.NOTICES),
        datasets=refs if gaps is None else union(refs, gaps.rows),
    )
    return sheet, warnings, data_stamp(conn)[:10]


def union(refs: list[DatasetRef], rows: Iterable[Any]) -> list[DatasetRef]:
    unique = {r.dataset_id: r for r in refs}
    for row in rows:
        unique.update({d.dataset_id: d for d in row.datasets})
    return [unique[k] for k in sorted(unique)]


# --- Viability ---


def run_viability(request: ViabilityRequest) -> ViabilityResult:
    area = request.buildable_m2
    land = request.land_eur
    if request.land_eur_m2 is not None:
        land = request.land_eur_m2 * area
    inputs = v.ViabilityInputs(
        buildable_m2=area,
        sale_price_m2=request.sale_price_m2,
        new_build_premium=request.new_build_premium_pct / 100,
        rent_m2_month=request.rent_m2_month,
        pem_m2=request.pem_m2,
        cost_coefficient=request.cost_coefficient,
        land_eur=land,
        sales_costs_share=request.sales_costs_pct / 100,
        target_margin=request.target_margin_pct / 100,
        adjust_floor=request.adjust_floor_pct / 100,
    )
    result = v.viability(inputs)
    new_price = v.sale_price_with_premium(inputs)
    return ViabilityResult(
        version=v.VIABILITY_VERSION,
        land_known=result.land_known,
        sale_price_m2_new=new_price,
        scenarios=[outcome(s) for s in result.scenarios],
        demand=None if request.demand is None else demand(request.demand, new_price, inputs),
        notices=list(v.NOTICES),
    )


def as_pct(share: float | None) -> float | None:
    return None if share is None else share * 100


def outcome(s: v.ScenarioResult) -> ScenarioOutcome:
    return ScenarioOutcome(
        key=s.scenario.key,
        label=s.scenario.label,
        price_factor=s.scenario.price_factor,
        cost_factor=s.scenario.cost_factor,
        revenue=s.revenue,
        construction=s.construction,
        sales_costs=s.sales_costs,
        land=s.land,
        total_cost=s.total_cost,
        profit=s.profit,
        margin_pct=as_pct(s.margin),
        residual_land_value=s.residual_land_value,
        residual_land_value_m2=s.residual_land_value_m2,
        annual_rent=s.annual_rent,
        rental_yield_pct=as_pct(s.rental_yield),
        yield_land=None if s.yield_land is None else s.yield_land.value,
        verdict=None if s.verdict is None else Verdict(s.verdict.value),
        headline=s.headline,
    )


def demand(request: DemandRequest, price_m2: float, inputs: v.ViabilityInputs) -> DemandOutcome:
    check = v.demand_check(
        v.DemandInputs(
            household_income_year=request.household_income,
            sale_price_m2=price_m2,
            rent_m2_month=inputs.rent_m2_month,
            home_m2=request.home_m2,
            loan_to_value=request.ltv_pct / 100,
            loan_years=request.loan_years,
            loan_rate=request.loan_rate_pct / 100,
            effort_threshold=request.effort_threshold_pct / 100,
        )
    )
    return DemandOutcome(
        home_price=check.home_price,
        loan=check.loan,
        down_payment=check.down_payment,
        down_payment_years=check.down_payment_years,
        monthly_payment=check.monthly_payment,
        purchase_effort_pct=check.purchase_effort * 100,
        monthly_rent=check.monthly_rent,
        rent_effort_pct=as_pct(check.rent_effort),
        threshold_pct=check.threshold * 100,
        purchase_within=check.purchase_within,
        rent_within=check.rent_within,
        lines=list(check.lines),
    )
