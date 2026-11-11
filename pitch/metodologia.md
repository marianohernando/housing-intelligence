# «Cómo lo calculamos» — contenido de la pestaña

Para la línea B. La **parte 1** es el texto de la pestaña, en español llano. La **parte 2** es interna: de dónde sale cada afirmación y qué falta.

**Marcas en la parte 1:** los párrafos con **[pendiente de A: …]** no se publican hasta que A lo tenga hecho. Si el 16 nov no existe, B quita el párrafo entero; no se deja un hueco ni un «próximamente».

Los textos de B en `apps/web/src/app/(vida)/como-lo-calculamos/page.tsx` («Tres reglas que seguimos siempre») encajan con la sección 1.1 y se mantienen.

---

## Parte 1 · Texto de la pestaña

### 1.1 Tres reglas que seguimos siempre
- Comparamos cada zona con el conjunto de la Comunidad de Madrid, siempre según cuánta gente vive en ella.
- Si un dato no existe, lo decimos: «sin datos» no es lo mismo que cero.
- Cada dato dice de dónde sale y cuánto podemos fiarnos de él.

### 1.2 Qué zonas comparamos
Los 179 municipios de la Comunidad de Madrid. Madrid capital no va como un solo bloque: la dividimos en sus 21 distritos, porque no es lo mismo vivir en un distrito que en otro.

### 1.3 Cómo sale el % de encaje
El % de encaje dice **cuánto se parece una zona a lo que tú buscas**. No es una nota de la zona: la misma zona puede encajar mucho con una familia con niños y poco con una persona mayor que vive sola.

**Paso 1. Lo imprescindible.** Miramos tus condiciones en cada zona, por ejemplo tu presupuesto o tener un colegio cerca. Cada condición puede salir de tres maneras:
- **Cumple.**
- **No cumple.**
- **No lo sabemos**, porque falta el dato. En ese caso no la damos por buena.

Solo te enseñamos como «zonas que encajan» las que cumplen todo. Las que fallan en una sola cosa salen aparte, en «Casi encajan», para que decidas tú.

**Paso 2. Lo que te importa.** Entre las zonas que cumplen, pesa más lo que marcaste primero en «Me importa». **[pendiente de A: CORE-003. Explicar aquí cómo se reparten los pesos entre las prioridades y cómo se pasa a %, con un ejemplo real del caso de la Castellana.]**

**Debajo del %** van entre 3 y 5 hechos que puedes comprobar, como «Colegio público a 6 min andando», y cada uno dice cuánto nos fiamos del dato.

**El alquiler estimado** sale del precio medio por metro cuadrado que publica la Comunidad de Madrid para cada municipio, multiplicado por los metros que necesita tu hogar. **[pendiente de A: CORE-006. Decir cuántos metros se cuentan según el tamaño del hogar.]**

### 1.4 Cómo decidimos qué falta en una zona
Para cada servicio contamos cuántos hay en la zona por cada número fijo de vecinos. Por ejemplo:
- **Centros de salud:** centros de salud y consultorios por cada 10.000 habitantes.
- **Colegios:** colegios públicos por cada 1.000 menores de 15 años.

Después hacemos la misma cuenta para toda la Comunidad de Madrid y comparamos:

| Si la zona tiene… | Sale |
|---|---|
| menos del 80 % de lo que tiene el conjunto de la región | **FALTA** |
| entre el 80 % y el 100 % | **JUSTO** |
| el 100 % o más | **CUBIERTO** |
| no tenemos el dato | **SIN DATOS** |

**Ejemplo real.** En Móstoles hay 0,47 centros de salud por cada 10.000 habitantes. En el conjunto de la Comunidad hay 0,59. Móstoles tiene el 79 % de lo de la región, así que sale **FALTA**. **[pendiente de A: los cortes del 80 % y el 100 % son provisionales hasta GAP-001; si cambian, se cambian aquí la tabla y el ejemplo.]**

Es una señal para saber dónde mirar primero, no un veredicto: comparamos con el conjunto de la región, no con una norma oficial que diga cuántos centros debería haber.

**Lo que mide cada fila:**
- **Colegios:** colegios públicos por cada 1.000 menores de 15 años.
- **Centros de salud:** centros de salud y consultorios de atención primaria por cada 10.000 habitantes.
- **Mayores:** plazas autorizadas en residencias por cada 100 personas de 65 años o más. **[pendiente de A: fila en GAP-001.]**
- **Escuelas infantiles, farmacias y vivienda:** **[pendiente de A: GAP-001. Una línea por fila con lo que mide; la de vivienda compara el tamaño de los hogares con la superficie de las viviendas (D-194).]**

### 1.5 Distancias a pie
**[pendiente de A: enseñarlo en la web con GAP-001.]** Medimos lo que tardarías andando por las calles de verdad, no en línea recta, a un paso tranquilo de 4 km/h, con el mapa de calles de OpenStreetMap. Desde cada calle donde vive gente calculamos cuánto se tarda hasta lo más cercano: escuela infantil, colegio con primaria (público o concertado), centro de salud o consultorio, farmacia, centro de mayores y parada de autobús, metro o Cercanías. Damos dos cifras: los minutos en los que llega la mitad de las calles de la zona, y qué parte de sus calles está a 10 minutos o menos (15 para el centro de salud y 5 para la parada). A ese paso, 10 minutos son unos 670 metros. Si en una zona no hay calles en el mapa, sale «sin datos», nunca cero. Usamos el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento.

### 1.6 Qué significa la fiabilidad
Cada dato lleva una de estas etiquetas:
- **Dato fiable:** sale de un registro oficial completo.
- **Dato aproximado:** es oficial, pero la zona tiene poca población o la fuente no está completa.
- **Dato poco seguro:** faltan bastantes datos en la fuente.
- **Sin datos:** no lo tenemos.

Usamos estas etiquetas según la fiabilidad del dato, que va de 0 a 1:
- **0,8 o más:** dato fiable.
- **De 0,5 a menos de 0,8:** dato aproximado.
- **Más de 0 y menos de 0,5:** dato poco seguro.
- **0:** sin datos.

El 0,5 cuenta como aproximado porque es la fiabilidad que reciben siempre las zonas con poca población.

La fiabilidad baja en estos casos:
- **Zonas con poca población.** En un pueblo pequeño, un solo centro más o menos cambia mucho la cuenta, así que el dato cuenta como aproximado. Pasa con menos de 500 menores de 15 años en colegios, menos de 2.000 habitantes en centros de salud y menos de 500 personas mayores en residencias.
- **Fuentes incompletas.** Por ejemplo, si de algunas residencias no se publica cuántas plazas tienen, cuanto mayor es esa parte, menos nos fiamos.
- **Cuentas aproximadas.** Por ejemplo, la fuente agrupa los hogares de «5 o más personas» y los contamos como de 5.

### 1.7 Qué datos usamos
- **21 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid:** población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias y las 6 redes de transporte público del Consorcio Regional de Transportes de Madrid, que también se publican en ese portal.
- **Como apoyo,** el padrón y el panel de distritos del Ayuntamiento de Madrid para la población y los hogares de cada distrito de Madrid capital, y el mapa de calles de OpenStreetMap para las distancias a pie.
- **Antes de usar un conjunto,** pasa un control de calidad: que no haya registros repetidos, que cada municipio exista, que los errores queden apartados y que un dato que falta no se convierta en un cero.
- **Cada resultado** dice de qué conjuntos sale, con el enlace a su ficha en el portal, su versión y su licencia.
- **Ver la lista completa** (enlace a `pitch/datasets_cm.md` en el repositorio).

### 1.8 Lo que estos datos no te dicen
- **Contamos centros, no plazas.** Un colegio grande y uno pequeño cuentan igual, y un consultorio rural cuenta como un centro de salud. En mayores sí contamos plazas, pero autorizadas: no sabemos cuántas están libres.
- **Colegios** **[pendiente de A: hoy la cuenta incluye también escuelas infantiles e institutos públicos; GAP-001 lo separa. Quitar esta línea cuando esté corregido.]**
- **Alquiler:** la Comunidad solo publica el precio medio de los municipios de más de 20.000 habitantes. En los demás no tenemos el dato y lo decimos.
- **Compra:** el precio de compra es solo orientativo. **[pendiente de A: DATA-021. Si no hay una fuente oficial fiable, decir: «Todavía no tenemos precios oficiales de compra por zona, así que no podemos comprobar si una zona entra en tu presupuesto».]**
- **Seguridad:** solo hay datos de Madrid capital, por distrito. Usamos las actuaciones de la Policía Municipal registradas por cada 1.000 habitantes y solo cuentan si marcas «Seguridad». Nunca usamos datos sobre las personas (como la nacionalidad) ni ponemos etiquetas a ninguna zona. Fuera de Madrid capital sale «sin datos». **[pendiente de A: DATA-020.]**
- **Zonas verdes y «sin escaleras»:** **[pendiente de A: DATA-018 y DATA-019. Decir dónde hay datos (parques: Ayuntamiento en Madrid capital y OpenStreetMap en el resto; sin escaleras: estaciones de metro y Cercanías, y edificios públicos del Ayuntamiento) y que en lo demás sale «sin datos».]**
- **No enseñamos pisos en venta ni en alquiler.** Te ayudamos a elegir zona; el piso lo buscas donde prefieras.
- **Todavía no sabemos qué echan en falta los vecinos.** Hoy todo sale de datos oficiales. Más adelante queremos sumar lo que la gente diga que necesita, siempre de forma anónima y por zonas.
- **Cada dato tiene su fecha.** Algunos horarios de transporte son los últimos publicados aunque ya estén caducados (el del metro venció en mayo de 2026). Lo avisamos.

### 1.9 Tu privacidad
No te pedimos nombre ni cuenta. Solo trabajamos con datos de zonas, nunca de personas.

### 1.10 Versiones
- Método de «Qué falta»: `{method.version}` (hoy, `gap-0.1`).
- Método del encaje: `{methodology_version}` **[pendiente de A: CORE-003]**.

---

## Parte 2 · Notas internas: de dónde sale cada afirmación

| Sección | Afirmación | Fuente | Estado |
|---|---|---|---|
| 1.2 | 179 municipios + 21 distritos | `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json` · D-200 · D-209 | Hecho (DATA-012, `be40c2f`) |
| 1.7 | Ayuntamiento como apoyo | `pitch/datasets_cm.md` §3 (`ayto_padron_municipal`, `ayto_panel_indicadores_distritos_barrios`) · D-209 | Hecho |
| 1.3 | Condiciones PASS / FAIL / UNKNOWN; UNKNOWN nunca es PASS; `results` solo con todo en PASS; `near_misses` | `packages/contracts/src/hi_contracts/public/search.py` · `CLAUDE.md` §14 · `docs/04_technical_architecture/31_public_api_routes.md` | Contrato hecho; cálculo **pendiente de A** (CORE-003) |
| 1.3 | % de encaje, no nota; 3–5 hechos con su confianza | D-202 · `search.py` (`match_pct`, `facts`) | Contrato hecho |
| 1.3 | Alquiler estimado = €/m² × m² | `data/catalog/features/alquiler_m2_mensual.yaml` · `search.py` (`estimated_cost_eur`, `min_floor_area_m2`: «None = derived from the household size») | **Pendiente de A** (CORE-006) |
| 1.4 | Referencia = total de la región / su población; cortes 0,8 y 1,0 | `packages/domain/src/hi_domain/gaps.py` (`GAP_METHOD`, `gap-0.1`) · `services/features/src/hi_features/methods.py` (`_regional_reference`) | Hecho y provisional (ADR de GAP-001) |
| 1.4 | Móstoles: 0,47 frente a 0,59; ratio 0,789 | `data/fixtures/contracts/zone_gap_list.mostoles.fixture.json` = `GET /api/v1/gaps/municipio/28092` | Hecho y provisional |
| 1.4 | Colegios: públicos por 1.000 menores de 15; centros de salud: centros de salud y consultorios por 10.000 habitantes | `data/catalog/features/colegios_publicos_por_1000_menores.yaml` · `centros_salud_por_10000_hab.yaml` | Hecho |
| 1.4 | Mayores: plazas autorizadas por 100 personas de 65 o más | `data/catalog/features/plazas_residencia_por_100_mayores.yaml` | Feature hecha; fila **pendiente de A** |
| 1.5 | Por la red de calles de OSM, no en línea recta | D-210 · `packages/domain/src/hi_domain/access/walk.py` · `evidence/gate-01/2026-11-11/osm_red_peatonal/` | Hecho (CORE-005, `fc025b6`, Gate 3 PASS) |
| 1.5 | 4 km/h, el paso del estudio «El Madrid de los 15 minutos» del Ayuntamiento | Decisión de Mariano (11 nov), D-211. El estudio: «Velocidad de desplazamiento estimada en 4 Km/h» (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf) · `speed_kmh: 4.0` en `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` (versión 2) | Hecho (CORE-005 Fase 5, `ad2129a`, Gate 3 PASS: `evidence/gate-03/2026-11-11/phase-core005-f5.txt`) |
| 1.5 | 10 minutos andando son unos 670 metros | D-211 («Efecto»: 5 min ≈ 333 m, 10 min ≈ 667 m, 15 min ≈ 1.000 m) | Hecho |
| 1.5 | 6 destinos; mediana de minutos y % de calle a 10 min (15 el centro de salud, 5 la parada) | `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` (`subcategories`, ventanas) · D-210 | Hecho; en la web, **pendiente de A** (API, con GAP-001) |
| 1.5 | Sin calles en el mapa: «sin datos», nunca 0 | D-210 (`SOURCE_NO_COVERAGE`, 24 secciones) · `null_policy` en los YAML · `evidence/gate-03/2026-11-11/walk-coverage.txt` · 15 casos golden y coherencia mediana/% en `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (a 4 km/h; D-211) | Hecho (Gate 3 PASS) |
| 1.6 | Etiquetas: ≥ 0,8 fiable; 0,5 ≤ c < 0,8 aproximado; 0 < c < 0,5 poco seguro; 0 sin datos | Criterio de D (`pitch/textos_web.md` §6), confirmado por A el 11 nov. Tope de 0,5 en zonas pequeñas: D-189. Rango 0–1 y 0 = desconocido: `packages/contracts/src/hi_contracts/public/common.py` (`Confidence`) | Hecho |
| 1.6 | Confianza ≤ 0,5 en zonas pequeñas; umbrales 500 / 2.000 / 500 | `services/features/src/hi_features/methods.py` (`SMALL_POPULATION_CONFIDENCE`) · `small_population_threshold` en los 3 YAML de features | Hecho |
| 1.6 | Fuente incompleta: confianza = parte de residencias con plazas conocidas | `methods.py` (suma de atributos: «Places lacking it lower confidence») | Hecho |
| 1.6 | «5 o más» contado como 5 (confianza 0,9) | `data/catalog/features/tamano_medio_hogar.yaml` | Hecho |
| 1.7 | 21 conjuntos CM, 6 del CRTM con ficha en el portal | `pitch/datasets_cm.md` · D-196 | Hecho |
| 1.7 | Control de calidad | `evidence/gate-01/*/<dataset>/quality_report.json` | Hecho |
| 1.8 | Alquiler: solo municipios de más de 20.000 habitantes | `alquiler_m2_mensual.yaml` (`limitations`) · título del dataset en `pitch/datasets_cm.md` | Hecho |
| 1.8 | Compra orientativa o SIN DATOS | D-203 | **Pendiente de A** (DATA-021) |
| 1.8 | Seguridad: Madrid capital, por distrito, por 1.000 habitantes, sin datos de personas ni etiquetas, solo si se marca | D-204 · D-205 | **Pendiente de A** (DATA-020) |
| 1.8 | Zonas verdes y «sin escaleras» | D-205 | **Pendiente de A** (DATA-018 y DATA-019) |
| 1.8 | Necesidad declarada: siguiente paso, nunca simulada | D-194 | Hecho (no está en la demo) |
| 1.8 | GTFS de metro vencido el 27-05-2026 | `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` (`feed_current`) · D-196 | Hecho |
| 1.9 | Sin cuenta; solo datos de zonas | Brief de diseño (sin login) · D-186 · D-197 | Hecho. No se afirma nada sobre registros del servidor: C no lo ha documentado |
| 1.10 | Versiones de método | `GapMethod.version` · `SearchResult.methodology_version` | `gap-0.1` hecho; encaje **pendiente de A** |
