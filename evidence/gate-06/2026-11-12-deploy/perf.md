# Production performance · 2026-11-12 00:59 (Madrid)

Line C, test phase T3 (`prompts/FASE_PRUEBAS.md` §C).
- **Target:** https://vidafacil-madrid.vercel.app, deployment `dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ`.
- **Command:** `node infra/deploy/e2e/perf_prod.mjs --runs 3`.
- **Report:** [perf-report.json](perf-report.json), with every run.

## How it is measured
- **Browser and cache:** Chromium (Playwright 1.63). Every run uses a new context with the cache off, so it is an empty-cache load.
- **Phone, slow 4G:** the Lighthouse mobile profile.
  - Network: 150 ms RTT, 1.6 Mbps down, 750 kbps up, applied with CDP to the page's requests.
  - CPU 4× slower.
  - 390 × 844 at 2× device pixels.
- **Desktop:** 1440 × 900 with no throttling, for reference.
- **Metrics:**
  - LCP is the last `largest-contentful-paint` entry once the network goes idle.
  - FCP, and «load» (`loadEventEnd`).
  - Bytes are the response body plus headers of **every** request, including those of the map's Web Worker, counted with Playwright.
- **Limits:**
  - CDP does not throttle the Web Worker's requests, which are the basemap tiles from `tiles.openfreemap.org`. Their time on slow 4G is estimated from their bytes.
  - The canvas map is never an LCP candidate, so LCP measures text (the page's lead paragraph).

## Load: medians of 3 runs, empty cache
| Profile | Page | LCP | FCP | Load | Total | Web (HTML, JS, CSS, fonts) | API | Map tiles |
|---|---|---|---|---|---|---|---|---|
| phone, slow 4G | home `/` | **1.1 s** | 1.1 s | 3.2 s | 1,465 KB | 722 KB | 99 KB | 644 KB (≈ 3.1 s on slow 4G, estimated) |
| phone, slow 4G | zone `/zona/distrito/2807905` | **4.5 s** | 1.1 s | 3.1 s | 1,814 KB | 724 KB | 106 KB | 984 KB (≈ 4.8 s, estimated) |
| phone, slow 4G | «Qué falta» Madrid | **0.8 s** | 0.8 s | 1.6 s | 583 KB | 577 KB | 5 KB | 0 |
| desktop | home | 0.19 s | 0.19 s | 0.19 s | 2,726 KB | 717 KB | 99 KB | 1,911 KB |
| desktop | zone Chamartín | 0.98 s | 0.22 s | 0.26 s | 4,980 KB | 718 KB | 106 KB | 4,156 KB |
| desktop | «Qué falta» Madrid | 0.39 s | 0.18 s | 0.21 s | 583 KB | 577 KB | 5 KB | 0 |

- **Thresholds:** Core Web Vitals call an LCP under 2.5 s good and over 4 s poor.
  - On the phone with slow 4G, the home page (1.1 s) and «Qué falta» (0.8 s) are good.
  - **The zone view (4.5 s) is poor.**
- **Why the zone view is slow** (measured with the LCP entry and the Resource Timing of the API):
  - The LCP element is the paragraph «Mira sus servicios y puntos clave, con datos oficiales.», painted at about 4.58 s.
  - It appears right after `GET /api/v1/geo/admin-units?level=municipio&simplify_m=50` ends (about 330 KB; 3.21 → 4.54 s).
  - So the zone's text waits for the geometry of all the municipios.
  - Before that, the API is not called until about 3.2 s, the time it takes the phone to download and run the about 720 KB of JS.
  - After it, `gaps`, `datasets` and `barrio` start at 4.58 s, and `places` at 6.98 s: a waterfall.
- **Data used:**
  - The first visit to the home page uses 1.5 MB on a phone and 2.7 MB on a desktop.
  - The zone view uses 1.8 MB on a phone and 5 MB on a desktop: the tiles depend on the screen size and the zoom of the 3D view.
  - A repeat visit reuses the browser cache, which is off in this measurement.

## «Ver un ejemplo» → results on screen (warm API)
| Profile | From the click to `/search` responding | To «Con tu búsqueda tal cual…» on screen | `/search` body |
|---|---|---|---|
| phone, slow 4G | 353 · 411 · 367 ms | 393 · 452 · 434 ms | 107 KB |
| desktop | 536 · 830 · 316 ms | 541 · 834 · 331 ms | 107 KB |

## First `/search` cold
- **True cold, measured:** 5.96 s, then 0.30 s for the next one.
  - The API instances had shut down at 00:08 UTC, with no traffic for over 5 min.
  - The `/search` at 00:10:33 UTC started a new instance. In `vercel logs`: «Started server process» and «Uvicorn running» at 00:10:37.4, and the `POST /api/v1/search` 200 at 00:10:39.9.
  - Breakdown: about 3.5 s of container start plus about 2.5 s for the instance's first search (database connection and search caches).
- **New instance, warm container (11 Nov):** the first search on each new instance took 0.96–1.82 s ([deploy-11-search.md](../2026-11-11-deploy/deploy-11-search.md)).
- **Warm:** 0.29–0.44 s.
- **Two earlier attempts at cold could not be isolated.** Other sessions of the test phase kept the API warm, with requests every few seconds, and someone else had run a `/search` 2 s before mine.

## Proposals (not done)
- **C (smoke):**
  - The warm-up of the final day (`make smoke-demo` 2–3 min before presenting) does not call `/search`, so the first search of the pitch can still take 1–2.5 s if it lands on a fresh instance or caches.
  - Adding a `POST /api/v1/search` check with the demo case to `scripts/smoke_demo.sh` would warm it up, and would also cover search in the daily smoke.
- **B (web):**
  - In the zone view, paint the header (name, lead) without waiting for `admin-units?level=municipio`: from the route parameters or from a light zone request.
  - Start `gaps`, `datasets` and `places` in parallel.
  - Reduce or split the initial JS (about 720 KB transferred).
