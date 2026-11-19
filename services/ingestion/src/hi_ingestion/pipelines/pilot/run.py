"""The pilot barrios of the investor version (D-247), from their versioned table."""

import uuid
from datetime import UTC, datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.manual import PilotZonesTable
from hi_contracts.catalog.pipeline import CsvFormat, PilotZonesPipeline
from hi_domain.geo.codes import admin_unit_id
from hi_ingestion.bronze import sha256_file
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.padron.run import known_barrios
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import OBS_COLUMNS, Observations, dims_key
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    barrio_checks,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver
from hi_ingestion.pipelines.zone_context.normalize import observation
from hi_ingestion.pipelines.zone_context.run import MANUAL_DIR

PARSER_VERSION = "pilot_zones-1.0.0"
CENTRE = "dentro"
EDGE = "borde"


def load_pilot(spec: PilotZonesPipeline, manual_dir: Path = MANUAL_DIR) -> PilotZonesTable:
    path = manual_dir / spec.table
    return PilotZonesTable.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def pilot_source(
    spec: PilotZonesPipeline, table: PilotZonesTable, manual_dir: Path = MANUAL_DIR
) -> FetchedFile:
    """The versioned table is the input; its lineage keeps the query's URL and the day the road
    was read, never a local path."""
    path = manual_dir / spec.table
    consulted = datetime.combine(table.consulted, time(), tzinfo=UTC)
    return FetchedFile(
        dataset_id=spec.dataset_id,
        role=spec.resource_role,
        path=path,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
        url=str(table.url),
        retrieved_at=consulted.isoformat(),
    )


def pilot_rows(table: PilotZonesTable, metric_id: str) -> pd.DataFrame:
    """One observation per pilot barrio: value 1, with whether it is on the edge and its note."""
    rows: list[dict[str, Any]] = []
    for barrio in table.barrios:
        dims = {
            "item": barrio.code,
            "name": barrio.name,
            "stage": EDGE if table.on_edge(barrio) else CENTRE,
        }
        if barrio.review:
            dims["note"] = barrio.review
        rows.append(
            observation(
                metric_id=metric_id,
                territory_level=TerritoryLevel.BARRIO.value,
                territory_code=barrio.code,
                territory_name=barrio.name,
                admin_unit_id=admin_unit_id(TerritoryLevel.BARRIO.value, barrio.code),
                period_start=table.consulted,
                period_end=table.consulted,
                dims=dims,
                dims_key=dims_key(dims),
                value=1.0,
                null_reason=None,
                unit="barrio",
                raw_value=None,
            )
        )
    return pd.DataFrame(rows, columns=OBS_COLUMNS)


def pilot_quality(
    obs: Observations, table: PilotZonesTable, known: set[str], catalog: Catalog, metric_id: str
) -> QualityReport:
    """Blocking: every pilot barrio is in the geography, and the table accounts for all of the
    municipio's barrios (a reform of the barrios is read again, never half applied)."""
    base = run_quality(obs, {metric_id: catalog.metrics[metric_id]}, set())
    listed = len(table.barrios) + len(table.reviewed_outside) + table.outside
    return QualityReport(
        [
            *base.checks,
            *barrio_checks(obs.frame, known, len(table.barrios)),
            CheckResult(
                "every_barrio_accounted_for",
                True,
                listed == len(known),
                {"in_table": listed, "in_geography": len(known)},
            ),
        ]
    )


def pilot_steps(
    engine: Engine, catalog: Catalog, spec: PilotZonesPipeline, table: PilotZonesTable
) -> PipelineSteps[Observations]:
    def publish(session: Session, obs: Observations, version_id: uuid.UUID) -> dict[str, int]:
        return {
            "observations": replace_observations(session, obs.frame, [spec.metric_id], version_id)
        }

    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # not read: `parse` reads the versioned table
        resource_role=spec.resource_role,
        parse=lambda _path: pd.DataFrame([b.model_dump() for b in table.barrios]),
        normalize=lambda _frame: Observations(
            pilot_rows(table, spec.metric_id),
            pd.DataFrame(columns=["source_row", "reason", "raw"]),
            len(table.barrios),
        ),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: pilot_quality(
            obs, table, known_barrios(engine, table.municipio_ine), catalog, spec.metric_id
        ).to_dict(),
        counts=lambda obs: (
            row_counts(obs.frame) | {"reviewed_edge": sum(1 for b in table.barrios if b.review)}
        ),
        write_silver=write_silver,
        publish=publish,
    )


def run_pilot_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: PilotZonesPipeline,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    manual_dir: Path = MANUAL_DIR,
) -> RunSummary:
    """Always the versioned table (no `--local`, no network)."""
    table = load_pilot(spec, manual_dir)
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        pilot_steps(engine, catalog, spec, table),
        pilot_source(spec, table, manual_dir),
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
