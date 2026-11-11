"""Pure feature methods over pandas frames. Missing inputs propagate as explicit null reasons.

Observation frame columns: territory_code, period_start, dims (dict), value, null_reason.
Place frame columns: municipio_ine, subcategory, attributes (dict).
Result columns: territory_code, period_start, value, null_reason, confidence and, when a row is
not at the feature's own level (the regional reference), territory_level.
"""

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import NullReason

RESULT_COLUMNS = [
    "territory_code",
    "period_start",
    "value",
    "null_reason",
    "confidence",
    "territory_level",
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


def _place_filter(
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
            out.append(_ok(code, period, per * totals.get(code, 0.0) / population, conf))
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
    row = _ok(
        REGION_CODE,
        max(period for period, _, _ in pop.values()),
        per * sum(totals.get(code, 0.0) for code in known) / population,
        len(known) / len(pop) * weighted,
    )
    return row | {"territory_level": REGION_LEVEL}


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
    for record in _place_filter(places, subcategories, attributes):
        code = record["territory_code"]
        if code:
            counts[code] = counts.get(code, 0.0) + 1.0
    return _per_population(
        counts, _population(population, population_dims), per, {}, small_population
    )


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
    for record in _place_filter(places, subcategories, None):
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
