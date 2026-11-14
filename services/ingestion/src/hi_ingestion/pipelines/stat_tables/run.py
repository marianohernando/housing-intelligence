"""Metric pipelines (cm_stat_table, cm_postcode_concept, cm_municipio_concept) on the generic
runner."""

from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.pipeline import (
    CmMunicipioConceptPipeline,
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
)
from hi_db.models import GeoAdminUnit
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import Observations, normalize
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    QualityReport,
    expected_municipios_check,
    latest_year_complete_check,
    quarantine_empty_check,
    row_counts,
    run_quality,
)

# 1.1: cm_municipio_concept reads several concepts as a dimension and blocks on a lost row (D-235)
PARSER_VERSION = "stat_tables-1.1.0"
MetricPipeline = CmStatTablePipeline | CmPostcodeConceptPipeline | CmMunicipioConceptPipeline


def run_metric_quality(
    obs: Observations, spec: MetricPipeline, metrics: dict[str, MetricSpec], known: set[str]
) -> QualityReport:
    """A table that names its municipios by hand must publish all it declares, place every
    row it reads, and give each of them every concept in the year that is shown (D-235)."""
    base = run_quality(obs, metrics, known)
    if not isinstance(spec, CmMunicipioConceptPipeline):
        return base
    expected = set(spec.municipios.values())
    return QualityReport(
        [
            *base.checks,
            expected_municipios_check(obs.frame, spec.expected_municipios),
            quarantine_empty_check(obs.quarantine),
            latest_year_complete_check(obs.frame, spec.dimension, spec.concepts.values(), expected),
        ]
    )


def metric_counts(obs: Observations) -> dict[str, int]:
    """Rows left aside: out of the period window (stat tables) or of the concepts read (tables
    that name their municipios by hand, like the panel's `out_of_scope`)."""
    left_out = (
        {"out_of_scope": obs.out_of_scope}
        if obs.out_of_scope is not None
        else {"out_of_window": obs.out_of_window}
    )
    counts = row_counts(obs.frame) | left_out
    return counts | ({"excluded_status": obs.excluded_status} if obs.excluded_status else {})


def known_municipios(engine: Engine) -> set[str]:
    with Session(engine) as session:
        return set(
            session.scalars(
                select(GeoAdminUnit.code_official).where(GeoAdminUnit.level == "municipio")
            )
        )


def write_silver(obs: Observations, directory: Path) -> Path:
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
        quality=lambda obs: run_metric_quality(
            obs, spec, metrics, known_municipios(engine)
        ).to_dict(),
        counts=metric_counts,
        write_silver=write_silver,
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
