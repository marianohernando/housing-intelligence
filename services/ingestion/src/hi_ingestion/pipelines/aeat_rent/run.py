"""Agencia Tributaria rent comparison tables (aeat_rent_comparison) on the generic runner."""

from pathlib import Path

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import AeatRentComparisonPipeline, CsvFormat
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.aeat_rent.normalize import normalize, parse_html
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import Observations
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import known_municipios, write_silver

PARSER_VERSION = "aeat_rent-1.0.0"


def quality(
    obs: Observations, spec: AeatRentComparisonPipeline, municipios: set[str], catalog: Catalog
) -> QualityReport:
    """The checks of the statistical tables plus the size of the table in scope: a table cut
    or reshaped by the publisher stops the pipeline instead of publishing half of it."""
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}
    report = run_quality(obs, metrics, municipios)
    in_scope = obs.frame.loc[obs.frame["territory_level"] == spec.level, "territory_code"]
    zones = int(in_scope.nunique())
    report.checks.append(
        CheckResult(
            "rows_in_scope",
            True,
            spec.min_rows <= zones <= spec.max_rows,
            {"zones": zones, "min": spec.min_rows, "max": spec.max_rows},
        )
    )
    if spec.region_label is not None:  # the fallback factor of municipios without a table
        region = int((obs.frame["territory_level"] == "ccaa").sum())
        report.checks.append(
            CheckResult("region_row_present", True, region > 0, {"observations": region})
        )
    return report


def aeat_steps(
    engine: Engine, catalog: Catalog, spec: AeatRentComparisonPipeline
) -> PipelineSteps[Observations]:
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # unused: the HTML is read by `parse`
        resource_role=spec.resource_role,
        parse=parse_html,
        normalize=lambda frame: normalize(frame, spec),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: quality(obs, spec, known_municipios(engine), catalog).to_dict(),
        counts=lambda obs: row_counts(obs.frame) | {"out_of_scope": obs.out_of_window},
        write_silver=write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, spec.metric_ids(), version_id)
        },
    )


def run_aeat_rent_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: AeatRentComparisonPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        aeat_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
