# Offline package regenerated with gap-0.3, B's web 1dfe69b and A's names · 2026-11-12 11:13 (Madrid)

Asked by D: the package still had data from before gap-0.3 (`1913393`).

## Regeneration (`make demo-offline-prepare`, 52 s)
- **Checkout:** `a5a2f07`, which is origin/claude/sprint-1-public `a334982` (B's web 1dfe69b, A's names up to HOSP-001 F3) plus line C's evidence.
- **Migration:** 0006 in both the source and the checkout, with no override.
- **Dump:** 42 MB. Its counts in [offline-gap03/manifest.txt](offline-gap03/manifest.txt) match Supabase after the last sync:

| Table | Rows |
|---|---|
| `feature_value` | 67,805 |
| `place_master` | 23,368 |
| `geo_admin_unit` | 4,973 |

- **Search:** on, as before (`NEXT_PUBLIC_FEATURE_SEARCH=true`).
- **Basemap:** still `tiles.openfreemap.org`. `NEXT_PUBLIC_MAP_TILES_URL` is not set, because the local extract is waiting for permission to run tilemaker.
- **Output:** [offline-gap03/prepare-output.txt](offline-gap03/prepare-output.txt).

## Start (`make demo-offline`, 8 s): smoke 7/7
The search gives «33 of 199 zones, 1st Ciudad Lineal», the same as production. Output: [offline-gap03/start-output.txt](offline-gap03/start-output.txt).

## Manual checks on the package (desktop and mobile, no console errors)
Data: [offline-gap03/offline-checks.json](offline-gap03/offline-checks.json).
- **Puente de Vallecas, «Qué falta» → «Escuelas infantiles»: FALTA.**
  - On screen: «Escuelas infantiles a 15 min andando por cada 1.000 niños de 0 a 4 años, repartidas entre todos los que las tienen cerca», with 2.8 in Puente de Vallecas against 4.9 in the other urban municipios (4.7 across the whole Comunidad).
  - The local API agrees: FALTA, ratio 0.571, `reliable: true`.
  - Screenshots: [desktop](offline-gap03/desktop-puente-vallecas-escuelas-infantiles.jpg) · [mobile](offline-gap03/mobile-puente-vallecas-escuelas-infantiles.jpg).
- **Fuencarral-El Pardo, «Todos los centros» → «Hospitales»:** 6 hospitals with beds and management.
  - The list: «Hospital Universitario La Paz · 966 camas instaladas · gestión pública», Lafora 336 (public), Hestia 297, Ruber Internacional 143 and Clínica Cemtro 100 (private).
  - The sixth still comes out as just «Hospital»; that data note is already with A.
  - Screenshots: [desktop](offline-gap03/desktop-fuencarral-hospitales.jpg) · [mobile](offline-gap03/mobile-fuencarral-hospitales.jpg).

## Pitch journeys against the package (`e2e_prod.mjs --base http://localhost:3012`, with network)
1440 px 66/66 and 390 px 40/40. Report: [offline-gap03/e2e-offline-report.json](offline-gap03/e2e-offline-report.json).

Package stopped afterwards with `make demo-offline-stop`.
