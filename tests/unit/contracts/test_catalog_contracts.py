from typing import Any

import pytest
from pydantic import ValidationError

from hi_contracts.catalog import DatasetSpec, FeatureSpec, Scorecard, SourceSpec


def _source(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "source_id": "test_source",
        "name": "Test",
        "provider": "Test",
        "source_type": "open_data_portal",
        "api_type": "ckan",
        "license_name": "CC-BY",
        "license_status": "CLEAR",
        "attribution_text": "Fuente: test",
        "trust_tier": "A_OFFICIAL",
        "update_frequency": "daily",
        "geographic_scope": "Madrid",
        "terms_reviewed_at": "2026-10-20T00:00:00Z",
    }
    return base | overrides


def _dataset(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "dataset_id": "test_dataset",
        "source_id": "test_source",
        "name": "Test dataset",
        "domain": "health",
        "owner": "Test",
        "format": "CSV",
        "geography": "point",
        "geo": {"resolution": "point"},
        "refresh_policy": "daily",
        "license_status": "CLEAR",
        "priority": "P1",
    }
    return base | overrides


def test_valid_source() -> None:
    assert SourceSpec.model_validate(_source()).active


def test_rejected_source_cannot_be_active() -> None:
    with pytest.raises(ValidationError, match="REJECTED"):
        SourceSpec.model_validate(_source(license_status="REJECTED"))


def test_active_source_requires_review_fields() -> None:
    with pytest.raises(ValidationError, match="attribution_text"):
        SourceSpec.model_validate(_source(attribution_text=None))


def test_inactive_source_may_lack_review_fields() -> None:
    spec = SourceSpec.model_validate(_source(active=False, attribution_text=None))
    assert not spec.active


def test_p0_requires_reviewed_scorecard() -> None:
    with pytest.raises(ValidationError, match="P0 requires"):
        DatasetSpec.model_validate(_dataset(priority="P0"))
    ok = DatasetSpec.model_validate(_dataset(priority="P0", scorecard={"reviewed_by": "x"}))
    assert ok.priority == "P0"


def test_production_gate() -> None:
    with pytest.raises(ValidationError, match="PRODUCTION gate failed"):
        DatasetSpec.model_validate(_dataset(status="PRODUCTION", license_status="RESTRICTED"))


@pytest.mark.parametrize("value", [-1, 6])
def test_scorecard_range(value: int) -> None:
    with pytest.raises(ValidationError):
        Scorecard(quality=value)


def test_scorecard_pending_criteria() -> None:
    card = Scorecard(datamad_relevance=5)
    assert "datamad_relevance" not in card.pending_criteria()
    assert "quality" in card.pending_criteria()


def test_schema_alias_roundtrip() -> None:
    spec = DatasetSpec.model_validate(_dataset(schema={"primary_key": ["id"]}))
    assert spec.table_schema.primary_key == ["id"]


def test_productive_feature_requires_tests_and_limitations() -> None:
    feature: dict[str, Any] = {
        "feature_id": "pharmacy_access_walk_10m",
        "version": 1,
        "human_name": "Farmacias a 10 min",
        "domain": "health",
        "type": "derived",
        "unit": "count",
        "direction": "higher_is_better",
        "geo_level": "h3",
        "time_semantics": "current",
        "sources": [{"dataset_id": "cm_pharmacies"}],
        "formula": {"method": "network_isochrone_count"},
        "public_use": True,
    }
    with pytest.raises(ValidationError, match="need tests"):
        FeatureSpec.model_validate(feature)
    ok = FeatureSpec.model_validate(feature | {"tests": ["non_negative"], "limitations": ["x"]})
    assert ok.public_use
