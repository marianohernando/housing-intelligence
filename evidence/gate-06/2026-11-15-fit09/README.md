# fit-0.9 «cerca y plazas» (D-243): paridad con el banco, golden y ejemplo del pitch

15 nov. Rama `claude/s1-fit-0.9`. Base local `housing_fit09`: copia de `housing` con el lote 4 (datos calculados hasta las 11:06 UTC) y `alquiler_m2_mensual_referencia` recalculada con el factor de reserva 1,155 (12:36 UTC). Todo en solo lectura salvo ese recálculo; nada contra Supabase ni producción.

## Paridad con el banco de fórmulas

Referencia: el preset `f4_a_recomendada` del banco (A + `tope_trayecto`) sobre el código de `5c22ded` (`fit-0.8`). Implantación: la variante `actual` del banco sobre esta rama (`fit-0.9`). Misma base y mismos parámetros.

| Comprobación | Antes de recalcular (factor 1,2085) | Después (factor 1,155) |
|---|---|---|
| 26 personas y 1.000 búsquedas de la rejilla: top 10, «Casi encajan», recuentos y encaje sin redondear de cada zona | Iguales en las 1.026 (diferencia máxima 0) | Iguales en las 1.026 (diferencia máxima 0) |
| Informe `run` del banco (personas, expectativas, métricas, invariantes) | Idéntico salvo 2 invariantes | Idéntico salvo 2 invariantes |
| Informe `rejilla` del banco (rejilla, metamórficos, Monte Carlo) | Idéntico salvo 1 metamórfico | Idéntico salvo 1 metamórfico |
| Los mismos informes, pasando al código el forzado de plazas del banco | Idénticos | Idénticos |

- **Por qué difieren esas 3 comprobaciones sin el forzado.** «Un dato que falta nunca puntúa como un 0» y «marcar un servicio que la zona tiene en la puerta…» fuerzan la ratio de plazas desde el banco (`Ctx.forced`: 0 cuando el servicio está a 10.000 min, 1 cuando está en la puerta). Los componentes del banco la leen de ahí; `fit-0.9` la lee de `ZoneData.supply`, así que sin forzado ve la ratio real de la zona. Con un envoltorio que escribe ese mismo forzado en `ZoneData.supply` antes de evaluar, los informes salen idénticos línea a línea (salvo la descripción de la variante y los tiempos).
- **Diferencia deliberada (no ejercitada por el banco):** una casilla de ocio imprescindible no es un criterio aparte (D-236); el banco sí la convierte. Ninguna persona ni búsqueda del banco marca ocio.
- Las herramientas de paridad (volcado por búsqueda, comparación y envoltorio del forzado) están junto al banco, fuera del repo (`formula_bench/paridad/`), con sus informes en `formula_bench/out/2026-11-15_fit09_*`. Los informes del banco no se copian aquí: llevan frases de la prueba con usuarios.

## Golden de búsqueda

`golden-search.txt`: 10/10 contra `housing_fit09`. Cambia lo que fija el ejemplo del pitch (`ranked_order`, `ranked_pct` y `near_miss_order`, más el nuevo `zones_passing`), `results_within_km` de 15 a 16 (Leganés, a 15,2 km de Azca, entra en el top 10) y el orden del caso con 10.000 € y nada marcado.

## El ejemplo del pitch por la API

`search-example.txt`: `POST /api/v1/search` con el ejemplo, API de esta rama en el puerto 8051 sobre `housing_fit09`.

| | `fit-0.8` (D-242) | `fit-0.9` |
|---|---|---|
| Encajan · no cumplen · sin dato | 42 · 157 · 0 | 42 · 157 · 0 |
| Top 10 | Latina 98, Moratalaz 98, Ciudad Lineal 98, Puente de Vallecas 98, Fuencarral-El Pardo 97, Usera 97, Carabanchel 97, Hortaleza 97, San Blas-Canillejas 97, Villaverde 97 | Puente de Vallecas 94, Latina 94, Usera 93, Moratalaz 93, Tetuán 92, Ciudad Lineal 92, Villaverde 92, Carabanchel 90, Coslada 90, Leganés 90 |
| «Casi encajan» | Chamartín, Salamanca, Centro, Chamberí, Retiro (93) | Chamartín 92, Arganzuela 92, Centro 91, Chamberí 91, Retiro 91 (presupuesto) |
| Reality Check | +5 min de colegio: +49 · +150 €/mes: +3 | Igual |
| Bandas (199 zonas) | – | muy bien 18 · bien 13 · regular 47 · poco 121 |

## Factor de reserva de SERPAVI

`serpavi-summary.txt`: los 126 municipios rellenos usan ahora la mediana de los factores municipales (`mediana_municipios`, 1,1551) en lugar de la fila de la Comunidad (1,2085); cobertura y calibración (1,0388) sin cambios.

## Tests

- `make lint typecheck test-unit`: ver el PR.
- `make test-db` contra una base de test propia (`housing_fit09_test`).
