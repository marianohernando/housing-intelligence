"""Gate 3: every computed feature satisfies the invariants its dictionary entry declares."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import (
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
    PointsPipeline,
)
from hi_features.compute import METHODS, compute, persist
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.places.run import run_places_pipeline
from hi_ingestion.pipelines.stat_tables.run import run_metric_pipeline

pytestmark = pytest.mark.db
GOLDEN = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden"
INVARIANTS = {
    "range_0_100": (0.0, 100.0),
    "range_1_5": (1.0, 5.0),
    "non_negative": (0.0, float("inf")),
    "positive": (1e-12, float("inf")),
}


@pytest.fixture(scope="module")
def fixtures_ingested(
    published: RunSummary, migrated_engine: Engine, tmp_path_factory: pytest.TempPathFactory
) -> None:
    assert published.status == "SUCCESS"
    catalog = load_catalog()
    tmp = tmp_path_factory.mktemp("features")
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if isinstance(spec, PointsPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "places_sample" / f"{dataset_id}.csv")
            result = run_places_pipeline(
                migrated_engine, catalog, spec, src, evidence_root=None, data_dir=tmp
            )
        elif isinstance(spec, CmStatTablePipeline | CmPostcodeConceptPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "stat_sample" / f"{dataset_id}.csv")
            result = run_metric_pipeline(
                migrated_engine, catalog, spec, src, evidence_root=None, data_dir=tmp
            )
        else:
            continue
        assert result.status in {"SUCCESS", "SKIPPED"}, (dataset_id, result.quality)


def test_features_satisfy_declared_invariants(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    catalog = load_catalog()
    computed = 0
    for spec in catalog.features.values():
        if spec.formula.method not in METHODS:
            continue
        result = compute(migrated_engine, spec)
        persist(migrated_engine, spec, result)
        computed += 1
        values = [v for v in result["value"].tolist() if v is not None and v == v]
        assert values, f"{spec.feature_id}: no value computed on fixtures"
        for label in spec.tests:
            if label in INVARIANTS:
                low, high = INVARIANTS[label]
                assert all(low <= v <= high for v in values), (spec.feature_id, label)
    assert computed >= 12


def test_feature_rows_respect_null_contract(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    with migrated_engine.connect() as conn:
        broken = conn.execute(
            text("SELECT count(*) FROM feature_value WHERE (value IS NULL) = (null_reason IS NULL)")
        ).scalar()
        no_lineage = conn.execute(
            text("SELECT count(*) FROM feature_value WHERE NOT (inputs ? 'dataset_versions')")
        ).scalar()
    assert broken == 0
    assert no_lineage == 0
