"""Features computed at more than one level (D-200: municipios + districts of Madrid)."""

import pandas as pd
import pytest

from hi_contracts.catalog import FeatureSpec
from hi_features.compute import combine_levels, pass_level, versions_by_pass
from hi_features.methods import RESULT_COLUMNS
from hi_ingestion.catalog.loader import load_catalog

VERSIONS = {
    "cm_centros_educativos": "v-centros",
    "cm_poblacion_edad_nacionalidad_sexo": "v-censo",
    "ayto_padron_municipal": "v-padron",
}


@pytest.fixture(scope="module")
def colegios() -> FeatureSpec:
    return load_catalog().features["colegios_publicos_por_1000_menores"]


def _rows(*rows: tuple[str, float, str | None]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "territory_code": code,
                "period_start": "2026-10-01",
                "value": value,
                "null_reason": None,
                "confidence": 1.0,
                "territory_level": level,
            }
            for code, value, level in rows
        ],
        columns=RESULT_COLUMNS,
    )


def test_extra_levels_keep_their_rows_but_never_a_second_regional_reference() -> None:
    base = _rows(("28079", 1.5, None), ("28", 2.0, "ccaa"))
    district = _rows(("2807901", 1.2, None), ("2807905", 1.9, None), ("28", 1.6, "ccaa"))
    out = combine_levels(base, {"distrito": district})
    levels = [None if pd.isna(level) else level for level in out["territory_level"]]
    assert levels == [None, "ccaa", "distrito", "distrito"]  # None: the feature's own level
    assert out.loc[out["territory_level"] == "ccaa", "value"].tolist() == [2.0]


def test_rows_belong_to_the_pass_that_computed_them(colegios: FeatureSpec) -> None:
    assert pass_level(colegios, "municipio") == "municipio"
    assert pass_level(colegios, "ccaa") == "municipio"  # the regional reference
    assert pass_level(colegios, "distrito") == "distrito"


def test_each_pass_cites_only_the_datasets_it_used(colegios: FeatureSpec) -> None:
    by_pass = versions_by_pass(colegios, VERSIONS)
    assert by_pass["municipio"] == {
        "cm_centros_educativos": "v-centros",
        "cm_poblacion_edad_nacionalidad_sexo": "v-censo",
    }
    assert by_pass["distrito"] == {
        "cm_centros_educativos": "v-centros",
        "ayto_padron_municipal": "v-padron",
    }
