"""Smoke test of the MCP server as a client sees it (MCP-001): launch it over stdio, list the
tools and ask the demo questions against DATABASE_URL (the local database by default).

Usage: uv run python scripts/mcp_smoke.py
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

import anyio
from mcp import Client, StdioServerParameters
from mcp.types import CallToolResult

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "contracts"


def _family() -> dict[str, Any]:
    """The demo case of the pitch, with the place of work as a preference."""
    scenario = json.loads((FIXTURES / "scenario_state.familia_castellana.fixture.json").read_text())
    for anchor in scenario["anchors"]:
        anchor["max_minutes"] = None
    return scenario


def _summary(name: str, data: dict[str, Any]) -> str:
    if name == "encontrar_zona":
        return ", ".join(f"{z['name']} ({z['level']} {z['code']})" for z in data["zones"])
    if name == "que_falta":
        return ", ".join(f"{r['row']} {r['status']}" for r in data["rows"])
    if name == "explicar_zona":
        facts = " | ".join(f["text"] for f in data["facts"])
        return (
            f"{data['zone']['name']}: encaje {data['match_pct']} %, {len(data['indicators'])} "
            f"indicadores, {len(data['datasets'])} datasets ({data['cm_open_data_count']} CM). "
            f"Hechos: {facts}"
        )
    if name == "buscar_zonas":
        top = ", ".join(f"{z['zone']['name']} {z['match_pct']} %" for z in data["results"][:3])
        check = data["reality_check"]
        return (
            f"{check['zones_passing']} de {check['zones_evaluated']} zonas cumplen todo; "
            f"primeras: {top}; {len(data['datasets'])} datasets"
        )
    return f"{data['total']} datasets, {data['cm_open_data_count']} del portal de la CM"


CALLS: list[tuple[str, dict[str, Any]]] = [
    ("encontrar_zona", {"name": "chamartin"}),
    ("que_falta", {"level": "distrito", "code": "2807905"}),
    ("explicar_zona", {"level": "distrito", "code": "2807905"}),
    ("buscar_zonas", {"scenario": _family()}),
    ("fuentes_de_datos", {"cm_only": False}),
    ("explicar_zona", {"level": "municipio", "code": "28079"}),
]


def _line(name: str, result: CallToolResult, seconds: float) -> str:
    block = result.content[0]
    text = block.text if block.type == "text" else ""
    if result.is_error:
        return f"- {name}: error legible ({seconds:.2f} s): {text}"
    content = result.structured_content or {}
    kb = len(text.encode()) / 1024
    warnings = len(content.get("warnings", []))
    return (
        f"- {name}: {seconds:.2f} s, {kb:.1f} KB, {warnings} avisos, método "
        f"{content['meta']['methodology_version']}: {_summary(name, content['data'])}"
    )


async def main() -> int:
    params = StdioServerParameters(command=sys.executable, args=["-m", "hi_mcp.server"])
    async with Client(params) as client:
        tools = (await client.list_tools()).tools
        print(f"Servidor {client.server_info.name if client.server_info else '?'} por stdio")
        print("Herramientas:", ", ".join(t.name for t in tools))
        read_only = all(t.annotations and t.annotations.read_only_hint for t in tools)
        print("Todas de solo lectura:", read_only)
        for name, arguments in CALLS:
            started = time.perf_counter()
            result = await client.call_tool(name, arguments)
            print(_line(name, result, time.perf_counter() - started))
    return 0


if __name__ == "__main__":
    sys.exit(anyio.run(main))
