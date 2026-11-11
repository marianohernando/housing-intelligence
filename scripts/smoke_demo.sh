#!/usr/bin/env bash
# Smoke test of the public demo: web, API liveness and readiness, one zone and one map layer.
#   scripts/smoke_demo.sh [BASE_URL]                       # default https://vida-facil-eight.vercel.app
#   SMOKE_API_ONLY=1 scripts/smoke_demo.sh http://localhost:8012   # API container, no web
# Exits 0 only if every check passes. Needs curl and jq. Prints no secrets.
set -euo pipefail
export LC_ALL=C

BASE="${1:-${SMOKE_BASE_URL:-https://vida-facil-eight.vercel.app}}"
BASE="${BASE%/}"
ZONE="${SMOKE_ZONE:-municipio/28079}"   # Madrid
LAYER="${SMOKE_LAYER:-education}"
TIMEOUT="${SMOKE_TIMEOUT:-60}"          # the first request after idle may cold start
MAX_BYTES=4500000                       # Vercel Functions response body limit (4.5 MB)

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
total=0
failures=0

# check NAME PATH JQ_FILTER: HTTP 200, body under MAX_BYTES and, if given, a jq filter that
# prints a summary (no output or false means the body is wrong).
check() {
  local name="$1" path="$2" filter="$3" code secs bytes detail="" ok=1
  read -r code secs bytes < <(curl -sS -o "$TMP/$name" --max-time "$TIMEOUT" \
    -w '%{http_code} %{time_total} %{size_download}\n' "$BASE$path" 2>/dev/null || echo "000 0 0")
  if [[ "$code" != "200" ]]; then
    ok=0 detail="HTTP $code"
  elif ((bytes > MAX_BYTES)); then
    ok=0 detail="body over 4.5 MB"
  elif [[ -n "$filter" ]] && ! detail="$(jq -er "$filter" "$TMP/$name" 2>/dev/null)"; then
    ok=0 detail="unexpected body"
  fi
  total=$((total + 1))
  ((ok)) || failures=$((failures + 1))
  printf '%-4s %-9s %6.2fs %9s B  %s  %s\n' \
    "$( ((ok)) && echo OK || echo FAIL)" "$name" "$secs" "$bytes" "$path" "$detail"
}

echo "smoke: $BASE ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
if [[ "${SMOKE_API_ONLY:-0}" != "1" ]]; then
  check web "/" ""
fi
check health "/api/v1/health" 'select(.data.status == "ok") | "process up"'
check ready "/api/v1/health/ready" 'select(.data.status == "ok") | "database and geography visible"'
check zone "/api/v1/gaps/$ZONE" \
  'select((.data.rows | length) > 0) | "\(.data.zone.name): \(.data.rows | length) rows"'
check geography "/api/v1/geo/admin-units?level=municipio&simplify_m=50" \
  'select((.data.features | length) > 0) | "\(.data.features | length) municipios"'
check layer "/api/v1/places?category=$LAYER" \
  'select((.data.features | length) > 0) | "\(.data.features | length) places"'

echo "smoke: $((total - failures))/$total OK"
((failures == 0))
