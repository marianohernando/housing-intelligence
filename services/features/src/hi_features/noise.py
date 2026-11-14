"""Inputs of the street-noise features (D-237): the last valid noise grid of a dataset, read
once per process, and points along the streets where people live to read it at.

The map is read along each residential street segment, every `step_m` metres at most, never at
the street nodes alone: a node is a crossing, where two streets add up their traffic (review of
PR #65, R-03).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sqlalchemy import Engine

from hi_domain.access.graph import FloatArray, WalkNetwork
from hi_features.loaders import silver_file
from hi_ingestion.pipelines.noise_raster.grid import GRID_FILE, NoiseGrid, load_grid


@dataclass(frozen=True)
class StreetSamples:
    """Points along the residential streets: where, the street metres each stands for and the
    census section it lies in (that of the nearer end of its segment; '' outside every one)."""

    x: FloatArray
    y: FloatArray
    weight: FloatArray
    section: NDArray[np.str_]


def street_samples(
    network: WalkNetwork,
    origin_highways: Sequence[str],
    section_of_node: NDArray[np.str_],
    step_m: float,
    prefix: str = "",
) -> StreetSamples:
    """Each residential segment cut into equal pieces of `step_m` at most, sampled at their
    middle and weighted by their length, so a segment weighs its `edge_length_m` whatever its
    pieces. With `prefix`, only the segments with an end in a section under it."""
    codes = [i for i, name in enumerate(network.highways) if name in origin_highways]
    keep = np.isin(network.edge_highway, codes)
    if prefix:
        inside = np.char.startswith(section_of_node.astype(str), prefix)
        keep &= inside[network.edge_u] | inside[network.edge_v]
    u, v, length = network.edge_u[keep], network.edge_v[keep], network.edge_length_m[keep]
    pieces = np.maximum(1, np.ceil(length / step_m)).astype(np.int64)
    edge = np.repeat(np.arange(len(u)), pieces)
    first = np.repeat(np.cumsum(pieces) - pieces, pieces)
    t = (np.arange(int(pieces.sum())) - first + 0.5) / pieces[edge]
    x0, y0 = network.node_x[u][edge], network.node_y[u][edge]
    x1, y1 = network.node_x[v][edge], network.node_y[v][edge]
    section = np.where(t < 0.5, section_of_node[u][edge], section_of_node[v][edge])
    return StreetSamples(
        x=x0 + t * (x1 - x0),
        y=y0 + t * (y1 - y0),
        weight=(length / pieces)[edge],
        section=section,
    )


def grid_path(engine: Engine, dataset_id: str) -> Path:
    return silver_file(engine, dataset_id, GRID_FILE)


@cache
def grid(path: Path) -> NoiseGrid:
    return load_grid(path)


def reference_period(noise: NoiseGrid) -> date:
    """The map describes one year: its values are dated on that year's first day."""
    return date(noise.reference_year, 1, 1)
