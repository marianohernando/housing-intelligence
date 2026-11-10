"""Metric pipelines (cm_stat_table, cm_postcode_concept) on the generic runner."""

from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog.pipeline import CmPostcodeConceptPipeline, CmStatTablePipeline
from hi_db.models import GeoAdminUnit
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import Observations, normalize
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import row_counts, run_quality

PARSER_VERSION = "stat_tables-1.0.0"
MetricPipeline = CmStatTablePipeline | CmPostcodeConceptPipeline


def known_municipios(engine: Engine) -> set[str]:
    with Session(engine) as session:
        return set(
            session.scalars(
                select(GeoAdminUnit.code_official).where(GeoAdminUnit.level == "municipio")
            )
        )


def _write_silver(obs: Observations, directory: Path) -> Path:
    path = directory / "observations.csv.gz"
    obs.frame.to_csv(path, index=False)
    return path


def metric_steps(
    engine: Engine, catalog: Catalog, spec: MetricPipeline
) -> PipelineSteps[Observations]:
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize(frame, spec),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: run_quality(obs, metrics, known_municipios(engine)).to_dict(),
        counts=lambda obs: row_counts(obs.frame),
        write_silver=_write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, spec.metric_ids(), version_id)
        },
    )


def run_metric_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MetricPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    steps = metric_steps(engine, catalog, spec)
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
