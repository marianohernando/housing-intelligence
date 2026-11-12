"""madrid_district_panel pipeline on the generic runner."""

from pathlib import Path

from sqlalchemy import Engine

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.pipeline import MadridDistrictPanelPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.district_panel.normalize import normalize
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.padron.run import known_districts
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import Observations
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    QualityReport,
    district_checks,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver

PARSER_VERSION = "madrid_district_panel-1.2.0"  # 1.2: city indicators, one row per date


def run_panel_quality(
    obs: Observations,
    spec: MadridDistrictPanelPipeline,
    metrics: dict[str, MetricSpec],
    known: set[str],
) -> QualityReport:
    own = {m: metrics[m] for m in spec.metric_ids()}
    city = {spec.municipio_ine} if spec.city_indicators else set()
    base = run_quality(obs, own, known_municipios=city)
    return QualityReport(
        [*base.checks, *district_checks(obs.frame, known, spec.expected_districts)]
    )


def panel_steps(
    engine: Engine, catalog: Catalog, spec: MadridDistrictPanelPipeline
) -> PipelineSteps[Observations]:
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize(frame, spec),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: run_panel_quality(
            obs, spec, catalog.metrics, known_districts(engine, spec.municipio_ine)
        ).to_dict(),
        counts=lambda obs: row_counts(obs.frame) | {"out_of_scope": obs.out_of_window},
        write_silver=write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, spec.metric_ids(), version_id)
        },
    )


def run_panel_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MadridDistrictPanelPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        panel_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
