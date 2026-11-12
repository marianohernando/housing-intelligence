"""Commute matrix on the sample feeds and geography (CORE-009, D-220)."""

import pytest
from sqlalchemy import Engine, text

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
