"""Commute matrix on the sample feeds and geography (CORE-009, D-220)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.public.responses import SearchResponse
from hi_features.commute import METHOD_VERSION, compute_commutes, persist
from hi_ingestion.catalog.loader import load_catalog

pytestmark = pytest.mark.db


def test_every_zone_gets_a_row_for_every_hub_with_its_inputs(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    matrix = compute_commutes(migrated_engine, load_catalog())
    n = persist(migrated_engine, matrix)
    zones = matrix.times["origin_admin_unit_id"].nunique()
    assert n == len(matrix.hubs) * zones
    assert {h.kind for h in matrix.hubs} == {"station", "zone"}
    with migrated_engine.connect() as conn:
        stored = conn.execute(
            text("SELECT count(*), count(minutes), min(minutes), max(minutes) FROM commute_time")
        ).one()
        hub = conn.execute(
            text("SELECT method_version, inputs FROM transit_hub ORDER BY hub_id LIMIT 1")
        ).one()
    assert stored[0] == n
    assert stored[1] > 0  # the sample network reaches somewhere
    assert 0 <= stored[2] <= stored[3] <= 180
    assert hub.method_version == METHOD_VERSION
    feeds = {f["dataset_id"] for f in hub.inputs["feeds"]}
    assert feeds == {
        "crtm_gtfs_autobuses_urbanos",
        "crtm_gtfs_cercanias",
        "crtm_gtfs_emt",
        "crtm_gtfs_interurbanos",
        "crtm_gtfs_metro",
        "crtm_gtfs_metro_ligero",
    }
    again = persist(migrated_engine, matrix)  # recomputing replaces, never duplicates
    assert again == n


def test_barrios_are_origins_but_never_destinations(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    """D-232: each Madrid barrio gets its trip to every hub (the median of its sections, as a
    district); the places of work stay the stations and the municipios and districts."""
    matrix = compute_commutes(migrated_engine, load_catalog())
    with migrated_engine.connect() as conn:
        barrios = set(
            conn.execute(text("SELECT admin_unit_id FROM geo_admin_unit WHERE level = 'barrio'"))
            .scalars()
            .all()
        )
    origins = set(matrix.times["origin_admin_unit_id"])
    assert barrios and barrios <= origins
    assert not any(h.admin_unit_id in barrios for h in matrix.hubs)
    per_hub = matrix.times.groupby("hub_id")["origin_admin_unit_id"].nunique()
    assert set(per_hub) == {len(origins)}


def test_a_zone_reaches_its_own_centre_faster_than_the_median_zone(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    matrix = compute_commutes(migrated_engine, load_catalog())
    times = matrix.times
    own = [(h.admin_unit_id, h.hub_id) for h in matrix.hubs if h.kind == "zone" and h.admin_unit_id]
    checked = 0
    for zone_id, hub_id in own:
        if zone_id == "ES.28.MUN.28079":  # Madrid holds its districts: not a peer of them
            continue
        level = zone_id.rsplit(".", 1)[0]  # compare districts with districts, municipios too
        rows = times.loc[times["hub_id"] == hub_id].set_index("origin_admin_unit_id")["minutes"]
        rows = rows[[i.startswith(level) and i != "ES.28.MUN.28079" for i in rows.index]]
        mine = rows.get(zone_id)
        if mine is None or mine != mine or rows.dropna().size < 3:
            continue
        assert mine <= rows.dropna().median()
        checked += 1
    assert checked > 0


FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "contracts"


def test_the_search_uses_the_minutes_by_public_transport(
    features_computed: None, migrated_engine: Engine
) -> None:
    persist(migrated_engine, compute_commutes(migrated_engine, load_catalog()))
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    scenario = json.loads((FIXTURES / "scenario_state.familia_castellana.fixture.json").read_text())
    scenario["anchors"][0]["max_minutes"] = 40
    response = TestClient(app).post("/api/v1/search", json=scenario)
    assert response.status_code == 200, response.text
    body = SearchResponse.model_validate(response.json())
    assert not any("trip by public transport" in w for w in body.warnings)
    checks = [
        c
        for z in [*body.data.results, *body.data.near_misses]
        for c in z.constraints
        if c.constraint_id == "commute:0"
    ]
    assert checks, "no zone ranked on the fixtures"
    decided = [c for c in checks if c.status in {"PASS", "FAIL"}]
    assert decided, "the sample timetable decides no trip"
    for check in decided:
        assert check.value is not None
        assert (check.status == "PASS") == (check.value <= 40)
        assert "en transporte público" in check.explanation
    gtfs = {d.dataset_id for d in body.data.datasets if d.dataset_id.startswith("crtm_gtfs_")}
    assert gtfs  # the timetables are in the provenance
