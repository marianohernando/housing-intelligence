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
