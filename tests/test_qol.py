"""Base-game QoL: batch skilling, typo hints, out-of-combat hp regen,
rest. (Rewrite — the original suite was lost to tmp cleanup.)"""
import io, sys, contextlib, random, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".."))
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


def do(p, cmd):
    return run(a.dispatch, p, cmd)


random.seed(22)

p = a.Player("Batcher")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[60]
p.location = "al_kharid_mine"if "al_kharid_mine" in a.ROOMS else "sw_mine"
# find any room with copper
mine_room = next(r for r, d in a.ROOMS.items()
                 if "copper" in d.get("rocks", []))
p.location = mine_room

# batch: n actions, one summary
c0 = p.count("copper ore")
out = do(p, "mine copper 5")
check("batch mines up to 5", p.count("copper ore") - c0 >= 2, out)
check("batch prints one summary", out.count("+") >= 1
      and "xp" in out.lower(), out[-200:])

# 'all' caps at 28
out = do(p, "mine copper all")
check("'all' runs without error", "xp" in out.lower() or "chip" in out,
      out[-150:])

# blocked action stops the batch loudly
p2 = a.Player("Toolless")
for it in list(p2.inventory):
    if a.ITEMS.get(it, {}).get("tool") == "pickaxe":
        p2.take(it, p2.count(it))
p2.location = mine_room
out = do(p2, "mine copper 5")
check("no pickaxe stops the batch with the reason", "pickaxe" in out, out)

# typo hints
p3 = a.Player("Fumble")
out = do(p3, "chp")
check("typo suggests the verb", "chop" in out.lower()
      or "mean" in out.lower(), out)

# hp regen out of combat, none in combat
p4 = a.Player("Healer")
p4.hp = p4.max_hp - 3
run(a._regen_energy, p4)
check("+1 hp per action out of combat", p4.hp == p4.max_hp - 2)
p4.combat = {"name": "goblin", "cur": 5, "hp": 5}
h0 = p4.hp
run(a._regen_energy, p4)
check("no regen mid-fight", p4.hp == h0)
p4.combat = None

# rest heals to full in a city
p5 = a.Player("Sleeper")
p5.hp = 3
p5.location = "lumbridge_castle"
run(a.cmd_rest, p5, "")
check("rest heals to full", p5.hp == p5.max_hp)

# batchable set covers the classics
check("batchable verbs registered",
      {"chop", "mine", "fish", "cook", "bury", "worship"} <= a.BATCHABLE)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
