"""CORE-005 walking features on the fixture database: a synthetic street grid over the Madrid
sample, the real feature pipeline, rows at every level and explicit nulls where no street is."""

from typing import Any

import pytest
from sqlalchemy import Engine, text

pytestmark = pytest.mark.db

MEDIAN, SHARE = "min_a_pie_farmacia", "pct_calle_farmacia_10min"
ROWS = text(
    """
    SELECT territory_level, territory_code, value, null_reason, confidence, inputs
      FROM feature_value
     WHERE feature_id = :feature
    """
)
SECTIONS = text("SELECT code_official FROM geo_admin_unit WHERE level = 'seccion_censal'")


def _rows(engine: Engine, feature: str) -> dict[tuple[str, str], dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(ROWS, {"feature": feature}).mappings().all()
    return {(r["territory_level"], r["territory_code"]): dict(r) for r in rows}


def test_every_section_gets_a_row_with_explicit_nulls_outside_the_grid(
    migrated_engine: Engine, features_computed: None
) -> None:
    rows = _rows(migrated_engine, MEDIAN)
    with migrated_engine.connect() as conn:
        sections = [str(c) for c in conn.execute(SECTIONS).scalars()]
    for code in sections:
        row = rows[("seccion_censal", code)]
        if code.startswith("28079"):  # inside the street grid
            assert row["value"] is not None and row["value"] >= 0, code
            assert 0 < row["confidence"] <= 1
        else:  # La Acebeda and Ajalvir: no street, never 0
            assert row["value"] is None and row["null_reason"] == "SOURCE_NO_COVERAGE", code
            assert row["confidence"] == 0


def test_levels_and_regional_reference(migrated_engine: Engine, features_computed: None) -> None:
    rows = _rows(migrated_engine, MEDIAN)
    levels = {level for level, _ in rows}
    assert levels == {"seccion_censal", "municipio", "distrito", "ccaa"}
    assert rows[("municipio", "28079")]["value"] is not None
    assert rows[("municipio", "28001")]["value"] is None
    assert rows[("ccaa", "28")]["value"] is not None
    district = rows[("distrito", "2807906")]
    assert district["value"] is not None
    assert set(district["inputs"]["dataset_versions"]) == {
        "osm_red_peatonal",
        "cm_oficinas_farmacia",
    }


def test_median_within_the_window_means_half_the_street_or_more(
    migrated_engine: Engine, features_computed: None
) -> None:
    """The street-weighted median is at most 10 min exactly when >= 50 % of street is."""
    median, share = _rows(migrated_engine, MEDIAN), _rows(migrated_engine, SHARE)
    checked = 0
    for key, row in median.items():
        if row["value"] is None:
            assert share[key]["value"] is None
            continue
        assert 0 <= share[key]["value"] <= 100
        assert (row["value"] <= 10) == (share[key]["value"] >= 50), key
        checked += 1
    assert checked > 10
