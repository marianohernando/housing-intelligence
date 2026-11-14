"""The search inside one district of Madrid (D-232, POST /api/v1/search/barrios): its barrios
ranked by the same engine as POST /search (hi_domain.search), and the same over every barrio
of Madrid capital for POST /search with `scope: madrid` (D-238). Each barrio brings its own
walking minutes and rent of its postcodes; its trip by public transport is that of its own
sections, or its district's when the barrio is missing from the matrix (said in the fact, with
lower confidence). Parameterised SQL only, no feature id here.
"""

from sqlalchemy import Connection, text

from hi_api.services.commute import commutes
from hi_api.services.gaps import ZoneNotFoundError, dataset_refs
from hi_api.services.search import (
    FIT_VALUES,
    Loaded,
    indicators_by_zone,
    load_warnings,
    union_datasets,
    zone_ref,
)
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.public import BarrioSearchResult, IndicatorValue, ScenarioState, ZoneRef
from hi_domain.fit import FIT_VERSION, Commute, ZoneData
from hi_domain.search import SPLIT_BY_DISTRICT, run_search

# A barrio without a trip of its own takes its district's, which stands for the whole district:
# its confidence is the district's times this factor, and it never decides a trip limit.
DISTRICT_TRIP_CONFIDENCE = 0.8
DISTRICT_TRIP_NOTE = "trayecto medido para todo el distrito, no solo para este barrio"
# Why a barrio has no rent, by the null reason of its row (hi_features postcode_weighted_mean).
RENT_MISSING = {
    NullReason.SOURCE_NO_COVERAGE.value: (
        "Sin datos de alquiler para este barrio: el alquiler se publica por código postal y "
        "ningún colegio, centro de salud o centro social del barrio lo lleva en su dirección"
    ),
    NullReason.SOURCE_MISSING.value: (
        "Sin datos de alquiler para este barrio: la fuente no publica el alquiler de los "
        "códigos postales de sus colegios, centros de salud y centros sociales"
    ),
}
RENT_UNKNOWN = "Sin datos de alquiler para este barrio"
RENT_NOT_COMPUTED = "Sin datos de alquiler para este barrio todavía"

_UNITS = """
    SELECT u.level, u.code_official AS code, u.admin_unit_id, u.name, u.parent_admin_unit_id,
           m.code_official AS municipio_ine, m.name AS municipio_name,
           ST_X(u.c) AS lon, ST_Y(u.c) AS lat
      FROM (SELECT *, ST_PointOnSurface(geom_4326) AS c FROM geo_admin_unit
             WHERE {where}) u
      LEFT JOIN geo_admin_unit m
        ON m.level = 'municipio' AND m.code_official = left(u.code_official, 5)
     ORDER BY u.code_official
"""
_DISTRICT = text(_UNITS.format(where="level = 'distrito' AND code_official = :code"))
_BARRIOS = text(_UNITS.format(where="level = 'barrio' AND parent_admin_unit_id = :district"))
_CAPITAL_BARRIOS = text(
    _UNITS.format(where="level = 'barrio' AND left(code_official, 5) = ANY(:split)")
)


def rent_missing(rent: IndicatorValue | None) -> str | None:
    """Why the barrio has no rent, in plain words; None when it has one."""
    if rent is None:
        return RENT_NOT_COMPUTED
    if rent.value is not None:
        return None
    return RENT_MISSING.get(str(rent.null_reason), RENT_UNKNOWN)


def borrowed_trips(
    by_zone: dict[int, dict[str, Commute]], barrio_id: str, district_id: str
) -> tuple[dict[int, Commute], bool]:
    """The barrio's own trip to each place of work, else its district's (declared)."""
    trips: dict[int, Commute] = {}
    borrowed = False
    for i, by in by_zone.items():
        if barrio_id in by:
            trips[i] = by[barrio_id]
        elif district_id in by:
            own = by[district_id]
            trips[i] = Commute(
                own.minutes, own.confidence * DISTRICT_TRIP_CONFIDENCE, DISTRICT_TRIP_NOTE
            )
            borrowed = True
    return trips, borrowed


def district(conn: Connection, code: str) -> ZoneRef:
    row = conn.execute(_DISTRICT, {"code": code}).mappings().first()
    if row is None:
        msg = f"no district of Madrid with code {code}"
        raise ZoneNotFoundError(msg)
    return zone_ref(dict(row))


def load_barrios(conn: Connection, scenario: ScenarioState, parent: ZoneRef | None) -> Loaded:
    """The barrios of one district, or with no `parent` those of the whole capital (D-238)."""
    if parent is None:
        found = conn.execute(_CAPITAL_BARRIOS, {"split": list(SPLIT_BY_DISTRICT)})
    else:
        found = conn.execute(_BARRIOS, {"district": parent.admin_unit_id})
    rows = [dict(r) for r in found.mappings()]
    codes = {str(r["code"]) for r in rows}
    level = TerritoryLevel.BARRIO.value
    value_rows = [
        dict(r)
        for r in conn.execute(FIT_VALUES, {"levels": [level]}).mappings()
        if r["territory_code"] in codes
    ]
    indicators = indicators_by_zone(value_rows)
    trips = commutes(conn, scenario.anchors)
    zones: list[ZoneData] = []
    borrowed = 0
    for row in rows:
        key = (level, str(row["code"]))
        rent = indicators.rent.get(key)
        commute, from_district = borrowed_trips(
            trips.by_zone, str(row["admin_unit_id"]), str(row["parent_admin_unit_id"])
        )
        borrowed += from_district
        zones.append(
            ZoneData(
                zone=zone_ref(row),
                rent=rent,
                rent_note=indicators.rent_note,
                rent_missing=rent_missing(rent),
                price=indicators.price.get(key),
                walk=indicators.walk.get(key, {}),
                priority_walk=indicators.priority_walk.get(key, {}),
                transit=indicators.transit.get(key, {}),
                commute=commute,
            )
        )
    versions: dict[str, str] = dict(trips.versions)
    for row in value_rows:
        versions.update(row["inputs"].get("dataset_versions", {}))
    return Loaded(
        zones,
        versions,
        [row["computed_at"] for row in value_rows],
        [],
        barrio_warnings(len(rows), bool(value_rows), borrowed, whole_capital=parent is None),
        trips.unresolved,
        dict(trips.versions),
    )


def barrio_warnings(
    barrios: int, indicators: bool, borrowed: int, *, whole_capital: bool = False
) -> list[str]:
    insufficient = ErrorCode.INSUFFICIENT_DATA.value
    warnings: list[str] = []
    if not barrios:  # never an empty answer that looks complete
        where = "Madrid capital" if whole_capital else "this district"
        warnings.append(f"{insufficient}: no barrio of {where} is in the geography")
    elif not indicators:
        warnings.append(
            f"{insufficient}: no indicator by barrio has been computed yet, so every condition "
            "of every barrio is UNKNOWN"
        )
    if borrowed:
        warnings.append(
            f"{insufficient}: {borrowed} barrios have no trip of their own by public transport; "
            "they take the trip measured for the whole district, with lower confidence, and a "
            "trip limit is UNKNOWN for them"
        )
    return warnings


def search_barrios(
    conn: Connection, scenario: ScenarioState, distrito: str
) -> tuple[BarrioSearchResult, list[str], str | None]:
    """The result, warnings and the data version. ZoneNotFoundError for an unknown district."""
    parent = district(conn, distrito)
    loaded = load_barrios(conn, scenario, parent)
    outcome = run_search(scenario, loaded.zones)
    warnings = load_warnings(loaded)
    if outcome.unscored_passing:
        warnings.append(
            f"{ErrorCode.INSUFFICIENT_DATA.value}: {outcome.unscored_passing} barrios pass every "
            "condition but have no data for any chosen priority; they are only in all_zones"
        )
    result = BarrioSearchResult(
        scenario=scenario,
        distrito=parent,
        results=outcome.results,
        near_misses=outcome.near_misses,
        all_zones=outcome.all_zones,
        reality_check=outcome.reality_check,
        datasets=union_datasets(dataset_refs(conn, loaded.versions)),
        methodology_version=FIT_VERSION,
    )
    data_version = max(loaded.computed).date().isoformat() if loaded.computed else None
    return result, warnings, data_version
