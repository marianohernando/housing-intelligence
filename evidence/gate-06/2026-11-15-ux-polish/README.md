# Pulido de experiencia (línea B, 15 nov)

Feedback de usuarios de prueba, de Mariano y de la línea C. Rama `claude/s1-visual-polish`, con la base `0f6988b` integrada por merge (#62 ocio, #67 vivienda nueva, #68 analítica). Todo lo de abajo se comprobó sobre el árbol ya fusionado.

Cómo se comprobó:
- API de esta rama sobre la base local `housing`, en solo lectura (`default_transaction_read_only=on`).
- Web con `next build` y `next start`, con el buscador activo y esa API.
- Playwright con Chromium, a 1440 y a 390 px, y axe (WCAG 2.2 AA): `capture-report.json`.

Solo cambia la pantalla: ni la API, ni la fórmula, ni el ejemplo del pitch.

## Invariante del pitch (`invariante-produccion.txt`, `golden-search.txt`, `e2e-local.txt`)

- El ejemplo sigue enviando `min_floor_area_m2: null`: lo comprueban un test unitario, la captura (`m2_*.ejemplo_envia`) y un check nuevo del e2e.
- El caso del ejemplo da lo mismo en la API local que en producción: 27 zonas que encajan, 15 sin dato, el mismo top 10 (de Latina a Villaverde, con sus precios) y los mismos «Casi encajan». `data` es igual entera.
- `scripts/golden_search.py`: 10 de 10.
- e2e (`infra/deploy/e2e/e2e_prod.mjs`) contra esta web: 70 de 70 a 1440 y 44 de 44 a 390.
- `make lint typecheck test-unit`: 882 tests de Python y 476 de la web, todo en verde.

## Capturas

| Fichero | Qué se ve |
|---|---|
| `hospitales-lista-1440.png`, `hospitales-lista-390.png` | Moncloa-Aravaca, 6 hospitales. Cada fila empieza por la pastilla («Público» rellena, «Privado» con contorno) y el nombre; debajo, en pequeño, «gestión privada» (Fundación Jiménez Díaz) o el tipo («Hospital de salud mental»); a la derecha, la cama y la cifra |
| `hospitales-que-significa-1440.png`, `hospitales-que-significa-390.png` | La nota de público y privado, plegada tras «¿Qué significa?» y abierta |
| `hospitales-etiqueta-mapa-1440.png`, `hospitales-etiqueta-mapa-390.png` | La etiqueta del punto en el mapa: «[Privado] Hospital de salud mental» y, en escritorio, «Clínica López Ibor · [cama] 67» |
| `m2-selector-1440.png`, `m2-selector-390.png` | El ejemplo con «Para 60 m² (cámbialo)» abierto: el selector («Lo normal para tu hogar (77 m²)», de 40 a 150 m²) y su ayuda |
| `m2-resultados-60-1440.png`, `m2-resultados-60-390.png` | Las filas con «≈ 994 €/mes» y «por 60 m²» debajo |
| `m2-tarjeta-60-1440.png`, `m2-tarjeta-60-390.png` | La tarjeta de Fuencarral-El Pardo: «Alquiler ≈ 994 €/mes por 60 m²» arriba y el hecho de la API con los mismos 60 m² |
| `cerca-pocas-puente-de-vallecas-1440.png`, `cerca-pocas-puente-de-vallecas-390.png` | El ejemplo con «Escuela infantil a 10 min como mucho»: Puente de Vallecas (4.º, 98 %) dice «Escuela infantil a unos 6 min andando, pero hay pocas para tantos niños de 0 a 4 años: por eso sale FALTA.», con la ayuda nueva bajo «Qué falta aquí» |
| `leyenda-madrid-capital-1440.png`, `leyenda-madrid-capital-390.png` | «Madrid capital»: «Cumple todo 78 barrios», «No cumple todo 52 barrios», «Sin datos 1 barrio», como la API |
| `ocio-casillas-1440.png`, `ocio-casillas-390.png` | «¿Qué ocio quieres cerca?» con sus casillas |
| `ocio-casillas-antes-390.png`, `ocio-casillas-despues-390.png`, `ocio-casillas-medidas.txt` | A 390 px, antes del arreglo «Bares y cafeterías» y «Gimnasios y deporte» tenían la casilla de 15,8 y 14 px frente a 19,5; después, todas de 19,5 (también a 375 y 360 px) |
| `contexto-pie-1440.png`, `contexto-pie-390.png` | La tarjeta «Otros datos de la zona» de Puente de Vallecas con su pie |

## Comprobaciones (`capture-report.json`)

- **Hospitales:** las 6 filas empiezan por «Público» o «Privado»; «gestión privada» solo bajo un público; el lector de pantalla oye «651 camas instaladas»; la nota está plegada al llegar.
- **m²:** la línea dice «Para unos 77 m² (cámbialo)» con el ejemplo; con 60 m², la búsqueda envía `min_floor_area_m2: 60`, la API responde «Alquiler hasta 1.500 €/mes para 60 m²» y la fila, la cabecera de la tarjeta y su hecho dicen 60 m². Con «Lo normal para tu hogar» vuelve a `null` (test unitario).
- **Cerca, pero pocas:** la línea sale en Puente de Vallecas, con la escuela infantil a 6,3 min (`near:escuela_infantil` PASS) y la fila FALTA.
- **Leyenda y mapa con «Madrid capital»:** la leyenda cuenta barrios (78, 52 y 1, los de la API) y la etiqueta del mapa dice «Mapa de la Comunidad de Madrid por municipios, con Madrid capital dividida en sus barrios. Cada barrio tiene el color de su encaje…», sin «21 distritos».
- **Pie único:** la vivienda nueva (D-241) aún no tiene datos ni en la base local ni en producción, así que la tarjeta no sale. Para comprobar la regla, la prueba pone en la página una copia de la tarjeta de contexto detrás de ella: el primer pie se oculta y el último se ve. No se inventa ninguna cifra.
- **axe:** 0 incidencias en todas las pantallas, a 1440 y a 390 px. Ningún desborde horizontal ni error en la consola, salvo los 404 esperados de las cinco variables de D-241, que la tarjeta ya trata como «sin dato».
