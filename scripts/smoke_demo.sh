#!/usr/bin/env bash
# Smoke test of the public demo: web, API liveness and readiness, one zone, the map layers, one
# search (POST /api/v1/search with the demo case, which also warms up the search before a pitch) and
# the same case barrio by barrio in one Madrid district (POST /api/v1/search/barrios).
#   scripts/smoke_demo.sh [BASE_URL]                       # default https://vidafacil-madrid.vercel.app
#   SMOKE_API_ONLY=1 scripts/smoke_demo.sh http://localhost:8012   # API container, no web
#   SMOKE_TAG=<id> scripts/smoke_demo.sh   # User-Agent vida-facil-smoke/<id>, to find the requests
#                                          # in `vercel logs requests` (infra/deploy/deploy.sh)
# Exits 0 only if every check passes. Needs curl and jq. Prints no secrets.
set -euo pipefail
export LC_ALL=C
for tool in curl jq; do
  command -v "$tool" >/dev/null || { echo "smoke: $tool is required" >&2; exit 2; }
done

BASE="${1:-${SMOKE_BASE_URL:-https://vidafacil-madrid.vercel.app}}"
BASE="${BASE%/}"
ZONE="${SMOKE_ZONE:-municipio/28079}"   # Madrid
LAYER="${SMOKE_LAYER:-education}"
TIMEOUT="${SMOKE_TIMEOUT:-60}"          # the first request after idle may cold start
MAX_BYTES=4500000                       # Vercel Functions response body limit (4.5 MB)
SEARCH_MAX_BYTES=1000000                # a search answer is about 110 KB; over 1 MB means something broke
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SEARCH_BODY="${SMOKE_SEARCH_BODY:-$ROOT/data/fixtures/contracts/scenario_state.familia_castellana.fixture.json}"
[[ -f "$SEARCH_BODY" ]] || { echo "smoke: search body not found (SMOKE_SEARCH_BODY)" >&2; exit 2; }
TAG="${SMOKE_TAG:-}"
if [[ -n "$TAG" && ! "$TAG" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "smoke: SMOKE_TAG may only contain letters, digits, '.', '_' and '-'" >&2
  exit 2
fi
USER_AGENT="vida-facil-smoke${TAG:+/$TAG}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
total=0
failures=0

# check NAME PATH JQ_FILTER [JSON_BODY_FILE] [MAX]: HTTP 200 (a POST of the file when given), body
# under MAX bytes (default MAX_BYTES) and, if given, a jq filter that prints a summary (no output or
# false means the body is wrong).
check() {
  local name="$1" path="$2" filter="$3" body="${4:-}" max="${5:-$MAX_BYTES}" code secs bytes detail="" ok=1
  local post=()
  [[ -n "$body" ]] && post=(-X POST -H "Content-Type: application/json" --data-binary "@$body")
  read -r code secs bytes < <(curl -sS -o "$TMP/$name" --max-time "$TIMEOUT" -A "$USER_AGENT" \
    ${post[@]+"${post[@]}"} -w '%{http_code} %{time_total} %{size_download}\n' "$BASE$path" 2>/dev/null ||
    echo "000 0 0")
  if [[ "$code" != "200" ]]; then
    ok=0 detail="HTTP $code"
  elif ((bytes > max)); then
    ok=0 detail="body over $max B"
  elif [[ -n "$filter" ]] && ! detail="$(jq -er "$filter" "$TMP/$name" 2>/dev/null)"; then
    ok=0 detail="unexpected body"
  fi
  total=$((total + 1))
  ((ok)) || failures=$((failures + 1))
  printf '%-4s %-9s %6.2fs %9s B  %s  %s\n' \
    "$( ((ok)) && echo OK || echo FAIL)" "$name" "$secs" "$bytes" "$path" "$detail"
}

echo "smoke: $BASE ($(date -u +%Y-%m-%dT%H:%M:%SZ))${TAG:+ tag $TAG}"
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
# The largest layer, paginated since 879101a: page 1 is the biggest single response the map asks
# for, so this guards the 4.5 MB limit per page (not the size of the whole layer).
check largest "/api/v1/places?category=transport" \
  'select(.data.page == 1 and .data.pages >= 1 and (.data.features | length) > 0
          and .data.total >= (.data.features | length))
   | "\(.data.total) stops, page \(.data.page)/\(.data.pages)"'
# The demo case of the pitch: at least one zone passes. Its figures are read on screen, never here.
check search "/api/v1/search" \
  'select(.data.reality_check.zones_passing >= 1
          and (.data.results[0].match_pct | type == "number" and . >= 0 and . <= 100))
   | "\(.data.reality_check.zones_passing) of \(.data.reality_check.zones_evaluated) zones, 1st \(.data.results[0].zone.name)"' \
  "$SEARCH_BODY" "$SEARCH_MAX_BYTES"
# The same case, barrio by barrio inside one Madrid district (BARRIO-001, D-232): at least one passes.
BARRIO_DISTRICT="${SMOKE_BARRIO_DISTRICT:-2807920}"   # San Blas-Canillejas
jq --arg d "$BARRIO_DISTRICT" '{scenario: ., distrito: $d}' "$SEARCH_BODY" >"$TMP/barrios-body.json"
check barrios "/api/v1/search/barrios" \
  'select(.data.reality_check.zones_passing >= 1 and .data.results[0].zone.level == "barrio"
          and (.data.results[0].match_pct | type == "number" and . >= 0 and . <= 100))
   | "\(.data.reality_check.zones_passing) of \(.data.reality_check.zones_evaluated) barrios, 1st \(.data.results[0].zone.name)"' \
  "$TMP/barrios-body.json" "$SEARCH_MAX_BYTES"

echo "smoke: $((total - failures))/$total OK"
((failures == 0))
