"""OSM parks (DATA-018, D-222) on a hand-built extract: which areas are parks, their size and the
edge points where a walk reaches them."""

from pathlib import Path

import pytest
import shapely
from pydantic import ValidationError

from hi_contracts.catalog.corrections import ParkInclusion
from hi_contracts.catalog.pipeline import OsmParksPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.osm_parks.inclusions import load_inclusions
from hi_ingestion.pipelines.osm_parks.parks import (
    EDGE_POINTS,
    edge_points,
    normalize_parks,
    polygons_only,
)
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
    **_rectangle(51, 200, 100, 2500),  # 2 ha forest relation: a park only by its inclusion
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
        _way(105, _closed(51)),
        '  <relation id="600"><member type="way" ref="105" role="outer"/>'
        '<tag k="type" v="multipolygon"/><tag k="landuse" v="forest"/></relation>',
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


GARDEN = ParkInclusion.model_validate(
    {
        "osm_id": "way/103",
        "reason": "una fuente oficial lo lista como parque público",
        "source": {
            "publisher": "Ayuntamiento",
            "url": "https://datos.madrid.es/x.csv",
            "consulted": "2026-11-12",
            "says": "Huerto · parque histórico",
        },
    }
)


def test_an_area_an_official_source_lists_as_a_park_is_included(extract: Path) -> None:
    frame = parse_parks(extract, SPEC, [GARDEN.osm_id])
    places = normalize_parks(frame, SPEC, {GARDEN.osm_id: GARDEN}).frame.set_index("external_id")
    assert "way/103" in places.index  # leisure=garden: only by its inclusion
    inclusion = places.loc["way/103", "attributes"]["inclusion"]
    assert inclusion["url"] == "https://datos.madrid.es/x.csv"
    assert "inclusion" not in places.loc["way/100", "attributes"]


def test_the_casa_de_campo_is_included_with_an_official_source() -> None:
    inclusions = {p.osm_id: p for p in load_inclusions().parks}
    assert "relation/1946885" in inclusions  # landuse=forest in OSM (D-222 §5)
    for inclusion in inclusions.values():
        assert str(inclusion.source.url).startswith("https://")
    with pytest.raises(ValidationError):
        ParkInclusion.model_validate(GARDEN.model_dump() | {"osm_id": "node/1"})


FOREST = GARDEN.model_copy(update={"osm_id": "relation/600"})


def test_a_relation_an_official_source_lists_as_a_park_is_included(extract: Path) -> None:
    """osmium numbers a relation's area 2 x id + 1 (D-222 §5)."""
    places = normalize_parks(
        parse_parks(extract, SPEC, [FOREST.osm_id]), SPEC, {FOREST.osm_id: FOREST}
    )
    assert "relation/600" in set(places.frame["external_id"])
    assert run_parks_quality(places, SPEC, [FOREST.osm_id]).passed


def test_an_inclusion_that_is_not_published_fails_the_quality_gate(extract: Path) -> None:
    places = normalize_parks(parse_parks(extract, SPEC), SPEC)
    assert run_parks_quality(places, SPEC).passed
    assert not run_parks_quality(places, SPEC, ["relation/600"]).passed


def test_an_invalid_outline_keeps_only_its_polygons() -> None:
    mixed = shapely.GeometryCollection(
        [
            shapely.box(0, 0, 100, 100),
            shapely.LineString([(0, 0), (500, 500)]),
            shapely.MultiPolygon([shapely.box(200, 0, 300, 100)]),
        ]
    )
    kept = polygons_only(mixed)
    assert kept is not None
    assert shapely.area(kept) == pytest.approx(20_000)
    assert len(edge_points(kept, 50.0)) >= 16
    assert polygons_only(shapely.LineString([(0, 0), (1, 1)])) is None
    bowtie = shapely.Polygon([(0, 0), (200, 200), (200, 0), (0, 200), (0, 0)])
    valid = polygons_only(shapely.make_valid(bowtie))
    assert valid is not None
    assert shapely.area(valid) == pytest.approx(20_000)
