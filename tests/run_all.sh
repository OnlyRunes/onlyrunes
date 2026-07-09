#!/bin/bash
# Run every suite + the audit. Usage: ./tests/run_all.sh
cd "$(dirname "$0")"
python3 ../build.py >/dev/null   # assemble adventure.py from src/ first
fails=0
for t in test_*.py; do
  r=$(python3 "$t" 2>&1 | tail -1)
  case "$r" in
    *"FAILURES: 0"*) echo "ok    $t" ;;
    *) echo "FAIL  $t: $r"; fails=1 ;;
  esac
done
PYTHONPATH=.. python3 audit.py 2>&1 | grep "AUDIT"
exit $fails
