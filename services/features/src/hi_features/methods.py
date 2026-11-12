"""Pure feature methods over pandas frames. Missing inputs propagate as explicit null reasons.

Observation frame columns: territory_code, period_start, dims (dict), value, null_reason.
Place frame columns: municipio_ine, subcategory, attributes (dict).
Result columns: territory_code, period_start, value, null_reason, confidence and, when a row is
not at the feature's own level (the regional reference), territory_level.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from hi_contracts.catalog.enums import NullReason
from hi_domain.access.walk import access_confidence, summarise_zones

RESULT_COLUMNS = [
    "territory_code",
    "period_start",
    "value",
    "null_reason",
    "confidence",
    "territory_level",
    "numerator",  # counts behind a per-population ratio (GAP-001 significance, D-213)
    "denominator",
]
REGION_LEVEL = "ccaa"
REGION_CODE = "28"  # Comunidad de Madrid, as in metric_observation
DimFilter = Mapping[str, Sequence[str] | str]
ANY = "*"


def _matches(dims: Mapping[str, str], selector: DimFilter) -> bool:
    for key, wanted in selector.items():
        if wanted == ANY:
            continue
        values = [wanted] if isinstance(wanted, str) else list(wanted)
        if dims.get(key) not in values:
            return False
    return True


def latest(obs: pd.DataFrame) -> pd.DataFrame:
    if obs.empty:
        return obs
    newest = obs["period_start"].max()
    return obs.loc[[period == newest for period in obs["period_start"].tolist()]]


def _rows(obs: pd.DataFrame) -> list[dict[str, Any]]:
    return obs.to_dict("records")  # pyright: ignore[reportReturnType]


def _result(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def _null(code: str, period: Any, reason: NullReason) -> dict[str, Any]:
    return {
        "territory_code": code,
        "period_start": period,
        "value": None,
        "null_reason": reason.value,
        "confidence": 0.0,
    }


def _ok(code: str, period: Any, value: float, confidence: float = 1.0) -> dict[str, Any]:
    return {
        "territory_code": code,
        "period_start": period,
        "value": float(value),
        "null_reason": None,
        "confidence": confidence,
    }


def _sum_selected(
    records: list[dict[str, Any]], selector: DimFilter
) -> tuple[float, str | None, int]:
    """(sum, first null reason found, rows matched). Any null member makes the sum unknown."""
    total, matched = 0.0, 0
    for record in records:
        if not _matches(record["dims"], selector):
            continue
        matched += 1
        if record["value"] is None or pd.isna(record["value"]):
            return 0.0, record["null_reason"] or NullReason.UNKNOWN.value, matched
        total += float(record["value"])
    return total, None, matched


def _by_territory(obs: pd.DataFrame) -> dict[tuple[str, Any], list[dict[str, Any]]]:
    groups: dict[tuple[str, Any], list[dict[str, Any]]] = {}
    for record in _rows(latest(obs)):
        groups.setdefault((record["territory_code"], record["period_start"]), []).append(record)
    return groups


def metric_value(obs: pd.DataFrame, dims: DimFilter, confidence: float = 1.0) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for (code, period), records in _by_territory(obs).items():
        value, reason, matched = _sum_selected(records, dims)
        if matched != 1:
            out.append(
                _null(
                    code,
                    period,
                    NullReason.SOURCE_MISSING
                    if matched == 0
                    else NullReason.ESTIMATION_NOT_ALLOWED,
                )
            )
        elif reason:
            out.append(_null(code, period, NullReason(reason)))
        else:
            out.append(_ok(code, period, value, confidence))
    return _result(out)


def metric_share(
    obs: pd.DataFrame, numerator: DimFilter, denominator: DimFilter, confidence: float = 1.0
) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for (code, period), records in _by_territory(obs).items():
        num, num_reason, num_n = _sum_selected(records, numerator)
        den, den_reason, den_n = _sum_selected(records, denominator)
        if num_reason or den_reason or not num_n or not den_n:
            out.append(
                _null(
                    code,
                    period,
                    NullReason(num_reason or den_reason or NullReason.SOURCE_MISSING.value),
                )
            )
        elif den == 0:
            out.append(_null(code, period, NullReason.NOT_APPLICABLE))
        else:
            out.append(_ok(code, period, 100.0 * num / den, confidence))
    return _result(out)


def metric_weighted_mean(
    obs: pd.DataFrame, dim: str, weights: Mapping[str, float], confidence: float = 1.0
) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for (code, period), records in _by_territory(obs).items():
        members = [r for r in records if r["dims"].get(dim) in weights]
        if not members or any(r["value"] is None or pd.isna(r["value"]) for r in members):
            out.append(_null(code, period, NullReason.SOURCE_MISSING))
            continue
        count = sum(float(r["value"]) for r in members)
        if count == 0:
            out.append(_null(code, period, NullReason.NOT_APPLICABLE))
            continue
        weighted = sum(weights[r["dims"][dim]] * float(r["value"]) for r in members)
        out.append(_ok(code, period, weighted / count, confidence))
    return _result(out)


def _population(
    obs: pd.DataFrame, dims: DimFilter
) -> dict[str, tuple[Any, float | None, str | None]]:
    pop: dict[str, tuple[Any, float | None, str | None]] = {}
    for (code, period), records in _by_territory(obs).items():
        value, reason, matched = _sum_selected(records, dims)
        pop[code] = (
            period,
            None if reason or not matched else value,
            reason or (None if matched else NullReason.SOURCE_MISSING.value),
        )
    return pop


def place_filter(
    places: pd.DataFrame,
    subcategories: Sequence[str] | None,
    attributes: Mapping[str, Sequence[str]] | None,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for record in _rows(places):
        if subcategories and record["subcategory"] not in subcategories:
            continue
        attrs: dict[str, Any] = record["attributes"] or {}
        if attributes and any(attrs.get(k) not in v for k, v in attributes.items()):
            continue
        kept.append(record)
    return kept


# A destination reached at any point of its edge (a park, D-222) keeps them in its attributes.
EDGE_POINTS = "edge_points_25830"


def destination_points(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """x and y (EPSG:25830) where a walk reaches each destination: every point of its edge when
    it keeps one, otherwise its own point."""
    points: list[tuple[float, float]] = []
    for row in rows:
        edge = (row.get("attributes") or {}).get(EDGE_POINTS)
        if edge:
            points.extend((float(x), float(y)) for x, y in edge)
        else:
            points.append((float(row["x"]), float(row["y"])))
    xy = np.array(points, dtype=float).reshape(-1, 2)
    return xy[:, 0], xy[:, 1]


SMALL_POPULATION_CONFIDENCE = 0.5


def _per_population(
    totals: dict[str, float],
    pop: dict[str, tuple[Any, float | None, str | None]],
    per: float,
    confidence: dict[str, float],
    small_population: float = 0.0,
) -> pd.DataFrame:
    """Ratios over tiny denominators are unstable: they keep their value with lower confidence."""
    out: list[dict[str, Any]] = []
    for code, (period, population, reason) in sorted(pop.items()):
        if population is None:
            out.append(_null(code, period, NullReason(reason or NullReason.SOURCE_MISSING.value)))
        elif population == 0:
            out.append(_null(code, period, NullReason.NOT_APPLICABLE))
        else:  # no place in an exhaustive official register is a confirmed zero
            conf = confidence.get(code, 1.0)
            if population < small_population:
                conf = min(conf, SMALL_POPULATION_CONFIDENCE)
            count = totals.get(code, 0.0)
            row = _ok(code, period, per * count / population, conf)
            out.append(row | {"numerator": count, "denominator": population})
    region = _regional_reference(totals, pop, per, confidence)
    return _result([*out, region] if region else out)


def _regional_reference(
    totals: dict[str, float],
    pop: dict[str, tuple[Any, float | None, str | None]],
    per: float,
    confidence: dict[str, float],
) -> dict[str, Any] | None:
    """Region total over region population (GAP-001 reference), over municipios whose
    population is known; confidence is the share of municipios known times their own."""
    known = {code: p for code, (_, p, _) in pop.items() if p is not None}
    population = sum(known.values())
    if not known or population <= 0:
        return None
    weighted = sum(confidence.get(code, 1.0) * p for code, p in known.items()) / population
    count = sum(totals.get(code, 0.0) for code in known)
    row = _ok(
        REGION_CODE,
        max(period for period, _, _ in pop.values()),
        per * count / population,
        len(known) / len(pop) * weighted,
    )
    return row | {"territory_level": REGION_LEVEL, "numerator": count, "denominator": population}


def places_per_population(
    places: pd.DataFrame,
    population: pd.DataFrame,
    population_dims: DimFilter,
    per: float,
    subcategories: Sequence[str] | None = None,
    attributes: Mapping[str, Sequence[str]] | None = None,
    small_population: float = 0.0,
) -> pd.DataFrame:
    counts: dict[str, float] = {}
    for record in place_filter(places, subcategories, attributes):
        code = record["territory_code"]
        if code:
            counts[code] = counts.get(code, 0.0) + 1.0
    return _per_population(
        counts, _population(population, population_dims), per, {}, small_population
    )


def metric_ratio(
    numerator: pd.DataFrame,
    numerator_dims: DimFilter,
    denominator: pd.DataFrame,
    denominator_dims: DimFilter,
    per: float,
    small_population: float = 0.0,
    confidence: float = 1.0,
) -> pd.DataFrame:
    """per x numerator / denominator for two metrics of the same zones (e.g. dwellings over
    90 m2 per 100 households of 4 or more). Each metric uses its own latest period and the row
    carries the denominator's. A zone whose numerator is unknown or absent is unknown, never 0.
    The regional reference adds up the zones where both are known; as in places per
    population, a zone with a 0 denominator is NOT_APPLICABLE but its numerator still counts
    for the region."""
    numerators = _population(numerator, numerator_dims)
    denominators = _population(denominator, denominator_dims)
    totals: dict[str, float] = {}
    for code, (period, den, den_reason) in list(denominators.items()):
        _, num, num_reason = numerators.get(code, (None, None, NullReason.SOURCE_MISSING.value))
        if num is None:
            denominators[code] = (period, None, den_reason if den is None else num_reason)
        else:
            totals[code] = num
    shared = dict.fromkeys(denominators, confidence)
    return _per_population(totals, denominators, per, shared, small_population)


def not_published(territories: pd.DataFrame) -> pd.DataFrame:
    """One explicit SOURCE_MISSING row per zone of the level, for an indicator its sources do
    not publish there (e.g. the CM housing tables have no district rows): never 0, never an
    absent row."""
    return _result(
        [
            _null(code, period, NullReason.SOURCE_MISSING)
            for code, period in sorted(_by_territory(territories))
        ]
    )


def _postcode_values(obs: pd.DataFrame, dims: DimFilter) -> tuple[dict[str, float], Any]:
    """Latest published value of each postcode (exactly one matching row), and its period."""
    values: dict[str, float] = {}
    periods: list[Any] = []
    for (code, period), records in _by_territory(obs).items():
        value, reason, matched = _sum_selected(records, dims)
        periods.append(period)
        if matched == 1 and reason is None:
            values[str(code)] = value
    return values, max(periods) if periods else None


def postcode_weighted_mean(
    obs: pd.DataFrame, weights: pd.DataFrame, dims: DimFilter, confidence: float = 1.0
) -> pd.DataFrame:
    """A zone's value as the mean of its postcodes' values, each weighted by how many of the
    zone's geocoded places carry that postcode (CORE-006: there is no postcode geometry, so the
    places locate the postcodes; a declared proxy of where people live). The confidence is the
    base confidence times the share of that weight whose postcode publishes a value. A zone
    with none is SOURCE_NO_COVERAGE, never 0.

    `weights` columns: territory_code (the zone), postcode, weight (places)."""
    values, period = _postcode_values(obs, dims)
    out: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = weights.to_dict("records")  # pyright: ignore[reportAssignmentType]
    by_zone: dict[str, list[tuple[str, float]]] = {}
    for record in records:
        by_zone.setdefault(str(record["territory_code"]), []).append(
            (str(record["postcode"]), float(record["weight"]))
        )
    for code, members in sorted(by_zone.items()):
        total = sum(w for _, w in members)
        known = [(values[cp], w) for cp, w in members if cp in values]
        known_weight = sum(w for _, w in known)
        if not known or known_weight <= 0 or total <= 0:
            out.append(_null(code, period, NullReason.SOURCE_NO_COVERAGE))
            continue
        mean = sum(v * w for v, w in known) / known_weight
        out.append(_ok(code, period, mean, confidence * known_weight / total))
    return _result(out)


WALK_STATISTICS = ("median_minutes", "share_within")


@dataclass(frozen=True)
class WalkSettings:
    statistic: str  # one of WALK_STATISTICS
    speed_m_per_min: float
    within_min: float
    base_confidence: float
    min_street_m: float  # zones with less origin street keep confidence 0.5 at most

    def __post_init__(self) -> None:
        if self.statistic not in WALK_STATISTICS:
            msg = f"unknown walking statistic {self.statistic!r} (known: {WALK_STATISTICS})"
            raise ValueError(msg)


def _walk_rows(
    codes: Sequence[str],
    zone: NDArray[np.int64],
    weight: NDArray[np.float64],
    distance_m: NDArray[np.float64],
    period: Any,
    settings: WalkSettings,
) -> list[dict[str, Any]]:
    within_m = settings.within_min * settings.speed_m_per_min
    summary = summarise_zones(zone, weight, distance_m, len(codes), within_m)
    confidence = access_confidence(
        summary.reachable_share(),
        summary.street_m,
        settings.base_confidence,
        settings.min_street_m,
    )
    if settings.statistic == "median_minutes":
        values = summary.median_m / settings.speed_m_per_min
    else:
        values = 100.0 * summary.within_share
    rows: list[dict[str, Any]] = []
    for i, code in enumerate(codes):
        if summary.street_m[i] <= 0:  # no origin street mapped in the zone
            rows.append(_null(code, period, NullReason.SOURCE_NO_COVERAGE))
        elif summary.reachable_m[i] <= 0:  # its streets are cut off from every destination
            rows.append(_null(code, period, NullReason.UNKNOWN))
        else:
            rows.append(_ok(code, period, float(values[i]), float(confidence[i])))
    return rows


def walk_access(
    zone_of_node: NDArray[np.str_],
    weight: NDArray[np.float64],
    distance_m: NDArray[np.float64],
    zones: Sequence[str],
    period: Any,
    settings: WalkSettings,
) -> pd.DataFrame:
    """Per zone: street-weighted median minutes to the nearest destination, or % of street
    within `within_min`. Every zone gets a row (null when it has no reachable origin street),
    plus the regional reference pooling every node that lies in some zone."""
    index = {code: i for i, code in enumerate(zones)}
    zone = np.array([index.get(str(c), -1) for c in zone_of_node], dtype=np.int64)
    in_region = np.where(zone >= 0, 0, -1)
    rows = _walk_rows(zones, zone, weight, distance_m, period, settings)
    region = _walk_rows([REGION_CODE], in_region, weight, distance_m, period, settings)
    return _result([*rows, *(r | {"territory_level": REGION_LEVEL} for r in region)])


def place_attribute_per_population(
    places: pd.DataFrame,
    population: pd.DataFrame,
    population_dims: DimFilter,
    per: float,
    attribute: str,
    subcategories: Sequence[str] | None = None,
    small_population: float = 0.0,
) -> pd.DataFrame:
    """Sum a numeric attribute (e.g. authorised places). Places lacking it lower confidence."""
    sums: dict[str, float] = {}
    seen: dict[str, int] = {}
    known: dict[str, int] = {}
    for record in place_filter(places, subcategories, None):
        code = record["territory_code"]
        if not code:
            continue
        seen[code] = seen.get(code, 0) + 1
        try:
            sums[code] = sums.get(code, 0.0) + float(
                str((record["attributes"] or {}).get(attribute, "")).replace(",", ".")
            )
            known[code] = known.get(code, 0) + 1
        except ValueError:
            continue
    confidence = {code: known.get(code, 0) / n for code, n in seen.items()}
    return _per_population(
        sums, _population(population, population_dims), per, confidence, small_population
    )


# Shared with the 2SFCA features (hi_features.fca, D-217).
def population_by_code(
    obs: pd.DataFrame, dims: DimFilter
) -> dict[str, tuple[Any, float | None, str | None]]:
    return _population(obs, dims)


def null_row(code: str, period: Any, reason: NullReason) -> dict[str, Any]:
    return _null(code, period, reason)


def result_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return _result(rows)


def fill_missing_zones(result: pd.DataFrame, zones: Sequence[str], level: str) -> pd.DataFrame:
    """Every zone of `level` gets a row: one the source does not publish is SOURCE_MISSING,
    never left out (the null contract of Gate 3), dated like the rest of the level."""
    if result.empty:
        return result
    # Rows of a feature's own geo_level may leave territory_level empty (set when persisting).
    levels = (
        result["territory_level"].astype(object).where(result["territory_level"].notna(), level)
    )
    at_level = result[levels == level]
    if at_level.empty:
        return result
    period = at_level["period_start"].max()
    present = set(at_level["territory_code"].astype(str))
    missing = [
        _null(code, period, NullReason.SOURCE_MISSING) | {"territory_level": level}
        for code in zones
        if code not in present
    ]
    if not missing:
        return result
    return pd.concat([result, _result(missing)], ignore_index=True)
