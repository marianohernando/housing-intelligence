# OPS-001 (line C) · deploy of 2761696 (OSM/CRTM credits always visible, «Sin escaleras», fit-0.4) and offline package equal to Supabase · 2026-11-12 16:20 (Madrid)

## Deploy
- **Code:** `2761696`, the HEAD of `claude/sprint-1-public`, CI green on all five jobs. It carries:
  - B's PR #26: AdminMap and MapPanel removed (`/map` now redirects to `/`), «© OpenStreetMap · Powered by CRTM» always visible beside the (i), now called «Fuentes y licencias de los datos», and the «Sin escaleras» chip;
  - A's fit-0.4 (DATA-019, D-223), which scores the walking minutes to a step-free station;
  - MCP-001 F1, which is local and does not change the API.
- **Data:** Supabase was synced with DATA-019 (`555c2b4`) before the deploy. Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_5QyHVrcXXn8KLrkucgGtQBikcykg`, verified on **round 0**, with all 8 requests from the new deployment. Smoke 8/8. Output: [deploy-18/deploy-output.txt](deploy-18/deploy-output.txt).

## Watch, 15:11–15:16 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 48 API requests and 0 5xx, plus 5 `/search` with the demo case, all 200. Output: [deploy-18/watch.txt](deploy-18/watch.txt).
  - 4 searches took 0.39–0.75 s.
  - 1 took 2.8 s: the first on a new instance.
- **Logs, 15:08–15:16 UTC:** [deploy-18/logs-summary.txt](deploy-18/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks | 0 |
| API access lines | 247, all 200 |
| Instances started | 7 |
| CDN records | 1,259: 1,253 × 200 and 6 × 307 |

- **The 307s** are `/map` → `/`, asked for by the credits probe.

## LCP, one pass on a phone with slow 4G
Report: [deploy-18/perf-report.json](deploy-18/perf-report.json). Elements: [deploy-18/lcp-elements.txt](deploy-18/lcp-elements.txt).

| Page | LCP | LCP element |
|---|---|---|
| home | **1.20 s** | the lead paragraph |
| zone Chamartín | **2.20 s** | «Mira sus servicios…», at 2.02 s |
| «Qué falta» Madrid | 0.88 s | — |

All three are under 2.5 s.

## OSM/CRTM credits seen without touching anything
- **Pages checked:** the home page and Chamartín, in Chromium, at desktop 1440 × 900, mobile 390 × 844 and projector 1024 × 576. Output: [deploy-18/credits-prod.txt](deploy-18/credits-prod.txt).
- **Each case:**
  - The links «© OpenStreetMap» and «Powered by CRTM» are inside the viewport, at opacity 1.
  - **0 of 5 points covered:** `elementFromPoint` at the four corners and the centre of each link returns the link itself.
  - **0 overlaps** with any button, link, input, heading or paragraph outside the map controls.
- **The (i):** «Fuentes y licencias de los datos».
- **Screenshots:** [desktop](deploy-18/credits-desktop-zona-distrito-2807905.jpg) · [mobile](deploy-18/credits-mobile-zona-distrito-2807905.jpg) · [projector](deploy-18/credits-projector-zona-distrito-2807905.jpg).

## `/search` with «sin_escaleras»
- **Request:** the demo case with the priorities `["sin_escaleras", "colegios", "transporte"]`. Output: [deploy-18/search-sin-escaleras.txt](deploy-18/search-sin-escaleras.txt).
- **Result:** the fact «Estación de metro o tren accesible (sin escaleras) a N min andando desde la mitad de sus calles» is in **10 of 10 results**.

| Rank | Zone | Match | Step-free station |
|---|---|---|---|
| 1 | Ciudad Lineal | 99 % | 10 min |
| 2 | Retiro | 97 % | 9 min |
| 3 | Centro | 95 % | 7 min |

- **Before this deploy:** the same request gave the fact in 0 of 10 results (fit-0.3).

## Offline package with 2761696
- **Row counts:** the 11 tables of the demo profile are **identical to Supabase**, with migration 0007 on both sides. The Supabase counts, read at about 15:14 UTC just before `prepare`, are in [supabase-counts.txt](deploy-18/offline/supabase-counts.txt), line by line equal to the package's manifest.

| Table | Rows |
|---|---|
| `feature_value` | 82,334 |
| `dataset_registry` | 42 |
| `dataset_version` | 53 |
| `feature_registry` | 42 |

- **Files:** [manifest](deploy-18/offline/package-manifest.txt) · [prepare](deploy-18/offline/prepare-output.txt) · [start](deploy-18/offline/start-output.txt).
  - `start-output.txt` still ends in «…3012/map».
  - That run is older than the guide fix below; `make demo-offline` now prints «…3012/».
- **API against production,** rounded to 1e-9, with `meta` left out: `/search` for the demo case, `/search` with sin_escaleras, the gaps of Madrid, Chamartín and Fuencarral-El Pardo, and `/datasets` are **all identical** ([api-vs-production.txt](deploy-18/offline/api-vs-production.txt)).
- **Smoke:** `make demo-offline`, 7/7.
- **Pitch journeys with `--block-external`:** 66/66 and 40/40, with **0 blocked hosts and 0 console errors** ([report](deploy-18/offline/e2e-nonet/e2e-report.json)).
- **Credits without network:** the same visible pair, uncovered and with no overlaps ([credits-offline.txt](deploy-18/offline/credits-offline.txt)).
  - The probe also finds a third «© OpenStreetMap»: the link of the local TileJSON, inside the folded list.
  - It is hidden (0 × 0) until the (i) opens it.

## Guide
- **`/map` now redirects to `/`.** The guide and the message of `make demo-offline` point at `/` directly, so the pitch avoids the redirect.
