"""Every catalog YAML is valid, consistent and respects DATAMAD source rules."""

import pytest

from hi_contracts.catalog.enums import LicenseStatus, Priority, TrustTier
from hi_ingestion.catalog.loader import Catalog, load_catalog

CM_SOURCE = "comunidad_madrid_ckan"


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


def test_catalog_loads(catalog: Catalog) -> None:
    assert catalog.sources
    assert catalog.datasets


def test_google_maps_is_rejected_and_inactive(catalog: Catalog) -> None:
    gmaps = catalog.sources["google_maps_scraped"]
    assert gmaps.license_status is LicenseStatus.REJECTED
    assert not gmaps.active


def test_no_dataset_depends_on_rejected_or_scraped_source(catalog: Catalog) -> None:
    for dataset in [*catalog.datasets.values(), *catalog.drafts.values()]:
        source = catalog.sources[dataset.source_id]
        assert source.license_status is not LicenseStatus.REJECTED, dataset.dataset_id
        assert source.trust_tier is not TrustTier.D_SCRAPED, dataset.dataset_id


def test_comunidad_de_madrid_is_structural(catalog: Catalog) -> None:
    """DATAMAD bases §6/§10: at least one P0 dataset from the CM open data portal."""
    p0_cm = [
        d
        for d in catalog.datasets.values()
        if d.priority is Priority.P0 and d.source_id == CM_SOURCE
    ]
    assert p0_cm


def test_p0_datasets_have_clear_license(catalog: Catalog) -> None:
    for dataset in catalog.datasets.values():
        if dataset.priority is Priority.P0:
            assert dataset.license_status is LicenseStatus.CLEAR, dataset.dataset_id


def test_drafts_are_never_p0(catalog: Catalog) -> None:
    assert all(d.priority is not Priority.P0 for d in catalog.drafts.values())
