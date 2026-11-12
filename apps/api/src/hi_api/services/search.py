"""People search (CORE-003, POST /api/v1/search): loads the zones and the indicators bound to
the search in the Feature Dictionary (`fit`), and the «Qué falta aquí» highlights from the
same rows as GET /gaps; hi_domain.search decides. Parameterised SQL only, no feature id here.
"""

from collections.abc import Iterable
from datetime import datetime
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_api.services.commute import commutes
from hi_api.services.gap_map import RowNotBoundError, gap_row_map
from hi_api.services.gaps import dataset_refs, significant
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    GapHighlight,
    GapRowMap,
    IndicatorValue,
    NeedKey,
    PriorityKey,
    ScenarioState,
    SearchResult,
    ZoneRef,
)
from hi_domain.fit import FIT_VERSION, ZoneData
from hi_domain.geo.names import display_name
from hi_domain.search import SPLIT_BY_DISTRICT, highlight_rows, run_search

LEVELS = (TerritoryLevel.MUNICIPIO, TerritoryLevel.DISTRITO)

_ZONES = text(
    """
    SELECT u.level, u.code_official AS code, u.admin_unit_id, u.name,
           m.code_official AS municipio_ine, m.name AS municipio_name,
           ST_X(u.c) AS lon, ST_Y(u.c) AS lat
      FROM (SELECT *, ST_PointOnSurface(geom_4326) AS c FROM geo_admin_unit
             WHERE (level = 'municipio' AND NOT code_official = ANY(:split))
                OR (level = 'distrito' AND left(code_official, 5) = ANY(:split))) u
      LEFT JOIN geo_admin_unit m
        ON m.level = 'municipio' AND m.code_official = left(u.code_official, 5)
     ORDER BY u.level DESC, u.code_official
    """
)
# One row per feature and zone: the latest period of the newest version.
_FIT_VALUES = text(
    """
    SELECT DISTINCT ON (v.feature_id, v.territory_level, v.territory_code)
           v.feature_id, v.territory_level, v.territory_code, v.value, v.null_reason,
           v.confidence, v.inputs, v.computed_at, f.human_name, f.unit, f.spec->'fit' AS fit
      FROM feature_value v
      JOIN feature_registry f ON f.feature_id = v.feature_id
     WHERE f.spec->'fit' IS NOT NULL AND f.spec->'fit' <> 'null'::jsonb
       AND v.territory_level = ANY(:levels)
     ORDER BY v.feature_id, v.territory_level, v.territory_code,
              v.feature_version DESC, v.period_start DESC
    """
)
_DATA_STAMP = text("SELECT max(computed_at) FROM feature_value")


class Loaded(NamedTuple):
    zones: list[ZoneData]
    versions: dict[str, str]
    computed: list[datetime]
    gap_datasets: list[DatasetRef]
    warnings: list[str]
    unresolved_anchors: list[int]
    commute_versions: dict[str, str]  # the GTFS feeds behind the trips to the places of work


def _zone_ref(row: dict[str, Any]) -> ZoneRef:
    return ZoneRef(
        level=TerritoryLevel(row["level"]),
        code=row["code"],
        admin_unit_id=row["admin_unit_id"],
        name=display_name(row["name"]) if row["name"] else row["code"],
        municipio_ine=row["municipio_ine"],
        municipio_name=display_name(row["municipio_name"]) if row["municipio_name"] else None,
        center_lon=None if row["lon"] is None else round(row["lon"], 5),
        center_lat=None if row["lat"] is None else round(row["lat"], 5),
    )


def _indicator(row: dict[str, Any]) -> IndicatorValue:
    return IndicatorValue(
        feature_id=row["feature_id"],
        label=row["human_name"],
        value=None if row["value"] is None else significant(float(row["value"])),
        unit=row["unit"],
        confidence=round(float(row["confidence"]), 3),
        null_reason=row["null_reason"],
        level=TerritoryLevel(row["territory_level"]),
        datasets=sorted(row["inputs"].get("dataset_versions", {})),
    )


class Indicators(NamedTuple):
    rent: dict[tuple[str, str], IndicatorValue]
    price: dict[tuple[str, str], IndicatorValue]  # appraised value per m² to buy (D-227)
    walk: dict[tuple[str, str], dict[NeedKey, IndicatorValue]]
    priority_walk: dict[tuple[str, str], dict[PriorityKey, IndicatorValue]]


def _indicators(rows: Iterable[dict[str, Any]]) -> Indicators:
    rent: dict[tuple[str, str], IndicatorValue] = {}
    price: dict[tuple[str, str], IndicatorValue] = {}
    walk: dict[tuple[str, str], dict[NeedKey, IndicatorValue]] = {}
    priority_walk: dict[tuple[str, str], dict[PriorityKey, IndicatorValue]] = {}
    for row in rows:
        key = (row["territory_level"], row["territory_code"])
        fit = row["fit"]
        if fit["role"] == "rent_m2":
            rent[key] = _indicator(row)
        elif fit["role"] == "price_m2":
            price[key] = _indicator(row)
        elif fit.get("need"):
            walk.setdefault(key, {})[NeedKey(fit["need"])] = _indicator(row)
        else:  # a priority measured on foot: the park for «Zonas verdes» (D-222)
            priority_walk.setdefault(key, {})[PriorityKey(fit["priority"])] = _indicator(row)
    return Indicators(rent, price, walk, priority_walk)


GapMapEntry = tuple[GapRowMap | None, list[str]]
_GAP_MAPS: dict[tuple[str, str, str, str], GapMapEntry] = {}
GAP_CACHE_MAX = 64


def _gap_map(conn: Connection, level: TerritoryLevel, row: GapRowKey, stamp: str) -> GapMapEntry:
    """GET /gaps?level=&row= for one row, cached per process until the features change (the
    stamp is the latest computation): the same answer, without ~5 queries per row and level."""
    key = (str(conn.engine.url), stamp, level.value, row.value)
    cached = _GAP_MAPS.get(key)
    if cached is not None:
        return cached
    try:
        gap_map, warnings, _ = gap_row_map(conn, level, row)
        entry: GapMapEntry = (gap_map, warnings)
    except RowNotBoundError as exc:
        entry = (None, [f"{ErrorCode.INSUFFICIENT_DATA.value}: {exc}"])
    if len(_GAP_MAPS) >= GAP_CACHE_MAX:
        _GAP_MAPS.clear()
    _GAP_MAPS[key] = entry  # returned from the local: another thread may clear the cache
    return entry


def _highlights(
    conn: Connection, rows: list[GapRowKey]
) -> tuple[dict[tuple[str, str], list[GapHighlight]], list[DatasetRef], list[str]]:
    """Each zone's status in the household's 3 rows, from the same map as GET /gaps."""
    stamp = str(conn.execute(_DATA_STAMP).scalar())
    highlights: dict[tuple[str, str], list[GapHighlight]] = {}
    datasets: list[DatasetRef] = []
    warnings: list[str] = []
    for row in rows:
        for level in LEVELS:
            gap_map, row_warnings = _gap_map(conn, level, row, stamp)
            warnings += [w for w in row_warnings if w not in warnings]
            if gap_map is None:
                continue
            datasets += gap_map.datasets
            for zone in gap_map.zones:
                highlight = GapHighlight(row=row, label=gap_map.label, status=zone.status)
                highlights.setdefault((level.value, zone.code), []).append(highlight)
    return highlights, datasets, warnings


def load(conn: Connection, scenario: ScenarioState) -> Loaded:
    split = list(SPLIT_BY_DISTRICT)
    zone_rows = [dict(r) for r in conn.execute(_ZONES, {"split": split}).mappings()]
    levels = [level.value for level in LEVELS]
    value_rows = [dict(r) for r in conn.execute(_FIT_VALUES, {"levels": levels}).mappings()]
    indicators = _indicators(value_rows)
    highlights, gap_datasets, warnings = _highlights(conn, highlight_rows(scenario))
    trips = commutes(conn, scenario.anchors)
    zones = []
    for row in zone_rows:
        key = (row["level"], row["code"])
        zone_id = str(row["admin_unit_id"])
        zones.append(
            ZoneData(
                zone=_zone_ref(row),
                rent=indicators.rent.get(key),
                price=indicators.price.get(key),
                walk=indicators.walk.get(key, {}),
                priority_walk=indicators.priority_walk.get(key, {}),
                gaps=highlights.get(key, []),
                commute={i: by[zone_id] for i, by in trips.by_zone.items() if zone_id in by},
            )
        )
    versions: dict[str, str] = dict(trips.versions)
    for row in value_rows:
        versions.update(row["inputs"].get("dataset_versions", {}))
    computed = [row["computed_at"] for row in value_rows]
    return Loaded(
        zones, versions, computed, gap_datasets, warnings, trips.unresolved, dict(trips.versions)
    )


def _union(refs: Iterable[DatasetRef]) -> list[DatasetRef]:
    unique = {r.dataset_id: r for r in refs}
    return [unique[k] for k in sorted(unique)]


def load_warnings(loaded: Loaded) -> list[str]:
    """What every answer built on the loaded zones must say: rows without a gap map and places
    of work outside every computed destination (scored in a straight line)."""
    return [
        *loaded.warnings,
        *(
            f"{ErrorCode.INSUFFICIENT_DATA.value}: no computed destination holds anchor {i}, so "
            "its trip by public transport is unknown: a trip limit is UNKNOWN and the place is "
            "scored in a straight line"
            for i in loaded.unresolved_anchors
        ),
    ]


def search(conn: Connection, scenario: ScenarioState) -> tuple[SearchResult, list[str], str | None]:
    """The result, warnings and the data version (latest computation of the values used)."""
    loaded = load(conn, scenario)
    outcome = run_search(scenario, loaded.zones)
    warnings = load_warnings(loaded)
    if outcome.unscored_passing:
        warnings.append(
            f"{ErrorCode.INSUFFICIENT_DATA.value}: {outcome.unscored_passing} zones pass every "
            "condition but have no data for any chosen priority; they are only in all_zones"
        )
    result = SearchResult(
        scenario=scenario,
        results=outcome.results,
        near_misses=outcome.near_misses,
        all_zones=outcome.all_zones,
        reality_check=outcome.reality_check,
        datasets=_union([*dataset_refs(conn, loaded.versions), *loaded.gap_datasets]),
        methodology_version=FIT_VERSION,
    )
    data_version = max(loaded.computed).date().isoformat() if loaded.computed else None
    return result, warnings, data_version
