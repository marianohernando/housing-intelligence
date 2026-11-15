# OPS-001 (line C) · deploy of 025a4a2, F6 (`fit-0.9`), and its sync · 2026-11-15 (Madrid)

## What the deploy brings
- **#76:** the «cerca y plazas» formula, `fit-0.9`, in the domain and the API (D-243).
- **#75:** the web for `fit-0.9`:
  - the % with its band and visible ties;
  - «Casi encajan» without a %;
  - the 2024 rent notice and «¿Trabajas fuera de casa?»;
  - Casarrubuelos's name kept whole.

## Order (D-243 §15)
1. Deploy the code.
2. Verify with the data Supabase had then.
3. datamad-10 recalculated `alquiler_m2_mensual_referencia` in `housing`:
   - reserve factor 1,1551 (`mediana_municipios`) for the 126 filled municipios, feature `version: 2`;
   - golden 10/10;
   - then `make supabase-sync PROFILE=demo` from 025a4a2.
4. Verify again. The sync landed between 15:49 and 15:51 UTC.

## Deploy · `dpl_8tDBNAFxt3S996JKcKht4yUZTJix` · 16:41
- **CI:** green on 025a4a2, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-32/deploy-output.txt](deploy-32/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.

## Before the sync: fit-0.8 → fit-0.9 with the same data
Details in [deploy-32/search.txt](deploy-32/search.txt). The fit-0.8 answers were taken from production just before the deploy, with the same bodies.
- **Smoke and e2e:**
  - smoke 13/13, `methodology_version` fit-0.9;
  - e2e **74/74** at 1440 px and **48/48** at 390 px, with the new 2024 notice checks: once when renting, never when buying, and by the rent in the card ([report](deploy-32/e2e-report-presync.json)).
- **Contract:** additive. Only `match_band` appears, in `results`, `near_misses` and `all_zones`. The datasets each answer cites are the same.
- **In all 7 cases the same zones fit;** only the % and the order change:

  | Case | Zones | What changes |
  |---|---|---|
  | The example | 42 of 199, 0 without data | % of 195 zones (182 down); 4 tied with the 1st → 2 |
  | Buying 400.000 € | 41 | same top 10 at 100 %; «casi» from 0 % to 56–14 % (the budget's tail) |
  | Telework | 42 | 10 tied → 3; Puente de Vallecas 97 first |
  | Renting 10.000 €/month | 183 | no %; the tie reorders as in the golden (Chamberí, Tetuán, Salamanca, Puente de Vallecas…) |
  | A couple at 1.500 € | 181 | no zone at the top changes its 100 %; Latina and Moratalaz swap (5th and 6th), and Parla replaces Navalagamella as 10th |
  | «Pueblos», a couple at 1.500 € | 122 of 138 | no %; the 9th: Serranillos del Valle instead of Alpedrete |
  | The golden student (500 €, URJC Vicálvaro) | 59 | Carabaña 53 first; Zarzalejo 32 with «No llegas a URJC Vicálvaro a las 9:00 en transporte público: el encaje se queda en la mitad» |

- **The pitch example**, as D-243 §9 says:
  - Top 10: Puente de Vallecas 94, Latina 94, Usera 93, Moratalaz 93, Tetuán 92, Ciudad Lineal 92, Villaverde 92, Carabanchel 90, Coslada 90 and Leganés 90, all `muy_bien`.
  - «Casi»: Chamartín 92, Arganzuela 92, Centro 91, Chamberí 91 and Retiro 91, all by `budget` and with `match_band` null.
  - The 42 by band: 12 `muy_bien`, 5 `bien`, 13 `regular` and 12 `poco`. The 157 that fail carry `null`.
  - Reality Check: +49 zones with 5 more min to the school, +3 with 150 € more.
- **Web at 1440 and 390** ([deploy-32/web-checks.txt](deploy-32/web-checks.txt)), with the same figures at both widths:
  - **The list:**
    - the 1st row reads «Encaja muy bien 94 %», under «Empatan al 94 %»;
    - «Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.» shows once;
    - there is no «¿Trabajas fuera de casa?», because the example has a place.
  - **Puente de Vallecas's card:**
    - the band, «Empata al 94 % con Latina.» and the 2024 notice;
    - its 5 facts as the API gives them, the rent one without «; un anuncio de hoy puede pedir más».
  - **«Casi encajan (5)»:**
    - no row has a %; they read «Se pasa ≈ 90 / 20 / 190 / 230 / 30 €/mes de tu presupuesto»;
    - Chamartín's card has no % pill and reads «Se pasa ≈ 90 €/mes…».
  - **Buying:** no 2024 notice, in the list or in the card.
  - **«¿Trabajas fuera de casa?»:**
    - It shows with «Toda la Comunidad», no place and «Colegios» marked, with its two buttons, «Dinos dónde» and «¿Dónde?».
    - It does not show with a place or with «Madrid capital».
    - With nothing marked, «Encajan 155 zonas igual de bien…» takes its place, as `resultados.sin_lugar` says.
  - **Casarrubuelos's card:** the name on one line and the «Encaja muy bien 100 %» pill under it, at both widths (review R-02 of #75, and item 1 of deploy-31).
  - **«Cómo lo calculamos»:**
    - the band table;
    - «Ejemplo real … Encajan 42 de las 199 zonas: 12 encajan muy bien, 5 bien, 13 regular y 12 poco»;
    - «Arriba empatan dos al 94 %: Puente de Vallecas y Latina»;
    - Latina's breakdown: «Pierde unos 6 puntos: 3 por esos 39 minutos de trayecto, y 1,1 por el colegio, 1,1 por la parada y 0,9 por el centro de salud…».
  - **The «la mitad» fact in a card:** a student-like search, the closest the web gets, with «Solo/a», 500 € and «Trabajo en» Vicálvaro (Cercanías). Titulcia, 9th at 17 % («Encaja poco»), shows «No llegas a Vicálvaro (Cercanías) a las 9:00 en transporte público: el encaje se queda en la mitad».
  - Screenshots:
    - [list 1440](deploy-32/presync-1440-1-ejemplo-lista.jpg) · [list 390](deploy-32/presync-390-1-ejemplo-lista.jpg);
    - [«casi» 1440](deploy-32/presync-1440-2-ejemplo-casi.jpg) · [«casi» 390](deploy-32/presync-390-2-ejemplo-casi.jpg);
    - [card 1440](deploy-32/presync-1440-3-ejemplo-tarjeta.jpg) · [card 390](deploy-32/presync-390-3-ejemplo-tarjeta.jpg);
    - [«¿Trabajas fuera de casa?» 390](deploy-32/presync-390-4-sin-lugar.jpg) · [«la mitad»](deploy-32/presync-1440-6-mitad.jpg) · [«Ejemplo real»](deploy-32/presync-1440-7-metodo-ejemplo.jpg).
- **Console:** 0 errors at both widths.
- **`check-qa.mjs`:** not run. It is pinned to localhost:3011 and is line B's tool.

## After the sync
- **Supabase** ([deploy-32/supabase-postsync.txt](deploy-32/supabase-postsync.txt)):
  - the same counts as after batch 4: `feature_registry` 68, `feature_value` 119,135 and 216 MB;
  - `alquiler_m2_mensual_referencia` is at version 2 in the registry, with 331 rows, all of version 2.
- **Smoke and e2e:** smoke 13/13 ([deploy-32/smoke-postsync.txt](deploy-32/smoke-postsync.txt)); e2e 74/74 and 48/48 ([report](deploy-32/e2e-report-postsync.json)).
- **The golden through the public API** ([deploy-32/golden-api.txt](deploy-32/golden-api.txt)): all 10 cases are line by line what `evidence/gate-06/2026-11-15-fit09/golden-search.txt` says:
  - zones, passing and unknown;
  - Reality Check;
  - the top 5 with % and cost, and every fact with its confidence;
  - «casi» and the San Blas barrios.
  - The golden student goes from 59 to **68** zones, with **Morata de Tajuña 68** first. 6 repeats of it gave the same.
- **The example and the other cases:** identical to before the sync. 0 zones change their %, and the order, «casi» and Reality Check are the same. Only the student changes:
  - 9 more zones fit (Bustarviejo, Casarrubuelos, Chinchón, Moraleja de Enmedio, Morata de Tajuña, Perales de Tajuña, Robledo de Chavela, Los Santos de la Humosa and Torrelaguna);
  - 61 zones go up;
  - «+50 €/mes» adds 20 (18 before).
- **«Pueblos», a couple renting up to 1.500 €:**
  - 120 of the 122 villages with a rent go down 4,2 to 4,6 % (median ratio 0,9558; 1,155 / 1,2085 = 0,9557).
  - Arroyomolinos and Navalcarnero do not change: they have their own AEAT table.
  - Zones, % and top 10 stay the same: every rent is still under 75 % of 1.500 €.
- **Casarrubuelos's card**, at both widths:
  - «Alquiler ≈ 546 €/mes · Dato aproximado» (571 before);
  - «La mitad de los contratos, entre 470 y 750 €/mes» (500–790);
  - «Elaboración propia a partir del Ministerio de Vivienda (SERPAVI), 2024»;
  - the 2024 notice under it.
  - Screenshots: [1440](deploy-32/postsync-1440-5-casarrubuelos.jpg) · [390](deploy-32/postsync-390-5-casarrubuelos.jpg).
- **The search with no place and «Colegios»:**
  - Titulcia is still 2nd at 98 %, now at ≈ 377 €/month (395 before);
  - the 97 % run grows from 10 to 11 zones;
  - «¿Trabajas fuera de casa?» still shows.
- **The student-like web search:** 68 zones, with Orusco de Tajuña 51, Perales de Tajuña 48 and Morata de Tajuña 46 first. Its top 10 no longer has a «la mitad» fact: Titulcia leaves it.
- **Console:** 0 errors at both widths.

## Logs, 15:39–15:57 UTC, through the sync
Details in [deploy-32/logs-summary.txt](deploy-32/logs-summary.txt).
- **Runtime:** 542 lines, all info, with 7 instances started.
  - 0 `fit bindings ignored` and 0 `WARNING`;
  - 0 pool, prepared-statement, authentication, validation or traceback lines.
- **CDN:** 1,803 records, 1,615 × 200 and 188 × 304. **0 4xx and 0 5xx.**

## For review, not blocking
1. **Small villages without a place.** With «Colegios» marked and no place, Titulcia comes 2nd at 98 % with a «Dato poco seguro» rent. This is the known risk of D-243 §13, and «¿Trabajas fuera de casa?» shows exactly there. datamad-10 takes it to the UX round.
2. **`pitch/guion.md:104` still says «27 conjuntos»;** the screen says 35. This is unchanged from deploy-31.

## Rollback
- **To `dpl_G26vdu…` (59187f8):** code only (D-243 §14). The old web ignores `match_band`. The sync changed values only, not rows of the registry, so the village rents would stay at 1,155.
- To go back to 1,2085 as well: D-243 §14 (`fallback: {level: ccaa, code: "28"}`, recalculate and sync).
- D-241 §9 still applies before `dpl_G26vdu…`.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
