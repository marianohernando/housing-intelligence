# «Cómo lo calculamos» — contenido de la pestaña

Para la línea B. La **parte 1** es el texto de la pestaña, en español llano. La **parte 2** es interna: de dónde sale cada afirmación y qué falta.

**Marcas en la parte 1:**
- Los párrafos con **[pendiente de A: …]** no se publican hasta que A lo tenga hecho. Si el 16 nov no existe, B quita el párrafo entero; no se deja un hueco ni un «próximamente».
- **Cambio del 11 nov (D-213):** la sección 1.4 sustituye la comparación con toda la región por la comparación con los municipios del mismo tipo. B tiene que cambiar la tabla de estados y el ejemplo de «Cómo lo calculamos», y la primera de las «Tres reglas» (1.1).

Los textos de B en `apps/web/src/app/(vida)/como-lo-calculamos/page.tsx` («Tres reglas que seguimos siempre») encajan con la sección 1.1 y se mantienen.

---

## Parte 1 · Texto de la pestaña

### 1.1 Tres reglas que seguimos siempre
- Comparamos cada zona con los demás municipios de la Comunidad de Madrid de su mismo tipo, urbanos o rurales, siempre según cuánta gente vive en ella.
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
Para cada servicio contamos cuántos hay en la zona por cada número fijo de vecinos. Por ejemplo, centros de salud por cada 10.000 habitantes.

Después comparamos la zona con **los demás municipios de su mismo tipo** en la Comunidad de Madrid: los rurales con los rurales y los urbanos con los urbanos. Rural es lo que dice la ley de medio rural: menos de 30.000 habitantes y menos de 100 por km². Los distritos de Madrid son urbanos. Una zona nunca se compara consigo misma: un distrito de Madrid se compara con los demás municipios urbanos, sin contar Madrid.

¿Por qué no con toda la región? Porque cada pueblo tiene su consultorio. Por habitante, los municipios rurales tienen casi 15 veces más centros de salud que los urbanos, así que con la media de toda la región a cualquier ciudad le faltaría de todo.

| Si la zona tiene… | Sale |
|---|---|
| menos del 80 % de lo que tienen los municipios de su tipo, y la diferencia no se explica por el tamaño de la zona | **FALTA** |
| menos de lo que tienen los municipios de su tipo, pero sin llegar a FALTA | **JUSTO** |
| lo mismo o más | **CUBIERTO** |
| no tenemos el dato | **SIN DATOS** |

**¿Por qué el tamaño importa?** En una zona con poca gente, un centro más o menos cambia mucho la cuenta. Por eso, para decir FALTA pedimos además que la diferencia sea demasiado grande para ser casualidad. Es la misma prueba que usan los indicadores de salud pública de Inglaterra. Si una zona es tan pequeña que ni siquiera no tener ninguno bastaría para decir que le falta, la marcamos como **zona pequeña para comparar** y nunca sale FALTA. Por ejemplo, La Acebeda, con 70 habitantes, no tiene farmacia, pero con su tamaño eso no basta para decir que le falta.

**Ejemplo real.** Madrid capital tiene 0,37 centros de atención primaria por cada 10.000 habitantes y los demás municipios urbanos, 0,56. Es un tercio menos y, con tanta población, no es casualidad: sale **FALTA**. Ningún distrito por separado basta para afirmarlo: Chamartín tiene 0,47 y sale **JUSTO**.

Es una señal para saber dónde mirar primero, no un veredicto: comparamos con zonas parecidas, no con una norma oficial que diga cuántos centros debería haber.

**Lo que mide cada fila** (para los 179 municipios y los 21 distritos de Madrid):
- **Escuelas infantiles:** escuelas infantiles, públicas y privadas, por cada 1.000 niños de 0 a 4 años.
- **Colegios:** colegios con primaria, públicos o concertados, por cada 1.000 menores de 15 años.
- **Centros de salud:** centros de atención primaria (centros de salud y consultorios) por cada 10.000 habitantes.
- **Centros de mayores:** hogares, clubes y centros de día por cada 1.000 personas de 65 años o más. Son centros, no plazas; las residencias van aparte.
- **Farmacias:** farmacias por cada 10.000 habitantes.
- **Vivienda para familias:** viviendas de más de 90 m² por cada 100 hogares de 4 o más personas. En los distritos de Madrid sale «sin datos», porque la Comunidad no publica estas tablas por distrito.

Cada fila, salvo la de vivienda, dice además cuántos minutos se tarda andando hasta el más cercano (sección 1.5).

### 1.5 Distancias a pie
Medimos lo que tardarías andando por las calles de verdad, no en línea recta, a un paso tranquilo de 4 km/h, con el mapa de calles de OpenStreetMap. Desde cada calle donde vive gente calculamos cuánto se tarda hasta lo más cercano: escuela infantil, colegio con primaria (público o concertado), centro de salud o consultorio, farmacia, centro de mayores y parada de autobús, metro o Cercanías. En cada fila de «Qué falta» verás los minutos en los que se llega desde la mitad de las calles de la zona. A ese paso, 10 minutos son unos 670 metros. Si en una zona no hay calles en el mapa, sale «sin datos», nunca cero. Usamos el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento.

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
- **Zonas con poca población.** En un pueblo pequeño, un solo centro más o menos cambia mucho la cuenta, así que el dato cuenta como aproximado. Pasa con menos de 200 niños de 0 a 4 años en escuelas infantiles, menos de 500 menores de 15 años en colegios, menos de 2.000 habitantes en centros de salud y en farmacias, menos de 300 personas mayores en centros de mayores y menos de 100 hogares de 4 o más personas en vivienda. Esto mide cuánto nos fiamos del dato; si la zona es demasiado pequeña para comparar, se ve aparte (sección 1.4).
- **Fuentes incompletas.** Por ejemplo, si de algunas residencias no se publica cuántas plazas tienen, cuanto mayor es esa parte, menos nos fiamos.
- **Cuentas aproximadas.** Por ejemplo, la fuente agrupa los hogares de «5 o más personas» y los contamos como de 5.

### 1.7 Qué datos usamos
- **21 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid:** población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias y las 6 redes de transporte público del Consorcio Regional de Transportes de Madrid, que también se publican en ese portal.
- **Como apoyo,** el padrón y el panel de distritos del Ayuntamiento de Madrid para la población y los hogares de cada distrito de Madrid capital, y el mapa de calles de OpenStreetMap para las distancias a pie.
- **Antes de usar un conjunto,** pasa un control de calidad: que no haya registros repetidos, que cada municipio exista, que los errores queden apartados y que un dato que falta no se convierta en un cero.
- **Cada resultado** dice de qué conjuntos sale, con el enlace a su ficha en el portal, su versión y su licencia.
- **Ver la lista completa** (enlace a `pitch/datasets_cm.md` en el repositorio).

### 1.8 Lo que estos datos no te dicen
- **Contamos centros, no plazas.** Un colegio grande y uno pequeño cuentan igual, y un consultorio rural cuenta como un centro de salud. Las plazas de residencia de mayores van aparte y son plazas autorizadas: no sabemos cuántas están libres.
- **Vivienda:** comparamos las viviendas grandes con los hogares grandes, no el mercado. No sabemos cuántas están libres ni a qué precio.
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
- Método de «Qué falta»: `{method.version}` (hoy, `gap-0.2`).
- Método del encaje: `{methodology_version}` **[pendiente de A: CORE-003]**.

---

## Parte 2 · Notas internas: de dónde sale cada afirmación

| Sección | Afirmación | Fuente | Estado |
|---|---|---|---|
| 1.2 | 179 municipios + 21 distritos, con su nombre oficial («Redueña», «Griñón», «El Álamo», «Vicálvaro») | `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json` · D-200 · D-209 · nombres: D-212 (`evidence/gate-01/2026-11-11/phase-data022-f1.txt`) | Hecho (DATA-012, `be40c2f`; DATA-022, `c4f1bc0`) |
| 1.7 | Ayuntamiento como apoyo | `pitch/datasets_cm.md` §3 (`ayto_padron_municipal`, `ayto_panel_indicadores_distritos_barrios`) · D-209 | Hecho |
| 1.3 | Condiciones PASS / FAIL / UNKNOWN; UNKNOWN nunca es PASS; `results` solo con todo en PASS; `near_misses` | `packages/contracts/src/hi_contracts/public/search.py` · `CLAUDE.md` §14 · `docs/04_technical_architecture/31_public_api_routes.md` | Contrato hecho; cálculo **pendiente de A** (CORE-003) |
| 1.3 | % de encaje, no nota; 3–5 hechos con su confianza | D-202 · `search.py` (`match_pct`, `facts`) | Contrato hecho |
| 1.3 | Alquiler estimado = €/m² × m² | `data/catalog/features/alquiler_m2_mensual.yaml` · `search.py` (`estimated_cost_eur`, `min_floor_area_m2`: «None = derived from the household size») | **Pendiente de A** (CORE-006) |
| 1.4 | Referencia = los demás municipios del mismo tipo (rural o urbano, Ley 45/2007 art. 3.a: < 30.000 hab. y < 100 hab./km²), sin el municipio de la zona; los distritos heredan el tipo de su municipio | D-213 (punto 1) · `packages/domain/src/hi_domain/gaps.py` (`gap-0.2`) · `apps/api/src/hi_api/services/gap_reference.py` · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt` (84 rurales, 95 urbanos) | Hecho (GAP-001 F5, `d02574f`, `f626e1f`). La demo pública lo enseña cuando C despliegue (hoy `/gaps` aún da `gap-0.1`) |
| 1.4 | Rurales, 14,8 veces más centros de atención primaria por habitante; la diferencia rural/urbano es significativa en las 6 filas | D-213 (tabla χ²) · `phase-gap001-f5-review.txt` | Hecho |
| 1.4 | FALTA = ratio < 0,8 y significativa (intervalo exacto de Poisson al 95 %); CUBIERTO = ratio ≥ 1; JUSTO, el resto | D-213 (punto 2: regla de los cuatro quintos, Garwood, Fingertips, Spiegelhalter 2005) | Hecho |
| 1.4 | Zona pequeña para comparar (casos esperados < 3,69): nunca FALTA; La Acebeda, sin farmacia y con 70 habitantes | D-213 (punto 3, `reliable: false`) · `phase-gap001-f5-review.txt` («La Acebeda farmacia JUSTO … fiable False») · `poblacion_total` de 28001 en `feature_value` | Hecho en la API; en la web, **pendiente de B** (texto en `pitch/textos_web.md`, `fila.zona_pequena`) |
| 1.4 | Madrid capital, centros de salud: 0,37 frente a 0,56, FALTA (ratio 0,67); ningún distrito solo; Chamartín 0,47, JUSTO (0,84) | D-213 («Efecto») · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` (`ratio_to_reference` 0,6681) · `phase-gap001-f5-review.txt` («distrito centro_salud … FAL 0 JUS 21») | Hecho en local; comprobar en la demo tras el despliegue de C |
| 1.4 | Las 6 filas y lo que mide cada una, por municipio y por distrito | `gap_row` (`phrase`, `proxy_note`) en `data/catalog/features/`: `escuelas_infantiles_por_1000_ninos.yaml`, `colegios_publicos_por_1000_menores.yaml` (v2), `centros_salud_por_10000_hab.yaml`, `centros_mayores_por_1000_mayores.yaml`, `oficinas_farmacia_por_10000_hab.yaml`, `viviendas_grandes_por_100_hogares_grandes.yaml` · `evidence/gate-04/2026-11-11/phase-gap001-f2.txt`, `-f3a.txt`, `-f3b.txt` | Hecho (GAP-001 F2 `21939dd`, F3a `4523d69`, F3b `98b842a`) |
| 1.4 | Colegios: solo con primaria, públicos o concertados (antes contaba también infantiles, institutos y escuelas de música) | `colegios_publicos_por_1000_menores.yaml` v2 (`limitations`) · commit `21939dd` («v1 counted every public education centre, including nurseries, institutos, music and adult schools») · `phase-gap001-f2.txt` (región 2,178 → 1,315; 1.241 colegios en la región) | Hecho |
| 1.4 | Mayores: centros (hogares, clubes y centros de día), no plazas; residencias aparte | `centros_mayores_por_1000_mayores.yaml` (`proxy_note`) · `plazas_residencia_por_100_mayores.yaml` (dato extra de la fila) | Hecho |
| 1.4 | Vivienda: SIN DATOS en los distritos de Madrid | `viviendas_grandes_por_100_hogares_grandes.yaml` (`levels.distrito: not_published`, `limitations`) · `phase-gap001-f3b.txt` (Chamartín: `SOURCE_MISSING`) | Hecho |
| 1.5 | Por la red de calles de OSM, no en línea recta | D-210 · `packages/domain/src/hi_domain/access/walk.py` · `evidence/gate-01/2026-11-11/osm_red_peatonal/` | Hecho (CORE-005, `fc025b6`, Gate 3 PASS) |
| 1.5 | 4 km/h, el paso del estudio «El Madrid de los 15 minutos» del Ayuntamiento | Decisión de Mariano (11 nov), D-211. El estudio: «Velocidad de desplazamiento estimada en 4 Km/h» (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf) · `speed_kmh: 4.0` en `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` (versión 2) | Hecho (CORE-005 Fase 5, `ad2129a`, Gate 3 PASS: `evidence/gate-03/2026-11-11/phase-core005-f5.txt`) |
| 1.5 | 10 minutos andando son unos 670 metros | D-211 («Efecto»: 5 min ≈ 333 m, 10 min ≈ 667 m, 15 min ≈ 1.000 m) | Hecho |
| 1.5 | 6 destinos; en cada fila, los minutos de la mitad de las calles (mediana) | `data/catalog/features/min_a_pie_*.yaml` · D-210 · `/gaps` los da en `extra_indicators` (GAP-001 F1, `2d05d78`) · en la web: `evidence/map-004/2026-11-11/c4_que_falta_completa_desktop.png` (MAP-004 y PUB-001, `bd5b006`) | Hecho. La web redondea al minuto: Chamartín, 9,47 min al centro de salud, sale «9 min». El % de calle a 10 min (`pct_calle_*.yaml`) se calcula pero no se enseña, así que la parte 1 no lo nombra |
| 1.5 | Sin calles en el mapa: «sin datos», nunca 0 | D-210 (`SOURCE_NO_COVERAGE`, 24 secciones) · `null_policy` en los YAML · `evidence/gate-03/2026-11-11/walk-coverage.txt` · 15 casos golden y coherencia mediana/% en `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (a 4 km/h; D-211) | Hecho (Gate 3 PASS) |
| 1.6 | Etiquetas: ≥ 0,8 fiable; 0,5 ≤ c < 0,8 aproximado; 0 < c < 0,5 poco seguro; 0 sin datos | Criterio de D (`pitch/textos_web.md` §6), confirmado por A el 11 nov. Tope de 0,5 en zonas pequeñas: D-189. Rango 0–1 y 0 = desconocido: `packages/contracts/src/hi_contracts/public/common.py` (`Confidence`) | Hecho |
| 1.6 | Confianza ≤ 0,5 en zonas pequeñas; umbrales 200 / 500 / 2.000 / 300 / 2.000 / 100 | `services/features/src/hi_features/methods.py` (`SMALL_POPULATION_CONFIDENCE`) · `small_population_threshold` en los 6 YAML de las filas | Hecho. D-213 no lo cambia: la confianza mide el dato y la «zona pequeña para comparar» va aparte (punto 3) |
| 1.6 | Fuente incompleta: confianza = parte de residencias con plazas conocidas | `methods.py` (suma de atributos: «Places lacking it lower confidence») | Hecho |
| 1.6 | «5 o más» contado como 5 (confianza 0,9) | `data/catalog/features/tamano_medio_hogar.yaml` | Hecho |
| 1.7 | 21 conjuntos CM, 6 del CRTM con ficha en el portal | `pitch/datasets_cm.md` · D-196 | Hecho |
| 1.7 | Control de calidad | `evidence/gate-01/*/<dataset>/quality_report.json` | Hecho |
| 1.8 | Centros, no plazas; residencias aparte y con plazas autorizadas; vivienda: parque, no mercado | `proxy_note` de las 6 filas · `plazas_residencia_por_100_mayores.yaml` · `viviendas_grandes_por_100_hogares_grandes.yaml` (`limitations`) | Hecho |
| 1.8 | Alquiler: solo municipios de más de 20.000 habitantes | `alquiler_m2_mensual.yaml` (`limitations`) · título del dataset en `pitch/datasets_cm.md` | Hecho |
| 1.8 | Compra orientativa o SIN DATOS | D-203 | **Pendiente de A** (DATA-021) |
| 1.8 | Seguridad: Madrid capital, por distrito, por 1.000 habitantes, sin datos de personas ni etiquetas, solo si se marca | D-204 · D-205 | **Pendiente de A** (DATA-020) |
| 1.8 | Zonas verdes y «sin escaleras» | D-205 | **Pendiente de A** (DATA-018 y DATA-019) |
| 1.8 | Necesidad declarada: siguiente paso, nunca simulada | D-194 | Hecho (no está en la demo) |
| 1.8 | GTFS de metro vencido el 27-05-2026 | `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` (`feed_current`) · D-196 | Hecho |
| 1.9 | Sin cuenta; solo datos de zonas | Brief de diseño (sin login) · D-186 · D-197 | Hecho. No se afirma nada sobre registros del servidor: C no lo ha documentado |
| 1.10 | Versiones de método | `GapMethod.version` · `SearchResult.methodology_version` | `gap-0.2` hecho (D-213); encaje **pendiente de A** |
