"""Black Knights' Fortress: the 12-QP gate, the disguise gear-lock, the
cabbage sabotage, and multi-NPC talk. (Rewrite — the original suite was
lost to tmp cleanup.)"""
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


random.seed(20)

p = a.Player("Squire")
p.location = "white_knights_castle"

# 12-QP gate
out = do(p, "talk amik")
check("amik demands 12 qp", a._q(p, "black_knights") == "not_started", out)
for k in ("cooks_assistant", "sheep_shearer", "dorics_quest",
          "romeo_juliet", "vampyre_slayer", "ernest_chicken"):
    p.quests[k] = "complete"
check("bots have 12 qp", a.quest_points(p) >= 12)
out = do(p, "talk amik")
check("quest starts with 12 qp", a._q(p, "black_knights") == "infiltrate",
      out)

# multi-NPC room lists names
out = do(p, "talk")
check("multi-npc room offers a pick", "talk" in out.lower(), out)

# the fortress demands the disguise
p.location = "monastery"
out = run(a.cmd_go, p, "fortress")
check("fortress bars the undisguised",
      p.location == "monastery" and "wearing" in out, out)
for it in ("bronze med helm", "iron chainbody"):
    p.add(it)
    run(p.equip_item, it, True)
run(a.cmd_go, p, "fortress")
check("disguise admits you", p.location == "black_knights_fortress")

# sabotage needs the cabbage
if p.has("cabbage"):
    p.take("cabbage", p.count("cabbage"))
out = run(a.cmd_search, p, "")
check("no cabbage, no sabotage",
      a._q(p, "black_knights") == "infiltrate", out)
p.add("cabbage")
out = run(a.cmd_search, p, "")
check("cabbage curdles the brew",
      a._q(p, "black_knights") == "sabotaged", out)

# the reward
p.location = "white_knights_castle"
coins0 = p.count("coins")
qp0 = a.quest_points(p)
out = do(p, "talk amik")
check("quest complete", a._q(p, "black_knights") == "complete", out)
check("2,500 coins paid", p.count("coins") - coins0 == 2500)
check("+3 quest points", a.quest_points(p) == qp0 + 3)

# the fortress garrison
check("black knight registered", "black knight" in a.MONSTERS)
blob = a.player_to_json(p)
p2 = a.player_from_json(blob)
check("quest survives the save",
      p2.quests.get("black_knights") == "complete")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
