"""People affected where something is missing and where to invest first (D-229)."""

from pathlib import Path

import pytest
import yaml
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.enums import GapRowKey
from hi_domain.gap_impact import (
    ROW_PEOPLE,
    ImpactZone,
    chance_text,
    people_in,
    people_scale,
    rank,
    row_summary,
    share_of,
    shortfall_p_value,
    shown_p_value,
    zone_sentence,
)
from hi_domain.gaps import GAP_METHOD, poisson_upper

FEATURES = Path(__file__).resolve().parents[3] / "data" / "catalog" / "features"

# The population each row's main indicator divides by, as its catalog entry declares it.
ROW_DIMS = {
    GapRowKey.ESCUELA_INFANTIL: ["de_0_4_anos"],
    GapRowKey.COLEGIO: ["de_5_9_anos", "de_10_14_anos"],
    GapRowKey.CENTRO_SALUD: ["total"],
    GapRowKey.MAYORES: [
        "de_65_69_anos",
        "de_70_74_anos",
        "de_75_79_anos",
        "de_80_84_anos",
        "de_85_89_anos",
        "de_90_94_anos",
        "de_95_99_anos",
        "de_100_y_mas_anos",
    ],
    GapRowKey.FARMACIA: ["total"],
    GapRowKey.VIVIENDA: ["de_4_personas", "de_5_o_mas_personas"],
}


def _primary_specs() -> dict[GapRowKey, dict[str, object]]:
    specs: dict[GapRowKey, dict[str, object]] = {}
    for path in FEATURES.glob("*.yaml"):
        spec = yaml.safe_load(path.read_text())
        binding = spec.get("gap_row")
        if binding and binding["role"] == "primary":
            specs[GapRowKey(binding["row"])] = spec
    return specs


def test_every_row_names_the_population_its_indicator_divides_by() -> None:
    """The label («niños de 0 a 4 años») must follow the catalog: a new main indicator with
    another denominator fails here until its label changes too."""
    specs = _primary_specs()
    assert set(specs) == set(GapRowKey) == set(ROW_PEOPLE)
    for row, spec in specs.items():
        formula = spec["formula"]
        assert isinstance(formula, dict)
        dims = formula.get("population_dims") or formula.get("denominator_dims")
        assert dims is not None, row
        key = "edad" if "edad" in dims else "tamano"
        assert dims[key] == ROW_DIMS[row], row


@pytest.mark.parametrize(
    ("formula", "level", "scale"),
    [
        ({"method": "two_step_fca", "per": 1000}, "municipio", 1000.0),  # stores people / per
        ({"method": "two_step_fca", "per": 10000, "levels": {"distrito": {}}}, "distrito", 1e4),
        ({"method": "metric_ratio", "per": 100}, "municipio", 1.0),  # stores people as such
        ({"method": "places_per_population", "per": 10000}, "ccaa", 1.0),
        # a level override changes the method, and with it how the denominator is stored
        (
            {"method": "metric_ratio", "per": 100, "levels": {"distrito": {"method": "x"}}},
            "distrito",
            1.0,
        ),
    ],
)
def test_people_scale_follows_how_each_method_stores_its_denominator(
    formula: dict[str, object], level: str, scale: float
) -> None:
    assert people_scale(formula, level) == scale


def test_people_in_counts() -> None:
    fca = {"method": "two_step_fca", "per": 1000}
    assert people_in({"numerator": 31.2, "denominator": 6.7286}, fca, "distrito") == 6729
    assert people_in({"numerator": 107, "denominator": 1}, {"method": "metric_ratio"}, "x") == 1
    assert people_in(None, fca, "municipio") is None  # no counts: unknown, never 0
    assert people_in({"numerator": 0.0, "denominator": 0.0}, fca, "municipio") == 0


def test_p_value_agrees_with_the_shortfall_test_of_d213() -> None:
    """FALTA's test (Garwood upper bound below the expected count) is p < 0,025 one-sided."""
    level = GAP_METHOD.confidence_level
    assert level is not None
    for observed in (0.0, 1.0, 4.0, 31.5, 120.0):
        bound = poisson_upper(observed, level)
        assert shortfall_p_value(observed, bound * 1.001) < (1 - level) / 2
        assert shortfall_p_value(observed, bound * 0.999) > (1 - level) / 2


@given(
    observed=st.floats(min_value=0, max_value=500),
    expected=st.floats(min_value=0.1, max_value=1000),
)
def test_p_value_is_a_probability_that_falls_as_the_gap_grows(
    observed: float, expected: float
) -> None:
    p = shortfall_p_value(observed, expected)
    assert 0.0 <= p <= 1.0
    assert shortfall_p_value(observed, expected * 2) <= p


@pytest.mark.parametrize(
    ("p", "text"),
    [
        (1e-9, "menos de 1 entre 1.000"),
        (0.004, "menos de 1 entre 100"),
        (0.02, "menos de 1 entre 40"),
    ],
)
def test_chance_text(p: float, text: str) -> None:
    assert chance_text(p) == text


def _zone(code: str, name: str, people: int) -> ImpactZone:
    return ImpactZone(code, name, people, 0.5, 1e-6, False)


def test_rank_puts_most_people_first_then_by_name() -> None:
    zones = [_zone("2", "Bravo", 10), _zone("1", "Alfa", 10), _zone("3", "Carlos", 50)]
    assert [z.code for z in rank(zones)] == ["3", "1", "2"]


def test_row_summary_in_everyday_words() -> None:
    text = row_summary(GapRowKey.ESCUELA_INFANTIL, people=23456, total=260310, zones=3)
    assert text == (
        "En la Comunidad de Madrid, 23.456 niños de 0 a 4 años (el 9,0 %) viven en 3 zonas "
        "donde faltan escuelas infantiles"
    )
    one = row_summary(GapRowKey.VIVIENDA, people=1200, total=669984, zones=1)
    assert "en 1 zona donde falta vivienda para familias" in one
    assert row_summary(GapRowKey.COLEGIO, people=0, total=683666, zones=0) == (
        "Ninguna zona de la Comunidad de Madrid tiene una falta clara de colegios"
    )


def test_zone_sentence_gives_people_ratio_and_chance() -> None:
    zone = ImpactZone("2807913", "Puente de Vallecas", 9876, 0.623, 2e-5, False)
    assert zone_sentence(GapRowKey.ESCUELA_INFANTIL, zone) == (
        "Viven aquí 9.876 niños de 0 a 4 años. Tienen 62 por cada 100 que tienen los "
        "municipios parecidos, y una diferencia así sale por azar menos de 1 entre 1.000 veces"
    )
    grouped = ImpactZone("28004", "El Álamo", 410, 0.5, 0.01, True)
    assert zone_sentence(GapRowKey.MAYORES, grouped).startswith(
        "Viven aquí 410 personas de 65 años o más. Junto con sus vecinos tienen 50 por cada 100"
    )


def test_zone_sentence_without_a_test_gives_only_the_ratio() -> None:
    zone = ImpactZone("28092", "Móstoles", 1200, 0.7, None, False)
    assert zone_sentence(GapRowKey.VIVIENDA, zone) == (
        "Viven aquí 1.200 hogares de 4 o más personas. Tienen 70 por cada 100 que tienen los "
        "municipios parecidos"
    )


def test_shown_p_value_never_rounds_a_significant_p_up_to_the_cut_off() -> None:
    assert shown_p_value(0.0249999) == 0.0249
    assert shown_p_value(0.00115372) == 0.00115
    assert shown_p_value(0.0) == 0.0


def test_share_is_bounded_and_the_summary_omits_an_unknown_total() -> None:
    assert share_of(5, 0) == 0.0
    assert share_of(12, 10) == 1.0
    text = row_summary(GapRowKey.FARMACIA, people=12, total=0, zones=1)
    assert text == "En la Comunidad de Madrid, 12 personas viven en 1 zona donde faltan farmacias"
