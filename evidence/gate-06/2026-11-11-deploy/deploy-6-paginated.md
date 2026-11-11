# OPS-001 (line C) · redeploy with /places paginated (879101a) · 2026-11-11 15:36 UTC

## make deploy-demo at cf33a5b (= origin/claude/sprint-1-public + line C docs and smoke, ALLOW_BRANCH=1) · 92 s · smoke 7/7 on the first run
```
-> deploying cf33a5b (claude/s1-deploy) to production
    "id": "dpl_3EwQCx1BaXdxv7UQ6toooivr7wPi",
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T15:36:34Z)
OK   web         0.21s      5596 B  /
OK   health      0.14s       225 B  /api/v1/health  process up
OK   ready       0.13s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        3.45s      5036 B  /api/v1/gaps/municipio/28079  Madrid: 2 rows
OK   geography   0.75s    331879 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.25s   1156850 B  /api/v1/places?category=education  3851 places
OK   largest     0.57s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
```

## Transport pages in production
```
page 1: HTTP 200 1407222 B · 5000 features · total 14982 · pages 3 · warnings 1
page 2: HTTP 200 1407659 B · 5000 features · total 14982 · pages 3 · warnings 1
page 3: HTTP 200 1401201 B · 4982 features · total 14982 · pages 3 · warnings 0
page 4: HTTP 422 120 B · 0 features · total null · pages null · warnings 0
```
- The biggest page is about 1.4 MB, 31% of the 4.5 MB limit. The three pages add up to the 14,982 stops.
- Pages 1 and 2 carry the next-page warning. Page 4 returns 422 because it is out of range.
- Before this deploy, the new `largest` check failed against the previous deployment, which had no pagination (6/7, "unexpected body"). So the check does tell the two versions apart.

## Offline package regenerated with the paginated API
- prepare: 39 s. 42 MB dump. Source and checkout both at 0005, with no override.
- start: 8 s, smoke 6/6 (`largest`: 14982 stops, page 1/3).
- stop: no listeners left.
