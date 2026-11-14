# Invariante del pitch con ocio (D-236) · Gate 4

El ejemplo de la web (`exampleScenario` en `apps/web/src/lib/scenario.ts`, igual que `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`: pareja con 2 hijos, 1.500 €/mes, colegio a 10 min imprescindible, trabajo en la Castellana; prioridades colegios, transporte y salud; **sin ocio**) da exactamente lo mismo con este código y los datos de ocio que en producción.

`POST /api/v1/search` el 14 nov a las 19:00 contra:
- la API local de esta rama (`fit-0.8`, base `housing_ocio` con las 4 features de ocio y los 16.507 locales);
- producción (`https://vidafacil-madrid.vercel.app`, `fit-0.7`, desplegado `ad4a8f2`, sin datos de ocio).

| | Local (`fit-0.8`) | Producción (`fit-0.7`) |
|---|---|---|
| Zonas que cumplen | 27 de 199 | 27 de 199 |
| Top 10 | Latina 98, Moratalaz 98, Ciudad Lineal 98, Puente de Vallecas 98, Fuencarral-El Pardo 97, Usera 97, Carabanchel 97, Hortaleza 97, San Blas-Canillejas 97, Villaverde 97 | igual |
| «Casi encajan» | Chamartín 93, Salamanca 93, Centro 93, Chamberí 93, Retiro 93 | igual |

Comparación completa (`jq -S` y `diff`): el `match_pct` de las 199 zonas de `all_zones` es idéntico, y en el top 10 y las 5 de «casi encajan» también lo son la confianza, los textos de los hechos y el estado de cada condición. El Reality Check coincide (27 cumplen, 15 desconocidas, condición que más limita `near:colegio`, «+5 min a pie hasta colegio con primaria» → 44 zonas). Solo cambia `methodology_version`.

Con ocio (el mismo ejemplo más «Ocio» con bares y cafeterías, restaurantes y cultura a 10 min, sin «Imprescindible»): siguen cumpliendo 27 (el ocio no filtra si no se marca «Imprescindible»); Latina sube al 99 % con «Ocio a pie: bares y cafeterías a unos 3 min, restaurantes a unos 4 min, cultura a unos 11 min», y entran Torrejón de Ardoz y Alcorcón (96 %) en el top 10. El log de la API local no tiene ningún «fit bindings ignored».

Tests que lo fijan: `test_a_scenario_without_leisure_ignores_the_leisure_data` (`tests/unit/fit/test_fit.py`) y `is not part of a search that never marked it` (`apps/web/src/lib/__tests__/scenario.test.ts`).
