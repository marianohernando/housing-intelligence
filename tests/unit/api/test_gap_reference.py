"""D-213: each zone against the other municipios of its type, with a tested shortfall."""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_api.services.gap_reference import Reference, References, assess
from hi_contracts.public import GapStatus
from hi_domain.gaps import REGION_TEXT, TerritoryType, classify, oriented_ratio

RURAL, URBAN = TerritoryType.RURAL, TerritoryType.URBANO
PER = 10_000.0


def _row(numerator: float, denominator: float) -> dict[str, Any]:
    value = PER * numerator / denominator
    return {
        "value": value,
        "inputs": {"counts": {"numerator": numerator, "denominator": denominator}},
    }


def _refs() -> References:
    # Madrid (urban, half of the urban population), Getafe (urban), two villages (rural)
    own = {"28079": (100.0, 3_000_000.0), "28065": (60.0, 200_000.0), "28001": (1.0, 70.0)}
    own |= {"28002": (3.0, 1_000.0)}
    types = {"28079": URBAN, "28065": URBAN, "28001": RURAL, "28002": RURAL}
    sums: dict[TerritoryType, list[float]] = {URBAN: [160.0, 3_200_000.0], RURAL: [4.0, 1_070.0]}
    return References(types=types, sums={"f": sums}, own={"f": own}, versions={"cm_x": "v1"})


REGION = _row(164.0, 3_201_070.0)


def test_a_municipio_is_compared_with_the_others_of_its_type() -> None:
    refs = _refs()
    madrid = refs.for_zone("f", "28079", REGION)
    assert madrid is not None
    assert madrid.label == "Otros municipios urbanos de la Comunidad de Madrid"
    assert madrid.rate == 60.0 / 200_000.0  # Getafe only: Madrid is left out
    assert madrid.value == pytest.approx(PER * 60.0 / 200_000.0)
    assert madrid.regional == REGION["value"]
    district = refs.for_zone("f", "2807905", REGION)  # a district leaves its whole municipio out
    assert district is not None and district.rate == madrid.rate
    assert refs.used


def test_no_counts_no_type_or_nothing_left_fall_back_to_the_region() -> None:
    refs = _refs()
    no_counts = {"value": 1.0, "inputs": {}}
    assert refs.for_zone("f", "28079", no_counts) == Reference(
        1.0, REGION_TEXT.label, REGION_TEXT.phrase, None, None
    )
    unknown_type = refs.for_zone("f", "28999", REGION)
    assert unknown_type is not None and unknown_type.label == REGION_TEXT.label
    alone = References(
        types={"28001": RURAL}, sums={"f": {RURAL: [1.0, 70.0]}}, own={"f": {"28001": (1.0, 70.0)}}
    )
    only_one = alone.for_zone("f", "28001", REGION)  # the only rural municipio: nothing left
    assert only_one is not None and only_one.label == REGION_TEXT.label
    assert refs.for_zone("f", "28079", {"value": None, "inputs": {}}) is None
    assert not alone.used


def test_assessment_marks_small_zones_and_skips_what_cannot_be_tested() -> None:
    ref = Reference(3.0, "x", "y", 4.0, rate=3.0 / PER)
    small = assess(_row(0.0, 1_000.0), ref, "higher_is_better")  # expects 0.3 cases
    assert small == (False, False)
    big = assess(_row(0.0, 100_000.0), ref, "higher_is_better")  # expects 30, has none
    assert big == (True, True)
    assert assess(_row(1.0, 10.0), ref, "lower_is_better") == (None, True)
    assert assess({"value": 1.0, "inputs": {}}, ref, "higher_is_better") == (None, True)


ORDER = [GapStatus.FALTA, GapStatus.JUSTO, GapStatus.CUBIERTO]


def _status(numerator: int, denominator: float, ref: Reference) -> GapStatus:
    row = _row(float(numerator), denominator)
    judged = assess(row, ref, "higher_is_better")
    status = classify(
        oriented_ratio(row["value"], ref.value, "higher_is_better"), significant=judged.significant
    )
    if not judged.reliable:
        assert status is not GapStatus.FALTA  # a zone too small is never FALTA
    return status


@given(
    st.integers(min_value=0, max_value=300),
    st.integers(min_value=1, max_value=50),
    st.floats(min_value=50, max_value=1e6),
    st.floats(min_value=1e-5, max_value=1e-2),
)
def test_more_supply_never_worsens_the_status(
    numerator: int, extra: int, denominator: float, rate: float
) -> None:
    ref = Reference(PER * rate, "x", "y", None, rate)
    before = _status(numerator, denominator, ref)
    after = _status(numerator + extra, denominator, ref)
    assert ORDER.index(after) >= ORDER.index(before)
