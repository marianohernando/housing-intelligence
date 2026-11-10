# Gate 02 — limitaciones conocidas (2026-11-10)

Alcance: paradas y estaciones de los 6 GTFS del CRTM (DATA-007, D-196). La QA geoespacial de la geografía canónica sigue en `evidence/gate-01/2026-10-20`.

## Datos publicados
| Modo | Paradas o estaciones | Sin sección | Headway en punta (mediana, min) |
|---|---|---|---|
| Metro | 230 | 0 | 4,3 |
| Metro Ligero | 56 | 0 | 6,7 |
| Cercanías | 93 | 2 (Azuqueca y Guadalajara, fuera de la CM) | 6,7 |
| EMT | 4.935 | 0 | 9,2 |
| Autobuses urbanos | 3.023 | 0 | 20 |
| Interurbanos | 6.645 | 231 (fuera de la CM, dentro del rectángulo de la región) | 17,1 |

## Limitaciones
- **El GTFS de metro venció el 27-05-2026.** Es el último publicado por el CRTM, así que se usa. El día de referencia (25-11-2025) cae dentro de su vigencia y la calidad lo avisa (`feed_current`, no crítico).
- **Cercanías no declara `direction_id`.** Su headway en punta es por línea con los dos sentidos juntos (`headway_basis: route`), así que no es comparable uno a uno con el de metro, que es por sentido.
- **Interurbanos:** 40 paradas fuera del rectángulo de la región quedan en cuarentena con su motivo. 231 paradas de provincias vecinas se publican sin sección censal, porque ninguna sección de la CM las contiene.
- **Paradas compartidas.** Una parada servida por autobuses urbanos e interurbanos aparece una vez por red, con el servicio de cada red. Hay 3 grupos de paradas interurbanas con ids oficiales distintos en el mismo punto. A este nivel no se hace entity resolution entre redes.
- **Andenes de transbordo sin estación declarada.** Le pasa a 25 estaciones de metro y a 1 de metro ligero. Se unen a la estación que está en el mismo punto y tiene el mismo nombre (parser `gtfs-1.1.0`).
- **Headway de una sola salida.** Un headway de 120 min significa que la línea más frecuente solo sale una vez entre las 07:00 y las 09:00.
- **Nivel B pendiente** (tiempo a polos de empleo, transbordos y destinos directos): CORE-009.

## Muestra manual (`manual-sample.txt`)
Las 20 paradas se eligen con md5 del id, así que la muestra es determinista. Claude revisó que el nombre, el municipio asignado y las coordenadas encajan. Por ejemplo: «CTRA.M506-BEMBIBRE» y «VASCOS-POL.IND.LA TOCA» caen en Fuenlabrada (28058), «SOMOSAGUAS SUR» en Pozuelo de Alarcón (28115) y «APALACHES-NARANJO DE BULNES» en Colmenar Viejo (28045). Resultado: 20/20 coherentes. Mariano puede revisar la muestra cuando quiera; no bloquea nada.
