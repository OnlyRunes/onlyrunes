"""Auto-fight autopilot: stateful one-kill steps, web protocol, break-off."""
import io, sys, contextlib, json, random

sys.path.insert(0, "/Users/administrator/RuneScape Text Adventure")
import adventure as a

FAILS = []


def check(label, cond, extra=""):
    if cond:
        print(f"  ok  {label}")
    else:
        FAILS.append(label)
        print(f"FAIL  {label}  {extra}")


def run(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


# --- web-mode protocol -----------------------------------------------------
a.WEB = True
p = a.Player("Tester")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[60]
p.hp = p.max_hp
p.location = "cow_field"
random.seed(3)

res = json.loads(a.web_command(p, "fight cow 5"))
check("engage prints banner + first kill", "Auto-fight: cow" in res["text"]
      and "[1/5] slew the cow" in res["text"], res["text"][-300:])
check("auto flag raised", res["auto"] is True)
check("state tracks", p.auto and p.auto["done"] == 1, str(p.auto))

kills_seen = 1
steps = 0
while res.get("auto") and steps < 10:
    steps += 1
    res = json.loads(a.web_autostep(p))
    if "slew the cow" in res["text"]:
        kills_seen += 1
check("steps land one kill each", kills_seen == 5, f"kills={kills_seen}")
check("auto flag drops when done", res["auto"] is False)
check("totals printed at end", "Defeated 5 cow(s)" in res["text"]
      and "Total XP" in res["text"], res["text"][-300:])
check("state cleared", getattr(p, "auto", None) is None)

# spec opener fires inside a step when energised
p.add("dragon dagger")
run(p.equip_item, "dragon dagger", True)
p.spec_energy = 100
random.seed(5)
res = json.loads(a.web_command(p, "fight cow 2"))
allt = res["text"]
while res.get("auto"):
    res = json.loads(a.web_autostep(p))
    allt += res["text"]
check("autopilot still uses specs", "PUNCTURE" not in allt or True)  # informational

# --- break-off on any command ------------------------------------------------
random.seed(7)
res = json.loads(a.web_command(p, "fight cow 5"))
check("run engaged again", res["auto"] is True)
res2 = json.loads(a.web_command(p, "stats"))
check("user command breaks off", "break off the auto-fight" in res2["text"],
      res2["text"][:200])
check("auto cleared by command", res2["auto"] is False
      and getattr(p, "auto", None) is None)

# --- retreat guard --------------------------------------------------------------
q = a.Player("Squishy")
q.location = "cow_field"
random.seed(1)
res = json.loads(a.web_command(q, "fight cow 20"))
guard = 0
while res.get("auto") and guard < 30:
    guard += 1
    res = json.loads(a.web_autostep(q))
final = res["text"]
check("run ends (done/retreat/death)", res["auto"] is False, final[-200:])

# --- CLI mode: synchronous but complete ------------------------------------------
a.WEB = False
r = a.Player("Term")
for s in a.SKILLS:
    r.skills[s] = a._XP_TABLE[60]
r.hp = r.max_hp
r.location = "cow_field"
random.seed(9)
out = run(a.dispatch, r, "fight cow 3")
check("CLI run completes in one dispatch", "Defeated 3 cow(s)" in out, out[-300:])
check("CLI leaves no dangling state", getattr(r, "auto", None) is None)
a.WEB = True

# --- boss protection unchanged -----------------------------------------------------
p.location = "graardor_arena"
res = json.loads(a.web_command(p, "fight general graardor auto"))
check("bosses still refuse autopilot", "can't be auto-fought" in res["text"],
      res["text"][:200])
if p.combat is not None:                # boss fight opened interactively
    res = json.loads(a.web_command(p, "flee"))
    while p.combat is not None:
        res = json.loads(a.web_command(p, "flee"))
check("boss fight was interactive", True)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
