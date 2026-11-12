# OPS-001 (line C) · deploy of the audit, gap-0.3 and hospitals with beds; database connection incident · 2026-11-12 02:40 (Madrid)

Supabase migrated to 0006 and synced by Mariano before the deploy (orchestrator check by MCP: `feature_value` 67,805 rows, `place_master` 23,368, 136 MB).

## Deploy
- **What:** `28e53fa`, the HEAD of origin/claude/sprint-1-public. It includes PRs #12, #13 and #14 and line A's work up to HOSP-001 Fase 1b: the audit (D-216), 2SFCA gap-0.3 and hospitals with beds (D-218).
- **Before deploying:**
  - Migration head 0006, the same as Supabase.
  - The API reads only the 7 tables granted to `vf_api_ro`.
  - New dependencies `openpyxl` (A's ingestion) and `axe-core` (web dev); neither affects the API image.
- **Gate:** green, with 469 Python tests and 226 web tests.
- **`make deploy-demo` (ALLOW_BRANCH=1):** 169 s, `dpl_Dn6j3oK7FUxBwnUnrLdsMmzK8NHq`, verified on round 2.
  - Round 1 was 8/8, but 4 of its 8 requests were served by the previous deployment `dpl_21KY…`. You can tell from the size: the old `/places` was 1.16 MB, the typed one 1.55 MB.
  - Round 2 was 8/8 with all 8 from the new deployment.
  - Output: [deploy-13/deploy-output.txt](deploy-13/deploy-output.txt). Search gave «33 of 199 zones, 1st Ciudad Lineal».
- **`make e2e-prod`:**
  - 1440 px: 66/66.
  - 390 px: 40/40, with the legend counts skipped (hidden up to 760 px).
  - The six rows already come with gap-0.3 («… al alcance a pie …»).
  - Report: [deploy-13/e2e-report.json](deploy-13/e2e-report.json).

## Incident: intermittent 500s from the Supabase pooler's connection limit
**Symptom:** the zone view (Fuencarral-El Pardo, Chamartín) sometimes fell into «Algo ha fallado por nuestra parte. Inténtalo de nuevo en unos minutos.». In one load, 4 of about 20 API requests returned 500: `places` by subcategory, `admin-units?level=barrio` and `gaps`.

**Cause, from `vercel logs`:**
- The error: `FATAL: (EMAXCONNSESSION) max clients reached in session mode - max clients are limited to pool_size: 15`.
- Its scale: 14 connection failures and 10 responses with 500 out of 212 requests in 30 min.
- The connection setup:
  - `DATABASE_URL` uses the Supavisor pooler in session mode (port 5432), capped at 15 clients in total.
  - Each API instance uses SQLAlchemy's default pool: 5 fixed connections plus 10 of overflow. This is `make_engine` in `packages/db/src/hi_db/session.py`, with no settings.
- Why it fills up:
  - The new web fires many requests in parallel: `places` by subcategory for «Todos los centros», barrios, gaps, datasets.
  - So Vercel starts several instances, and with three of them the 15 are full.

**Timeline (UTC, 12 Nov):**
| Time | What |
|---|---|
| 01:40 | Deploy `dpl_Dn6j…` verified, smoke 8/8 |
| 01:44–01:50 | e2e 66/66 and 40/40; the manual checks hit the 500s |
| 01:53 | Rollback per the guide to `dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ`: **worse**. Smoke 2/8 (`ready` 503, the rest 500), with 20 `EMAXCONNSESSION` in its logs: the live instances of the new deployment kept the 15 connections, and the old one's instance could not get any |
| 01:56 | `vercel promote dpl_Dn6j3oK7FUxBwnUnrLdsMmzK8NHq`: smoke 8/8 straight away. Production stays here |

**Root fix:** not C's, and not doable at night. Proposed to the orchestration:
- **(a) For serverless:** move `DATABASE_URL` to the pooler in transaction mode by changing only the port (5432 → 6543), which accepts many more clients. Also turn off psycopg's prepared statements with `connect_args={"prepare_threshold": None}` in `make_engine`. The secret is Mariano's, the code is A's.
- **(b) Mitigation without touching the secret:** a pool that can be set from the environment (for example `DB_POOL_SIZE` and `DB_MAX_OVERFLOW`). Set to 2 and 1 in Vercel, as Config, each instance holds at most 3 connections.
- **(c) B:** group the requests of the zone view.

## Manual checks (after the promote; no retries and no console errors on desktop or mobile)
Data: [deploy-13/manual-checks.json](deploy-13/manual-checks.json).
- **Hospitals in «Todos los centros», with their own names and beds:**
  - Fuencarral-El Pardo, 6 hospitals: «Hospital Universitario La Paz · 966 camas instaladas», plus Clínica Cemtro (100), Hospital Hestia Madrid (297), Psiquiátrico Doctor Rodríguez Lafora (336) and Ruber Internacional (143). The sixth comes out as just «Hospital», with no name and no beds, and the panel says «La fuente oficial no publica el nombre de cada centro de este tipo».
  - Chamartín, 5 hospitals: Quirónsalud San José (84), San Francisco de Asís (168), San Rafael (184), Virgen del Mar (73), and one «Hospital especializado · 50 camas instaladas» with no name.
  - Data notes for A: the hospital with no name in Fuencarral, and the one in Chamartín.
- **Pharmacies:** in their own category (`pharmacy`).
  - Chamartín has 114 and Fuencarral 124, named by address («Farmacia · Avenida de Alberto Alcocer 22»).
  - None inside `health`.
- **Redueña, «Qué falta»:** the escuelas infantiles and farmacias rows say «Comparado con municipios parecidos de la zona. Redueña es demasiado pequeño … lo juntamos con sus 7 vecinos más cercanos del mismo tipo: Cabanillas de la Sierra, El Vellón, …».
- **«Cómo lo calculamos»:** «Para cada servicio miramos cuánto tiene la gente de la zona a 15 minutos andando: un kilómetro por la calle, a paso tranquilo (4 km/h).» It also talks about capacity: «Solo usamos la capacidad que se publica».

## Production screenshots (`deploy-13/`)
- **Search, demo case:** [desktop](deploy-13/chromium-desktop-1440-j1-results.jpg) · [mobile](deploy-13/chromium-mobile-390-j1-results.jpg)
- **«Qué falta» Madrid:** [desktop](deploy-13/chromium-desktop-1440-j2-madrid.jpg) · [mobile](deploy-13/chromium-mobile-390-j2-madrid.jpg)
- **Map by row:** [desktop](deploy-13/chromium-desktop-1440-j3-row-map.jpg)
- **Hospitals, Fuencarral:** [desktop](deploy-13/desktop-fuencarral-hospitales.jpg) · [mobile](deploy-13/mobile-fuencarral-hospitales.jpg)
- **Hospitals, Chamartín:** [desktop](deploy-13/desktop-chamartin-hospitales.jpg) · [mobile](deploy-13/mobile-chamartin-hospitales.jpg)
- **Pharmacies, Chamartín:** [desktop](deploy-13/desktop-chamartin-farmacias.jpg) · [mobile](deploy-13/mobile-chamartin-farmacias.jpg)
- **Redueña:** [desktop](deploy-13/desktop-reduena-que-falta.jpg) · [mobile](deploy-13/mobile-reduena-que-falta.jpg)
- **«Cómo lo calculamos»:** [desktop](deploy-13/desktop-como-lo-calculamos.jpg) · [mobile](deploy-13/mobile-como-lo-calculamos.jpg)
