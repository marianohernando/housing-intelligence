"""Step-free stations (DATA-019, D-223): the CRTM network topology and its link to GTFS places."""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from hi_contracts.catalog.pipeline import (
    GtfsFeedPipeline,
    StationAccessibilityLink,
    StationTopologyPipeline,
)
from hi_ingestion.pipelines.gtfs.accessibility import StationGrades, station_step_free
from hi_ingestion.pipelines.station_topology.normalize import (
    normalize_topology,
    parse_layer,
)
from hi_ingestion.pipelines.station_topology.quality import run_topology_quality


def _spec(**overrides: Any) -> StationTopologyPipeline:
    data: dict[str, Any] = {
        "kind": "station_topology",
        "dataset_id": "crtm_topologia_metro",
        "id_field": "IDESTACION",
        "operator_code_field": "CODIGOEMPRESA",
        "name_field": "DENOMINACION",
        "grade_field": "GRADOACCESIBILIDAD",
        "step_free": {"T": "yes", "P": "partial", "N": "no"},
        "min_rows": 2,
        "max_rows": 10,
    }
    return StationTopologyPipeline.model_validate(data | overrides)


def _feature(station: str, grade: str | None, code: str = "60101") -> dict[str, Any]:
    return {
        "attributes": {
            "IDESTACION": station,
            "CODIGOEMPRESA": code,
            "DENOMINACION": f"Estación {station}",
            "GRADOACCESIBILIDAD": grade,
            "LINEAS": "1, 2",
        },
        "geometry": {"x": 440000.0, "y": 4475000.0},
    }


def _layer(tmp_path: Path, features: list[dict[str, Any]], **extra: Any) -> Path:
    path = tmp_path / "M4_Estaciones.json"
    path.write_text(json.dumps({"features": features, **extra}), encoding="utf-8")
    return path


def test_the_layer_becomes_one_row_per_station(tmp_path: Path) -> None:
    path = _layer(tmp_path, [_feature("4_12", "P"), _feature("4_38", "N"), _feature("4_1", "T")])
    topology = normalize_topology(parse_layer(path), _spec())
    rows = topology.frame.set_index("station_id").to_dict("index")
    assert rows["4_1"]["step_free"] == "yes"
    assert rows["4_12"]["step_free"] == "partial"
    assert rows["4_38"]["step_free"] == "no"
    assert rows["4_38"]["grade"] == "N"  # the published code is kept next to its reading
    assert rows["4_1"]["operator_code"] == "60101"
    assert topology.quarantine.empty


def test_an_unknown_or_missing_grade_is_quarantined_never_guessed(tmp_path: Path) -> None:
    path = _layer(tmp_path, [_feature("4_1", "T"), _feature("4_2", None), _feature("4_3", "X")])
    topology = normalize_topology(parse_layer(path), _spec())
    assert list(topology.frame["station_id"]) == ["4_1"]
    assert sorted(topology.quarantine["station_id"]) == ["4_2", "4_3"]
    assert set(topology.quarantine["reason"]) == {"grade_not_published"}


def test_a_truncated_layer_fails_loudly(tmp_path: Path) -> None:
    """ArcGIS cuts a query at its transfer limit and says so: never a partial network."""
    path = _layer(tmp_path, [_feature("4_1", "T")], exceededTransferLimit=True)
    with pytest.raises(ValueError, match="transfer limit"):
        parse_layer(path)


def test_quality_gate(tmp_path: Path) -> None:
    good = _layer(tmp_path, [_feature("4_1", "T"), _feature("4_2", "N")])
    report = run_topology_quality(normalize_topology(parse_layer(good), _spec()), _spec())
    assert report.passed
    duplicated = _layer(tmp_path, [_feature("4_1", "T"), _feature("4_1", "N")])
    report = run_topology_quality(normalize_topology(parse_layer(duplicated), _spec()), _spec())
    assert not report.passed
    assert {c.name for c in report.checks if not c.passed} == {"unique_ids"}
    short = _layer(tmp_path, [_feature("4_1", "T")])
    report = run_topology_quality(normalize_topology(parse_layer(short), _spec()), _spec())
    assert {c.name for c in report.checks if not c.passed} == {"rows_in_range"}


def test_topology_spec_rejects_readings_outside_yes_partial_no() -> None:
    with pytest.raises(ValidationError):
        _spec(step_free={"T": "si"})
    with pytest.raises(ValidationError):
        _spec(min_rows=10, max_rows=2)


def test_gtfs_link_needs_a_pattern_with_one_group() -> None:
    base = {"kind": "gtfs_feed", "dataset_id": "crtm_gtfs_metro", "mode": "metro"}
    link = {"dataset_id": "crtm_topologia_metro", "match": "station_id"}
    ok = GtfsFeedPipeline.model_validate(
        base | {"station_accessibility": link | {"stop_id_pattern": r"^(?:par|est)_(\d+_\d+)$"}}
    )
    assert ok.station_accessibility is not None
    for pattern in (r"^par_\d+$", r"^(par)_(\d+)$", "(unclosed"):
        with pytest.raises(ValidationError):
            StationAccessibilityLink.model_validate(link | {"stop_id_pattern": pattern})


METRO = re.compile(r"^(?:par|est)_(4_\d+)$")
GRADES = StationGrades(
    dataset_id="crtm_topologia_metro",
    version_label="v1",
    step_free={"4_1": "yes", "4_2": "yes", "4_3": "no", "4_4": "partial"},
)


def test_a_station_is_step_free_when_its_topology_says_so() -> None:
    assert station_step_free(["est_4_1", "par_4_1"], METRO, GRADES) == ("yes", ["4_1"])


def test_an_interchange_takes_its_least_accessible_station() -> None:
    """Sol is one place in the GTFS and three stations (one per line) in the topology: it is
    step-free only if every one of them is (D-223 §3)."""
    assert station_step_free(["est_90_58", "par_4_1", "par_4_2"], METRO, GRADES) == (
        "yes",
        ["4_1", "4_2"],
    )
    assert station_step_free(["par_4_1", "par_4_4"], METRO, GRADES)[0] == "partial"
    assert station_step_free(["par_4_1", "par_4_4", "par_4_3"], METRO, GRADES)[0] == "no"


def test_a_station_missing_from_the_topology_stays_unknown() -> None:
    """Unknown is never step-free, even if its other platforms are (CLAUDE.md §14)."""
    assert station_step_free(["par_4_1", "par_4_99"], METRO, GRADES) == (None, ["4_1", "4_99"])
    assert station_step_free(["acc_4_1_7", "bus_1"], METRO, GRADES) == (None, [])


def test_operator_codes_match_as_published() -> None:
    renfe = StationGrades("crtm_topologia_cercanias", "v1", {"10000": "partial"})
    assert station_step_free(["10000"], re.compile(r"^(\d+)$"), renfe) == ("partial", ["10000"])


def _transport(attributes: list[dict[str, Any]]) -> Any:
    import pandas as pd

    from hi_ingestion.pipelines.gtfs.run import TransportPlaces
    from hi_ingestion.pipelines.places.normalize import Places

    frame = pd.DataFrame(
        {
            "external_id": [f"S{i}" for i in range(len(attributes))],
            "canonical_name": [f"Estación {i}" for i in range(len(attributes))],
            "attributes": attributes,
        }
    )
    places = Places(frame=frame, quarantine=pd.DataFrame(), source_rows=len(frame), filtered_out={})
    return TransportPlaces(places=places, feed={})


def test_step_free_gate_blocks_only_once_the_topology_is_loaded() -> None:
    from hi_ingestion.pipelines.gtfs.run import step_free_check

    source = {"step_free_source": "crtm_topologia_metro v1"}
    loaded = [source | {"step_free": "yes"}] * 9 + [source]
    check = step_free_check(_transport(loaded))
    assert check.critical and check.passed  # 9 of 10 read: 90 %
    short = [source | {"step_free": "yes"}] * 8 + [source] * 2
    check = step_free_check(_transport(short))
    assert check.critical and not check.passed
    missing = step_free_check(_transport([{}, {}]))
    assert not missing.critical and not missing.passed
    assert missing.details["source"] == "topology not ingested"


def test_a_shared_operator_code_keeps_the_least_accessible_station() -> None:
    import pandas as pd

    from hi_ingestion.pipelines.gtfs.accessibility import grades_from_frame

    frame = pd.DataFrame(
        {
            "station_id": ["5_1", "5_2", "5_3", "5_4"],
            "operator_code": ["10000", "10000", "", "17000"],
            "step_free": ["yes", "partial", "no", "yes"],
        }
    )
    link = StationAccessibilityLink(
        dataset_id="crtm_topologia_cercanias", match="operator_code", stop_id_pattern=r"^(\d+)$"
    )
    grades = grades_from_frame(frame, link, "v1")
    assert dict(grades.step_free) == {"10000": "partial", "17000": "yes"}


def test_a_file_already_in_bronze_keeps_its_official_url(tmp_path: Path) -> None:
    from hi_ingestion.bronze import sha256_file
    from hi_ingestion.pipelines.fetch import local_file

    data = tmp_path / "feed.zip"
    data.write_bytes(b"gtfs")
    loose = local_file("crtm_gtfs_metro", "primary", data)
    assert loose.url.startswith("file://")
    entry = {
        "sha256": sha256_file(data),
        "url": "https://www.arcgis.com/sharing/rest/content/items/x/data",
        "retrieved_at": "2026-11-10T19:39:58+00:00",
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"files": [entry]}))
    kept = local_file("crtm_gtfs_metro", "primary", data)
    assert (kept.url, kept.retrieved_at) == (entry["url"], entry["retrieved_at"])
