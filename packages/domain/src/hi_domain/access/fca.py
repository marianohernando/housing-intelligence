"""Two-step floating catchment area (2SFCA) on the walking network (D-217).

Luo & Wang (2003): every facility's capacity is shared among the people who can reach it; a
person's access is the sum of the shares of the facilities they can reach.
  step 1, per facility j: R_j = S_j / sum of the demand within its catchment
  step 2, per demand point k: A_k = sum of R_j over the facilities whose catchment holds k
Capacity is conserved: sum_k P_k A_k equals the capacity of the facilities that someone can
reach, so the regional figure is that capacity over the regional population.
"""

from dataclasses import dataclass

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import KDTree

from hi_domain.access.graph import FloatArray, IntArray
from hi_domain.access.walk import RoutableNetwork


@dataclass(frozen=True)
class Catchments:
    """(facility, node) pairs within the catchment, with the walking metres between them."""

    facility: IntArray
    node: IntArray
    metres: FloatArray
    n_facilities: int


@dataclass(frozen=True)
class FcaResult:
    ratio: FloatArray  # R_j per facility; nan when nobody lives in its catchment
    access: FloatArray  # A_k per network node (0 when no facility is in reach)
    unreached_capacity: float  # capacity of facilities with no demand in their catchment


def catchments(
    network: RoutableNetwork,
    x: FloatArray,
    y: FloatArray,
    radius_m: float,
    all_nodes: KDTree | None = None,
) -> Catchments:
    """Nodes within `radius_m` walking metres of each facility (snap leg included).

    Network distance is never shorter than the straight line, so the nodes within `radius_m`
    in a straight line of the facility hold every node it can reach: Dijkstra runs on that
    small subgraph only, which is exact and fast.
    """
    tree = all_nodes or KDTree(np.column_stack([network.network.node_x, network.network.node_y]))
    source, snap_m = network.snap(x, y)
    parts: list[tuple[IntArray, IntArray, FloatArray]] = []
    for j in range(len(x)):
        budget = radius_m - float(snap_m[j])
        if budget < 0:
            continue
        near = np.asarray(tree.query_ball_point((float(x[j]), float(y[j])), radius_m), np.int64)
        position = np.flatnonzero(near == source[j])
        if len(near) == 0 or len(position) == 0:
            continue
        sub = network.adjacency[near][:, near]
        metres = np.asarray(dijkstra(sub, directed=True, indices=int(position[0]), limit=budget))
        hit = np.flatnonzero(np.isfinite(metres))
        parts.append((np.full(len(hit), j, np.int64), near[hit], metres[hit] + snap_m[j]))
    if not parts:
        empty = np.zeros(0, np.int64)
        return Catchments(empty, empty, np.zeros(0), len(x))
    facility, node, metres = (np.concatenate(p) for p in zip(*parts, strict=True))
    return Catchments(facility, node, metres, len(x))


def two_step(catch: Catchments, supply: FloatArray, demand: FloatArray) -> FcaResult:
    """2SFCA with a binary catchment. `demand` is per network node (0 where nobody lives)."""
    if len(supply) != catch.n_facilities:
        msg = f"{len(supply)} capacities for {catch.n_facilities} facilities"
        raise ValueError(msg)
    if np.any(supply < 0) or np.any(demand < 0):
        raise ValueError("capacity and demand cannot be negative")
    reached = np.bincount(catch.facility, weights=demand[catch.node], minlength=len(supply))
    ratio = np.full(len(supply), np.nan)
    np.divide(supply, reached, out=ratio, where=reached > 0)
    share = np.nan_to_num(ratio[catch.facility], nan=0.0)
    access = np.bincount(catch.node, weights=share, minlength=len(demand))
    return FcaResult(ratio, access, float(supply[reached <= 0].sum()))


def zone_totals(
    zone: IntArray, demand: FloatArray, access: FloatArray, n_zones: int
) -> tuple[FloatArray, FloatArray]:
    """Per zone: capacity reaching its people (sum P_k A_k) and its people (sum P_k).

    `zone` is the zone index of each node, -1 outside every zone. The ratio of the two is the
    population-weighted mean access of the zone.
    """
    inside = zone >= 0
    capacity = np.bincount(zone[inside], weights=(demand * access)[inside], minlength=n_zones)
    people = np.bincount(zone[inside], weights=demand[inside], minlength=n_zones)
    return capacity, people


def spread_demand(zone: IntArray, weight: FloatArray, population: FloatArray) -> FloatArray:
    """People per node: each zone's population over its nodes, in proportion to `weight`.

    D-210 places people on the streets where they live (street metres per node); a zone
    without origin streets keeps its people unplaced (they reach nothing and count nowhere).
    """
    inside = zone >= 0
    total = np.bincount(zone[inside], weights=weight[inside], minlength=len(population))
    zw = total[zone[inside]]
    placed = np.zeros(int(inside.sum()))
    np.divide(population[zone[inside]] * weight[inside], zw, out=placed, where=zw > 0)
    demand = np.zeros(len(weight))
    demand[inside] = placed
    return demand
