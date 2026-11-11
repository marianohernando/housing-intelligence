"""Walking distance from every street node to the nearest destination, summarised per zone.

Destinations are snapped to the nearest node of the main connected network; the snap leg is
added as a straight line. One multi-source Dijkstra per destination kind gives every node its
distance to the nearest destination. Zones summarise the nodes of the streets where people live
(origins), each weighted by the street length it stands for.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import KDTree

from hi_domain.access.graph import FloatArray, IntArray, WalkNetwork

ZERO_WEIGHT_M = 1e-6  # sparse graphs drop explicit zeros; a destination on a node is ~0 m away


@dataclass(frozen=True)
class RoutableNetwork:
    """The walking graph prepared once: adjacency, main component and a KD-tree over it."""

    network: WalkNetwork
    adjacency: csr_matrix
    main_nodes: IntArray
    tree: KDTree

    @classmethod
    def build(cls, network: WalkNetwork) -> "RoutableNetwork":
        adjacency = network.adjacency()
        _, labels = connected_components(adjacency, directed=False)
        sizes = np.bincount(labels[network.edge_u], weights=network.edge_length_m)
        main = np.flatnonzero(labels == int(np.argmax(sizes)))
        tree = KDTree(np.column_stack([network.node_x[main], network.node_y[main]]))
        return cls(network, adjacency, main.astype(np.int64), tree)

    def snap(self, x: FloatArray, y: FloatArray) -> tuple[IntArray, FloatArray]:
        """Nearest main-network node and the straight distance to it, for each point."""
        if len(x) == 0:
            return np.zeros(0, dtype=np.int64), np.zeros(0)
        distance, index = self.tree.query(np.column_stack([x, y]))
        return self.main_nodes[np.asarray(index, dtype=np.int64)], np.asarray(distance, float)

    def distance_to_nearest(self, x: FloatArray, y: FloatArray) -> FloatArray:
        """Metres from every node to the nearest destination (inf when none can be reached)."""
        n = self.network.n_nodes
        if len(x) == 0:
            return np.full(n, np.inf)
        nodes, snap_m = self.snap(x, y)
        order = np.lexsort((snap_m, nodes))  # several destinations on one node: keep the closest
        nodes, snap_m = nodes[order], snap_m[order]
        first = np.ones(len(nodes), dtype=bool)
        first[1:] = nodes[1:] != nodes[:-1]
        # A virtual node n reaches each destination's node through its snap leg (one direction
        # only); the street edges are already stored in both directions.
        streets = self.adjacency.tocoo()
        rows = np.concatenate([streets.row, np.full(int(first.sum()), n)])
        cols = np.concatenate([streets.col, nodes[first]])
        legs = np.maximum(snap_m[first], ZERO_WEIGHT_M)
        augmented = csr_matrix(
            (np.concatenate([streets.data, legs]), (rows, cols)), shape=(n + 1, n + 1)
        )
        distances = dijkstra(augmented, directed=True, indices=n)
        return np.asarray(distances, dtype=float)[:n]


def origin_weights(network: WalkNetwork, origin_highways: list[str]) -> FloatArray:
    """Street metres each node stands for: half of every incident origin street segment."""
    codes = [i for i, name in enumerate(network.highways) if name in origin_highways]
    is_origin = np.isin(network.edge_highway, codes)
    half = network.edge_length_m[is_origin] / 2
    weights = np.bincount(network.edge_u[is_origin], weights=half, minlength=network.n_nodes)
    weights += np.bincount(network.edge_v[is_origin], weights=half, minlength=network.n_nodes)
    return weights


@dataclass(frozen=True)
class ZoneSummary:
    """Per zone (index into the caller's zone list); NaN where a zone has no reachable street."""

    street_m: FloatArray
    reachable_m: FloatArray
    median_m: FloatArray
    within_share: FloatArray

    def reachable_share(self) -> FloatArray:
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(self.street_m > 0, self.reachable_m / self.street_m, np.nan)


def _weighted_median(
    zone: IntArray, distance: FloatArray, weight: FloatArray, n_zones: int
) -> FloatArray:
    order = np.lexsort((distance, zone))
    zone, distance, weight = zone[order], distance[order], weight[order]
    cumulative = np.cumsum(weight)
    totals = np.bincount(zone, weights=weight, minlength=n_zones)
    before = np.concatenate([[0.0], np.cumsum(totals)[:-1]])
    present = totals > 0
    targets = before[present] + totals[present] / 2
    position = np.minimum(np.searchsorted(cumulative, targets, side="left"), len(distance) - 1)
    median = np.full(n_zones, np.nan)
    median[present] = distance[position]
    return median


def summarise_zones(
    zone: NDArray[np.int64],
    weight: FloatArray,
    distance_m: FloatArray,
    n_zones: int,
    within_m: float,
) -> ZoneSummary:
    """Street-length-weighted median distance and share within `within_m`, per zone.

    `zone` is -1 for nodes outside every zone. Unreachable nodes (inf) count in `street_m` but
    not in the median or the share: an unknown distance is never treated as far or near.
    """
    origin = (zone >= 0) & (weight > 0)
    street = np.bincount(zone[origin], weights=weight[origin], minlength=n_zones)
    reachable = origin & np.isfinite(distance_m)
    zone_r, weight_r, distance_r = zone[reachable], weight[reachable], distance_m[reachable]
    reachable_m = np.bincount(zone_r, weights=weight_r, minlength=n_zones)
    near = distance_r <= within_m
    near_m = np.bincount(zone_r[near], weights=weight_r[near], minlength=n_zones)
    with np.errstate(invalid="ignore", divide="ignore"):
        within = np.where(reachable_m > 0, near_m / reachable_m, np.nan)
    median = (
        _weighted_median(zone_r, distance_r, weight_r, n_zones)
        if len(zone_r)
        else np.full(n_zones, np.nan)
    )
    return ZoneSummary(street, reachable_m, median, within)


def access_confidence(
    reachable_share: FloatArray, street_m: FloatArray, base: float, min_street_m: float
) -> FloatArray:
    """Base confidence scaled by the reachable street share; 0.5 at most for thin coverage."""
    confidence = base * np.nan_to_num(reachable_share, nan=0.0)
    return np.where(street_m < min_street_m, np.minimum(confidence, 0.5), confidence)
