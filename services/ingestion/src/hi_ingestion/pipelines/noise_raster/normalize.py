"""Rasters of one map -> the grid kept in Silver, cropped to the cells that carry a level."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from hi_contracts.catalog.pipeline import NoiseRasterPipeline
from hi_ingestion.pipelines.noise_raster.grid import NO_LEVEL, SCALE, NoiseGrid, encode
from hi_ingestion.pipelines.noise_raster.parse import LAYERS_ATTR, RasterLayer

PROBLEM_COLUMNS = ["layer", "reason"]


@dataclass(frozen=True)
class NoiseResult:
    """`grid` is None when the layers cannot share one grid; `problems` says why."""

    grid: NoiseGrid | None
    problems: pd.DataFrame
    found: list[str]
    max_db: dict[str, float]

    def cells_with_level(self) -> dict[str, int]:
        if self.grid is None:
            return {}
        return {name: int((cells != NO_LEVEL).sum()) for name, cells in self.grid.layers.items()}


def _problems(layers: list[RasterLayer], spec: NoiseRasterPipeline) -> list[tuple[str, str]]:
    found = {layer.name for layer in layers}
    problems = [(name, f"{file} is not in the ZIP") for name, file in spec.layers.items()
                if name not in found]  # fmt: skip
    first = layers[0] if layers else None
    for layer in layers:
        if layer.crs != spec.crs:
            problems.append((layer.name, f"CRS {layer.crs}, expected {spec.crs}"))
        if layer.pixel_m != spec.pixel_m:
            problems.append((layer.name, f"pixel of {layer.pixel_m} m, expected {spec.pixel_m}"))
        if layer.origin_x is None or layer.origin_y is None:
            problems.append((layer.name, "no top-left tiepoint"))
        elif first is not None and (
            layer.levels_db.shape != first.levels_db.shape
            or (layer.origin_x, layer.origin_y) != (first.origin_x, first.origin_y)
        ):
            problems.append((layer.name, "not on the grid of the first layer"))
    return problems


def _crop(layers: dict[str, np.ndarray]) -> tuple[slice, slice]:
    """Rows and columns that hold a level in some layer."""
    any_level = np.zeros(next(iter(layers.values())).shape, dtype=bool)
    for cells in layers.values():
        any_level |= cells != NO_LEVEL
    rows, cols = np.flatnonzero(any_level.any(axis=1)), np.flatnonzero(any_level.any(axis=0))
    if len(rows) == 0:
        return slice(0, 0), slice(0, 0)
    return slice(int(rows[0]), int(rows[-1]) + 1), slice(int(cols[0]), int(cols[-1]) + 1)


def normalize_rasters(frame: pd.DataFrame, spec: NoiseRasterPipeline) -> NoiseResult:
    layers: list[RasterLayer] = frame.attrs.get(LAYERS_ATTR, [])
    problems = pd.DataFrame(_problems(layers, spec), columns=PROBLEM_COLUMNS)
    found = [layer.name for layer in layers]
    if len(problems) or not layers:
        return NoiseResult(None, problems, found, {})
    encoded = {layer.name: encode(layer.levels_db, spec.nodata) for layer in layers}
    rows, cols = _crop(encoded)
    first = layers[0]
    assert first.origin_x is not None and first.origin_y is not None  # noqa: S101 - checked above
    grid = NoiseGrid(
        layers={name: np.ascontiguousarray(cells[rows, cols]) for name, cells in encoded.items()},
        origin_x=first.origin_x + cols.start * spec.pixel_m,
        origin_y=first.origin_y - rows.start * spec.pixel_m,
        pixel_m=spec.pixel_m,
        reference_year=spec.reference_year,
    )
    max_db = {name: float(cells.max()) / SCALE for name, cells in grid.layers.items()}
    return NoiseResult(grid, problems, found, max_db)
