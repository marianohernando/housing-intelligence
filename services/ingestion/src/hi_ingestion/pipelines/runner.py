"""Generic FETCH -> PARSE -> NORMALIZE -> QUALITY -> PUBLISH orchestration for CSV pipelines."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import PipelineStage, RunStatus
from hi_contracts.catalog.pipeline import CsvFormat
from hi_db.models import DatasetVersion
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
from hi_ingestion.pipelines.tracking import StageTracker
from hi_ingestion.pipelines.versions import (
    combined_checksum,
    is_current,
    mark_failed,
    mark_last_valid,
    register_version,
)


@dataclass(frozen=True)
class PipelineSteps[T]:
    parser_version: str
    csv: CsvFormat
    resource_role: str
    normalize: Callable[[pd.DataFrame], T]
    quarantine: Callable[[T], pd.DataFrame]
    quality: Callable[[T], dict[str, Any]]
    counts: Callable[[T], dict[str, Any]]
    write_silver: Callable[[T, Path], Path]
    publish: Callable[[Session, T, uuid.UUID], dict[str, Any]]


def _skip_if_current(
    engine: Engine, tracker: StageTracker, summary: RunSummary, parser: str
) -> bool:
    with Session(engine) as session:
        current = is_current(session, summary.dataset_id, summary.checksum, parser)
        if current is None:
            return False
        tracker.version_id, summary.version_label = current.id, current.version_label
    tracker.record(
        PipelineStage.SNAPSHOT, RunStatus.SKIPPED, {"reason": "same checksum and parser"}
    )
    summary.status = "SKIPPED"
    return True


def _register(
    engine: Engine,
    tracker: StageTracker,
    summary: RunSummary,
    source: FetchedFile,
    frame: pd.DataFrame,
    parser: str,
    manifest: Path,
) -> None:
    with Session(engine) as session, session.begin():
        version = register_version(
            session,
            source,
            summary.checksum,
            parser_version=parser,
            row_count=len(frame),
            schema_hash=schema_hash(frame),
            manifest_path=rel(manifest),
        )
        tracker.version_id, summary.version_label = version.id, version.version_label


def run_pipeline[T](
    engine: Engine,
    catalog: Catalog,
    dataset_id: str,
    steps: PipelineSteps[T],
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    sync_catalog(engine, catalog)
    source = source or fetch_role(catalog.datasets[dataset_id], steps.resource_role)
    tracker = StageTracker(engine, dataset_id)
    summary = RunSummary("RUNNING", dataset_id, combined_checksum([source]), tracker.correlation_id)
    if _skip_if_current(engine, tracker, summary, steps.parser_version):
        return summary

    with tracker.stage(PipelineStage.PARSE) as metrics:
        frame = read_csv(source.path, steps.csv)
        metrics |= {"rows": len(frame), "columns": list(frame.columns)}
    silver_dir = data_dir / "silver" / dataset_id / summary.checksum[:12]
    manifest = {
        "inputs": [source.manifest_entry()],
        "checksum": summary.checksum,
        "parser_version": steps.parser_version,
    }
    write_json(silver_dir / "manifest.json", manifest)
    _register(
        engine, tracker, summary, source, frame, steps.parser_version, silver_dir / "manifest.json"
    )

    with tracker.stage(PipelineStage.NORMALIZE) as metrics:
        result = steps.normalize(frame)
        quarantine = steps.quarantine(result)
        metrics |= {"quarantined": len(quarantine)}
    if len(quarantine):
        path = data_dir / "quarantine" / dataset_id / summary.checksum[:12] / "rows.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        quarantine.to_csv(path, index=False)

    with tracker.stage(PipelineStage.QUALITY_CHECK) as metrics:
        report = steps.quality(result)
        metrics |= {
            "passed": report["passed"],
            "failed": [c["name"] for c in report["checks"] if not c["passed"]],
        }
    summary.quality, summary.counts = report, steps.counts(result)
    out = evidence_dir(evidence_root, dataset_id)
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

    silver_file = steps.write_silver(result, silver_dir)
    with (
        tracker.stage(PipelineStage.PUBLISH_SILVER) as metrics,
        Session(engine) as session,
        session.begin(),
    ):
        db_version = session.get(DatasetVersion, tracker.version_id)
        assert db_version is not None  # noqa: S101 - registered above in this run
        metrics |= steps.publish(session, result, db_version.id)
        mark_last_valid(session, db_version, "PASSED")
        summary.counts |= {k: v for k, v in metrics.items() if isinstance(v, int | float)}
    if out:
        write_json(out / "row_counts.json", summary.counts)
        write_json(
            out / "lineage.json",
            manifest
            | {
                "dataset_version": summary.version_label,
                "correlation_id": tracker.correlation_id,
                "silver": rel(silver_file),
            },
        )
    summary.status = "SUCCESS"
    return summary
