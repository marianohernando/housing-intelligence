#!/usr/bin/env bash
# Offline demo for the final (26 Nov): API + web on this laptop from a dump of the demo profile,
# in an isolated Postgres (compose project vida-facil-offline, ports 5441/8012/3012). It only
# reads the development database (to dump it), never uses its ports (5440/8010/3010) and never
# touches apps/web/.next (the web is built from a private copy).
#   make demo-offline-prepare   # online, e.g. 23 Nov: images, dump, validated database, web build
#   make demo-offline           # 26 Nov: start in seconds, no network needed
#   make demo-offline-stop
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# -p pins the project: a COMPOSE_PROJECT_NAME in the environment (e.g. exported from .env by make)
# must never aim these commands at the development stack.
COMPOSE=(docker compose -p vida-facil-offline -f infra/deploy/offline/compose.yml)
OUT="data/offline"                 # inside the checkout, ignored by git
DUMP="$OUT/demo-data.sql.gz"
MANIFEST="$OUT/manifest.txt"
WEB_BUILD="$OUT/web-build"         # private copy of apps/web, built for the offline API
WEB_RUN="$OUT/web"                 # standalone server assembled from that build
WEB_PID="$OUT/web.pid"
WEB_LOG="$OUT/web.log"
# Source of the dump, seen from inside the offline db container: the development database.
SOURCE_URL="${SOURCE_DATABASE_URL:-postgresql://housing:housing@host.docker.internal:5440/housing}"
DB=vidafacil
STAGING=vidafacil_staging
API_URL="http://localhost:8012"
WEB_PORT=3012
WEB_URL="http://localhost:${WEB_PORT}"
# The demo profile of scripts/supabase_sync.sh (tests/unit/test_deploy_offline.py checks it).
TABLES=(source_registry dataset_registry dataset_version metric_registry feature_registry geo_admin_unit place_master place_source_alias feature_value)

trap 'echo "demo-offline: failed at line $LINENO. Clean up with: make demo-offline-stop" >&2' ERR

psql_in() { # DATABASE psql-args...
  local db="$1"
  shift
  "${COMPOSE[@]}" exec -T db psql -U vidafacil -d "$db" -v ON_ERROR_STOP=1 "$@"
}
source_psql() { "${COMPOSE[@]}" exec -T db psql "$SOURCE_URL" -v ON_ERROR_STOP=1 "$@"; }
source_label() { sed -E 's#://([^:@/]+):[^@]*@#://\1:***@#' <<<"$SOURCE_URL"; }

counts() { # command... : one "table count" line per demo table
  local t
  for t in "${TABLES[@]}"; do printf '%s %s\n' "$t" "$("$@" -Atc "select count(*) from public.$t")"; done
}

matches_manifest() { # DATABASE: its row counts equal the manifest's
  diff <(grep -E "^($(IFS='|'; echo "${TABLES[*]}")) " "$MANIFEST") <(counts psql_in "$1") >/dev/null
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

check_source() { # sets SOURCE_HEAD and HEAD
  if ! source_psql -Atc 'select 1' >/dev/null 2>&1; then
    echo "cannot reach the source database $(source_label) from the offline container:" >&2
    echo "start the development stack (make up) or set SOURCE_DATABASE_URL." >&2
    exit 2
  fi
  SOURCE_HEAD="$(source_psql -Atc 'select version_num from alembic_version')"
  HEAD="$(uv run --frozen alembic -c infra/migrations/alembic.ini heads 2>/dev/null | awk '{print $1}')"
  if [[ "$SOURCE_HEAD" != "$HEAD" ]]; then
    echo "source database is at migration $SOURCE_HEAD, this checkout at $HEAD" >&2
    # Only for migrations that do not touch the demo tables (e.g. 0005 only adds a role).
    [[ "${DEMO_OFFLINE_ALLOW_HEAD_MISMATCH:-0}" == "1" ]] || exit 2
    echo "continuing: DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1" >&2
  fi
}

load_staging() { # DUMP: fresh staging database with the schema and the dump's data
  psql_in postgres -q -c "DROP DATABASE IF EXISTS $STAGING" -c "CREATE DATABASE $STAGING"
  psql_in "$STAGING" -q <<SQL
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
ALTER DATABASE $STAGING SET search_path TO public, extensions;
SQL
  uv run --frozen alembic -c infra/migrations/alembic.ini \
    -x url="postgresql+psycopg://vidafacil:vidafacil@localhost:5441/$STAGING" upgrade head >/dev/null 2> >(grep -v "^INFO " >&2 || true)
  gunzip -c "$1" | psql_in "$STAGING" -q >/dev/null
}

promote_staging() { # the validated staging database becomes the one the API reads
  "${COMPOSE[@]}" stop api >/dev/null 2>&1 || true
  psql_in postgres -q -c "DROP DATABASE IF EXISTS $DB WITH (FORCE)" \
    -c "ALTER DATABASE $STAGING RENAME TO $DB"
}

build_web() { # into $WEB_RUN.new; apps/web/.next and NEXT_PUBLIC_* from this shell stay out
  local server app unset_public=()
  rm -rf "$WEB_BUILD" "$WEB_RUN.new"
  mkdir -p "$WEB_BUILD"
  rsync -a --exclude node_modules --exclude .next --exclude 'public/maplibre' --exclude '.env*' \
    apps/web/ "$WEB_BUILD/"
  while read -r name; do unset_public+=(-u "$name"); done < <(compgen -e | grep '^NEXT_PUBLIC_' || true)
  (cd "$WEB_BUILD" && node scripts/copy-maplibre-worker.mjs >/dev/null &&
    env ${unset_public[@]+"${unset_public[@]}"} NEXT_PUBLIC_API_URL="$API_URL" \
      "$ROOT/node_modules/.bin/next" build >/dev/null)
  server="$(find "$WEB_BUILD/.next/standalone" -name server.js -not -path '*/node_modules/*' | head -1)"
  [[ -n "$server" ]] || { echo "the web build produced no standalone server.js" >&2; return 1; }
  app="$(dirname "${server#"$WEB_BUILD/.next/standalone/"}")"
  cp -R "$WEB_BUILD/.next/standalone" "$WEB_RUN.new"
  cp -R "$WEB_BUILD/.next/static" "$WEB_RUN.new/$app/.next/static"
  cp -R "$WEB_BUILD/public" "$WEB_RUN.new/$app/public"
  echo "$app" >"$WEB_RUN.new/.app"
}

prepare() {
  mkdir -p "$OUT"
  echo "-> images (vida-facil-offline) and the offline database on 5441"
  "${COMPOSE[@]}" build
  "${COMPOSE[@]}" up -d --wait db
  check_source

  echo "-> dumping the demo profile from $(source_label) (read only)"
  local table_args=() t
  for t in "${TABLES[@]}"; do table_args+=(--table "public.$t"); done
  "${COMPOSE[@]}" exec -T db pg_dump "$SOURCE_URL" --data-only --disable-triggers --no-owner \
    --no-privileges "${table_args[@]}" 2> >(grep -v -E "circular foreign-key|detail:|hint:" >&2 || true) \
    | gzip -9 >"$DUMP.tmp"
  {
    echo "created_at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "git_commit $(git rev-parse --short HEAD)"
    echo "alembic_head $HEAD (source $SOURCE_HEAD)"
    counts source_psql
  } >"$MANIFEST.tmp"

  echo "-> loading into a staging database (the current package stays until this one validates)"
  load_staging "$DUMP.tmp"
  if ! diff <(grep -E "^($(IFS='|'; echo "${TABLES[*]}")) " "$MANIFEST.tmp") <(counts psql_in "$STAGING"); then
    echo "row counts differ: the source changed during the dump or the load failed; rerun" >&2
    exit 1
  fi

  echo "-> web build from a private copy of apps/web, API at $API_URL"
  build_web

  echo "-> switching to the new package"
  stop_web
  promote_staging
  mv -f "$DUMP.tmp" "$DUMP"
  mv -f "$MANIFEST.tmp" "$MANIFEST"
  rm -rf "$WEB_RUN"
  mv "$WEB_RUN.new" "$WEB_RUN"
  "${COMPOSE[@]}" down
  echo "ready: $(du -h "$DUMP" | cut -f1) dump, manifest $MANIFEST. Start with: make demo-offline"
}

start() {
  [[ -f "$DUMP" && -f "$MANIFEST" ]] ||
    { echo "no offline package: run make demo-offline-prepare first (online)" >&2; exit 2; }
  [[ -f "$WEB_RUN/.app" && -f "$WEB_RUN/$(cat "$WEB_RUN/.app")/server.js" ]] ||
    { echo "no offline web build: run make demo-offline-prepare first (online)" >&2; exit 2; }
  if curl -fs -o /dev/null -m 2 "$WEB_URL"; then
    echo "port $WEB_PORT is already serving something: make demo-offline-stop first" >&2
    exit 2
  fi

  echo "-> database (no network needed)"
  "${COMPOSE[@]}" up -d --wait --no-build db
  if ! matches_manifest "$DB" 2>/dev/null; then
    echo "-> the database volume does not match the package: restoring it from $DUMP"
    load_staging "$DUMP"
    matches_manifest "$STAGING" || { echo "restore failed: counts differ from $MANIFEST" >&2; exit 1; }
    promote_staging
  fi
  echo "-> API"
  "${COMPOSE[@]}" up -d --wait --no-build api

  echo "-> web on $WEB_URL"
  PORT="$WEB_PORT" HOSTNAME=127.0.0.1 nohup node "$WEB_RUN/$(cat "$WEB_RUN/.app")/server.js" \
    >"$WEB_LOG" 2>&1 &
  echo $! >"$WEB_PID"
  wait_for "$WEB_URL" 60
  SMOKE_API_ONLY=1 scripts/smoke_demo.sh "$API_URL"
  echo "offline demo up: $WEB_URL/map  (data: $(head -1 "$MANIFEST"))"
}

stop_web() { # only kills the pid if it is still our Next.js server
  [[ -f "$WEB_PID" ]] || return 0
  local pid command
  pid="$(cat "$WEB_PID")"
  command="$(ps -o command= -p "$pid" 2>/dev/null || true)"
  if [[ "$command" == *next-server* || "$command" == *server.js* ]]; then
    kill "$pid"
  fi
  rm -f "$WEB_PID"
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
