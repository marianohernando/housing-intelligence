# DATA-019 · Estaciones sin escaleras: fuente, lectura del grado y enlace con el GTFS (D-223)

Fecha: 2026-11-12. Línea A.

## 1. Fuente
Portal de datos abiertos de la Comunidad de Madrid (publica el CRTM, licencia CRTM-LDA, cita obligatoria):
- «Topología de la Red de Metro»: `datos.comunidad.madrid/dataset/red_de_metro_lineas_estaciones_accesos_vestibulos_andenes`
- «Topología de la Red de Metro Ligero / Tranvía»: `…/red_de_metro_ligero_tranvia_lineas_estaciones_accesos_vestibulos_andenes`
- «Topología de la Red de Cercanías Madrid»: `…/red_de_cercanias_lineas_estaciones_accesos_vestibulos_andenes`

Cada ficha lleva al servicio ArcGIS del CRTM (`M4_Red`, `M10_Red`, `M5_Red`); se descarga solo la capa 0 (estaciones) con 4 campos. Resultado de las cargas (`evidence/gate-01/2026-11-12/crtm_topologia_*/quality_report.json`):

| Red | Estaciones | T | P | N | Cuarentena |
|---|---|---|---|---|---|
| Metro | 293 | 195 | 6 | 92 | 0 |
| Metro Ligero | 57 | 57 | 0 | 0 | 0 |
| Cercanías | 111 | 42 | 28 | 41 | 0 |

## 2. Qué significa T (sin diccionario publicado)
Ni la ficha CM, ni el ítem de ArcGIS (metadatos ISO), ni la serie de metadatos del CRTM definen `GRADOACCESIBILIDAD`. Se contrasta con lo que publican la Comunidad de Madrid y el CRTM (consultado el 12 nov):
- comunidad.madrid, «Accesibilidad en el transporte público», sección Metro Ligero: «El 100% de la red es accesible.»
- crtm.es, «Accesibilidad en el transporte»: «los autobuses urbanos e interurbanos, los Metros Ligeros y los intercambiadores cuentan ya con un 100% de accesibilidad» y, de Metro, «el 70% de las estaciones están actualmente adaptadas».

La capa da T a las 57 estaciones de Metro Ligero (100 %) y a 195 de 293 en metro (66,6 %; T o P: 68,6 %). Lectura: T = accesibilidad total (cuenta como sin escaleras); P = parcial y N = no (no cuentan).

## 3. El `wheelchair_boarding` del GTFS del CRTM no sigue el estándar
`uv run python scripts/audit_step_free.py` (paradas del GTFS con su estación de la topología):

## crtm_gtfs_metro frente a crtm_topologia_metro: paradas por código GTFS y grado de la topología
| wheelchair_boarding | T | P | N | no está |
|---|---|---|---|---|
| 0 | 414 | 15 | 320 | 0 |
| 1 | 3 | 3 | 0 | 0 |
| 2 | 282 | 0 | 0 | 0 |

## crtm_gtfs_metro_ligero frente a crtm_topologia_metro_ligero: paradas por código GTFS y grado de la topología
| wheelchair_boarding | T | P | N | no está |
|---|---|---|---|---|
| 0 | 25 | 0 | 0 | 0 |
| 2 | 71 | 0 | 0 | 0 |

En el estándar GTFS, 2 = «no se puede subir en silla de ruedas». En el CRTM, el 2 solo aparece en estaciones T y en todo Metro Ligero, que la CM y el CRTM declaran accesible al 100 %. El código no se usa: desde `gtfs-1.2.0` se guarda tal cual (`gtfs_wheelchair_boarding`).

## 4. Enlace con las estaciones del GTFS
Quality Gate `step_free_read` de cada GTFS de tren (`evidence/gate-01/2026-11-12/crtm_gtfs_*/quality_report.json`):

| GTFS | Estaciones | Con lectura | sí | parcial | no | Sin dato |
|---|---|---|---|---|---|---|
| Metro | 230 | 100 % | 148 | 2 | 80 | 0 |
| Metro Ligero | 56 | 100 % | 56 | 0 | 0 | 0 |
| Cercanías | 93 | 97,85 % | 26 | 26 | 39 | 2 (Méndez Álvaro P.V., Vallecas: su código no está en la topología) |

Intercambiadores del metro (un lugar en el GTFS, una estación por línea en la topología; cuenta el menos accesible): Sol (4_12, 4_35, 4_48) sí; Nuevos Ministerios sí; Moncloa sí; Plaza Elíptica sí; Chamartín sí; Plaza de Castilla parcial; Príncipe Pío parcial; Avenida de América no; Méndez Álvaro no.

Los 6 GTFS se recargaron desde su mismo Bronze (`--local`, sin descargar horarios nuevos): mismos lugares (metro 230, Metro Ligero 56, Cercanías 93, EMT 4.935, urbanos 3.023, interurbanos 6.645) y ningún `wheelchair_boarding` interpretado.

## 5. Feature `min_a_pie_estacion_sin_escaleras`
`uv run hi-features compute --feature min_a_pie_estacion_sin_escaleras`: 4.843 filas, 4.819 con valor y 24 desconocidas (secciones sin calles conectadas). En las 199 zonas del buscador: 5 a 10 min o menos, 29 entre 10 y 30 y 165 a más de 30 (puntúan 0 con confidence ≤ 0,5). Referencia regional: 85,8 min.

Municipios a 30 min o menos: Parla 8,1 · Coslada 12,0 · Alcorcón 14,8 · Getafe 14,9 · Leganés 15,8 · Móstoles 16,8 · Alcobendas 16,8 · Fuenlabrada 17,2 · Pozuelo de Alarcón 20,6 · San Sebastián de los Reyes 20,8 · Rivas-Vaciamadrid 20,8 · Arganda del Rey 23,3 · Zarzalejo 25,3. Distritos de Madrid: de Chamberí 6,8 y Centro 7,2 a Vicálvaro 24,1 y Usera 25,5.

## 6. Búsqueda
`uv run python scripts/golden_search.py` → 8/8 (`evidence/gate-04/2026-11-12/golden-search-sin-escaleras.txt`). Escenario nuevo `golden_reduced_mobility` («sin escaleras» primero): Ciudad Lineal 10 min, Latina 13, Carabanchel 12, Parla 8 y Coslada 12.
