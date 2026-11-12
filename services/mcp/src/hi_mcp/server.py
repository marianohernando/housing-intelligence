"""Vida Fácil MCP server (MCP-001, D-225): five read-only tools over the domain services.

Local only, by stdio, for the demo and the jury: `make mcp` or `uv run hi-mcp`. DATABASE_URL
picks the database (the local one by default, as the API). Every tool reads through a
read-only transaction and calls the same service as its API route; there is no SQL tool
(CLAUDE.md §3). Usage and a client configuration: docs/04_technical_architecture/32_mcp_server.md.
"""

import json
import logging
import time
from collections.abc import Callable
from functools import partial
from importlib.metadata import version
from typing import Annotated, Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import BaseModel, Field
from sqlalchemy import Connection, Engine
from sqlalchemy.exc import OperationalError

from hi_api.deps import get_engine
from hi_api.services.explanation import ZoneNotInSearchError
from hi_api.services.gaps import ZoneNotFoundError
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import (
    DatasetListResponse,
    SearchResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)
from hi_mcp import tools

log = logging.getLogger("hi_mcp")

SERVER_NAME = "vida-facil"
DB_UNAVAILABLE = (
    "No se puede leer la base de datos de Vida Fácil. En local: `make up` (Postgres en el "
    "puerto 5440) o DATABASE_URL apuntando a una base con los datos cargados."
)
INSTRUCTIONS = """\
Vida Fácil: dónde vivir en la Comunidad de Madrid con datos abiertos oficiales (sobre todo del \
portal de la Comunidad de Madrid). Las herramientas son de solo lectura y llaman a los mismos \
servicios que la web y la API pública; no hay SQL.
Reglas al responder:
- No inventes cifras ni rellenes huecos: un valor null, SIN_DATOS o UNKNOWN es desconocido, \
nunca 0 ni PASS. Dilo con la razón (null_reason) si la hay.
- match_pct es el % de encaje con lo que la persona pide, no una nota de la zona.
- Da la confianza (confidence) cuando sea baja y cita las fuentes con su attribution_text.
- Los avisos de warnings son parte de la respuesta.
Flujo: encontrar_zona da el nivel y el código INE de un municipio o distrito de Madrid; con \
ellos, que_falta (lo que falta frente a municipios parecidos) y explicar_zona (hechos e \
indicadores con sus fuentes). buscar_zonas ordena las zonas para un ScenarioState (presupuesto, \
hogar, trabajo, servicios cerca y prioridades). fuentes_de_datos lista los datasets."""

READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)
ZoneCode = Annotated[
    str,
    Field(
        pattern=r"^28\d{3}(\d{2}(\d{3})?)?$",
        description="Código INE: municipio (28079), distrito de Madrid (2807905) o sección "
        "censal (2807905001). encontrar_zona lo da a partir del nombre",
    ),
]
GapLevel = Literal["municipio", "distrito", "seccion_censal"]
SearchLevel = Literal["municipio", "distrito"]
ToolFn = Callable[..., Any]


def reply(response: BaseModel) -> CallToolResult:
    """Structured content for programs and the same JSON, compact, as text for the model."""
    payload = response.model_dump(mode="json", by_alias=True)
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return CallToolResult(content=[TextContent(type="text", text=text)], structured_content=payload)


def run_tool(tool: str, engine: Engine, work: Callable[[Connection], BaseModel]) -> CallToolResult:
    """Run one tool in a read-only transaction; anticipated failures become tool errors the
    agent can read (the API answers them with 404)."""
    started = time.perf_counter()
    try:
        with engine.connect() as conn:
            response = work(conn.execution_options(postgresql_readonly=True))
    except OperationalError as exc:
        log.warning("%s: database unavailable (%s)", tool, type(exc).__name__)
        raise ToolError(DB_UNAVAILABLE) from exc
    except (ZoneNotFoundError, ZoneNotInSearchError) as exc:
        raise ToolError(str(exc)) from exc
    log.info("%s answered in %.2f s", tool, time.perf_counter() - started)
    return reply(response)


# Title and description of each tool, as the agent reads them.
TOOL_TEXT: dict[str, tuple[str, str]] = {
    "buscar_zonas": (
        "Buscar zonas para vivir",
        "Ordena los municipios de la Comunidad de Madrid (Madrid capital por sus 21 distritos) "
        "para un ScenarioState: lo mismo que POST /api/v1/search y el buscador de la web. "
        "Devuelve las 10 mejores zonas que cumplen todas las condiciones, hasta 5 que fallan "
        "una, el Reality Check (qué añade relajar cada condición) y los datasets. Cada zona trae "
        "su % de encaje y 3-5 hechos con su confianza. include_map=true añade all_zones (las 199 "
        "zonas para pintar un mapa, la mitad de la respuesta).",
    ),
    "que_falta": (
        "Qué falta en una zona",
        "Lo que falta en una zona frente a los municipios de su mismo tipo (rural o urbano): "
        "escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda, cada fila "
        "FALTA, JUSTO, CUBIERTO o SIN_DATOS con su indicador, referencia, explicación y "
        "datasets. Lo mismo que GET /api/v1/gaps/{level}/{code}.",
    ),
    "explicar_zona": (
        "Explicar una zona con sus fuentes",
        "Una zona del buscador explicada: su % de encaje, condiciones y hechos para el escenario "
        "(los mismos que su tarjeta en buscar_zonas), todos los indicadores que lee y los "
        "datasets con el texto que pide su licencia (attribution_text) y cuántos son de la "
        "Comunidad de Madrid. Sin scenario no se pide nada (encaje 100 %, como en el buscador) "
        "y los hechos son los minutos a pie a los servicios. Solo municipios y distritos de "
        "Madrid (Madrid capital va por distritos).",
    ),
    "encontrar_zona": (
        "Encontrar una zona por su nombre",
        "Municipios y distritos de Madrid capital cuyo nombre oficial coincide con el texto "
        "(sin importar mayúsculas ni tildes), el más parecido primero, con el nivel y el código "
        "INE que piden que_falta y explicar_zona.",
    ),
    "fuentes_de_datos": (
        "Fuentes de datos",
        "Los datasets con una versión válida detrás del producto: editor, licencia, versión, "
        "enlace, attribution_text y si son del portal de datos abiertos de la Comunidad de "
        "Madrid. Lo mismo que GET /api/v1/datasets; cm_only=true deja solo los de la CM.",
    ),
}


def build_server(engine: Callable[[], Engine] = get_engine) -> MCPServer:
    server = MCPServer(
        SERVER_NAME,
        title="Vida Fácil",
        instructions=INSTRUCTIONS,
        version=version("hi-mcp"),
        log_level="INFO",  # stderr: stdout carries the protocol
    )

    def register(name: str) -> Callable[[ToolFn], ToolFn]:
        title, description = TOOL_TEXT[name]
        return server.tool(name=name, title=title, description=description, annotations=READ_ONLY)

    @register("buscar_zonas")
    def buscar_zonas(
        scenario: ScenarioState, include_map: bool = False
    ) -> Annotated[CallToolResult, SearchResponse]:
        work = partial(tools.search_zones, scenario=scenario, include_map=include_map)
        return run_tool("buscar_zonas", engine(), work)

    @register("que_falta")
    def que_falta(
        level: GapLevel, code: ZoneCode
    ) -> Annotated[CallToolResult, ZoneGapListResponse]:
        work = partial(tools.zone_gaps, level=TerritoryLevel(level), code=code)
        return run_tool("que_falta", engine(), work)

    @register("explicar_zona")
    def explicar_zona(
        level: SearchLevel, code: ZoneCode, scenario: ScenarioState | None = None
    ) -> Annotated[CallToolResult, ZoneExplanationResponse]:
        work = partial(
            tools.zone_explanation,
            level=TerritoryLevel(level),
            code=code,
            scenario=scenario or ScenarioState(),
        )
        return run_tool("explicar_zona", engine(), work)

    @register("encontrar_zona")
    def encontrar_zona(
        name: Annotated[str, Field(min_length=2, max_length=80, examples=["Chamartín"])],
    ) -> Annotated[CallToolResult, ZoneLookupResponse]:
        return run_tool("encontrar_zona", engine(), partial(tools.zone_lookup, name=name))

    @register("fuentes_de_datos")
    def fuentes_de_datos(cm_only: bool = False) -> Annotated[CallToolResult, DatasetListResponse]:
        return run_tool("fuentes_de_datos", engine(), partial(tools.datasets, cm_only=cm_only))

    return server


def main() -> None:
    """Serve over stdio (stdout carries the protocol; logs go to stderr)."""
    build_server().run("stdio")


if __name__ == "__main__":
    main()
