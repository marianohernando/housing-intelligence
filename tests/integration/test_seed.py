"""catalog sync is idempotent and fills the registries."""

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from hi_db.models import DatasetRegistry, MetricRegistry, SourceRegistry
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.catalog.sync import sync_catalog

pytestmark = pytest.mark.db


def test_sync_is_idempotent(migrated_engine: Engine) -> None:
    catalog = load_catalog()
    first = sync_catalog(migrated_engine, catalog)
    second = sync_catalog(migrated_engine, catalog)
    assert first == second
    with Session(migrated_engine) as session:
        n_sources = session.scalar(select(func.count()).select_from(SourceRegistry))
        n_datasets = session.scalar(select(func.count()).select_from(DatasetRegistry))
        gmaps = session.get(SourceRegistry, "google_maps_scraped")
        n_metrics = session.scalar(select(func.count()).select_from(MetricRegistry))
    assert n_sources == len(catalog.sources)
    assert n_datasets == len(catalog.datasets)
    assert n_metrics == len(catalog.metrics)
    assert gmaps is not None
    assert gmaps.license_status == "REJECTED"
    assert gmaps.active is False
