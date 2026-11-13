# DATA-020 F1 · Seguridad: fuentes de Madrid capital (D-226)

Fecha: 2026-11-12. Línea A. Petición de Mariano a través de `datamad-10`. Es una evaluación de solo lectura: no se ha cargado nada en la base. Las fichas se consultaron por la API CKAN de datos.madrid.es (`package_show`). Los ficheros se descargaron el 12 nov a una carpeta temporal y no se versionan. Las cifras son cálculos de evaluación.

## 1. Fuentes comprobadas
| Fuente | Ficha (datos.madrid.es) | Licencia (CKAN) | Granularidad | Última actualización |
|---|---|---|---|---|
| Policía Municipal. Datos estadísticos de actuaciones | `212616-0-policia-estadisticas` | `cc-by` (CC BY 4.0) | Un XLSX por mes. En la hoja «SEGURIDAD», los 21 distritos con 5 columnas: relacionadas con las personas, con el patrimonio, tenencia de armas, tenencia de drogas y consumo de drogas. También detenidos por distrito y atestados de accidente por distrito | 26 oct 2026 (septiembre de 2026) |
| Encuesta de calidad de vida y satisfacción con los servicios públicos (resultados) | `319934-0-encuesta-calidad-de-vida-resultados` | `cc-by` | Bloque 7, «Seguridad y Emergencias» 2021–2025, por distrito: percepción de seguridad en la ciudad, en el distrito y en el barrio o zona donde vive, de día y de noche, de 0 a 10 | 21 oct 2026 (edición 2025) |
| Panel de indicadores de distritos y barrios (ya cargado, `ayto_panel_indicadores_distritos_barrios`) | `300087-0-indicadores-distritos` | CC BY 4.0 (fuente `ayuntamiento_madrid_ckan`) | Repite las dos anteriores por distrito: «Percepción de seguridad en el barrio por el día / por la noche» (encuesta de 2025) e «Intervenciones de la policía municipal…» (año 2025) | panel 2026 (Bronze `11a758e6249d`) |
| Accidentes de tráfico de la ciudad de Madrid | `300228-0-accidentes-trafico-detalle` | `cc-by` | Una fila por persona implicada, con expediente, distrito, tipo de accidente, tipo de persona, lesividad y coordenadas UTM. Desde 2019. Provisional hasta seis meses después de cerrar el año | 5 nov 2026 (hasta septiembre de 2026) |

Ninguna fuente tiene filas por persona residente. El fichero de accidentes trae la edad y el sexo de los implicados; si se usara alguna vez, solo se contarían expedientes.

## 2. Percepción vecinal (encuesta de 2025)
- Ficha técnica («Marco de estudio»): 8.893 personas de 16 años o más que residen en Madrid, unas 400 por distrito. Muestreo estratificado por distrito y sección censal, ponderado por distrito, sexo y edad según el padrón. Error de muestreo de ±4,9 % por distrito (para una proporción, al 95,5 %). Trabajo de campo del 19 sep al 30 oct de 2025.
- Ítem: «Percepción de seguridad en el barrio o la zona donde vive durante la noche», de 0 a 10. Son los vecinos valorando su propio barrio, así que no tiene el problema de denominador de D-224 (no cuenta a quien está de paso).
- Valores de 2025, de noche: Madrid 6,4; Villaverde 4,9; Puente de Vallecas 5,1; Usera 5,2; Carabanchel 5,8; Tetuán, Villa de Vallecas y San Blas-Canillejas 6,1; Latina y Ciudad Lineal 6,2; Centro y Vicálvaro 6,5; Moratalaz 6,8; Arganzuela y Hortaleza 7,0; Fuencarral-El Pardo 7,2; Chamartín y Moncloa-Aravaca 7,3; Retiro 7,4; Salamanca 7,5; Chamberí y Barajas 7,7. De día, Madrid 7,8 (de 6,8 a 8,6).
- **El panel coincide con la encuesta** en los 21 distritos comprobados (noche: Villaverde 4,9, Chamberí 7,7, Centro 6,5, Hortaleza 7,0…). Se puede leer del panel, que ya se carga.
- **Riesgo de estigma:** una cifra baja puede leerse como una etiqueta del barrio. Por eso, si se enseña, va como lo que es («así valoran sus vecinos la seguridad de su barrio de noche»), con la media de Madrid y sin colores de alarma ni palabras como «peligroso» (D-075, CLAUDE.md §11).

## 3. Policía Municipal: actuaciones de seguridad ciudadana en 2025
Suma de los 12 ficheros mensuales de 2025 (hoja «SEGURIDAD»). La fila «SIN DISTRITO ASIGNADO» vale 0. Totales de la ciudad: personas 1.961, patrimonio 4.035, armas 566, tenencia de drogas 6.784 y consumo de drogas 635.

| Distrito | Personas | Patrimonio | Tenencia de drogas |
|---|---|---|---|
| Centro | 265 | 1.363 | 1.878 |
| Puente de Vallecas | 329 | 398 | 1.011 |
| Salamanca | 44 | 349 | 76 |
| Carabanchel | 180 | 185 | 396 |
| Chamartín | 78 | 144 | 620 |
| Vicálvaro | 38 | 53 | 54 |
| Moratalaz | 24 | 94 | 73 |

- **La copia del panel tiene errores.** Distritos distintos repiten valores que la fuente mensual no tiene:
  - Salamanca, Chamberí y Barajas, 44 / 57 / 205;
  - Hortaleza y Vicálvaro, 38 / 76 / 386;
  - Latina y Villa de Vallecas, 95 / 105 / 284;
  - Ciudad Lineal y Chamartín, 78 / 144 / 806.

  En la fuente mensual, Salamanca tiene 349 en patrimonio y no 57, y Vicálvaro 53 y no 76. Los totales de la ciudad sí cuadran. **No se lee del panel.**
- **Qué mide:** las actuaciones de la Policía Municipal, una parte de la actividad policial (la Policía Nacional lleva la mayoría de los delitos). Las de drogas y armas dependen sobre todo de dónde se hacen operativos: Centro tiene 1.878 de tenencia de drogas y Chamartín 620. Las de personas y patrimonio se cuentan donde ocurren o se denuncian, así que Centro y Salamanca suben por quien está de paso, como en D-224.
- Hacen falta los 12 ficheros mensuales de cada año. El pipeline del panel no sirve porque la copia está mal, así que se necesita uno nuevo para ese XLSX mensual.

## 4. Seguridad vial: atropellos en 2025
Expedientes distintos con `tipo_accidente = «Atropello a persona»` (8 de 3.155 filas sin coordenadas). Graves: hay al menos un peatón con ingreso hospitalario o fallecido.

| Distrito | Atropellos | Graves | Por 1.000 habitantes |
|---|---|---|---|
| Vicálvaro | 22 | 7 | 0,22 |
| Hortaleza | 50 | 15 | 0,24 |
| Fuencarral-El Pardo | 69 | 23 | 0,27 |
| Chamberí | 65 | 25 | 0,46 |
| Barajas | 27 | 7 | 0,53 |
| Salamanca | 87 | 29 | 0,59 |
| Centro | 110 | 30 | 0,78 |
| **Madrid** | **1.375** | **434** | **0,39** |

- **No es un riesgo por paseo.** Los atropellos ocurren donde más gente camina y donde hay más tráfico. Sin un dato de cuánta gente anda por cada calle (exposición), una tasa por vecino o por kilómetro de calle señala los barrios más vivos (Centro, Salamanca) y premia los que dependen del coche. Barajas sube por el aeropuerto.
- **Pocos casos para un radio a pie.** Hay 1.375 al año en unas 2.400 secciones censales: de media, uno cada dos años por sección. La variación aleatoria pesaría más que la diferencia entre calles.
- Una prioridad «calles más seguras para ir andando» ordenaría zonas con un dato que no mide eso. No se propone.

## 5. Fuera de la capital
- El Balance de Criminalidad sigue como en D-224: no puntúa, porque solo cubre 36 zonas y tiene el problema del denominador.
- No se ha encontrado una descarga abierta de la DGT con atropellos por municipio. La página de microdatos consultada no ofrece ficheros ni licencia. Queda sin verificar y no se usa.
- La encuesta de calidad de vida solo cubre Madrid capital. El resto de la región queda SIN DATOS, declarado.
