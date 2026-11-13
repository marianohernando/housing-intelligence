"""People affected by each row of the list of what is missing, and where to invest first
(GET /api/v1/gaps/impact, D-229).

The zones are those of the search (D-215): the municipios, with Madrid capital split into its
21 districts when the row has district values. Statuses come from the same cached maps as
GET /gaps?level=&row=, so a zone counted here is FALTA on the map and in its list. People are
the denominator each row's feature already keeps (D-213 §4): nothing is estimated. Parameterised
SQL only.
"""

from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_api.services.gap_map import cached_row_map, data_stamp, primary_feature
from hi_api.services.gap_reference import References, load_references
from hi_api.services.gaps import REGION_CODE, REGION_LEVEL, significant
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    GapImpact,
    GapImpactRow,
    GapImpactZone,
    GapRowMap,
    GapStatus,
    ZoneGapStatus,
)
from hi_domain.gap_impact import (
    ROW_PEOPLE,
    ImpactZone,
    people_in,
    rank,
    row_summary,
    share_of,
    shortfall_p_value,
    shown_p_value,
    zone_sentence,
)
from hi_domain.gaps import GAP_METHOD

IMPACT_VERSION = "impact-0.1"
MADRID = "28079"
ZONES_NOTE = (
    "Los municipios de la Comunidad de Madrid; Madrid capital, por sus 21 distritos cuando la "
    "fila tiene datos por distrito y, si no, entera"
)

_COUNTS = text(
    """
    SELECT territory_level, territory_code, inputs->'counts' AS counts
      FROM feature_value
     WHERE feature_id = :feature_id AND inputs ? 'counts'
       AND territory_level IN ('municipio', 'distrito', :region_level)
    """
)
_REGION = text(
    """
    SELECT value, inputs FROM feature_value
     WHERE feature_id = :feature_id AND territory_level = :level AND territory_code = :code
    """
)


class RowData(NamedTuple):
    feature: dict[str, Any]
    counts: dict[tuple[str, str], dict[str, float]]
    region: dict[str, Any] | None
    references: References


def _row_data(conn: Connection, row: GapRowKey) -> RowData:
    feature = primary_feature(conn, row)
    params = {"feature_id": feature["feature_id"], "region_level": REGION_LEVEL}
    counts = {
        (r["territory_level"], r["territory_code"]): r["counts"]
        for r in conn.execute(_COUNTS, params).mappings()
    }
    region_params = {"feature_id": feature["feature_id"], "level": REGION_LEVEL}
    region = conn.execute(_REGION, region_params | {"code": REGION_CODE}).mappings().first()
    references = load_references(conn, [feature["feature_id"]])
    return RowData(feature, counts, None if region is None else dict(region), references)


def _p_value(data: RowData, zone: ZoneGapStatus) -> float | None:
    """The same test that made the zone FALTA: its own counts, or its group's (D-217)."""
    feature_id = data.feature["feature_id"]
    if zone.comparison_group is not None:
        pool = data.references.pool(feature_id, zone.code)
        return None if pool is None else shortfall_p_value(pool.observed, pool.expected)
    counts = data.counts.get((_level_of(zone).value, zone.code))
    ref = data.references.for_zone(feature_id, zone.code, data.region)
    if counts is None or ref is None or ref.rate is None:
        return None
    return shortfall_p_value(counts["numerator"], counts["denominator"] * ref.rate)


def _level_of(zone: ZoneGapStatus) -> TerritoryLevel:
    return TerritoryLevel.DISTRITO if len(zone.code) == 7 else TerritoryLevel.MUNICIPIO


def _zones(
    municipios: GapRowMap, districts: GapRowMap | None
) -> tuple[list[ZoneGapStatus], TerritoryLevel]:
    """The zones of the search for this row, and how Madrid capital is counted."""
    by_district = districts is not None and any(z.value is not None for z in districts.zones)
    if not by_district or districts is None:
        return municipios.zones, TerritoryLevel.MUNICIPIO
    others = [z for z in municipios.zones if z.code != MADRID]
    return [*others, *districts.zones], TerritoryLevel.DISTRITO


def _impact_zone(row: GapRowKey, data: RowData, zone: ZoneGapStatus) -> ImpactZone | None:
    """The zone's people and how clear its shortfall is; None without counts."""
    level = _level_of(zone)
    formula = data.feature["formula"] or {}
    people = people_in(data.counts.get((level.value, zone.code)), formula, level.value)
    group = zone.comparison_group
    ratio = group.ratio_to_reference if group is not None else zone.ratio_to_reference
    if people is None or ratio is None:
        return None
    return ImpactZone(zone.code, zone.name, people, ratio, _p_value(data, zone), group is not None)


def _ranked(
    row: GapRowKey, data: RowData, zones: list[ZoneGapStatus], warnings: list[str]
) -> list[GapImpactZone]:
    """Where to invest first: the zones in FALTA, most people affected first."""
    statuses = {z.code: z for z in zones if z.status is GapStatus.FALTA}
    measured: list[ImpactZone] = []
    for zone in statuses.values():
        impact = _impact_zone(row, data, zone)
        if impact is None:
            warnings.append(f"{row.value}: {zone.code} is FALTA without counts, not ranked")
        else:
            measured.append(impact)
    return [
        GapImpactZone(
            admin_unit_id=statuses[z.code].admin_unit_id,
            code=z.code,
            name=z.name,
            level=_level_of(statuses[z.code]),
            people=z.people,
            ratio_to_reference=significant(z.ratio),
            p_value=None if z.p_value is None else shown_p_value(z.p_value),
            comparison_group=statuses[z.code].comparison_group,
            explanation=zone_sentence(row, z),
        )
        for z in rank(measured)
    ]


def _impact_row(
    conn: Connection, row: GapRowKey, stamp: str, warnings: list[str]
) -> tuple[GapImpactRow, list[DatasetRef]] | None:
    municipios, muni_warnings = cached_row_map(conn, TerritoryLevel.MUNICIPIO, row, stamp)
    districts, district_warnings = cached_row_map(conn, TerritoryLevel.DISTRITO, row, stamp)
    warnings += [w for w in [*muni_warnings, *district_warnings] if w not in warnings]
    if municipios is None:
        return None
    data = _row_data(conn, row)
    zones, madrid_level = _zones(municipios, districts)
    ranking = _ranked(row, data, zones, warnings)
    region_counts = data.counts.get((REGION_LEVEL, REGION_CODE))
    total = people_in(region_counts, data.feature["formula"] or {}, REGION_LEVEL) or 0
    in_falta = sum(z.people for z in ranking)
    impact = GapImpactRow(
        row=row,
        label=municipios.label,
        people_label=ROW_PEOPLE[row].people,
        madrid_level=madrid_level,
        zones=len(zones),
        zones_in_falta=len(ranking),
        people_in_falta=in_falta,
        people_total=total,
        share_in_falta=share_of(in_falta, total),
        summary=row_summary(row, in_falta, total, len(ranking)),
        ranking=ranking,
    )
    used = municipios.datasets + (
        districts.datasets
        if districts is not None and madrid_level is TerritoryLevel.DISTRITO
        else []
    )
    return impact, used


def gap_impact(conn: Connection) -> tuple[GapImpact, list[str], str | None]:
    """Every row's people affected and ranking, warnings and the data version."""
    stamp = data_stamp(conn)
    rows: list[GapImpactRow] = []
    datasets: dict[str, DatasetRef] = {}
    warnings: list[str] = []
    for key in GapRowKey:
        built = _impact_row(conn, key, stamp, warnings)
        if built is None:
            continue
        rows.append(built[0])
        datasets.update((d.dataset_id, d) for d in built[1])
    impact = GapImpact(
        version=IMPACT_VERSION,
        method=GAP_METHOD,
        zones_note=ZONES_NOTE,
        rows=rows,
        datasets=[datasets[k] for k in sorted(datasets)],
    )
    data_version = stamp[:10] if stamp and stamp != "None" else None
    return impact, warnings, data_version
