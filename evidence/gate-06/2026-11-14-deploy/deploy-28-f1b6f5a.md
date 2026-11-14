# OPS-001 (line C) · deploy of f1b6f5a, batch 2a (#56 D-239 tie-break and public or private hospitals, #58 D-238 «¿Dónde?») · 2026-11-14 (Madrid)

## What changed
- **#56, D-239:**
  - «Zonas que encajan» breaks exact ties by everyday services at a walk;
  - the list warns «Encajan N zonas igual de bien» when more than 10 tie;
  - each hospital says «Hospital público», «Hospital público · gestión privada» or «Hospital privado»;
  - `/places` gains `dependency` and `management`, both additive.
- **#58, D-238:**
  - the «¿Dónde?» selector: Toda la Comunidad, Madrid capital (131 barrios), Alrededores de Madrid and Pueblos;
  - `ScenarioState.scope` is optional, and the web leaves it out with «Toda»;
  - the zoning ships in the API image (`hi_domain/geo/zoning_data.py`).
- **No sync:** code only.

## Deploy · `dpl_59jvNLYJAitb5mopLmjGMmpXuogg` · 19:40
- **CI:** green on f1b6f5a, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-28/deploy-output.txt](deploy-28/deploy-output.txt).
- **Verification:** on round 0. The smoke passed 9/9, and all 9 of its requests came from the new deployment.
- **e2e:** 69/69 at 1440 px and 43/43 at 390 px ([deploy-28/e2e-report.json](deploy-28/e2e-report.json)). The new copy broke no check.

## The demo case, before and after
Details in [deploy-28/search-scopes.txt](deploy-28/search-scopes.txt).
- **`/search` without `scope`:**
  - 27 of 199 zones;
  - the top 10 starts Latina, Moratalaz, Ciudad Lineal and Puente de Vallecas, all at 98 %;
  - «Casi encajan» is Chamartín, Salamanca, Centro, Chamberí and Retiro, at 93 %.
- **Against the production answer from just before the deploy:** identical, with `meta` left out, once the echoed `scope` is removed. The only change is 3 new `"scope": "all"` fields: in `scenario` and in the 2 `relaxed_scenario`. This is the echo of D-238 §6.
- **`/search/barrios`:** identical in the same way for San Blas-Canillejas and Latina.

## `/search` by «¿Dónde?» (D-238)
All four give 200, with the demo case. Details in [deploy-28/search-scopes.txt](deploy-28/search-scopes.txt).

| `scope` | Echo | Zones that fit | Level | 1st |
|---|---|---|---|---|
| none | `all` | 27 of 199 | districts and municipios | Latina 98 % |
| `madrid` | `madrid` | 78 of 131 | barrios only | Lucero 99 %, then Campamento 99 % and Media Legua 98 % |
| `alrededores` | `alrededores` | 14 of 40 | municipios only | Alcorcón 95 % |
| `pueblos` | `pueblos` | 1 of 138 | municipios only | Navalcarnero 84 % |

- **«Madrid capital»** gives the same figures as D-238 §8: 78 of 131, with Lucero and Campamento at 99 %. The Reality Check keeps the scope in `relaxed_scenario`.
- **«Pueblos»** has only 1 zone that fits because most villages publish no rent, so the budget is UNKNOWN (D-214). The binding constraint is the budget.
- **The smoke now covers these three** ([deploy-28/smoke-12.txt](deploy-28/smoke-12.txt)), 12/12 against production.
  - Each check needs 200, the scope echoed back, and the right level: only barrios in Madrid capital, only municipios in the other two.
  - None needs a zone that fits, because «Pueblos» may have none.
  - The checks were also run on purpose against wrong answers. They fail with the answer without `scope`, with the one from before this deploy, and with «alrededores» checked as «pueblos».

## `/places` (D-239)
Details in [deploy-28/places-health.txt](deploy-28/places-health.txt).
- **The new fields are additive.** The 553 health places gain `dependency` and `management`, and every other field is identical to before the deploy.
- **85 hospitals:**
  - 35 public, 5 of them run by a company: the Fundación Jiménez Díaz (651 beds), Torrejón, Móstoles (the Rey Juan Carlos, still unnamed), Villalba and Infanta Elena;
  - 50 private.
  - These are the figures in the PR #56 evidence.

## On screen, 1440 and 390
Details in [deploy-28/web-checks.txt](deploy-28/web-checks.txt).
- **«Ver un ejemplo» sends no `scope`,** and Latina comes 1st.
- **«¿Dónde?»:**
  - four radios, with «Toda la Comunidad» checked;
  - its help line changes with the option checked.
  - Screenshots: [1440](deploy-28/1440-1-selector.jpg) · [390](deploy-28/390-1-selector.jpg).
- **Madrid capital:**
  - the web sends `scope: madrid` and asks for the 131 barrio outlines (200);
  - the list reads «Con tu búsqueda tal cual salen 78 barrios. De 131 barrios de Madrid capital.», with rows «Lucero · Latina» and «Barrio de Madrid»;
  - the map paints the barrios of the capital by their fit and leaves the rest of the region unpainted;
  - the legend counts 78 + 52 + 1 = 131;
  - the map's `aria-label` adds «Madrid capital sale por barrios…».
  - Screenshots: [1440](deploy-28/1440-2-madrid-mapa.jpg) · [390](deploy-28/390-2-madrid-mapa.jpg).
- **Alrededores and Pueblos:**
  - the web sends their `scope`;
  - the lists read «De 40 municipios de los alrededores de Madrid.» and «De 138 pueblos de la Comunidad de Madrid.»;
  - the «Pueblos» help warns that almost none publish their rent.
  - Screenshot: [Pueblos at 1440](deploy-28/1440-4-pueblos.jpg).
- **Moncloa-Aravaca, «Hospitales» (6):**
  - the list shows «Hospital público · gestión privada · Hospital Universitario Fundación Jiménez Díaz · 651 camas instaladas»;
  - the Clínico San Carlos is public, and the other four are private.
  - Screenshots: [1440](deploy-28/1440-5-hospitales-moncloa.jpg) · [390](deploy-28/390-5-hospitales-moncloa.jpg).
- **Errors:** 0 console errors and 0 HTTP ≥ 400 at both widths.

**Two copy details for review, not blocking:**
1. **The legend says «zonas» while the list says «barrios».** With «Madrid capital», the legend reads «Cumple todo 78 zonas», and the list reads «salen 78 barrios».
2. **The map's `aria-label` contradicts itself.** It still starts with the general sentence «… con Madrid capital dividida en sus 21 distritos.» before «Madrid capital sale por barrios…».

## Logs, 18:38–18:45 UTC
Details in [deploy-28/logs-summary.txt](deploy-28/logs-summary.txt).
- **Runtime:** 208 lines, all info, with 7 instances started.
  - 0 for every search: `WARNING`, `ignored`, `ValidationError`, `Traceback`, pool, prepared-statement and authentication errors.
- **CDN:** 717 records, 705 × 200 and 12 × 304, with **no 4xx or 5xx**. That includes the smoke, the e2e and these checks.

## Offline package
- **Not regenerated, as asked.** It is still at 39644a9.
- **It does not know `scope`.** With the new smoke, its 3 «¿Dónde?» checks fail until it is regenerated. The README now says so.

## Rollback
- **If needed:** `dpl_HDY4ezEb35YLdtw5TXZCwXiKPnKq` (ad4a8f2). It reads the same data, but it brings back the old ranking for ties, the old hospital labels and the search without «¿Dónde?».
- **The D-233 rule still applies:** no rollback to anything before ad4a8f2 without first deleting the 2 `feature_registry` rows.
