"""GAP-001 classification: oriented ratio, declared cut-offs, unknown never classified."""

from pathlib import Path

import pytest
import yaml
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.enums import GapRowKey
from hi_contracts.public import GapStatus
from hi_domain.gaps import (
    CONTEXT_ROWS,
    GAP_METHOD,
    JUDGED_ROWS,
    TerritoryType,
    UnclassifiableError,
    classify,
    context_status,
    es_number,
    explanation,
    oriented_ratio,
    poisson_upper,
    row_label,
    significant_shortfall,
    territory_type,
)

FEATURES = Path(__file__).resolve().parents[3] / "data" / "catalog" / "features"
HOUSING_FEATURE = FEATURES / "viviendas_grandes_por_100_hogares_grandes.yaml"


@pytest.mark.parametrize(
    ("ratio", "status"),
    [
        (None, GapStatus.SIN_DATOS),
        (0.0, GapStatus.FALTA),  # a confirmed zero is a real FALTA, not missing data
        (0.79, GapStatus.FALTA),
        (0.8, GapStatus.JUSTO),
        (0.99, GapStatus.JUSTO),
        (1.0, GapStatus.CUBIERTO),
        (3.0, GapStatus.CUBIERTO),
    ],
)
def test_cut_offs(ratio: float | None, status: GapStatus) -> None:
    assert classify(ratio) is status


def test_ratio_is_oriented_so_above_one_is_better() -> None:
    assert oriented_ratio(3.0, 2.0, "higher_is_better") == 1.5
    assert oriented_ratio(5.0, 10.0, "lower_is_better") == 2.0  # 5 min vs 10 in the region
    with pytest.raises(UnclassifiableError):
        oriented_ratio(1.0, 0.0, "higher_is_better")
    with pytest.raises(UnclassifiableError):
        oriented_ratio(0.0, 10.0, "lower_is_better")


@given(
    st.floats(min_value=0, max_value=1e4),
    st.floats(min_value=0, max_value=1e4),
    st.floats(min_value=1e-3, max_value=1e4),
)
def test_more_supply_never_worsens_the_status(value: float, extra: float, reference: float) -> None:
    order = [GapStatus.FALTA, GapStatus.JUSTO, GapStatus.CUBIERTO]
    before = classify(oriented_ratio(value, reference, "higher_is_better"))
    after = classify(oriented_ratio(value + extra, reference, "higher_is_better"))
    assert order.index(after) >= order.index(before)


def test_method_is_versioned_and_ordered() -> None:
    assert GAP_METHOD.version.startswith("gap-")
    assert GAP_METHOD.falta_below <= GAP_METHOD.cubierto_from


def test_spanish_numbers_and_explanation() -> None:
    assert es_number(1234.56, 1) == "1.234,6"
    assert explanation(0.371, 0.592, "centros por cada 10.000 habitantes") == (
        "0,37 centros por cada 10.000 habitantes; en el conjunto de la Comunidad de Madrid, 0,59"
    )


def test_spanish_explanation_against_the_type_with_the_region_for_context() -> None:
    assert explanation(
        0.469,
        0.463,
        "centros por cada 10.000 habitantes",
        "en los municipios urbanos de la Comunidad de Madrid",
        regional=0.592,
    ) == (
        "0,47 centros por cada 10.000 habitantes; en los municipios urbanos de la Comunidad de "
        "Madrid, 0,46 (en toda la Comunidad, 0,59)"
    )


@pytest.mark.parametrize(
    ("population", "area_km2", "kind"),
    [
        (70, 22.0, TerritoryType.RURAL),  # La Acebeda
        (29_999, 300.0, TerritoryType.RURAL),  # 100 per km2 or less
        (29_999, 299.0, TerritoryType.URBANO),  # just over 100 per km2
        (30_000, 1_000.0, TerritoryType.URBANO),  # 30.000 inhabitants or more
        (1_400, 5.0, TerritoryType.URBANO),  # small but dense
    ],
)
def test_territory_type_follows_ley_45_2007(
    population: float, area_km2: float, kind: TerritoryType
) -> None:
    assert territory_type(population, area_km2) is kind


def test_poisson_upper_bound_matches_the_exact_tables() -> None:
    # Garwood 95 % upper limits (e.g. Ulm 1990): 0 -> 3.689, 7 -> 14.42, 100 -> 121.6
    assert poisson_upper(0, 0.95) == pytest.approx(3.689, abs=1e-3)
    assert poisson_upper(7, 0.95) == pytest.approx(14.42, abs=1e-2)
    assert poisson_upper(100, 0.95) == pytest.approx(121.6, abs=0.1)


def test_falta_needs_a_material_and_significant_shortfall() -> None:
    # 7 centres where 8,8 were expected: 0,79 of the reference, within chance -> JUSTO
    assert significant_shortfall(7, 8.84) is False
    assert classify(7 / 8.84, significant=significant_shortfall(7, 8.84)) is GapStatus.JUSTO
    # 60 where 100 were expected: material and significant -> FALTA
    assert classify(0.6, significant=significant_shortfall(60, 100)) is GapStatus.FALTA
    # significant but small (95 of 100 is not below the four-fifths cut-off) -> JUSTO
    assert classify(0.95, significant=True) is GapStatus.JUSTO
    # at or above the reference is CUBIERTO whatever the counts say
    assert classify(1.2, significant=False) is GapStatus.CUBIERTO
    # without counts the ratio decides alone
    assert classify(0.5, significant=None) is GapStatus.FALTA


@given(st.integers(min_value=0, max_value=500), st.floats(min_value=0.1, max_value=500))
def test_a_count_never_reads_as_short_of_itself(observed: int, extra: float) -> None:
    assert significant_shortfall(observed, observed) is False
    assert significant_shortfall(observed + extra, observed) is False


def test_the_housing_row_is_context_from_gap_0_4() -> None:
    """D-254: second homes inflate the stock of the villages, so the housing row is shown with
    its reference and never judged; every other row still is."""
    assert GAP_METHOD.version == "gap-0.4"
    assert GAP_METHOD.context_rows == [GapRowKey.VIVIENDA] == list(CONTEXT_ROWS)
    assert [row for row in GapRowKey if row is not GapRowKey.VIVIENDA] == JUDGED_ROWS
    label = "Viviendas grandes por cada 100 hogares grandes (contexto)"
    assert row_label(GapRowKey.VIVIENDA, "Vivienda para familias") == label
    assert row_label(GapRowKey.FARMACIA, "Farmacias") == "Farmacias"
    # The catalog says the same, so a sync of the Feature Dictionary changes nothing
    assert yaml.safe_load(HOUSING_FEATURE.read_text())["gap_row"]["label"] == label


@given(st.one_of(st.none(), st.floats(min_value=0, allow_nan=False, allow_infinity=False)))
def test_a_context_value_is_never_judged(value: float | None) -> None:
    status = context_status(value)
    assert status is (GapStatus.SIN_DATOS if value is None else GapStatus.CONTEXTO)
    assert status not in {GapStatus.FALTA, GapStatus.JUSTO, GapStatus.CUBIERTO}
