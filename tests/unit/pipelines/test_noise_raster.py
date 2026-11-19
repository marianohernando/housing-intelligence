"""The strategic noise map (D-237): GeoTIFF layers -> one compact grid, read at a point."""

import io
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from PIL import Image
from PIL.TiffImagePlugin import ImageFileDirectory_v2

from hi_contracts.catalog.pipeline import NoiseRasterPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.noise_raster.grid import load_grid, save_grid
from hi_ingestion.pipelines.noise_raster.normalize import normalize_rasters
from hi_ingestion.pipelines.noise_raster.parse import parse_rasters
from hi_ingestion.pipelines.noise_raster.quality import run_noise_quality

ORIGIN = (440000.0, 4475000.0)  # top-left corner, EPSG:25830
# 4 rows x 5 columns of 5 m; the first row and the first column carry no level (0)
DAY = np.array(
    [
        [0, 0, 0, 0, 0],
        [0, 64.99, 65.0, 65.01, 70.0],
        [0, 50.0, 0, 66.6, 0],
        [0, -3.2, 55.5, 60.0, 0.001],
    ],
    dtype=np.float32,
)
NIGHT = np.where(DAY == 0, 0, DAY - 8).astype(np.float32)


def _tiff(levels: np.ndarray, *, epsg: int = 25830, pixel: float = 5.0) -> bytes:
    tags = ImageFileDirectory_v2()
    tags[33550] = (pixel, pixel, 0.0)
    tags[33922] = (0.0, 0.0, 0.0, ORIGIN[0], ORIGIN[1], 0.0)
    tags[34735] = (1, 1, 0, 2, 1024, 0, 1, 1, 3072, 0, 1, epsg)
    buffer = io.BytesIO()
    Image.fromarray(levels).save(buffer, format="TIFF", tiffinfo=tags)
    return buffer.getvalue()


def _zip(path: Path, files: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, raw in files.items():
            archive.writestr(f"MER/{name}", raw)
    return path


def _spec(**overrides: Any) -> NoiseRasterPipeline:
    data: dict[str, Any] = {
        "kind": "noise_raster",
        "dataset_id": "ayto_mapa_estrategico_ruido_2021",
        "layers": {"day": "day.tif", "night": "night.tif"},
        "crs": "EPSG:25830",
        "pixel_m": 5.0,
        "reference_year": 2021,
        "min_cells_with_level": 5,
    }
    return NoiseRasterPipeline.model_validate(data | overrides)


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    return _zip(tmp_path / "map.zip", {"day.tif": _tiff(DAY), "night.tif": _tiff(NIGHT)})


def test_layers_become_one_grid_cropped_to_its_levels(archive: Path) -> None:
    spec = _spec()
    result = normalize_rasters(parse_rasters(archive, spec), spec)
    assert run_noise_quality(result, spec).passed
    grid = result.grid
    assert grid is not None
    assert grid.shape == (3, 4)  # the empty first row and column are gone
    assert (grid.origin_x, grid.origin_y) == (ORIGIN[0] + 5, ORIGIN[1] - 5)
    assert result.cells_with_level() == {"day": 10, "night": 10}


def test_a_point_reads_the_level_of_its_cell(archive: Path, tmp_path: Path) -> None:
    spec = _spec()
    result = normalize_rasters(parse_rasters(archive, spec), spec)
    assert result.grid is not None
    grid = load_grid(save_grid(result.grid, tmp_path))
    assert grid.reference_year == 2021
    # centres of the cells of the second source row (y from 4474995 to 4474990), columns 1 to 4
    x = ORIGIN[0] + np.array([7.5, 12.5, 17.5, 22.5])
    y = np.full(4, ORIGIN[1] - 7.5)
    assert grid.levels_at("day", x, y).tolist() == [64.99, 65.0, 65.01, 70.0]
    assert grid.levels_at("night", x, y).tolist() == [56.99, 57.0, 57.01, 62.0]


def test_no_level_and_outside_the_map_are_unknown_never_zero(archive: Path) -> None:
    spec = _spec()
    grid = normalize_rasters(parse_rasters(archive, spec), spec).grid
    assert grid is not None
    x = np.array([ORIGIN[0] + 12.5, ORIGIN[0] + 2.5, ORIGIN[0] - 100.0, ORIGIN[0] + 7.5])
    y = np.array([ORIGIN[1] - 12.5, ORIGIN[1] - 12.5, ORIGIN[1] - 12.5, ORIGIN[1] + 100.0])
    assert np.isnan(grid.levels_at("day", x, y)).all()


def test_a_real_level_near_zero_is_kept_as_a_level(archive: Path) -> None:
    """The model gives levels below 0 dB far from every road: they are levels, not «no data»."""
    spec = _spec()
    grid = normalize_rasters(parse_rasters(archive, spec), spec).grid
    assert grid is not None
    x = ORIGIN[0] + np.array([7.5, 22.5])
    y = np.full(2, ORIGIN[1] - 17.5)
    assert grid.levels_at("day", x, y).tolist() == [0.01, 0.01]


def test_a_missing_layer_fails_the_quality_gate(tmp_path: Path) -> None:
    spec = _spec()
    only_day = _zip(tmp_path / "day.zip", {"day.tif": _tiff(DAY)})
    result = normalize_rasters(parse_rasters(only_day, spec), spec)
    report = run_noise_quality(result, spec).to_dict()
    assert not report["passed"]
    failed = {c["name"] for c in report["checks"] if not c["passed"]}
    assert "every_layer_found" in failed
    assert list(result.problems["layer"]) == ["night"]


@pytest.mark.parametrize(
    ("night", "reason"),
    [
        (_tiff(NIGHT, epsg=4326), "CRS EPSG:4326"),
        (_tiff(NIGHT, pixel=10.0), "pixel of 10.0 m"),
        (_tiff(NIGHT[:, :4]), "not on the grid"),
    ],
)
def test_layers_off_the_declared_grid_fail(tmp_path: Path, night: bytes, reason: str) -> None:
    spec = _spec()
    archive = _zip(tmp_path / "bad.zip", {"day.tif": _tiff(DAY), "night.tif": night})
    result = normalize_rasters(parse_rasters(archive, spec), spec)
    assert result.grid is None
    assert not run_noise_quality(result, spec).passed
    assert any(reason in r for r in result.problems["reason"])


def test_levels_that_are_not_decibels_or_an_empty_map_fail(archive: Path) -> None:
    for spec in (_spec(max_db=60.0), _spec(min_cells_with_level=11)):
        result = normalize_rasters(parse_rasters(archive, spec), spec)
        assert not run_noise_quality(result, spec).passed


def test_the_madrid_map_keeps_day_and_night() -> None:
    catalog = load_catalog()
    spec = catalog.pipelines["ayto_mapa_estrategico_ruido_2021"]
    assert isinstance(spec, NoiseRasterPipeline)
    assert spec.layers == {"ld": "Madrid_Ld_2021.tif", "ln": "Madrid_Ln_2021.tif"}  # R-02
    assert (spec.crs, spec.pixel_m, spec.reference_year) == ("EPSG:25830", 5.0, 2021)
    dataset = catalog.datasets[spec.dataset_id]
    assert catalog.sources[dataset.source_id].license_status.value == "CLEAR"
    assert "CC BY 4.0" in (catalog.sources[dataset.source_id].attribution_text or "")
