"""Skilling expansion 3: high RC altars, wilderness agility, slayer rewards."""
import io, sys, contextlib, random

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


p = a.Player("Tester")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[80]
p.hp = p.max_hp
p.members = True

# --- high RC altars -----------------------------------------------------------
for hub, ex, rune in [("brimhaven", "altar", "nature rune"),
                      ("catherby", "islet", "law rune")]:
    p.location = hub
    p.add("rune essence", 10)
    run(a.cmd_go, p, ex)
    run(a.cmd_craftrune, p, "")
    check(f"{rune} craftable", p.has(rune))
p.location = "chaos_temple"
p.add("rune essence", 5)
run(a.cmd_craftrune, p, "")
check("chaos runes at chaos temple", p.has("chaos rune"))
q = a.Player("Fresh")
q.members = True
q.location = "paterdomus"
out = run(a.cmd_go, q, "crypt")
check("death altar locked pre-quest", q.location == "paterdomus", out)
p.quests["priest_in_peril"] = "complete"
p.location = "paterdomus"
run(a.cmd_go, p, "crypt")
check("death altar open post-quest", p.location == "death_altar")
p.add("rune essence", 5)
run(a.cmd_craftrune, p, "")
check("death runes craftable", p.has("death rune"))

# --- wilderness agility ---------------------------------------------------------
p.location = "deep_wilderness"
run(a.cmd_go, p, "course")
check("wildy course reachable", p.location == "wilderness_course")
xp0 = p.skills["agility"]
random.seed(2)
run(a.cmd_agility, p, "")
check("wildy lap grants big xp", p.skills["agility"] - xp0 >= 48)
q.location = "wilderness_course"
q.skills["agility"] = a._XP_TABLE[10]
out = run(a.cmd_agility, q, "")
check("wildy course gated at 52", "level 52" in out, out)
p.location = "agility_course"
out = run(a.cmd_agility, p, "")
check("barbarian course still runs",
      "lap" in out.lower() or "slip" in out.lower(), out)

# --- slayer rewards ----------------------------------------------------------------
p.location = "edgeville"
p.slayer_points = 100
out = run(a.cmd_slayerbuy, p, "")
check("rewards list shows", "slayer helmet" in out, out)
run(a.cmd_slayerbuy, p, "helmet")
check("helmet bought", p.has("slayer helmet") and p.slayer_points == 40)
xp0 = p.skills["slayer"]
run(a.cmd_slayerbuy, p, "tome")
check("tome grants xp",
      p.skills["slayer"] - xp0 == 2500 * a.XP_RATE)
p.slayer_task = {"monster": "cow", "amount": 10, "remaining": 10}
run(a.cmd_slayerbuy, p, "skip")
check("skip clears task", p.slayer_task is None)
out = run(a.cmd_slayerbuy, p, "helmet")
check("insufficient points refused", "need 60" in out, out)

# helmet on-task bonus (max-hit comparison over identical seeds)
run(p.equip_item, "slayer helmet", True)
m = a._new_monster("cow")


def max_hit_sample(task):
    p.slayer_task = task
    random.seed(0)
    best = 0
    for _ in range(300):
        m["cur"] = m["hp"]
        buf = run(a._resolve_player_hit, p, m)
        if "for" in buf and "glances" not in buf:
            try:
                best = max(best, int(buf.split("for ")[1].split("!")[0]))
            except Exception:
                pass
    return best


on = max_hit_sample({"monster": "cow", "amount": 10, "remaining": 10})
off = max_hit_sample(None)
check("helmet boosts on-task max hit", on > off, f"{on} vs {off}")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
