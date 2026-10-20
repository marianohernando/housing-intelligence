#!/usr/bin/env bash
# Runs once on first boot. Creates extensions in schema `extensions` (Supabase convention)
# for the main database and a sibling `<db>_test` database used by integration tests.
set -euo pipefail

setup_db() {
  local db="$1"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" <<SQL
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
ALTER DATABASE "$db" SET search_path TO public, extensions;
SQL
}

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -c "CREATE DATABASE \"${POSTGRES_DB}_test\" OWNER \"$POSTGRES_USER\";"

setup_db "$POSTGRES_DB"
setup_db "${POSTGRES_DB}_test"
