# Gate 6 · Vivienda nueva y lo que viene (D-241) · 14 nov 2026

Contexto en la vista de zona que **no puntúa**: no cambia el % de encaje, no ordena zonas y no entra en «Qué falta». Base local `housing_vivienda` (copia completa de `housing`) con los 4 datasets cargados y las 5 features calculadas. API y web de esta rama en local.

## Cobertura (`cobertura.txt`)
| Dato | Feature | Zonas con dato | Nota |
|---|---|---|---|
| Obra nueva entre las compraventas del último año | `compraventas_obra_nueva_pct` | 179/179 municipios (177 con %; 2 sin compraventas: `NOT_APPLICABLE`) | Madrid entero; en los distritos, la cifra de la ciudad con su etiqueta |
| Valor tasado de hasta 5 años y de más de 5 | `valor_tasado_vivienda_nueva_m2`, `…_usada_m2` | 20 y 28 municipios (2025) | Sin distritos |
| Plan Vive | `plan_vive_viviendas` | 26 municipios con viviendas; Hortaleza y Vicálvaro | El resto, 0 confirmado |
| Ámbitos residenciales sin terminar (VEDA) | `ambitos_residenciales_en_desarrollo` | 21/21 distritos (19 con alguno; 57 ámbitos) | Solo Madrid capital |

El cruce de nombres de la tabla de compraventas casa 179 de 179 municipios con la geografía (178 iguales y «Alamo (El)», sin tilde en la fuente), y la tabla CM de museos por municipio, que trae el código, da los mismos 179.

## Ejemplos
- Getafe: 650 de las 2.311 compraventas del último año fueron de obra nueva (28 %); el último trimestre es provisional. Plan Vive: 864 viviendas en entrega (Buenavista y Los Molinos). Tasación: 2.827 €/m², un 1 % más que la usada.
- Alcobendas: 28 de 1.067 (2,6 %); Plan Vive: 756 viviendas en obras (avda. Olímpica y avda. Camilo José Cela); tasación 4.914 €/m², un 14 % más.
- Pozuelo de Alarcón: tasación 5.432 €/m², un 13 % más que la usada. Alcorcón: un 7 % menos.
- Vicálvaro: en toda la ciudad, 1.512 de 40.086 (3,8 %) y tasación 5.459 €/m² (+9 %); Plan Vive, 1.616 viviendas en entrega y en obras (Valdebebas y Los Ahijones, sin reparto entre los dos sitios); en desarrollo: Los Berrocales, Los Ahijones, Los Cerros y Camino Viejo de Vicálvaro (urbanización en obras).

## Invariante del pitch
- `golden-search.txt`: `scripts/golden_search.py` contra `housing_vivienda`, **9/9 OK**, con `ranked_order` y `near_miss_order` del ejemplo (27 zonas cumplen; Latina, Moratalaz, Ciudad Lineal y Puente de Vallecas al 98 %; «Casi encajan» Chamartín, Salamanca, Centro, Chamberí y Retiro al 93 %).
- `invariante.txt`: `POST /search` (toda la Comunidad y Madrid capital por barrios) y `POST /search/barrios` en los 21 distritos dan la misma respuesta **byte a byte** con y sin las filas de D-241 (quitadas dentro de una transacción que se deshace).

## Capturas (1440 y 390 px)
- `municipio-getafe-*.jpg`: obra nueva, tasación y Plan Vive.
- `municipio-alcobendas-*.jpg`: Plan Vive en obras.
- `distrito-vicalvaro-*.jpg` y `distrito-vicalvaro-*-tarjeta.jpg` (la tarjeta entera): cifras de la ciudad, Plan Vive compartido con su nota y los ámbitos en obras.
