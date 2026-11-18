"""The zone context pipelines (D-241) on the generic runner, with their own blocking checks."""

import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime, time
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.manual import ParcelPointsTable, ZoneItemsTable
from hi_contracts.catalog.pipeline import (
    CmMunicipioNameTablePipeline,
    CsvFormat,
    CuratedZoneItemsPipeline,
    MadridDevelopmentAreasPipeline,
    PublicLandParcelsPipeline,
)
from hi_db.models import GeoAdminUnit
from hi_ingestion.bronze import REPO_ROOT, sha256_file
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile, fetch_role
from hi_ingestion.pipelines.padron.run import known_barrios, known_districts
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
from hi_ingestion.pipelines.zone_context.parcels import (
    ParcelObservations,
    Placement,
    normalize_parcels,
)

PARSER_VERSION = "zone_context-1.1.0"
PARCELS_PARSER_VERSION = "public_land_parcels-1.0.0"  # D-246
MANUAL_DIR = REPO_ROOT / "data" / "catalog" / "manual"


def municipio_names_by_code(engine: Engine) -> dict[str, str]:
    """INE code -> the municipio's name in the geography."""
    with Session(engine) as session:
        rows = session.execute(
            select(GeoAdminUnit.code_official, GeoAdminUnit.name).where(
                GeoAdminUnit.level == "municipio"
            )
        ).all()
    return {str(code): str(name) for code, name in rows}


def geography_names(engine: Engine) -> MunicipioNames:
    return municipio_names(municipio_names_by_code(engine))


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
        # The zone value is the areas of the latest date: an area left with an older date
        # would drop out of its district's count in silence, so a mixed register blocks.
        CheckResult(
            "one_register_date",
            True,
            len(result.dates) == 1,
            {"dates": sorted(str(d) for d in result.dates)},
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


def load_points(
    spec: PublicLandParcelsPipeline, manual_dir: Path = MANUAL_DIR
) -> ParcelPointsTable:
    path = manual_dir / spec.points
    return ParcelPointsTable.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def points_input(
    spec: PublicLandParcelsPipeline, table: ParcelPointsTable, manual_dir: Path = MANUAL_DIR
) -> FetchedFile:
    """The versioned points as an input of the run: they enter its checksum and its lineage,
    with the map layer's URL and the day it was read, never a local path."""
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


_LOCATE = text(
    """
    SELECT p.ref,
           (SELECT d.code_official FROM geo_admin_unit d
             WHERE d.level = 'distrito' AND d.code_official LIKE :prefix
               AND ST_Contains(d.geom_25830, p.geom)) AS distrito,
           (SELECT b.code_official FROM geo_admin_unit b
             WHERE b.level = 'barrio' AND b.code_official LIKE :prefix
               AND ST_Contains(b.geom_25830, p.geom)) AS barrio
      FROM (SELECT ref, ST_SetSRID(ST_MakePoint(x, y), 25830) AS geom
              FROM unnest(CAST(:refs AS text[]), CAST(:xs AS float8[]), CAST(:ys AS float8[]))
                   AS t(ref, x, y)) AS p
    """
)


def locate_points(engine: Engine, table: ParcelPointsTable) -> dict[str, Placement]:
    """District and barrio of each point, in the canonical geography of its municipio."""
    params = {
        "prefix": f"{table.municipio_ine}%",
        "refs": [p.ref for p in table.points],
        "xs": [float(p.x) for p in table.points],
        "ys": [float(p.y) for p in table.points],
    }
    with engine.connect() as conn:
        rows = conn.execute(_LOCATE, params).all()
    return {str(r.ref): Placement(r.distrito, r.barrio) for r in rows}


def parcels_quality(
    result: ParcelObservations,
    spec: PublicLandParcelsPipeline,
    metrics: dict[str, MetricSpec],
    known: set[str],
    zones: set[str],
) -> QualityReport:
    """`known`: municipios of the geography; `zones`: districts and barrios of the split one."""
    base = run_quality(result.obs, metrics, known)
    frame = result.obs.frame
    placed = set(frame.loc[frame["territory_level"].isin(["distrito", "barrio"]), "territory_code"])
    extra = [
        nothing_quarantined(result.obs.quarantine),
        CheckResult(
            "file_size",
            True,
            spec.min_rows <= result.parcels <= spec.max_rows,
            {"parcels": result.parcels, "min": spec.min_rows, "max": spec.max_rows},
        ),
        CheckResult(
            "districts_and_barrios_resolve_to_geography",
            True,
            placed <= zones,
            {"zones": len(placed), "unknown": sorted(placed - zones)},
        ),
    ]
    return QualityReport([*base.checks, *extra])


def parcel_steps(
    engine: Engine,
    catalog: Catalog,
    spec: PublicLandParcelsPipeline,
    points: ParcelPointsTable,
    observed: date,
) -> PipelineSteps[ParcelObservations]:
    metrics = _metrics(catalog, spec.metric_ids())
    publish = _publish(spec.metric_ids())
    split = spec.split_municipio_ine

    def normalize(frame: pd.DataFrame) -> ParcelObservations:
        names = municipio_names_by_code(engine)
        return normalize_parcels(frame, spec, names, locate_points(engine, points), observed)

    return PipelineSteps(
        parser_version=PARCELS_PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=normalize,
        quarantine=lambda result: result.obs.quarantine,
        quality=lambda result: parcels_quality(
            result,
            spec,
            metrics,
            known_municipios(engine),
            known_districts(engine, split) | known_barrios(engine, split),
        ).to_dict(),
        counts=lambda result: (
            row_counts(result.obs.frame)
            | {
                "parcels": result.parcels,
                "out_of_scope": result.out_of_scope,
                "municipios": len(result.municipios),
                "points": len(points.points),
            }
        ),
        write_silver=lambda result, directory: write_silver(result.obs, directory),
        publish=lambda session, result, version_id: publish(session, result.obs, version_id),
    )


def run_parcels_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: PublicLandParcelsPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
    manual_dir: Path = MANUAL_DIR,
) -> RunSummary:
    """The file is a daily snapshot without a date column: its observations are dated the day
    it was downloaded (`retrieved_at`, which a Bronze file keeps)."""
    source = source or fetch_role(catalog.datasets[spec.dataset_id], spec.resource_role)
    points = load_points(spec, manual_dir)
    observed = date.fromisoformat(source.retrieved_at[:10])
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        parcel_steps(engine, catalog, spec, points, observed),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
        extra_inputs=[points_input(spec, points, manual_dir)],
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
