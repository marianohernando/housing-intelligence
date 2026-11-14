"""The zone context pipelines (D-241) on the generic runner, with their own blocking checks."""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, time
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.manual import ZoneItemsTable
from hi_contracts.catalog.pipeline import (
    CmMunicipioNameTablePipeline,
    CsvFormat,
    CuratedZoneItemsPipeline,
    MadridDevelopmentAreasPipeline,
)
from hi_db.models import GeoAdminUnit
from hi_ingestion.bronze import REPO_ROOT, sha256_file
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.padron.run import known_districts
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
from hi_ingestion.pipelines.zone_context.normalize import (
    AreaObservations,
    MunicipioNames,
    municipio_names,
    normalize_development_areas,
    normalize_municipio_names,
    normalize_zone_items,
    zone_items_frame,
)

PARSER_VERSION = "zone_context-1.1.0"
MANUAL_DIR = REPO_ROOT / "data" / "catalog" / "manual"


def geography_names(engine: Engine) -> MunicipioNames:
    with Session(engine) as session:
        rows = session.execute(
            select(GeoAdminUnit.code_official, GeoAdminUnit.name).where(
                GeoAdminUnit.level == "municipio"
            )
        ).all()
    return municipio_names({str(code): str(name) for code, name in rows})


def _metrics(catalog: Catalog, metric_ids: list[str]) -> dict[str, MetricSpec]:
    return {m: catalog.metrics[m] for m in metric_ids}


Publish = Callable[[Session, Observations, uuid.UUID], dict[str, int]]


def _publish(metric_ids: list[str]) -> Publish:
    def publish(session: Session, obs: Observations, version_id: uuid.UUID) -> dict[str, int]:
        return {"observations": replace_observations(session, obs.frame, metric_ids, version_id)}

    return publish


def nothing_quarantined(quarantine: pd.DataFrame) -> CheckResult:
    """Blocking: a name, state or date this pipeline cannot read is a change a person must see."""
    return CheckResult(
        "nothing_quarantined",
        True,
        quarantine.empty,
        {"quarantined": len(quarantine), "reasons": quarantine["reason"].head(5).tolist()},
    )


def every_municipio_published(frame: pd.DataFrame, known: set[str]) -> CheckResult:
    """Blocking: a table that names every municipio publishes all of the geography's."""
    codes = set(frame.loc[frame["territory_level"] == "municipio", "territory_code"])
    return CheckResult(
        "every_municipio_published",
        True,
        codes == known,
        {"covered": len(codes), "expected": len(known), "missing": sorted(known - codes)[:20]},
    )


def names_quality(
    obs: Observations, metrics: dict[str, MetricSpec], known: set[str]
) -> QualityReport:
    base = run_quality(obs, metrics, known)
    extra = [nothing_quarantined(obs.quarantine), every_municipio_published(obs.frame, known)]
    return QualityReport([*base.checks, *extra])


def name_table_steps(
    engine: Engine, catalog: Catalog, spec: CmMunicipioNameTablePipeline
) -> PipelineSteps[Observations]:
    metrics = _metrics(catalog, spec.metric_ids())
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_municipio_names(frame, spec, geography_names(engine)),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: names_quality(obs, metrics, known_municipios(engine)).to_dict(),
        counts=lambda obs: row_counts(obs.frame) | {"out_of_window": obs.out_of_window},
        write_silver=write_silver,
        publish=_publish(spec.metric_ids()),
    )


def read_areas(path: Path) -> pd.DataFrame:
    """The register's first sheet, every cell as text (calamine reads the old .xls format)."""
    frame = pd.read_excel(path, sheet_name=0, dtype=str, engine="calamine")
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame.loc[:, [c for c in frame.columns if not c.startswith("Unnamed")]]


def areas_quality(
    result: AreaObservations,
    spec: MadridDevelopmentAreasPipeline,
    metrics: dict[str, MetricSpec],
    known: set[str],
) -> QualityReport:
    """The whole register is checked (size and its 21 districts), not only the areas kept."""
    base = run_quality(result.obs, metrics, set())
    kept = set(result.obs.frame["territory_code"])
    extra = [
        nothing_quarantined(result.obs.quarantine),
        CheckResult(
            "register_size",
            True,
            spec.min_rows <= result.areas <= spec.max_rows,
            {"areas": result.areas, "min": spec.min_rows, "max": spec.max_rows},
        ),
        CheckResult(
            "register_districts",
            True,
            len(result.districts) == spec.expected_districts and result.districts <= known,
            {"districts": len(result.districts), "unknown": sorted(result.districts - known)},
        ),
        CheckResult(
            "kept_areas_resolve_to_geography", True, kept <= known, {"districts": len(kept)}
        ),
    ]
    return QualityReport([*base.checks, *extra])


def area_steps(
    engine: Engine, catalog: Catalog, spec: MadridDevelopmentAreasPipeline
) -> PipelineSteps[AreaObservations]:
    metrics = _metrics(catalog, spec.metric_ids())
    publish = _publish(spec.metric_ids())
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # not read: `parse` reads the file
        resource_role=spec.resource_role,
        parse=read_areas,
        normalize=lambda frame: normalize_development_areas(frame, spec),
        quarantine=lambda result: result.obs.quarantine,
        quality=lambda result: areas_quality(
            result, spec, metrics, known_districts(engine, spec.municipio_ine)
        ).to_dict(),
        counts=lambda result: (
            row_counts(result.obs.frame)
            | {"areas": result.areas, "out_of_scope": result.out_of_scope}
        ),
        write_silver=lambda result, directory: write_silver(result.obs, directory),
        publish=lambda session, result, version_id: publish(session, result.obs, version_id),
    )


def load_table(spec: CuratedZoneItemsPipeline, manual_dir: Path = MANUAL_DIR) -> ZoneItemsTable:
    path = manual_dir / spec.table
    return ZoneItemsTable.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def curated_source(
    spec: CuratedZoneItemsPipeline, table: ZoneItemsTable, manual_dir: Path = MANUAL_DIR
) -> FetchedFile:
    """The versioned file is the input; its lineage keeps the page it was typed from and the
    day it was consulted, never a local path."""
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


def items_quality(
    obs: Observations,
    metrics: dict[str, MetricSpec],
    known_munis: set[str],
    known_dists: set[str],
) -> QualityReport:
    base = run_quality(obs, metrics, known_munis)
    districts = set(obs.frame.loc[obs.frame["territory_level"] == "distrito", "territory_code"])
    extra = CheckResult(
        "districts_resolve_to_geography",
        True,
        districts <= known_dists,
        {"unknown": sorted(districts - known_dists)},
    )
    return QualityReport([*base.checks, extra])


def items_steps(
    engine: Engine, catalog: Catalog, spec: CuratedZoneItemsPipeline, table: ZoneItemsTable
) -> PipelineSteps[Observations]:
    metrics = _metrics(catalog, spec.metric_ids())
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # not read: `parse` reads the file
        resource_role=spec.resource_role,
        parse=lambda _path: zone_items_frame(table),
        normalize=lambda _frame: normalize_zone_items(table, spec.metric_id),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: items_quality(
            obs, metrics, known_municipios(engine), known_districts(engine, "28079")
        ).to_dict(),
        counts=lambda obs: row_counts(obs.frame) | {"entries": len(table.items)},
        write_silver=write_silver,
        publish=_publish(spec.metric_ids()),
    )


ZoneContextPipeline = (
    CmMunicipioNameTablePipeline | MadridDevelopmentAreasPipeline | CuratedZoneItemsPipeline
)


def run_zone_context_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: ZoneContextPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    manual_dir: Path = MANUAL_DIR,
) -> RunSummary:
    """A curated table always reads its versioned file (`source` is ignored for it)."""
    if isinstance(spec, CuratedZoneItemsPipeline):
        table = load_table(spec, manual_dir)
        steps = items_steps(engine, catalog, spec, table)
        return run_pipeline(
            engine,
            catalog,
            spec.dataset_id,
            steps,
            curated_source(spec, table, manual_dir),
            evidence_root=evidence_root,
            data_dir=data_dir,
        )
    if isinstance(spec, MadridDevelopmentAreasPipeline):
        return run_pipeline(
            engine,
            catalog,
            spec.dataset_id,
            area_steps(engine, catalog, spec),
            source,
            evidence_root=evidence_root,
            data_dir=data_dir,
        )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        name_table_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
