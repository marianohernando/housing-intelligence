# OPS-001 (line C) · API image and dependency size (2026-11-11)

## API dependency closure (`hi-api`, no dev group)
Measured before choosing the host. The API depends on `hi-contracts`, `hi-db` and `hi-domain`; `hi-domain` brings scipy, numpy, pyproj, shapely and h3.

| Package | macOS arm64 installed | Linux x86_64 wheel unzipped |
|---|---|---|
| scipy 1.18.1 | 70.5 MB | 111.9 MB |
| numpy 2.5.4 | 20.6 MB | 56.4 MB |
| pyproj 3.8.0 | 19.6 MB | 35.1 MB |
| psycopg-binary 3.3.6 | 17.6 MB | 19.9 MB |
| sqlalchemy 2.1.5 | 10.1 MB | 18.2 MB |
| uvloop 0.23.0 | 4.3 MB | 16.6 MB |
| shapely 2.2.0 | 5.3 MB | 7.8 MB |
| pydantic-core 2.50.1 | 4.7 MB | 5.2 MB |
| **Total closure** | **166.9 MB** | **≈ 280 MB** (8 largest: 271 MB) |

Method: `importlib.metadata` file sizes in the local venv; Linux wheels from the PyPI JSON API, unzipped in memory (cp312 manylinux x86_64).

At runtime the API imports only fastapi, pydantic, sqlalchemy, psycopg and pure-Python modules of `hi_domain` (`gaps`, `geo.names`). The scientific stack is installed but not imported, so it does not slow the start.

## Image `infra/deploy/api/Dockerfile`
- Build: `docker build -f infra/deploy/api/Dockerfile .` from the repo root. Exit 0 in 27 s with a warm cache (linux/arm64).
- `uv sync --frozen --no-dev --package hi-api --no-editable` installs only the API closure. The workspace packages are installed as wheels: `hi_api`, `hi_contracts`, `hi_db`, `hi_domain`.
- Python 3.12.16. Runs as non-root `uid=10001(api)`. Listens on `$PORT` (default 8080).
- Image: 151 MB compressed. `/opt/venv` is 370 MB unpacked, including the precompiled bytecode.

## Local run
- Against the local DB through the API (port 8012): `api-container-smoke.txt`, 5/5 OK.
- The largest response is `places?category=transport` at 2.8 MB, capped at 10,000 points. Every response is under the 4.5 MB limit of Vercel Functions.
- Read-only role: `readonly-role-local.txt`. Validated in a throwaway DB `housing_test_c`, which was dropped afterwards together with the role.

## Note on Docker Desktop
`docker build` hung on `resolve image config` because the `desktop` credential helper (macOS keychain) did not answer. Anonymous pulls work with a scratch `DOCKER_CONFIG` that has no `credsStore` plus a symlink to `~/.docker/cli-plugins`. The global Docker config was not changed.
