"""The MCP server over Streamable HTTP, beside the public API (D-255).

`uvicorn hi_mcp.http:app` (the API container, infra/deploy/api/Dockerfile) serves the API exactly
as `hi_api.main:app`, mounted unchanged, plus one route: the seven read-only tools of server.py at
/api/v1/mcp, since vercel.json only sends /api/v1/* to the container. So the URL an MCP client adds
is https://vidafacil-madrid.vercel.app/api/v1/mcp. The tools call the same services as the routes,
with the same engine and the same read-only database role (DATABASE_URL); none reaches the
Catastro or another upstream (the parcel search, and its guard, stay in the API).

- Stateless, with JSON answers: the platform may send each POST to another instance, so there is
  no session to keep (no Mcp-Session-Id) and no SSE stream. Only POST: a GET (the stream) or a
  DELETE (the end of a session) is a 405, the spec's answer when the server offers neither.
- The SDK's DNS-rebinding protection stays on, with our hosts: another Host header is a 421, and
  an Origin header from elsewhere a 403 (MCP_ALLOWED_HOSTS and MCP_ALLOWED_ORIGINS change them).
- No authentication: public data, read-only, as the API.

Usage and client configuration: docs/04_technical_architecture/32_mcp_server.md.
"""

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route
from starlette.types import ASGIApp, Receive, Scope, Send

from hi_api.logs import FORMAT
from hi_api.main import app as api_app
from hi_mcp.server import build_server

MCP_PATH = "/api/v1/mcp"
PUBLIC_HOSTS = ("vidafacil-madrid.vercel.app", "vida-facil-eight.vercel.app")
LOCAL_HOSTS = ("127.0.0.1:*", "localhost:*", "[::1]:*")  # the SDK's own, for local runs and tests
# Our web, the client the jury is most likely to use, and localhost. A request without Origin
# (curl, server-side clients, mcp-remote) is not checked.
ORIGINS = (
    *(f"https://{host}" for host in PUBLIC_HOSTS),
    "https://claude.ai",
    "https://claude.com",
    *(f"http://{host}" for host in LOCAL_HOSTS),
)


class HttpSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_", env_file=None, extra="ignore")

    allowed_hosts: list[str] = [*PUBLIC_HOSTS, *LOCAL_HOSTS]
    allowed_origins: list[str] = list(ORIGINS)


def transport_security(settings: HttpSettings) -> TransportSecuritySettings:
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=settings.allowed_hosts,
        allowed_origins=settings.allowed_origins,
    )


class PostOnly:
    """In stateless mode the SDK still answers a GET with an SSE stream that stays open, with
    nothing to send, until the client or the platform drops it."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] != "POST":
            response = PlainTextResponse("Method Not Allowed", 405, headers={"Allow": "POST"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def build_http_server() -> MCPServer:
    """build_server() without the logging the SDK sets up for stdio (the root logger at INFO,
    to stderr): in the API container it would print every API line twice and library lines
    that are dropped today. The tools' own lines (name and time, never the arguments) go to
    stdout, as the API's do (hi_api.logs)."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    server = build_server()
    root.handlers[:] = handlers
    root.setLevel(level)
    log = logging.getLogger("hi_mcp")
    log.setLevel(logging.INFO)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(FORMAT))
        log.addHandler(handler)
    return server


def create_app(server: MCPServer | None = None, api: FastAPI = api_app) -> Starlette:
    """The API, unchanged, and the MCP route in front of it. Each call builds its own session
    manager, which runs once: inside this app's lifespan, around the API's own."""
    server = server or build_http_server()
    # Sets up the session manager; the app it returns is one Route, rebuilt here behind PostOnly
    server.streamable_http_app(
        streamable_http_path=MCP_PATH,
        stateless_http=True,
        json_response=True,
        transport_security=transport_security(HttpSettings()),
    )
    mcp = Route(MCP_PATH, endpoint=PostOnly(server.session_manager.handle_request))

    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        # A mounted app's lifespan does not run by itself (the API keeps no lifespan state)
        async with api.router.lifespan_context(api), server.session_manager.run():
            yield

    # A Route, not a Mount: /api/v1/mcp without a redirect to /api/v1/mcp/
    return Starlette(routes=[mcp, Mount("", app=api)], lifespan=lifespan)


app = create_app()
