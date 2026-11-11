"""Undirected walking graph held as arrays; scipy turns it into a sparse adjacency matrix."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class WalkNetwork:
    """Nodes in projected metres (EPSG:25830) and undirected edges with their length."""

    node_id: IntArray  # source identifier (OSM node id), kept for traceability
    node_x: FloatArray
    node_y: FloatArray
    edge_u: IntArray  # node index
    edge_v: IntArray
    edge_length_m: FloatArray
    edge_highway: IntArray  # index into `highways`
    highways: tuple[str, ...]

    @property
    def n_nodes(self) -> int:
        return len(self.node_x)

    @property
    def n_edges(self) -> int:
        return len(self.edge_u)

    @property
    def total_km(self) -> float:
        return float(self.edge_length_m.sum()) / 1000

    def adjacency(self) -> csr_matrix:
        """Symmetric matrix of edge lengths; parallel edges keep the shortest."""
        rows = np.concatenate([self.edge_u, self.edge_v])
        cols = np.concatenate([self.edge_v, self.edge_u])
        weights = np.concatenate([self.edge_length_m, self.edge_length_m])
        order = np.lexsort((weights, cols, rows))
        rows, cols, weights = rows[order], cols[order], weights[order]
        first = np.ones(len(rows), dtype=bool)
        first[1:] = (rows[1:] != rows[:-1]) | (cols[1:] != cols[:-1])
        shape = (self.n_nodes, self.n_nodes)
        return csr_matrix((weights[first], (rows[first], cols[first])), shape=shape)

    def km_by_highway(self) -> dict[str, float]:
        totals = np.bincount(
            self.edge_highway, weights=self.edge_length_m, minlength=len(self.highways)
        )
        return {
            name: round(float(m) / 1000, 1) for name, m in zip(self.highways, totals, strict=True)
        }

    def main_component_share(self) -> float:
        """Share of street length inside the largest connected piece of the network."""
        if self.n_edges == 0:
            return 0.0
        _, labels = connected_components(self.adjacency(), directed=False)
        per_component = np.bincount(labels[self.edge_u], weights=self.edge_length_m)
        return float(per_component.max() / per_component.sum())


def from_edges(
    u_id: IntArray,
    v_id: IntArray,
    u_xy: tuple[FloatArray, FloatArray],
    v_xy: tuple[FloatArray, FloatArray],
    highway: list[str],
) -> WalkNetwork:
    """Build the network from one row per way segment: end ids and projected end coordinates.

    Self-loops are dropped and a segment shared by two ways is kept once.
    """
    ids, inverse = np.unique(np.concatenate([u_id, v_id]), return_inverse=True)
    n = len(u_id)
    u, v = inverse[:n].astype(np.int64), inverse[n:].astype(np.int64)
    node_x = np.zeros(len(ids))
    node_y = np.zeros(len(ids))
    node_x[u], node_y[u] = u_xy
    node_x[v], node_y[v] = v_xy
    low, high = np.minimum(u, v), np.maximum(u, v)
    keep = low != high
    _, first = np.unique(np.stack([low[keep], high[keep]]), axis=1, return_index=True)
    rows = np.flatnonzero(keep)[np.sort(first)]
    lengths = np.hypot(node_x[u[rows]] - node_x[v[rows]], node_y[u[rows]] - node_y[v[rows]])
    kept_highway = np.array(highway)[rows]
    highways = tuple(sorted(set(kept_highway.tolist())))
    codes = np.searchsorted(np.array(highways), kept_highway).astype(np.int64)
    return WalkNetwork(
        node_id=ids.astype(np.int64),
        node_x=node_x,
        node_y=node_y,
        edge_u=u[rows],
        edge_v=v[rows],
        edge_length_m=lengths,
        edge_highway=codes,
        highways=highways,
    )
