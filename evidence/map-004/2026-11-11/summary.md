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
