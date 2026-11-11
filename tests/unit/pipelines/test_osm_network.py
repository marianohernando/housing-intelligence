"""OSM walking network on a hand-built extract whose expected graph is worked out by hand."""

from pathlib import Path

import numpy as np
import pytest

from hi_contracts.catalog.pipeline import OsmWalkNetworkPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.osm_network.network import (
    load_network,
    normalize_segments,
    save_network,
)
from hi_ingestion.pipelines.osm_network.parse import is_walkable, parse_extract
from hi_ingestion.pipelines.osm_network.quality import run_network_quality


def _way(way_id: int, refs: list[int], **tags: str) -> str:
    nodes = "".join(f'<nd ref="{ref}"/>' for ref in refs)
    tag_xml = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items())
    return f'  <way id="{way_id}">{nodes}{tag_xml}</way>'


# 1 -> 2 is ~100 m north, 2 -> 3 ~102 m east, 3 -> 4 ~145 m north; 5 -> 6 is a separate island.
NODES = {
    1: (40.4168, -3.7038),
    2: (40.4177, -3.7038),
    3: (40.4177, -3.7026),
    4: (40.4190, -3.7026),
    5: (40.4300, -3.7100),
    6: (40.4301, -3.7100),
}
WAYS = [
    _way(10, [1, 2, 3], highway="residential"),
    _way(11, [1, 3], highway="motorway"),
    _way(12, [3, 4], highway="footway", access="private"),
    _way(13, [3, 4], highway="footway", access="private", foot="yes"),
    _way(14, [3, 2], highway="residential"),
    _way(15, [1, 4], highway="cycleway"),
    _way(16, [1, 4], highway="residential", foot="no"),
    _way(17, [1, 4], highway="proposed", foot="yes"),
    _way(18, [5, 6], highway="residential"),
    _way(19, [4, 99], highway="path"),  # node 99 is not in the extract
    _way(20, [1, 1], highway="steps"),
]
EXTRACT = "\n".join(
    [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<osm version="0.6" generator="test">',
        *(f'  <node id="{i}" lat="{lat}" lon="{lon}"/>' for i, (lat, lon) in NODES.items()),
        *WAYS,
        "</osm>",
    ]
)


def _spec(**overrides: object) -> OsmWalkNetworkPipeline:
    return OsmWalkNetworkPipeline.model_validate(
        {
            "kind": "osm_walk_network",
            "dataset_id": "osm_test",
            "walkable_highways": ["residential", "footway", "path", "steps"],
            "min_total_km": 0.1,
            **overrides,
        }
    )


@pytest.fixture
def extract(tmp_path: Path) -> Path:
    path = tmp_path / "extract.osm"
    path.write_text(EXTRACT)
    return path


@pytest.mark.parametrize(
    ("tags", "walkable"),
    [
        ({"highway": "residential"}, True),
        ({"highway": "motorway"}, False),
        ({"highway": "motorway", "foot": "yes"}, True),
        ({"highway": "footway", "access": "private"}, False),
        ({"highway": "footway", "access": "private", "foot": "permissive"}, True),
        ({"highway": "residential", "foot": "no"}, False),
        ({"highway": "proposed", "foot": "yes"}, False),
        ({"highway": "cycleway"}, False),
        ({"highway": "cycleway", "foot": "designated"}, True),
        ({"building": "yes"}, False),
    ],
)
def test_walkable_rules(tags: dict[str, str], walkable: bool) -> None:
    assert is_walkable(tags, _spec()) is walkable


def test_parse_keeps_only_walkable_segments(extract: Path) -> None:
    frame = parse_extract(extract, _spec())
    ways = {(int(u), int(v)) for u, v in zip(frame["u_id"], frame["v_id"], strict=True)}
    assert ways == {(1, 2), (2, 3), (3, 4), (3, 2), (5, 6), (4, 99), (1, 1)}
    missing = frame.loc[frame["v_id"] == 99]
    assert missing[["v_lon", "v_lat"]].isna().all(axis=None)


def test_normalize_builds_a_deduplicated_graph_in_metres(extract: Path) -> None:
    result = normalize_segments(parse_extract(extract, _spec()))
    network = result.network
    assert list(result.quarantine["reason"]) == ["missing_node_location"]
    assert network.n_nodes == 6
    assert network.n_edges == 4  # 1-2, 2-3 (once), 3-4, 5-6; the self-loop is dropped
    by_pair = {
        (int(network.node_id[u]), int(network.node_id[v])): round(float(m))
        for u, v, m in zip(network.edge_u, network.edge_v, network.edge_length_m, strict=True)
    }
    assert by_pair[(1, 2)] == pytest.approx(100, abs=2)
    assert by_pair[(2, 3)] == pytest.approx(102, abs=2)
    assert by_pair[(3, 4)] == pytest.approx(145, abs=2)
    assert set(network.highways) == {"residential", "footway"}


def test_silver_round_trip(extract: Path, tmp_path: Path) -> None:
    network = normalize_segments(parse_extract(extract, _spec())).network
    loaded = load_network(save_network(network, tmp_path))
    assert loaded.highways == network.highways
    np.testing.assert_array_equal(loaded.edge_u, network.edge_u)
    np.testing.assert_allclose(loaded.edge_length_m, network.edge_length_m)


def test_quality_flags_a_truncated_or_broken_network(extract: Path) -> None:
    result = normalize_segments(parse_extract(extract, _spec()))
    assert run_network_quality(result, _spec()).passed is False  # 1 of 5 segments lacks a node
    clean = normalize_segments(parse_extract(extract, _spec(walkable_highways=["residential"])))
    report = {c.name: c for c in run_network_quality(clean, _spec()).checks}
    assert report["missing_node_locations"].passed
    assert report["main_component_share"].details["share_of_length"] < 1
    truncated = run_network_quality(clean, _spec(min_total_km=10))
    assert not truncated.passed


def test_catalog_declares_the_walk_network() -> None:
    spec = load_catalog().pipelines["osm_red_peatonal"]
    assert isinstance(spec, OsmWalkNetworkPipeline)
    assert {"motorway", "trunk", "cycleway"}.isdisjoint(spec.walkable_highways)
    assert {"residential", "footway", "pedestrian", "living_street"} <= set(spec.walkable_highways)
