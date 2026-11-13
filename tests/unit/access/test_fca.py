"""2SFCA on the walking network (D-217): conservation, catchments and the classic toy case."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hi_domain.access.fca import Catchments, catchments, spread_demand, two_step, zone_totals
from hi_domain.access.graph import from_edges
from hi_domain.access.walk import RoutableNetwork


def line_network(n: int, step: float) -> RoutableNetwork:
    """n nodes on a straight street, `step` metres apart, starting at x = 0."""
    u = np.arange(n - 1, dtype=np.int64)
    xs = u.astype(float) * step
    zeros = np.zeros(n - 1)
    network = from_edges(u, u + 1, (xs, zeros), (xs + step, zeros), ["residential"] * (n - 1))
    return RoutableNetwork.build(network)


def test_catchment_holds_exactly_the_nodes_within_walking_metres() -> None:
    net = line_network(11, 100.0)  # nodes at 0, 100, ..., 1000 m
    got = catchments(net, np.array([500.0]), np.array([0.0]), radius_m=250.0)
    xs = net.network.node_x[got.node]
    assert sorted(xs.tolist()) == [300.0, 400.0, 500.0, 600.0, 700.0]
    assert sorted(got.metres.tolist()) == [0.0, 100.0, 100.0, 200.0, 200.0]


def test_snap_leg_counts_against_the_catchment() -> None:
    net = line_network(11, 100.0)
    got = catchments(net, np.array([500.0]), np.array([60.0]), radius_m=250.0)
    assert sorted(got.metres.tolist()) == [60.0, 160.0, 160.0]


def test_classic_two_step_shares_capacity_among_who_can_reach_it() -> None:
    """Two facilities, three demand points; the middle one reaches both."""
    catch = Catchments(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 2]), np.zeros(4), 2)
    result = two_step(catch, np.array([10.0, 30.0]), np.array([100.0, 100.0, 200.0]))
    assert result.ratio.tolist() == pytest.approx([10 / 200, 30 / 300])
    assert result.access.tolist() == pytest.approx([0.05, 0.15, 0.10])


def test_facility_nobody_reaches_is_reported_not_spread() -> None:
    catch = Catchments(np.array([0]), np.array([0]), np.zeros(1), 2)
    result = two_step(catch, np.array([5.0, 7.0]), np.array([10.0]))
    assert np.isnan(result.ratio[1])
    assert result.unreached_capacity == 7.0


# People and capacities are counts: no subnormal floats (5e-324 people would turn a share into
# an overflow, which is float arithmetic, not 2SFCA). CI found that case on 12 Nov.
COUNTS = st.one_of(st.just(0.0), st.floats(1e-3, 1000))


@settings(max_examples=60, deadline=None)
@given(
    st.lists(st.one_of(st.just(0.0), st.floats(1e-3, 50)), min_size=1, max_size=6),
    st.lists(COUNTS, min_size=1, max_size=8),
    st.data(),
)
def test_capacity_is_conserved(
    supply: list[float], demand: list[float], data: st.DataObject
) -> None:
    """sum_k P_k A_k == capacity of the facilities someone reaches (Luo & Wang's identity)."""
    pair = st.tuples(st.integers(0, len(supply) - 1), st.integers(0, len(demand) - 1))
    pairs = data.draw(st.lists(pair, unique=True))
    fac = np.array([p[0] for p in pairs], dtype=np.int64)
    node = np.array([p[1] for p in pairs], dtype=np.int64)
    s, d = np.array(supply), np.array(demand)
    result = two_step(Catchments(fac, node, np.zeros(len(pairs)), len(supply)), s, d)
    reached = float((d * result.access).sum())
    assert reached == pytest.approx(float(s.sum()) - result.unreached_capacity, rel=1e-9, abs=1e-6)


def test_more_capacity_never_lowers_anyone_access() -> None:
    catch = Catchments(np.array([0, 0, 1]), np.array([0, 1, 1]), np.zeros(3), 2)
    demand = np.array([50.0, 80.0])
    low = two_step(catch, np.array([1.0, 1.0]), demand).access
    high = two_step(catch, np.array([3.0, 1.0]), demand).access
    assert np.all(high >= low)


def test_demand_spreads_by_street_weight_and_zone_totals_add_up() -> None:
    zone = np.array([0, 0, 1, -1], dtype=np.int64)
    demand = spread_demand(zone, np.array([1.0, 3.0, 2.0, 5.0]), np.array([400.0, 50.0]))
    assert demand.tolist() == pytest.approx([100.0, 300.0, 50.0, 0.0])
    capacity, people = zone_totals(zone, demand, np.array([0.01, 0.02, 0.1, 9.0]), 2)
    assert people.tolist() == pytest.approx([400.0, 50.0])
    assert capacity.tolist() == pytest.approx([7.0, 5.0])
