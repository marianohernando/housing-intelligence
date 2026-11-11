"""Feature methods on synthetic frames: null semantics, invariants and monotonicity."""

from datetime import date

import pandas as pd
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
