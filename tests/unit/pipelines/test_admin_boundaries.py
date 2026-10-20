"""Admin boundaries transform/QA/H3 on the real fixture, without a database."""

import hashlib
from pathlib import Path

import pytest

from hi_ingestion.pipelines.admin_boundaries.h3map import build_h3_mapping
from hi_ingestion.pipelines.admin_boundaries.quality import run_quality
from hi_ingestion.pipelines.admin_boundaries.run import load_zones
from hi_ingestion.pipelines.admin_boundaries.transform import (
    AdminUnits,
    build_admin_units,
    read_barrio_names,
    read_names,
    read_sections,
    to_wgs84,
)

FIXTURE = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "admin_sample"


def _build() -> AdminUnits:
    return build_admin_units(
        read_sections(FIXTURE / "sections.gpkg"),
        *read_names(FIXTURE / "names.csv"),
        read_barrio_names(FIXTURE / "barrios.csv"),
    )


@pytest.fixture(scope="module")
def admin() -> AdminUnits:
    return _build()


def test_levels_and_hierarchy(admin: AdminUnits) -> None:
    units = admin.units
    assert set(units["level"]) == {"municipio", "distrito", "barrio", "seccion_censal"}
    ids = set(units["admin_unit_id"])
    parents = units.loc[units["parent_admin_unit_id"].notna(), "parent_admin_unit_id"]
    assert set(parents) <= ids
    assert units.loc[units["level"] == "municipio", "parent_admin_unit_id"].isna().all()
    assert set(units.loc[units["level"] == "municipio", "name"]) >= {"MADRID", "AJALVIR"}


def test_quality_passes_on_real_fixture(admin: AdminUnits) -> None:
    report = run_quality(admin, load_zones())
    failed = [c.name for c in report.checks if c.critical and not c.passed]
    assert report.passed, failed
    assert {g["zone_id"] for g in report.golden} == {"sol", "chamartin_plaza_castilla"}


def test_transform_is_deterministic() -> None:
    def digest(a: AdminUnits) -> str:
        rows = sorted(zip(a.units["admin_unit_id"], a.units.geometry.to_wkb(), strict=True))
        return hashlib.sha256(b"".join(i.encode() + w for i, w in rows)).hexdigest()

    assert digest(_build()) == digest(_build())


def test_wgs84_output_is_valid(admin: AdminUnits) -> None:
    units_4326 = to_wgs84(admin.units)
    assert units_4326.is_valid.all()
    assert str(units_4326.crs) == "EPSG:4326"


def test_h3_invariants(admin: AdminUnits) -> None:
    mapping = build_h3_mapping(admin.units)
    links = mapping.links
    shares: list[float] = links.loc[links["method"] == "overlap", "overlap_share"].tolist()
    assert all(0 < s <= 1 for s in shares)
    per_cell: dict[str, float] = {}
    for cell, unit, method, share in links.itertuples(index=False, name=None):
        del unit
        if method == "overlap":
            per_cell[cell] = per_cell.get(cell, 0.0) + share
    assert max(per_cell.values()) <= 1 + 1e-6
    sections = set(admin.units.loc[admin.units["level"] == "seccion_censal", "admin_unit_id"])
    overlap_units = set(links.loc[links["method"] == "overlap", "admin_unit_id"])
    assert sections <= overlap_units
    level_of = dict(zip(admin.units["admin_unit_id"], admin.units["level"], strict=True))
    centroid_units = set(links.loc[links["method"] == "centroid", "admin_unit_id"])
    assert {level_of[u] for u in centroid_units} == {
        "municipio", "distrito", "barrio", "seccion_censal"
    }  # fmt: skip


def test_quarantine_catches_unparseable_codes(admin: AdminUnits) -> None:
    raw = read_sections(FIXTURE / "sections.gpkg")
    raw.loc[raw.index[0], "CDGSECCION"] = "garbage"
    broken = build_admin_units(
        raw, *read_names(FIXTURE / "names.csv"), read_barrio_names(FIXTURE / "barrios.csv")
    )
    assert len(broken.quarantine) == 1
    assert broken.quarantine.iloc[0]["reason"].startswith("Unparseable")
    assert len(broken.units) < len(admin.units) + 1
