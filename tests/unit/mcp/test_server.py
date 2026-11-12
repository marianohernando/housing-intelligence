"""MCP server contract without a database (MCP-001, D-225): five read-only tools whose inputs and
outputs are the API contracts, inputs validated before any query, a readable error when the
database is down and a stdio entrypoint that speaks the protocol."""

import json
import os
import sys
from collections.abc import Callable
from typing import Any

import anyio
import pytest
from mcp import Client, StdioServerParameters
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, Tool
from pydantic import BaseModel
from sqlalchemy import Engine

from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import (
    DatasetListResponse,
    SearchResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)
from hi_db.session import make_engine
from hi_mcp.server import DB_UNAVAILABLE, build_server, reply

NO_DATABASE = "postgresql+psycopg://unit:unit@127.0.0.1:1/no_database_in_unit_tests"
OUTPUTS: dict[str, type[BaseModel]] = {
    "buscar_zonas": SearchResponse,
    "que_falta": ZoneGapListResponse,
    "explicar_zona": ZoneExplanationResponse,
    "encontrar_zona": ZoneLookupResponse,
    "fuentes_de_datos": DatasetListResponse,
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


def test_the_five_tools_are_read_only_and_closed_world() -> None:
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
    """CLAUDE.md §3: tools over domain services; the only free text is a place name."""
    for name, tool in _tools(build_server(_never_connects)).items():
        assert "sql" not in name
        free_text = {
            key
            for key, spec in tool.input_schema["properties"].items()
            if spec.get("type") == "string" and "pattern" not in spec and "enum" not in spec
        }
        assert free_text <= {"name"}, (name, free_text)


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
        {"data": {"query": "Chamartín", "zones": []}, "warnings": ["NOT_FOUND: ninguna"]}
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
