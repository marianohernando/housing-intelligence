"""FETCH -> PARSE -> NORMALIZE -> QUALITY -> PUBLISH for metric pipelines."""

from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.enums import PipelineStage, RunStatus
from hi_contracts.catalog.pipeline import CmPostcodeConceptPipeline, CmStatTablePipeline
from hi_db.models import DatasetVersion, GeoAdminUnit
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.catalog.sync import sync_catalog
from hi_ingestion.pipelines.common import (
    DATA_DIR,
    RunSummary,
    evidence_dir,
    read_csv,
    rel,
    schema_hash,
    write_json,
)
from hi_ingestion.pipelines.fetch import FetchedFile, fetch_role
from hi_ingestion.pipelines.stat_tables.normalize import normalize
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import row_counts, run_quality
from hi_ingestion.pipelines.tracking import StageTracker
from hi_ingestion.pipelines.versions import (
    combined_checksum,
    is_current,
    mark_failed,
    mark_last_valid,
    register_version,
)

PARSER_VERSION = "stat_tables-1.0.0"
MetricPipeline = CmStatTablePipeline | CmPostcodeConceptPipeline


def known_municipios(engine: Engine) -> set[str]:
    with Session(engine) as session:
        codes = session.scalars(
            select(GeoAdminUnit.code_official).where(GeoAdminUnit.level == "municipio")
        )
        return set(codes)


def _metrics_for(catalog: Catalog, spec: MetricPipeline) -> dict[str, MetricSpec]:
    return {m: catalog.metrics[m] for m in spec.metric_ids()}


def run_metric_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MetricPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    sync_catalog(engine, catalog)
    source = source or fetch_role(catalog.datasets[spec.dataset_id], spec.resource_role)
    checksum = combined_checksum([source])
    tracker = StageTracker(engine, spec.dataset_id)
    summary = RunSummary("RUNNING", spec.dataset_id, checksum, tracker.correlation_id)
    with Session(engine) as session:
        current = is_current(session, spec.dataset_id, checksum, PARSER_VERSION)
        if current:
            tracker.version_id = current.id
            summary.status, summary.version_label = "SKIPPED", current.version_label
    if summary.status == "SKIPPED":
        tracker.record(
            PipelineStage.SNAPSHOT, RunStatus.SKIPPED, {"reason": "same checksum and parser"}
        )
        return summary

    with tracker.stage(PipelineStage.PARSE) as metrics:
        frame = read_csv(source.path, spec.csv)
        metrics |= {"rows": len(frame), "columns": list(frame.columns)}
    silver_dir = data_dir / "silver" / spec.dataset_id / checksum[:12]
    manifest = {
        "inputs": [source.manifest_entry()],
        "checksum": checksum,
        "parser_version": PARSER_VERSION,
    }
    write_json(silver_dir / "manifest.json", manifest)
    with Session(engine) as session, session.begin():
        version = register_version(
            session,
            source,
            checksum,
            parser_version=PARSER_VERSION,
            row_count=len(frame),
            schema_hash=schema_hash(frame),
            manifest_path=rel(silver_dir / "manifest.json"),
        )
        tracker.version_id, summary.version_label = version.id, version.version_label

    with tracker.stage(PipelineStage.NORMALIZE) as metrics:
        obs = normalize(frame, spec)
        metrics |= {"observations": len(obs.frame), "quarantined": len(obs.quarantine)}
    if len(obs.quarantine):
        quarantine = data_dir / "quarantine" / spec.dataset_id / checksum[:12] / "rows.csv"
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        obs.quarantine.to_csv(quarantine, index=False)

    with tracker.stage(PipelineStage.QUALITY_CHECK) as metrics:
        report = run_quality(obs, _metrics_for(catalog, spec), known_municipios(engine)).to_dict()
        metrics |= {
            "passed": report["passed"],
            "failed": [c["name"] for c in report["checks"] if not c["passed"]],
        }
    summary.quality, summary.counts = report, row_counts(obs.frame)
    out = evidence_dir(evidence_root, spec.dataset_id)
    if out:
        write_json(out / "quality_report.json", report)
        summary.evidence_dir = out
    if not report["passed"]:
        with Session(engine) as session, session.begin():
            mark_failed(session, tracker.version_id)
        tracker.record(
            PipelineStage.PUBLISH_SILVER, RunStatus.SKIPPED, {"reason": "quality failed"}
        )
        summary.status = "FAILED"
        return summary

    obs.frame.to_csv(silver_dir / "observations.csv.gz", index=False)
    with (
        tracker.stage(PipelineStage.PUBLISH_SILVER) as metrics,
        Session(engine) as session,
        session.begin(),
    ):
        db_version = session.get(DatasetVersion, tracker.version_id)
        assert db_version is not None  # noqa: S101 - registered above in this run
        metrics["observations"] = replace_observations(
            session, obs.frame, spec.metric_ids(), db_version.id
        )
        mark_last_valid(session, db_version, "PASSED")
    if out:
        write_json(out / "row_counts.json", summary.counts)
        write_json(
            out / "lineage.json",
            manifest
            | {
                "dataset_version": summary.version_label,
                "correlation_id": tracker.correlation_id,
                "silver": rel(silver_dir / "observations.csv.gz"),
            },
        )
    summary.status = "SUCCESS"
    return summary
