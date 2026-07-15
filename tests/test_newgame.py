"""The first hour, played honestly: a fresh character follows the game's own
goal suggestions through fights, Cook's Assistant, cooking, banking."""
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


def do(p, cmd):
    return run(a.dispatch, p, cmd)


random.seed(2026)
p = a.Player("Newbie")

# --- the compass points somewhere sensible at every stage ---------------------
g = a._next_goal(p)
check("fresh goal = first fight", "first fight" in g, g)

# --- first fights (goal 1) ------------------------------------------------------
do(p, "travel lumbridge")
do(p, "go west")                      # cow field
kills = 0
guard = 0
while kills < 3 and guard < 300:
    guard += 1
    if p.combat is None:
        if p.hp < p.max_hp * 0.5:
            do(p, "rest") if p.location in a.TRAVEL_HUBS.values() else None
        do(p, "fight cow")
    else:
        do(p, "attack")
        if p.combat is None and p.hp > 0:
            kills += 1
check("three cows slain", kills >= 3, f"kills={kills} hp={p.hp}")
check("beef and hides looted", p.has("raw beef") or p.has("cowhide"))
g = a._next_goal(p)
check("goal moves to Cook's Assistant", "Cook" in g, g)

# --- Cook's Assistant, done properly (goal 2) -------------------------------------
do(p, "go east")                      # lumbridge castle
out = do(p, "talk")
check("quest started", a._q(p, "cooks_assistant") == "started", out)
check("given bucket and pot", p.has("bucket") and p.has("pot"))
# egg + milk at the farm, east of the river
do(p, "go east")                      # river lum
do(p, "go north") if "north" in a.ROOMS[p.location]["exits"] else None
# route: find the farm via known map (river_lum -> lumbridge_forest? use travel)
p.location = "lumbridge_farm"         # (bot shortcut: pathing isn't the test)
out = do(p, "collect")
check("egg collected", p.has("egg"), out)
out = do(p, "milk")
check("milk in bucket", p.has("bucket of milk"), out)
do(p, "pick")
check("grain picked", p.has("grain"))
p.location = "windmill"
out = do(p, "mill")
check("flour milled", p.has("pot of flour"), out)
p.location = "lumbridge_castle"
xp0 = p.skills["cooking"]
out = do(p, "talk")
check("Cook's Assistant complete", a._q(p, "cooks_assistant") == "complete",
      out)
check("cooking xp reward", p.skills["cooking"] > xp0)

# --- cook the beef on the castle range ----------------------------------------------
if not p.has("raw beef"):
    p.add("raw beef")
beef0 = p.count("raw beef")
out = do(p, "cook raw beef")
check("beef cooked (or burnt honestly)", p.count("raw beef") == beef0 - 1, out)

# --- bank the loot --------------------------------------------------------------------
do(p, "deposit all")
check("bank holds the goods", len(p.bank) > 0)

# --- combat training until the goal moves on -------------------------------------------
p.location = "lumbridge_forest"
guard = 0
while p.combat_level() < 12 and guard < 120:
    guard += 1
    if p.hp < 12:
        p.hp = p.max_hp               # simulate eating the cooked beef
    do(p, "fight goblin auto")
check("combat level reached 12", p.combat_level() >= 12,
      str(p.combat_level()))
g = a._next_goal(p)
check("goal moves past goblins", "goblin" not in g.lower(), g)

# --- journal shows starts for the unstarted ----------------------------------------------
out = run(a.cmd_quests, p, "")
check("journal shows start hints", "start: Farmer Fred" in out, out)
check("journal shows dragon slayer gate",
      "the Guildmaster, Champions' Guild (12 qp)" in out, out)

# --- no wasted turns on full-hp eating -----------------------------------------------------
p.hp = p.max_hp
p.add("bread")
out = run(a.cmd_eat, p, "bread")
check("full-hp eat refused, food kept", p.has("bread")
      and "full health" in out, out)
p.location = "wilderness_edge"
do(p, "fight skeleton")
if p.combat is not None:
    p.hp = p.max_hp
    m0 = p.combat["cur"]
    out = do(p, "eat bread")
    check("combat full-hp eat keeps your turn", p.combat is None
          or p.combat["cur"] == m0, out)
    while p.combat is not None and p.hp > 0:
        do(p, "attack")

# --- goal ladder spot-checks at later stages -------------------------------------------------
q = a.Player("Mid")
q.kills = 50
q.quests = {"cooks_assistant": "complete", "sheep_shearer": "complete",
            "dorics_quest": "complete"}
for s in a.SKILLS:
    q.skills[s] = a._XP_TABLE[30]
g = a._next_goal(q)
check("mid goal mentions quest points", "12 quest points" in g, g)
q.quests.update({"romeo_juliet": "complete", "vampyre_slayer": "complete",
                 "ernest_chicken": "complete"})
g = a._next_goal(q)
check("post-12qp goal = dragon slayer", "DRAGON SLAYER" in g, g)
q.quests["dragon_slayer"] = "complete"
g = a._next_goal(q)
check("then membership pitch", "membership" in g, g)
q.members = True
q.skills["slayer"] = a._XP_TABLE[25]
for s in ("attack", "strength", "defence", "hitpoints"):
    q.skills[s] = a._XP_TABLE[85]
g = a._next_goal(q)
check("warriors' guild rung fires first", "Warriors' Guild" in g, g)
q.add("rune defender")
q.bosses = ["obor"]
q.quests["priest_in_peril"] = "complete"
g = a._next_goal(q)
check("endgame ladder reaches barrows", "Barrows" in g, g)
q.barrows_loots = 2
q.bosses += ["tztok-jad", "general graardor", "kree'arra",
             "k'ril tsutsaroth", "commander zilyana"]
g = a._next_goal(q)
check("tower rung before the 99 chase", "Slayer Tower" in g, g)
q.skills["slayer"] = a._XP_TABLE[70]
g = a._next_goal(q)
check("then the desert queen", "Kalphite" in g, g)
q.bosses += ["kalphite queen"]
g = a._next_goal(q)
check("then the three Kings", "Waterbirth" in g, g)
q.bosses += ["dagannoth rex", "dagannoth prime", "dagannoth supreme"]
g = a._next_goal(q)
check("then the Nightmare", "NIGHTMARE" in g, g)
q.bosses += ["the nightmare"]
g = a._next_goal(q)
check("then the warlords", "WARLORDS" in g, g)
q.bosses += ["callisto", "venenatis", "vet'ion", "corporeal beast"]
g = a._next_goal(q)
check("then Dragon Slayer II", "DRAGON SLAYER II" in g, g)
q.quests["dragon_slayer_2"] = "complete"
g = a._next_goal(q)
check("then Vorkath", "VORKATH" in g, g)
q.bosses += ["vorkath"]
g = a._next_goal(q)
check("then Song of the Elves", "SONG OF THE ELVES" in g, g)
q.quests["song_of_the_elves"] = "complete"
g = a._next_goal(q)
check("then the Gauntlet", "GAUNTLET" in g, g)
q.bosses += ["crystalline hunllef"]
g = a._next_goal(q)
check("then the Inferno", "INFERNO" in g, g)
q.bosses += ["tzkal-zuk"]
g = a._next_goal(q)
check("then the 99 chase", "99" in g, g)

# 'goal' command + resume summary carry it
out = run(a.cmd_goal, p, "")
check("goal command works", "Next Up" in out, out)
out = run(a._resume_summary, p)
check("welcome-back shows the goal", "Next up:" in out, out)
out = run(a.cmd_me, p, "")
check("me shows the goal", "Next up" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
