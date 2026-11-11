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

---

# MAP-004 Fase 3 — Mapa 2D de la región y 3D de zona (2026-11-11)

## Qué hay
- **Mapa persistente** en el grupo `(vida)/(mapa)`. La portada y `/zona/[level]/[code]` comparten la misma instancia de MapLibre 6.11.2, así que la cámara vuela de la vista general a la zona sin recargar.
- **Teselas:** OpenFreeMap (`https://tiles.openfreemap.org/planet`), esquema OpenMapTiles, sin clave.
  - Uso gratuito, también comercial, sin límite de peticiones; solo se prohíbe la descarga masiva.
  - Atribución en el mapa: «OpenFreeMap © OpenMapTiles Data from OpenStreetMap» (viene del TileJSON), seguida de «Comunidad de Madrid · Powered by CRTM».
- **Estilo propio** (`src/lib/map/style.ts`): suelo lavanda, carreteras blancas, parques y agua suaves, sin etiquetas (no hace falta servidor de glifos). Los colores salen de `tokens.css` (`--map-*`). El test lo valida con el validador oficial `@maplibre/maplibre-gl-style-spec`.
- **Vista general:**
  - 179 municipios, con Madrid capital partido en sus 21 distritos (`buildZoneCollection`, D-200).
  - Coropleta neutra hasta que exista el buscador: no se inventa ningún encaje.
  - Lo que queda fuera de la Comunidad se atenúa; al pasar el ratón se resalta la zona y al pulsar se entra en ella.
- **Zona:**
  - **Vuelo:** 2,8 s, inclinación de 55° (45° en móvil) y giro lento de 15° en 18 s. Con `prefers-reduced-motion`, MapLibre salta sin animar y no hay giro.
  - **Contorno:** violeta con brillo; el exterior se atenúa con una máscara blanca pintada encima de los edificios.
  - **Edificios:** extruidos con su altura ×2 (vista estilizada; la altura no se muestra como dato).
  - **Puntos clave:** etiquetas de cristal con datos reales de `/api/v1/places`, dentro de la zona según su sección censal. Hay una estación (Cercanías antes que metro), un centro de salud y un colegio público, repartidos para que no se tapen. Las farmacias, las paradas de autobús y los colegios privados quedan fuera.
- **Pantalla de zona** con las migas «Madrid › Chamartín» o «Comunidad de Madrid › Móstoles», el título y «Volver al mapa de la región». Textos de `pitch/textos_web.md` (línea D).
- **Velo de lectura** detrás del texto (arriba a la izquierda; en móvil, de arriba abajo) para leerlo sobre el 3D.

## Hallazgos técnicos (comprobados)
- OpenFreeMap solo trae `render_height` en las teselas de zoom 14. En las de 13, los edificios llegan fusionados y sin altura: tesela 13/4012/3087 con 1 polígono; tesela 14/8024/6175 con 55 y todas con altura. Por eso la cámara lleva las zonas del tamaño de un distrito a zoom 14 (`zoneZoom`, con test). Los municipios grandes conservan su encuadre en 2D.
- A zoom 14 los edificios vienen agrupados por altura en multipolígonos que cruzan el límite de la zona. Separarlos dentro y fuera con `distance` no es fiable, así que se usa una máscara 2D encima. `within` solo admite puntos y líneas.
- Las teselas que MapLibre cancela durante el vuelo (`net::ERR_ABORTED`) no son errores: el script de capturas ya no las cuenta.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` | 0, sin avisos |
| `npm run -w apps/web typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 13 ficheros, 106 tests (nuevos: `names`, `zones`, `places`, `style` y `camera`, más 2 de `api`) |
| `npm run -w apps/web build` | 0 (`NEXT_PUBLIC_API_URL=http://localhost:8011`) |
| `make lint typecheck test-unit` | 0 (233 pytest y 106 vitest) |
| `npm run -w apps/web capture -- --prefix f3_ --wait 8000 …` | 6 capturas sin errores en la consola (`f3_capture.json`) |

## Capturas
- `f3_inicio_desktop_vs_mockup.jpg`: región por municipios y distritos frente a `mockup_1_mapa.png`. Faltan la tarjeta «Tu búsqueda», la de zona y la leyenda (Fase 4).
- `f3_chamartin_desktop_vs_mockup.jpg`: Chamartín en 3D frente a `mockup_2_detalle.png`. Se ven edificios con altura (las torres de Castellana y Plaza de Castilla), parques, contorno, exterior atenuado y 4 puntos clave reales. Faltan las tarjetas de cristal y la barra de barrios (Fase 4).
- `f3_chamartin_mobile.png`: en móvil la zona entera, con menos inclinación y etiquetas compactas.
- `f3_mostoles_{desktop,mobile}.png`: una zona de nivel municipio.
- `f3_inicio_mobile.png`: el contenido tapa el mapa; lo resuelve la hoja inferior (Fase 5).

## Limitaciones y pendientes
- **No se ha medido el rendimiento:** Playwright usa SwiftShader, un renderizador por software, así que esas cifras no valen como fps reales. Queda medirlo en un navegador real.
- **El distrito no cabe entero en pantalla a zoom 14:** la parte más ancha queda bajo las tarjetas de cristal, que dejan ver el mapa. Es un compromiso entre ver el distrito completo y ver los edificios en 3D.
- **Peticiones a la línea A:**
  - `/api/v1/places` corta en 10.000 lugares (transporte tiene 14.982) y no filtra por zona, así que la web descarga unos 2 MB.
  - `/geo/admin-units` devuelve los municipios en mayúsculas y no filtra por `parent`. La web aplica `displayName`, una réplica de `hi_domain.geo.names` con los mismos casos de test.

---

# MAP-004 Fase 4a — Estado de la búsqueda y tarjeta «Tu búsqueda» (2026-11-11)

## Qué hay
- **`src/lib/scenario.ts`:** el único `ScenarioState` (tipo generado del contrato v2).
  - Hogar: adultos 1 o 2, hijos de 0 a 8 y mayores a cargo de 0 a 4. Al cambiar el número de hijos se borran sus edades.
  - Prioridades en el orden en que se marcan; la primera cuenta más.
  - Presupuesto de alquiler (300–5.000 €/mes) o compra (50.000–2.000.000 €), dentro de los rangos del contrato.
  - `encodeScenario` y `decodeScenario` en base64url para compartir un enlace y precargar el caso demo (Fase 10).
- **`ScenarioProvider`** en el layout del mapa: un estado compartido por la portada y la zona, con la llamada a `POST /api/v1/search`. Hasta el 15 nov la ruta no existe y se muestra «Algo ha fallado por nuestra parte…».
- **Tarjeta «Tu búsqueda»** con los textos de `pitch/textos_web.md`:
  - Tu hogar: chips con icono, contadores con «Quitar uno» y «Añadir uno», y el valor anunciado (`aria-live`).
  - Me importa: Transporte, Salud y Colegios, con el número de orden. Zonas verdes, seguridad y sin escaleras salen como «Muy pronto» en una sola línea, en vez de como chips desactivados.
  - Trabajo en: solo el campo; el autocompletado llega en la Fase 9.
  - Presupuesto: Alquilar o Comprar (radios nativos) y una barra con «Hasta 1.200 € al mes». En compra se añade la etiqueta «Orientativo».
  - Botón «Ver zonas que encajan».
  - En la pantalla de zona la tarjeta es plegable («Ver mi búsqueda» / «Ocultar mi búsqueda») y muestra un resumen («1 persona en casa · …»).
- **Primitivas nuevas:** `Chip` (`aria-pressed`, 44 px), `Counter` y `Segmented`.
- **`formatEuros`:** «1.200 €». `es-ES` no agrupa los números de 4 cifras, así que se fuerza.
- **`errorMessage`:** los textos `error.*` en lenguaje llano; un fallo de red se distingue de uno del servidor.
- **Token `--control-border`:** borde de los campos de texto, con 3:1 frente al blanco comprobado en `tokens.test.ts`.

## Gate
- `npm run -w apps/web` lint, typecheck, test y build: 0, con 16 ficheros y 123 tests (nuevos: `scenario` 12, `format` 1, `errors` 3 y un par de contraste más).
- `make lint typecheck test-unit`: 0, con 257 pytest.
- Capturas `f4a_*` sin errores en la consola.

## Pendiente (Fase 4b y pulido)
- Tarjeta de zona con «Qué falta aquí» real, leyenda «Encaje con tu búsqueda» y seleccionar en el mapa sin salir de la vista.
- A 1440×900 la tarjeta de búsqueda obliga a desplazarse un poco para llegar al presupuesto y al botón.
- En el titular de la portada, «en Madrid» se parte entre líneas.

---

# MAP-004 Fase 4b — Tarjeta de zona, «Qué falta aquí» real, leyenda y selección (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `83c74dd`: `/gaps/distrito` ya da filas reales en los 21 distritos.

## Qué hay
- **`ZoneCard`**, la tarjeta de zona de los mockups:
  - antetítulo «Distrito de Madrid» o «Municipio» y el nombre;
  - un chip «{pct} % de encaje» que solo aparece cuando la búsqueda devuelve `match_pct`: nunca «/100» ni barras, y nunca un % inventado;
  - **«Qué falta aquí»** con `/api/v1/gaps/{level}/{code}`: hasta 3 filas, lo que falta primero (`topRows`), cada una con su icono y su texto (FALTA, JUSTO, CUBIERTO o SIN DATOS; este último con borde discontinuo);
  - mientras carga, «Calculando qué falta en {zona}…»; si falla, el error en llano con «Reintentar»; si no hay filas, «Estamos calculando el resto…»;
  - en la vista general, botón «Ver la zona»; en la pantalla de zona, «Ver todo lo que falta» (abre la pestaña de la Fase 8).
- **Selección en la vista general:** al pulsar una zona se resalta su contorno y su tarjeta aparece a la derecha, en lugar de «Así funciona», con un botón para cerrarla. En la pantalla de zona, pulsar una zona vecina lleva a ella.
- **Leyenda «Encaje con tu búsqueda»:** escala de `--violet-soft` a `--violet`, «Encaja menos» y «Encaja más», «Sin datos» con borde discontinuo y, antes de la primera búsqueda, «Haz tu búsqueda para ver qué zonas encajan contigo.». En móvil se oculta hasta la Fase 5.
- **Pantalla de zona** con las tres columnas del mockup 2: introducción y «Tu búsqueda» plegable a la izquierda, el 3D en el centro y la tarjeta de zona a la derecha.
- **`lib/gaps.ts`** (con tests): textos y ayudas de los estados (`estado.*` de D), orden de las filas y detección del aviso real de la API («No indicators computed at this level yet»).
- En la portada, «en Madrid» ya no se parte entre líneas.

## Datos reales en las capturas
- Chamartín (`/gaps/distrito/2807905`): Colegios **FALTA** y Centros de salud **FALTA**.
- Alcobendas (`f4b_seleccion_desktop.png`, seleccionada pulsando en el mapa): Colegios **FALTA** y Centros de salud **JUSTO**.
- Móstoles: Colegios **CUBIERTO** y Centros de salud **FALTA**.

## Gate
- `npm run -w apps/web` lint, typecheck, test y build: 0, con 17 ficheros y 126 tests.
- `make lint typecheck test-unit`: 0, con 257 pytest.
- Capturas `f4b_*` (6) más `f4b_seleccion_desktop.png`, sin errores en la consola.

## Checkpoint del 12 nov
Cumplido:
- 3D de zona con un distrito real: vuelo, edificios y contorno;
- tarjetas de cristal en las dos pantallas;
- capturas junto a los mockups (`f4b_chamartin_desktop_vs_mockup.jpg`, `f4b_inicio_desktop_vs_mockup.jpg`).

## Para A
- `31_public_api_routes.md` dice que las filas aún no calculadas se avisan en `warnings`. En el código (`services/gaps.py`, línea 206), si faltan solo algunas filas no hay aviso; solo lo hay cuando no hay ninguna.
