# Device matrix of the pitch journeys in production · 2026-11-12 00:50 (Madrid)

Line C, test phase T2 (`prompts/FASE_PRUEBAS.md` §C).
- **Target:** https://vidafacil-madrid.vercel.app, deployment `dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ`, with search on.
- **Command:**
  ```
  node infra/deploy/e2e/e2e_prod.mjs --browsers chromium,webkit,firefox \
    --devices desktop-1440,desktop-1920,mobile-390,projector-125 --shots --out <dir>
  ```
- **Browsers:** Playwright 1.63, with Chromium, WebKit 26.6 (the Safari engine) and Firefox 155.
- **Report:** [e2e-matrix-report.json](e2e-matrix-report.json), with all 414 checks and their details.

## Devices
| Id | Viewport (CSS px) | Device pixels | Notes |
|---|---|---|---|
| desktop-1440 | 1440 × 900 | 1 | |
| desktop-1920 | 1920 × 1080 | 1 | The resolution planned for the room (`pitch/guion.md`) |
| mobile-390 | 390 × 844 | 2 | Touch and mobile emulation in Chromium and WebKit. Firefox has no mobile emulation in Playwright, so it gets the same size without it |
| projector-125 | 1024 × 576 | 1.25 | A 1280 × 720 projector with the browser at 125 % zoom |

## What each run checks
The four journeys of `infra/deploy/README.md` («Recorridos del pitch»). Every figure on screen is compared with the API response the page received:
- **J1:** the demo case, the legend, the 1st zone card (name, % and facts), and «¿Y si cambias algo?» applied and undone.
- **J2:** «Qué falta» in Madrid.
- **J3:** the map by row, first row only when taking screenshots.
- **J4:** the zone list.

On top of that: browser console errors and horizontal overflow.

## Results
| Browser | Device | Passed | Skipped | Failed | Console errors | Time |
|---|---|---|---|---|---|---|
| chromium | desktop-1440 | 36 | 0 | 0 | 0 | 22 s |
| chromium | desktop-1920 | 36 | 0 | 0 | 0 | 19 s |
| chromium | mobile-390 | 28 | 2 | 0 | 0 | 19 s |
| chromium | projector-125 | 36 | 0 | 0 | 0 | 18 s |
| webkit | desktop-1440 | 36 | 0 | 0 | 0 | 19 s |
| webkit | desktop-1920 | 36 | 0 | 0 | 0 | 18 s |
| webkit | mobile-390 | 28 | 2 | 0 | 0 | 19 s |
| webkit | projector-125 | 36 | 0 | 0 | 0 | 19 s |
| firefox | desktop-1440 | 36 | 0 | 0 | 0 | 19 s |
| firefox | desktop-1920 | 36 | 0 | 0 | 0 | 19 s |
| firefox | mobile-390 | 28 | 2 | 0 | 0 | 21 s |
| firefox | projector-125 | 36 | 0 | 0 | 0 | 19 s |

- **Skipped:** the legend counts on mobile. The legend hides them at that width on purpose (`Legend.module.css`), so they are not counted as passed.
- **Data:** the same in every combination. The demo case gives 32 of 199 zones, and the first is Ciudad Lineal at 99 %. «+5 min a pie hasta colegio con primaria» gives 49 zones, and undoing it gives 32 again. Madrid has 6 rows.

## Visual review (all 48 screenshots, one sheet per journey)
**Correct:** desktop 1440 and 1920, and mobile 390, in the three browsers. J2 («Qué falta» in Madrid) is also correct on the projector.

**Fault on the projector, the same in the three browsers.** This is visual: the data checks pass. On the home page with the map (J1, J3), at 1100 CSS px wide or less:
- **The region map shows up tiny and is not framed.** At 1024 × 576 and at 1024 × 768 the Comunidad is a blob of a few dozen px.
  - [projector J1](matrix/chromium-projector-125-j1-results.jpg)
  - [projector J3](matrix/chromium-projector-125-j3-row-map.jpg)
  - [1024 × 768](matrix/sizes-home-1024x768.jpg)
- **The «¿Qué quieres ver?» legend covers the left column:** the «Ver un ejemplo» button, the search and the zone card's facts.
  - [projector J1 card](matrix/chromium-projector-125-j1-card.jpg)
  - [1024 × 576 at 125 %](matrix/sizes-home-1024x576-zoom125.jpg)
- **At 1280 × 720 and 100 %** the map is framed well, but the legend still slightly covers the right edge of the search card ([1280 × 720](matrix/sizes-home-1280x720.jpg)).
- **At 1366 × 768 and above** there is no overlap.

Measured with Chromium, as the overlap of the legend's box with «Ver un ejemplo»:
| Size | Device pixels | Legend over «Ver un ejemplo» |
|---|---|---|
| 1024 × 576 | 1.25 | yes |
| 1024 × 768 | 1 | no (it covers the search card instead) |
| 1100 × 700 | 1 | no |
| 1101 × 700 | 1 | no |
| 1280 × 720 | 1 | no |
| 1366 × 768 | 1 | no |
| 1536 × 864 | 1.25 | no |

What to do, decided by D and B: on the day, present at 1920 × 1080 and 100 %, as the script says. If the projector forces 1280 × 720, do not zoom in. The layout fix (framing the map and placing the legend at ≤ 1100 px) belongs to `apps/web`, line B.

## Screenshots (`matrix/`)
Named `<browser>-<device>-<step>.jpg`, with step `j1-results`, `j1-card`, `j2-madrid` or `j3-row-map`. That is 12 combinations × 4 steps = 48. They are JPEG at quality 55, and the mobile and projector ones are scaled to CSS pixels. The `sizes-*` files are the size probe of the home page.
