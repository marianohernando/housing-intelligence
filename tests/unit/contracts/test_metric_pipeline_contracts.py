from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from hi_contracts.catalog import MetricSpec, PipelineSpec

PIPELINE: TypeAdapter[PipelineSpec] = TypeAdapter(PipelineSpec)


def _metric(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "metric_id": "poblacion_test",
        "human_name": "x",
        "description": "x",
        "domain": "population",
        "unit": "personas",
        "aggregation_method": "sum",
        "geo_resolution_min": "municipio",
        "temporal_resolution": "annual",
        "dataset_id": "cm_test",
    }
    return base | kw


def test_sensitive_metrics_cannot_be_public() -> None:
    with pytest.raises(ValidationError, match="sensitive"):
        MetricSpec.model_validate(_metric(sensitive=True))
    assert MetricSpec.model_validate(_metric(sensitive=True, public_visible=False)).sensitive


def test_stat_table_needs_exactly_one_metric_source() -> None:
    base = {
        "kind": "cm_stat_table",
        "dataset_id": "cm_test",
        "territory_types": {"Municipios": "municipio"},
    }
    with pytest.raises(ValidationError, match="exactly one"):
        PIPELINE.validate_python(base)
    both = base | {
        "metric_id": "a_metric",
        "metric_split": {"column": "M", "metrics": {"x": "b_metric"}},
    }
    with pytest.raises(ValidationError, match="exactly one"):
        PIPELINE.validate_python(both)
    split = PIPELINE.validate_python(
        base | {"metric_split": {"column": "M", "metrics": {"x": "b_m", "y": "a_m"}}}
    )
    assert split.metric_ids() == ["a_m", "b_m"]


def test_points_status_requires_active_values() -> None:
    spec = {
        "kind": "points_csv",
        "dataset_id": "cm_test",
        "category": "education",
        "id_column": "id",
        "subcategory_column": "tipo",
        "x_column": "x",
        "y_column": "y",
        "status_column": "estado",
    }
    with pytest.raises(ValidationError, match="active_values"):
        PIPELINE.validate_python(spec)
    assert PIPELINE.validate_python(spec | {"active_values": ["ALTA"]}).kind == "points_csv"


def test_unknown_kind_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PIPELINE.validate_python({"kind": "scrape_google", "dataset_id": "cm_test"})
