"""Feature methods on synthetic frames: null semantics, invariants and monotonicity."""

import math
from datetime import date
from typing import Any, cast

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_features import methods

Y = date(2025, 1, 1)


def _obs(rows: list[tuple[str, dict[str, str], float | None]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "territory_code": c,
                "period_start": Y,
                "dims": d,
                "value": v,
                "null_reason": None if v is not None else "SOURCE_MISSING",
            }
            for c, d, v in rows
        ]
    )


POP = _obs(
    [
        ("28001", {"edad": "total"}, 100.0),
        ("28001", {"edad": "de_0_4_anos"}, 10.0),
        ("28001", {"edad": "de_65_69_anos"}, 30.0),
        ("28002", {"edad": "total"}, 0.0),
        ("28002", {"edad": "de_65_69_anos"}, 0.0),
        ("28003", {"edad": "total"}, None),
        ("28003", {"edad": "de_65_69_anos"}, 5.0),
    ]
)


def _is_missing(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _by_code(frame: pd.DataFrame) -> dict[str, dict[str, object]]:
    return {r["territory_code"]: r for r in frame.to_dict("records")}


def test_share_propagates_unknown_and_not_applicable() -> None:
    out = _by_code(methods.metric_share(POP, {"edad": ["de_65_69_anos"]}, {"edad": ["total"]}))
    assert out["28001"]["value"] == 30.0
    assert out["28002"]["null_reason"] == "NOT_APPLICABLE"  # 0/0 is not a 0 %
    assert out["28003"]["null_reason"] == "SOURCE_MISSING"  # never imputed


def test_metric_value_requires_exactly_one_row() -> None:
    out = _by_code(methods.metric_value(POP, {"edad": "total"}))
    assert out["28001"]["value"] == 100.0
    assert pd.isna(out["28003"]["value"])  # type: ignore[arg-type]
    assert out["28003"]["null_reason"] == "SOURCE_MISSING"


def test_only_latest_period_is_used() -> None:
    old = POP.assign(period_start=date(2020, 1, 1), value=999.0)
    out = _by_code(methods.metric_value(pd.concat([old, POP]), {"edad": "total"}))
    assert out["28001"]["value"] == 100.0


def test_weighted_mean_and_its_confidence() -> None:
    obs = _obs(
        [
            ("28001", {"tamano": "de_1_persona"}, 2.0),
            ("28001", {"tamano": "de_3_personas"}, 2.0),
            ("28001", {"tamano": "total"}, 4.0),
        ]
    )
    out = _by_code(
        methods.metric_weighted_mean(
            obs, "tamano", {"de_1_persona": 1, "de_3_personas": 3}, confidence=0.9
        )
    )
    assert out["28001"]["value"] == 2.0
    assert out["28001"]["confidence"] == 0.9


def _places(codes: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"territory_code": c, "subcategory": "Centro de salud", "attributes": {"plazas": "10"}}
            for c in codes
        ]
    )


def test_no_place_in_official_register_is_confirmed_zero() -> None:
    out = _by_code(
        methods.places_per_population(_places(["28001"]), POP, {"edad": ["total"]}, 1000.0)
    )
    assert out["28001"]["value"] == 10.0
    assert out["28002"]["null_reason"] == "NOT_APPLICABLE"
    assert out["28003"]["null_reason"] == "SOURCE_MISSING"


def test_per_population_rows_keep_their_counts() -> None:
    """GAP-001 F5: the counts behind each ratio, so a shortfall can be tested (D-213)."""
    out = methods.places_per_population(
        _places(["28001", "28001", "28003"]), POP, {"edad": ["total"]}, 1000.0
    )
    rows = _by_code(out)
    assert (rows["28001"]["numerator"], rows["28001"]["denominator"]) == (2.0, 100.0)
    assert rows["28002"]["numerator"] != rows["28002"]["numerator"]  # NaN: NOT_APPLICABLE
    assert rows["28003"]["numerator"] != rows["28003"]["numerator"]  # NaN: unknown population
    region = out.loc[out["territory_level"] == "ccaa"].iloc[0]
    assert (region["numerator"], region["denominator"]) == (2.0, 100.0)  # known zones only


def test_small_denominators_lower_confidence() -> None:
    out = _by_code(
        methods.places_per_population(
            _places(["28001"]), POP, {"edad": ["total"]}, 1000.0, small_population=500
        )
    )
    assert out["28001"]["confidence"] == methods.SMALL_POPULATION_CONFIDENCE


def test_attribute_sum_confidence_reflects_missing_attributes() -> None:
    places = pd.concat(
        [
            _places(["28001"]),
            pd.DataFrame(
                [{"territory_code": "28001", "subcategory": "Centro de salud", "attributes": {}}]
            ),
        ]
    )
    out = _by_code(
        methods.place_attribute_per_population(places, POP, {"edad": ["total"]}, 100.0, "plazas")
    )
    assert out["28001"]["value"] == 10.0
    assert out["28001"]["confidence"] == 0.5


@given(st.integers(min_value=0, max_value=50), st.integers(min_value=1, max_value=20))
def test_more_places_never_lowers_coverage(n: int, extra: int) -> None:
    base = methods.places_per_population(_places(["28001"] * n), POP, {"edad": ["total"]}, 1000.0)
    more = methods.places_per_population(
        _places(["28001"] * (n + extra)), POP, {"edad": ["total"]}, 1000.0
    )
    assert _by_code(more)["28001"]["value"] > _by_code(base)["28001"]["value"]  # type: ignore[operator]


@given(st.floats(min_value=0, max_value=1e6), st.floats(min_value=0, max_value=1e6))
def test_shares_stay_within_0_100_when_members_are_subsets(part: float, rest: float) -> None:
    obs = _obs([("28001", {"edad": "total"}, part + rest), ("28001", {"edad": "x"}, part)])
    value = _by_code(methods.metric_share(obs, {"edad": ["x"]}, {"edad": ["total"]}))["28001"][
        "value"
    ]
    assert value is None or 0.0 <= value <= 100.0 + 1e-9  # type: ignore[operator]


def test_regional_reference_is_region_total_over_region_population() -> None:
    """GAP-001: the reference is the region's total over its population, not a mean of ratios."""
    pop = _obs(
        [
            ("28001", {"edad": "total"}, 1000.0),
            ("28002", {"edad": "total"}, 3000.0),
            ("28003", {"edad": "total"}, 0.0),
        ]
    )
    frame = methods.places_per_population(
        _places(["28001", "28002", "28002", "28002", "28003"]), pop, {"edad": ["total"]}, 1000.0
    )
    region = frame.loc[frame["territory_level"] == methods.REGION_LEVEL]
    assert region["territory_code"].tolist() == [methods.REGION_CODE]
    assert region["value"].iloc[0] == 1000.0 * 5 / 4000  # the place in a 0-population town counts
    assert region["confidence"].iloc[0] == 1.0
    municipal = frame.loc[frame["territory_level"] != methods.REGION_LEVEL]
    assert set(municipal["territory_code"]) == {"28001", "28002", "28003"}


def test_regional_reference_confidence_drops_with_unknown_population() -> None:
    frame = methods.places_per_population(_places(["28001"]), POP, {"edad": ["total"]}, 1000.0)
    region = _by_code(frame)[methods.REGION_CODE]
    assert region["value"] == 1000.0 * 1 / 100  # 28003 has unknown population: left out
    assert region["confidence"] == 2 / 3  # 2 of 3 municipios have a known population


@given(st.integers(min_value=0, max_value=50), st.integers(min_value=1, max_value=20))
def test_more_places_never_lowers_the_regional_reference(n: int, extra: int) -> None:
    base = methods.places_per_population(_places(["28001"] * n), POP, {"edad": ["total"]}, 1000.0)
    more = methods.places_per_population(
        _places(["28001"] * (n + extra)), POP, {"edad": ["total"]}, 1000.0
    )
    assert (
        _by_code(more)[methods.REGION_CODE]["value"] > _by_code(base)[methods.REGION_CODE]["value"]
    )  # type: ignore[operator]


NUM = _obs(
    [
        ("28001", {"superficie": "grande"}, 30.0),
        ("28001", {"superficie": "otra"}, 70.0),
        ("28002", {"superficie": "grande"}, None),  # unknown numerator
        ("28004", {"superficie": "grande"}, 5.0),
    ]
)
DEN = _obs(
    [
        ("28001", {"tamano": "grande"}, 20.0),
        ("28002", {"tamano": "grande"}, 10.0),
        ("28003", {"tamano": "grande"}, 10.0),  # no numerator row at all
        ("28004", {"tamano": "grande"}, 0.0),
    ]
)


def test_metric_ratio_of_two_metrics_never_turns_unknown_into_zero() -> None:
    """GAP-001 F3b: per x numerator / denominator, two metrics of the same zones."""
    out = _by_code(
        methods.metric_ratio(
            NUM, {"superficie": ["grande"]}, DEN, {"tamano": ["grande"]}, 100.0, confidence=0.8
        )
    )
    assert out["28001"]["value"] == 150.0
    assert out["28001"]["confidence"] == 0.8
    assert out["28002"]["null_reason"] == "SOURCE_MISSING"  # unknown numerator, never 0
    assert out["28003"]["null_reason"] == "SOURCE_MISSING"  # no numerator row, never 0
    assert out["28004"]["null_reason"] == "NOT_APPLICABLE"  # 5 / 0
    region = out[methods.REGION_CODE]
    assert region["value"] == 100.0 * (30.0 + 5.0) / (20.0 + 0.0)  # zones with both known
    assert region["confidence"] == pytest.approx(0.8 * 2 / 4)


def test_metric_ratio_small_denominator_lowers_confidence() -> None:
    out = _by_code(
        methods.metric_ratio(
            NUM, {"superficie": "*"}, DEN, {"tamano": "*"}, 100.0, small_population=50.0
        )
    )
    assert out["28001"]["value"] == 500.0
    assert out["28001"]["confidence"] == methods.SMALL_POPULATION_CONFIDENCE


@given(st.floats(min_value=0, max_value=1e6), st.floats(min_value=1, max_value=1e6))
def test_metric_ratio_grows_with_its_numerator(part: float, more: float) -> None:
    def ratio(value: float) -> float:
        num = _obs([("28001", {"k": "v"}, value)])
        den = _obs([("28001", {"k": "v"}, 1000.0)])
        return _by_code(methods.metric_ratio(num, {"k": "v"}, den, {"k": "v"}, 100.0))["28001"][
            "value"
        ]  # type: ignore[return-value]

    assert ratio(part + more) > ratio(part)


def test_not_published_gives_one_explicit_unknown_per_zone() -> None:
    """A source with no rows at a level (e.g. housing tables by district) is SIN DATOS there,
    with its reason: never 0 and never an absent row."""
    out = methods.not_published(POP)
    assert sorted(out["territory_code"]) == ["28001", "28002", "28003"]
    assert all(pd.isna(v) for v in out["value"].tolist())
    assert set(out["null_reason"]) == {"SOURCE_MISSING"}
    assert set(out["confidence"]) == {0.0}


def test_metric_ratio_keeps_the_reason_of_an_unknown_input() -> None:
    num = _obs([("28001", {"k": "v"}, None), ("28002", {"k": "v"}, None)])
    den = _obs([("28001", {"k": "v"}, None), ("28002", {"k": "v"}, 10.0)])
    num.loc[1, "null_reason"] = "UNKNOWN"
    den.loc[0, "null_reason"] = "STALE"
    out = _by_code(methods.metric_ratio(num, {"k": "v"}, den, {"k": "v"}, 100.0))
    assert out["28001"]["null_reason"] == "STALE"  # both unknown: the denominator's reason
    assert out["28002"]["null_reason"] == "UNKNOWN"  # the numerator's own reason, never 0
    assert methods.REGION_CODE not in out  # no zone with both known: no reference


def _weights(rows: list[tuple[str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["territory_code", "postcode", "weight"])


CP_RENT = _obs([("28001", {}, 20.0), ("28002", {}, 10.0), ("28003", {}, None)])


def test_postcode_mean_weights_each_postcode_by_its_places() -> None:
    weights = _weights([("2807901", "28001", 3.0), ("2807901", "28002", 1.0)])
    out = methods.postcode_weighted_mean(CP_RENT, weights, {}, confidence=0.8)
    row = out.iloc[0]
    assert row["territory_code"] == "2807901"
    assert row["value"] == pytest.approx(17.5)
    assert row["confidence"] == pytest.approx(0.8)  # every place has a published postcode


def test_postcode_mean_confidence_is_the_share_of_places_with_a_value() -> None:
    weights = _weights([("2807902", "28001", 1.0), ("2807902", "28003", 1.0)])
    weights = pd.concat([weights, _weights([("2807902", "28999", 2.0)])])
    out = methods.postcode_weighted_mean(CP_RENT, weights, {}, confidence=0.8)
    row = out.iloc[0]
    assert row["value"] == pytest.approx(20.0)  # unknown postcodes never count as 0
    assert row["confidence"] == pytest.approx(0.8 * 1 / 4)


def test_postcode_mean_without_any_published_postcode_is_unknown_not_zero() -> None:
    """The zone's places carry postcodes, but the source publishes none of them: the source is
    missing, not our proxy (D-232 tells the two apart, so the text can say which)."""
    weights = _weights([("2807903", "28003", 5.0), ("2807903", "28999", 1.0)])
    row = methods.postcode_weighted_mean(CP_RENT, weights, {}).iloc[0]
    assert row["value"] is None
    assert row["null_reason"] == "SOURCE_MISSING"
    assert row["confidence"] == 0.0


@given(
    st.floats(min_value=1, max_value=50),
    st.floats(min_value=1, max_value=50),
    st.floats(min_value=0.1, max_value=100),
    st.floats(min_value=0.1, max_value=100),
)
def test_postcode_mean_stays_between_its_postcodes(
    a: float, b: float, wa: float, wb: float
) -> None:
    obs = _obs([("28001", {}, a), ("28002", {}, b)])
    weights = _weights([("2807901", "28001", wa), ("2807901", "28002", wb)])
    value = methods.postcode_weighted_mean(obs, weights, {}).iloc[0]["value"]
    assert min(a, b) - 1e-9 <= value <= max(a, b) + 1e-9


def test_a_zone_with_few_places_keeps_its_value_with_capped_confidence() -> None:
    """D-232: a barrio has far fewer places than a district; below `min_places` the mean rests
    on a handful of addresses, so its confidence is capped (the value is not hidden)."""
    weights = _weights(
        [("28079011", "28001", 2.0), ("28079012", "28001", 4.0), ("28079012", "28002", 4.0)]
    )
    out = _by_code(
        methods.postcode_weighted_mean(
            CP_RENT, weights, {}, confidence=0.6, min_places=5, few_places_confidence=0.3
        )
    )
    assert out["28079011"]["value"] == pytest.approx(20.0)
    assert out["28079011"]["confidence"] == pytest.approx(0.3)
    # 6 places, only 4 with a published value: the mean rests on 4, so it is capped too
    mixed = _weights([("28079013", "28001", 4.0), ("28079013", "28999", 2.0)])
    row = methods.postcode_weighted_mean(
        CP_RENT, mixed, {}, confidence=0.6, min_places=5, few_places_confidence=0.3
    ).iloc[0]
    assert row["confidence"] == pytest.approx(0.3)
    assert out["28079012"]["value"] == pytest.approx(15.0)
    assert out["28079012"]["confidence"] == pytest.approx(0.6)


def test_a_zone_without_any_place_is_an_explicit_null_never_absent() -> None:
    """Every zone of the level gets a row: one with no place carrying a postcode is
    SOURCE_NO_COVERAGE (D-232: barrio Sol), never left out and never 0."""
    weights = _weights([("28079011", "28001", 6.0)])
    out = _by_code(
        methods.postcode_weighted_mean(CP_RENT, weights, {}, zones=["28079011", "28079016"])
    )
    assert out["28079011"]["value"] == pytest.approx(20.0)
    assert _is_missing(out["28079016"]["value"])
    assert out["28079016"]["null_reason"] == "SOURCE_NO_COVERAGE"  # no place to locate a postcode


def test_postcode_mean_uses_the_latest_period_only() -> None:
    old = _obs([("28001", {}, 99.0)]).assign(period_start=date(2023, 1, 1))
    obs = pd.concat([old, _obs([("28001", {}, 20.0)])])
    weights = _weights([("2807901", "28001", 1.0)])
    assert methods.postcode_weighted_mean(obs, weights, {}).iloc[0]["value"] == 20.0


def test_a_zone_the_source_leaves_out_gets_an_explicit_null() -> None:
    """Gate 3 null contract: Zarzalejo has no tenure row in the census table -> SOURCE_MISSING."""
    from hi_features.methods import fill_missing_zones, result_frame

    result = result_frame(
        [
            {
                "territory_code": "28001",
                "period_start": "2021-01-01",
                "value": 1.0,
                "null_reason": None,
                "confidence": 1.0,
                "territory_level": None,  # a feature's own level is set when persisting
            },
            {
                "territory_code": "28",
                "period_start": "2021-01-01",
                "value": 2.0,
                "null_reason": None,
                "confidence": 1.0,
                "territory_level": "ccaa",
            },
        ]
    )
    filled = fill_missing_zones(result, ["28001", "28183"], "municipio")
    added = filled[filled["territory_code"] == "28183"].iloc[0]
    assert added["value"] is None or added["value"] != added["value"]
    assert added["null_reason"] == "SOURCE_MISSING"
    assert added["period_start"] == "2021-01-01"
    assert len(filled) == 3
    assert fill_missing_zones(filled, ["28001", "28183"], "municipio").shape == filled.shape


# D-228: the rent of a lease signed in the year, from the Agencia Tributaria's comparison of
# new leases with all of them (mean rent and mean m² of each).
def _irpf(rows: list[tuple[str, float | None, float | None]]) -> pd.DataFrame:
    """(code, value for all leases, value for new leases)."""
    out: list[tuple[str, dict[str, str], float | None]] = []
    for code, every, new in rows:
        out += [(code, {"contratos": "todos"}, every), (code, {"contratos": "nuevos"}, new)]
    return _obs(out)


IRPF_RENT = _irpf([("28079", 1012.0, 1167.0), ("28005", 735.0, 840.0), ("28", 949.0, 1101.0)])
IRPF_M2 = _irpf([("28079", 71.0, 68.0), ("28005", 77.0, 77.0), ("28", 75.0, 72.0)])


def test_new_contract_factor_is_the_ratio_of_euros_per_m2() -> None:
    factors = methods.new_contract_factors(IRPF_RENT, IRPF_M2).factors
    assert factors["28079"] == pytest.approx((1167 / 68) / (1012 / 71))  # 1,204
    assert factors["28005"] == pytest.approx(840 / 735)  # same m²: the ratio of rents


def test_a_zone_without_both_contract_kinds_has_no_factor() -> None:
    rent = _irpf([("28001", 900.0, None)])
    m2 = _irpf([("28001", 80.0, 78.0)])
    assert methods.new_contract_factors(rent, m2).factors == {}  # never a guessed 1


def test_rent_of_new_leases_uses_the_zone_factor_or_the_declared_fallback() -> None:
    rent = _obs(
        [
            ("28079", {"tipo_vivienda": "viviendas_habituales"}, 15.1),
            ("28006", {"tipo_vivienda": "viviendas_habituales"}, 12.7),
            ("28007", {"tipo_vivienda": "viviendas_habituales"}, None),
        ]
    )
    base = methods.metric_value(rent, {"tipo_vivienda": "viviendas_habituales"}, 0.9)
    factors = methods.new_contract_factors(IRPF_RENT, IRPF_M2)
    out = _by_code(methods.apply_new_contract_factors(base, factors, fallback="28"))
    madrid = (1167 / 68) / (1012 / 71)
    madrid_adjustment = cast(dict[str, Any], out["28079"]["adjustment"])
    assert out["28079"]["value"] == pytest.approx(15.1 * madrid)
    assert madrid_adjustment["factor_from"] == "28079"
    assert madrid_adjustment["all_contracts_value"] == pytest.approx(15.1)
    region = (1101 / 72) / (949 / 75)
    assert out["28006"]["value"] == pytest.approx(12.7 * region)  # no table of its own
    assert cast(dict[str, Any], out["28006"]["adjustment"])["factor_from"] == "28"
    assert out["28006"]["confidence"] == pytest.approx(0.9)
    assert math.isnan(cast(float, out["28007"]["value"]))  # unknown stays unknown


def test_without_own_factor_or_fallback_the_rent_of_new_leases_is_unknown() -> None:
    rent = _obs([("28006", {}, 12.7)])
    base = methods.metric_value(rent, {})
    factors = methods.new_contract_factors(IRPF_RENT, IRPF_M2)
    row = methods.apply_new_contract_factors(base, factors, fallback=None).iloc[0]
    assert row["value"] is None
    assert row["null_reason"] == "SOURCE_MISSING"  # never the old figure under a new label


def test_district_rent_of_new_leases_adjusts_each_postcode_before_the_mean() -> None:
    cp_rent = _irpf([("28001", 1702.0, 1940.0)])
    cp_m2 = _irpf([("28001", 86.0, 78.0)])
    factors = methods.new_contract_factors(cp_rent, cp_m2)
    fallback = methods.new_contract_factors(IRPF_RENT, IRPF_M2).factors["28079"]
    weights = _weights([("2807904", "28001", 3.0), ("2807904", "28002", 1.0)])
    out = methods.postcode_weighted_mean(
        CP_RENT, weights, {}, confidence=0.8, new_contracts=(factors, fallback)
    )
    row = out.iloc[0]
    own = (1940 / 78) / (1702 / 86)
    assert row["value"] == pytest.approx((20.0 * own * 3 + 10.0 * fallback) / 4)
    assert row["adjustment"]["postcodes_with_own_factor"] == 1
    assert row["adjustment"]["postcodes_with_fallback"] == 1
    assert row["adjustment"]["all_contracts_value"] == pytest.approx(17.5)


def test_a_factor_of_another_year_stops_the_computation() -> None:
    """D-228 review: the note says the year; value and factor must be of the same one."""
    rent = _obs([("28079", {}, 15.1)])
    base = methods.metric_value(rent, {})
    old = methods.NewContractFactors({"28079": 1.2}, date(2024, 1, 1))
    with pytest.raises(ValueError, match="same year"):
        methods.apply_new_contract_factors(base, old, fallback=None)
    weights = _weights([("2807901", "28001", 1.0)])
    with pytest.raises(ValueError, match="same year"):
        methods.postcode_weighted_mean(CP_RENT, weights, {}, new_contracts=(old, 1.2))
