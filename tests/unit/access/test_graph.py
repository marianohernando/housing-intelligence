"""Walking graph arrays: deduplication, symmetric adjacency, connected share."""

import numpy as np
import pytest

from hi_domain.access.graph import from_edges


def _square() -> tuple[np.ndarray, ...]:
    # 10 -> 20 -> 30 -> 10 triangle (3-4-5 m) plus an island 40 -> 50 of 1 m.
    u = np.array([10, 20, 30, 40, 20])
    v = np.array([20, 30, 10, 50, 10])
    ux = np.array([0.0, 3.0, 0.0, 100.0, 3.0])
    uy = np.array([0.0, 0.0, 4.0, 0.0, 0.0])
    vx = np.array([3.0, 0.0, 0.0, 101.0, 0.0])
    vy = np.array([0.0, 4.0, 0.0, 0.0, 0.0])
    return u, v, ux, uy, vx, vy


def test_from_edges_keeps_each_segment_once() -> None:
    u, v, ux, uy, vx, vy = _square()
    network = from_edges(u, v, (ux, uy), (vx, vy), ["a", "b", "a", "a", "b"])
    assert network.n_nodes == 5
    assert network.n_edges == 4  # 20 -> 10 repeats 10 -> 20
    assert sorted(network.edge_length_m.round(6).tolist()) == [1.0, 3.0, 4.0, 5.0]
    assert network.total_km == pytest.approx(0.013)
    assert network.km_by_highway() == {"a": 0.0, "b": 0.0}


def test_adjacency_is_symmetric_and_keeps_shortest_parallel_edge() -> None:
    u = np.array([1, 2])
    v = np.array([2, 1])
    xs = (np.array([0.0, 10.0]), np.array([0.0, 0.0]))
    ys = (np.array([10.0, 0.0]), np.array([0.0, 0.0]))
    network = from_edges(u, v, xs, ys, ["a", "a"])
    matrix = network.adjacency().toarray()
    np.testing.assert_allclose(matrix, matrix.T)


def test_self_loops_are_dropped() -> None:
    network = from_edges(
        np.array([1]),
        np.array([1]),
        (np.array([0.0]), np.array([0.0])),
        (np.array([0.0]), np.array([0.0])),
        ["a"],
    )
    assert network.n_edges == 0
    assert network.main_component_share() == 0.0


def test_main_component_share_is_by_length() -> None:
    u, v, ux, uy, vx, vy = _square()
    network = from_edges(u, v, (ux, uy), (vx, vy), ["a"] * 5)
    assert network.main_component_share() == pytest.approx(12 / 13)
