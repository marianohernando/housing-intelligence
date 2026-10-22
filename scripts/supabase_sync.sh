#!/usr/bin/env bash
# Copy validated Silver/Gold tables from the local Docker DB to the remote (Supabase) DB.
# Schema must already be migrated remotely (make supabase-migrate). Target tables are truncated.
# Usage: SUPABASE_DATABASE_URL=... scripts/supabase_sync.sh [demo|full]
set -euo pipefail

PROFILE="${1:-demo}"
REMOTE="${SUPABASE_DATABASE_URL:?SUPABASE_DATABASE_URL is required}"
REMOTE="${REMOTE/postgresql+psycopg:/postgresql:}"   # libpq URL for pg_dump/psql

BASE=(source_registry dataset_registry dataset_version metric_registry feature_registry geo_admin_unit place_master place_source_alias feature_value)
FULL_EXTRA=(h3_cell h3_cell_admin_unit metric_observation)
case "$PROFILE" in
  demo) TABLES=("${BASE[@]}") ;;
  full) TABLES=("${BASE[@]}" "${FULL_EXTRA[@]}") ;;
  *) echo "profile must be demo or full" >&2; exit 2 ;;
esac

LOCAL_USER="${POSTGRES_USER:-housing}"
LOCAL_DB="${POSTGRES_DB:-housing}"
TABLE_ARGS=()
for t in "${TABLES[@]}"; do TABLE_ARGS+=(--table "public.$t"); done
TRUNCATE="TRUNCATE $(IFS=,; echo "${TABLES[*]}") CASCADE;"

echo "-> truncating ${#TABLES[@]} remote tables ($PROFILE)"
docker compose exec -T db psql "$REMOTE" -v ON_ERROR_STOP=1 -q -c "$TRUNCATE"
echo "-> copying"
# No --disable-triggers: Supabase's postgres role is not a superuser. pg_dump orders tables by
# foreign keys and the self-referencing geo_admin_unit rows are checked at the end of its COPY.
docker compose exec -T db pg_dump -U "$LOCAL_USER" -d "$LOCAL_DB" --data-only --no-owner --no-privileges \
  "${TABLE_ARGS[@]}" 2> >(grep -v -E "circular foreign-key|detail: geo_admin_unit|hint:" >&2) \
  | docker compose exec -T db psql "$REMOTE" -v ON_ERROR_STOP=1 -q
echo "-> row counts (remote)"
for t in "${TABLES[@]}"; do
  printf "%-22s %s\n" "$t" "$(docker compose exec -T db psql "$REMOTE" -Atc "select count(*) from public.$t")"
done
docker compose exec -T db psql "$REMOTE" -Atc "select 'database size: ' || pg_size_pretty(pg_database_size(current_database()))"
