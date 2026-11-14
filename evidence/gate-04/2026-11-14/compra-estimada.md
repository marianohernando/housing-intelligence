# Precio de compra estimado en distritos y barrios de Madrid (D-234, `fit-0.8`)

Base local de la línea (copia de `housing` con el panel reingerido y las dos features recalculadas), 14 nov. API local contra esa base. Salidas completas: `casos-compra-estimada.txt` (casos reales) y `golden-search-compra-estimada.txt` (9/9 escenarios dorados OK). Capturas: `evidence/gate-06/2026-11-14-buy-estimate/`.

## Método

€/m² de la zona = valor tasado de Madrid (4.993,3 €/m², Ministerio de Vivienda, portal CM) × (valor catastral por m² de la zona / media del de los distritos ponderada por sus inmuebles residenciales). El valor catastral por m² es el valor catastral medio por inmueble residencial entre su superficie construida media (Catastro, panel de indicadores del Ayuntamiento, 1 de enero de 2025). Los barrios se reparten igual a partir de la estimación de su distrito. Confianza 0,5 («Dato aproximado»). Comprobado en la base: la media ponderada de los 21 distritos vuelve a 4.993,3 y la de los barrios de cada distrito, a la de su distrito (test de integración).

## Los 21 distritos (pareja: 68 m²)

| Distrito | €/m² estimado | Comprar ≈ |
|---|---:|---:|
| Salamanca | 7.771 | 528.000 € |
| Chamartín | 7.434 | 506.000 € |
| Chamberí | 7.009 | 477.000 € |
| Retiro | 6.790 | 462.000 € |
| Centro | 6.287 | 428.000 € |
| Tetuán | 6.051 | 411.000 € |
| Arganzuela | 5.970 | 406.000 € |
| Barajas | 5.696 | 387.000 € |
| Hortaleza | 5.102 | 347.000 € |
| Moncloa-Aravaca | 4.823 | 328.000 € |
| Ciudad Lineal | 4.770 | 324.000 € |
| Fuencarral-El Pardo | 4.670 | 318.000 € |
| Moratalaz | 4.492 | 305.000 € |
| San Blas-Canillejas | 4.251 | 289.000 € |
| Villa de Vallecas | 4.029 | 274.000 € |
| Latina | 3.827 | 260.000 € |
| Carabanchel | 3.638 | 247.000 € |
| Vicálvaro | 3.484 | 237.000 € |
| Villaverde | 3.442 | 234.000 € |
| Usera | 3.046 | 207.000 € |
| Puente de Vallecas | 2.971 | 202.000 € |

Barrios: 131 de 131 con valor, de 2.033 a 9.945 €/m².

## Casos reales (feedback de usuarios de prueba)

Pareja (2 adultos), sin «Me importa» ni servicios a pie.

1. **Comprar 400.000 € (`POST /search`).** Cumplen 41 de 199 zonas: 27 municipios con valor tasado y 14 distritos. Hay 151 zonas sin datos, todas municipios sin precio publicado (`unknown_by_constraint = {budget: 151}`). La condición que más limita es el presupuesto, porque 7 distritos la incumplen. Reality Check: «+40.000 €» → 44 zonas (+3: Arganzuela, Tetuán y Centro).
   - **Tetuán no sale:** ≈ 411.000 €, sale el 2.º en «Casi encajan» (tras Arganzuela, 406.000 €).
   - **Top 10, con la clave de D-239** (tras fusionar #56): Puente de Vallecas, Usera, Carabanchel, Latina, Villaverde, Coslada, Parla, Móstoles, San Blas-Canillejas y Leganés, todos al 100 %. Son 6 distritos y 4 municipios. Antes de D-239 eran 10 municipios, porque la confianza 0,8 del precio publicado desempataba antes que la 0,5 de la estimación.
2. **Comprar 400.000 € en Tetuán (`POST /search/barrios`, distrito 2807906).** Cumplen 4 de 6: **Valdeacederas** (1.º, 52 %, ≈ 348.000 €, 5.111 €/m²), **Berruguete** (2.º, 22 %, ≈ 378.000 €, 5.555 €/m²), Almenara (≈ 390.000 €) y Bellas Vistas (≈ 395.000 €). No cumplen Castillejos ni Cuatro Caminos. El % es bajo porque se acercan al tope (margen del presupuesto).
3. **Comprar 1.000.000 €, trabajo en Cuatro Torres (40,4776, −3,6880).**
   - **Sin límite de tiempo:** cumplen 48 de 199 (las 48 zonas con precio) y los 10 primeros son distritos: Chamberí, Tetuán, Chamartín y Fuencarral-El Pardo al 100 %, y Salamanca y Centro al 96 %. Ninguna zona incumple nada, así que no hay condición que limite y el Reality Check no ofrece «+100.000 €».
   - **Con `max_minutes: 45`:** cumplen 13 y los 10 primeros son distritos: Chamberí, Tetuán, Salamanca, Centro, Arganzuela, Ciudad Lineal, Retiro, Chamartín, Hortaleza y Fuencarral-El Pardo, todos al 100 %. Lo que más limita es el tiempo hasta el trabajo; «Sin límite de tiempo» → 48 (+35). Las 46 zonas sin datos son municipios sin precio y sin trayecto calculado.
4. **Invariante del pitch** (`exampleScenario`, alquiler 1.500 €, familia, Castellana): **27 zonas, Latina 1.ª al 98 %**, igual que antes. Le siguen Moratalaz y Ciudad Lineal, también al 98 %.

## Validación frente a precios de mercado

Referencia: precios de oferta por distrito del informe mensual de idealista (artículo `idealista.com/news/node/909039`, consultado el 14 nov 2026; trae 12 de los 21 distritos y 6.458 €/m² para la ciudad). Es un portal privado de anuncios: solo se usa para validar, nunca como dato.

- **Orden:** Spearman 0,95 en los 12 distritos.
- **Nivel:** el estimado es de media 0,88 veces el precio de oferta (geométrica), lo esperable de un valor tasado frente a un anuncio.
- **Error por distrito, quitada esa diferencia común:** entre −19 % (Salamanca) y +19 % (Villa de Vallecas). Ninguno pasa del 30 %.
- **Sesgo declarado:** el valor catastral comprime el rango. Los distritos caros salen algo por debajo de lo que dice el mercado (Salamanca, Chamberí y Retiro) y los baratos algo por encima (Villa de Vallecas, San Blas-Canillejas y Villaverde).

El agente anterior informó Spearman 0,96 en 13 distritos y ningún error por encima del 30 %, pero no dejó la fuente ni el cálculo. Esta comprobación se puede repetir y da lo mismo en lo esencial.

## El precio de cada zona, a la vista

Lo pidió el coordinador tras la prueba con usuarios: «si tuviera un precio aproximado por zona, se entendería mejor».

- **En la API:** `estimated_cost_confidence` en cada `RankedZone`, y `estimated_cost_eur` con su confidence en cada zona de `all_zones`. Ejemplo con 400.000 €: Aranjuez trae 131.000 € (0,8), Tetuán 411.000 € (0,5) y La Acebeda `null` (sin precio).
- **En la web:**
  - bajo el % de cada fila: «≈ 411.000 €» con «Dato aproximado», o «≈ 1.101 €/mes»;
  - bajo el nombre de la tarjeta: «Comprar ≈ 411.000 € · Dato aproximado»;
  - sin precio, nada.
- **Capturas:** `evidence/gate-06/2026-11-14-buy-estimate/`, de la 1 a la 6, a 1440 y 390 px.
- **Invariante, comprobado otra vez** con el código final, en la API y en pantalla (`6-ejemplo-alquiler`): 27 zonas. Latina 1.ª al 98 % (≈ 1.101 €/mes); Moratalaz (≈ 1.083 €/mes) y Ciudad Lineal (≈ 1.230 €/mes), también al 98 %. Los casos reales dan lo mismo que antes de añadir el precio (salida idéntica).

## Tras fusionar #56 (D-239)

- «Zonas que encajan» sigue la clave de D-239 sin coste: tras los servicios a pie no queda ningún empate exacto entre las zonas que encajan, ni comprando con 400.000 € o 1.000.000 €, ni con 10.000 €/mes de alquiler, ni en el ejemplo. El coste solo desempata «Casi encajan» (Arganzuela, Tetuán, Centro, Retiro y Chamberí con 400.000 €).
- Golden 9/9, con `ranked_order` y `near_miss_order` del ejemplo.
- Alquiler de 10.000 €/mes, pareja, sin prioridades: Chamberí, Tetuán, Puente de Vallecas, Salamanca, Centro, Usera, Arganzuela, Ciudad Lineal, Carabanchel y Retiro, el mismo top 10 que D-239.
- Las capturas de `evidence/gate-06/2026-11-14-buy-estimate/` son de antes de fusionar #56. Lo que cambia es el orden de las filas 1 y 5, no los precios ni los textos.
