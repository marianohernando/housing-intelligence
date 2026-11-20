# Notas de trabajo de la línea D

Fichero interno: lo que no va en los ficheros que puede leer el jurado (`formulario.md`, `datasets_cm.md` y el deck). Aquí sí van marcas «pendiente de A/B/C», decisiones D-xxx y PR. El formulario ya se envió (12 nov): lo de abajo queda como registro de cómo se preparó.

---

## Cifras que dependen de otra línea antes del freeze (23 nov)

| Cifra | Hoy | Si no llega | De quién |
|---|---|---|---|
| 39 conjuntos CM (27 el 12 nov; 29 con D-235; 35 con D-237 y D-241, en producción el 15 nov; 36 con D-246, en producción el 18 nov; 39 con D-247 y D-248, en producción el 19 nov) | **Cumplida.** La web enseña los 2 de camas bajo la nota del hospital (D-231, `3325084`, en producción) y `GET /api/v1/datasets?cm_only=true` da 39, y 59 en total (comprobado por D el 19 nov, tras el despliegue de `396d8f6`) | — | — |

---

## Tras la entrega 2 de UX: hecho el 18 nov

La claridad en el móvil (D-244 y D-245) está en producción desde el 15 nov (`55651c2`, PR #84) y D la comprobó el 18 nov. Las palabras de la web cambiaron: las bandas son «Muy buena opción», «Buena opción», «Opción regular» y «Poco recomendable»; la lista se llama «Zonas que te convienen» («os» con más de una persona); «Casi encajan» pasa a «Casi valen» y «¿Y si cambias algo?», a «¿Queréis ver más zonas?». La lista enseña la zona, la banda y el precio (en escritorio, el % pequeño), sin «Empatan»; la tarjeta, lo esencial y lo demás tras «Ver más». El método no cambia.

| Qué | Dónde | Estado |
|---|---|---|
| Rehacer C1, C2 y C3 en producción y quitar sus `data-pending` | `pitch/capturas/`, `pitch/deck/deck.html` y `deck.css` | **Hecho el 18 nov.** También C6, la lista del móvil a 390 px. Recortes de C2 y C3 y marcadores de la slide 4 al día |
| Cambiar las etiquetas citadas | `pitch/video_respaldo.md` (planos 2 a 5), preguntas 43 y 48, `pitch/banco_formula.md` y `pitch/metodologia.md` §1.3 (sin el aviso) | **Hecho el 18 nov** |
| «Zonas que encajan» → «Zonas que te/os convienen» | guion, `slides.md`, `video_respaldo.md`, `metodologia.md` y el deck | **Hecho el 18 nov.** `textos_web.md` ya lo tenía (B) |
| Contar como hecho lo de la persona mayor | pregunta 43, `slides.md`, guion (bloque 5) y el recuadro de la slide 4 | **Hecho el 18 nov**, con las medidas (0 textos < 16 px y 0 botones < 44 px a 390 y 360 px; 4 cosas por fila en vez de 7 a 9). **Sin segunda prueba todavía:** no se dice que ya le resulta fácil |
| Que el guion quepa en 5 minutos | guion | **Hecho el 18 nov:** 497 palabras y unos 28 s de margen, con el clic en «Ver más». Esa noche, con la frase del suelo público sin cifra (decisión de Mariano), 496 y unos 28 s |
| «Cómo lo calculamos» dice todavía que la lista pone «Empatan al 94 %» | web (B) | Avisado a datamad-10 el 18 nov; va a la deuda de la web |

## El siguiente paso: de dónde vivir a dónde construir (18 nov)

Aprobado por Mariano el 18 nov. Está en el guion (bloque 4), en la slide 3 («Viabilidad», en el sitio de la miniatura C7) y en la pregunta 60. En las slides, sin nombres de empresas; en la pregunta 60, Nestra y Sitescope como validación de mercado.

| Qué | Dónde | Estado |
|---|---|---|
| La capa del suelo público (Portal del Suelo 4.0 de la Comunidad, D-246) | otra línea, en la web | **En producción desde el 18 nov** (despliegue de `747cb65` y sync, `evidence/gate-06/2026-11-18-deploy/deploy-36-747cb65-suelo.md`, PR #90; confirmado por datamad-10). D lo leyó en la API ese día: 291 parcelas en 29 municipios, 394.298 m² edificables; 38 en 7 distritos de Madrid (`pitch/comprobacion_produccion_18nov.md`) |
| +1 en `pitch/datasets_cm.md` (36 CM, 53 en total, igual que el README y la API), la frase del suelo en el bloque 4 del guion, sin cifra (sin la lista de datos: 101 palabras, unos 28 s de margen) y la pregunta 60 sin «pendiente» | `datasets_cm.md`, guion, preguntas, slides, metodología | **Hecho el 18 nov** |
| «Ya enseñamos el suelo público para vivienda.» en la slide 3, o una captura de la capa | deck | **Hecho el 18 nov, por decisión de Mariano:** la frase va en la línea del siguiente paso de la slide 3 y cabe a 1920 × 1080; sin captura de la capa. Mariano también quitó la cifra (291) del bloque 4 del guion: no está en pantalla. La slide 2 ya cuenta 36: su número y su tabla salen del catálogo (`pitch/deck/build.py`) |

## Modelo de negocio del 19 nov

Decisión de Mariano del 19 nov, que sustituye a la del 12 nov: personas y ayuntamientos, gratis; pagan inversores y promotores privados, con un plan de precios (`pitch/modelo_negocio.md`).

| Qué | Dónde | Estado |
|---|---|---|
| El modelo nuevo, con los precios como hipótesis: Inversor 99–199 €/mes, Equipo 399 €/mes y estudio a medida de 490–1.500 €; Nestra, 175, 437,50 y 1.050 €/mes como referencia | `modelo_negocio.md` | **Hecho el 19 nov** |
| «Gratis para personas y ayuntamientos; pagan inversores y promotores», sin precios en la voz ni en la slide | slide 3, guion (bloque 4), `slides.md` y preguntas 6 y 60 | **Hecho el 19 nov.** Bloque 4: 102 palabras; margen, unos 28 s |
| La sección «Para inversores» de la web | otra línea, en la web | **En producción desde el 19 nov** (D-247 y D-248, despliegue de `396d8f6` y sync; `evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md`, PR #96; confirmado por datamad-10). Ya citada como hecha, **con redacción genérica** («la viabilidad sobre una parcela, con el contexto de su barrio»), en la slide 3, el bloque 4 del guion (93 palabras; margen, unos 32 s; sin «de dónde vivir a dónde construir», revisión del #98), las preguntas 6, 23 y 60, `slides.md` y `modelo_negocio.md`. Sin capturas. **Desde la tarde del 19 nov**, la lista de barrios va detrás de la búsqueda por parcela, como «Explorar barrios» (fila siguiente) |
| La versión por parcela exacta (referencia catastral, dirección o clic en el mapa, con su calificación; la lista de barrios, en segundo plano) | otra línea, en la web | **En producción desde el 19 nov** (D-250, despliegue de `79020a1` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102; confirmado por datamad-10). D leyó las 4 parcelas de demostración en la API de producción ese día: las 4, completas y en barrios del piloto. **Revisado el 19 nov (resuelve el «REVISAR tras la búsqueda por parcela»):** el bloque 4 del guion («…y su versión ya está: buscar una parcela de Madrid capital y calcular si una promoción sale, con la demanda de la zona.»; 105 palabras, margen de unos 26 s; «calcular» y no «ver» tras la revisión del #103); las preguntas 6 (la ficha, dónde funciona y las 4 parcelas con sus cifras) y 60 (lo distinto es el contexto de demanda al lado de la parcela, y cruzarlo con la vivienda que falta es el siguiente paso; el límite: no decimos qué se puede construir, y la fila «vivienda» sale SIN DATOS en los 21 distritos), y además la 1 (15 rutas y 16 esquemas), la 8 (licencias de la búsqueda) y la 23 (no suma conjuntos); `slides.md` (capturas C8–C10 de deploy-39, de reserva) y `modelo_negocio.md`. «Piloto en Madrid» dice ahora lo exacto: la búsqueda llega a toda Madrid capital, y el piloto de la M-40 es el contexto completo del barrio y «Explorar barrios». **La línea del pie de la slide 3**, aprobada por Mariano el 19 nov por la tarde: «Ya está, para inversores: busca tu parcela en Madrid capital y calcula si sale, con la demanda de su zona.» Medida a 1920 × 1080: 3 líneas, sin desborde (`slides.md`) |
| Contador 36 → 39 CM y 53 → 59 en total | `datasets_cm.md` (y la instantánea del portal, leída el 19 nov), slide 2, guion, preguntas 7 y 23, `slides.md`, `metodologia.md`, `textos_web.md`, `README_publico.md` y `video_respaldo.md` | **Hecho el 19 nov.** `pitch/formulario.md` no se toca. **Para Mariano:** en la slide 2, «Vivienda» pasa a 12 y ocupa una línea más; las filas de la tabla van 2 px más justas para que «Apoyo (no CM)» siga dentro de la tarjeta (`slides.md`, slide 2) |
| La API pública y el MCP, gratis para todos (decisión de Mariano del 19 nov) | `modelo_negocio.md`, preguntas 1, 2 y 6, y bloque 4 del guion | **Hecho el 19 nov.** La página `/desarrolladores` está en producción (D-249, despliegue de `20b46d9`, PR #99; confirmado por datamad-10 y comprobado por D: 200, 7 herramientas, «Funciona en local» y lo planteado como «Aún no disponible»). Mariano dejó a D si iba en la voz o en la slide. **Propuesta de D:** una frase en el bloque 4, «La API y el MCP para agentes de IA son gratis para todos.» (106 palabras; margen, unos 26 s), y la slide 3 sin cambios, para no rehacer la maqueta. **Slide 3, hecho el 19 nov:** Mariano aprobó la viñeta «Código abierto, y API y MCP gratis.» (antes, «Código abierto: cualquiera puede repetir los cálculos.»). Medida por D a 1920 × 1080 con `build.py` en borrador: una línea, sin desborde, y las tarjetas acaban a 834 px (la banda empieza a 858) |

## Prueba de la versión para inversores con P7 (inversor) (19 nov)

Un inversor con experiencia en promoción probó el 19 nov solo la versión para inversores; Mariano contó lo que dijo. Se cita siempre como «P7 (inversor)», nunca por su nombre ni por su relación con nadie. Señaló cuatro temas, **y los cuatro están ya en producción**: **D-252** (PR #109, desplegado el 19 nov, `f806850`) resuelve la edificabilidad por uso y el coste, y cambia «solar» por «¿Está sin edificar?»; **D-253** (PR #110, desplegado el 20 nov, `a669057`) trae los servicios y suministros, el catálogo de edificios protegidos, el aviso de edificio existente, el «primer filtro» y la frase para consultoras en la web.

| Tema | Lo que dijo | Qué hacía la ficha antes de D-252 (leída por D en producción el 19 nov, `GET /api/v1/investors/parcels?rc=3959601VK4735H`) | Estado |
|---|---|---|---|
| Servicios | Hay solares que no pueden tener suministro de luz (CUPS) ni acometida de agua; que la parcela tenga servicios condiciona si se puede construir | No lo decía. Las acometidas solo aparecen como coste, dentro de «Otros» del coeficiente | **Hecho en D-253** (§1–5), en producción desde el 20 nov: «Servicios y suministros» en la ficha (urbanización, potencia mínima «Supuesto» con el aviso del centro de transformación, la CNMC solo como enlace, Canal de Isabel II). Ya no dice «solar» (D-252 §4). En las preguntas 6 y 61; captura C11 |
| Edificabilidad por uso | Hay que separarla: terciario (público y privado), residencial y dotacional, y no dar solo una cifra | Una sola cifra (`buildability.value_m2`), marcada «Dato», «Supuesto» o «Sin dato», junto al uso del planeamiento (`planning.use`) | **Hecho en D-252** (§1–2), en producción desde el 19 nov: una línea por fuente con su uso y lo que el plan publica por uso (USOS_SUELO, tablas 4 y 5), sin repartir nunca una cifra. En la pregunta 6 |
| Coste | «Baila mucho ese dato»: hay que explicar de dónde sale y cuánto puede variar | El PEM de los visados de obra nueva de viviendas en bloque de toda la Comunidad (644 €/m², 2025, `cm_visados_presupuesto_obra`) por un coeficiente supuesto de 1,36 con su desglose; ±5 % de coste en los escenarios; el aviso «El PEM de los visados suele declararse a la baja…». Todo editable | **Hecho en D-252** (§5–7), en producción desde el 19 nov: PEM de partida de 968 €/m² (supuesto, Costes de Referencia General de la CM, 2022), los 644 €/m² de los visados como referencia baja y «Dato» (sigue contando como conjunto CM), tres referencias, qué incluye el coste y qué no, coeficiente 1,3575 (ICIO del 3,75 %) y pesimista con +15 % de coste. En las preguntas 6 y 61 |
| Consultoras | «la gente que va a hacer eso se va a una inmobiliaria o una consultora a que les hagan el estudio completo» | — | **Hecho.** En el pitch, el 19 nov (PR #108): la ficha es el primer filtro, en minutos, antes de pagar el estudio completo; las consultoras y las inmobiliarias son clientes (plan Equipo), en línea con `CLAUDE.md` §16. En la web, el 20 nov (D-253 §8): «Esto es un primer filtro de minutos, gratis y con fuentes…», «Lo que añade un estudio completo» y «Llévate esta ficha (PDF) a tu consultora: ahorra parte de la recopilación de datos públicos.» **La pregunta 61 se cerró el 20 nov.** La voz y las slides no cambian; cualquier cambio ahí se propone antes a datamad-10 |

**Las cifras de las parcelas de demostración cambian con D-252** (pregunta 6; D-252 en producción desde el 19 nov a las 23:43, despliegue de `f806850`, `evidence/gate-06/2026-11-19-deploy/deploy-41-f806850-coste.md`, PR #112; leídas por D en la API de producción el 20 nov):
- **Almería 1:** «Sin dato». Su ámbito, APR.04.09, no está terminado (las cuatro fases «Sin iniciar» y, en VEDA, «pendiente de planeamiento de desarrollo», a 1 de julio de 2026), y sus 32.697 m² quedan como referencia. Se puede contar como honestidad del producto: no damos una cifra donde el planeamiento no está desarrollado. **Cerrado el 20 nov:** comprobada por C tras el despliegue de `c4eaab1` (D-252b).
- **Méndez Álvaro 47:** unos 61,2 millones de € (69,9 y 50,8 en los otros escenarios), en deploy-41 y en la API (POST de la viabilidad con los valores de partida de la ficha). **Cerrado el 20 nov.**
- **Mayor 61:** unos 802.000 € (926.000 y 648.000), unos 3.580 € por m² edificable, con una rentabilidad bruta del 5,3 % si se alquila. La calculadora parte de 224 m² (la API da 224,4, que daría unos 803.000 €: manda la pantalla). **Cerrado el 20 nov:** en producción tras el despliegue de `d29e841` (D-252c), leído por C en pantalla a 360, 390 y 1440 px y por D en la API (POST de la viabilidad con 224 m²: 801.957, 926.305 y 648.174 €). Su catálogo llegó con D-253 (abajo).
- **Luis Misson 2:** sigue «Sin dato» (norma zonal 4).

**Con D-253 (en producción desde el 20 nov, despliegue de `a669057`; leído por D en la API ese día):** Méndez Álvaro 47, unas 164 viviendas y al menos 499,1 kW, con el aviso del centro de transformación; Mayor 61, unas 3 viviendas y al menos 17,3 kW, y catalogado («Protección parcial, nº 02933 (nivel 3 de 3)»), edificio de 1890 con 6 inmuebles; las otras tres no aparecen en el catálogo. En la pregunta 6.

**Capturas C8 a C11: rehechas por D en producción el 20 nov**, una sola vez, con D-253 y solo con las parcelas de demostración (`pitch/capturas/`, `slides.md`). Si el sábado 21 la web deja una sola vez «Llévate esta ficha (PDF) a tu consultora…», se revisa si C9 o C10 enseñan la que se quita.

**Conjuntos de datos (pendiente del sync del sábado 21):** D-253 añade al catálogo `ayto_edificios_protegidos` (300158, Ayuntamiento) y `cm_costes_referencia_edificacion` (el documento de la Comunidad de los costes de referencia, que no es del portal de datos abiertos). `GET /api/v1/datasets` sigue dando 59 hasta el sync. `pitch/datasets_cm.md`, regenerado el 20 nov, los pone en «todavía sin ingerir» (de 9 a 11) y no cambia los 39 CM. **No se cuentan en el pitch hasta el sync:** después, D vuelve a leer la API y, si el total cambia, actualiza `datasets_cm.md`, la slide 2, el guion y las preguntas 7 y 23.

---

## Condiciones de publicación de `metodologia.md`

Párrafos de la parte 1 que B solo publica si la web ya enseña lo que cuentan. Si el 16 nov no se cumple, B quita el párrafo entero.

| Sección | Párrafo | Se publica si | Pendiente de |
|---|---|---|---|
| 1.3 | «**Zonas verdes** (solo si lo marcas)…» | La web enseña el chip de zonas verdes (la API ya puntúa con `fit-0.3`, D-222) | **Cumplida** el 12 nov: el chip está en la web |
| 1.8 | «**En los 21 distritos de Madrid** te contamos, solo como contexto, cómo valoran los vecinos la seguridad…» | La vista de zona enseña `zona.seguridad_vecinos` (D-226) | **Cumplida** el 12 nov: dos barras de 0 a 10 (`PerceivedSafety.tsx`) |
| 1.8 | «**Zonas verdes:** contamos los parques de 1 hectárea o más…» | Igual que en 1.3 | **Cumplida** el 12 nov |

**Alquiler de contratos nuevos (D-228):** aplicado el 12 nov en `metodologia.md` §1.3, con el caso de ejemplo de `fit-0.6` (27 zonas, Latina 1.ª).

---

## Formulario: variante B y estado de cada afirmación (antes en `formulario.md`)

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo.

- **Formulario:** enviado el 12 nov con el resumen principal (`formulario.md`). La preparación campo a campo y la checklist del envío quedan en el historial: `git show 6d60ecb:pitch/formulario.md`.

### Campo 7 · Variante B (94 palabras) · no se envió
Esta versión no promete el buscador como hecho: lo presenta como lo que estamos construyendo. Solo vale si el 18 nov la demo vuelve a enseñar «Muy pronto». «Frente a municipios parecidos» es el método de D-213, refinado por D-217: cada zona se compara con los demás municipios de su tipo, urbanos o rurales, y un pueblo muy pequeño, junto con sus vecinos parecidos (`pitch/metodologia.md` §1.4).

<!-- variante-b:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto frente a municipios parecidos: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Para las personas construimos un buscador que recomienda dónde vivir según su alquiler, su hogar y su trabajo, con alternativas cuando nada encaja. Usa 26 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- variante-b:fin -->

```bash
awk '/^<!-- variante-b:fin/{f=0} f; /^<!-- variante-b:inicio/{f=1}' pitch/formulario.md | wc -w   # 94
```

### Cada afirmación del resumen: evidencia y estado interno

| Afirmación | Evidencia hoy (11 nov) | Estado |
|---|---|---|
| Datos abiertos de la Comunidad de Madrid · «Usa 26 datasets del portal regional» | `pitch/datasets_cm.md` (generado desde `data/catalog/`, regenerado el 12 nov: 26 con Gate 1 en PASS) · `evidence/gate-01/2026-11-10/real-run-quality.txt` (los 21 del 10 nov) · `evidence/gate-01/2026-11-12/cm_dotacion_camas/` y `cm_hospitales_datos_asistenciales/` (2 del 12 nov, D-217 §4) · `evidence/gate-01/2026-11-12/crtm_topologia_*/` (las 3 topologías del CRTM, 12 nov, D-223) · en producción, `GET /api/v1/datasets?cm_only=true` da `cm_open_data_count: 26` y la web lo enseña en «Cómo lo calculamos» y en el pie (12 nov) | Hecho: los 26 están ingeridos y validados. 24 alimentan la lista o el buscador; el alquiler por código postal se ve en la tarjeta de cada distrito de Madrid (Ciudad Lineal: «Alquiler medio ≈ 1.070 €/mes por 77 m²», producción, 12 nov). Los 2 de camas solo dan el total de la región (20.776 camas instaladas en 2023): su uso en pantalla está **pendiente de A** (`grep -c 'pendiente de A' pitch/datasets_cm.md` da 4: esos 2 y 2 fuentes del catálogo aún sin ingerir). Las 3 topologías alimentan «sin escaleras», en producción desde el 12 nov. Si el 18 nov siguen así, «usa 26» sigue siendo cierto, pero si preguntan se dice qué se ve en pantalla |
| «Un mapa de lo que falta» · «qué falta, qué está justo y qué está cubierto» | `GET /api/v1/gaps/{level}/{code}` y `GET /api/v1/gaps?level=&row=` (el mapa, GAP-001 F4) · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` (`gap-0.3`) · recuento por estado: `evidence/gate-04/2026-11-12/gap-status-gap03.md` | Hecho, con las 6 filas en los 179 municipios y los 21 distritos. Desde el 12 nov, las 5 de servicios miden lo que se tiene a 15 min andando, repartido entre quienes lo comparten (D-217, `gap-0.3`, en producción) |
| «frente a municipios parecidos» (solo variante B) | D-213: referencia = los demás municipios del mismo tipo, rural o urbano · D-217: un pueblo demasiado pequeño se compara junto con sus vecinos del mismo tipo a 15 km o menos (`comparison_group`) · `evidence/gate-04/2026-11-12/phase-t2-review-gate.txt` · en producción, `GET /api/v1/gaps/distrito/2807913` da `gap-0.3` (comprobado el 12 nov) | Hecho en la API y en producción (GAP-001 F5; DATA-AUDIT T2, D-217) |
| «escuelas infantiles, colegios, salud, mayores, farmacias y vivienda» | `gap_row` de los 6 YAML en `data/catalog/features/` · `evidence/gate-04/2026-11-11/phase-gap001-f2.txt`, `-f3a.txt` y `-f3b.txt` · en la demo pública, `GET /api/v1/gaps/distrito/2807905` devuelve las 6 filas (comprobado el 11 nov) | Hecho (GAP-001 F2–F3b). La vivienda sale SIN DATOS en los distritos de Madrid: la CM no la publica a ese nivel |
| «por distrito de Madrid» | D-200 · D-209 (población por distrito del padrón del Ayuntamiento) · DATA-012 hecha (`be40c2f`, `board/BOARD.md`) · ejemplo real: Chamartín, `GET /api/v1/gaps/distrito/2807905` (comprobado en la demo pública el 11 nov) · `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md`, «Manual check: Chamartín» | Hecho para las 6 filas (vivienda: SIN DATOS por distrito) |
| «recomienda dónde vivir según su alquiler, hogar y trabajo» | `POST /api/v1/search` (CORE-003, `915be3c`; CORE-006, `92eab6b`) · D-214 (alquiler × m² del hogar) · D-215 (condiciones y % de encaje) · `evidence/gate-04/2026-11-11/phase-core003-f2.txt` (6 escenarios dorados en datos reales) | Hecho en la API y en producción (PUB-001 F4, PR #10; encendido en el PR #11). El trabajo cuenta en minutos de transporte público llegando a las 9:00 (CORE-009, D-220, `fit-0.2`): hecho en la API y en producción desde el 12 nov (despliegue de `28a0f2f`, `evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`). **Solo en el resumen principal** |
| «si nada encaja, enseña cuántas zonas aparecen al relajar cada condición» (Reality Check) | D-215 (punto 8) · en producción, «¿Y si cambias algo?» del caso de la Castellana: «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» (`POST /api/v1/search` con el fixture, 12 nov; el 11 nov eran 49, `prod-buscador-check.json`, PR #11). Subir el presupuesto ya no suma zonas y la web no enseña esa opción | Hecho en la API y en producción. El bloque sale siempre, plegado a la opción que más zonas suma, y se despliega solo cuando salen pocas zonas o ninguna. **Solo en el resumen principal** |
| «explica el porqué en lenguaje cotidiano» | Campo `explanation` de la lista. Ejemplo real: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)» (Puente de Vallecas, `GET /api/v1/gaps/distrito/2807913`, `gap-0.3`, producción, 12 nov) | Hecho en la lista y en la API del buscador (`facts`, D-215: «Colegio con primaria a 5 min andando») |
| «cada resultado cita su fuente y su fiabilidad» | Cada fila de la lista lleva `datasets` (nombre, portal, versión, licencia) y `confidence` (`zone_gap_list.madrid.fixture.json` y la misma respuesta de Puente de Vallecas) | Hecho en la lista y en la API del buscador (`datasets` y `confidence` por zona y por hecho, D-215) |
| «Código abierto con API» | `LICENSE` (Apache-2.0, D-191) · repo público (D-198) · rutas en `docs/04_technical_architecture/31_public_api_routes.md` | Hecho |
| Demo con enlace público | https://vidafacil-madrid.vercel.app (URL elegida por Mariano) · `infra/deploy/README.md` · `evidence/gate-06/2026-11-11-deploy/deploy-9-web-nueva.md` (web nueva) · `deploy-12-buscador.md` (buscador, PR #11) · gap-0.3 en producción: despliegue `28e53fa`, smoke 8/8 con `/search` (PR #15 de C, abierto: `deploy-13-auditoria-gap03.md`) y `GET /api/v1/gaps/distrito/2807913` con `method.version: gap-0.3` (12 nov) | Hecho: la web nueva con el buscador, smoke 7/7 con datos reales (11 nov); gap-0.3 desplegado el 12 nov. Coste 0 €/mes. El 18 nov se vuelve a abrir antes de enviar |

El resumen no promete los extras: zonas verdes, «sin escaleras», precio de compra ni MCP (D-206). Las zonas verdes y «sin escaleras» ya están en la API (D-222, D-223), pero el 18 nov puede que la web aún no los enseñe y no caben en 100 palabras. La seguridad no puntúa (D-224) y no se menciona.
