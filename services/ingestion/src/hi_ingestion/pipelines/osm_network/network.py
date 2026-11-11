"""Way segments -> projected walking graph, plus Silver read/write."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

from hi_domain.access.graph import WalkNetwork, from_edges

NETWORK_FILE = "network.npz"
COORDINATES = ["u_lon", "u_lat", "v_lon", "v_lat"]
TO_25830 = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)


@dataclass(frozen=True)
class NetworkResult:
    network: WalkNetwork
    quarantine: pd.DataFrame


def normalize_segments(frame: pd.DataFrame) -> NetworkResult:
    missing = frame[COORDINATES].isna().any(axis=1)
    quarantine = frame.loc[missing].assign(reason="missing_node_location")
    ok = frame.loc[~missing]
    u_xy = TO_25830.transform(ok["u_lon"].to_numpy(float), ok["u_lat"].to_numpy(float))
    v_xy = TO_25830.transform(ok["v_lon"].to_numpy(float), ok["v_lat"].to_numpy(float))
    network = from_edges(
        ok["u_id"].to_numpy(np.int64),
        ok["v_id"].to_numpy(np.int64),
        (np.asarray(u_xy[0]), np.asarray(u_xy[1])),
        (np.asarray(v_xy[0]), np.asarray(v_xy[1])),
        ok["highway"].astype(str).tolist(),
    )
    return NetworkResult(network, quarantine)


def save_network(network: WalkNetwork, directory: Path) -> Path:
    path = directory / NETWORK_FILE
    np.savez_compressed(
        path,
        node_id=network.node_id,
        node_x=network.node_x,
        node_y=network.node_y,
        edge_u=network.edge_u,
        edge_v=network.edge_v,
        edge_length_m=network.edge_length_m,
        edge_highway=network.edge_highway,
        highways=np.array(network.highways),
    )
    return path


def load_network(path: Path) -> WalkNetwork:
    with np.load(path, allow_pickle=False) as data:
        return WalkNetwork(
            node_id=data["node_id"],
            node_x=data["node_x"],
            node_y=data["node_y"],
            edge_u=data["edge_u"],
            edge_v=data["edge_v"],
            edge_length_m=data["edge_length_m"],
            edge_highway=data["edge_highway"],
            highways=tuple(str(h) for h in data["highways"]),
        )
