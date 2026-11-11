#!/usr/bin/env bash
# One-command production deploy of the demo (web + API, one Vercel project), then smoke test.
#   make deploy-demo        (or infra/deploy/deploy.sh)
# Needs: Node/npx, a Vercel CLI login with access to the project, and this checkout linked once
# with `npx vercel@<VERCEL_CLI_VERSION> link --project vida-facil`. Secrets live only in Vercel.
set -euo pipefail

VERCEL_CLI_VERSION="65.12.1"   # pinned: 54.x does not understand "services" in vercel.json
DEMO_URL="${DEMO_URL:-https://vida-facil-eight.vercel.app}"
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

if [[ "$(git rev-parse HEAD)" != "$(git rev-parse '@{u}' 2>/dev/null || true)" ]]; then
  echo "warning: HEAD is not the pushed upstream; the demo will not match the PR" >&2
fi

echo "-> deploying $(git rev-parse --short HEAD) ($(git branch --show-current)) to production"
vercel deploy --prod --yes
echo "-> smoke test against ${DEMO_URL}"
if ! scripts/smoke_demo.sh "${DEMO_URL}"; then
  echo "smoke failed and production already serves this deploy." >&2
  echo "roll back to the previous one: npx vercel@${VERCEL_CLI_VERSION} rollback" >&2
  exit 1
fi
