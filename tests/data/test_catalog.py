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


PII_COLUMNS = ("telefono", "correo", "e_mail", "email", "nif", "fax", "web")


def test_every_pipeline_has_metrics_or_category(catalog: Catalog) -> None:
    for dataset_id, pipeline in catalog.pipelines.items():
        assert dataset_id in catalog.datasets
        if pipeline.kind == "points_csv":
            assert pipeline.attribute_columns, dataset_id
        elif pipeline.kind == "gtfs_feed":
            assert catalog.datasets[dataset_id].domain.value == "transport", dataset_id
        else:
            assert pipeline.metric_ids(), dataset_id


def test_point_pipelines_never_keep_contact_or_tax_ids(catalog: Catalog) -> None:
    """Data minimisation: facilities keep service attributes, never phones, emails or NIF."""
    for pipeline in catalog.pipelines.values():
        if pipeline.kind != "points_csv":
            continue
        kept = [pipeline.id_column, pipeline.name_column or "", *pipeline.attribute_columns]
        for column in kept:
            assert not any(term in column.lower() for term in PII_COLUMNS), (
                pipeline.dataset_id,
                column,
            )


def test_core_cm_statistics_have_pipelines(catalog: Catalog) -> None:
    stats = {m.dataset_id for m in catalog.metrics.values()}
    assert stats <= set(catalog.pipelines)
    assert all(catalog.datasets[d].source_id == CM_SOURCE for d in stats)


PROTECTED_SUBTYPES = ("PISOS TUTELADOS", "MUJERES MALTRATADAS", "ACOGIDA DE MENORES", "ALBERGUES")


def test_social_facilities_exclude_protected_housing(catalog: Catalog) -> None:
    """D-186: locations of protected housing and shelters are never mapped."""
    spec = catalog.pipelines["cm_centros_atencion_social"]
    assert spec.kind == "points_csv"
    allowed = spec.row_filters.get(spec.subcategory_column, [])
    assert allowed, "social facilities must use an explicit subtype allowlist"
    assert not any(p in a for a in allowed for p in PROTECTED_SUBTYPES)
    assert spec.row_filters.get("sector") == ["Personas mayores"]


PROTECTED_DIMENSION_VALUES = ("extranjeros", "espanoles", "hombres", "mujeres")


def test_features_never_score_by_protected_characteristics(catalog: Catalog) -> None:
    """CLAUDE.md §3: nationality or sex never become features (aggregate or not)."""
    for feature in catalog.features.values():
        formula = feature.formula.model_dump()
        text = str({k: v for k, v in formula.items() if k != "method"}).lower()
        hits = [v for v in PROTECTED_DIMENSION_VALUES if v in text]
        assert not hits, (feature.feature_id, hits)


PIPELINE_COMPUTED_METHODS = {"planar_area_epsg_25830"}


def test_every_feature_method_is_implemented(catalog: Catalog) -> None:
    from hi_features.compute import METHODS

    for feature in catalog.features.values():
        assert (
            feature.formula.method in METHODS or feature.formula.method in PIPELINE_COMPUTED_METHODS
        ), feature.feature_id
