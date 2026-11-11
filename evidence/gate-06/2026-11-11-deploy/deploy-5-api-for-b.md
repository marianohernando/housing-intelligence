# OPS-001 (line C) · redeploy with the new API changes from line A (2026-11-11 15:15 UTC)

This redeploy brings three API changes from line A: d3127d3 (one `/gaps` warning per missing row), d7037b7 (`/places` filters, no 10,000 cap) and 12c834a (`/geo/admin-units` readable names and `?parent=`).

## make deploy-demo at 1c22212 (= origin/claude/sprint-1-public, ALLOW_BRANCH=1) · 106 s · smoke 6/6 on the first run
```
-> deploying 1c22212 (claude/s1-deploy) to production
    "id": "dpl_BQdF1bhdZsCpQtxphfJBfwEhUc61",
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T15:15:36Z)
OK   web         0.97s      5596 B  /
OK   health      3.00s       225 B  /api/v1/health  process up
OK   ready       0.91s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.36s      5036 B  /api/v1/gaps/municipio/28079  Madrid: 2 rows
OK   geography   1.14s    331879 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.64s   1156850 B  /api/v1/places?category=education  3851 places
smoke: 6/6 OK
```

## Manual checks (vf_api_ro with the new filters)
```
$ /api/v1/places?category=transport&admin_unit_id=ES.28.DIS.2807905&subcategory=metro&subcategory=cercanias
15 points: cercanias=1, metro=14
$ /api/v1/geo/admin-units?level=distrito&parent=ES.28.MUN.28079
21 districts: Centro, Arganzuela, Retiro, Salamanca, Chamartín, Tetuán, Chamberí, Fuencarral-El Pardo, Moncloa-Aravaca, Latina, Carabanchel, Usera, Puente de Vallecas, Moratalaz, Ciudad Lineal, Hortaleza, Villaverde, Villa de Vallecas, Vicalvaro, San Blas-Canillejas, Barajas
$ /api/v1/gaps/distrito/2807905 (warnings)
colegio=FALTA, centro_salud=FALTA
INSUFFICIENT_DATA: row escuela_infantil not computed at distrito level yet
INSUFFICIENT_DATA: row mayores not computed at distrito level yet
INSUFFICIENT_DATA: row farmacia not computed at distrito level yet
INSUFFICIENT_DATA: row vivienda not computed at distrito level yet
```
Note: the URLs in the request lacked required parameters. `/places` requires `category` (422 without it) and `?parent=` needs `level=distrito`, because the default level is municipio. With those parameters everything comes back as expected.

## The largest response now that /places has no cap
```
transport: 200 4215307 B
health: 200 1296894 B
education: 200 1156850 B
social: 200 317290 B
```
Transport weighs 4.2 MB, which is 94% of the 4.5 MB Vercel limit. `scripts/smoke_demo.sh` now also measures that layer (`largest`):
```
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T15:17:01Z)
OK   web         0.09s      5596 B  /
OK   health      0.22s       225 B  /api/v1/health  process up
OK   ready       0.12s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.15s      5036 B  /api/v1/gaps/municipio/28079  Madrid: 2 rows
OK   geography   1.51s    331879 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.23s   1156850 B  /api/v1/places?category=education  3851 places
OK   largest     0.66s   4215307 B  /api/v1/places?category=transport  14982 stops
smoke: 7/7 OK
```
