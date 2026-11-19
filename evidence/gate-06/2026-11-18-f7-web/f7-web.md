# F7: deuda menor de las revisiones de la claridad en el móvil (18 nov)

Rama `claude/f7-web-debt`, desde `2dccc2d`. Deuda que dejaron las revisiones de D-244 y D-245 (#79, #81, #82 y #85). Decisión: D-245 §13. Textos: `pitch/textos_web.md` («Deuda menor…»). Solo la web, sus scripts, los textos y `scripts/redact_paths.py`: ni el contrato, ni la fórmula, ni la API cambian.

**Cómo se ha medido.** Un solo `npm ci` y un solo `npm run build` (`NEXT_PUBLIC_API_URL=http://localhost:8091`, `NEXT_PUBLIC_FEATURE_SEARCH=true`), con `next start` en el 3091, contra la API de la rama en el 8091 sobre la base local `housing` en solo lectura (`default_transaction_read_only=on`). El build terminó de compilar y escribir `.next` (con su `BUILD_ID`), y después `next build` salió con código 1 por un aviso de seguridad de la versión de Next.js; se ha usado ese build, sin repetirlo.

## Qué cambia

- **Un minuto, en singular:** «Tarda 1 min más de lo que pides», «Colegio con primaria: 1 min más andando de lo que pides» y «Aparcamiento público a 1 min andando»; nunca «unos 1 min» (tests en `shortfall.test.ts` y `environment.test.ts`). El e2e (`nearMissLine`) ya no acepta «unos 1 min» ni «unos 0 min».
- **«Somos mayores» con «Solo/a»** (`01-mayor-solo-*.png`): «¿Cerca de dónde quieres vivir?», «Donde vivo ahora» / «Cerca de mi familia», «¿Dónde vives ahora?» y, con el sitio elegido, «Donde vivo ahora: Ciudad Lineal (metro)». La búsqueda envía el lugar como «donde vivo ahora» y los trayectos de la API vuelven con esas palabras («… hasta donde vivo ahora»). Al pasar a «En pareja», la pregunta y el lugar pasan a «queréis» y «Donde vivimos ahora» (`02-mayores-pareja-*.png`). `capturas-f7.json`: 18/18 a 390 y 1440 px, axe 0, sin errores de consola.
- **Panel de un barrio (R-06 del #82)** (`qa/barrios_panel_*.png`, `qa/barrios_un_panel_*.png`): con los contornos retenidos, la 1.ª fila abre su panel (`aria-expanded`); al llegar los contornos sigue abierto; al pulsar otro barrio en la lista y otro con «Ir a un barrio» queda un solo panel; con el panel abierto, el nombre del botón ya no dice «empata con…» (lo dice el panel). El comentario de `BarrioFit.module.css` dice lo que hace la fila.
- **«Cómo lo calculamos»** (`03-como-lo-calculamos-empate-*.png`): el empate está en «Ver más sobre…» de la tarjeta («Igual de buena que Latina (94 %)»), no en la lista.
- **Código sin uso:** `ZonePrice.long` y `ZonePrice.area`; tsc y eslint limpios sin ellos.
- **Privacidad:** `scripts/redact_paths.py` cambia un slug de proyecto por `<project-slug>` (con test; un fichero de prueba con un slug hace fallar `test_no_tracked_file_has_a_local_path`), y `CLAUDE.md` §18 explica los marcadores.
- **README**, paso 2: «Mira las zonas que te convienen», con su precio y su valoración en palabras.

## Letra, botones y axe

`apps/web/scripts/check-ux-mobile.mjs --widths 390 --counts ""` (`tamanos-f7.json`): **0 textos de menos de 16 px y 0 objetivos de menos de 44 px** en las 12 pantallas a 390 px (los 3 controles del mapa, aparte, como siempre). **axe: 0 incidencias** a 390 y a 1440 px.

## e2e, golden, check-qa y tests

- `infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3091`: **escritorio 1440 px 116/116, móvil 390 px 92/92** (`e2e/`).
- `scripts/golden_search.py` contra `housing` en solo lectura: **10 de 10** (`golden.txt`).
- `apps/web/scripts/check-qa.mjs`, ahora con `--base`/`--api` (o `QA_BASE_URL`/`QA_API_URL`): **`barrios` y `compra` sin fallos** (`qa/`; `barrios` toma Puente de Vallecas, el primer distrito del ejemplo; LCP de la zona en el móvil con Slow 4G 2,4 s). También pasan `iconos`, `fuentes`, `esquema` y `pequenas`. Fallan `licencias` (espera otra forma de la línea de atribuciones), `seguridad` y `parques` (botones de antes de la entrega 1): no son de este PR.
- `make lint typecheck test-unit` (`gate_make.txt`): ruff, pyright, eslint y tsc limpios; Python 1036 y vitest 573.
