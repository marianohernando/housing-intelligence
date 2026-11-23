"""The MCP server over Streamable HTTP beside the API (D-255), without network or database: the
JSON-RPC a remote client sends to /api/v1/mcp, the hosts it accepts, and the API around it, which
answers as hi_api.main:app does."""

import json
import logging
from collections.abc import Callable
from contextlib import nullcontext
from typing import Any

import anyio
import httpx
import pytest
from fastapi.testclient import TestClient
from mcp.server.mcpserver import MCPServer
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.main import app as api_app
from hi_contracts.public import DatasetList
from hi_db.session import make_engine
from hi_mcp.http import MCP_PATH, build_http_server, create_app
from hi_mcp.server import DB_UNAVAILABLE, build_server
from tests.unit.mcp.test_server import NO_DATABASE, OUTPUTS, VIABILITY

LOCAL = "http://localhost:8010"
ACCEPT = {"Accept": "application/json, text/event-stream"}
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1"},
    },
}
TOOLS_LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}


def _never_connects() -> Engine:
    raise AssertionError("this tool should not open the database")


def _send(
    requests: list[tuple[str, str, dict[str, Any] | None, dict[str, str]]],
    server: MCPServer | None = None,
    base_url: str = LOCAL,
) -> list[httpx.Response]:
    """(method, path, JSON body, headers) through a fresh app, inside its lifespan."""
    app = create_app(server or build_server(_never_connects))

    async def run() -> list[httpx.Response]:
        with anyio.fail_after(30):  # a stream left open would hang the test, not fail it
            async with (
                app.router.lifespan_context(app),
                httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=base_url) as c,
            ):
                return [
                    await c.request(method, path, json=body, headers=headers)
                    for method, path, body, headers in requests
                ]

    return anyio.run(run)


def _rpc(
    body: dict[str, Any], server: MCPServer | None = None, *, headers: dict[str, str] | None = None
) -> httpx.Response:
    return _send([("POST", MCP_PATH, body, ACCEPT | (headers or {}))], server)[0]


def _call(name: str, arguments: dict[str, Any], server: MCPServer | None = None) -> dict[str, Any]:
    body = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    response = _rpc(body, server)
    assert response.status_code == 200, response.text
    return response.json()["result"]


def test_initialize_answers_json_without_a_session() -> None:
    response = _rpc(INITIALIZE)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "mcp-session-id" not in response.headers  # stateless: any instance answers the next
    result = response.json()["result"]
    assert result["serverInfo"]["name"] == "vida-facil"
    assert result["protocolVersion"] == "2025-06-18"
    assert "tools" in result["capabilities"]
    assert "No inventes cifras" in result["instructions"]


def test_tools_list_gives_the_seven_read_only_tools() -> None:
    tools = _rpc(TOOLS_LIST).json()["result"]["tools"]
    assert {tool["name"] for tool in tools} == set(OUTPUTS)
    for tool in tools:
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["destructiveHint"] is False


def test_the_viability_over_http_is_the_route() -> None:
    """A cheap call: viabilidad never opens the database (the engine factory would fail)."""
    result = _call("viabilidad", {"request": VIABILITY})
    assert result["isError"] is False
    route = TestClient(api_app).post("/api/v1/investors/viability", json=VIABILITY).json()
    assert result["structuredContent"]["data"] == route["data"]
    assert json.loads(result["content"][0]["text"]) == result["structuredContent"]


def test_a_database_that_does_not_answer_is_a_tool_error_not_a_500() -> None:
    engine = make_engine(NO_DATABASE)
    factory: Callable[[], Engine] = lambda: engine  # noqa: E731
    result = _call("que_falta", {"level": "municipio", "code": "28079"}, build_server(factory))
    assert result["isError"] is True
    assert DB_UNAVAILABLE in result["content"][0]["text"]
    assert "unit:unit" not in result["content"][0]["text"]


@pytest.mark.parametrize("host", ["vidafacil-madrid.vercel.app", "vida-facil-eight.vercel.app"])
def test_the_public_hosts_are_allowed(host: str) -> None:
    assert _rpc(TOOLS_LIST, headers={"Host": host}).status_code == 200


@pytest.mark.parametrize(
    ("headers", "status"),
    [
        ({"Host": "evil.example"}, 421),
        ({"Host": "vidafacil-madrid.vercel.app.evil.example"}, 421),
        ({"Host": "localhost"}, 421),  # the local hosts need their port, as in the SDK
        ({"Origin": "https://evil.example"}, 403),
    ],
)
def test_other_hosts_and_origins_are_refused(headers: dict[str, str], status: int) -> None:
    response = _rpc(TOOLS_LIST, headers=headers)
    assert response.status_code == status
    assert "tools" not in response.text


@pytest.mark.parametrize("method", ["GET", "DELETE"])
def test_only_post_no_stream_and_no_session_to_end(method: str) -> None:
    """In stateless mode the SDK would hold a GET open as an empty SSE stream."""
    response = _send([(method, MCP_PATH, None, ACCEPT)])[0]
    assert response.status_code == 405
    assert response.headers["allow"] == "POST"


class _NoEngine:
    def connect(self) -> nullcontext[None]:
        return nullcontext()


@pytest.fixture
def datasets_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """GET /api/v1/datasets over a stub service, in both apps (they share hi_api.main:app)."""
    listing = DatasetList(total=0, cm_open_data_count=0, datasets=[])
    monkeypatch.setattr("hi_api.routes.datasets.dataset_list", lambda _conn, cm_only: listing)
    monkeypatch.setitem(api_app.dependency_overrides, get_engine, _NoEngine)


@pytest.mark.usefixtures("datasets_without_database")
def test_the_api_routes_answer_as_before() -> None:
    """health, datasets, openapi.json (without the MCP route) and a 404, as hi_api.main:app."""
    paths = ["/api/v1/health", "/api/v1/datasets?cm_only=true", "/api/v1/openapi.json", "/nope"]
    combined = _send([("GET", path, None, {}) for path in paths])
    alone = TestClient(api_app, base_url=LOCAL)
    for path, response in zip(paths, combined, strict=True):
        before = alone.get(path)
        assert response.status_code == before.status_code, path
        assert _stable(response.json()) == _stable(before.json()), path
    assert combined[0].json()["data"] == {"status": "ok", "service": "hi-api"}
    assert combined[1].status_code == 200
    assert MCP_PATH not in combined[2].json()["paths"]


def _stable(body: dict[str, Any]) -> dict[str, Any]:
    """Without what changes on every request: the envelope's request_id and generated_at."""
    if "meta" not in body:
        return body
    meta = {k: v for k, v in body["meta"].items() if k not in ("request_id", "generated_at")}
    return body | {"meta": meta}


def test_the_api_container_keeps_its_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SDK sets the root logger up for stdio (INFO, to stderr); in the container that would
    print every API line twice. The root logger stays as it was; the tools log on their own."""
    root = logging.getLogger()
    monkeypatch.setattr(root, "handlers", [])
    monkeypatch.setattr(root, "level", logging.WARNING)
    build_http_server()
    assert root.handlers == []
    assert root.level == logging.WARNING
    tools_log = logging.getLogger("hi_mcp")
    assert tools_log.level == logging.INFO
    assert tools_log.handlers
