"""The noise grid kept in Silver: one layer per index on a shared grid, and how to read it.

Levels are stored as hundredths of a decibel in 16 bits (0 = no level in the cell), cropped to
the cells that carry a level: the source's 32-bit rasters are 184 MB each and mostly empty.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

GRID_FILE = "noise_grid.npz"
SCALE = 100  # stored value = decibels x 100
NO_LEVEL = 0
_LAYER_PREFIX = "layer_"


@dataclass(frozen=True)
class NoiseGrid:
    """`origin_x`, `origin_y` is the top-left corner; rows go south, columns east."""

    layers: dict[str, NDArray[np.uint16]]
    origin_x: float
    origin_y: float
    pixel_m: float
    reference_year: int

    @property
    def shape(self) -> tuple[int, int]:
        first = next(iter(self.layers.values()))
        return int(first.shape[0]), int(first.shape[1])

    def levels_at(
        self, layer: str, x: NDArray[np.float64], y: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Decibels of the cell each point lies in; NaN outside the grid or without a level."""
        cells = self.layers[layer]
        rows, cols = self.shape
        col = np.floor((x - self.origin_x) / self.pixel_m).astype(np.int64)
        row = np.floor((self.origin_y - y) / self.pixel_m).astype(np.int64)
        inside = (col >= 0) & (col < cols) & (row >= 0) & (row < rows)
        stored = np.zeros(len(x), dtype=np.uint16)
        stored[inside] = cells[row[inside], col[inside]]
        return np.where(stored == NO_LEVEL, np.nan, stored / SCALE)


def encode(levels_db: NDArray[np.float32], nodata: float) -> NDArray[np.uint16]:
    """Decibels -> stored hundredths. A real level below 0.01 dB keeps the smallest stored
    value, so it never reads as «no level»."""
    has_level = np.isfinite(levels_db) & (levels_db != nodata)
    hundredths = np.clip(np.rint(levels_db * SCALE), 1, np.iinfo(np.uint16).max)
    return np.where(has_level, hundredths, NO_LEVEL).astype(np.uint16)


def save_grid(grid: NoiseGrid, directory: Path) -> Path:
    path = directory / GRID_FILE
    arrays: dict[str, Any] = {
        "origin_x": grid.origin_x,
        "origin_y": grid.origin_y,
        "pixel_m": grid.pixel_m,
        "reference_year": grid.reference_year,
        **{f"{_LAYER_PREFIX}{name}": cells for name, cells in grid.layers.items()},
    }
    np.savez_compressed(path, **arrays)
    return path


def load_grid(path: Path) -> NoiseGrid:
    with np.load(path, allow_pickle=False) as data:
        layers = {
            key.removeprefix(_LAYER_PREFIX): data[key]
            for key in data.files
            if key.startswith(_LAYER_PREFIX)
        }
        return NoiseGrid(
            layers=layers,
            origin_x=float(data["origin_x"]),
            origin_y=float(data["origin_y"]),
            pixel_m=float(data["pixel_m"]),
            reference_year=int(data["reference_year"]),
        )
