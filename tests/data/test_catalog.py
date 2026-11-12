"""Every catalog YAML is valid, consistent and respects DATAMAD source rules."""

from typing import Any

import pytest

from hi_contracts.catalog.enums import LicenseStatus, Priority, TrustTier
from hi_contracts.public import NeedKey
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


PII_COLUMNS = ("telefono", "correo", "e_mail", "email", "nif", "fax", "web", "titulares")


def test_every_pipeline_has_metrics_or_category(catalog: Catalog) -> None:
    for dataset_id, pipeline in catalog.pipelines.items():
        assert dataset_id in catalog.datasets
        if pipeline.kind == "points_csv":
            assert pipeline.attribute_columns, dataset_id
        elif pipeline.kind == "gtfs_feed":
            assert catalog.datasets[dataset_id].domain.value == "transport", dataset_id
        elif pipeline.kind == "osm_walk_network":
            assert pipeline.walkable_highways, dataset_id
        elif pipeline.kind == "osm_parks":
            assert pipeline.leisure and pipeline.min_area_ha > 0, dataset_id
        elif pipeline.kind == "facility_directory":
            assert pipeline.scope_values, dataset_id
        else:
            assert pipeline.metric_ids(), dataset_id


def test_point_pipelines_never_keep_contact_or_tax_ids(catalog: Catalog) -> None:
    """Data minimisation: facilities keep service attributes, never phones, emails, NIF or
    the names of the people who own them (e.g. pharmacy holders)."""
    for pipeline in catalog.pipelines.values():
        if pipeline.kind != "points_csv":
            continue
        kept = [
            pipeline.id_column,
            pipeline.name_column or "",
            *pipeline.name_template_columns(),
            *pipeline.attribute_columns,
        ]
        for column in kept:
            assert not any(term in column.lower() for term in PII_COLUMNS), (
                pipeline.dataset_id,
                column,
            )


def test_directories_never_read_contact_columns(catalog: Catalog) -> None:
    """D-186 / D-218: a directory keeps names, addresses and capacity; never phones or emails."""
    directories = [p for p in catalog.pipelines.values() if p.kind == "facility_directory"]
    assert directories
    for pipeline in directories:
        for column in pipeline.kept_columns():
            folded = column.casefold().replace("é", "e").replace("ó", "o")
            assert not any(term in folded for term in PII_COLUMNS), (pipeline.dataset_id, column)


def test_directories_complement_cm_registers(catalog: Catalog) -> None:
    """D-218: a directory only names and sizes places of a CM register; it never creates them."""
    linked = {
        link.dataset_id: dataset_id
        for dataset_id, p in catalog.pipelines.items()
        if p.kind == "points_csv"
        for link in p.directories
    }
    directories = {d for d, p in catalog.pipelines.items() if p.kind == "facility_directory"}
    assert directories == set(linked)
    for directory, register in linked.items():
        assert catalog.datasets[register].source_id == CM_SOURCE, directory
        assert catalog.datasets[directory].source_id != CM_SOURCE, directory
        register_spec = catalog.pipelines[register]
        assert register_spec.kind == "points_csv"
        allowed = set(register_spec.row_filters.get(register_spec.subcategory_column or "", []))
        kinds = next(
            link.kinds for link in register_spec.directories if link.dataset_id == directory
        )
        assert set(kinds) <= allowed, (directory, set(kinds) - allowed)


# Statistics the CM does not publish at the level the product needs (D-209: population and
# households by district of Madrid). They complement CM data, never replace it.
COMPLEMENTARY_STATISTICS = {"ayto_padron_municipal", "ayto_panel_indicadores_distritos_barrios"}


def test_core_cm_statistics_have_pipelines(catalog: Catalog) -> None:
    stats = {m.dataset_id for m in catalog.metrics.values()}
    assert stats <= set(catalog.pipelines)
    assert all(catalog.datasets[d].source_id == CM_SOURCE for d in stats - COMPLEMENTARY_STATISTICS)


PROTECTED_SUBTYPES = ("PISOS TUTELADOS", "MUJERES MALTRATADAS", "ACOGIDA DE MENORES", "ALBERGUES")


def test_social_facilities_exclude_protected_housing(catalog: Catalog) -> None:
    """D-186: locations of protected housing and shelters are never mapped."""
    spec = catalog.pipelines["cm_centros_atencion_social"]
    assert spec.kind == "points_csv"
    allowed = spec.row_filters.get(spec.subcategory_column or "", [])
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


def test_gap_rows_have_one_primary_indicator_at_most(catalog: Catalog) -> None:
    """GAP-001: each row of the per-zone list is driven by a single declared feature."""
    primaries = [
        f.gap_row.row
        for f in catalog.features.values()
        if f.gap_row and f.gap_row.role == "primary"
    ]
    assert len(primaries) == len(set(primaries))
    assert {"escuela_infantil", "colegio", "centro_salud", "mayores", "farmacia"} <= set(primaries)


def _destinations(formula: dict[str, Any]) -> tuple[Any, ...]:
    attributes = formula.get("attributes") or {}
    return (
        formula.get("category") or formula.get("destination_category"),
        sorted(formula.get("subcategories") or []),
        sorted((k, sorted(v)) for k, v in attributes.items()),
    )


# D-217: the health row counts SERMAS health-centre teams as capacity, while its walking minutes
# reach any point of care (local consultorios included). Every counted place is still a
# destination of the walk, never the other way round.
COUNTED_SUBSET_OF_WALK = {"centro_salud"}
# Walking minutes to another service shown next to a row on purpose (D-217: the nearest general
# hospital next to primary care); they are not the row's own destinations.
OTHER_SERVICE_WALKS = {"min_a_pie_hospital"}


def test_gap_row_counts_the_same_places_as_its_walking_minutes(catalog: Catalog) -> None:
    """GAP-001: a row's main indicator and its walking minutes describe the same kind of place,
    e.g. colegios with primaria, public or concertado, in both (D-217 exception above)."""
    features = catalog.features.values()
    counted = {
        f.gap_row.row: f
        for f in features
        if f.gap_row
        and f.gap_row.role == "primary"
        and f.formula.method in {"places_per_population", "two_step_fca"}
    }
    checked = 0
    for walk in features:
        if not (walk.gap_row and walk.formula.method == "network_walk_time"):
            continue
        if walk.feature_id in OTHER_SERVICE_WALKS:
            continue
        primary = counted.get(walk.gap_row.row)
        if primary is None:
            continue
        category, subcategories, attributes = _destinations(primary.formula.model_extra or {})
        assert category is not None, primary.feature_id  # never compares empty filters
        assert subcategories or attributes, primary.feature_id
        walk_category, walk_subcategories, walk_attributes = _destinations(
            walk.formula.model_extra or {}
        )
        assert category == walk_category, f"{primary.feature_id} vs {walk.feature_id}"
        if walk.gap_row.row in COUNTED_SUBSET_OF_WALK:
            assert set(subcategories) < set(walk_subcategories), primary.feature_id
        else:
            assert (subcategories, attributes) == (walk_subcategories, walk_attributes), (
                f"{primary.feature_id} vs {walk.feature_id}"
            )
        checked += 1
    assert checked >= 5  # escuela infantil, colegio, centro de salud, mayores, farmacia


def test_feature_levels_use_known_metrics_and_declare_their_sources(catalog: Catalog) -> None:
    """A level override (e.g. districts) names metrics that exist, and lineage cites them."""
    for spec in catalog.features.values():
        levels: dict[str, dict[str, object]] = (spec.formula.model_extra or {}).get("levels") or {}
        passes = {spec.geo_level.value, *levels}
        for source in spec.sources:
            assert source.levels is None or set(source.levels) <= passes, spec.feature_id
        for level, override in levels.items():
            used = {s.dataset_id for s in spec.sources if s.levels is None or level in s.levels}
            for key in (
                "metric",
                "population_metric",
                "numerator_metric",
                "denominator_metric",
                "territories_metric",
            ):
                metric_id = override.get(key)
                if metric_id is None:
                    continue
                assert metric_id in catalog.metrics, (spec.feature_id, level, metric_id)
                assert catalog.metrics[str(metric_id)].dataset_id in used, (spec.feature_id, level)


def test_search_bindings_cover_every_need_once(catalog: Catalog) -> None:
    """CORE-003: the search finds its features through `fit`: one rent per m² and one walking
    feature per NeedKey, computed at the municipio and distrito levels it ranks."""
    bound = [s for s in catalog.features.values() if s.fit is not None]
    rents = [s for s in bound if s.fit is not None and s.fit.role == "rent_m2"]
    walks = {s.fit.need: s for s in bound if s.fit is not None and s.fit.role == "walk_minutes"}
    assert len(rents) == 1
    assert len(walks) == len([s for s in bound if s.fit and s.fit.role == "walk_minutes"])
    assert set(walks) == {n.value for n in NeedKey}
    for spec in bound:
        levels = {spec.geo_level.value, *((spec.formula.model_extra or {}).get("levels") or {})}
        assert {"municipio", "distrito"} <= levels, spec.feature_id
