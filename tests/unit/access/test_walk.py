"""Walking distances and zone summaries: hand-worked cases plus invariants (doc 47)."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.sparse.csgraph import dijkstra

from hi_domain.access.graph import WalkNetwork, from_edges
from hi_domain.access.walk import (
    RoutableNetwork,
    access_confidence,
    origin_weights,
    summarise_zones,
)


def _line(n: int = 4, step: float = 100.0, highway: str = "residential") -> WalkNetwork:
    """Nodes 0..n-1 on a straight street, `step` metres apart."""
    u = np.arange(n - 1)
    xs = np.arange(n - 1, dtype=np.float64) * step
    zeros = np.zeros(n - 1)
    return from_edges(u, u + 1, (xs, zeros), (xs + step, zeros), [highway] * (n - 1))


def test_distance_follows_the_street_and_adds_the_snap_leg() -> None:
    routable = RoutableNetwork.build(_line())
    distance = routable.distance_to_nearest(np.array([0.0]), np.array([10.0]))
    np.testing.assert_allclose(distance, [10, 110, 210, 310])


def test_destination_on_a_node_is_zero_metres_away() -> None:
    routable = RoutableNetwork.build(_line())
    distance = routable.distance_to_nearest(np.array([200.0]), np.array([0.0]))
    assert distance[2] == pytest.approx(0, abs=1e-5)
    assert distance[0] == pytest.approx(200)


def test_no_destination_means_unknown_distance_never_zero() -> None:
    routable = RoutableNetwork.build(_line())
    assert np.isinf(routable.distance_to_nearest(np.zeros(0), np.zeros(0))).all()


def test_island_is_unreachable_and_destinations_snap_to_the_main_network() -> None:
    main = _line()
    island_u, island_v = np.array([100]), np.array([101])
    network = from_edges(
        np.concatenate([main.node_id[main.edge_u], island_u]),
        np.concatenate([main.node_id[main.edge_v], island_v]),
        (np.array([0.0, 100, 200, 1000]), np.array([0.0, 0, 0, 5])),
        (np.array([100.0, 200, 300, 1010]), np.array([0.0, 0, 0, 5])),
        ["residential"] * 4,
    )
    routable = RoutableNetwork.build(network)
    # The destination sits on the island; it snaps to the main street end (300, 0) instead.
    distance = routable.distance_to_nearest(np.array([1000.0]), np.array([5.0]))
    island = np.isin(network.node_id, [100, 101])
    assert np.isinf(distance[island]).all()
    assert np.isfinite(distance[~island]).all()
    assert distance[~island].min() == pytest.approx(np.hypot(700, 5))


def test_origin_weights_split_each_street_between_its_ends() -> None:
    network = _line()
    weights = origin_weights(network, ["residential"])
    np.testing.assert_allclose(weights, [50, 100, 100, 50])
    assert weights.sum() == pytest.approx(network.edge_length_m.sum())
    assert origin_weights(network, ["footway"]).sum() == 0


def test_zone_summary_hand_worked() -> None:
    network = _line()
    distance = RoutableNetwork.build(network).distance_to_nearest(np.array([0.0]), np.array([10.0]))
    summary = summarise_zones(
        np.array([0, 0, 1, -1]), origin_weights(network, ["residential"]), distance, 3, 150
    )
    np.testing.assert_allclose(summary.street_m, [150, 100, 0])
    np.testing.assert_allclose(summary.median_m[:2], [110, 210])  # weights 50 + 100 -> 110 m
    np.testing.assert_allclose(summary.within_share[:2], [1, 0])
    assert np.isnan(summary.median_m[2])  # a zone without streets has no value, not 0
    assert np.isnan(summary.within_share[2])


def test_unreachable_streets_lower_coverage_but_never_count_as_far() -> None:
    distance = np.array([100.0, np.inf, 300.0])
    summary = summarise_zones(np.zeros(3, dtype=np.int64), np.ones(3), distance, 1, 200)
    assert summary.reachable_share()[0] == pytest.approx(2 / 3)
    assert summary.median_m[0] == 100  # the lower weighted median of {100, 300}
    assert summary.within_share[0] == pytest.approx(0.5)


def test_confidence_drops_with_coverage_and_thin_zones() -> None:
    share = np.array([1.0, 0.5, np.nan, 1.0])
    street = np.array([5000.0, 5000.0, 0.0, 100.0])
    confidence = access_confidence(share, street, base=0.9, min_street_m=200)
    np.testing.assert_allclose(confidence, [0.9, 0.45, 0.0, 0.5])


@st.composite
def graphs(draw: st.DrawFn) -> tuple[WalkNetwork, np.ndarray, np.ndarray]:
    """Random grid graphs (some edges missing) plus random destination points."""
    side = draw(st.integers(2, 6))
    edges: list[tuple[int, int]] = []
    for i in range(side * side):
        if i % side < side - 1 and draw(st.booleans()):
            edges.append((i, i + 1))
        if i + side < side * side and draw(st.booleans()):
            edges.append((i, i + side))
    if not edges:
        edges = [(0, 1)]
    u = np.array([a for a, _ in edges])
    v = np.array([b for _, b in edges])
    step = 50.0
    network = from_edges(
        u,
        v,
        ((u % side) * step, (u // side) * step),
        ((v % side) * step, (v // side) * step),
        ["residential"] * len(edges),
    )
    coords = st.floats(-20, side * step + 20, allow_nan=False)
    points = draw(st.lists(st.tuples(coords, coords), min_size=1, max_size=6))
    return network, np.array([p[0] for p in points]), np.array([p[1] for p in points])


@settings(max_examples=60, deadline=None)
@given(graphs())
def test_matches_brute_force_from_each_destination(
    case: tuple[WalkNetwork, np.ndarray, np.ndarray],
) -> None:
    network, x, y = case
    routable = RoutableNetwork.build(network)
    nodes, snap_m = routable.snap(x, y)
    single = dijkstra(network.adjacency(), directed=False, indices=nodes)
    expected = np.min(np.atleast_2d(single) + snap_m[:, None], axis=0)
    got = routable.distance_to_nearest(x, y)
    finite = np.isfinite(expected)
    np.testing.assert_allclose(got[finite], expected[finite], atol=1e-5)
    assert np.isinf(got[~finite]).all()
    assert (got[finite] >= 0).all()


@settings(max_examples=60, deadline=None)
@given(graphs(), st.integers(0, 5))
def test_adding_a_destination_never_worsens_any_zone(
    case: tuple[WalkNetwork, np.ndarray, np.ndarray], split: int
) -> None:
    network, x, y = case
    split = min(split, len(x) - 1)
    routable = RoutableNetwork.build(network)
    before = routable.distance_to_nearest(x[: split + 1], y[: split + 1])
    after = routable.distance_to_nearest(x, y)
    assert (after <= before + 1e-9).all()
    zone = np.arange(network.n_nodes) % 3
    weights = origin_weights(network, ["residential"])
    s_before = summarise_zones(zone, weights, before, 3, 75)
    s_after = summarise_zones(zone, weights, after, 3, 75)
    known = ~np.isnan(s_before.median_m) & ~np.isnan(s_after.median_m)
    assert (s_after.median_m[known] <= s_before.median_m[known] + 1e-9).all()
    known = ~np.isnan(s_before.within_share) & ~np.isnan(s_after.within_share)
    assert (s_after.within_share[known] >= s_before.within_share[known] - 1e-9).all()


@settings(max_examples=60, deadline=None)
@given(
    st.lists(st.floats(0, 1), min_size=1, max_size=20),
    st.lists(st.floats(0, 10_000), min_size=1, max_size=20),
    st.floats(0, 1),
)
def test_less_coverage_never_gives_more_confidence(
    shares: list[float], streets: list[float], cut: float
) -> None:
    n = min(len(shares), len(streets))
    share, street = np.array(shares[:n]), np.array(streets[:n])
    full = access_confidence(share, street, base=0.9, min_street_m=200)
    lower = access_confidence(share * cut, street * cut, base=0.9, min_street_m=200)
    assert (lower <= full + 1e-12).all()
    assert ((full >= 0) & (full <= 0.9)).all()


def test_same_input_same_output() -> None:
    network = _line(6)
    routable = RoutableNetwork.build(network)
    x, y = np.array([30.0, 410.0]), np.array([5.0, -3.0])
    np.testing.assert_array_equal(
        routable.distance_to_nearest(x, y), RoutableNetwork.build(network).distance_to_nearest(x, y)
    )
