# OPS-001 (line C) · deploy of ad4a8f2 (#53 commute limit, #54 D-233 stops by mode, #55 pitch) and D-233 sync · 2026-11-14 (Madrid)

## Order (D-233)
1. Deploy the code: ad4a8f2 understands the new features and ignores the fit roles, needs and priorities it does not know.
2. Smoke and e2e with the old data.
3. Sync: datamad-10 ran `make supabase-sync PROFILE=demo` from ad4a8f2.
4. Smoke and e2e again, and the transport fact checked.

## Rollback rule after the sync (D-233 §3)
**After this sync, do not roll back to any deployment before ad4a8f2** until the 2 rows `min_a_pie_bus` and `min_a_pie_metro` have been deleted from `feature_registry`. The deployments this rule covers include `dpl_5gWd6y97ixqWgub8c5m6wpMat1jE` (39644a9) and `dpl_7SDGd…` (5940ca7).

## Deploy · `dpl_HDY4ezEb35YLdtw5TXZCwXiKPnKq` · 13:47
- **CI:** green on ad4a8f2, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-27/deploy-output.txt](deploy-27/deploy-output.txt).
- **Verification:** on round 1.
  - Round 0: 3 of its 9 requests still came from `dpl_5gWd6…`.
  - Round 1: 9/9, all from the new deployment.
- **Before the sync:**
  - **Smoke:** 9/9, «27 of 199 zones, 1st Latina» and «7 of 8 barrios, 1st Canillejas».
  - **e2e:** 69/69 at 1440 px and 43/43 at 390 px ([deploy-27/e2e-report-presync.json](deploy-27/e2e-report-presync.json)). That includes the new `checkCommuteLimit`:
    - a limit of 45 min reaches `/search` as `max_minutes [45]`;
    - the summary reads 10 zones, the same as the API;
    - a limit never adds zones (10 ≤ 27).
  - **Transport fact:** «Parada de transporte público a unos N min andando» in all 10 results, with indicator `min_a_pie_transporte` ([deploy-27/search-presync.txt](deploy-27/search-presync.txt)).
  - **Supabase:** `feature_registry` had 47 rows, and neither it nor `feature_value` had any rows of `min_a_pie_bus` or `min_a_pie_metro` ([deploy-27/supabase-presync.txt](deploy-27/supabase-presync.txt)).

## After the sync
- **Supabase** ([deploy-27/supabase-postsync.txt](deploy-27/supabase-postsync.txt)):
  - `feature_registry` has 49 rows;
  - `feature_value` has 94,980 rows (+9,948): 4,974 for each new feature, the same shape as `min_a_pie_transporte`, the Comunidad reference (`ccaa`) included;
  - the other tables are unchanged.
- **Smoke:** 9/9, the same summaries ([deploy-27/smoke-postsync.txt](deploy-27/smoke-postsync.txt)).
- **e2e:** 69/69 and 43/43 ([deploy-27/e2e-report-postsync.json](deploy-27/e2e-report-postsync.json)).
- **`/search` with the demo case** ([deploy-27/search-postsync.txt](deploy-27/search-postsync.txt)):
  - 27 of 199 zones, Latina 98 %;
  - the transport fact reads **«Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 8 min»** for Latina, and the same pattern for all 10 results, from 7 to 12 min to Metro or Cercanías;
  - the indicator stays `min_a_pie_transporte`, so the web still tells it is a walk;
  - the ranking and the percentages are the same as before the sync.
- **`/search/barrios`, San Blas-Canillejas:** 7 of 8, with the same text. Simancas: «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 7 min». Rejas: «… Metro o Cercanías a unos 35 min».
- **On screen at 1440 and 390,** after «Ver un ejemplo» → Latina: the new text, the walking note, and no console errors ([deploy-27/screen-postsync.txt](deploy-27/screen-postsync.txt)). «Parada de transporte público» is left only as the name of a service in the «Lo quiero a un paseo» selector.

## Logs, 12:49–16:48 UTC
Details in [deploy-27/logs-summary.txt](deploy-27/logs-summary.txt).
- **Errors:** 0 `fit bindings ignored` warnings (the API's own text, also searched as «fit roles ignored» and «ignored»), and 0 WARNING lines.
  - Also 0 pool, prepared-statement or authentication errors and 0 tracebacks.
- **Traffic:** 31 instances started, and 278 of the 281 API lines are 200.
- **The 2 API 404s were at 16:45:07.** They were `GET /features/{hospitales_total,camas_instaladas_por_1000_hab}/values?level=ccaa`, the hospital note.
  - The API said «No values for … at ccaa», so `feature_value` had no rows for them at that moment, which is the window of the sync's reload.
  - Both answer 200 afterwards, three times in a row.
  - A sync while people use the demo hides that note for a moment. This is the same effect as the TRUNCATE on `/datasets` noted on 12 Nov.
- **Other 4xx:**
  - 416 (×14) and 405 from an anonymous bot at 13:02–13:03;
  - 404 for `/robots.txt` (OAI-SearchBot).
- **The WhatsApp link preview works:** `WhatsApp/2.23.20.0` fetched `/`, `/favicon.ico` and `/opengraph-image.png` at 14:25, 15:29 and 16:11, all 206.

## Not done in this batch
The offline package was not rebuilt, as asked: it comes with the next batch, which brings more data. Disk was at 4.1 GB free, and no local build was made.
