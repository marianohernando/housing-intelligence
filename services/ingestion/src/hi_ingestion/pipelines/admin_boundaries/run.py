"""Orchestrates FETCH -> PARSE -> NORMALIZE -> QUALITY -> GEO_RESOLVE -> PUBLISH for admin units."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import geopandas as gpd
from sqlalchemy import Engine, update
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import PipelineStage, RunStatus
from hi_db.models import DatasetVersion
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.catalog.sync import sync_catalog
from hi_ingestion.pipelines.admin_boundaries import config, transform
from hi_ingestion.pipelines.admin_boundaries.evidence import render_sample, write_json
from hi_ingestion.pipelines.admin_boundaries.fetch import FetchedFile, fetch_role, local_file
from hi_ingestion.pipelines.admin_boundaries.h3map import build_h3_mapping
from hi_ingestion.pipelines.admin_boundaries.publish import (
    find_version,
    mark_last_valid,
    register_version,
    replace_geography,
    upsert_h3,
)
from hi_ingestion.pipelines.admin_boundaries.quality import row_counts, run_quality
from hi_ingestion.pipelines.tracking import StageTracker

DATA_DIR = REPO_ROOT / "data"
GOLDEN_ZONES = DATA_DIR / "fixtures" / "golden" / "madrid_zones.json"


@dataclass(frozen=True)
class Inputs:
    sections: FetchedFile
    names: FetchedFile
    barrios: FetchedFile

    def files(self) -> list[FetchedFile]:
        return [self.sections, self.names, self.barrios]

    def checksum(self) -> str:
        joined = "|".join(f"{f.role}:{f.sha256}" for f in self.files())
        return hashlib.sha256(joined.encode()).hexdigest()

    def reader_path(self) -> str:
        path = self.sections.path
        return f"zip://{path}" if path.suffix == ".zip" else str(path)


@dataclass
class RunSummary:
    status: str
    dataset_id: str
    checksum: str
    correlation_id: str
    version_label: str | None = None
    counts: dict[str, Any] = field(default_factory=dict[str, Any])
    quality: dict[str, Any] = field(default_factory=dict[str, Any])
    evidence_dir: Path | None = None


def fetch_inputs(catalog: Catalog) -> Inputs:
    sections = catalog.datasets[config.SECTIONS_DATASET]
    barrios = catalog.datasets[config.BARRIOS_DATASET]
    return Inputs(
        fetch_role(sections, "primary"),
        fetch_role(sections, "names"),
        fetch_role(barrios, "primary"),
    )


def local_inputs(directory: Path) -> Inputs:
    sections = next(p for p in sorted(directory.iterdir()) if p.suffix in {".gpkg", ".zip", ".shp"})
    return Inputs(
        local_file(config.SECTIONS_DATASET, "primary", sections),
        local_file(config.SECTIONS_DATASET, "names", directory / "names.csv"),
        local_file(config.BARRIOS_DATASET, "primary", directory / "barrios.csv"),
    )


def load_zones(path: Path = GOLDEN_ZONES) -> list[dict[str, Any]]:
    return json.loads(path.read_text())["zones"]


def _schema_hash(raw: gpd.GeoDataFrame) -> str:
    signature = ",".join(f"{c}:{t}" for c, t in sorted(raw.dtypes.astype(str).items()))
    return hashlib.sha256(signature.encode()).hexdigest()


def _rel(path: Path) -> str:
    resolved = path.resolve()
    return (
        str(resolved.relative_to(REPO_ROOT))
        if resolved.is_relative_to(REPO_ROOT)
        else str(resolved)
    )


def _already_published(engine: Engine, tracker: StageTracker, checksum: str) -> str | None:
    with Session(engine) as session:
        existing = find_version(session, config.SECTIONS_DATASET, checksum)
        if (
            existing is None
            or not existing.is_last_valid
            or existing.parser_version != config.PARSER_VERSION
        ):
            return None
        tracker.version_id = existing.id
        label = existing.version_label
    tracker.record(
        PipelineStage.SNAPSHOT,
        RunStatus.SKIPPED,
        {"reason": "same checksum and parser_version already last valid"},
    )
    return label


def _fail_quality(engine: Engine, tracker: StageTracker, report: dict[str, Any]) -> None:
    with Session(engine) as session, session.begin():
        session.execute(
            update(DatasetVersion)
            .where(DatasetVersion.id == tracker.version_id)
            .values(quality_status="FAILED")
        )
    failed = [c["name"] for c in report["checks"] if c["critical"] and not c["passed"]]
    tracker.record(
        PipelineStage.PUBLISH_SILVER,
        RunStatus.SKIPPED,
        {"reason": "quality failed", "failed": failed},
    )


def run_admin_boundaries(
    engine: Engine,
    catalog: Catalog,
    inputs: Inputs,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    zones: list[dict[str, Any]] | None = None,
) -> RunSummary:
    zones = zones if zones is not None else load_zones()
    sync_catalog(engine, catalog)
    tracker = StageTracker(engine, config.SECTIONS_DATASET)
    checksum = inputs.checksum()
    summary = RunSummary("RUNNING", config.SECTIONS_DATASET, checksum, tracker.correlation_id)
    if label := _already_published(engine, tracker, checksum):
        summary.status, summary.version_label = "SKIPPED", label
        return summary

    with tracker.stage(PipelineStage.PARSE) as metrics:
        raw = transform.read_sections(inputs.reader_path())
        names = transform.read_names(inputs.names.path)
        barrio_names = transform.read_barrio_names(inputs.barrios.path)
        metrics |= {"rows": len(raw), "crs": str(raw.crs), "columns": list(raw.columns)}
    manifest = {"inputs": [f.manifest_entry() for f in inputs.files()], "checksum": checksum}
    version_dir = data_dir / "silver" / config.SECTIONS_DATASET / checksum[:12]
    write_json(version_dir / "manifest.json", manifest | {"parser_version": config.PARSER_VERSION})
    with Session(engine) as session, session.begin():
        version = register_version(
            session,
            inputs.sections,
            checksum,
            len(raw),
            _schema_hash(raw),
            _rel(version_dir / "manifest.json"),
        )
        tracker.version_id, summary.version_label = version.id, version.version_label

    with tracker.stage(PipelineStage.NORMALIZE) as metrics:
        admin = transform.build_admin_units(raw, *names, barrio_names)
        metrics |= {"units": row_counts(admin.units), "quarantined": len(admin.quarantine)}
    if len(admin.quarantine):
        quarantine_path = (
            data_dir / "quarantine" / config.SECTIONS_DATASET / checksum[:12] / "rows.csv"
        )
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)
        admin.quarantine.to_csv(quarantine_path, index=False)

    with tracker.stage(PipelineStage.QUALITY_CHECK) as metrics:
        report = run_quality(admin, zones).to_dict()
        metrics |= {
            "passed": report["passed"],
            "failed": [c["name"] for c in report["checks"] if not c["passed"]],
        }
    summary.quality, summary.counts = report, row_counts(admin.units)
    evidence_dir = (
        evidence_root / date.today().isoformat() / config.SECTIONS_DATASET
        if evidence_root
        else None
    )
    if evidence_dir:
        write_json(evidence_dir / "quality_report.json", report)
        summary.evidence_dir = evidence_dir
    if not report["passed"]:
        _fail_quality(engine, tracker, report)
        summary.status = "FAILED"
        return summary

    with tracker.stage(PipelineStage.GEO_RESOLVE) as metrics:
        mapping = build_h3_mapping(admin.units)
        metrics |= {"h3_cells": len(mapping.cells), "h3_links": len(mapping.links)}
    admin.units.drop(columns=["declared_area_km2"]).to_file(
        version_dir / "admin_units.gpkg", driver="GPKG"
    )

    with (
        tracker.stage(PipelineStage.PUBLISH_SILVER) as metrics,
        Session(engine) as session,
        session.begin(),
    ):
        source_id = catalog.datasets[config.SECTIONS_DATASET].source_id
        db_version = session.get(DatasetVersion, tracker.version_id)
        assert db_version is not None  # noqa: S101 - registered above in this run
        metrics["admin_units"] = replace_geography(session, admin.units, db_version.id, source_id)
        metrics |= upsert_h3(session, mapping)
        mark_last_valid(session, db_version, "PASSED")
        summary.counts |= {k: v for k, v in metrics.items() if k.startswith("h3_")}

    if evidence_dir:
        write_json(evidence_dir / "row_counts.json", summary.counts)
        write_json(evidence_dir / "lineage.json", manifest | {
            "dataset_version": summary.version_label,
            "parser_version": config.PARSER_VERSION,
            "correlation_id": tracker.correlation_id,
            "silver": _rel(version_dir / "admin_units.gpkg"),
        })  # fmt: skip
        write_json(evidence_dir / "golden_points.json", report["golden_points"])
        render_sample(evidence_dir / "render_sample.png", admin.units, mapping, zones)
    summary.status = "SUCCESS"
    return summary
