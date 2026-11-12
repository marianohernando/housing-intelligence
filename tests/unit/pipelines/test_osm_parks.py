"""OSM parks (DATA-018, D-222) on a hand-built extract: which areas are parks, their size and the
edge points where a walk reaches them."""

from pathlib import Path

import pytest
import shapely

from hi_contracts.catalog.pipeline import OsmParksPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.osm_parks.parks import EDGE_POINTS, normalize_parks
from hi_ingestion.pipelines.osm_parks.parse import parse_parks
from hi_ingestion.pipelines.osm_parks.quality import run_parks_quality

LAT, LON = 40.4168, -3.7038
M_LAT, M_LON = 1 / 111_000, 1 / 84_600  # degrees per metre near Madrid


def _rectangle(first_id: int, east_m: float, north_m: float, x0_m: float) -> dict[int, tuple]:
    corners = [(0, 0), (east_m, 0), (east_m, north_m), (0, north_m)]
    return {
        first_id + i: (LAT + n * M_LAT, LON + (x0_m + e) * M_LON)
        for i, (e, n) in enumerate(corners)
    }


def _way(way_id: int, refs: list[int], **tags: str) -> str:
    nodes = "".join(f'<nd ref="{ref}"/>' for ref in refs)
    tag_xml = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items())
    return f'  <way id="{way_id}">{nodes}{tag_xml}</way>'


def _closed(first_id: int) -> list[int]:
    return [first_id, first_id + 1, first_id + 2, first_id + 3, first_id]


NODES = {
    **_rectangle(1, 120, 100, 0),  # 1.2 ha: a park
    **_rectangle(11, 200, 100, 500),  # 2 ha, private
    **_rectangle(21, 60, 50, 1000),  # 0.3 ha: too small
    **_rectangle(31, 200, 100, 1500),  # 2 ha garden: not a park
    **_rectangle(41, 150, 100, 2000),  # 1.5 ha: multipolygon park without a name
}
EXTRACT = "\n".join(
    [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<osm version="0.6" generator="test">',
        *(f'  <node id="{i}" lat="{lat}" lon="{lon}"/>' for i, (lat, lon) in NODES.items()),
        _way(100, _closed(1), leisure="park", name="Parque Uno"),
        _way(101, _closed(11), leisure="park", access="private", name="Jardín privado"),
        _way(102, _closed(21), leisure="park", name="Placita"),
        _way(103, _closed(31), leisure="garden", name="Huerto"),
        _way(104, _closed(41)),
        '  <relation id="500"><member type="way" ref="104" role="outer"/>'
        '<tag k="type" v="multipolygon"/><tag k="leisure" v="park"/></relation>',
        "</osm>",
    ]
)
SPEC = OsmParksPipeline(
    kind="osm_parks", dataset_id="osm_parques", min_area_ha=1.0, min_parks=1, max_parks=10
)


@pytest.fixture(scope="module")
def extract(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("osm") / "parks.osm"
    path.write_text(EXTRACT)
    return path


def test_only_areas_with_a_park_tag_are_read(extract: Path) -> None:
    frame = parse_parks(extract, SPEC)
    assert sorted(frame["external_id"]) == ["relation/500", "way/100", "way/101", "way/102"]


def test_parks_closed_to_the_public_or_too_small_are_left_out(extract: Path) -> None:
    places = normalize_parks(parse_parks(extract, SPEC), SPEC)
    assert sorted(places.frame["external_id"]) == ["relation/500", "way/100"]
    assert places.filtered_out == {"access_denied": 1, "smaller_than_min_area": 1}
    assert places.quarantine.empty


def test_a_park_is_a_green_place_with_its_size_and_edge(extract: Path) -> None:
    places = normalize_parks(parse_parks(extract, SPEC), SPEC).frame.set_index("external_id")
    park = places.loc["way/100"]
    assert park["category"] == "green"
    assert park["subcategory"] == "Parque"
    assert park["canonical_name"] == "Parque Uno"
    assert places.loc["relation/500", "canonical_name"] == "Parque sin nombre"
    assert park["attributes"]["area_ha"] == pytest.approx(1.2, abs=0.05)
    edge = park["attributes"][EDGE_POINTS]
    assert len(edge) >= 440 / SPEC.edge_step_m  # 440 m of edge, a point every 50 m or less
    outline = shapely.MultiPoint(edge).convex_hull  # the points are the edge, in no order
    assert outline.contains(shapely.Point(park["x"], park["y"]))  # the place is inside its park
    assert outline.area == pytest.approx(12_000, rel=0.05)


def test_parks_quality_counts_the_parks(extract: Path) -> None:
    places = normalize_parks(parse_parks(extract, SPEC), SPEC)
    assert run_parks_quality(places, SPEC).passed
    strict = SPEC.model_copy(update={"min_parks": 3})
    assert not run_parks_quality(places, strict).passed


def test_the_catalogue_declares_the_parks_pipeline() -> None:
    spec = load_catalog().pipelines["osm_parques"]
    assert isinstance(spec, OsmParksPipeline)
    assert spec.min_area_ha == 1.0  # the WHO indicator's minimum size (D-222)
