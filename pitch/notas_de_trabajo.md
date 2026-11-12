# Notas de trabajo de la línea D

Fichero interno: lo que no va en los ficheros que puede leer el jurado (`formulario.md`, `datasets_cm.md` y el deck). Aquí sí van marcas «pendiente de A/B/C», decisiones D-xxx y PR. El formulario ya se envió (12 nov): lo de abajo queda como registro de cómo se preparó.

---

## Cifras que dependen de otra línea antes del freeze (23 nov)

| Cifra | Hoy | Si no llega | De quién |
|---|---|---|---|
| 27 conjuntos CM | Los 2 de camas los sirve la API (85 hospitales, 3,0 camas por 1.000 habitantes) | Si la web no enseña la línea de camas en la nota del hospital antes del 23 nov, se cuentan 25: guion (bloque 4), slides, preguntas 7 y 23, metodología §1.7 y tabla del formulario. El resumen enviado no se toca | B |

---

## Condiciones de publicación de `metodologia.md`

Párrafos de la parte 1 que B solo publica si la web ya enseña lo que cuentan. Si el 16 nov no se cumple, B quita el párrafo entero.

| Sección | Párrafo | Se publica si | Pendiente de |
|---|---|---|---|
| 1.3 | «**Zonas verdes** (solo si lo marcas)…» | La web enseña el chip de zonas verdes (la API ya puntúa con `fit-0.3`, D-222) | B |
| 1.8 | «**En los 21 distritos de Madrid** te contamos, solo como contexto, cómo valoran los vecinos la seguridad…» | La vista de zona enseña `zona.seguridad_vecinos` (D-226) | B |
| 1.8 | «**Zonas verdes:** contamos los parques de 1 hectárea o más…» | Igual que en 1.3 | B |

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
