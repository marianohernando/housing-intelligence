# Servidor MCP de Vida Fácil (MCP-001)

Servidor MCP local del producto DATA (D-225). Un agente (Claude Desktop, Claude Code o cualquier cliente MCP) pregunta a Vida Fácil lo mismo que la web y la API pública, con las mismas cifras y las mismas fuentes. Es para la demo y el jurado: **no se despliega**.

- Código: `services/mcp/src/hi_mcp/` (`server.py` registra las herramientas y `tools.py` llama a los servicios).
- Servicios: los de `apps/api/src/hi_api/services/`. Dos son nuevos, sin ruta en la API: `explanation.py` (`explicar_zona`) y `zones.py` (`encontrar_zona`).
- SDK: `mcp` 2.3.0, el SDK oficial de Python (`MCPServer`, transporte stdio), fijado en `uv.lock`.

## Reglas
- **No hay SQL libre ni acceso a tablas** (CLAUDE.md §3). Cada herramienta llama a la misma función de servicio que su ruta de la API y devuelve el mismo sobre `{data, meta, warnings}`. Las entradas tienen tipo, incluido el `ScenarioState` de la API. El único texto libre es el nombre de `encontrar_zona`, que se compara en Python con los nombres oficiales.
- **Solo lectura.** Cada llamada abre una transacción `READ ONLY` en Postgres (`postgresql_readonly` de SQLAlchemy). Si algo intentara escribir, Postgres lo rechaza; lo comprueba un test de integración. Todas las herramientas declaran `readOnlyHint: true` y `openWorldHint: false`.
- **Los huecos se dicen.** Las instrucciones del servidor le piden al agente que no invente cifras; que trate `null`, `SIN_DATOS` y `UNKNOWN` como desconocidos, nunca como 0 ni como PASS; que cite las fuentes con su `attribution_text`; y que lea los `warnings`.
- **Errores legibles.** Si la zona no existe o el buscador no la ordena, devuelve un error de herramienta con el mismo mensaje que el 404 de la API. Si la base no responde, devuelve un error sin URL ni credenciales. Una entrada inválida se rechaza antes de abrir la base.
- **Respuesta.** `structuredContent` sigue el esquema de salida, y el texto lleva el mismo JSON compacto en UTF-8, sin sangría: así ocupa menos para el modelo.

## Herramientas
| Herramienta | Entrada | Salida (esquema) | Igual que |
|---|---|---|---|
| `buscar_zonas` | `scenario`: `ScenarioState` · `include_map` (opcional, `false`) | `SearchResponse` (`data/schemas/api/search_response.schema.json`) | `POST /api/v1/search`. Sin `include_map`, `all_zones` llega vacío: son las 199 zonas de la coropleta, la mitad de la respuesta |
| `que_falta` | `level`: `municipio`, `distrito` o `seccion_censal` · `code`: código INE de la Comunidad de Madrid | `ZoneGapListResponse` | `GET /api/v1/gaps/{level}/{code}` |
| `explicar_zona` | `level`: `municipio` o `distrito` · `code` · `scenario` (opcional) | `ZoneExplanationResponse` (`data/schemas/mcp/zone_explanation_response.schema.json`) | la tarjeta de la zona en `POST /search`: el mismo `match_pct`, `confidence`, `facts`, `constraints`, `estimated_cost_eur` y `gap_highlights`. Añade `indicators` (todo lo que el buscador lee de la zona), `datasets` con `attribution_text` y `cm_open_data_count` |
| `encontrar_zona` | `name`: de 2 a 80 caracteres | `ZoneLookupResponse` (`data/schemas/mcp/zone_lookup_response.schema.json`) | los mismos `ZoneRef` que `/gaps`, para los municipios y los 21 distritos de Madrid. Ignora mayúsculas, tildes y signos y pone primero el nombre exacto, después el que empieza igual, después una palabra que empieza igual y por último el que lo contiene. Da 10 como mucho; `total` cuenta todas y, si quedan fuera, un aviso pide escribir más del nombre. Sin coincidencias no es un error: `zones: []` y un aviso `NOT_FOUND` |
| `fuentes_de_datos` | `cm_only` (opcional) | `DatasetListResponse` | `GET /api/v1/datasets` |

Notas:
- `explicar_zona` sin `scenario` usa el escenario vacío: no se pide nada, así que el encaje es 100 % (como en el buscador) y los hechos son los minutos a pie hasta el transporte, el centro de salud, el colegio y la farmacia.
- Madrid capital se ordena por distritos (D-200): `explicar_zona` con el municipio 28079 da un error que lo explica. `que_falta` sí admite Madrid entera.
- Los datasets de `explicar_zona` son los de todos sus indicadores (también los que el escenario no puntúa y los que están sin dato, porque se leen), los de las filas destacadas de «Qué falta» (tal como las cita `/gaps` para esa zona) y los GTFS de los trayectos al trabajo, si hay sitio de trabajo. Sus `warnings` son los de `/search` para el mismo escenario, salvo el recuento de zonas sin datos para puntuar, que es de la búsqueda entera.

## Arrancarlo en local
Necesita la base local con los datos cargados (`make up`; Postgres en el puerto 5440) o un `DATABASE_URL` que apunte a otra.

```bash
make mcp                 # stdio; para probarlo a mano (Ctrl-C para salir)
uv run python scripts/mcp_smoke.py   # se conecta como un cliente y hace las preguntas de la demo
```

`make mcp` no imprime nada por stdout salvo el protocolo; los registros (nivel INFO, con la duración de cada herramienta) van a stderr. Un cliente no debería lanzarlo con `make -C`, porque esa opción escribe «Entering directory» en stdout y rompe el protocolo. Mejor `uv run --directory`, como en los ejemplos.

## Configuración de un cliente MCP
**Claude Code** (desde cualquier carpeta):

```bash
claude mcp add vida-facil \
  -e DATABASE_URL=postgresql+psycopg://housing:housing@localhost:5440/housing \
  -- uv run --quiet --directory ~/Desktop/DATAMAD/housing-intelligence hi-mcp
```

**Claude Desktop** (`claude_desktop_config.json`; la ruta tiene que ser absoluta y `uv` tiene que estar en el PATH de la aplicación, o con su ruta completa):

```json
{
  "mcpServers": {
    "vida-facil": {
      "command": "uv",
      "args": ["run", "--quiet", "--directory", "/ruta/a/housing-intelligence", "hi-mcp"],
      "env": {
        "DATABASE_URL": "postgresql+psycopg://housing:housing@localhost:5440/housing"
      }
    }
  }
}
```

Es la base local de desarrollo (usuario `housing`, sin datos personales). Para la demo sin red, el paquete offline (`make demo-offline`) levanta su propia base: `DATABASE_URL=postgresql+psycopg://vidafacil:vidafacil@localhost:5441/vidafacil` (`infra/deploy/offline/compose.yml`).

## Preguntas de ejemplo para la demo
- «¿Qué le falta a Chamartín frente a otros sitios parecidos?» → `encontrar_zona` + `que_falta`.
- «Somos dos adultos y un niño de 4 años, 1.500 €/mes de alquiler y trabajo en la Castellana. ¿Dónde miramos?» → `buscar_zonas`.
- «¿Por qué Ciudad Lineal? ¿De dónde salen los datos?» → `explicar_zona` con el mismo escenario: los hechos, los indicadores y las fuentes con su atribución.
- «¿Cuántos datasets de la Comunidad de Madrid usáis?» → `fuentes_de_datos` con `cm_only`.

## Tamaño y tiempos (base local, 12 nov)
| Herramienta | Tiempo | Texto |
|---|---|---|
| `buscar_zonas` (caso demo, sin mapa) | 0,23 s | 60 KB |
| `que_falta` (un distrito) | 0,18 s | 30 KB |
| `explicar_zona` (un distrito) | 0,45 s | 18 KB |
| `encontrar_zona` | 0,16 s | menos de 1 KB |
| `fuentes_de_datos` | 0,01 s | 18 KB |

Claude Code avisa por encima de unos 10.000 tokens por resultado y corta en 25.000 (`MAX_MCP_OUTPUT_TOKENS`). `buscar_zonas` con `include_map: true` ronda los 115 KB y puede pasar de ese límite: el mapa es para programas, no para el modelo.

## Pruebas
- `tests/unit/mcp/test_server.py`, sin base ni red:
  - las 5 herramientas, de solo lectura y sin SQL libre;
  - cada esquema de salida es el del contrato de la API (o el de `data/schemas/mcp/`), y `buscar_zonas` recibe el `ScenarioState` de la API;
  - las entradas inválidas no llegan a la base;
  - la base caída da un error legible sin credenciales;
  - el texto es el `structuredContent` compacto;
  - el arranque por stdio habla el protocolo y su stdout es solo JSON-RPC;
  - `encontrar_zona` avisa cuando no encuentra nada o deja coincidencias fuera.
- `tests/integration/test_mcp_tools.py`, con la base de fixtures:
  - cada herramienta devuelve lo mismo que su ruta (`data`, `warnings` y versiones);
  - `explicar_zona` coincide con las tarjetas de `/search` (resultados y alternativas) en tres escenarios: el caso demo, el vacío y un trabajo fuera de toda zona, avisos incluidos; y cita todos los datasets de sus indicadores, con el mismo `attribution_text` que `/datasets`;
  - las zonas que no existen dan errores legibles;
  - una escritura dentro de una herramienta falla por la transacción de solo lectura.
- Evidencia: `evidence/gate-11/2026-11-12/`.

## Fuera de alcance
- No se despliega ni tiene autenticación, límites de uso ni transporte HTTP: es local, por stdio, para una persona en su ordenador (`29_api_mcp_security_rate_limits.md` aplicará si algún día se publica).
- No hay control del mapa ni capas dinámicas (CLAUDE.md §9): necesitarían que la web escuche un `MapState`.
- No hay herramientas PRO ni documentales (`03_api_openapi_mcp.md`).
