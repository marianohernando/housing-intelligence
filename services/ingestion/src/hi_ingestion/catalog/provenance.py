"""Provenance references for results: which datasets, who publishes them, where to open them."""

from hi_contracts.catalog import DatasetSpec
from hi_contracts.public import DatasetRef
from hi_ingestion.catalog.loader import Catalog

CM_SOURCE_ID = "comunidad_madrid_ckan"
CM_PORTAL_ROLE = "cm_portal"


def is_cm_open_data(dataset: DatasetSpec) -> bool:
    """Published in the Comunidad de Madrid open data portal (D-196 counts the CRTM GTFS too)."""
    return dataset.source_id == CM_SOURCE_ID or any(
        r.role == CM_PORTAL_ROLE for r in dataset.resources
    )


def portal_url(dataset: DatasetSpec) -> str | None:
    """The CM portal page when the dataset has one, otherwise its own landing page."""
    cm_page = next((r.url for r in dataset.resources if r.role == CM_PORTAL_ROLE), None)
    url = cm_page or dataset.landing_url
    return str(url) if url else None


def _source_name(catalog: Catalog, dataset: DatasetSpec, own: str) -> str:
    """Where `url` opens (D-231): the CM portal for CM open data, whoever produces it."""
    return catalog.sources[CM_SOURCE_ID].name if is_cm_open_data(dataset) else own


def dataset_ref(catalog: Catalog, dataset_id: str, version: str | None = None) -> DatasetRef:
    dataset = catalog.datasets[dataset_id]
    source = catalog.sources[dataset.source_id]
    return DatasetRef.model_validate(
        {
            "dataset_id": dataset_id,
            "name": dataset.name,
            "publisher": dataset.owner,
            "is_cm_open_data": is_cm_open_data(dataset),
            "url": portal_url(dataset),
            "version": version,
            "license": source.license_name,
            "source_name": _source_name(catalog, dataset, source.name),
        }
    )
