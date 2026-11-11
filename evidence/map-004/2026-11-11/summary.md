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

---

# MAP-004 Fase 4c — Pulido 3D y «Tu búsqueda» sin desplazamiento (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `ad31fc8`. Recoge las notas de datamad-10 tras comparar la F3 con el mockup 2 y un pendiente de la F4a.

## Qué hay
- **Edificios lavanda dentro y casi blancos fuera:**
  - `--map-building` pasa a `#e6e3f5`;
  - la luz se vuelve más suave (0,35) y con un tinte lavanda, para que las paredes no salgan grises;
  - la máscara blanca del exterior pasa de 0,62 a 0,78, así que los edificios de fuera quedan casi blancos y el distrito se lee como una «isla».
- **Verde:** `--map-park` pasa a `#cdebd6` y la vegetación (landcover) a 0,9 de opacidad.
- **Base extruida** (`edgeWall`, con tests): una pared lavanda de 80 m justo por fuera del contorno, con efecto de maqueta.
  - No tapa calles ni parques del interior.
  - En móvil se oculta, igual que el brillo.
- **Etiquetas:**
  - iconos reconocibles: tren, cruz (`Cross`, también en el chip «Salud») y birrete;
  - icono violeta directamente sobre el cristal, como en el mockup.
- **Mismo cristal en todas las etiquetas:**
  - en la F4b, una etiqueta quedaba bajo el velo de lectura y otra bajo la tarjeta «Tu búsqueda»;
  - el velo ya se ciñe a la columna de texto;
  - los puntos clave se eligen cuando la cámara aterriza, solo entre los que caen en el hueco libre entre tarjetas y sin solaparse (`pickKeyPoints` con `inView` y `apart`, con tests);
  - si un tipo no tiene ningún punto así, no se muestra.
- **«Tu búsqueda» cabe a 1440×900 sin desplazarse** (antes sobraban 234 px). Solo en pantallas de escritorio bajas (`min-width: 1101px` y `max-height: 960px`):
  - cabecera y héroe más compactos, y menos separación en la tarjeta;
  - las ayudas de «Tu hogar» y «Trabajo en» van en la línea de su etiqueta;
  - Alquilar/Comprar y la cifra van en una sola fila.
  
  Se mantienen todos los textos y los objetivos de 44 px. La ayuda de «Tu hogar» pasa a formar parte del `legend`. En la de «Trabajo en» solo cambia el orden visual; el DOM y `aria-describedby` no cambian.
- **`capture.mjs`** anota `overflow_px` por captura.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` | 0 |
| `npm run -w apps/web typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 17 ficheros, 135 tests (nuevos: 5 de `places`, 4 de `zones`) |
| `npm run -w apps/web build` | 0 (`NEXT_PUBLIC_API_URL=http://localhost:8011`) |
| `make lint typecheck test-unit` | 0 (266 pytest, 135 vitest) |
| `npm run -w apps/web capture -- --prefix f4c_ --wait 7000 …` | 6 capturas sin errores en la consola (`f4c_capture.json`) |

## Capturas
- `f4c_chamartin_desktop_vs_mockup.jpg`: Chamartín frente al mockup 2.
  - Se ven los edificios lavanda, los parques más verdes, el exterior lavado y el borde elevado.
  - Hay cuatro etiquetas nítidas (Estación, Centro de salud, Metro y Colegio), todas en el hueco libre.
- `f4c_inicio_desktop_vs_mockup.jpg`: la portada con «Tu búsqueda» entera, botón incluido; `overflow_px: 0` a 1440×900.
- `f4c_mostoles_desktop.png`: un municipio grande en 2,5D. Salen dos etiquetas: las demás caerían bajo las tarjetas o encima de otra.
- En móvil la página se sigue desplazando (`overflow_px` de 161 a 834): lo resuelve la hoja inferior de la F5.

## Pendiente
- **F5:** hoja inferior en móvil, donde ahora el contenido tapa el mapa.
- **F8:** pintar como SIN DATOS las filas de `/gaps` con aviso `INSUFFICIENT_DATA: row … not computed at … level yet` (A, `d3127d3`), en la tarjeta de zona y en «Qué falta».
- **Nombres sin tilde:** el municipio se muestra «Mostoles» porque `/geo/admin-units` lo devuelve en mayúsculas y sin tilde («MOSTOLES»). `displayName` no puede reponer tildes que no vienen en el dato.

---

# MAP-004 Fase 5 — Hoja inferior en móvil (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `6d02abb` (con `d3127d3` y `d7037b7` de A).

## Qué hay
- **`MapSheet`**: en móvil (≤ 760 px) todo el contenido va en una hoja inferior y el mapa queda a la vista.
  - Plegada ocupa el 45 % de la pantalla (`SHEET_PEEK`); abierta llega justo debajo de la cabecera, que sigue usable.
  - El tirador es un botón de verdad, con `aria-expanded` y `aria-controls`: se maneja tocando, con Intro o Espacio, y también deslizando hacia arriba o hacia abajo.
  - Texto: «Desliza hacia arriba para ver más» (`movil.hoja.tirador`). Abierta dice «Ver el mapa», provisional y pendiente de D.
  - Sin `transform` ni `backdrop-filter` en la hoja, para que los hijos fijos (la leyenda) se sigan colocando respecto a la pantalla.
  - En escritorio no se dibuja: `display: contents`.
- **`cameraPadding`** (pura, con tests): en móvil, la cámara encuadra entre la cabecera y la hoja plegada. Las etiquetas de los puntos clave usan ese mismo hueco.
- **Leyenda en móvil:**
  - va compacta, justo encima de la hoja, y se oculta al abrirla;
  - antes de la primera búsqueda solo muestra «Haz tu búsqueda para ver qué zonas encajan contigo.», porque la escala aún no significa nada;
  - el título se mantiene accesible.
- **Pantalla de zona:** la tarjeta de zona («Qué falta aquí») va delante de «Tu búsqueda» en el DOM, así que en móvil sale antes. En escritorio no cambia: la columna derecha abarca dos filas.
- **Vista general en móvil:** al elegir una zona en el mapa, su tarjeta se desplaza a la vista dentro de la hoja.
- **Velo de lectura:** desaparece en móvil, porque el texto ya va sobre la hoja.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 17 ficheros, 138 tests (nuevos: 3 de `cameraPadding`) |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 (269 pytest, 138 vitest) |
| `capture -- --prefix f5_ …` | 6 capturas sin errores en la consola; `overflow_px: 0` en las seis, también en móvil (antes, de 161 a 834) |

## Hoja en móvil con Playwright (`f5_hoja_movil.json`, 390×844)
- Plegada: 380 px y `aria-expanded="false"`.
- Con Tab se llega al tirador; Intro la abre (721 px y `aria-expanded="true"`) y la leyenda se oculta.
- «Ver zonas que encajan» se alcanza dentro de la hoja abierta.
- Espacio la pliega y deslizar hacia arriba la abre.
- Sin errores en la consola. `f5_inicio_mobile_abierta.png` es la hoja abierta con el foco en el tirador.

## Pendiente
- **En móvil, Chamartín se ve en 2D:** el distrito entero cabe por debajo del zoom 14, y ahí OpenFreeMap no trae alturas. Se trata junto al encuadre «isla» que pide datamad-10, en la fase de pulido.
- **Para D:** el texto de la hoja abierta («Ver el mapa»).

---

# MAP-004 Fase 5b — API nueva de A para puntos clave y distritos (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `ec126b0` (con `d7037b7`, `12c834a` y `879101a` de A).

## Por qué
Desde `879101a`, `/places` va en páginas de 5.000. La web pedía capas enteras: de transporte solo habría llegado la página 1 (5.000 de 14.982 paradas), sin aviso, y cada zona descargaba unos 4,4 MB. Además, para usar 21 distritos se bajaban 246.

## Qué cambia
- **Puntos clave:** `api.places({ category, adminUnitId, subcategories })` pide por zona y repite `subcategory`. Si `data.pages > 1`, pide el resto de páginas en vez de cortar.
- **Qué se pide:** `keyPointQueries()` se deriva de las mismas reglas que eligen los puntos (`RULES`), así que las subcategorías siguen en un solo sitio. La caché va por zona (`admin_unit_id`).
- **Zona:** fuera `placesInZone`. A filtra en servidor con la misma regla: la sección donde cae el lugar.
- **Distritos:** `/geo/admin-units?level=distrito&parent=ES.28.MUN.28079`. `MUNICIPIOS_BY_DISTRITO` pasa a `admin_unit_id` (D-200).
- **Nombres:** fuera la réplica de `display_name`, porque la API ya da nombres legibles. `titleCase` se queda para los nombres de `/places`, que siguen en mayúsculas.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 17 ficheros, 133 tests. Nuevos: páginas de `/places`, `subcategory` repetida, `parent` (×2), `keyPointQueries` y partición por `admin_unit_id`. Fuera: 8 casos de `displayName` y 2 de `placesInZone` |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 (275 pytest, 133 vitest) |
| `capture -- --prefix f5b_ …` | 6 capturas (inicio, Chamartín y Móstoles a 1440 y 390 px), sin errores en la consola y con `overflow_px: 0` |

## Red (`f5b_red.txt`)
- **Chamartín:** los puntos clave pasan de unos 3,9 MB a 9.932 B, en 3 peticiones filtradas. La pantalla de zona entera pide 384 KB a la API.
- **Distritos:** de 537.540 B a 31.867 B.
- **Ninguna petición sin filtro** en `/`, `/zona/distrito/2807905` ni `/zona/municipio/28092`.
- **Mismos puntos clave que antes:**
  - Chamartín: Madrid-Chamartín-Clara Campoamor, Concha Espina, centro de salud y Padre Poveda (`f5b_chamartin_desktop_vs_mockup.jpg`);
  - Móstoles: Móstoles-El Soto y Hospital de Móstoles.

## Pendiente
- **`/map`:** la página heredada, que la demo no enlaza, sigue pidiendo capas enteras con su propio `fetch`. Ahora solo verá la página 1 de transporte. Fuera del alcance de la demo.
- **«Mostoles» sin tilde:** así viene en la fuente, y la API no la repone.

---

# MAP-004 Fase 5c — Encuadre «isla» y barra «Barrios de la zona» (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `fbc7e37`. Decisión de Mariano, transmitida por datamad-10: aterrizar con el distrito entero a la vista y con el borde de maqueta, y acercarse despacio hasta el 3D. Con `prefers-reduced-motion`, sin animación.

## Qué hay
- **Isla:** la cámara aterriza con la zona entera inclinada, libre de las tarjetas y de la barra. `cameraPadding("island")` deja el mismo centro que el modo zona, así que el acercamiento no desplaza la vista.
- **`projectAt` e `islandZoom`** (puras, con tests):
  - proyectan como MapLibre: campo de visión de 36,87°, cámara a 1,5 alturas de pantalla y punto de fuga en el centro del área con relleno;
  - buscan el zoom más cercano al que cabe todo el contorno. `cameraForBounds` ignora la inclinación, y el lado cercano, que se ve más grande, se salía.
- **Acercamiento:** tras 0,7 s en la isla, 4 s con aceleración suave hasta el zoom 14, donde OpenFreeMap trae alturas. Después, el giro lento de siempre.
  - Solo en distritos de hasta 10 km de diagonal (14 de 21).
  - Fuencarral-El Pardo (31 km), Moncloa-Aravaca, Villa de Vallecas, Vicálvaro, Latina, Barajas, San Blas y los municipios se quedan en la isla. Si no, la cámara aterrizaba en el monte de El Pardo, sin nada que ver.
- **Puntos clave:**
  - se eligen y se muestran al llegar al final, con la cámara final (`projectAt`). En la isla se amontonaban: en móvil está unas 6 veces más lejos;
  - los lugares se piden durante el vuelo y aparecen sin espera.
- **Móvil:** Chamartín llega ya al 3D. Era lo pendiente de la F5.
- **Barra «Barrios de la zona»** (`BarriosBar`):
  - barrios del distrito con `/geo/admin-units?level=barrio&parent=…` (6 en Chamartín);
  - chips con `aria-pressed`: «Todo {distrito}» y uno por barrio;
  - pulsar uno lleva la cámara a ese barrio (isla y acercamiento), con contorno discontinuo y las etiquetas del distrito que quedan a la vista;
  - solo navega: no hay cifras por barrio. Los municipios no la muestran;
  - en escritorio va fija abajo; en una columna o en móvil, dentro del flujo.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 17 ficheros, 145 tests. Nuevos: `projectAt` (5), `islandZoom` (4), `approachZoom` y `extentKm` (4), `outlinePoints` y la capa del barrio. Fuera: 3 de `zoneZoom` |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 (277 pytest, 145 vitest) |
| `capture -- --prefix f5c_ --wait 9500 …` | 6 capturas sin errores en la consola, con `overflow_px: 0` |

## Vuelo (`f5c_vuelo.json` y `f5c_vuelo_*`)
- **Isla y final de Chamartín** en escritorio y móvil: `f5c_vuelo_chamartin_isla_*` y `f5c_vuelo_chamartin_3d_*`.
- **Fuencarral-El Pardo:** se queda en la isla, con 2 puntos clave (`f5c_vuelo_fuencarral_isla_desktop.png`).
- **Barrio:** Tab hasta «Hispanoamérica» e Intro dejan `aria-pressed="true"`; la cámara va al barrio con 3 etiquetas (`f5c_barrio_hispanoamerica_desktop.png`).
- **`prefers-reduced-motion`:** a los 2,5 s la cámara ya está en el final, con 4 etiquetas (`f5c_sin_movimiento_desktop.png`).
- **Consola:** sin errores en ninguna ruta.

## Pendiente
- **Para D:** «Todo {distrito}» es provisional. `barrios.titulo` dice que la barra no se muestra sin datos por barrio; datamad-10 pidió una barra que solo navega. Hay que alinear la nota.
- **Para A:** nombres de municipio mal codificados en `/geo/admin-units`: «Redue/a», «Griðon», «Villanueva de la Ca/ada», «Pi/uecar-Gandullas».
- **En la isla, el móvil no muestra el borde de maqueta:** se quitó en la F5 por rendimiento.

## Revisión (agente `reviewer`, cierre de MAP-004)
- **Ningún bloqueante.** `projectAt` coincide con `Transform` de MapLibre: signo del bearing, distancia de cámara, perspectiva y padding.
- **Corregido:**
  - **Etiquetas antiguas:** al volver a una vista ya vista salían sobre la isla. Ahora exigen haber aterrizado.
  - **Foco de barrio:** se recordaba al volver al distrito. Ahora vuelve a «Todo {distrito}».
  - **Anillo de foco:** se recortaba en la lista desplazable.
  - **Barrios:** un fallo puntual al pedirlos ya no se queda guardado; se reintentan en la siguiente visita.
  - **`stop()`:** no se llama sobre un mapa ya desmontado.
  - **Barra:** deja sitio a los controles del mapa.
- **Comprobado** en `f5c_reviewer.json`: 0 etiquetas durante el vuelo de vuelta y 4 al llegar; al volver, «Todo Chamartín» queda pulsado; consola sin errores.
- **Aceptado sin cambio:**
  - si el usuario arrastra durante el vuelo, las etiquetas se calculan para la cámara prevista;
  - el giro lento final (+15°) puede llevar alguna etiqueta bajo el cristal;
  - un cambio de tamaño de la ventana no recalcula la isla.

---

# PUB-001 Fase 1 (F6) — Pie de procedencia y «Cómo lo calculamos» (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `4523d69`.

## Qué hay
- **Contador** (`DataCounter`, `pie.contador`):
  - «Datos: 21 conjuntos de la Comunidad de Madrid + Ayuntamiento de Madrid + CRTM»;
  - el número es `cm_open_data_count` de `GET /api/v1/datasets`;
  - enlaza a «Cómo lo calculamos». Mientras carga, o si falla, queda solo el enlace;
  - va en la columna derecha del mapa y de la zona, bajo «Así funciona» y la tarjeta de zona, sin desplazar «Tu búsqueda» a 1440×900.
- **Petición única:** `useDatasets` comparte una sola llamada a `/datasets` entre el contador, la lista y el número de la página.
- **Pie de las páginas sin mapa** (`SiteFooter`, sección 10 de los textos):
  - contador;
  - atribuciones con enlace: Comunidad de Madrid, Ayuntamiento, CRTM (bruto o explotado) y OpenStreetMap;
  - «no es un servicio oficial», proyecto y código abierto;
  - el mapa base no se repite, porque MapLibre ya lo pinta en el mapa.
- **CRTM:** «Powered by CRTM» es ahora un enlace a crtm.es en la atribución del mapa, como pide su licencia.
- **«Cómo lo calculamos»:**
  - texto de D (`pitch/metodologia.md`, parte 1) en 8 secciones;
  - el número de conjuntos sale de la API;
  - la lista completa de fuentes (`DatasetList`, `fuente.*`) va con cada nombre, quién lo publica, la marca del portal de la Comunidad, versión, licencia y «Abrir en el portal» (pestaña nueva, con `aria-label`).
- **`lib/provenance.ts`** (pura, con tests): `counterText`, `datasetLines` y `sortDatasets` (primero los del portal de la Comunidad).

## Qué no se publica (para D, en el PR)
- **Pendientes de A** (regla de D): el paso 2 del encaje (CORE-003), el alquiler estimado (CORE-006), el ejemplo de Móstoles, compra, seguridad, zonas verdes y la sección 1.10 de versiones.
- **La 1.5 (distancias a pie):** entra con la F8, cuando la web enseñe los minutos.
- **Definiciones de fila que ya no coinciden con `/gaps`** desde GAP-001:
  - colegios cuenta ahora los «con primaria públicos o concertados»;
  - mayores cuenta «centros de mayores (hogares, clubes y centros de día)», no plazas en residencias;
  - por eso no entran «Por ejemplo», «Lo que mide cada fila» ni la frase de plazas de mayores en 1.8.
- **«Ver la lista completa»:** sobra, porque la lista está en la misma página.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 18 ficheros, 149 tests (nuevos: 4 de `provenance`) |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 |
| `capture -- --prefix f6_ …` | 8 capturas (inicio, Chamartín, «Cómo lo calculamos» y «Qué falta» a 1440 y 390 px), sin errores en la consola. `overflow_px: 0` en las pantallas de mapa; en las de texto es el desplazamiento vertical de una página larga |

## Comprobado en el navegador
- **Secciones:** 8 `h2` en «Cómo lo calculamos».
- **Números de la API:** «21 conjuntos de datos del Portal…» y el contador del pie.
- **Enlaces:** 24 «Abrir en el portal» con «se abre en una pestaña nueva» en el nombre accesible.
- **CRTM:** 1 enlace a crtm.es en la atribución del mapa.

---

# PUB-001 Fase 2 (F7) — Estados de vacío, carga y error (2026-11-11)

Sobre `origin/claude/sprint-1-public` en `98b842a`. Textos de la sección 8 de `pitch/textos_web.md`.

## Qué hay
- **Lista de zonas** (`/zonas`, `mapa.alternativa`):
  - las 199 zonas del mapa (21 distritos de Madrid y 178 municipios) como enlaces, con un filtro por nombre que ignora mayúsculas y tildes (`zoneDirectory`, pura, con tests);
  - es la alternativa al mapa para teclado y lectores de pantalla, y el destino de los mensajes de fallo, que la prometían y no existía.
- **«Ver las zonas en una lista»:** siempre a la vista, en la columna derecha del mapa y de la zona, y dentro de los avisos de fallo del mapa.
- **Carga del mapa** (`carga.mapa`): «Cargando el mapa…» mientras llegan los contornos.
- **Error del mapa:** el mensaje del código (`error.*`) y «Reintentar».
- **Avisos del mapa:** van arriba, entre las columnas, sin tapar el botón de búsqueda ni la leyenda.
- **Pantalla de zona sin contornos:** si falla la red, dice «No hemos podido conectar…» con «Reintentar» y el enlace a la lista. Antes decía «No encontramos esa zona».
- **`carga.lento`** (`useSlow`): «Está tardando un poco más de lo normal. Gracias por esperar.» tras 5 s, en el mapa, en «Preparando la zona…», en «Calculando qué falta en {zona}…», en la lista de fuentes y en la de zonas.
- **`fetchZones`:** la carga de zonas se comparte entre el mapa y la lista.
- **Fuera de esta fase:** los vacíos de la búsqueda (`vacio.sin_busqueda`, `vacio.sin_resultados`), que llegan con el buscador (F9).

## Comprobado con Playwright (`f7_estados.json`, peticiones retrasadas 7 s o cortadas)
- **Contornos retrasados:** «Cargando el mapa…» a 1,5 s; «Está tardando…» a 6 s; desaparece al llegar (`f7_mapa_cargando_lento_desktop.png`).
- **Contornos cortados:**
  - en el mapa: «No hemos podido conectar…»; tras quitar el corte y pulsar «Reintentar», el mapa carga (`f7_mapa_error_desktop.png`);
  - en la zona: error de red con «Reintentar» y el enlace a la lista, sin «No encontramos esa zona» (`f7_zona_error_desktop.png`).
- **`/gaps` retrasado:** «Calculando qué falta en Chamartín…» y «Está tardando…».
- **Teselas caídas (móvil):** el aviso enlaza a `/zonas` (`f7_teselas_caidas_mobile.png`).
- **`/zonas`:** 199 enlaces. Con «chamartin» queda solo «Chamartín»; Tab lleva el foco a ese enlace e Intro abre `/zona/distrito/2807905`.
- **Consola:** sin errores de página en ningún caso.

## Gate
| Comando | Resultado |
|---|---|
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test -- --run` | 18 ficheros, 151 tests (nuevos: 2 de `zoneDirectory`) |
| `npm run -w apps/web build` | 0 |
| `make lint typecheck test-unit` | 0 (285 pytest, 151 vitest) |
| `capture -- --prefix f7_ …` | 6 capturas (inicio, Chamartín y `/zonas` a 1440 y 390 px), sin errores en la consola. `overflow_px: 0` en las de mapa; en `/zonas` es el desplazamiento vertical de la lista |

## Para D
Textos provisionales:
- título «Todas las zonas»;
- «Busca una zona»;
- «Distritos de Madrid» y «Municipios»;
- «No hay ninguna zona con ese nombre.»;
- «Cargando las zonas…».

---

# PUB-001 Fase 3 (F8) — «Qué falta» completo contra `/gaps` (2026-11-11)

Hecha sobre `9ced17b` (GAP-001 F1–F3b) y rebasada sobre `dc2c86a` (DATA-022 F1 y GAP-001 F4); el gate y `f8_que_falta.json` son de después del rebase (ya sale «La Acebeda» con su nombre oficial). Checkpoint del 14 nov. Datos reales de `GET /api/v1/gaps/{level}/{code}` en la API 8011: las 200 zonas (179 municipios y 21 distritos) traen las 6 filas.

## Qué hay
- **Pestaña «Qué falta»** (`/que-falta?zona=distrito/2807905`):
  - título «Qué falta en {zona}», `falta.intro`, «Ver la zona» y «Cambiar de zona»;
  - las 6 filas, lo que falta primero (FALTA, JUSTO, CUBIERTO, SIN DATOS; dentro de cada estado, el orden de la API);
  - cada fila: estado con icono y texto, qué mide (los textos cortos que pasó datamad-10), la cifra de la zona y la de la Comunidad de Madrid con los decimales de la `explanation` de la API, los minutos a pie, la fiabilidad en palabras, «Ojo: {proxy_note}» y «De dónde sale» con cada conjunto enlazado a su ficha (abierto en escritorio; en el móvil, a un toque);
  - **SIN DATOS** con el motivo de `null_reason` en el texto de D (vivienda por distrito: «La fuente oficial no trae este dato.»);
  - **filas aún no calculadas** (`INSUFFICIENT_DATA: row X not computed at <nivel> level yet`): no se pintan; una línea discreta «Próximamente: {filas}. Estamos calculando el resto de servicios para esta zona.» (`falta.filas_pendientes`);
  - «Cómo leer esta lista»: los 4 estados con su explicación, una nota sobre los minutos a pie y «¿Cómo lo decidimos?»;
  - sin zona: `falta.elige_zona` y la lista de zonas con el filtro (`falta.buscador.placeholder`), que lleva a la lista de cada una; con una zona que no existe o un `?zona=` que no es una zona del mapa, `error.zona_no_existe`.
- **Minutos a pie** (`extra_indicators`, `min_a_pie_*`): «A pie hasta el colegio más cercano: 6 min»; por encima de 60, «más de 60 min»; sin valor, «sin dato» (con el motivo al pasar el ratón). Los demás indicadores extra (plazas en residencias, tamaño del hogar…) no se muestran todavía.
- **Tarjeta de zona:** la mini lista lleva «A pie: 9 min» bajo cada fila, la misma línea «Próximamente» y, en el mapa, el enlace «Ver todo lo que falta».
- **Pestaña «Qué falta» desde una zona:** abre la lista de esa zona (`tabHref`).
- **Funciones puras con tests:** `pendingRows`, `sortRows`, `gapFigures`, `walking`/`walkingText`, `gapsHref`/`parseZoneParam` (`lib/gaps.ts`), `confidenceText` (`lib/confidence.ts`), `formatNumber` (`lib/format.ts`) y `tabHref` (`lib/nav.ts`).
- **`capture.mjs`:** opción `--full` para capturar la página entera.
- **Tipos:** `src/contracts/gap_row_map_response.ts` generado del schema nuevo de A (GAP-001 F4); aún sin usar.

## Comprobado con Playwright (`f8_que_falta.json`)
- **Chamartín, 1440 px:** 6 filas. Centros de salud FALTA (0,47 frente a 0,59; a pie, 9 min), mayores FALTA (0,25 / 0,39; 10 min), escuelas infantiles CUBIERTO (5 min), colegios CUBIERTO (6 min), farmacias CUBIERTO (3 min) y vivienda SIN DATOS con su motivo. 4 enlaces de fuentes por fila. axe (WCAG 2.2 A/AA): 0 fallos.
- **Chamartín, 390 px:** fuentes plegadas, se abren al tocar; sin desplazamiento horizontal; axe: 0 fallos.
- **La Acebeda:** «más de 60 min» en cuatro filas y escuelas infantiles SIN DATOS con «Este dato no tiene sentido en esta zona.» (`f8_que_falta_acebeda_desktop.png`).
- **Filas pendientes** (respuesta real de Chamartín sin farmacia ni vivienda y con sus dos avisos, con `page.route`): quedan 4 filas, ninguna SIN DATOS de más, y la línea «Próximamente: farmacias y vivienda…» en la pestaña y en la tarjeta (`f8_pendientes_*`).
- **Zona:** mini lista «Centros de salud · A pie: 9 min · FALTA»…; la pestaña «Qué falta» y «Ver todo lo que falta» llevan a `/que-falta?zona=distrito/2807905`.
- **Sin zona y teclado:** con «Chamar», Tab lleva el foco a «Chamartín» e Intro abre su lista.
- **Errores:** `?zona=barrio/123` y `distrito/2807999` (404) dicen «No encontramos esa zona…»; el segundo, con «Elegir otra zona». El único error de consola es el 404 esperado del navegador.
- **Consola:** sin errores en el resto.

## Capturas para las slides (`pitch/slides.md`, C1–C7)
| Captura | Fichero | Estado |
|---|---|---|
| C1 · mapa con el caso demo y la coropleta de encaje | — | **Pendiente de A:** necesita `POST /search` |
| C2 · tarjeta con % de encaje y hechos | — | **Pendiente de A:** necesita `POST /search` |
| C3 · «¿Y si cambias algo?» | — | **Pendiente de A:** necesita `POST /search` |
| C4 · «Qué falta» con las 6 filas | `c4_que_falta_completa_desktop.png` (página entera), `c_que_falta_desktop.png` (primera pantalla) y sus `_mobile` | Hecha |
| C5 · zona en 3D | `c_zona_3d_desktop.png` y `c_zona_3d_desktop_vs_mockup.jpg` | Hecha |
| C6 · móvil con la hoja inferior | `c_zona_3d_mobile.png` | Hecha |
| C7 · «Cómo lo calculamos» | `c_como_lo_calculamos_desktop.png` y `_mobile` | Hecha |

Todas sin errores en la consola (`c_capture.json`, `c4_capture.json`). Las definitivas, a densidad 2× y sobre la demo desplegada, las hace D el 24 nov.

## Gate (`f8_gate.txt`)
| Comando | Resultado |
|---|---|
| `make lint typecheck test-unit` | 0 (313 pytest, 167 vitest), tras el rebase |
| `npm run -w apps/web lint` / `typecheck` | 0 |
| `npm run -w apps/web test` | 19 ficheros, 167 tests (nuevos: `confidence`, y más casos en `gaps`, `format` y `nav`) |
| `npm run -w apps/web build` | 0 |

## Revisión (agente `reviewer`, sin bloqueantes) y lo corregido
- «De dónde sale» se abre o se cierra una sola vez al pintar la fila: cambiar el ancho de la ventana ya no pisa lo que abrió la persona.
- SIN DATOS siempre con motivo: si falta `null_reason`, el de `UNKNOWN`.
- El motivo de un «sin dato» de minutos a pie se lee también con lector de pantalla (antes solo en `title`).
- Encabezados sin saltos: cada fila es un `h2`, como «Cómo leer esta lista».
- Sin `<ul>` vacío si la API no trae ninguna fila calculada.
- «Próximamente: farmacias y vivienda.»: los nombres van en minúscula en mitad de la frase.
- Pendiente, sin impacto hoy: una fila que la API no puede clasificar (`UnclassifiableError`) desaparece sin aviso visible; hoy no ocurre en ninguna de las 200 zonas.

## Para D (textos provisionales)
- «Cambiar de zona», «Elegir otra zona», «Cómo leer esta lista» y «De dónde sale: {n} conjuntos de datos».
- Nota de los minutos: «Los minutos a pie se miden por la calle, a paso tranquilo (4 km/h): desde la mitad de las calles de la zona se llega en ese tiempo o menos.»
- `falta.fila.a_pie` se escribe «A pie hasta {el colegio más cercano}: {n} min»; en la tarjeta, «A pie: {n} min».
- «Próximamente: {filas}.» delante de `falta.filas_pendientes`.
- «Cómo lo calculamos» no cambia hasta que `metodologia.md` tenga las definiciones de las 6 filas (1.4) y la 1.5 diga solo lo que la web enseña: hoy solo los minutos, no el % de calles.

---

# PUB-001 Fase 3c — Buscador tras una bandera y mejoras de la revisión de A (2026-11-11)

Revisión de A en el PR #2 (comentario 6803192711): «Buscar» llamaba a `POST /api/v1/search`, que aún no existe, y acababa en «Algo ha fallado por nuestra parte».

## Qué hay
- **Bandera `NEXT_PUBLIC_FEATURE_SEARCH`** (`lib/capabilities.ts`), que se lee al compilar y está **apagada por defecto**:
  - **apagada:** «Ver zonas que encajan» aparece desactivado con la etiqueta «Muy pronto» y el aviso «Estamos terminando el cálculo del encaje. Mientras, toca una zona del mapa para ver qué le falta.». La leyenda dice «Muy pronto verás aquí qué zonas encajan contigo.» y la tarjeta de zona ya no pide hacer la búsqueda. No se llama a la API (`runSearch`). «¿Y si cambias algo?» todavía no está en la web; llegará en la F9 detrás de la misma bandera;
  - **encendida** (`NEXT_PUBLIC_FEATURE_SEARCH=true` al compilar): todo como antes.
- **«Trabajo en»** (punto 3 de A): sin campo, con «Muy pronto», porque el campo no hacía nada.
- **Fiabilidad** (punto 4): la explicación también se lee con lector de pantalla, no solo en `title`.
- **Avisos de filas pendientes** (punto 5): un test lee los avisos literales del test de la API (`tests/unit/api/test_gaps_warnings.py`) y comprueba que la web los reconoce todos.

## Comprobado
- **Tests** (`capabilities.test.ts`): la bandera en los dos estados. Con la bandera apagada, `runSearch` no llama a la API; encendida, la llama una vez.
- **Playwright, apagada** (`f8c_bandera_off.json`): botón desactivado con «Muy pronto», aviso visible, 0 peticiones a `/search` incluso forzando el clic, sin errores en la consola, a 1440 y 390 px (`f8c_bandera_off_inicio_*`).
- **Playwright, encendida** (`f8c_bandera_on.json`): botón activo y un `POST /search` al pulsar. La respuesta es el 404 de hoy, porque la ruta aún no existe.

## Gate (`f8c_gate.txt`)
`make lint typecheck test-unit`: 0 (313 pytest y 172 vitest). Web: lint, typecheck y build en 0.

## Para C
Cuando A publique `POST /search`, hay que compilar la web con `NEXT_PUBLIC_FEATURE_SEARCH=true`. Hasta entonces, sin definir.

## Pendiente de la revisión de A (siguiente PR)
- Punto 2 (`NEXT_PUBLIC_API_URL` con `localhost` por defecto): toca el despliegue, así que lo hablo con C.
- Punto 6 (textos que duplican la API): leer los cortes de `method` cuando llegue gap-0.2.
- Punto 7 (código heredado de `/map` y teselas externas para la demo sin conexión).

---

# PUB-001 Fase 3d — Mapa por fila de «Qué falta», «Zona pequeña para comparar» (gap-0.2) y textos definitivos de D (2026-11-11)

Rama `claude/s1-web-map`, hecha sobre `f1b487a` (GAP-001 F5, D-213, `gap-0.2`) y rebasada sobre `92eab6b` (CORE-006 F2); el gate es de después del rebase. Textos de `pitch/textos_web.md` en `04f1e8e` (línea D).

## Qué hay
- **«¿Qué quieres ver?»** (leyenda del mapa de la vista general): un `select` nativo, que se usa con el teclado, con «Encaje con tu búsqueda» o una de las 6 filas. Con una fila elegida:
  - pide `GET /gaps?level=municipio&row=` y `?level=distrito&row=` y las une a las zonas del mapa por `admin_unit_id` (Madrid, por sus 21 distritos);
  - cada zona se pinta con el color de su estado y una trama: FALTA con rayas, JUSTO con puntos, zona pequeña con líneas y SIN DATOS con el borde discontinuo; CUBIERTO va sin trama. La leyenda repite colores y tramas, con el texto y el número de zonas de cada estado;
  - una zona que la fila no trae se queda sin pintar; nunca sale como SIN DATOS;
  - el encuadre deja la región por encima de la leyenda, en escritorio y en móvil.
- **«Zona pequeña para comparar»** (`reliable: false`, D-213, `fila.zona_pequena`): una etiqueta con icono junto al estado, en la pestaña, en la tarjeta de zona y en la lista de zonas; en la leyenda de la pestaña, con su explicación. En el mapa, una zona pequeña tiene su propia clase, porque cada zona lleva un solo relleno.
- **Lista de zonas como alternativa:** «Ver las zonas en una lista», desde la leyenda y desde el enlace de siempre, abre `/zonas?fila=<fila>` con el estado de cada zona.
- **Madrid entero** (paso 3.1 del guion de D): «Madrid (toda la ciudad)» aparece en la lista de «Qué falta» y en `/zonas`, y lleva a `/que-falta?zona=municipio/28079`. Allí no sale «Ver la zona», porque en el mapa Madrid son sus distritos.
- **gap-0.2 en la pestaña:** cada fila se compara con su `reference_label` (por ejemplo, «Otros municipios urbanos de la Comunidad de Madrid») y, en pequeño, «En toda la Comunidad de Madrid: …» (`falta.fila.region`).
- **Textos definitivos de D:** `estado.*`, `falta.intro`, `falta.otra_zona`, `falta.leyenda.*`, `a_pie.min` («Sin datos»), `fila.mayores`, `fila.vivienda`, `portada.paso3`, `barrios.*` («Ir a un barrio», con su ayuda para lectores de pantalla), `busqueda.pronto` (en lugar del botón), `leyenda.pronto` y `zona.encaje.pronto`.
- **«Cómo lo calculamos»:** la tabla de estados ya dice lo de gap-0.2 con los textos `estado.*`. Las definiciones largas esperan a `metodologia.md`.

## Comprobado con Playwright
- **`f8d_mapa_por_fila.json`:**
  - con el teclado (búsqueda por letras en el `select`) se elige «Centros de salud»;
  - la leyenda coincide con la API en centros de salud (4 FALTA, 33 JUSTO, 3 CUBIERTO, 159 zonas pequeñas), farmacias y vivienda (los 21 distritos SIN DATOS);
  - axe WCAG 2.2 AA: 0 fallos. La lista con la fila muestra las 199 zonas y Madrid entero;
  - en el móvil, los 5 estados se ven, no hay desplazamiento horizontal y la consola no da errores.
- **`f8d_madrid.json`:** en la lista, Tab lleva el foco a «Madrid (toda la ciudad)» e Intro abre su lista. Centros de salud sale FALTA (0,37 frente a 0,56), como en la slide 3. No hay «Ver la zona».
- **`f8d_que_falta.json`:**
  - La Acebeda: JUSTO con «Zona pequeña para comparar» en colegio, mayores y farmacia;
  - Chamartín: centro de salud JUSTO (0,47 frente a 0,56);
  - axe sin fallos a 1440 y 390 px;
  - las filas pendientes siguen saliendo como «Próximamente».

## Gate (`f8d_gate.txt`)
`make lint typecheck test-unit`: 0 (340 pytest y 189 vitest). Web: lint, typecheck y build en 0.

## Para D (textos provisionales)
«¿Qué quieres ver?» (de datamad-10), «Leyenda del mapa», «Qué falta» como grupo del `select`, «{indicador}, frente a los municipios de su tipo (urbanos o rurales).», «{n} zonas», «Ver estas zonas en una lista», «Cargando el estado de cada zona…», «Madrid (toda la ciudad)» y la frase del mapa para lectores de pantalla.

---

# PUB-001 Fase 3e — Fuentes desde el repo, `/map` a la portada y capturas de producción (2026-11-11)

Notas de C después del primer despliegue.

## Qué hay
- **Fuentes servidas desde el repo** (`next/font/local`): Plus Jakarta Sans e Inter en `apps/web/src/fonts/`, con el subconjunto latino de las fuentes variables (el mismo que servía `next/font/google`) y la licencia SIL Open Font License 1.1 (`OFL.txt`) junto a cada una. El build ya no pide nada a Google: el primer build en Vercel había fallado con `next/font/google`.
- **`/map`** (el mapa anterior a Vida Fácil, titulado «Mapa — Housing Intelligence», que cargaba capas enteras) ahora lleva a la portada. Sus componentes `AdminMap` y `MapPanel` siguen en el repo, sin uso; borrarlos queda a decisión de Mariano.
- **Capturas C4, C5 y C7 contra producción** (`https://vidafacil-madrid.vercel.app`, gap-0.2), a 1440 y 390 px, sin errores en la consola:
  - C4, «Qué falta» de Madrid capital, página entera: `prod_c4_madrid_que_falta_*`. Centros de salud sale FALTA, 0,37 frente a 0,56;
  - C5, Chamartín en 3D: `prod_c5_chamartin_3d_*`, también junto al mockup;
  - C7, «Cómo lo calculamos»: `prod_c7_como_lo_calculamos_*`.
  - Producción todavía es el PR #2: no lleva «Zona pequeña para comparar» ni los textos definitivos de D, que llegan con el PR #9.

## Comprobado
- **`f8e_fuentes_y_map.json`:**
  - las 4 peticiones de fuentes van a `/_next/static/media` del propio servidor, ninguna a Google;
  - `titleFont` (600 y 700) y `bodyFont` (400 y 500) están cargadas y el `h1` usa Plus Jakarta Sans;
  - `/map` acaba en `/` con el título de Vida Fácil;
  - la consola no da errores.
- **`f8e_inicio_fuentes_locales_*`:** la portada con las fuentes del repo.

## Gate (`f8e_gate.txt`)
`make lint typecheck test-unit` y lint, typecheck y build de la web, en verde.

---

# PUB-001 Fase 4 (F9) — Buscador y «¿Y si cambias algo?» contra `POST /api/v1/search` (2026-11-11)

Rama `claude/s1-web-search`, hecha sobre `claude/s1-web-map` (PR #9). La API es la de `origin/claude/sprint-1-public` en `f479281` (CORE-003, `915be3c` y `5f373b6`, método `fit-0.1`, D-215), lanzada en el puerto 8011 desde un árbol de trabajo aparte, sin comitear nada de A. La bandera `NEXT_PUBLIC_FEATURE_SEARCH` sigue apagada por defecto; la evidencia es con la bandera encendida, salvo `f9_bandera_off.json`.

## Qué hay
- **«Ver zonas que encajan»:**
  - Coropleta de encaje: las zonas que cumplen todo, en una escala de violetas según su `match_pct` (60 → 100 %); las que fallan alguna condición, casi blancas; y las de `match_pct: null`, grises con borde discontinuo («Sin datos», nunca 0). La leyenda da el número de zonas de cada clase.
  - Ranking (`results`), con las 5 primeras a la vista y «Ver las 10 primeras», y «Casi encajan» (`near_misses`) con la condición que fallan.
  - La tarjeta de zona añade el % de encaje, «La N.ª que más encaja», lo que no cumple o no se puede comprobar y «Lo que tienes aquí»: los hechos de la API, cada uno con su fiabilidad en palabras.
  - La web no recalcula nada: une `all_zones`, `results` y `near_misses` a las zonas del mapa por nivel y código.
- **«¿Y si cambias algo?»,** siempre visible y plegado a la opción que más zonas añade (decisión de datamad-10). Se despliega solo cuando salen 5 zonas o menos.
  - Cada opción se aplica con un toque (reenvía `relaxed_scenario`), con el aviso «Ahora ves las zonas con…» y «Volver a mi búsqueda».
  - Lleva también «Lo que más limita tu búsqueda» y las zonas sin datos (`zones_unknown`).
- **Caso demo** desde la portada («Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana»): el perfil dorado de A, comprobado por un test contra `scenario_state.familia_castellana.fixture.json`.
- **«Lo quiero a un paseo»** (`nearby`): cada servicio con sus minutos a pie y la casilla «Imprescindible».
- **«Trabajo en»:**
  - Un combobox ARIA sobre las estaciones de metro, Cercanías y Metro Ligero (`/places`, sin geocodificador externo) y sobre las zonas del mapa.
  - Siempre se envía con `max_minutes: null` y con la etiqueta «Tiempo en transporte: muy pronto».
- **Presupuesto:** «Sin límite de presupuesto» (`budget: null`). Con «Comprar» se ve «Sin datos» con su explicación (`presupuesto.compra.sin_datos`).
- **Mejoras de la revisión independiente del PR #9:**
  - Borde de *hover* en una capa aparte (`zones-hover`), que se ve con cualquier relleno.
  - `useGapRowMap` ya no pierde la fila si falla un nivel: lo deja «sin calcular» con un aviso y «Reintentar» (`joinLevels`).
  - `useMemo` en `GapLayerProvider`.

## Comprobado con Playwright (web `next build` + `start` en el 3011, API real en el 8011)
- **`f9_buscador.json`, escritorio (1440 × 900):**
  - El caso demo se abre con el teclado: 32 de 199 zonas. 1.ª Ciudad Lineal (99 %); Chamartín, 8.ª (95 %).
  - «¿Y si cambias algo?» propone «+5 min a pie hasta colegio con primaria: saldrían 49 zonas, 17 más».
  - Las cifras coinciden con un `POST /search` hecho aparte con el mismo cuerpo, y la leyenda («Cumple todo: 32 zonas») coincide con `zones_passing`.
  - Aplicar la opción con Intro lleva a 49 zonas, y el selector de la búsqueda pasa a 15 min. «Volver a mi búsqueda» vuelve a 32 y a 10 min, y el foco pasa al título «Zonas que encajan».
  - «Trabajo en», con el teclado:
    - al quitar el lugar, el foco pasa al campo;
    - «nuevos min» da 2 estaciones; flecha abajo e Intro eligen «Nuevos Ministerios (metro)» y el foco pasa a «Quitar»;
    - el hecho de la tarjeta dice «A 3,2 km en línea recta de Nuevos Ministerios (metro)».
  - Con «Comprar», la API devuelve 0 zonas y 48 sin datos, y «¿Y si cambias algo?» ofrece «Sin límite de precio de compra: saldrían 48 zonas».
  - Las 6 peticiones a `/search` llevan `max_minutes: null`. axe WCAG 2.2 AA: 0 fallos antes y después de buscar, con la tarjeta abierta y con compra. Consola sin errores y sin desplazamiento horizontal.
- **Móvil (390 × 844):** los resultados entran a la vista en la hoja inferior. axe da 0 fallos, la consola no da errores y no hay desplazamiento horizontal.
- **`f9_bandera_off.json`:** con la bandera apagada no hay botón de ejemplo ni «Lo quiero a un paseo», sale «Muy pronto», no hay ninguna petición a `/search` y axe da 0 fallos.

## Capturas C1–C3 (`pitch/slides.md`)
- **C1:** `c1_busqueda_desktop.png` (y `_vs_mockup.jpg`) y `c1_busqueda_mobile.png`: «Tu búsqueda» con el caso demo, la coropleta de encaje y la tarjeta de Ciudad Lineal (en el móvil, el ranking en la hoja).
- **C2:** `c2_tarjeta_zona_desktop.png` y `c2_tarjeta_zona_mobile.png`: 99 % de encaje, 5 hechos con su fiabilidad y la mini lista «Qué falta aquí».
- **C3:** `c3_y_si_cambias_desktop.png` y `c3_y_si_cambias_mobile.png`: el bloque desplegado con las cifras de la API.
- Otras: `f9_aplicada_desktop.png`, `f9_trabajo_desktop.png`, `f9_compra_desktop.png` y `f9_bandera_off_inicio_desktop.png`.

## Revisión
Agente `reviewer` sin bloqueantes. Aplicado:
- el estado de la búsqueda pasa a un *reducer* puro (`lib/searchState.ts`, con tests): una relajación fallida ya no deja el aviso ni el escenario cambiados, y «Reintentar» repite el intento tal cual;
- el foco ya no se pierde (combobox, «Quitar» y opciones con `aria-disabled`);
- regiones vivas fijas, reintento de las estaciones, `stale` por contenido y el aviso «de tu búsqueda anterior» en la tarjeta.

Quedan anotados en el PR el R-06 (la lista de al lado es la alternativa sin color a «Cumple todo» frente a «No cumple todo») y el R-09.

## Gate (`f9_gate.txt`)
- `make lint typecheck test-unit`: 0 (360 pytest y 226 vitest).
- Web: lint, typecheck y build en 0, con la bandera apagada y encendida.
