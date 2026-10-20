"""Raw census sections -> canonical admin units (section, barrio, district, municipality)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import geopandas as gpd
import pandas as pd

from hi_contracts.catalog.enums import AdminLevel
from hi_domain.geo.codes import admin_unit_id, barrio_from_cm_csv, barrio_from_shp, parse_gseccion
from hi_domain.geo.geometry import to_multipolygon
from hi_ingestion.pipelines.admin_boundaries.config import SOURCE_CRS, WGS84

CSV_ENCODINGS = ("utf-8", "latin-1")
UNIT_COLUMNS = [
    "admin_unit_id",
    "level",
    "code_official",
    "code_source",
    "name",
    "parent_admin_unit_id",
]


@dataclass(frozen=True)
class AdminUnits:
    units: gpd.GeoDataFrame  # UNIT_COLUMNS + geometry in SOURCE_CRS
    quarantine: pd.DataFrame  # source_row, code, reason
    source_crs: str
    source_rows: int


def read_sections(path: Path | str) -> gpd.GeoDataFrame:
    return gpd.read_file(path)


def read_csv(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in CSV_ENCODINGS:
        try:
            frame = pd.read_csv(path, sep=";", dtype=str, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        for column in frame.columns:
            frame[column] = frame[column].str.strip()
        return frame
    msg = f"Cannot decode {path}"
    raise ValueError(msg) from last_error


def read_names(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Section CSV -> (municipio INE 5d -> name, district INE 7d -> name for Madrid)."""
    frame = read_csv(path)
    munis = {
        f"28{m}": n
        for m, n in zip(frame["municipio_codigo"], frame["municipio_nombre"], strict=True)
    }
    named = frame.dropna(subset=["distrito_nombre"])
    districts = {
        f"28{d}": n for d, n in zip(named["distrito_codigo"], named["distrito_nombre"], strict=True)
    }
    return munis, districts


def read_barrio_names(path: Path) -> dict[str, str]:
    frame = read_csv(path)
    return {
        barrio_from_cm_csv(c): n
        for c, n in zip(frame["barrio_codigo"], frame["barrio_nombre"], strict=True)
    }


def _normalize_row(row: Any) -> dict[str, Any]:
    municipio, distrito, seccion = parse_gseccion(str(row.CDGSECCION))
    barrio = barrio_from_shp(row.CDTBARRIO if isinstance(row.CDTBARRIO, str) else None, municipio)
    geometry = to_multipolygon(row.geometry)
    if geometry is None:
        msg = "empty or non-polygonal geometry"
        raise ValueError(msg)
    return {
        "seccion": seccion,
        "distrito": distrito,
        "municipio": municipio,
        "barrio": barrio,
        "code_source": str(row.CDGSECCION),
        "declared_area_km2": float(row.Area_k2),
        "geometry": geometry,
    }


def normalize_sections(raw: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    for index, row in enumerate(raw.itertuples(index=False)):
        try:
            rows.append(_normalize_row(row))
        except (ValueError, TypeError) as exc:
            bad.append(
                {"source_row": index, "code": getattr(row, "CDGSECCION", None), "reason": str(exc)}
            )
    sections = gpd.GeoDataFrame(rows, geometry="geometry", crs=raw.crs)
    return sections, pd.DataFrame(bad, columns=["source_row", "code", "reason"])


def _dissolve(sections: gpd.GeoDataFrame, key: str) -> gpd.GeoDataFrame:
    dissolved = sections[[key, "geometry"]].dissolve(by=key, as_index=False)
    dissolved["geometry"] = dissolved.geometry.map(to_multipolygon)
    return dissolved


def _units(frame: gpd.GeoDataFrame, key: str, level: AdminLevel, **cols: Any) -> gpd.GeoDataFrame:
    out = gpd.GeoDataFrame(
        {
            "admin_unit_id": [admin_unit_id(level.value, c) for c in frame[key]],
            "level": level.value,
            "code_official": frame[key].to_numpy(),
            "code_source": cols.get("code_source"),
            "name": cols.get("name"),
            "parent_admin_unit_id": cols.get("parent"),
        },
        geometry=frame.geometry.to_numpy(),
        crs=frame.crs,
    )
    return cast(gpd.GeoDataFrame, out[[*UNIT_COLUMNS, "geometry"]])


def build_admin_units(
    raw: gpd.GeoDataFrame,
    municipio_names: dict[str, str],
    district_names: dict[str, str],
    barrio_names: dict[str, str],
) -> AdminUnits:
    sections, quarantine = normalize_sections(raw)
    munis = _dissolve(sections, "municipio")
    dists = _dissolve(sections, "distrito")
    barrios = _dissolve(cast(gpd.GeoDataFrame, sections[sections["barrio"].notna()]), "barrio")

    def dist_name(code: str) -> str:
        muni = municipio_names.get(code[:5], code[:5])
        return district_names.get(code, f"{muni} — distrito censal {code[5:]}")

    frames = [
        _units(
            munis,
            "municipio",
            AdminLevel.MUNICIPIO,
            name=munis["municipio"].map(lambda c: municipio_names.get(c)),
        ),
        _units(
            dists,
            "distrito",
            AdminLevel.DISTRITO,
            name=dists["distrito"].map(dist_name),
            parent=dists["distrito"].map(lambda c: admin_unit_id("municipio", c[:5])),
        ),
        _units(
            barrios,
            "barrio",
            AdminLevel.BARRIO,
            name=barrios["barrio"].map(lambda c: barrio_names.get(c)),
            parent=barrios["barrio"].map(lambda c: admin_unit_id("distrito", c[:7])),
        ),
        _units(
            sections,
            "seccion",
            AdminLevel.SECCION_CENSAL,
            code_source=sections["code_source"],
            parent=[
                admin_unit_id("barrio", b) if isinstance(b, str) else admin_unit_id("distrito", d)
                for b, d in zip(sections["barrio"], sections["distrito"], strict=True)
            ],
        ),
    ]
    units = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=raw.crs)
    declared: dict[str, float] = {
        admin_unit_id("seccion_censal", c): a
        for c, a in zip(sections["seccion"], sections["declared_area_km2"], strict=True)
    }
    units["declared_area_km2"] = units["admin_unit_id"].map(lambda u: declared.get(u))
    return AdminUnits(units, quarantine, str(raw.crs.to_string() if raw.crs else ""), len(raw))


def expected_crs_ok(raw_crs: str) -> bool:
    return raw_crs.upper() == SOURCE_CRS


def to_wgs84(units: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to EPSG:4326 and repair: reprojection can create ring self-intersections."""
    out = units.to_crs(WGS84)
    out["geometry"] = out.geometry.map(to_multipolygon)
    return out
