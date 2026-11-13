# Demo case with fit-0.6 · production on 2026-11-12, 23:10 (Madrid)

The pitch's demo case, «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana», as production gives it after the deploy of fit-0.6 (`310056b`, `dpl_4P9B8j15b8pzTHugitgyeFxAaq94`) and D's sync of the 2024 rent leases (D-228).
- **For D and B:** the pitch script and the screenshots.
- **Where the figures come from:** read from the API (`POST /api/v1/search`, [deploy-20/search-demo-response.json](deploy-20/search-demo-response.json)) and checked on screen. The e2e compares each figure on screen with that response: 66/66 on desktop and 40/40 on mobile.
- **What changed:** before, it was «33 de 199 zonas, 1.ª Fuencarral-El Pardo 100 %». Now the budget limits, because the rent of a lease signed in 2024 is higher than the rent of the leases in force.

## The search (the fixture `scenario_state.familia_castellana`)
- **Household:** 2 adults and 2 children, aged 4 and 8.
- **Budget:** rent, up to 1,500 €/mes.
- **Work:** Paseo de la Castellana (Azca), 4 days a week, arriving at 9:00, with no time limit.
- **Within walking distance:** a colegio, 10 min at most (required).
- **What matters, in order:** colegios, transporte, salud.

## Result
**«Con tu búsqueda tal cual salen 27 zonas», out of 199.** Map legend: 27 «Cumple todo», 157 «No cumple todo», 15 «Sin datos».

| Rank | Zone | Match | Work, by public transport, arriving at 9:00 | Rent of a 77 m² home |
|---|---|---|---|---|
| 1 | **Latina** | **98 %** | 39 min | ≈ 1.101 €/mes (14,3 €/m²) |
| 2 | **Moratalaz** | **98 %** | 40 min | ≈ 1.083 €/mes (14,1 €/m²) |
| 3 | **Ciudad Lineal** | **98 %** | 33 min | ≈ 1.230 €/mes (16,0 €/m²) |
| 5 | Fuencarral-El Pardo | 97 % | — | ≈ 1.276 €/mes (16,6 €/m²) |

### Latina's card, as on screen
[desktop](deploy-20/e2e/chromium-desktop-1440-j1-card.jpg) · [mobile](deploy-20/e2e/chromium-mobile-390-j1-card.jpg)

- «98 % de encaje» · «La 1.ª que más encaja»
- **Lo que tienes aquí:**
  - «Colegio con primaria a unos 6 min andando» · Dato fiable
  - «Parada de transporte público a unos 2 min andando» · Dato fiable
  - «Centro de salud a unos 10 min andando» · Dato fiable
  - **Work:** «39 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» · Dato aproximado
  - **Rent:** «Alquiler ≈ 1.101 €/mes por 77 m² (14,3 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)» · Dato fiable
- **Qué falta aquí:** «Encaja con lo que pides; aun así, en la zona van justos de: escuelas infantiles, centros de salud.»
  - Escuelas infantiles: JUSTO
  - Centros de salud: JUSTO
  - Colegios: CUBIERTO

**The same facts for the 2nd and 3rd zones:**

| Zone | Colegio | Transport stop | Centro de salud | Work | Rent |
|---|---|---|---|---|---|
| Moratalaz | 6 min | 2 min | 11 min | 40 min | ≈ 1.083 €/mes |
| Ciudad Lineal | 5 min | 2 min | 10 min | 33 min | ≈ 1.230 €/mes |

**All 10 results** say «contratos firmados en 2024» in their rent text.

## «¿Y si cambias algo?»
The binding constraint is the colegio within walking distance (`near:colegio`). [desktop after applying the 1st option](deploy-20/e2e/chromium-desktop-1440-j1-applied.jpg)

| Option | Zones |
|---|---|
| «+5 min a pie hasta colegio con primaria» | 27 → **44** (+17) |
| «+150 €/mes» | 27 → **30** (+3). Before fit-0.6 it added none. |

## Sources
The rent comes from the Agencia Tributaria, with leases signed in 2024 (`aeat_alquiler_nuevos_contratos_codigo_postal` and `aeat_alquiler_nuevos_contratos_municipios`).
- `/datasets` lists them with `is_cm_open_data=false`.
- The «Datos: 27 conjuntos de la Comunidad de Madrid» line does not change. There are 35 datasets in total.

Results screenshots: [desktop](deploy-20/e2e/chromium-desktop-1440-j1-results.jpg) · [mobile](deploy-20/e2e/chromium-mobile-390-j1-results.jpg).
