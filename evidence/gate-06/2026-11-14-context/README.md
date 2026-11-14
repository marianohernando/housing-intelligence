# D-235 · Otros datos de la zona (14 nov)

Base local `housing_contexto` (copia de `housing` con los datos de D-235), API local y web de producción (`next build` + `next start`) contra ella. Capturas con Chromium (Playwright) a 1440×900 y 390×844; en móvil, con la hoja abierta.

## Capturas

| Zona | 1440 px | 390 px |
|---|---|---|
| Municipio grande: Pozuelo de Alarcón (`/zona/municipio/28115`) | `municipio-pozuelo-1440.jpg` | `municipio-pozuelo-390.jpg` |
| Pueblo: Rascafría (`/zona/municipio/28120`) | `pueblo-rascafria-1440.jpg` | `pueblo-rascafria-390.jpg` |
| Distrito: Usera (`/zona/distrito/2807912`) | `distrito-usera-1440.jpg` | `distrito-usera-390.jpg` |
| Barrio: Recoletos, elegido en «Ir a un barrio» de Salamanca (`/zona/distrito/2807904`) | `barrio-recoletos-1440.jpg` | `barrio-recoletos-390.jpg` |

Texto de la tarjeta, leído de la página:

- **Pozuelo de Alarcón:** Infracciones penales conocidas: 21,6 por cada 1.000 habitantes (Ministerio del Interior, 2024). · Mide hechos conocidos por la policía, sin los delitos por internet; sube donde hay mucha gente de paso. · Viviendas construidas desde 2001: 32,7 % (censo anual de la Comunidad de Madrid, 2023). · Renta disponible bruta por persona: 47.217 € al año (Instituto de Estadística de la Comunidad de Madrid, 2024).
- **Rascafría:** Infracciones penales conocidas: sin dato. El Ministerio solo lo publica para municipios de más de 20.000 habitantes. · Viviendas construidas desde 2001: 21,6 % (…, 2023). · Renta disponible bruta por persona: 20.532 € al año (…, 2024).
- **Usera:** Infracciones penales conocidas: 58,6 por cada 1.000 habitantes (Ministerio del Interior, 2024). Dato de toda la ciudad de Madrid; no se publica por distrito. · (aviso) · Año medio de construcción de los edificios de viviendas: 1978 (Catastro, 2025). · Renta media por hogar: 34.651 € al año (INE, 2023).
- **Recoletos (barrio de Salamanca):** la cifra de la ciudad, con la misma etiqueta · Año medio de construcción de los edificios de viviendas en Recoletos: 1948 (Catastro, 2025). · Renta media por hogar en Recoletos: 95.138 € al año (INE, 2023).

Todas terminan con «Son datos informativos: no cambian el encaje ni el orden de las zonas».

## Cobertura (`feature_value`, último periodo)

| Feature | Nivel | Con cifra | Mínimo | Mediana | Máximo |
|---|---|---|---|---|---|
| `infracciones_penales_por_1000_hab` (2024) | municipio | 37 de 179 (142 «sin dato», `SOURCE_MISSING`) | 20,7 Tres Cantos | — | 116,2 Humanes de Madrid |
| `viviendas_desde_2001_pct` (2023) | municipio | 179 de 179 | 7,6 % Robregordo | 33,4 % | 88,7 % Arroyomolinos |
| `renta_per_capita` (2024) | municipio | 179 de 179 | 13.995 € Cenicientos | 19.929 € | 47.217 € Pozuelo de Alarcón |
| `ano_medio_construccion_residencial` (2025) | distrito | 21 de 21 | 1926 Centro | 1977 | 1999 Vicálvaro |
| | barrio | 131 de 131 | 1919 Sol | 1974 | 2021 El Cañaveral |
| `renta_neta_media_hogar` (2023) | distrito | 21 de 21 | 32.666 € Puente de Vallecas | 45.762 € | 79.274 € Chamartín |
| | barrio | 131 de 131 | 28.240 € San Cristóbal | 48.025 € | 104.774 € Fuentelarreina |

Los 21 distritos y los 131 barrios enseñan la cifra de infracciones de toda la ciudad (58,6), con su etiqueta.

## Ejemplos

| Zona | Infracciones / 1.000 hab. | Antigüedad | Renta |
|---|---|---|---|
| Madrid (ciudad) | 58,6 | 16,5 % desde 2001 | 27.188 € por persona |
| Pozuelo de Alarcón | 21,6 | 32,7 % desde 2001 | 47.217 € por persona |
| Parla | 47,7 | 43,6 % desde 2001 | 14.349 € por persona |
| Rascafría (pueblo) | sin dato | 21,6 % desde 2001 | 20.532 € por persona |
| Salamanca (distrito) | 58,6 (ciudad) | año medio 1953 | 69.147 € por hogar |
| Usera (distrito) | 58,6 (ciudad) | año medio 1978 | 34.651 € por hogar |

Criminalidad convencional (total menos cibercriminalidad, D-224 §3) sobre los vecinos del mismo año: Madrid 2024, (237.020 − 36.591) / 3,42 millones. Con el total sin restar, Madrid daría 69,3 y Humanes 131,4.

## Invariante del pitch

`POST /api/v1/search` con `exampleScenario` (`apps/web/src/lib/scenario.ts`):

```
zones_evaluated 199 · zones_passing 27 · zones_unknown 15 · binding near:colegio
Latina 98 · Moratalaz 98 · Ciudad Lineal 98 · Puente de Vallecas 98 · Fuencarral-El Pardo 97 · Usera 97
Casi encajan: Chamartín, Salamanca, Centro, Chamberí, Retiro
```

La respuesta completa (`results`, `near_misses`, `all_zones`, `reality_check`, `datasets`, `methodology_version`) es idéntica contra `housing` (sin los datos de D-235) y contra `housing_contexto` (con ellos), con el código de este PR antes y después de traer el desempate de D-239. El log de la API no tiene ningún «fit bindings ignored».

## Gates

- Sobre `origin/claude/sprint-1-public` en `15393cb` (con #56, D-239): `make lint typecheck test-unit` verde (pytest 749, vitest 402).
- `make test-db` contra una base de tests vacía (`housing_contexto_test`, migrada a `0007`): 134 passed.
- `npm run build` (apps/web): verde.
- Gate 1 de los tres datasets: `evidence/gate-01/2026-11-14/` (PASS; los avisos no críticos son la cobertura de 37 municipios y `totals_are_additive`, porque la cibercriminalidad es una parte del total, no un reparto).
