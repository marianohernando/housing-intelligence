"""Geospatial QA (docs/02_data/41_geospatial_qa_spec.md). Critical failures block Silver."""

from dataclasses import asdict, dataclass, field
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from hi_domain.geo.bounds import COMUNIDAD_MADRID_BBOX, BBox, looks_lat_lon_swapped
from hi_ingestion.pipelines.admin_boundaries import config
from hi_ingestion.pipelines.admin_boundaries.transform import AdminUnits, expected_crs_ok, to_wgs84


@dataclass(frozen=True)
class CheckResult:
    name: str
    critical: bool
    passed: bool
    details: dict[str, Any] = field(default_factory=dict[str, Any])


@dataclass
class QualityReport:
    checks: list[CheckResult]
    golden: list[dict[str, Any]]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.critical)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [asdict(c) for c in self.checks],
            "golden_points": self.golden,
        }


def _level(units: gpd.GeoDataFrame, level: str) -> gpd.GeoDataFrame:
    return units[units["level"] == level]  # pyright: ignore[reportReturnType]


def _bounds_check(units_4326: gpd.GeoDataFrame) -> CheckResult:
    minx, miny, maxx, maxy = units_4326.total_bounds
    bbox = BBox(float(minx), float(miny), float(maxx), float(maxy))
    centroid = units_4326.union_all().centroid
    return CheckResult(
        "within_madrid_bounds_and_not_swapped",
        critical=True,
        passed=COMUNIDAD_MADRID_BBOX.contains_bbox(bbox)
        and not looks_lat_lon_swapped(centroid.x, centroid.y),
        details={"total_bounds_4326": [round(v, 5) for v in (minx, miny, maxx, maxy)]},
    )


def _area_check(sections: gpd.GeoDataFrame) -> CheckResult:
    computed = sections.geometry.area / 1e6
    declared = sections["declared_area_km2"].astype(float)
    rel = ((computed - declared).abs() / declared.where(declared > 0)).fillna(0)
    off = sections.loc[rel > config.AREA_TOLERANCE, "code_official"].tolist()
    share_ok = 1 - len(off) / max(len(sections), 1)
    return CheckResult(
        "area_matches_declared_within_1pct",
        critical=False,
        passed=share_ok >= 0.99,
        details={"share_ok": round(share_ok, 5), "outliers_sample": off[:10], "outliers": len(off)},
    )


def _containment_check(units: gpd.GeoDataFrame) -> CheckResult:
    """Each child's representative point lies inside its parent (1 m tolerance)."""
    geoms = dict(zip(units["admin_unit_id"], units.geometry, strict=True))
    children = units[units["parent_admin_unit_id"].notna()]
    failures: list[str] = []
    for child_id, parent_id, geom in zip(
        children["admin_unit_id"], children["parent_admin_unit_id"], children.geometry, strict=True
    ):
        parent = geoms.get(parent_id)
        if parent is None or not parent.buffer(1.0).contains(geom.representative_point()):
            failures.append(child_id)
    return CheckResult(
        "child_inside_parent",
        critical=True,
        passed=not failures,
        details={"checked": len(children), "failures": failures[:20]},
    )


def _coverage_check(units: gpd.GeoDataFrame) -> CheckResult:
    sections = _level(units, "seccion_censal")
    munis = _level(units, "municipio")
    ratio = float(sections.geometry.area.sum() / munis.geometry.area.sum())
    return CheckResult(
        "sections_cover_municipalities",
        critical=False,
        passed=abs(1 - ratio) <= config.AREA_TOLERANCE,
        details={"sections_over_municipios_area": round(ratio, 6)},
    )


def _expected_counts(units: gpd.GeoDataFrame, source_rows: int) -> CheckResult:
    counts = units.groupby("level").size().to_dict()
    madrid = units["admin_unit_id"].str.contains(f".{config.MADRID_MUNICIPIO}")
    observed = {
        "municipio": int(counts.get("municipio", 0)),
        "madrid_distritos": int(((units["level"] == "distrito") & madrid).sum()),
        "madrid_barrios": int(((units["level"] == "barrio") & madrid).sum()),
    }
    full = source_rows >= config.FULL_RUN_MIN_SECTIONS
    expected = {
        "municipio": config.EXPECTED_MUNICIPIOS,
        "madrid_distritos": config.EXPECTED_MADRID_DISTRICTS,
        "madrid_barrios": config.EXPECTED_MADRID_BARRIOS,
    }
    return CheckResult(
        "expected_region_counts",
        critical=full,
        passed=(observed == expected) if full else True,
        details={"observed": observed, "expected": expected, "enforced": full, "by_level": counts},
    )


def golden_points(
    units_4326: gpd.GeoDataFrame, zones: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    present = set(_level(units_4326, "municipio")["code_official"])
    out: list[dict[str, Any]] = []
    for zone in zones:
        if zone["municipio_ine"] not in present:
            continue
        point = Point(zone["lon"], zone["lat"])
        hits = units_4326[units_4326.geometry.contains(point)]
        by_level = dict(zip(hits["level"], hits["code_official"], strict=True))
        out.append(
            {
                "zone_id": zone["zone_id"],
                "expected_municipio": zone["municipio_ine"],
                **{f"resolved_{k}": v for k, v in sorted(by_level.items())},
                "ok": by_level.get("municipio") == zone["municipio_ine"]
                and "seccion_censal" in by_level,
            }
        )
    return out


def run_quality(admin: AdminUnits, zones: list[dict[str, Any]]) -> QualityReport:
    units = admin.units
    units_4326 = to_wgs84(units)
    sections = _level(units, "seccion_censal")
    duplicated = units["admin_unit_id"].duplicated()
    golden = golden_points(units_4326, zones)
    quarantine_ratio = len(admin.quarantine) / max(admin.source_rows, 1)
    barrios = _level(units, "barrio")
    checks = [
        CheckResult(
            "source_crs_is_epsg_25830",
            True,
            expected_crs_ok(admin.source_crs),
            {"crs": admin.source_crs},
        ),
        CheckResult(
            "quarantine_ratio",
            True,
            quarantine_ratio <= config.MAX_QUARANTINE_RATIO,
            {"quarantined": len(admin.quarantine), "ratio": round(quarantine_ratio, 5)},
        ),
        CheckResult(
            "unique_admin_unit_ids",
            True,
            not bool(duplicated.any()),
            {"duplicates": units.loc[duplicated, "admin_unit_id"].tolist()[:20]},
        ),
        CheckResult(
            "geometries_valid",
            True,
            bool(units.is_valid.all()),
            {"invalid": int((~units.is_valid).sum())},
        ),
        CheckResult(
            "geometries_valid_epsg_4326",
            True,
            bool(units_4326.geometry.notna().all() and units_4326.is_valid.all()),
            {
                "invalid": int((~units_4326.is_valid).sum()),
                "empty": int(units_4326.geometry.isna().sum()),
            },
        ),
        CheckResult("area_positive", True, bool((units.geometry.area > 0).all()), {}),
        _bounds_check(units_4326),
        _containment_check(units),
        _area_check(sections),
        _coverage_check(units),
        _expected_counts(units, admin.source_rows),
        CheckResult(
            "golden_points_resolve", True, all(g["ok"] for g in golden), {"evaluated": len(golden)}
        ),
        CheckResult(
            "barrio_names_present",
            False,
            bool(barrios["name"].notna().all()),
            {"missing": barrios.loc[barrios["name"].isna(), "code_official"].tolist()},
        ),
    ]
    return QualityReport(checks, golden)


def row_counts(units: gpd.GeoDataFrame) -> dict[str, int]:
    return {
        str(k): int(v) for k, v in pd.Series(units["level"]).value_counts().sort_index().items()
    }
