#!/usr/bin/env bash
# One-command production deploy of the demo (web + API, one Vercel project), then smoke test.
#   make deploy-demo        (or infra/deploy/deploy.sh)
#   ALLOW_BRANCH=1 make deploy-demo   # deploy from a branch other than the demo's (on purpose)
# Needs: Node/npx, a Vercel CLI login with access to the project, and this checkout linked once
# with `npx vercel@<VERCEL_CLI_VERSION> link --project vida-facil`. Secrets live only in Vercel.
set -euo pipefail

VERCEL_CLI_VERSION="65.12.1"   # pinned: 54.x does not understand "services" in vercel.json
DEMO_URL="${DEMO_URL:-https://vidafacil-madrid.vercel.app}"
DEMO_BRANCHES=("claude/sprint-1-public" "main")   # integration branch, then main after the merge
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

vercel() { npx --yes "vercel@${VERCEL_CLI_VERSION}" "$@"; }

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
vercel deploy --prod --yes
echo "-> smoke test against ${DEMO_URL}"
if ! scripts/smoke_demo.sh "${DEMO_URL}"; then
  # Right after the domain switch the previous deployment can still answer for a few seconds
  # (seen on 11 Nov: one 500 from the old instance, then 6/6). A real failure fails twice.
  echo "-> smoke failed right after the switch; retrying once in 20 s" >&2
  sleep 20
  if ! scripts/smoke_demo.sh "${DEMO_URL}"; then
    echo "smoke failed and production already serves this deploy." >&2
    echo "roll back to the previous one: npx vercel@${VERCEL_CLI_VERSION} rollback" >&2
    exit 1
  fi
fi
