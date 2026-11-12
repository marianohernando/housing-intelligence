# OPS-001 (line C) · deploy of e7d4fa3 (B's PR #32: «Dónde invertir primero», safety bars, several centre types, «No comparable») · 2026-11-12 23:56 (Madrid)

## Deploy
- **Code:** `e7d4fa3`, the HEAD of `claude/sprint-1-public` when D asked. It carries:
  - **B's PR #32:** «Dónde invertir primero» in «Qué falta», the plain texts («Aquí hay 57 por cada 100…»), the 5-step scheme, perceived safety as bars, several types at once in «Todos los centros», «No comparable» (D-230) and the Agencia Tributaria in the footer;
  - **A's `861af7b` and `c269100`:** `source_name` and the 2 bed features (D-231), plus the fixture.
- **Data:** no sync needed, because Supabase was already at `c269100`.
- **CI:**
  - The `pull_request` run of `e7d4fa3` passed all five jobs.
  - Its `push` run was cancelled when `8249b28` arrived (D's deck). That commit only changes `pitch/`, so the deployed code is the same.
- **Deployed from a detached checkout.** Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_JCgqNtxco3ChAa9iJo7sqEpBAZGN`, verified on round 1 with smoke 8/8, «27 of 199 zones, 1st Latina». Output: [deploy-21/deploy-output.txt](deploy-21/deploy-output.txt).
  - Round 0 had 3 requests from `dpl_4P9B8…`.
  - Round 1 was 8/8, all from the new deployment.

## Manual checks, desktop 1440 × 900 and mobile 390 × 844
No console errors and no HTTP errors on either. Output: [deploy-21/manual-checks.txt](deploy-21/manual-checks.txt).

1. **«Qué falta» of the Comunidad (`/que-falta`), «Dónde invertir primero»:** [desktop](deploy-21/desktop-1-donde-invertir.jpg) · [mobile](deploy-21/mobile-1-donde-invertir.jpg).
   - «Escuelas infantiles: **25.551** niños de 0 a 4 años viven donde faltan escuelas infantiles. El 9,8 % de toda la Comunidad, en 3 zonas.»

   | Rank | Zone | Children | Text |
   |---|---|---|---|
   | 1 | **Puente de Vallecas** | 9.433 | «Aquí hay 57 por cada 100 que hay en municipios parecidos» |
   | 2 | **Carabanchel** | 9.150 | 68 per 100 |
   | 3 | **Villaverde** | 6.968 | 61 per 100 |

   - The next row: «Centros de mayores: 54.581 personas de 65 años o más…».
2. **Villaverde, safety bars:** «4,9 de noche y 6,8 de día, de 0 a 10 (en todo Madrid, 6,4 y 7,8)», drawn as bars: «De noche 4,9 | Madrid 6,4» and «De día 6,8 | Madrid 7,8», on a scale from 0 to 10. [desktop](deploy-21/desktop-2-seguridad.jpg) · [mobile](deploy-21/mobile-2-seguridad.jpg).
3. **Villaverde, «Todos los centros» with three types at once:**
   - Colegios, Farmacias and Parques, each with `aria-pressed=true`.
   - The text reads «32 colegios con primaria en Villaverde, 65 farmacias en Villaverde y 34 parques de 1 ha o más en Villaverde», and the map shows the three sets of dots.
   - «Todos» and «Ninguno» are available.
   - The footer reads «… + Ministerio de Sanidad + Agencia Tributaria».
   - [desktop](deploy-21/desktop-3-varios-centros.jpg) · [mobile, list](deploy-21/mobile-3-varios-centros.jpg) · [mobile, map](deploy-21/mobile-3-varios-centros-mapa.jpg).
4. **La Acebeda (`/que-falta?zona=municipio/28001`):** «Zona muy pequeña para comparar: colegios, centros de salud, centros de mayores, farmacias y viviendas grandes para familias. Sin datos: escuelas infantiles.»
   - «No comparable» appears 11 times, for example «No comparable: aquí viven muy pocos niños de 5 a 14 años (3) para saber si falta».
   - [desktop](deploy-21/desktop-4-la-acebeda.jpg) · [mobile](deploy-21/mobile-4-la-acebeda.jpg).

## Watch, 22:58–23:03 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 80 API requests and 0 5xx, plus 5 `/search`, all 200 in 0.39–0.47 s. Output: [deploy-21/watch.txt](deploy-21/watch.txt).
- **Logs, 22:55–23:03 UTC:** [deploy-21/logs-summary.txt](deploy-21/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks, `ValueError` or `KeyError` | 0 |
| API access lines | 254, all 200 |
| Instances started | 7 |
| CDN records | 1,029: 1,021 × 200 and 8 × 304 |

## LCP, one pass on a phone with slow 4G
Report: [deploy-21/perf-report.json](deploy-21/perf-report.json). Elements: [deploy-21/lcp-elements.txt](deploy-21/lcp-elements.txt).

| Page | LCP |
|---|---|
| zone Chamartín | **2.06 s** |
| home | 1.14 s |
| «Qué falta» Madrid | 0.92 s |

In the separate element probe, the zone's lead text painted at 2.42 s, still under 2.5 s.

## Offline package
Not regenerated, at D's request. It waits for B's labels PR, which uses the fonts of PR #36.
