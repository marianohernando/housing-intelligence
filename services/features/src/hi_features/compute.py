"""Dispatch FeatureSpec.formula.method to a pure method and persist feature_value rows.

A feature is computed at its `geo_level` and, when `formula.levels` declares overrides (e.g.
districts with their own population metric), once more per extra level. An override replaces
the keys it names (a shallow merge: unused keys of the base formula are simply ignored). The
regional reference only comes from the base level.
"""

from collections.abc import Callable, Mapping
from itertools import pairwise
from typing import Any

import pandas as pd
from sqlalchemy import Engine, delete, insert
from sqlalchemy.orm import Session

from hi_contracts.catalog import FeatureSpec
from hi_db.models import FeatureValue
from hi_domain.geo.codes import admin_unit_id
from hi_features import fca, loaders, methods, walk

Method = Callable[[Engine, dict[str, Any], str], pd.DataFrame]


def _factors(engine: Engine, spec: Mapping[str, Any]) -> methods.NewContractFactors:
    return methods.new_contract_factors(
        loaders.observations(engine, spec["rent_metric"], spec["level"]),
        loaders.observations(engine, spec["area_metric"], spec["level"]),
    )


def new_contracts(
    engine: Engine, f: Mapping[str, Any]
) -> tuple[methods.NewContractFactors, str | None] | None:
    """D-228: the factors of the leases signed in the year, plus the fallback territory's under
    its own code (e.g. the region «28» for a municipio without a table of its own)."""
    spec = f.get("new_contracts")
    if not spec:
        return None
    factors = _factors(engine, spec)
    fallback = spec.get("fallback")
    if not fallback:
        return factors, None
    other = _factors(engine, {**spec, **fallback})
    code = str(fallback["code"])
    merged = dict(factors.factors)
    if code in other.factors:
        merged[code] = other.factors[code]
    return methods.NewContractFactors(merged, factors.period), code


def _metric_value(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    result = methods.metric_value(
        loaders.observations(engine, f["metric"], level),
        f.get("dims", {}),
        f.get("confidence", 1.0),
    )
    adjust = new_contracts(engine, f)
    return result if adjust is None else methods.apply_new_contract_factors(result, *adjust)


def _metric_share(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    obs = loaders.observations(engine, f["metric"], level)
    return methods.metric_share(obs, f["numerator"], f["denominator"], f.get("confidence", 1.0))


def _metric_weighted_mean(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    obs = loaders.observations(engine, f["metric"], level)
    return methods.metric_weighted_mean(obs, f["dim"], f["weights"], f.get("confidence", 1.0))


def _places_per_population(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    return methods.places_per_population(
        loaders.places(engine, f["category"], level),
        loaders.observations(engine, f["population_metric"], level),
        f["population_dims"],
        float(f["per"]),
        subcategories=f.get("subcategories"),
        attributes=f.get("attributes"),
        small_population=float(f.get("small_population_threshold", 0)),
    )


def _place_attribute_per_population(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    return methods.place_attribute_per_population(
        loaders.places(engine, f["category"], level),
        loaders.observations(engine, f["population_metric"], level),
        f["population_dims"],
        float(f["per"]),
        f["attribute"],
        subcategories=f.get("subcategories"),
        small_population=float(f.get("small_population_threshold", 0)),
    )


def _metric_ratio(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    return methods.metric_ratio(
        loaders.observations(engine, f["numerator_metric"], level),
        f["numerator_dims"],
        loaders.observations(engine, f["denominator_metric"], level),
        f["denominator_dims"],
        float(f["per"]),
        small_population=float(f.get("small_population_threshold", 0)),
        confidence=float(f.get("confidence", 1.0)),
    )


def _not_published(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    """The zones of the level are those of `territories_metric` (e.g. the padrón districts)."""
    return methods.not_published(loaders.observations(engine, f["territories_metric"], level))


def _postcode_weighted_mean(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    """CORE-006: districts from postcode values, weighted by the places that carry each code;
    D-228: each postcode adjusted to the leases signed in the year before the mean."""
    adjust = new_contracts(engine, f)
    fallback = None if adjust is None or adjust[1] is None else adjust[0].factors.get(adjust[1])
    municipio = str(f["postcode_municipio"])
    few = f.get("few_places") or {}  # D-232: barrios, with far fewer places than a district
    return methods.postcode_weighted_mean(
        loaders.observations(engine, f["metric"], "codigo_postal"),
        loaders.place_postcodes(engine, list(f["postcode_attributes"]), municipio, level),
        f.get("dims", {}),
        float(f.get("confidence", 1.0)),
        new_contracts=None if adjust is None else (adjust[0], fallback),
        zones=[z for z in walk.zone_codes(engine, level) if z.startswith(municipio)],
        min_places=float(few.get("below", 0)),
        few_places_confidence=float(few.get("max_confidence", 1.0)),
    )


# D-234: the zones a published value is shared out to, each level anchored to the one above;
# a zone's parent is a prefix of its code (28079 -> 2807906 -> 28079065).
SHARE_OUT_CHAIN = ("municipio", "distrito", "barrio")
CODE_DIGITS = {"municipio": 5, "distrito": 7}


def _anchored_relative_value(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    """The anchor metric's value (a city's appraised value) shared out level by level down to
    `level`: districts anchored to their municipio, barrios to their district's estimate."""
    chain = SHARE_OUT_CHAIN[SHARE_OUT_CHAIN.index(f["anchor_level"]) :]
    if level not in chain[1:]:
        msg = f"a {f['anchor_level']} value is shared out to {list(chain[1:])}, not to {level!r}"
        raise ValueError(msg)
    anchor, period = methods.latest_values(
        loaders.observations(engine, f["anchor_metric"], f["anchor_level"])
    )
    result = methods.result_frame([])
    for parent, step in pairwise(chain):
        value, _ = methods.latest_values(loaders.observations(engine, f["numerator_metric"], step))
        area, _ = methods.latest_values(loaders.observations(engine, f["denominator_metric"], step))
        weight, _ = methods.latest_values(loaders.observations(engine, f["weight_metric"], step))
        ratio = {c: value[c] / area[c] for c in value.keys() & area.keys() if area[c] > 0}
        zones = sorted(value.keys() | area.keys() | weight.keys())
        result = methods.anchored_relative_value(
            ratio,
            weight,
            anchor,
            zones,
            CODE_DIGITS[parent],
            period,
            float(f.get("confidence", 1.0)),
        )
        if step == level:
            break
        known = result.loc[result["value"].notna()]
        anchor = dict(zip(known["territory_code"], known["value"].astype(float), strict=True))
    return result


def _network_walk_time(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    """CORE-005: walking access to the nearest destination of a kind, by zone."""
    version = walk.network_version(engine)
    origins = walk.origins(engine, version.path, tuple(f["origin_highways"]))
    distance = walk.distances(
        engine,
        version.path,
        f["destination_category"],
        tuple(f.get("subcategories") or ()),
        walk.frozen_attributes(f.get("attributes")),
    )
    settings = methods.WalkSettings(
        statistic=f["statistic"],
        speed_m_per_min=float(f["speed_kmh"]) * 1000 / 60,
        within_min=float(f.get("within_minutes", 0)),
        base_confidence=float(f.get("confidence", 1.0)),
        min_street_m=float(f["min_street_m"]),
    )
    return methods.walk_access(
        walk.zone_of_node(origins.section, level, walk.section_parents(engine, level)),
        origins.weight,
        distance[origins.node],
        walk.zone_codes(engine, level),
        version.observed,
        settings,
    )


def _two_step_fca(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    """D-217: capacity reachable on foot per person (2SFCA), by zone."""
    return fca.fca_feature(engine, f, level, walk.network_version(engine).observed)


METHODS: dict[str, Method] = {
    "metric_value": _metric_value,
    "metric_share": _metric_share,
    "metric_weighted_mean": _metric_weighted_mean,
    "places_per_population": _places_per_population,
    "place_attribute_per_population": _place_attribute_per_population,
    "network_walk_time": _network_walk_time,
    "metric_ratio": _metric_ratio,
    "not_published": _not_published,
    "postcode_weighted_mean": _postcode_weighted_mean,
    "two_step_fca": _two_step_fca,
    "anchored_relative_value": _anchored_relative_value,
}


def extra_levels(spec: FeatureSpec) -> dict[str, dict[str, Any]]:
    return dict((spec.formula.model_extra or {}).get("levels") or {})


def combine_levels(base: pd.DataFrame, extra: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Rows of each extra level, tagged with it; their own regional reference is dropped."""
    frames = [base]
    for level, rows in extra.items():
        own = rows.loc[rows["territory_level"].isna()].copy()
        own["territory_level"] = level
        frames.append(own)
    non_empty = [frame for frame in frames if not frame.empty]
    return pd.concat(non_empty, ignore_index=True) if non_empty else base


def compute(engine: Engine, spec: FeatureSpec) -> pd.DataFrame:
    formula = spec.formula.model_dump()
    levels = formula.pop("levels", None) or {}
    base = _run(spec, formula, engine, spec.geo_level.value)
    extra = {
        level: _run(spec, {**formula, **override}, engine, level)
        for level, override in levels.items()
    }
    combined = combine_levels(base, extra)
    if spec.geo_level.value == "municipio":
        zones = walk.zone_codes(engine, "municipio")
        combined = methods.fill_missing_zones(combined, zones, "municipio")
    if "category" not in formula:
        return combined
    shares = loaders.section_share(engine, formula["category"])
    for level in extra:
        combined = scale_by_section_share(combined, shares, level)
    return combined


def scale_by_section_share(
    rows: pd.DataFrame, share_by_municipio: Mapping[str, float], level: str = "distrito"
) -> pd.DataFrame:
    """Places are assigned to sub-municipal zones through their census section. Where some
    places of a municipio have none, its zones keep their value with confidence times the
    share of places that do (a missing place must not read as a sure 0)."""
    out = rows.copy()
    factors = [
        share_by_municipio.get(str(code)[:5], 1.0) if row_level == level else 1.0
        for code, row_level in zip(out["territory_code"], out["territory_level"], strict=True)
    ]
    out["confidence"] = out["confidence"] * factors
    return out


def _run(spec: FeatureSpec, formula: dict[str, Any], engine: Engine, level: str) -> pd.DataFrame:
    """A level override may also change the method (a published mean instead of a computed one)."""
    method = METHODS.get(formula["method"])
    if method is None:
        msg = f"{spec.feature_id}: no implementation for method {formula['method']!r}"
        raise KeyError(msg)
    return method(engine, formula, level)


ADMIN_LEVELS = frozenset({"municipio", "distrito", "barrio", "seccion_censal"})


def _level(spec: FeatureSpec, record: dict[str, Any]) -> str:
    """A method may return rows at another level (e.g. the regional reference)."""
    level = record.get("territory_level")
    return level if isinstance(level, str) else spec.geo_level.value


def pass_level(spec: FeatureSpec, row_level: str) -> str:
    """The computation a row comes from: its extra level, or the base one (region included)."""
    return row_level if row_level in extra_levels(spec) else spec.geo_level.value


def effective_method(spec: FeatureSpec, row_level: str) -> str:
    """The method a row was computed with: a level override may change it (e.g. not_published)."""
    override = extra_levels(spec).get(pass_level(spec, row_level), {})
    return str(override.get("method", spec.formula.method))


def versions_by_pass(spec: FeatureSpec, versions: dict[str, str]) -> dict[str, dict[str, str]]:
    passes = [spec.geo_level.value, *extra_levels(spec)]
    return {
        level: {
            s.dataset_id: versions[s.dataset_id]
            for s in spec.sources
            if s.dataset_id in versions and (s.levels is None or level in s.levels)
        }
        for level in passes
    }


def _admin_unit(level: str, code: str) -> str | None:
    return admin_unit_id(level, code) if level in ADMIN_LEVELS else None


def _counts(record: dict[str, Any]) -> dict[str, Any]:
    """The counts behind a per-population ratio, when the method gives them (D-213)."""
    numerator, denominator = record.get("numerator"), record.get("denominator")
    if numerator is None or denominator is None or pd.isna(numerator) or pd.isna(denominator):
        return {}
    return {"counts": {"numerator": float(numerator), "denominator": float(denominator)}}


def _adjustment(record: dict[str, Any]) -> dict[str, Any]:
    """How the published value was adjusted (D-228), kept next to the counts."""
    adjustment = record.get("adjustment")
    return {"new_contracts": adjustment} if isinstance(adjustment, dict) else {}


def persist(engine: Engine, spec: FeatureSpec, result: pd.DataFrame) -> int:
    versions = versions_by_pass(
        spec, loaders.last_valid_versions(engine, [s.dataset_id for s in spec.sources])
    )
    records: list[dict[str, Any]] = result.to_dict("records")  # pyright: ignore[reportAssignmentType]
    rows = [
        {
            "feature_id": spec.feature_id,
            "feature_version": spec.version,
            "territory_level": _level(spec, r),
            "territory_code": r["territory_code"],
            "admin_unit_id": _admin_unit(_level(spec, r), r["territory_code"]),
            "period_start": r["period_start"],
            "value": None if r["value"] is None or pd.isna(r["value"]) else float(r["value"]),
            "null_reason": r["null_reason"] if isinstance(r["null_reason"], str) else None,
            "confidence": float(r["confidence"]),
            "inputs": {
                "dataset_versions": versions[pass_level(spec, _level(spec, r))],
                "method": effective_method(spec, _level(spec, r)),
            }
            | _counts(r)
            | _adjustment(r),
        }
        for r in records
    ]
    with Session(engine) as session, session.begin():
        session.execute(delete(FeatureValue).where(FeatureValue.feature_id == spec.feature_id))
        if rows:
            session.execute(insert(FeatureValue), rows)
    return len(rows)
