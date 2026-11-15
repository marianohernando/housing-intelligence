"""Read the GeoTIFF of each declared index from the published ZIP, with its georeference."""

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from PIL import Image

from hi_contracts.catalog.pipeline import NoiseRasterPipeline

# GeoTIFF tags (OGC GeoTIFF 1.1) and the GeoKey that names a projected CRS by its EPSG code
PIXEL_SCALE_TAG = 33550
TIEPOINT_TAG = 33922
GEO_KEYS_TAG = 34735
PROJECTED_CRS_KEY = 3072
LAYERS_ATTR = "layers"
LAYER_COLUMNS = ["layer", "file", "rows", "columns", "crs", "pixel_m", "origin_x", "origin_y"]


@dataclass(frozen=True)
class RasterLayer:
    name: str
    file: str
    levels_db: NDArray[np.float32]
    crs: str | None
    pixel_m: float | None
    origin_x: float | None
    origin_y: float | None


def _projected_crs(geo_keys: tuple[int, ...] | None) -> str | None:
    """EPSG code of the projected CRS: the GeoKey directory is a header of 4 values and then
    (key, location, count, value) entries."""
    if not geo_keys:
        return None
    entries = [geo_keys[i : i + 4] for i in range(4, len(geo_keys), 4)]
    code = next((e[3] for e in entries if len(e) == 4 and e[0] == PROJECTED_CRS_KEY), None)
    return f"EPSG:{code}" if code else None


def read_layer(name: str, file: str, raw: bytes) -> RasterLayer:
    Image.MAX_IMAGE_PIXELS = None  # an official raster of a whole city, not an untrusted upload
    with Image.open(io.BytesIO(raw)) as image:
        tags = image.tag_v2  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        scale = tags.get(PIXEL_SCALE_TAG)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        tie = tags.get(TIEPOINT_TAG)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        geo_keys = tags.get(GEO_KEYS_TAG)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        levels = np.asarray(image, dtype=np.float32)
    square = scale is not None and float(scale[0]) == float(scale[1])  # pyright: ignore[reportUnknownArgumentType]
    # The tiepoint ties raster (0, 0) to a map coordinate: the top-left corner when it is there
    at_corner = tie is not None and float(tie[0]) == 0.0 and float(tie[1]) == 0.0  # pyright: ignore[reportUnknownArgumentType]
    return RasterLayer(
        name=name,
        file=file,
        levels_db=levels,
        crs=_projected_crs(tuple(int(k) for k in geo_keys) if geo_keys else None),  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        pixel_m=float(scale[0]) if square else None,  # pyright: ignore[reportUnknownArgumentType, reportOptionalSubscript]
        origin_x=float(tie[3]) if at_corner else None,  # pyright: ignore[reportUnknownArgumentType, reportOptionalSubscript]
        origin_y=float(tie[4]) if at_corner else None,  # pyright: ignore[reportUnknownArgumentType, reportOptionalSubscript]
    )


def parse_rasters(path: Path, spec: NoiseRasterPipeline) -> pd.DataFrame:
    """One row per layer found; the rasters travel in `attrs` for the normalisation. A declared
    file that is not in the ZIP has no row, and the quality gate fails on it."""
    layers: list[RasterLayer] = []
    with zipfile.ZipFile(path) as archive:
        members = {Path(m).name: m for m in archive.namelist()}
        for name, file in spec.layers.items():
            if file in members:
                layers.append(read_layer(name, file, archive.read(members[file])))
    frame = pd.DataFrame(
        [
            (
                layer.name,
                layer.file,
                *layer.levels_db.shape,
                layer.crs,
                layer.pixel_m,
                layer.origin_x,
                layer.origin_y,
            )
            for layer in layers
        ],
        columns=LAYER_COLUMNS,
    )
    frame.attrs[LAYERS_ATTR] = layers
    return frame
