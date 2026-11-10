"""Facility pipelines on fixtures against the test DB (needs published admin fixture)."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.places.run import run_places_pipeline

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden" / "places_sample"
DATASETS = [
    "cm_centros_educativos",
    "cm_centros_sanitarios",
    "cm_centros_atencion_social",
    "cm_oficinas_farmacia",
]
STATS_SQL = text(
    """
    SELECT count(*) AS n,
           count(seccion_admin_unit_id) AS assigned,
           count(*) FILTER (WHERE NOT ST_IsValid(geom_4326)) AS invalid,
           count(*) FILTER (
               WHERE seccion_admin_unit_id IS NULL AND EXISTS (
                   SELECT 1 FROM geo_admin_unit u
                    WHERE u.level = 'seccion_censal' AND ST_Contains(u.geom_25830, p.geom_25830)
               )
           ) AS missed
      FROM place_master p
     WHERE official_dataset_id = :ds
    """
)


@pytest.mark.parametrize("dataset_id", DATASETS)
def test_places_published_and_assigned(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path, dataset_id: str
) -> None:
    assert published.status == "SUCCESS"
    catalog = load_catalog()
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, PointsPipeline)
    source = local_file(dataset_id, "primary", FIXTURES / f"{dataset_id}.csv")
    result = run_places_pipeline(
        migrated_engine, catalog, spec, source, evidence_root=tmp_path, data_dir=tmp_path
    )
    assert result.status in {"SUCCESS", "SKIPPED"}, result.quality
    with migrated_engine.connect() as conn:
        row = conn.execute(STATS_SQL, {"ds": dataset_id}).mappings().one()
        aliases = conn.execute(
            text("SELECT count(*) FROM place_source_alias WHERE dataset_id = :ds"),
            {"ds": dataset_id},
        ).scalar()
    assert row["n"] > 0
    assert row["invalid"] == 0
    assert row["missed"] == 0  # a place inside a section is always assigned to it
    assert aliases == row["n"]
    if dataset_id != "cm_centros_atencion_social":  # no senior service lies inside the fixture area
        assert row["assigned"] > 0
