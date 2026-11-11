"""Dispatch FeatureSpec.formula.method to a pure method and persist feature_value rows.

A feature is computed at its `geo_level` and, when `formula.levels` declares overrides (e.g.
districts with their own population metric), once more per extra level with the same method.
The regional reference only comes from the base level.
"""

from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd
from sqlalchemy import Engine, delete, insert
from sqlalchemy.orm import Session

from hi_contracts.catalog import FeatureSpec
from hi_db.models import FeatureValue
from hi_domain.geo.codes import admin_unit_id
from hi_features import loaders, methods

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


METHODS: dict[str, Method] = {
    "metric_value": _metric_value,
    "metric_share": _metric_share,
    "metric_weighted_mean": _metric_weighted_mean,
    "places_per_population": _places_per_population,
    "place_attribute_per_population": _place_attribute_per_population,
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
    return combine_levels(base, extra)


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
                "method": spec.formula.method,
            },
        }
        for r in records
    ]
    with Session(engine) as session, session.begin():
        session.execute(delete(FeatureValue).where(FeatureValue.feature_id == spec.feature_id))
        if rows:
            session.execute(insert(FeatureValue), rows)
    return len(rows)
