"""GAP-001 classification: oriented ratio, declared cut-offs, unknown never classified."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.public import GapStatus
from hi_domain.gaps import (
    GAP_METHOD,
    UnclassifiableError,
    classify,
    es_number,
    explanation,
    oriented_ratio,
)


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
