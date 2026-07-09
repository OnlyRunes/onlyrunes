#!/usr/bin/env bash
# Build the deployable static site.
# 1) assemble adventure.py from the src/ fragments, 2) copy it into site/.
# Run this whenever anything in src/ changes, then deploy the site/ folder.
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py                       # src/*.py -> adventure.py
cp adventure.py site/adventure.py
echo "Copied adventure.py -> site/adventure.py"
echo "Deployable folder is ready: ./site"
echo
echo "Preview locally:   (cd site && python3 -m http.server 8000)  then open http://localhost:8000"
echo "Deploy:            see DEPLOY.md"
