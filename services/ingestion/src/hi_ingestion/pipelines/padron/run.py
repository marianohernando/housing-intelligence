"""madrid_padron pipeline on the generic runner."""

from pathlib import Path

from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session

from hi_contracts.catalog.pipeline import MadridPadronPipeline
from hi_db.models import GeoAdminUnit
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.padron.normalize import normalize
from hi_ingestion.pipelines.padron.quality import run_padron_quality
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import Observations, dims_key
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import row_counts
from hi_ingestion.pipelines.stat_tables.run import write_silver

PARSER_VERSION = "madrid_padron-1.0.0"
_LATEST_MUNICIPIO_VALUE = text(
    """
    SELECT value FROM metric_observation
     WHERE metric_id = :metric_id AND territory_level = 'municipio'
       AND territory_code = :code AND dims_key = :dims_key
     ORDER BY period_start DESC
     LIMIT 1
    """
)


def known_districts(engine: Engine, municipio_ine: str) -> set[str]:
    with Session(engine) as session:
        codes = session.scalars(
            select(GeoAdminUnit.code_official).where(GeoAdminUnit.level == "distrito")
        )
        return {code for code in codes if code.startswith(municipio_ine)}


def census_total(engine: Engine, catalog: Catalog, spec: MadridPadronPipeline) -> float | None:
    if spec.census_metric_id is None or spec.census_metric_id not in catalog.metrics:
        return None
    metric = catalog.metrics[spec.census_metric_id]
    params = {
        "metric_id": metric.metric_id,
        "code": spec.municipio_ine,
        "dims_key": dims_key(dict.fromkeys(metric.dimensions, "total")),
    }
    with engine.connect() as conn:
        value = conn.execute(_LATEST_MUNICIPIO_VALUE, params).scalar()
    return float(value) if value is not None else None


def padron_steps(
    engine: Engine, catalog: Catalog, spec: MadridPadronPipeline
) -> PipelineSteps[Observations]:
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize(frame, spec),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: run_padron_quality(
            obs,
            spec,
            catalog.metrics,
            known_districts(engine, spec.municipio_ine),
            census_total(engine, catalog, spec),
        ).to_dict(),
        counts=lambda obs: row_counts(obs.frame),
        write_silver=write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, spec.metric_ids(), version_id)
        },
    )


def run_padron_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MadridPadronPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        padron_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
