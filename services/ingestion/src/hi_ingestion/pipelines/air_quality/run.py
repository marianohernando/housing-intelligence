"""Air quality on the generic runner: Bronze CSV -> a small table in Silver, nothing in the DB
(D-237). The stations themselves are places (points_csv); the feature joins them by code."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import AirQualityHourlyPipeline, AirQualityZonesPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.air_quality.means import (
    StationMeans,
    run_means_quality,
    station_means,
)
from hi_ingestion.pipelines.air_quality.zones import ZoneTable, run_zones_quality, zone_table
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

MEANS_PARSER_VERSION = "air-quality-means-1.0.0"
ZONES_PARSER_VERSION = "air-quality-zones-1.0.0"
MEANS_FILE = "station_means.csv"
ZONES_FILE = "municipio_zones.csv"
_MUNICIPIOS = text("SELECT code_official, name FROM geo_admin_unit WHERE level = 'municipio'")


def _write(frame: Any, directory: Path, name: str) -> Path:
    path = directory / name
    frame.to_csv(path, index=False)
    return path


def run_air_quality_hourly_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: AirQualityHourlyPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    def counts(result: StationMeans) -> dict[str, Any]:
        known = result.means.dropna(subset=["mean"])
        return {
            "stations": len(known),
            "rows_of_year": result.rows_of_year,
            "quarantined": len(result.problems),
        }

    steps: PipelineSteps[StationMeans] = PipelineSteps(
        parser_version=MEANS_PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: station_means(frame, spec),
        quarantine=lambda result: result.problems,
        quality=lambda result: run_means_quality(result, spec).to_dict(),
        counts=counts,
        write_silver=lambda result, directory: _write(result.means, directory, MEANS_FILE),
        publish=lambda _session, result, _version_id: counts(result),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )


def run_air_quality_zones_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: AirQualityZonesPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    with engine.connect() as conn:
        municipios = {str(code): str(name) for code, name in conn.execute(_MUNICIPIOS)}

    def counts(result: ZoneTable) -> dict[str, Any]:
        return {
            "municipios": len(result.zones),
            "zones": result.zones["zone_code"].nunique(),
            "quarantined": len(result.problems),
        }

    steps: PipelineSteps[ZoneTable] = PipelineSteps(
        parser_version=ZONES_PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: zone_table(frame, spec, municipios),
        quarantine=lambda result: result.problems,
        quality=lambda result: run_zones_quality(result).to_dict(),
        counts=counts,
        write_silver=lambda result, directory: _write(result.zones, directory, ZONES_FILE),
        publish=lambda _session, result, _version_id: counts(result),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
