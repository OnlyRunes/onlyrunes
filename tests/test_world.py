"""World pushes back: ambushes, train focus, bird's nests, ambience."""
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


# --- train focus -----------------------------------------------------------
p = a.Player("Trainee")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[50]
p.hp = p.max_hp
out = run(a.dispatch, p, "train strength")
check("train sets focus", p.train == "strength", out)
xp0 = {s: p.skills[s] for s in ("attack", "strength", "defence")}
run(a._award_combat_xp, p, 30)
check("focused xp goes to strength",
      p.skills["strength"] > xp0["strength"]
      and p.skills["attack"] == xp0["attack"]
      and p.skills["defence"] == xp0["defence"])
run(a.dispatch, p, "train shared")
xp0 = {s: p.skills[s] for s in ("attack", "strength", "defence")}
run(a._award_combat_xp, p, 30)
check("shared splits three ways",
      all(p.skills[s] > xp0[s] for s in xp0))
out = run(a.cmd_train, p, "sideways")
check("bad focus explained", "Train what?" in out, out)
out = run(a.cmd_train, p, "")
check("bare train shows current", "shared" in out, out)
p2 = a.deserialize(a.serialize(p))
check("focus serialized", p2.train == "shared")
old = a.deserialize({k: v for k, v in a.serialize(p).items() if k != "train"})
check("old saves default shared", old.train == "shared")

# --- bird's nests ------------------------------------------------------------
q = a.Player("Lumberjack")
q.skills["woodcutting"] = a._XP_TABLE[60]
q.add("rune axe")
q.location = "edgeville"
random.seed(11)
buf = ""
got = False
for _ in range(300):
    buf += run(a.cmd_chop, q, "yew")
    if "bird's nest" in buf:
        got = True
        break
check("nests fall eventually", got)
check("nest gave a prize", any(q.has(i) for i, _ in a._NEST_LOOT))
# nest pops through batch quiet mode (print, not say)
random.seed(11)
q2 = a.Player("Batcher")
q2.skills["woodcutting"] = a._XP_TABLE[60]
q2.add("rune axe")
q2.location = "edgeville"
buf = ""
for _ in range(30):
    buf += run(a.dispatch, q2, "chop yew 28")
    if "bird's nest" in buf:
        break
check("nest visible mid-batch", "bird's nest" in buf)

# --- ambushes -------------------------------------------------------------------
low = a.Player("Prey")
low.hp = low.max_hp
random.seed(4)
ambushed = False
for _ in range(30):
    low.location = "edgeville"
    low.combat = None
    run(a.cmd_go, low, "down")           # hostile dungeon
    if low.combat is not None:
        ambushed = True
        break
check("low levels get ambushed in dungeons", ambushed)
check("ambush is a real fight", low.combat is not None
      and low.combat["name"] in a.ROOMS["edgeville_dungeon"]["monsters"])
while low.combat is not None and low.hp > 0:
    run(a.dispatch, low, "flee")
    if low.hp <= 0:
        break

big = a.Player("Apex")
for s in a.SKILLS:
    big.skills[s] = a._XP_TABLE[99]
big.hp = big.max_hp
random.seed(4)
safe = True
for _ in range(40):
    big.location = "edgeville"
    big.combat = None
    run(a.cmd_go, big, "down")
    if big.combat is not None:
        safe = False
        break
check("maxed players are beneath notice", safe)

towny = a.Player("Towny")
random.seed(4)
calm = True
for _ in range(40):
    towny.location = "lumbridge_castle"
    towny.combat = None
    run(a.cmd_go, towny, "west")         # cow field: not hostile
    if towny.combat is not None:
        calm = False
        break
check("towns and fields stay safe", calm)

boss_row = [m for m in a.ROOMS["gwd_entrance"].get("monsters", [])]
check("gwd entrance hostile but empty of lurkers", boss_row == [])

# --- ambience ----------------------------------------------------------------------
amb = a.Player("Wanderer")
for s in a.SKILLS:
    amb.skills[s] = a._XP_TABLE[99]     # no ambush noise
amb.hp = amb.max_hp
random.seed(9)
seen = False
for _ in range(60):
    amb.location = "wilderness_edge"
    out = run(a.cmd_go, amb, "north")    # deep wilderness (Wilderness region)
    if any(l in out for l in a.REGION_AMBIENT["Wilderness"]):
        seen = True
        break
check("ambient lines appear in the wastes", seen)

# --- inventory values -----------------------------------------------------------------
v = a.Player("Rich")
v.add("rune platebody")
out = run(a.cmd_inventory, v, "")
check("inventory shows worth", "gp)" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
