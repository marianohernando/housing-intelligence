#!/usr/bin/env bash
# One-command production deploy of the demo (web + API, one Vercel project), then a smoke test
# whose requests must all be served by the new deployment.
#   make deploy-demo        (or infra/deploy/deploy.sh)
#   ALLOW_BRANCH=1 make deploy-demo   # deploy from a branch other than the demo's (on purpose)
# Needs: Node/npx, jq, a Vercel CLI login with access to the project, and this checkout linked once
# with `npx vercel@<VERCEL_CLI_VERSION> link --project vida-facil`. Secrets live only in Vercel.
# Exit codes: 0 deployed and verified · 1 deploy or smoke failed · 2 refused before deploying ·
#             3 deployed but not verified: no deployment id, or the smoke passed without every
#               request of it coming from the new deployment.
set -euo pipefail

VERCEL_CLI_VERSION="65.12.1"   # pinned: 54.x does not understand "services" in vercel.json
DEMO_URL="${DEMO_URL:-https://vidafacil-madrid.vercel.app}"
DEMO_BRANCHES=("claude/sprint-1-public" "main")   # integration branch, then main after the merge
SMOKE_REPEATS=3   # after the first smoke, at most 3 more, 20 s apart
LOG_WAIT_S=60     # vercel logs shows a request 10-20 s after it is served
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

vercel() { npx --yes "vercel@${VERCEL_CLI_VERSION}" "$@"; }

# The CLI prints dashboard and deployment URLs that carry the Vercel team slug, which has
# Mariano's surname: mask them, so this output can go into evidence as it is (LINEAS.md).
mask_urls() {
  awk '{ gsub(/https:\/\/vercel\.com\/[^ \t"]*/, "<panel de Vercel>")
         gsub(/https:\/\/vida-facil-[a-z0-9]+-[a-z0-9-]+\.vercel\.app/, "<despliegue>")
         print; fflush() }'
}

command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }
if [[ ! -f .vercel/project.json ]]; then
  echo "not linked: npx vercel@${VERCEL_CLI_VERSION} link --project vida-facil" >&2
  exit 2
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "uncommitted or untracked files: deploy a committed state (git status)" >&2
  exit 2
fi

branch="$(git branch --show-current)"
if [[ ! " ${DEMO_BRANCHES[*]} " == *" ${branch} "* ]]; then
  if [[ "${ALLOW_BRANCH:-0}" != "1" ]]; then
    echo "branch '${branch}' is not a demo branch (${DEMO_BRANCHES[*]}); ALLOW_BRANCH=1 to force" >&2
    exit 2
  fi
  echo "warning: deploying branch '${branch}' (ALLOW_BRANCH=1)" >&2
fi
if [[ "$(git rev-parse HEAD)" != "$(git rev-parse '@{u}' 2>/dev/null || true)" ]]; then
  echo "warning: HEAD is not the pushed upstream; the demo will not match the remote branch" >&2
fi

# Local secrets and databases that .vercelignore keeps out of the upload: say so, never send them.
ignored="$({
  find . -maxdepth 1 -type f -name '.env*' ! -name '.env.example'
  find apps packages services infra \( -name node_modules -o -name .next -o -name .venv \) -prune \
    -o -type f \( -name '.env*' -o -name '*.pem' -o -name '*.key' -o -name '*.db' -o -name '*.sqlite' \) \
    ! -name '.env.example' -print
} | sort)"
if [[ -n "$ignored" ]]; then
  echo "note: these local files match .vercelignore and are NOT uploaded:" >&2
  sed 's/^/  /' <<<"$ignored" >&2
fi

echo "-> deploying $(git rev-parse --short HEAD) (${branch}) to production"
# stdout (JSON) to a file; the CLI's progress on stderr shown masked, and kept to find the id
if ! vercel deploy --prod --yes --json 2>&1 >"$TMP/deploy.json" | tee "$TMP/deploy.err" | mask_urls >&2; then
  mask_urls <"$TMP/deploy.json" >&2
  failed="$(grep -oE 'vercel\.com/[^/ ]+/vida-facil/[A-Za-z0-9]+' "$TMP/deploy.err" | tail -1 | sed 's#.*/#dpl_#')"
  echo "deploy failed; production is unchanged." >&2
  echo "build logs: npx vercel@${VERCEL_CLI_VERSION} inspect ${failed:-<dpl_id>} --logs" >&2
  exit 1
fi
deployment="$(jq -r '.deployment.id // empty' "$TMP/deploy.json")"
if [[ ! "$deployment" =~ ^dpl_[A-Za-z0-9]+$ ]]; then
  echo "deployed, but the CLI output carries no deployment id: check npx vercel@${VERCEL_CLI_VERSION} ls" >&2
  exit 3
fi
echo "-> deployment ${deployment} is ready"

# smoke TAG: the smoke against the public domain, its requests tagged in their User-Agent.
smoke() {
  echo "-> smoke test against ${DEMO_URL}"
  SMOKE_TAG="$1" scripts/smoke_demo.sh "$DEMO_URL" | tee "$TMP/smoke"
}

# fetch_requests TAG: the CDN records of that smoke, from vercel logs (secrets never in them).
fetch_requests() {
  vercel logs requests --environment production --since 10m --limit 1000 --json \
    --query "clientUserAgent:\"vida-facil-smoke/$1\"" >"$TMP/requests" 2>/dev/null
}

# served_by_this_deployment TAG: every request of that smoke shows up in vercel logs, served by
# the new deployment. Right after the domain switch the previous deployment keeps answering part
# of the traffic for about 10 s: on 11 Nov it gave one 500, and later 4 of 7 requests of a
# passing smoke. So a green smoke alone does not prove the new deployment.
served_by_this_deployment() {
  local expected found=0 ours waited=0
  expected="$(sed -n 's#^smoke: [0-9]*/\([0-9]*\) OK$#\1#p' "$TMP/smoke")"
  [[ "$expected" =~ ^[1-9][0-9]*$ ]] || { echo "-> cannot read the smoke's request count" >&2; return 1; }
  while ((found < expected && waited < LOG_WAIT_S)); do
    sleep 5
    waited=$((waited + 5))
    if fetch_requests "$1"; then
      found="$(jq -s '[.[] | select(.type == "request")] | length' "$TMP/requests")"
    fi
  done
  if ((found < expected)); then
    echo "-> only ${found}/${expected} smoke requests in vercel logs after ${LOG_WAIT_S} s" >&2
    return 1
  fi
  ours="$(jq -s --arg id "$deployment" \
    '[.[] | select(.type == "request" and .data.deploymentId == $id)] | length' "$TMP/requests")"
  jq -rs --arg id "$deployment" '[.[] | select(.type == "request") | .data.deploymentId]
    | group_by(.) | map("   \(length) from \(.[0])\(if .[0] == $id then " (this deploy)" else
      " (another deployment)" end)") | .[]' "$TMP/requests"
  ((ours == found))
}

# Each round: a smoke, then which deployment served it. A real failure fails every round.
outcome=""
for ((round = 0; round <= SMOKE_REPEATS; round++)); do
  if ((round > 0)); then
    echo "-> ${outcome}; repeating the smoke in 20 s (${round}/${SMOKE_REPEATS})" >&2
    sleep 20
  fi
  tag="${deployment}-${round}"
  if ! smoke "$tag"; then
    outcome="smoke failed"
    continue
  fi
  echo "-> which deployment served the smoke (vercel logs requests, tag ${tag})"
  if served_by_this_deployment "$tag"; then
    echo "-> verified: ${DEMO_URL} serves ${deployment}, and the smoke passed against it"
    exit 0
  fi
  outcome="the smoke did not come entirely from ${deployment}"
done

if [[ "$outcome" == "smoke failed" ]]; then
  echo "smoke failed and production already serves this deploy." >&2
  echo "roll back to the previous one: npx vercel@${VERCEL_CLI_VERSION} rollback" >&2
  exit 1
fi
echo "NOT VERIFIED: the smoke passes, but after ${SMOKE_REPEATS} repeats not all of its requests" >&2
echo "came from ${deployment}. Do not present from this state. Inspect with:" >&2
echo "  npx vercel@${VERCEL_CLI_VERSION} logs requests --environment production --since 10m" >&2
exit 3
