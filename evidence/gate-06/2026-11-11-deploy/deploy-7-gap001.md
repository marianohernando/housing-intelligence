# OPS-001 (line C) · redeploy with GAP-001 F1–F3b and official names (D-212) · 2026-11-11 17:35 UTC

Supabase was synced by Mariano before this deploy (orchestrator check by MCP: `feature_value` 61,935 rows, names without «/» or «Ð», 106 MB).

## Gate at 995f7ce (= origin/claude/sprint-1-public after PR #7)
`make lint typecheck test-unit`: green, 310 Python tests and 11 web tests.

## make deploy-demo at 995f7ce (ALLOW_BRANCH=1) · 102 s · smoke 7/7 on the first run
```
warning: deploying branch 'claude/s1-deploy' (ALLOW_BRANCH=1)
-> deploying 995f7ce (claude/s1-deploy) to production
    "id": "dpl_25X3tSgAWMQVgsazzPUzWt148rei",
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T17:37:17Z)
OK   web         0.22s      5596 B  /
OK   health      3.00s       225 B  /api/v1/health  process up
OK   ready       3.48s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.55s     12237 B  /api/v1/gaps/municipio/28079  Madrid: 6 rows
OK   geography   1.55s    331914 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.43s   1156882 B  /api/v1/places?category=education  3851 places
OK   largest     0.35s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
```

## Which deployment answered that smoke (vercel logs --json, field deploymentId)
| Request | Deployment |
|---|---|
| `/api/v1/health` | `dpl_3EwQ…` (previous, cf33a5b) |
| `/api/v1/health/ready` | `dpl_25X3…` (new) |
| `/api/v1/gaps/municipio/28079` | `dpl_3EwQ…` (previous) |
| `/api/v1/geo/admin-units` | `dpl_25X3…` (new) |
| `/api/v1/places?category=education` | `dpl_25X3…` (new) |
| `/api/v1/places?category=transport` | `dpl_3EwQ…` (previous) |

- For about 10 s after the deploy reported ready, both deployments answered the production domain.
- `zone` came from the previous code reading the new data: 6 rows, no `extra_indicators`, 12,237 B. The new code returns 20,640 B for the same zone.
- So a smoke run right after the switch does not prove the new deployment by itself. The smoke below, two minutes later, does: all 6 API requests went to `dpl_25X3…`.

## Smoke two minutes later, with the stricter `largest` check (`.data.pages >= 1`)
```
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T17:39:15Z)
OK   web         0.36s      5596 B  /
OK   health      0.14s       225 B  /api/v1/health  process up
OK   ready       0.12s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.16s     20640 B  /api/v1/gaps/municipio/28079  Madrid: 6 rows
OK   geography   0.63s    331914 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.24s   1156882 B  /api/v1/places?category=education  3851 places
OK   largest     0.34s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
```
The new filter fails, as it should, when `pages` is 0, null or missing (checked with crafted bodies).

## Manual checks against production (new deployment)
`/api/v1/gaps/distrito/2807905` (Chamartín): HTTP 200, 18,865 B, 6 rows, all with `extra_indicators`.
```
escuela_infantil  CUBIERTO   min_a_pie_escuela_infantil=5.168 min
colegio           CUBIERTO   min_a_pie_colegio=5.815 min
centro_salud      FALTA      min_a_pie_centro_salud=9.466 min
mayores           FALTA      min_a_pie_mayores=10.01 min, plazas_residencia_por_100_mayores=3.712
farmacia          CUBIERTO   min_a_pie_farmacia=2.574 min
vivienda          SIN_DATOS  tamano_medio_hogar=2.4 personas/hogar (primary value null, SOURCE_MISSING)
```

`/api/v1/geo/admin-units?level=municipio`: HTTP 200, 466,286 B, 179 municipios.
- `28066 Griñón` and `28121 Redueña` are spelled correctly.
- No name contains «/», «Ð» or U+FFFD.
- Names with ñ: Carabaña, Cobeña, Fuentidueña de Tajo, Griñón, Morata de Tajuña, Orusco de Tajuña, Perales de Tajuña, Piñuécar-Gandullas, Redueña, Villanueva de la Cañada.

All 21 Madrid districts (`/api/v1/gaps/distrito/<code>`, codes from `admin-units?level=distrito&parent=ES.28.MUN.28079`): 6 rows and 7 extra indicators each, `vivienda` SIN_DATOS in all of them.
```
2807901 Centro               CUBIERTO=2 JUSTO=3 SIN_DATOS=1
2807902 Arganzuela           CUBIERTO=2 FALTA=1 JUSTO=2 SIN_DATOS=1
2807903 Retiro               CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807904 Salamanca            CUBIERTO=1 FALTA=2 JUSTO=2 SIN_DATOS=1
2807905 Chamartín            CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807906 Tetuán               CUBIERTO=2 FALTA=3 SIN_DATOS=1
2807907 Chamberí             CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807908 Fuencarral-El Pardo  CUBIERTO=2 FALTA=2 JUSTO=1 SIN_DATOS=1
2807909 Moncloa-Aravaca      CUBIERTO=3 JUSTO=2 SIN_DATOS=1
2807910 Latina               CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807911 Carabanchel          CUBIERTO=1 FALTA=2 JUSTO=2 SIN_DATOS=1
2807912 Usera                CUBIERTO=2 FALTA=2 JUSTO=1 SIN_DATOS=1
2807913 Puente de Vallecas   CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807914 Moratalaz            CUBIERTO=3 FALTA=1 JUSTO=1 SIN_DATOS=1
2807915 Ciudad Lineal        CUBIERTO=3 FALTA=2 SIN_DATOS=1
2807916 Hortaleza            CUBIERTO=1 FALTA=2 JUSTO=2 SIN_DATOS=1
2807917 Villaverde           CUBIERTO=2 FALTA=2 JUSTO=1 SIN_DATOS=1
2807918 Villa de Vallecas    FALTA=2 JUSTO=3 SIN_DATOS=1
2807919 Vicálvaro            CUBIERTO=1 FALTA=3 JUSTO=1 SIN_DATOS=1
2807920 San Blas-Canillejas  CUBIERTO=2 FALTA=2 JUSTO=1 SIN_DATOS=1
2807921 Barajas              CUBIERTO=3 FALTA=1 JUSTO=1 SIN_DATOS=1
```

## Sync during the final: what the demo shows
`scripts/supabase_sync.sh` truncates the demo tables in one statement and copies them back one by one. `/gaps` drops a row when its feature has no value at that level. So mid-sync the list comes back with no rows, and the smoke fails on `ready` (no geography) or on `zone` (no rows) until the copy ends. The README now forbids a sync in the hour before presenting.
