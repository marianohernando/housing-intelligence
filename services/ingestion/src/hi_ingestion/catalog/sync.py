"""Upsert curated catalog YAML into source_registry and dataset_registry."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from hi_db.models import DatasetRegistry, FeatureRegistry, MetricRegistry, SourceRegistry
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.catalog.provenance import is_cm_open_data, portal_url

REPO_ROOT = Path(__file__).resolve().parents[5]


def _source_row(spec: Any) -> dict[str, Any]:
    data = spec.model_dump(mode="json", exclude={"robots_status"})
    data["notes"] = "\n".join(filter(None, [spec.notes, f"robots_status: {spec.robots_status}"]))
    return data


def _dataset_row(spec: Any, yaml_path: Path | None) -> dict[str, Any]:
    return {
        "dataset_id": spec.dataset_id,
        "source_id": spec.source_id,
        "name": spec.name,
        "domain": spec.domain.value,
        "owner": spec.owner,
        "format": spec.format,
        "geography": spec.geography,
        "geo_resolution": spec.geo.resolution.value,
        "temporal_resolution": spec.temporal_resolution,
        "refresh_policy": spec.refresh_policy,
        "landing_url": str(spec.landing_url) if spec.landing_url else None,
        "license_status": spec.license_status.value,
        "status": spec.status.value,
        "priority": spec.priority.value,
        "scorecard": spec.scorecard.model_dump(mode="json"),
        "catalog_yaml_path": str(yaml_path.relative_to(REPO_ROOT)) if yaml_path else None,
        "portal_url": portal_url(spec),
        "is_cm_open_data": is_cm_open_data(spec),
    }


def sync_catalog(engine: Engine, catalog: Catalog) -> dict[str, int]:
    """Idempotent upsert. Drafts are not registered: only curated datasets."""
    with Session(engine) as session, session.begin():
        for spec in catalog.sources.values():
            row = _source_row(spec)
            stmt = insert(SourceRegistry).values(**row)
            update = {k: stmt.excluded[k] for k in row if k != "source_id"}
            session.execute(stmt.on_conflict_do_update(index_elements=["source_id"], set_=update))
        for dataset_id, spec in catalog.datasets.items():
            row = _dataset_row(spec, catalog.paths.get(dataset_id))
            stmt = insert(DatasetRegistry).values(**row)
            update = {k: stmt.excluded[k] for k in row if k != "dataset_id"}
            session.execute(stmt.on_conflict_do_update(index_elements=["dataset_id"], set_=update))
        for spec in catalog.metrics.values():
            row = spec.model_dump(mode="json")
            stmt = insert(MetricRegistry).values(**row)
            update = {k: stmt.excluded[k] for k in row if k != "metric_id"}
            session.execute(stmt.on_conflict_do_update(index_elements=["metric_id"], set_=update))
        for spec in catalog.features.values():
            row = {
                "feature_id": spec.feature_id,
                "version": spec.version,
                "human_name": spec.human_name,
                "domain": spec.domain.value,
                "unit": spec.unit,
                "direction": spec.direction,
                "geo_level": spec.geo_level.value,
                "spec": spec.model_dump(mode="json"),
            }
            stmt = insert(FeatureRegistry).values(**row)
            update = {k: stmt.excluded[k] for k in row if k != "feature_id"}
            session.execute(stmt.on_conflict_do_update(index_elements=["feature_id"], set_=update))
    return {
        "sources": len(catalog.sources),
        "datasets": len(catalog.datasets),
        "metrics": len(catalog.metrics),
        "features": len(catalog.features),
    }
