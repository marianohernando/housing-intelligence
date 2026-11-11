"""Dispatch FeatureSpec.formula.method to a pure method and persist feature_value rows.

A feature is computed at its `geo_level` and, when `formula.levels` declares overrides (e.g.
districts with their own population metric), once more per extra level. An override replaces
the keys it names (a shallow merge: unused keys of the base formula are simply ignored). The
regional reference only comes from the base level.
"""

from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd
from sqlalchemy import Engine, delete, insert
from sqlalchemy.orm import Session

from hi_contracts.catalog import FeatureSpec
from hi_db.models import FeatureValue
from hi_domain.geo.codes import admin_unit_id
from hi_features import loaders, methods, walk

Method = Callable[[Engine, dict[str, Any], str], pd.DataFrame]


def _metric_value(engine: Engine, f: dict[str, Any], level: str) -> pd.DataFrame:
    return methods.metric_value(
        loaders.observations(engine, f["metric"], level),
        f.get("dims", {}),
        f.get("confidence", 1.0),
    )


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
        walk.zone_of_node(origins.section, level),
        origins.weight,
        distance[origins.node],
        walk.zone_codes(engine, level),
        version.observed,
        settings,
    )


METHODS: dict[str, Method] = {
    "metric_value": _metric_value,
    "metric_share": _metric_share,
    "metric_weighted_mean": _metric_weighted_mean,
    "places_per_population": _places_per_population,
    "place_attribute_per_population": _place_attribute_per_population,
    "network_walk_time": _network_walk_time,
    "metric_ratio": _metric_ratio,
    "not_published": _not_published,
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
            },
        }
        for r in records
    ]
    with Session(engine) as session, session.begin():
        session.execute(delete(FeatureValue).where(FeatureValue.feature_id == spec.feature_id))
        if rows:
            session.execute(insert(FeatureValue), rows)
    return len(rows)
