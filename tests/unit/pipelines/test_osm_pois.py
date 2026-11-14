"""OSM points of interest (D-236) on a hand-built extract: which nodes and areas are leisure
places, what is kept of each and what stays out."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from hi_contracts.catalog.pipeline import OsmPoisPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.osm_pois.parse import parse_pois
from hi_ingestion.pipelines.osm_pois.places import normalize_pois
from hi_ingestion.pipelines.osm_pois.quality import run_pois_quality

LAT, LON = 40.4168, -3.7038
CLASSES = [
    {"key": "amenity", "value": "bar", "category": "commerce", "subcategory": "Bar"},
    {"key": "amenity", "value": "restaurant", "category": "commerce", "subcategory": "Restaurante"},
    {
        "key": "leisure",
        "value": "sports_centre",
        "category": "sport",
        "subcategory": "Centro deportivo",
    },
]
SPEC = OsmPoisPipeline.model_validate(
    {
        "kind": "osm_pois",
        "dataset_id": "osm_ocio",
        "classes": CLASSES,
        "min_places": 1,
        "max_places": 10,
    }
)


def _node(node_id: int, lat: float, lon: float, **tags: str) -> str:
    tag_xml = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items())
    return f'  <node id="{node_id}" lat="{lat}" lon="{lon}">{tag_xml}</node>'


SQUARE = [(0.0, 0.0), (0.001, 0.0), (0.001, 0.001), (0.0, 0.001)]
EXTRACT = "\n".join(
    [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<osm version="0.6" generator="test">',
        _node(1, LAT, LON, amenity="bar", name="Bar Uno", phone="910000000"),
        _node(2, LAT, LON + 0.001, amenity="restaurant"),
        _node(3, LAT, LON + 0.002, amenity="fast_food", name="Burger"),
        _node(4, LAT, LON + 0.003, amenity="bar", access="private", name="Peña privada"),
        _node(5, 43.0, -8.0, amenity="bar", name="Fuera de Madrid"),
        _node(6, LAT, LON + 0.004, tourism="museum", amenity="cafe", name="Museo del Barrio"),
        _node(7, LAT, LON + 0.005, amenity="library", name="Biblioteca Municipal"),
        *(_node(10 + i, LAT + 0.01 + n, LON + e) for i, (e, n) in enumerate(SQUARE)),
        '  <way id="100"><nd ref="10"/><nd ref="11"/><nd ref="12"/><nd ref="13"/><nd ref="10"/>'
        '<tag k="leisure" v="sports_centre"/><tag k="name" v="Polideportivo Municipal"/></way>',
        "</osm>",
    ]
)


@pytest.fixture(scope="module")
def extract(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("osm") / "pois.osm"
    path.write_text(EXTRACT)
    return path


def test_only_nodes_and_areas_with_a_declared_tag_are_read(extract: Path) -> None:
    frame = parse_pois(extract, SPEC)
    assert sorted(frame["external_id"]) == ["node/1", "node/2", "node/4", "node/5", "way/100"]


def test_an_area_becomes_a_point_inside_it(extract: Path) -> None:
    area = parse_pois(extract, SPEC).set_index("external_id").loc["way/100"]
    assert LON < area["lon"] < LON + 0.001
    assert LAT + 0.01 < area["lat"] < LAT + 0.011


def test_private_places_stay_out_and_places_outside_the_region_are_quarantined(
    extract: Path,
) -> None:
    places = normalize_pois(parse_pois(extract, SPEC), SPEC)
    assert sorted(places.frame["external_id"]) == ["node/1", "node/2", "way/100"]
    assert places.filtered_out == {"access_denied": 1}
    assert places.quarantine["external_id"].tolist() == ["node/5"]


def test_a_place_keeps_its_class_name_and_tag_and_nothing_else(extract: Path) -> None:
    places = normalize_pois(parse_pois(extract, SPEC), SPEC).frame.set_index("external_id")
    bar = places.loc["node/1"]
    assert (bar["category"], bar["subcategory"], bar["canonical_name"]) == (
        "commerce",
        "Bar",
        "Bar Uno",
    )
    assert bar["attributes"] == {"osm_tag": "amenity=bar"}  # no phone, address or hours
    assert places.loc["node/2", "canonical_name"] == "Restaurante sin nombre"
    assert places.loc["way/100", "category"] == "sport"  # municipal sports centres count


def test_quality_wants_a_plausible_count_every_class_and_few_bad_points(extract: Path) -> None:
    frame = parse_pois(extract, SPEC)
    assert not run_pois_quality(normalize_pois(frame, SPEC), SPEC).passed  # 1 of 4 quarantined
    inside = frame.loc[frame["external_id"] != "node/5"]
    places = normalize_pois(inside, SPEC)
    assert run_pois_quality(places, SPEC).passed
    assert not run_pois_quality(places, SPEC.model_copy(update={"min_places": 5})).passed
    cinema = {"key": "amenity", "value": "cinema", "category": "culture", "subcategory": "Cine"}
    wider = OsmPoisPipeline.model_validate(SPEC.model_dump() | {"classes": [*CLASSES, cinema]})
    report = run_pois_quality(normalize_pois(inside, wider), wider)
    assert not report.passed  # a declared class with no place: a tag misspelt or a bad extract


def test_museums_and_libraries_are_culture_and_the_first_declared_tag_wins(
    extract: Path,
) -> None:
    """«Cultura» (D-236): a museum is a `tourism` tag, a library an `amenity` one. A museum
    that also has a café takes the class declared first in the pipeline."""
    culture = [
        {"key": "tourism", "value": "museum", "category": "culture", "subcategory": "Museo"},
        {"key": "amenity", "value": "library", "category": "culture", "subcategory": "Biblioteca"},
        {"key": "amenity", "value": "cafe", "category": "commerce", "subcategory": "Cafetería"},
    ]
    wider = OsmPoisPipeline.model_validate(SPEC.model_dump() | {"classes": [*CLASSES, *culture]})
    places = normalize_pois(parse_pois(extract, wider), wider).frame.set_index("external_id")
    museum, library = places.loc["node/6"], places.loc["node/7"]
    assert (museum["category"], museum["subcategory"]) == ("culture", "Museo")
    assert museum["attributes"] == {"osm_tag": "tourism=museum"}
    assert (library["subcategory"], library["canonical_name"]) == (
        "Biblioteca",
        "Biblioteca Municipal",
    )


def test_a_tag_cannot_be_declared_twice() -> None:
    with pytest.raises(ValidationError, match="once"):
        OsmPoisPipeline.model_validate(SPEC.model_dump() | {"classes": [*CLASSES, CLASSES[0]]})


def test_the_catalogue_declares_the_leisure_pipeline_without_fast_food() -> None:
    """D-236: bars, pubs and cafés; restaurants; gyms and sports centres; culture (museums,
    libraries, theatres, cinemas and arts centres). Fast food stays out of «Restaurantes»."""
    spec = load_catalog().pipelines["osm_ocio"]
    assert isinstance(spec, OsmPoisPipeline)
    tags = {f"{c.key}={c.value}" for c in spec.classes}
    assert tags == {
        "amenity=bar",
        "amenity=pub",
        "amenity=cafe",
        "amenity=restaurant",
        "leisure=fitness_centre",
        "leisure=sports_centre",
        "tourism=museum",
        "amenity=library",
        "amenity=theatre",
        "amenity=cinema",
        "amenity=arts_centre",
    }
    culture = {c.subcategory for c in spec.classes if c.category.value == "culture"}
    assert culture == {"Museo", "Biblioteca", "Teatro", "Cine", "Centro cultural"}
