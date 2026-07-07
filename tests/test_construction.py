"""Construction — the 22nd skill: sawmill, house, furniture perks, home tp."""
import io, sys, contextlib

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


check("construction registered", "construction" in a.SKILLS
      and len(a.SKILLS) >= 22)
check("construction cape", "construction cape" in a.ITEMS)

p = a.Player("Tester")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[70]
p.hp = p.max_hp

# --- sawmill ---------------------------------------------------------------
p.location = "grand_exchange"
run(a.cmd_go, p, "mill")
check("sawmill reachable", p.location == "sawmill")
p.add("logs", 6); p.add("oak logs", 25); p.add("coins", 3000)
out = run(a.dispatch, p, "saw logs 6")
check("batch sawing planks", p.count("plank") == 6, out)
run(a.dispatch, p, "saw oak logs 25")
check("oak planks sawn", p.count("oak plank") >= 21)
coins_after = p.count("coins")
check("sawmill charges", coins_after < 3000 + 25)

# --- house + build -----------------------------------------------------------
p.location = "rimmington"
run(a.cmd_go, p, "house")
check("house reachable", p.location == "your_house")
out = run(a.cmd_build, p, "")
check("build menu lists perks", "portal chamber" in out and "oak bed" in out, out)
while p.has("hammer"):
    p.take("hammer")                      # starter kit includes one
out = run(a.cmd_build, p, "crude chair")
check("build needs hammer", "You need a hammer" in out, out)
p.add("hammer")
xp0 = p.skills["construction"]
run(a.cmd_build, p, "crude chair")
check("chair built + xp", "crude chair" in p.house
      and p.skills["construction"] > xp0)
out = run(a.cmd_build, p, "crude chair")
check("no duplicate builds", "already built" in out, out)

p.add("steel bar", 2); p.add("gold bar", 2); p.add("law rune", 25)
for f in ("oak bed", "workbench", "kitchen range", "chapel altar",
          "portal chamber"):
    run(a.cmd_build, p, f)
check("all furniture built", len(p.house) == len(a.FURNITURE), str(p.house))

# --- perks --------------------------------------------------------------------
p.hp = 5
p.prayer_points = 1
out = run(a.cmd_rest, p, "")
check("home bed full rest incl prayer", p.hp == p.max_hp
      and p.prayer_points == p.prayer_max(), out)
p.add("raw trout")
out = run(a.cmd_cook, p, "raw trout")
check("cook at home", not p.has("raw trout"), out)
p.add("bronze bar")
out = run(a.cmd_smith, p, "bronze dagger")
check("smith at home workbench", p.has("bronze dagger"), out)
p.prayer_points = 0
run(a.cmd_pray, p, "altar")
check("pray at home altar", p.prayer_points == p.prayer_max())
out = run(a.cmd_home, p, "")
check("already home msg", "already home" in out, out)
p.location = "canifis"
out = run(a.cmd_home, p, "")
check("home teleport works", p.location == "your_house", out)

# --- gates + persistence ---------------------------------------------------------
q = a.Player("F2P")
q.location = "your_house"
out = run(a.cmd_build, q, "crude chair")
check("construction members-gated", "members skill" in out, out)
q2 = a.Player("Low")
q2.members = True
q2.location = "your_house"
q2.add("hammer"); q2.add("oak plank", 10)
out = run(a.cmd_build, q2, "oak bed")
check("level gate", "level 10" in out, out)
q2.location = "lumbridge_castle"
out = run(a.cmd_home, q2, "")
check("home gated on portal", "no portal chamber" in out, out)

out = run(a.cmd_look, p, "")
check("look lists furniture", "furniture:" in out and "portal chamber" in out,
      out)
p2 = a.deserialize(a.serialize(p))
check("house serialized", p2.house == p.house)
old = a.deserialize({k: v for k, v in a.serialize(p).items() if k != "house"})
check("old saves default no house", old.house == [])

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
