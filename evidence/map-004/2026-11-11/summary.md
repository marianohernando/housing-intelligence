# MAP-004 Fase 1 — Tokens, tipografía y armazón de Vida Fácil (2026-11-11)

Línea B (`claude/s1-web`), sobre `origin/claude/sprint-1-public` en `a338458`.

## Qué hay
- `apps/web/src/styles/tokens.css` es la fuente única de color, tipo, espacio y movimiento. Parte del brief (`prompts/DISENO_VIDA_FACIL.md`).
- Fuentes con `next/font/google`: Plus Jakarta Sans 600/700 para títulos e Inter 400/500 para texto. Base de 17 px (`font-size: 106.25%`, respeta el ajuste del navegador). Botones y pestañas de 44 px como mínimo.
- Rutas del grupo `app/(vida)/` con cabecera común: logo «Vida Fácil» y pestañas «Mapa» · «Qué falta» · «Cómo lo calculamos», sin usuario. Llevan `aria-current`, el enlace «Saltar al contenido» y foco visible de 3 px. `/map`, la vista técnica anterior, no cambia.
- Primitivas: `GlassCard` (cristal del brief) y `Button` (botón o enlace).
- `apps/web/scripts/capture.mjs`, con Playwright 1.63.0 fijado para usar el Chromium que ya está en caché. Hace capturas a 1440 y 390 px, compone la de escritorio junto al mockup y sale con error si la consola registra algún error, fallo de red o HTTP ≥ 400.

## Ajustes de color para AA (WCAG 2.2)
Los comprueba `src/lib/__tests__/tokens.test.ts`, que lee `tokens.css`. Peor caso: cristal sobre `--map-darkest`, el violeta más oscuro de la coropleta.

| Token | Brief | Ahora | Motivo |
|---|---|---|---|
| Cristal | `rgba(255,255,255,.72)` | `.82` | `--ink-soft` bajaba a 4,18:1 sobre el violeta del mapa; ahora 4,81:1 |
| Texto violeta | `--violet` | `--violet-strong` `#4B3BBF` | `--violet` sobre `--violet-soft` da 4,25:1; el nuevo, 6,59:1 |
| FALTA | `#D9485F` | `#C93A52` (icono) · `#A61E33` (texto) | 3,26:1 sobre cristal en el peor caso |
| JUSTO | `#E8A317` | `#A86A00` (icono) · `#7E4C00` (texto) | 2,17:1 sobre blanco: no valía ni para iconos |
| CUBIERTO | `#2E9E77` | `#23805F` (icono) · `#17634A` (texto) | 2,62:1 sobre cristal |
| SIN DATOS | `#8A8FA3` | `#6E7389` (icono) · `#4F546A` (texto) | 2,51:1 sobre cristal |

Cada estado tiene además un tono de fondo (`--*-bg`). El test es de 4,5:1 para texto y 3:1 para iconos, bordes y foco. Prueba de mutación: con el ámbar y el cristal originales el test falla en 3 pares.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` | 0 |
| `npm run -w apps/web typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 6 ficheros, 60 tests en verde (nuevos: `color`, `tokens`, `nav`) |
| `npm run -w apps/web build` | 0 (`/`, `/que-falta`, `/como-lo-calculamos` estáticas) |
| `make lint typecheck test-unit` | 0 (ruff, pyright, 226 pytest y 60 vitest) |
| `MOCKUP_DIR=… npm run -w apps/web capture -- --prefix f1_ …` contra `next start` en 3011 | 6 capturas sin errores ni avisos en la consola (`f1_capture.json`) |

## Capturas
- `f1_inicio_desktop_vs_mockup.jpg`: portada a 1440 px junto a `mockup_1_mapa.png`. Coinciden la cabecera, la jerarquía del titular y el cristal. Faltan el mapa, la tarjeta de búsqueda y la de zona (Fases 3 y 4).
- `f1_inicio_{desktop,mobile}.png`, `f1_que-falta_{desktop,mobile}.png` y `f1_como-lo-calculamos_{desktop,mobile}.png`.

## Limitaciones
- Todavía no hay mapa ni datos: llegan en las Fases 2 (tipos y cliente de la API) y 3 (mapa).
- El texto de «Cómo lo calculamos» recoge solo las reglas ya cerradas. Los cortes y los datasets vendrán de la API (PUB-001 Fase 1).

---

# MAP-004 Fase 2 — Tipos de contrato generados y cliente de la API (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `97b47bc`, con los contratos v2 de A (`2bcc35e`).

## Qué hay
- `apps/web/scripts/gen-contracts.mjs` (`npm run -w apps/web contracts`) genera `src/contracts/*.ts` desde `data/schemas/api/*.schema.json` con `json-schema-to-typescript` 16.0.0 (MIT, fijado). Los tipos no se escriben a mano.
- `src/lib/__tests__/contracts.test.ts` ejecuta el generador con `--check` y falla si los tipos no coinciden con los schemas. Prueba de mutación: con un tipo generado tocado, el test falla.
- `src/lib/api.ts` es el cliente tipado:
  - rutas: `zoneGaps(level, code)` (municipio, distrito o sección), `datasets({cmOnly})` (pie) y `search(scenario)` (`POST`);
  - errores: `ApiError` con `status` y `code`. El código sale de `{detail:{code,message}}`, o es `VALIDATION` (422 de FastAPI), `HTTP_<status>` o `NETWORK` (API caída), que no se confunde con «sin datos».
- `vitest.config.ts` tiene el mismo alias `@/` que el tsconfig.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` | 0, sin avisos |
| `npm run -w apps/web typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 8 ficheros, 69 tests en verde (nuevos: `api` con 8 y `contracts` con 1) |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 (233 pytest y 69 vitest) |

## Contra la API real
API de la línea B en 8011 (`CORS_ORIGINS='["http://localhost:3011"]' uv run uvicorn hi_api.main:app --port 8011`), base local `housing`:
- Preflight CORS desde `http://localhost:3011` para `POST /api/v1/search`: `200`, `allow-methods: GET, POST`.
- `f2_api_client_live.txt`: salida del cliente tipado contra la API (prueba temporal, no queda en la suite porque usa red):
  - `/datasets?cm_only=true`: 21 datasets CM.
  - `/gaps/municipio/28079` (Madrid): colegio y centro de salud FALTA.
  - `/gaps/municipio/28092` (Móstoles): colegio CUBIERTO y centro de salud FALTA.
  - `/gaps/distrito/2807905` (Chamartín): la zona existe y aún no tiene filas, con el aviso «No indicators computed at this level yet». Llegan con DATA-012 (línea A).
  - Una zona inexistente da `ApiError 404 NOT_FOUND`. `POST /search` da 404: la ruta está prevista para el 15 nov. Con la API caída: `ApiError 0 NETWORK`.

Esta fase no cambia ninguna pantalla: las capturas de la Fase 1 siguen vigentes.

## Notas para A (en el PR)
- Los schemas se exportan en modo validación, así que en los tipos de respuesta los campos con valor por defecto salen opcionales (`near_misses?`, `warnings?`, `meta?`). La web los trata con `?? []`. Si se exportaran en modo serialización, saldrían obligatorios.
- La API devuelve el nombre «Mostoles» sin tilde: viene así de la fuente.
