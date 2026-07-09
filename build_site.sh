#!/usr/bin/env bash
# Build the deployable static site.
# 1) assemble adventure.py from the src/ fragments, 2) copy it into site/.
# Run this whenever anything in src/ changes, then deploy the site/ folder.
set -euo pipefail
cd "$(dirname "$0")"

# Assemble adventure.py from src/ fragments. The committed adventure.py is
# always kept in sync, so if python3 isn't available (some CI images) we
# fall back to it rather than failing the deploy.
if command -v python3 >/dev/null 2>&1; then
  python3 build.py
else
  echo "python3 not found — using the committed adventure.py as-is"
fi
cp adventure.py site/adventure.py
echo "Copied adventure.py -> site/adventure.py"
echo "Deployable folder is ready: ./site"
echo
echo "Preview locally:   (cd site && python3 -m http.server 8000)  then open http://localhost:8000"
echo "Deploy:            see DEPLOY.md"
