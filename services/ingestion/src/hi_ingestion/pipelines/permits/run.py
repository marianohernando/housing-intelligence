"""D-248: the PEM per m² of the building permits of the Comunidad de Madrid, on the generic
runner, from data/catalog/manual/<table> (written from the portal's CSV by
scripts/pem_visados_cm.py). The run reads the versioned file, never the portal: the same file
gives the same version, and the demo offline package needs no network."""

from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sqlalchemy import Engine

from hi_contracts.catalog.manual_permits import PermitBudgetTable
from hi_contracts.catalog.pipeline import CsvFormat, PermitBudgetPipeline
from hi_ingestion.bronze import REPO_ROOT, sha256_file
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import OBS_COLUMNS, Observations, dims_key
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import known_municipios, write_silver

PARSER_VERSION = "permit_budget-1.0.0"
MANUAL_DIR = REPO_ROOT / "data" / "catalog" / "manual"
REGION_CODE = "28"
REGION_NAME = "Comunidad de Madrid"
UNIT = "EUR/m2"


def load_table(spec: PermitBudgetPipeline, manual_dir: Path = MANUAL_DIR) -> PermitBudgetTable:
    path = manual_dir / spec.table
    return PermitBudgetTable.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def table_source(
    spec: PermitBudgetPipeline, table: PermitBudgetTable, manual_dir: Path = MANUAL_DIR
) -> FetchedFile:
    """The versioned file is the input; its lineage keeps the portal's CSV and the day it was
    read, never a local path."""
    path = manual_dir / spec.table
    read = datetime.combine(table.consulted, time(), tzinfo=UTC)
    return FetchedFile(
        dataset_id=spec.dataset_id,
        role=spec.resource_role,
        path=path,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
        url=str(table.csv_url),
        retrieved_at=read.isoformat(),
    )


def table_frame(table: PermitBudgetTable) -> pd.DataFrame:
    """One row per year and kind, as the PARSE stage's frame (row count and hash)."""
    return pd.DataFrame(
        [
            {"year": y.year, "tipo": kind, **figures.model_dump()}
            for y in table.series
            for kind, figures in y.figures().items()
        ]
    )


def permit_rows(table: PermitBudgetTable, metric_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in table.series:
        for kind, figures in entry.figures().items():
            dims = {"tipo": kind}
            row = dict.fromkeys(OBS_COLUMNS)
            row.update(
                metric_id=metric_id,
                territory_level="ccaa",
                territory_code=REGION_CODE,
                territory_name=REGION_NAME,
                admin_unit_id=None,
                period_start=date(entry.year, 1, 1),
                period_end=date(entry.year, 12, 31),
                dims=dims,
                dims_key=dims_key(dims),
                value=float(figures.pem_eur_m2),
                null_reason=None,
                unit=UNIT,
                raw_value=f"{figures.pem_miles_eur} miles de € / {figures.superficie_m2} m²",
            )
            rows.append(row)
    return rows


def normalize_permits(table: PermitBudgetTable, metric_id: str) -> Observations:
    """The contract checked every ratio against its pieces: nothing to quarantine."""
    frame = pd.DataFrame(permit_rows(table, metric_id), columns=OBS_COLUMNS)
    return Observations(frame, pd.DataFrame(columns=["source_row", "reason", "raw"]), len(frame))


def permits_quality(
    obs: Observations, engine: Engine, catalog: Catalog, metric_id: str
) -> dict[str, Any]:
    """The generic checks, and a blocking one: the homes in blocks (what the viability reads)
    in every year of the table."""
    base = run_quality(obs, {metric_id: catalog.metrics[metric_id]}, known_municipios(engine))
    frame = obs.frame
    blocks = set(frame.loc[frame["dims_key"] == "tipo=viviendas_en_bloque", "period_start"])
    years = set(frame["period_start"])
    check = CheckResult(
        "homes_in_blocks_every_year",
        True,
        bool(years) and blocks == years,
        {"years": len(years), "with_homes_in_blocks": len(blocks)},
    )
    return QualityReport([*base.checks, check]).to_dict()


def permit_steps(
    engine: Engine, catalog: Catalog, spec: PermitBudgetPipeline, table: PermitBudgetTable
) -> PipelineSteps[Observations]:
    metric_ids = spec.metric_ids()
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # not read: `parse` reads the table
        resource_role=spec.resource_role,
        parse=lambda _path: table_frame(table),
        normalize=lambda _frame: normalize_permits(table, spec.metric_id),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: permits_quality(obs, engine, catalog, spec.metric_id),
        counts=lambda obs: row_counts(obs.frame) | {"years": len(table.series)},
        write_silver=write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, metric_ids, version_id)
        },
    )


def run_permit_budget_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: PermitBudgetPipeline,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    manual_dir: Path = MANUAL_DIR,
) -> RunSummary:
    table = load_table(spec, manual_dir)
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        permit_steps(engine, catalog, spec, table),
        table_source(spec, table, manual_dir),
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
