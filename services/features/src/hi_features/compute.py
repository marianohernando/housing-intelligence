"""Dispatch FeatureSpec.formula.method to a pure method and persist feature_value rows."""

from collections.abc import Callable
from typing import Any

import pandas as pd
from sqlalchemy import Engine, delete, insert
from sqlalchemy.orm import Session

from hi_contracts.catalog import FeatureSpec
from hi_db.models import FeatureValue
from hi_domain.geo.codes import admin_unit_id
from hi_features import loaders, methods

Method = Callable[[Engine, dict[str, Any]], pd.DataFrame]


def _metric_value(engine: Engine, f: dict[str, Any]) -> pd.DataFrame:
    return methods.metric_value(
        loaders.observations(engine, f["metric"]), f.get("dims", {}), f.get("confidence", 1.0)
    )


def _metric_share(engine: Engine, f: dict[str, Any]) -> pd.DataFrame:
    obs = loaders.observations(engine, f["metric"])
    return methods.metric_share(obs, f["numerator"], f["denominator"], f.get("confidence", 1.0))


def _metric_weighted_mean(engine: Engine, f: dict[str, Any]) -> pd.DataFrame:
    obs = loaders.observations(engine, f["metric"])
    return methods.metric_weighted_mean(obs, f["dim"], f["weights"], f.get("confidence", 1.0))


def _places_per_population(engine: Engine, f: dict[str, Any]) -> pd.DataFrame:
    return methods.places_per_population(
        loaders.places(engine, f["category"]),
        loaders.observations(engine, f["population_metric"]),
        f["population_dims"],
        float(f["per"]),
        subcategories=f.get("subcategories"),
        attributes=f.get("attributes"),
        small_population=float(f.get("small_population_threshold", 0)),
    )


def _place_attribute_per_population(engine: Engine, f: dict[str, Any]) -> pd.DataFrame:
    return methods.place_attribute_per_population(
        loaders.places(engine, f["category"]),
        loaders.observations(engine, f["population_metric"]),
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


def compute(engine: Engine, spec: FeatureSpec) -> pd.DataFrame:
    formula = spec.formula.model_dump()
    method = METHODS.get(formula["method"])
    if method is None:
        msg = f"{spec.feature_id}: no implementation for method {formula['method']!r}"
        raise KeyError(msg)
    return method(engine, formula)


ADMIN_LEVELS = frozenset({"municipio", "distrito", "barrio", "seccion_censal"})


def _level(spec: FeatureSpec, record: dict[str, Any]) -> str:
    """A method may return rows at another level (e.g. the regional reference)."""
    level = record.get("territory_level")
    return level if isinstance(level, str) else spec.geo_level.value


def _admin_unit(level: str, code: str) -> str | None:
    return admin_unit_id(level, code) if level in ADMIN_LEVELS else None


def persist(engine: Engine, spec: FeatureSpec, result: pd.DataFrame) -> int:
    versions = loaders.last_valid_versions(engine, [s.dataset_id for s in spec.sources])
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
            "inputs": {"dataset_versions": versions, "method": spec.formula.method},
        }
        for r in records
    ]
    with Session(engine) as session, session.begin():
        session.execute(delete(FeatureValue).where(FeatureValue.feature_id == spec.feature_id))
        if rows:
            session.execute(insert(FeatureValue), rows)
    return len(rows)
