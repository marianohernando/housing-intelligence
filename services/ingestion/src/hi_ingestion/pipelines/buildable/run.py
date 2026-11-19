"""The VEDA register of buildable area left (D-247) on the generic runner: each area placed in
its barrio by the versioned points, with its blocking checks."""

import uuid
from datetime import UTC, datetime, time
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from hi_contracts.catalog.manual import AreaPointsTable
from hi_contracts.catalog.pipeline import CsvFormat, MadridBuildableAreasPipeline
from hi_ingestion.bronze import sha256_file
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.buildable.normalize import (
    AreaRegister,
    PlacedArea,
    normalize_buildable_areas,
)
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile, fetch_role
from hi_ingestion.pipelines.padron.run import known_barrios, known_districts
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    barrio_checks,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver
from hi_ingestion.pipelines.zone_context.run import (
    MANUAL_DIR,
    locate_points,
    nothing_quarantined,
    read_areas,
)

PARSER_VERSION = "madrid_buildable_areas-1.0.0"


def load_area_points(
    spec: MadridBuildableAreasPipeline, manual_dir: Path = MANUAL_DIR
) -> AreaPointsTable:
    path = manual_dir / spec.points
    return AreaPointsTable.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def area_points_input(
    spec: MadridBuildableAreasPipeline, table: AreaPointsTable, manual_dir: Path = MANUAL_DIR
) -> FetchedFile:
    """The versioned points enter the run's checksum and lineage, with the layer's URL and the
    day it was read, never a local path."""
    path = manual_dir / spec.points
    consulted = datetime.combine(table.consulted, time(), tzinfo=UTC)
    return FetchedFile(
        dataset_id=spec.dataset_id,
        role="points",
        path=path,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
        url=str(table.url),
        retrieved_at=consulted.isoformat(),
    )


def placed_areas(engine: Engine, table: AreaPointsTable) -> dict[str, PlacedArea]:
    located = locate_points(engine, table)
    return {p.ref: PlacedArea(located[p.ref], p.share_pct) for p in table.points}


def areas_quality(
    result: AreaRegister,
    spec: MadridBuildableAreasPipeline,
    districts: set[str],
    barrios: set[str],
    catalog: Catalog,
) -> QualityReport:
    """The whole register is checked (size, its 21 districts, one date), not only what is kept."""
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}
    base = run_quality(result.obs, metrics, set())
    extra = [
        nothing_quarantined(result.obs.quarantine),
        CheckResult(
            "register_size",
            True,
            spec.min_rows <= result.rows <= spec.max_rows,
            {"rows": result.rows, "min": spec.min_rows, "max": spec.max_rows},
        ),
        CheckResult(
            "register_districts",
            True,
            len(result.districts) == spec.expected_districts and result.districts <= districts,
            {"districts": len(result.districts), "unknown": sorted(result.districts - districts)},
        ),
        CheckResult(
            "one_register_date",
            True,
            len(result.dates) == 1,
            {"dates": sorted(str(d) for d in result.dates)},
        ),
        *barrio_checks(result.obs.frame, barrios, None),
    ]
    return QualityReport([*base.checks, *extra])


def area_steps(
    engine: Engine,
    catalog: Catalog,
    spec: MadridBuildableAreasPipeline,
    points: AreaPointsTable,
) -> PipelineSteps[AreaRegister]:
    def normalize(frame: pd.DataFrame) -> AreaRegister:
        return normalize_buildable_areas(frame, spec, placed_areas(engine, points))

    def publish(session: Session, result: AreaRegister, version_id: uuid.UUID) -> dict[str, int]:
        frame = result.obs.frame
        return {"observations": replace_observations(session, frame, spec.metric_ids(), version_id)}

    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # not read: `parse` reads the register
        resource_role=spec.resource_role,
        parse=read_areas,
        normalize=normalize,
        quarantine=lambda result: result.obs.quarantine,
        quality=lambda result: areas_quality(
            result,
            spec,
            known_districts(engine, spec.municipio_ine),
            known_barrios(engine, spec.municipio_ine),
            catalog,
        ).to_dict(),
        counts=lambda result: (
            row_counts(result.obs.frame)
            | {"rows": result.rows, "areas_kept": result.kept, "points": len(points.points)}
            | {"partial_blank": result.partial_blank}
            | {f"out_of_scope|{k}": v for k, v in sorted(result.out_of_scope.items())}
        ),
        write_silver=lambda result, directory: write_silver(result.obs, directory),
        publish=publish,
    )


def run_buildable_areas_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MadridBuildableAreasPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    manual_dir: Path = MANUAL_DIR,
) -> RunSummary:
    source = source or fetch_role(catalog.datasets[spec.dataset_id], spec.resource_role)
    points = load_area_points(spec, manual_dir)
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        area_steps(engine, catalog, spec, points),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
        extra_inputs=[area_points_input(spec, points, manual_dir)],
    )
