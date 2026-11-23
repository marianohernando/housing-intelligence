"""MCP server contract without a database (MCP-001, D-225, D-249): seven read-only tools whose
inputs and outputs are the API contracts, inputs validated before any query, a readable error when
the database is down and a stdio entrypoint that speaks the protocol."""

import json
import os
import sys
from collections.abc import Callable
from typing import Any

import anyio
import pytest
from fastapi.testclient import TestClient
from mcp import Client, StdioServerParameters
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, Tool
from pydantic import BaseModel
from sqlalchemy import Connection, Engine

from hi_api.main import app
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.pro.investors import ViabilityRequest
from hi_contracts.public import ScenarioState, ZoneLookup, ZoneRef
from hi_contracts.public.responses import (
    DatasetListResponse,
    InvestorZoneResponse,
    SearchResponse,
    ViabilityResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)
from hi_db.session import make_engine
from hi_domain.viability import VIABILITY_VERSION
from hi_mcp import tools
from hi_mcp.server import DB_UNAVAILABLE, build_server, reply

NO_DATABASE = "postgresql+psycopg://unit:unit@127.0.0.1:1/no_database_in_unit_tests"
OUTPUTS: dict[str, type[BaseModel]] = {
    "buscar_zonas": SearchResponse,
    "que_falta": ZoneGapListResponse,
    "explicar_zona": ZoneExplanationResponse,
    "encontrar_zona": ZoneLookupResponse,
    "fuentes_de_datos": DatasetListResponse,
    "ficha_inversor": InvestorZoneResponse,
    "viabilidad": ViabilityResponse,
}
# The body of tests/unit/investors/test_investors_api.py, as POST /investors/viability takes it
VIABILITY = {
    "buildable_m2": 1000,
    "sale_price_m2": 4000,
    "rent_m2_month": 15,
    "pem_m2": 600,
    "cost_coefficient": 1.5,
    "sales_costs_pct": 10,
}


def _never_connects() -> Engine:
    raise AssertionError("the input should have been rejected before opening the database")


def _tools(server: MCPServer) -> dict[str, Tool]:
    async def listing() -> dict[str, Tool]:
        async with Client(server) as client:
            return {t.name: t for t in (await client.list_tools()).tools}

    return anyio.run(listing)


def _call(server: MCPServer, name: str, arguments: dict[str, Any]) -> CallToolResult:
    async def call() -> CallToolResult:
        async with Client(server) as client:
            return await client.call_tool(name, arguments)

    return anyio.run(call)


def _text(result: CallToolResult) -> str:
    block = result.content[0]
    assert block.type == "text"
    return block.text


def test_the_seven_tools_are_read_only_and_closed_world() -> None:
    tools = _tools(build_server(_never_connects))
    assert set(tools) == set(OUTPUTS)
    for tool in tools.values():
        hints = tool.annotations
        assert hints is not None
        assert hints.read_only_hint is True
        assert hints.destructive_hint is False
        assert hints.open_world_hint is False
        assert tool.title and tool.description


def test_no_tool_takes_free_sql() -> None:
    """CLAUDE.md §3: tools over domain services; the only free text is a place name (a zone's,
    or a barrio's, which may also be its code)."""
    for name, tool in _tools(build_server(_never_connects)).items():
        assert "sql" not in name
        free_text = {
            key
            for key, spec in tool.input_schema["properties"].items()
            if spec.get("type") == "string" and "pattern" not in spec and "enum" not in spec
        }
        assert free_text <= {"name", "barrio"}, (name, free_text)


@pytest.mark.parametrize(("tool", "model"), list(OUTPUTS.items()))
def test_each_output_is_its_contract(tool: str, model: type[BaseModel]) -> None:
    """The API routes answer the same models (data/schemas/api, data/schemas/mcp)."""
    assert _tools(build_server(_never_connects))[tool].output_schema == model.model_json_schema()


def test_the_search_takes_the_scenario_state_of_the_api() -> None:
    schema = _tools(build_server(_never_connects))["buscar_zonas"].input_schema
    assert schema["required"] == ["scenario"]
    assert schema["properties"]["scenario"] == {"$ref": "#/$defs/ScenarioState"}
    expected = ScenarioState.model_json_schema()
    assert schema["$defs"]["ScenarioState"]["properties"] == expected["properties"]


def test_the_viability_takes_the_request_of_the_api() -> None:
    """The same body as POST /api/v1/investors/viability: same fields, bounds and defaults."""
    schema = _tools(build_server(_never_connects))["viabilidad"].input_schema
    assert schema["required"] == ["request"]
    assert schema["properties"]["request"] == {"$ref": "#/$defs/ViabilityRequest"}
    expected = ViabilityRequest.model_json_schema()
    assert schema["$defs"]["ViabilityRequest"]["properties"] == expected["properties"]
    assert schema["$defs"]["ViabilityRequest"]["required"] == expected["required"]


def test_the_viability_names_the_method_version_of_the_domain() -> None:
    """The description reads the version from hi_domain.viability, never a typed one."""
    description = _tools(build_server(_never_connects))["viabilidad"].description or ""
    assert f"({VIABILITY_VERSION})" in description
    assert description.count("viability-") == 1  # no other version typed by hand


def test_the_viability_is_the_route_without_a_database() -> None:
    """It never opens the database (the engine factory would fail) and answers what the route
    answers: data, warnings and method version."""
    for body in (VIABILITY, VIABILITY | {"land_eur_m2": 2200, "demand": {"household_income": 4e4}}):
        route = TestClient(app).post("/api/v1/investors/viability", json=body).json()
        result = _call(build_server(_never_connects), "viabilidad", {"request": body})
        assert not result.is_error, result.content
        tool = ViabilityResponse.model_validate(result.structured_content).model_dump(mode="json")
        assert tool["data"] == route["data"]
        assert tool["warnings"] == route["warnings"]
        assert tool["meta"]["methodology_version"] == route["meta"]["methodology_version"]


@pytest.mark.parametrize(
    ("tool", "arguments", "says"),
    [
        ("que_falta", {"level": "barrio", "code": "28079"}, "level"),
        ("que_falta", {"level": "municipio", "code": "08019"}, "code"),
        ("que_falta", {"level": "municipio", "code": "28079; select 1"}, "code"),
        ("explicar_zona", {"level": "seccion_censal", "code": "2807905001"}, "level"),
        ("buscar_zonas", {"scenario": {"priorities": ["vistas"]}}, "priorities"),
        ("buscar_zonas", {"scenario": {"budget": {"kind": "rent", "amount_eur": 5}}}, "budget"),
        ("encontrar_zona", {"name": "a"}, "name"),
        ("ficha_inversor", {"barrio": "a"}, "barrio"),
        ("ficha_inversor", {"barrio": "Atlántida"}, "No pilot barrio"),
        ("ficha_inversor", {"barrio": "San"}, "matches 5 pilot barrios: San Diego"),
        ("viabilidad", {"request": VIABILITY | {"buildable_m2": 49}}, "buildable_m2"),
        ("viabilidad", {"request": VIABILITY | {"land_eur": 1, "land_eur_m2": 1}}, "not both"),
        ("viabilidad", {"request": VIABILITY | {"sql": "select 1"}}, "sql"),
        ("viabilidad", {"request": {"buildable_m2": 1000}}, "sale_price_m2"),
    ],
)
def test_invalid_inputs_never_reach_the_database(
    tool: str, arguments: dict[str, Any], says: str
) -> None:
    result = _call(build_server(_never_connects), tool, arguments)
    assert result.is_error
    assert says in _text(result)


def test_a_database_that_does_not_answer_is_a_readable_tool_error() -> None:
    engine = make_engine(NO_DATABASE)
    factory: Callable[[], Engine] = lambda: engine  # noqa: E731
    result = _call(build_server(factory), "que_falta", {"level": "municipio", "code": "28079"})
    assert result.is_error
    message = _text(result)
    assert DB_UNAVAILABLE in message
    assert "unit:unit" not in message
    assert "127.0.0.1" not in message


def test_the_text_is_the_structured_content_in_compact_json() -> None:
    response = ZoneLookupResponse.model_validate(
        {
            "data": {"query": "Chamartín", "zones": [], "total": 0},
            "warnings": ["NOT_FOUND: ninguna"],
        }
    )
    result = reply(response)
    text = _text(result)
    assert json.loads(text) == result.structured_content
    assert "\n" not in text
    assert "Chamartín" in text  # UTF-8, not \u escapes: fewer tokens for the model


def test_the_stdio_entrypoint_speaks_the_protocol() -> None:
    """What `make mcp` and an MCP client launch: stdout carries only the protocol."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "hi_mcp.server"],
        env={**os.environ, "DATABASE_URL": NO_DATABASE},
    )

    async def over_stdio() -> tuple[set[str], str | None]:
        async with Client(params) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            return names, client.instructions

    names, instructions = anyio.run(over_stdio)
    assert names == set(OUTPUTS)
    assert instructions is not None
    assert "No inventes cifras" in instructions


def test_stdout_carries_only_json_rpc() -> None:
    """A stray print or log line on stdout would break a stricter client than the SDK's."""
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    }

    async def run() -> tuple[str, str]:
        with anyio.fail_after(60):
            process = await anyio.run_process(
                [sys.executable, "-m", "hi_mcp.server"],
                input=(json.dumps(initialize) + "\n").encode(),
                env={**os.environ, "DATABASE_URL": NO_DATABASE},
                check=False,
            )
        return process.stdout.decode(), process.stderr.decode()

    stdout, stderr = anyio.run(run)
    lines = [line for line in stdout.splitlines() if line.strip()]
    assert lines, stderr
    for line in lines:
        message = json.loads(line)
        assert message["jsonrpc"] == "2.0"
    assert json.loads(lines[0])["result"]["serverInfo"]["name"] == "vida-facil"


def _lookup(total: int, shown: int) -> Callable[[Connection, str], ZoneLookup]:
    zone = ZoneRef(level=TerritoryLevel.DISTRITO, code="2807905", name="Chamartín")
    return lambda _conn, name: ZoneLookup(query=name, zones=[zone] * shown, total=total)


@pytest.mark.parametrize(
    ("total", "shown", "warning"),
    [(0, 0, "NOT_FOUND"), (12, 10, "2 more zones match"), (3, 3, None)],
)
def test_the_lookup_says_when_nothing_or_not_everything_is_shown(
    monkeypatch: pytest.MonkeyPatch, total: int, shown: int, warning: str | None
) -> None:
    monkeypatch.setattr(tools, "find_zones", _lookup(total, shown))
    warnings = tools.zone_lookup(Connection.__new__(Connection), "cha").warnings
    if warning is None:
        assert warnings == []
    else:
        assert len(warnings) == 1
        assert warning in warnings[0]


@pytest.mark.parametrize(
    ("query", "admin_unit_id"),
    [
        ("28079164", "ES.28.BAR.28079164"),
        ("ES.28.BAR.28079164", "ES.28.BAR.28079164"),
        (" pinar del rey ", "ES.28.BAR.28079164"),
        ("NIÑO JESUS", "ES.28.BAR.28079036"),
        ("Jerónimos", "ES.28.BAR.28079035"),
        ("Palos", "ES.28.BAR.28079026"),
    ],
)
def test_a_barrio_by_its_code_or_its_name(query: str, admin_unit_id: str) -> None:
    """As encontrar_zona: no case, accents or extra spaces; the code or the id the API takes."""
    assert tools.resolve_barrio(query) == (admin_unit_id, [])


def test_the_best_match_wins_and_the_others_are_named() -> None:
    pilot = (("28079011", "Palacio", "Centro"), ("28079091", "Casa de Campo", "Moncloa-Aravaca"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(tools, "PILOT_BARRIOS", pilot)
        found, warnings = tools.resolve_barrio("pala")  # starts Palacio; inside no other
        assert (found, warnings) == ("ES.28.BAR.28079011", [])
        found, warnings = tools.resolve_barrio("casa")  # Casa de Campo first; no tie
        assert found == "ES.28.BAR.28079091"
        assert warnings == []
        patch.setattr(tools, "PILOT_BARRIOS", (*pilot, ("1", "Las Casas", "X")))
        found, warnings = tools.resolve_barrio("casa")
        assert found == "ES.28.BAR.28079091"  # starts with it, before a word that starts with it
        assert len(warnings) == 1
        assert "1 more pilot barrios match «casa» (Las Casas (X, 1))" in warnings[0]


def test_a_code_outside_madrid_is_not_a_barrio_code() -> None:
    with pytest.raises(tools.BarrioNotResolvedError, match="No pilot barrio"):
        tools.resolve_barrio("28005001")
