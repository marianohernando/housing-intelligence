#!/usr/bin/env bash
# Offline demo for the final (26 Nov): API + web on this laptop from a dump of the demo profile,
# in an isolated Postgres (compose project vida-facil-offline, ports 5441/8012/3012). It only
# reads the development database (to dump it) and never uses its ports (5440/8010/3010).
#   make demo-offline-prepare   # online, e.g. 23 Nov: dump, images, offline DB, web build
#   make demo-offline           # 26 Nov: start in about a minute, no network needed
#   make demo-offline-stop
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

COMPOSE=(docker compose -f infra/deploy/offline/compose.yml)
OUT="${DEMO_OFFLINE_DIR:-data/offline}"
DUMP="$OUT/demo-data.sql.gz"
MANIFEST="$OUT/manifest.txt"
WEB_PID="$OUT/web.pid"
WEB_LOG="$OUT/web.log"
# Source of the dump, seen from inside the offline db container: the development database.
SOURCE_URL="${SOURCE_DATABASE_URL:-postgresql://housing:housing@host.docker.internal:5440/housing}"
OFFLINE_URL="postgresql+psycopg://vidafacil:vidafacil@localhost:5441/vidafacil"
API_URL="http://localhost:8012"
WEB_PORT=3012
WEB_URL="http://localhost:${WEB_PORT}"
WEB_APP="apps/web/.next/standalone/apps/web"   # Next.js standalone output (output: "standalone")
# The demo profile of scripts/supabase_sync.sh (tests/unit/test_deploy_offline.py checks it).
TABLES=(source_registry dataset_registry dataset_version metric_registry feature_registry geo_admin_unit place_master place_source_alias feature_value)

offline_psql() { "${COMPOSE[@]}" exec -T db psql -U vidafacil -d vidafacil -v ON_ERROR_STOP=1 "$@"; }
source_psql() { "${COMPOSE[@]}" exec -T db psql "$SOURCE_URL" -v ON_ERROR_STOP=1 "$@"; }

counts() { # psql function, then: one "table count" line per demo table
  local run="$1" t
  for t in "${TABLES[@]}"; do printf '%s %s\n' "$t" "$("$run" -Atc "select count(*) from public.$t")"; done
}

wait_for() { # URL SECONDS
  local i
  for ((i = 0; i < $2 * 2; i++)); do
    curl -fs -o /dev/null -m 2 "$1" && return 0
    sleep 0.5
  done
  echo "timeout waiting for $1" >&2
  return 1
}

prepare() {
  mkdir -p "$OUT"
  echo "-> images and an empty offline database (vida-facil-offline, port 5441)"
  stop_web
  "${COMPOSE[@]}" down --volumes --remove-orphans
  "${COMPOSE[@]}" build
  "${COMPOSE[@]}" up -d --wait db

  local source_head head
  source_head="$(source_psql -Atc 'select version_num from alembic_version')"
  head="$(uv run alembic -c infra/migrations/alembic.ini heads 2>/dev/null | awk '{print $1}')"
  if [[ "$source_head" != "$head" ]]; then
    echo "source database is at migration $source_head, this checkout at $head" >&2
    # Only for migrations that do not touch the demo tables (e.g. 0005 only adds a role).
    [[ "${DEMO_OFFLINE_ALLOW_HEAD_MISMATCH:-0}" == "1" ]] || exit 2
    echo "continuing: DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1" >&2
  fi

  echo "-> dumping the demo profile from the development database (read only)"
  local table_args=() t
  for t in "${TABLES[@]}"; do table_args+=(--table "public.$t"); done
  "${COMPOSE[@]}" exec -T db pg_dump "$SOURCE_URL" --data-only --disable-triggers --no-owner \
    --no-privileges "${table_args[@]}" 2> >(grep -v -E "circular foreign-key|detail:|hint:" >&2) \
    | gzip -9 >"$DUMP"
  {
    echo "created_at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "git_commit $(git rev-parse --short HEAD)"
    echo "alembic_head $head (source $source_head)"
    counts source_psql
  } >"$MANIFEST"

  echo "-> schema (alembic $head) and data into the offline database"
  uv run alembic -c infra/migrations/alembic.ini -x url="$OFFLINE_URL" upgrade head >/dev/null
  gunzip -c "$DUMP" | offline_psql -q >/dev/null
  if ! diff <(grep -v -E '^(created_at|git_commit|alembic_head) ' "$MANIFEST") <(counts offline_psql); then
    echo "row counts differ: the source changed during the dump or the load failed; rerun" >&2
    exit 1
  fi

  echo "-> web production build pointing at $API_URL"
  NEXT_PUBLIC_API_URL="$API_URL" npm run -w apps/web build >/dev/null
  # Standalone server (one process, unlike `next start`): it needs static assets and public/.
  rm -rf "$WEB_APP/.next/static" "$WEB_APP/public"
  cp -R apps/web/.next/static "$WEB_APP/.next/static"
  cp -R apps/web/public "$WEB_APP/public"
  "${COMPOSE[@]}" down
  echo "ready: $(du -h "$DUMP" | cut -f1) dump, manifest $MANIFEST. Start with: make demo-offline"
}

start() {
  [[ -f "$DUMP" ]] || { echo "no offline dump: run make demo-offline-prepare first (online)" >&2; exit 2; }
  [[ -f "$WEB_APP/server.js" && -d "$WEB_APP/.next/static" ]] ||
    { echo "no web build: run make demo-offline-prepare" >&2; exit 2; }
  if curl -fs -o /dev/null -m 2 "$WEB_URL"; then
    echo "port $WEB_PORT is already serving something: make demo-offline-stop first" >&2
    exit 2
  fi
  echo "-> database and API (no network needed)"
  "${COMPOSE[@]}" up -d --wait --no-build db api
  echo "-> web on $WEB_URL"
  PORT="$WEB_PORT" HOSTNAME=127.0.0.1 nohup node "$WEB_APP/server.js" >"$WEB_LOG" 2>&1 &
  echo $! >"$WEB_PID"
  wait_for "$WEB_URL" 60
  SMOKE_API_ONLY=1 scripts/smoke_demo.sh "$API_URL"
  echo "offline demo up: $WEB_URL/map  (data: $(head -1 "$MANIFEST"))"
}

stop_web() {
  if [[ -f "$WEB_PID" ]]; then
    kill "$(cat "$WEB_PID")" 2>/dev/null || true
    rm -f "$WEB_PID"
  fi
}

stop() {
  stop_web
  "${COMPOSE[@]}" down
  echo "offline demo stopped (data kept in the vida-facil-offline volume)"
}

case "${1:-}" in
  prepare) prepare ;;
  start) start ;;
  stop) stop ;;
  *) echo "usage: $0 prepare|start|stop" >&2; exit 2 ;;
esac
