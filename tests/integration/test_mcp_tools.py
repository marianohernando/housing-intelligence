"""MCP tools on the fixture database (MCP-001, D-225): each tool answers what its API route
answers, the explanation is the zone's search card plus its sources, and every tool reads in
a read-only transaction."""

import json
from pathlib import Path
from typing import Any

import anyio
import pytest
from fastapi.testclient import TestClient
from mcp import Client
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import DBAPIError

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.public import ZoneLookup
from hi_contracts.public.responses import (
    DatasetListResponse,
    SearchResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)
from hi_mcp.server import build_server, run_tool

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "contracts"


@pytest.fixture
def api(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


@pytest.fixture
def server(migrated_engine: Engine, features_computed: None) -> MCPServer:
    return build_server(lambda: migrated_engine)


def _call(server: MCPServer, name: str, arguments: dict[str, Any]) -> CallToolResult:
    async def call() -> CallToolResult:
        async with Client(server) as client:
            return await client.call_tool(name, arguments)

    return anyio.run(call)


def _ok(server: MCPServer, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = _call(server, name, arguments)
    assert not result.is_error, result.content
    assert result.structured_content is not None
    return result.structured_content


def _family() -> dict[str, Any]:
    scenario = json.loads((FIXTURES / "scenario_state.familia_castellana.fixture.json").read_text())
    for anchor in scenario["anchors"]:
        anchor["max_minutes"] = None
    return scenario


def _same_answer(tool: dict[str, Any], route: dict[str, Any]) -> None:
    """Same data, warnings and versions; only the request id and time differ."""
    assert tool["data"] == route["data"]
    assert tool["warnings"] == route["warnings"]
    for key in ("methodology_version", "data_version", "api_version"):
        assert tool["meta"][key] == route["meta"][key]


def test_buscar_zonas_is_post_search(server: MCPServer, api: TestClient) -> None:
    route = api.post("/api/v1/search", json=_family()).json()
    with_map = _ok(server, "buscar_zonas", {"scenario": _family(), "include_map": True})
    _same_answer(SearchResponse.model_validate(with_map).model_dump(mode="json"), route)
    without = SearchResponse.model_validate(_ok(server, "buscar_zonas", {"scenario": _family()}))
    assert without.data.all_zones == []
    assert without.model_dump(mode="json")["data"] == route["data"] | {"all_zones": []}


@pytest.mark.parametrize(("level", "code"), [("municipio", "28079"), ("distrito", "2807906")])
def test_que_falta_is_get_gaps(server: MCPServer, api: TestClient, level: str, code: str) -> None:
    route = api.get(f"/api/v1/gaps/{level}/{code}").json()
    tool = ZoneGapListResponse.model_validate(
        _ok(server, "que_falta", {"level": level, "code": code})
    )
    _same_answer(tool.model_dump(mode="json"), route)


def test_fuentes_de_datos_is_get_datasets(server: MCPServer, api: TestClient) -> None:
    for cm_only in (False, True):
        route = api.get(f"/api/v1/datasets?cm_only={str(cm_only).lower()}").json()
        tool = DatasetListResponse.model_validate(
            _ok(server, "fuentes_de_datos", {"cm_only": cm_only})
        )
        _same_answer(tool.model_dump(mode="json"), route)


def test_explicar_zona_is_the_zone_card_of_the_search(server: MCPServer, api: TestClient) -> None:
    search = SearchResponse.model_validate(api.post("/api/v1/search", json=_family()).json()).data
    card = (search.results or search.near_misses)[0]
    arguments = {"level": card.zone.level.value, "code": card.zone.code, "scenario": _family()}
    body = ZoneExplanationResponse.model_validate(_ok(server, "explicar_zona", arguments))
    explained = body.data
    assert explained.zone == card.zone
    assert explained.match_pct == card.match_pct
    assert explained.confidence == card.confidence
    assert explained.facts == card.facts
    assert explained.constraints == card.constraints
    assert explained.estimated_cost_eur == card.estimated_cost_eur
    assert explained.gap_highlights == card.gap_highlights
    assert body.meta.methodology_version == search.methodology_version


def test_explicar_zona_cites_every_dataset_it_reads(server: MCPServer, api: TestClient) -> None:
    every = DatasetListResponse.model_validate(api.get("/api/v1/datasets").json()).data.datasets
    published = {d.dataset_id: d for d in every}
    arguments = {"level": "distrito", "code": "2807906"}
    explained = ZoneExplanationResponse.model_validate(_ok(server, "explicar_zona", arguments)).data
    cited = {d.dataset_id for d in explained.datasets}
    assert explained.indicators
    for indicator in explained.indicators:
        assert set(indicator.datasets) <= cited, indicator.feature_id
    for fact in explained.facts:
        if fact.indicator is not None:
            assert set(fact.indicator.datasets) <= cited
    for dataset in explained.datasets:
        assert dataset.attribution_text == published[dataset.dataset_id].attribution_text
    assert explained.cm_open_data_count == sum(d.is_cm_open_data for d in explained.datasets) > 0


@pytest.mark.parametrize(
    ("tool", "arguments", "says"),
    [
        ("que_falta", {"level": "municipio", "code": "28999"}, "No municipio with code 28999"),
        ("explicar_zona", {"level": "municipio", "code": "28999"}, "No municipio with code 28999"),
        ("explicar_zona", {"level": "municipio", "code": "28079"}, "ranked by district"),
    ],
)
def test_zones_outside_the_tool_are_readable_errors(
    server: MCPServer, tool: str, arguments: dict[str, Any], says: str
) -> None:
    result = _call(server, tool, arguments)
    assert result.is_error
    block = result.content[0]
    assert block.type == "text"
    assert says in block.text


def test_encontrar_zona_gives_the_zone_of_the_gaps_route(
    server: MCPServer, api: TestClient
) -> None:
    found = ZoneLookup.model_validate(_ok(server, "encontrar_zona", {"name": "tetuan"})["data"])
    gaps = ZoneGapListResponse.model_validate(api.get("/api/v1/gaps/distrito/2807906").json())
    assert found.zones[0] == gaps.data.zone
    madrid = ZoneLookup.model_validate(_ok(server, "encontrar_zona", {"name": "MADRID"})["data"])
    assert (madrid.zones[0].level.value, madrid.zones[0].code) == ("municipio", "28079")
    nothing = ZoneLookupResponse.model_validate(
        _ok(server, "encontrar_zona", {"name": "Atlántida"})
    )
    assert nothing.data.zones == []
    assert nothing.warnings and nothing.warnings[0].startswith("NOT_FOUND")


def test_tools_read_in_a_read_only_transaction(migrated_engine: Engine) -> None:
    def write(conn: Connection) -> ZoneLookupResponse:
        conn.execute(text("CREATE TABLE mcp_must_not_write (x int)"))
        return ZoneLookupResponse(data=ZoneLookup(query="", zones=[]))

    with pytest.raises(DBAPIError, match="read-only transaction"):
        run_tool("write", migrated_engine, write)
