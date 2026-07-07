"""Hunter — the 23rd skill: traps on the action clock at Feldip."""
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


check("hunter registered", "hunter" in a.SKILLS and len(a.SKILLS) == 23)
check("hunter cape", "hunter cape" in a.ITEMS)

p = a.Player("Tester")
p.members = True
p.location = "ardougne"
run(a.cmd_go, p, "south")
check("feldip reachable", p.location == "feldip_hills")
out = run(a.cmd_settrap, p, "")
check("settrap lists creatures", "crimson swift" in out, out)
out = run(a.cmd_settrap, p, "chinchompa")
check("level gate", "level 53" in out, out)
p.add("coins", 100)
run(a.cmd_buy, p, "bird snare")
run(a.cmd_settrap, p, "swift")
check("trap set", len(p.traps) == 1)
p.add("bird snare")
out = run(a.cmd_settrap, p, "swift")
check("slot cap at lvl 1", "only manage 1" in out, out)
out = run(a.cmd_checktraps, p, "")
check("not sprung yet", "hasn't sprung" in out, out)
for _ in range(13):
    run(a.dispatch, p, "look")
random.seed(1)
caught = False
for _ in range(20):
    out = run(a.cmd_checktraps, p, "")
    if "Caught a crimson swift" in out:
        caught = True
        break
    if not p.traps:
        if not p.has("bird snare"):
            p.add("bird snare")
        run(a.cmd_settrap, p, "swift")
        for _ in range(13):
            run(a.dispatch, p, "look")
check("caught a swift eventually", caught)
check("loot granted", p.has("raw bird meat") and p.has("feather"))
check("hunter xp", p.skills["hunter"] > 0)
p.add("tinderbox"); p.add("logs")
run(a.dispatch, p, "light logs")
out = run(a.cmd_cook, p, "raw bird meat")
check("bird meat cookable", "cook" in out.lower(), out)
p.add("bird snare")
run(a.cmd_settrap, p, "swift")
p.location = "lumbridge_castle"
out = run(a.cmd_checktraps, p, "")
check("remote check points home", "Feldip" in out, out)
p.skills["hunter"] = a._XP_TABLE[80]
check("5 slots at 80", a._trap_slots(p) == 5)
p2 = a.deserialize(a.serialize(p))
check("traps serialized", p2.traps == p.traps)
old = a.deserialize({k: v for k, v in a.serialize(p).items() if k != "traps"})
check("old saves default no traps", old.traps == {})
q = a.Player("F")
q.location = "feldip_hills"
out = run(a.cmd_settrap, q, "swift")
check("hunter members-gated", "members skill" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
