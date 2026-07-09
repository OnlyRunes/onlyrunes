#!/usr/bin/env python3
"""Concatenate the ordered source fragments in src/ into adventure.py.

The game ships and runs as a single module (the browser fetches one
adventure.py into Pyodide), but the source is split into system-named
fragments under src/ for navigability. Fragment order is the 2-digit
numeric filename prefix — it is load-bearing, since the content blocks
mutate shared tables (ROOMS, MONSTERS, HANDLERS, ...) in order.

Edit files in src/, then run `python3 build.py` (build_site.sh does this
for you). Do NOT hand-edit adventure.py — it is generated.
"""
import glob
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "adventure.py")


def build():
    frags = sorted(glob.glob(os.path.join(SRC, "*.py")))
    if not frags:
        raise SystemExit("no fragments in src/ — nothing to build")
    parts = []
    for path in frags:
        with open(path) as f:
            parts.append(f.read())
    code = "".join(parts)
    with open(OUT, "w") as f:
        f.write(code)
    return frags, code.count("\n")


if __name__ == "__main__":
    frags, nlines = build()
    print(f"Built adventure.py from {len(frags)} fragments "
          f"({nlines:,} lines).")
