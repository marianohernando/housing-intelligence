"""People search (CORE-003, POST /api/v1/search): loads the zones and the indicators bound to
the search in the Feature Dictionary (`fit`), and the «Qué falta aquí» highlights from the
same rows as GET /gaps; hi_domain.search decides. Parameterised SQL only, no feature id here.
The entry point is hi_api.services.scope.search, which also ranks Madrid capital by barrio.
"""

import logging
from collections.abc import Iterable
from datetime import datetime
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_api.services.commute import commutes
from hi_api.services.gap_map import cached_row_map, data_stamp
from hi_api.services.gaps import dataset_refs, significant
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    GapHighlight,
    IndicatorValue,
    NeedKey,
    PriorityKey,
    ScenarioState,
    SearchResult,
    ZoneRef,
)
from hi_domain.affordability import HOUSES_NOTE
from hi_domain.fit import FIT_VERSION, PRIORITY_WALK, ZoneData, ignored_leisure
from hi_domain.geo.names import display_name
from hi_domain.geo.scope import in_scope
from hi_domain.search import SPLIT_BY_DISTRICT, highlight_rows, run_search

log = logging.getLogger(__name__)

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
FIT_VALUES = text(
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


class Loaded(NamedTuple):
    zones: list[ZoneData]
    versions: dict[str, str]
    computed: list[datetime]
    gap_datasets: list[DatasetRef]
    warnings: list[str]
    unresolved_anchors: list[int]
    commute_versions: dict[str, str]  # the GTFS feeds behind the trips to the places of work


def zone_ref(row: dict[str, Any]) -> ZoneRef:
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


class FillDetail(NamedTuple):
    """What a reference rent row says besides its value (its `inputs.reference_rent`)."""

    quartiles: tuple[float, float] | None  # p25 and p75 per m², scaled as the value
    typology: str | None


class Indicators(NamedTuple):
    rent: dict[tuple[str, str], IndicatorValue]
    rent_note: str | None  # what the rent figure is, from its feature's `fit.note` (D-228)
    price: dict[tuple[str, str], IndicatorValue]  # appraised value per m² to buy (D-227)
    # D-234: an estimated price per m², used only where no published one exists
    price_estimate: dict[tuple[str, str], IndicatorValue]
    walk: dict[tuple[str, str], dict[NeedKey, IndicatorValue]]
    priority_walk: dict[tuple[str, str], dict[PriorityKey, IndicatorValue]]
    transit: dict[tuple[str, str], dict[str, IndicatorValue]]  # by mode, only words a fact (D-233)
    # D-242: the Ministry's reference rent, used only where the CM publishes none
    rent_fill: dict[tuple[str, str], IndicatorValue]
    rent_fill_detail: dict[tuple[str, str], FillDetail]
    rent_fill_note: str | None
    rent_fill_source: str | None


class ZoneRent(NamedTuple):
    """The rent a zone is searched with: the CM one when published, else the reference."""

    rent: IndicatorValue | None
    note: str | None
    range_m2: tuple[float, float] | None = None
    source: str | None = None


TRANSIT_MODES = frozenset({"bus", "metro"})
HOUSES_TYPOLOGY = "unifamiliar"  # the reference rent of single-family homes (D-242)
# Every need is measured on foot, the leisure groups of «Ocio» too (D-236)
NEED_VALUES = frozenset(n.value for n in NeedKey)
# Only the priorities measured by walking to a place of their own (D-222, D-223): «ocio» scores
# its groups' needs and «seguridad» has no measure, so a feature bound to either is unknown
PRIORITY_WALK_VALUES = frozenset(p.value for p in PRIORITY_WALK)


def _unknown_binding(fit: dict[str, Any]) -> str:
    """«walk_minutes:need=piscinas», «transit_mode:mode=tram» or just the role."""
    detail = next((f"{k}={fit[k]}" for k in ("need", "priority", "mode") if fit.get(k)), None)
    return f"{fit['role']}:{detail}" if detail else str(fit["role"])


def fill_detail(inputs: dict[str, Any]) -> FillDetail:
    reference = inputs.get("reference_rent") or {}
    quartiles = reference.get("quartiles") or {}
    low, high = quartiles.get("p25"), quartiles.get("p75")
    spread = None if low is None or high is None else (float(low), float(high))
    return FillDetail(spread, reference.get("typology"))


def indicators_by_zone(rows: Iterable[dict[str, Any]]) -> Indicators:
    rent: dict[tuple[str, str], IndicatorValue] = {}
    rent_fill: dict[tuple[str, str], IndicatorValue] = {}
    rent_fill_detail: dict[tuple[str, str], FillDetail] = {}
    fill_note: str | None = None
    fill_source: str | None = None
    price: dict[tuple[str, str], IndicatorValue] = {}
    price_estimate: dict[tuple[str, str], IndicatorValue] = {}
    walk: dict[tuple[str, str], dict[NeedKey, IndicatorValue]] = {}
    priority_walk: dict[tuple[str, str], dict[PriorityKey, IndicatorValue]] = {}
    transit: dict[tuple[str, str], dict[str, IndicatorValue]] = {}
    unknown: set[str] = set()
    rent_note: str | None = None
    for row in rows:
        key = (row["territory_level"], row["territory_code"])
        fit = row["fit"]
        if fit["role"] == "rent_m2":
            rent[key] = _indicator(row)
            rent_note = fit.get("note") or rent_note
        elif fit["role"] == "rent_m2_fill":  # D-242: only where the CM publishes none
            rent_fill[key] = _indicator(row)
            rent_fill_detail[key] = fill_detail(row["inputs"])
            fill_note = fit.get("note") or fill_note
            fill_source = fit.get("source") or fill_source
        elif fit["role"] == "price_m2":
            price[key] = _indicator(row)
        elif fit["role"] == "price_m2_estimate":  # D-234: only where no price is published
            price_estimate[key] = _indicator(row)
        elif fit["role"] == "transit_mode" and fit.get("mode") in TRANSIT_MODES:
            transit.setdefault(key, {})[fit["mode"]] = _indicator(row)
        elif fit["role"] == "walk_minutes" and fit.get("need") in NEED_VALUES:
            walk.setdefault(key, {})[NeedKey(fit["need"])] = _indicator(row)
        elif fit["role"] == "walk_minutes" and fit.get("priority") in PRIORITY_WALK_VALUES:
            # a priority measured on foot: the park for «Zonas verdes» (D-222)
            priority_walk.setdefault(key, {})[PriorityKey(fit["priority"])] = _indicator(row)
        else:  # a role, need, priority or mode this code does not know (synced before deploy)
            unknown.add(_unknown_binding(fit))
    if unknown:
        log.warning("fit bindings ignored by this version: %s", sorted(unknown))
    return Indicators(
        rent,
        rent_note,
        price,
        price_estimate,
        walk,
        priority_walk,
        transit,
        rent_fill,
        rent_fill_detail,
        fill_note,
        fill_source,
    )


def zone_rent(indicators: Indicators, key: tuple[str, str]) -> ZoneRent:
    """D-242: the CM rent when it has a value, as always; else the Ministry's reference with
    what it is, where half its leases fall and who publishes it; with neither, the CM row that
    says why (or the reference's, without a CM row)."""
    published = indicators.rent.get(key)
    if published is not None and published.value is not None:
        return ZoneRent(published, indicators.rent_note)
    fill = indicators.rent_fill.get(key)
    if fill is None or fill.value is None:
        return ZoneRent(published or fill, indicators.rent_note)
    detail = indicators.rent_fill_detail.get(key, FillDetail(None, None))
    note = indicators.rent_fill_note
    if detail.typology == HOUSES_TYPOLOGY:
        note = HOUSES_NOTE if note is None else f"{HOUSES_NOTE}; {note}"
    return ZoneRent(fill, note, detail.quartiles, indicators.rent_fill_source)


def zone_price(indicators: Indicators, key: tuple[str, str]) -> tuple[IndicatorValue | None, bool]:
    """The zone's price per m² to buy and whether it is an estimate (D-234): the published
    appraised value when there is one, else the estimate; with neither, the row that says why."""
    published = indicators.price.get(key)
    if published is not None and published.value is not None:
        return published, False
    estimate = indicators.price_estimate.get(key)
    if estimate is not None and estimate.value is not None:
        return estimate, True
    return published or estimate, False


def _highlights(
    conn: Connection, rows: list[GapRowKey]
) -> tuple[dict[tuple[str, str], list[GapHighlight]], list[DatasetRef], list[str]]:
    """Each zone's status in the household's 3 rows, from the same map as GET /gaps."""
    stamp = data_stamp(conn)
    highlights: dict[tuple[str, str], list[GapHighlight]] = {}
    datasets: list[DatasetRef] = []
    warnings: list[str] = []
    for row in rows:
        for level in LEVELS:
            gap_map, row_warnings = cached_row_map(conn, level, row, stamp)
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
    zone_rows = [
        dict(r)
        for r in conn.execute(_ZONES, {"split": split}).mappings()
        if in_scope(r["code"], scenario.scope)
    ]
    levels = [level.value for level in LEVELS]
    value_rows = [dict(r) for r in conn.execute(FIT_VALUES, {"levels": levels}).mappings()]
    indicators = indicators_by_zone(value_rows)
    highlights, gap_datasets, warnings = _highlights(conn, highlight_rows(scenario))
    trips = commutes(conn, scenario.anchors)
    zones = []
    for row in zone_rows:
        key = (row["level"], row["code"])
        zone_id = str(row["admin_unit_id"])
        price, price_estimated = zone_price(indicators, key)
        rent = zone_rent(indicators, key)
        zones.append(
            ZoneData(
                zone=zone_ref(row),
                rent=rent.rent,
                rent_note=rent.note,
                rent_range=rent.range_m2,
                rent_source=rent.source,
                price=price,
                price_estimated=price_estimated,
                walk=indicators.walk.get(key, {}),
                priority_walk=indicators.priority_walk.get(key, {}),
                transit=indicators.transit.get(key, {}),
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


def union_datasets(refs: Iterable[DatasetRef]) -> list[DatasetRef]:
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


def scenario_warnings(scenario: ScenarioState) -> list[str]:
    """What the scenario asks that the search leaves out: leisure groups in `nearby` without the
    priority «ocio» (D-236), as the API or the MCP may send them."""
    ignored = ignored_leisure(scenario)
    if not ignored:
        return []
    names = ", ".join(need.value for need in ignored)
    log.warning("leisure needs without the priority ocio ignored: %s", names)
    return [
        f"{ErrorCode.INVALID_PROFILE.value}: nearby {names} ignored: the leisure groups only "
        "count with the priority «ocio» (D-236)"
    ]


def answer(
    conn: Connection, scenario: ScenarioState, loaded: Loaded, zones_word: str = "zones"
) -> tuple[SearchResult, list[str], str | None]:
    """The result, warnings and the data version (latest computation of the values used) of
    the search over the loaded zones."""
    outcome = run_search(scenario, loaded.zones)
    warnings = [*load_warnings(loaded), *scenario_warnings(scenario)]
    if outcome.unscored_passing:
        warnings.append(
            f"{ErrorCode.INSUFFICIENT_DATA.value}: {outcome.unscored_passing} {zones_word} pass "
            "every condition but have no data for any chosen priority; they are only in all_zones"
        )
    result = SearchResult(
        scenario=scenario,
        results=outcome.results,
        near_misses=outcome.near_misses,
        all_zones=outcome.all_zones,
        reality_check=outcome.reality_check,
        datasets=union_datasets([*dataset_refs(conn, loaded.versions), *loaded.gap_datasets]),
        methodology_version=FIT_VERSION,
    )
    data_version = max(loaded.computed).date().isoformat() if loaded.computed else None
    return result, warnings, data_version
