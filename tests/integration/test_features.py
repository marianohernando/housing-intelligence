"""Gate 3: every computed feature satisfies the invariants its dictionary entry declares."""

from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, RowMapping, text

from hi_features.compute import METHODS, compute, persist
from hi_ingestion.catalog.loader import load_catalog

pytestmark = pytest.mark.db
GOLDEN = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden"
INVARIANTS = {
    "range_0_100": (0.0, 100.0),
    "range_1_5": (1.0, 5.0),
    "non_negative": (0.0, float("inf")),
    "positive": (1e-12, float("inf")),
}


def test_features_satisfy_declared_invariants(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    catalog = load_catalog()
    computed = 0
    for spec in catalog.features.values():
        if spec.formula.method not in METHODS:
            continue
        result = compute(migrated_engine, spec)
        persist(migrated_engine, spec, result)
        computed += 1
        values = [v for v in result["value"].tolist() if v is not None and v == v]
        assert values, f"{spec.feature_id}: no value computed on fixtures"
        for label in spec.tests:
            if label in INVARIANTS:
                low, high = INVARIANTS[label]
                assert all(low <= v <= high for v in values), (spec.feature_id, label)
    assert computed >= 12


def test_feature_rows_respect_null_contract(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    with migrated_engine.connect() as conn:
        broken = conn.execute(
            text("SELECT count(*) FROM feature_value WHERE (value IS NULL) = (null_reason IS NULL)")
        ).scalar()
        no_lineage = conn.execute(
            text("SELECT count(*) FROM feature_value WHERE NOT (inputs ? 'dataset_versions')")
        ).scalar()
    assert broken == 0
    assert no_lineage == 0


def test_madrid_districts_get_their_own_rows_and_lineage(
    features_computed: None, migrated_engine: Engine
) -> None:
    """D-200/D-209: district rows use the padrón; the regional reference stays single."""
    with migrated_engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT feature_id, territory_level, territory_code, admin_unit_id, inputs "
                    "FROM feature_value WHERE feature_id IN "
                    "('colegios_publicos_por_1000_menores', 'poblacion_total') "
                    "AND territory_level IN ('distrito', 'ccaa', 'municipio')"
                )
            )
            .mappings()
            .all()
        )
    by_level: dict[tuple[str, str], list[RowMapping]] = {}
    for row in rows:
        by_level.setdefault((row["feature_id"], row["territory_level"]), []).append(row)
    districts = by_level[("colegios_publicos_por_1000_menores", "distrito")]
    assert {r["territory_code"] for r in districts} == {"2807901", "2807905", "2807906"}
    assert all(r["admin_unit_id"] == f"ES.28.DIS.{r['territory_code']}" for r in districts)
    assert len(by_level[("colegios_publicos_por_1000_menores", "ccaa")]) == 1
    assert ("poblacion_total", "ccaa") not in by_level
    for (_, level), level_rows in by_level.items():
        for row in level_rows:
            cited = set(row["inputs"]["dataset_versions"])
            if level == "distrito":
                assert "ayto_padron_municipal" in cited
                assert "cm_poblacion_edad_nacionalidad_sexo" not in cited
            else:
                assert "ayto_padron_municipal" not in cited


def test_madrid_districts_get_the_published_household_size(
    features_computed: None, migrated_engine: Engine
) -> None:
    """D-209: districts take the Ayuntamiento's published mean; municipios keep the census one."""
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT territory_level, territory_code, value, confidence, inputs "
                "FROM feature_value WHERE feature_id = 'tamano_medio_hogar' "
                "AND territory_level = 'distrito' ORDER BY territory_code"
            )
        ).all()
    assert [r.territory_code for r in rows] == ["2807901", "2807905", "2807906"]
    for row in rows:
        assert 1.0 <= row.value <= 5.0
        assert row.confidence == 1.0
        assert set(row.inputs["dataset_versions"]) == {"ayto_panel_indicadores_distritos_barrios"}


def test_per_population_rows_keep_the_counts_behind_their_value(
    features_computed: None, migrated_engine: Engine
) -> None:
    """D-213: the list of what is missing tests shortfalls on these counts."""
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT territory_level, value, inputs FROM feature_value "
                "WHERE feature_id = 'colegios_publicos_por_1000_menores' AND value IS NOT NULL"
            )
        ).all()
    assert rows
    for level, value, inputs in rows:
        counts = inputs["counts"]
        assert 1000 * counts["numerator"] / counts["denominator"] == pytest.approx(value), level


def test_district_rent_comes_from_its_postcodes(
    features_computed: None, migrated_engine: Engine
) -> None:
    """CORE-006: districts of Madrid get the rent of their postcodes (proxy, confidence <= 0.8),
    between the lowest and highest published postcode, and cite the postcode dataset."""
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT territory_code, value, null_reason, confidence, inputs FROM feature_value "
                "WHERE feature_id = 'alquiler_m2_mensual' AND territory_level = 'distrito'"
            )
        ).all()
        published = conn.execute(
            text(
                "SELECT min(value), max(value) FROM metric_observation "
                "WHERE metric_id = 'alquiler_m2_mensual_codigo_postal' AND period_start = "
                "(SELECT max(period_start) FROM metric_observation "
                " WHERE metric_id = 'alquiler_m2_mensual_codigo_postal')"
            )
        ).one()
    assert rows, "no district rent computed on fixtures"
    assert all(r.territory_code.startswith("28079") for r in rows)
    known = [r for r in rows if r.value is not None]
    assert known, "no sample place carries a published postcode"
    for row in rows:
        assert row.confidence <= 0.8
        assert "cm_alquiler_m2_codigo_postal_madrid" in row.inputs["dataset_versions"]
        assert "cm_alquiler_m2_municipios" not in row.inputs["dataset_versions"]
        assert row.inputs["method"] == "postcode_weighted_mean"
        if row.value is None:
            assert row.null_reason == "SOURCE_NO_COVERAGE"
        else:
            assert published[0] <= row.value <= published[1]


def test_two_step_rows_keep_facility_equivalents_and_madrid_districts(
    features_computed: None, migrated_engine: Engine
) -> None:
    """D-217: 2SFCA rows by municipio and by Madrid district only; their counts are capacity in
    facility-equivalents over people, so value / (numerator / denominator) is one constant."""
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT v.feature_id, v.territory_level, v.territory_code, v.value, "
                "v.inputs->'counts' AS counts FROM feature_value v "
                "JOIN feature_registry r ON r.feature_id = v.feature_id "
                "WHERE r.spec->'formula'->>'method' = 'two_step_fca'"
            )
        ).mappings()
        by_feature: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            by_feature.setdefault(r["feature_id"], []).append(dict(r))
    assert len(by_feature) == 5
    for feature_id, values in by_feature.items():
        levels = {v["territory_level"] for v in values}
        assert levels == {"municipio", "distrito", "ccaa"}, feature_id
        districts = [v["territory_code"] for v in values if v["territory_level"] == "distrito"]
        assert districts and all(code.startswith("28079") for code in districts), feature_id
        scales = {
            round(v["value"] / (v["counts"]["numerator"] / v["counts"]["denominator"]), 6)
            for v in values
            if v["value"] and v["counts"] and v["counts"]["numerator"]
        }
        assert len(scales) <= 1, (feature_id, scales)
