"""Small zones compared with their nearest same-type neighbours (D-217)."""

from collections.abc import Callable

import pytest

from hi_contracts.public import GapStatus
from hi_domain.gaps import min_expected, pool_with_neighbours, pooled_status

FLOOR = min_expected() or 0.0


def rate_from(counts: dict[str, tuple[float, float]]) -> Callable[[set[str]], float | None]:
    def rate_without(members: set[str]) -> float | None:
        num = sum(c[0] for k, c in counts.items() if k not in members)
        den = sum(c[1] for k, c in counts.items() if k not in members)
        return num / den if num > 0 and den > 0 else None

    return rate_without


COUNTS = {
    "a": (0.0, 500.0),  # tiny village with nothing
    "b": (1.0, 800.0),
    "c": (1.0, 900.0),
    "d": (2.0, 1500.0),
    "big": (30.0, 20000.0),
}


def test_a_large_zone_is_never_pooled() -> None:
    pool = pool_with_neighbours("big", COUNTS, ["a", "b"], rate_from(COUNTS), FLOOR)
    assert pool is not None
    assert pool.codes == ["big"]


def test_small_zone_adds_neighbours_in_order_until_the_floor() -> None:
    pool = pool_with_neighbours("a", COUNTS, ["b", "c", "d", "big"], rate_from(COUNTS), FLOOR)
    assert pool is not None
    assert pool.codes[:3] == ["a", "b", "c"]
    assert pool.expected >= FLOOR
    # the reference never includes a member of the group
    rest = {k: v for k, v in COUNTS.items() if k not in pool.codes}
    rate = sum(v[0] for v in rest.values()) / sum(v[1] for v in rest.values())
    assert pool.expected == pytest.approx(sum(COUNTS[m][1] for m in pool.codes) * rate)


def test_group_status_uses_the_same_cuts_and_test() -> None:
    pool = pool_with_neighbours("a", COUNTS, ["b", "c", "d", "big"], rate_from(COUNTS), FLOOR)
    assert pool is not None
    assert pooled_status(pool) in {GapStatus.JUSTO, GapStatus.CUBIERTO, GapStatus.FALTA}


def test_not_enough_neighbours_gives_no_group() -> None:
    counts = {"a": (0.0, 10.0), "b": (0.0, 10.0), "z": (5.0, 100000.0)}
    assert pool_with_neighbours("a", counts, ["b"], rate_from(counts), FLOOR) is None


def test_clear_shortfall_in_a_pooled_group_is_falta() -> None:
    counts = {"a": (0.0, 3000.0), "b": (0.0, 3000.0), "rest": (100.0, 50000.0)}
    pool = pool_with_neighbours("a", counts, ["b"], rate_from(counts), FLOOR)
    assert pool is not None
    assert pooled_status(pool) is GapStatus.FALTA
