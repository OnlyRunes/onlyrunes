#!/usr/bin/env bash
# One command to ship an update:
#   1. copies the latest adventure.py into site/
#   2. deploys site/ to the "onlyrunes" Cloudflare Worker
#
# First time only:  npx --yes wrangler login   (browser approval)
# Then any time:    ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

./build_site.sh
echo
echo "Deploying to Cloudflare..."
npx --yes wrangler@latest deploy
echo
echo "Done. Live at https://onlyrunes.net (hard-refresh to bypass cache)."
