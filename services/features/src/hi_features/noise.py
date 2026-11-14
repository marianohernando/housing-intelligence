"""Inputs of the street-noise features (D-237): the last valid noise grid of a dataset, read
once per process, and the level of each origin street node on it."""

from datetime import date
from functools import cache
from pathlib import Path

from sqlalchemy import Engine

from hi_features.loaders import silver_file
from hi_ingestion.pipelines.noise_raster.grid import GRID_FILE, NoiseGrid, load_grid


def grid_path(engine: Engine, dataset_id: str) -> Path:
    return silver_file(engine, dataset_id, GRID_FILE)


@cache
def grid(path: Path) -> NoiseGrid:
    return load_grid(path)


def reference_period(noise: NoiseGrid) -> date:
    """The map describes one year: its values are dated on that year's first day."""
    return date(noise.reference_year, 1, 1)
