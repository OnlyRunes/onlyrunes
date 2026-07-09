"""Build integrity: adventure.py is generated from the src/ fragments.
This guards against hand-edits to adventure.py and against committing a
stale build (edit src/, forget to run build.py)."""
import sys, os, glob, ast

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "adventure.py")

FAILS = []


def check(label, cond, extra=""):
    if cond:
        print(f"  ok  {label}")
    else:
        FAILS.append(label)
        print(f"FAIL  {label}  {extra}")


frags = sorted(glob.glob(os.path.join(SRC, "*.py")))
check("src/ has fragments", len(frags) >= 10, str(len(frags)))

# every fragment is individually parseable? NO — fragments are not standalone
# modules (they share one namespace). Only the concatenation must parse.
concat = "".join(open(p).read() for p in frags)
try:
    ast.parse(concat)
    parses = True
except SyntaxError as e:
    parses = False
    print("   concat SyntaxError:", e)
check("concatenated fragments parse", parses)

with open(OUT) as f:
    built = f.read()
check("adventure.py matches src/ (run build.py if this fails)",
      built == concat,
      "adventure.py is stale or hand-edited — run: python3 build.py")

check("generated banner present",
      "GENERATED FILE" in "\n".join(built.splitlines()[:6]))
check("shebang is still line 1", built.startswith("#!/usr/bin/env python3"))

# fragment prefixes are unique and zero-padded (so sort == load order)
names = [os.path.basename(p) for p in frags]
prefixes = [n[:2] for n in names]
check("fragment prefixes unique", len(set(prefixes)) == len(prefixes),
      str([p for p in prefixes if prefixes.count(p) > 1]))
check("fragments numerically ordered", names == sorted(names))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
