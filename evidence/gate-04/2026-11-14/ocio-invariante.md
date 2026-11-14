# Invariante del pitch con ocio (D-236) · Gate 4

Rehecho el 14 nov por la noche con el código fusionado sobre `claude/sprint-1-public` en `1a052b1`, que trae D-238 y D-239. La API local corre sobre la base `housing_ocio`, con las 4 features de ocio y 16.493 locales.

## El ejemplo de la web, sin ocio

`exampleScenario` en `apps/web/src/lib/scenario.ts` es igual que `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- pareja con 2 hijos y 1.500 €/mes de alquiler;
- colegio a 10 min, imprescindible;
- trabajo en la Castellana;
- prioridades: colegios, transporte y salud;
- **sin ocio**.

`POST /api/v1/search` contra la API local (`fit-0.8`) y contra producción (`https://vidafacil-madrid.vercel.app`, `fit-0.7`, sin datos de ocio):

| | Local (`fit-0.8`) | Producción (`fit-0.7`) |
|---|---|---|
| Zonas que cumplen | 27 de 199 (15 sin dato) | 27 de 199 (15 sin dato) |
| Top 10 | Latina 98, Moratalaz 98, Ciudad Lineal 98, Puente de Vallecas 98, Fuencarral-El Pardo 97, Usera 97, Carabanchel 97, Hortaleza 97, San Blas-Canillejas 97, Villaverde 97 | igual |
| «Casi encajan» | Chamartín 93, Salamanca 93, Centro 93, Chamberí 93, Retiro 93 | igual |

Comparación completa (`jq -S` y `diff`): la respuesta entera (`data`) es igual en las dos, salvo dos campos:
- `methodology_version`: `fit-0.8` frente a `fit-0.7`.
- `datasets` pasa de 24 a 25 con `osm_ocio`. La lista cita cada dataset de las features que lee la búsqueda, se usen o no en el caso, como ya hacía con `osm_parques`.

## El caso de D-239: pareja con 10.000 €/mes, sin prioridades

| | Local (`fit-0.8`, con los datos de ocio) | Producción (`fit-0.7`) |
|---|---|---|
| Zonas que cumplen | 57 | 57 |
| Top 10 | Chamberí, Tetuán, Puente de Vallecas, Salamanca, Centro, Usera, Arganzuela, Ciudad Lineal, Carabanchel, Retiro (todas al 100 %) | igual |

Con `EVERYDAY_NEEDS = tuple(NeedKey)`, como estaba en la base, el desempate leía también los minutos de ocio y Centro salía el primero. Ahora `EVERYDAY_NEEDS` son los 6 servicios cotidianos:
- el caso está en el golden (`data/fixtures/golden/search_scenarios.yaml`, `ranked_order`);
- el golden da 10 de 10 OK en `housing` (solo lectura, sin ocio) y en `housing_ocio` (con ocio): `golden-search-ocio.txt`;
- con la definición vieja, el golden falla sobre `housing_ocio`.

## Con ocio

El mismo ejemplo con «Ocio» marcado (bares y cafeterías, restaurantes y cultura a 10 min, sin «Imprescindible»):
- siguen cumpliendo 27 zonas: el ocio no filtra si no se marca «Imprescindible»;
- Latina sube al 99 %, con el hecho «Ocio a pie: bares y cafeterías a unos 3 min, restaurantes a unos 4 min, cultura a unos 11 min»;
- el log de la API local no tiene ningún «fit bindings ignored».

## Tests

- `test_a_scenario_without_leisure_ignores_the_leisure_data` y `test_leisure_minutes_never_break_a_tie` (`tests/unit/fit/test_fit.py`).
- `is not part of a search that never marked it` (`apps/web/src/lib/__tests__/scenario.test.ts`).

## Vista de zona de Centro: peticiones a `/api/v1/places`

Medido con Playwright sobre la web compilada (`next start`) y la API local, abriendo `/zona/distrito/2807901` en una pestaña nueva. Los bytes son los del cuerpo de la respuesta.

| | Antes (ocio en la petición de la zona) | Después (ocio aparte, al pulsar) |
|---|---|---|
| Petición al abrir la zona | 1 · 9 categorías · **2.862 lugares · 1,12 MB** · 1,86 s | 1 · 6 categorías · **179 lugares · 76 KB** · 1,32 s |
| Al pulsar «Cultura» | nada más (ya venía) | 1 petición · `culture` · 133 lugares · 53 KB |
| «Todos» | encendía también los 4 tipos de ocio | enciende los 7 servicios; el ocio queda como estaba |

Así, quien no toca el ocio deja de descargar los 2.683 locales de ocio de Centro, y los botones de ocio no muestran número hasta que se piden.
