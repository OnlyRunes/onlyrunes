#!/usr/bin/env bash
# Ship an update.  Usage:
#   ./deploy.sh         -> PRODUCTION (live)  https://onlyrunes.net
#   ./deploy.sh beta    -> BETA  (staging)    https://beta.onlyrunes.net
#
# First time only:  npx --yes wrangler login   (browser approval)
# Note: normally you don't need this — pushing to GitHub auto-deploys
#       (main -> live, beta -> beta). This is the manual fallback.
set -euo pipefail
cd "$(dirname "$0")"

if [ "${1:-}" = "beta" ]; then
  ENVFLAG="--env beta"; TARGET="BETA (beta.onlyrunes.net)"
else
  ENVFLAG=""; TARGET="PRODUCTION (onlyrunes.net)"
fi

./build_site.sh
echo
echo "Deploying to $TARGET ..."
npx --yes wrangler@latest deploy $ENVFLAG
echo
echo "Done."
