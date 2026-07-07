"""Slayer Tower & overhaul: gates, counter-gear, finisher, masters, streaks."""
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


def settle(pl):
    guard = 0
    while getattr(pl, "combat", None) is not None and pl.hp > 0 and guard < 400:
        guard += 1
        run(a.dispatch, pl, "attack")


# --- tower wiring ------------------------------------------------------------
check("tower off canifis", a.ROOMS["canifis"]["exits"].get("tower")
      == "slayer_tower_1")
for rm in ("slayer_tower_1", "slayer_tower_2", "slayer_tower_3"):
    check(f"{rm} hostile + region", a.ROOMS[rm].get("hostile")
          and a.REGIONS.get(rm) == "Morytania")

# --- slayer level gates -----------------------------------------------------------
p = a.Player("Novice")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[90]
p.skills["slayer"] = a._XP_TABLE[10]
p.hp = p.max_hp
for slot, item in a._best_gear_for_style("melee").items():
    p.add(item)
    run(p.equip_item, item, True)
p.add("swordfish", 500)
p.location = "slayer_tower_3"
out = run(a.cmd_fight, p, "abyssal demon")
check("abyssal gated at 85", "slayer level 85" in out and p.combat is None, out)
out = run(a.cmd_fight, p, "gargoyle")
check("gargoyle gated at 75", "slayer level 75" in out, out)

# ambush never sends the ungated... enter floor 3 repeatedly at slayer 10
random.seed(2)
clean = True
for _ in range(40):
    p.location = "slayer_tower_2"
    p.combat = None
    run(a.cmd_go, p, "up")
    if p.combat is not None:
        clean = False
        break
check("no ambush by ungated horrors", clean)

# --- counter-gear ----------------------------------------------------------------
p.skills["slayer"] = a._XP_TABLE[90]

# banshee scream vs earmuffs
b = a._new_monster("banshee")
p.stat_drain = {}
buf = ""
random.seed(3)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, b)
    if "SCREAM" in buf:
        break
check("banshee screams bare-headed", "SCREAM" in buf
      and p.stat_drain.get("attack", 0) > 0)
p.add("earmuffs")
run(p.equip_item, "earmuffs", True)
p.stat_drain = {}
buf = ""
random.seed(3)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, b)
check("earmuffs block the scream", "SCREAM" not in buf
      and not p.stat_drain)

# basilisk gaze vs mirror shield
bas = a._new_monster("basilisk")
p.stat_drain = {}
buf = ""
random.seed(4)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, bas)
    if "gaze" in buf:
        break
check("basilisk gaze drains", "gaze" in buf)
p.add("mirror shield")
run(p.equip_item, "mirror shield", True)
p.stat_drain = {}
buf = ""
random.seed(4)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, bas)
check("mirror shield reflects the gaze", "gaze" not in buf)

# spectre stench vs slayer helmet
sp = a._new_monster("aberrant spectre")
p.stat_drain = {}
buf = ""
random.seed(5)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, sp)
    if "stench" in buf:
        break
check("spectre stench sears", "stench" in buf)
p.add("slayer helmet")
run(p.equip_item, "slayer helmet", True)
p.stat_drain = {}
buf = ""
random.seed(5)
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, sp)
check("slayer helm seals out the stench", "stench" not in buf)

# --- gargoyle finisher ---------------------------------------------------------------
g = a._new_monster("gargoyle")
g["cur"] = 1
buf = ""
random.seed(6)
for _ in range(60):
    buf += run(a._resolve_player_hit, p, g)
    if "knits back together" in buf:
        break
check("gargoyle reforms without hammer", "knits back together" in buf
      and g["cur"] > 0)
p.add("rock hammer")
g["cur"] = 1
won = False
random.seed(6)
for _ in range(60):
    out = run(a._resolve_player_hit, p, g)
    if g["cur"] <= 0:
        won = True
        break
check("rock hammer finishes it", won)

# --- whip source moved ------------------------------------------------------------------
check("greater demons lost the whip",
      not any(d[0] == "abyssal whip"
              for d in a.MONSTERS["greater demon"]["drops"]))
check("abyssal demons drop the whip",
      any(d[0] == "abyssal whip"
          for d in a.MONSTERS["abyssal demon"]["drops"]))

# --- masters ---------------------------------------------------------------------------------
t = a.Player("Fresh")
t.members = True
t.location = "taverley"
run(a.cmd_talk, t, "")
check("turael assigns to anyone", t.slayer_task is not None
      and t.slayer_task["monster"] in a.TURAEL_TARGETS)

d = a.Player("Soft")
d.members = True
d.location = "brimhaven"
out = run(a.cmd_talk, d, "")
check("duradel refuses the soft", "combat 100" in out
      and d.slayer_task is None, out)
for s in a.SKILLS:
    d.skills[s] = a._XP_TABLE[99]
run(a.cmd_talk, d, "")
check("duradel assigns to the worthy", d.slayer_task is not None
      and d.slayer_task["monster"] in a.DURADEL_TARGETS,
      str(d.slayer_task))

lowslay = a.Player("LowSlay")
lowslay.members = True
for s in a.SKILLS:
    lowslay.skills[s] = a._XP_TABLE[99]
lowslay.skills["slayer"] = a._XP_TABLE[20]
lowslay.location = "brimhaven"
out = run(a.cmd_talk, lowslay, "")
check("duradel also demands slayer 50", "slayer 50" in out, out)

# vannaka pool respects the player's slayer level too (no gated tasks)
v = a.Player("Vann")
v.members = True
v.skills["slayer"] = a._XP_TABLE[10]
v.location = "edgeville"
ok = True
random.seed(7)
for _ in range(25):
    v.slayer_task = None
    run(a.cmd_talk, v, "")
    mon = v.slayer_task["monster"]
    if a.MONSTERS[mon].get("slayer_req", 0) > 10:
        ok = False
        break
check("assignments respect slayer level", ok)

# --- streaks --------------------------------------------------------------------------------------
s = a.Player("Streaker")
s.members = True
s.slayer_points = 0
pts_log = []
for i in range(1, 11):
    s.slayer_task = {"monster": "cow", "amount": 1, "remaining": 1}
    before = s.slayer_points
    run(a._quest_on_kill, s, "cow")
    pts_log.append(s.slayer_points - before)
check("streak counts", s.task_streak == 10, str(s.task_streak))
check("5th task pays x3", pts_log[4] == pts_log[0] * 3, str(pts_log))
check("10th task pays x5", pts_log[9] == pts_log[0] * 5, str(pts_log))
check("taskmaster achievement", "taskmaster" in a._earned_achievements(s))
# skip resets
s.location = "edgeville"
s.slayer_task = {"monster": "cow", "amount": 5, "remaining": 5}
s.slayer_points = 50
run(a.cmd_slayerbuy, s, "skip")
check("skip resets the streak", s.task_streak == 0)

# --- slayerbuy gear ------------------------------------------------------------------------------
s.slayer_points = 50
run(a.cmd_slayerbuy, s, "mirror")
check("mirror shield purchasable", s.has("mirror shield")
      and s.slayer_points == 35)

# --- a real tower hunt: duradel task done on-site ---------------------------------------------------
h = a.Player("Hunter")
h.members = True
for s2 in a.SKILLS:
    h.skills[s2] = a._XP_TABLE[99]
h.hp = h.max_hp
for slot, item in a._best_gear_for_style("melee").items():
    h.add(item)
    run(h.equip_item, item, True)
h.add("swordfish", 500)
h.add("rock hammer")
h.slayer_task = {"monster": "gargoyle", "amount": 3, "remaining": 3}
h.location = "slayer_tower_2"
random.seed(8)
run(a.cmd_go, h, "up")
settle(h)
guard = 0
while h.slayer_task and h.slayer_task.get("remaining", 0) > 0 and guard < 40:
    guard += 1
    if h.combat is None:
        if h.hp < 60:
            run(a.dispatch, h, "eat swordfish")
        else:
            run(a.dispatch, h, "fight gargoyle")
    else:
        run(a.dispatch, h, "attack")
check("gargoyle task completed in the tower", h.slayer_task is None
      and h.task_streak >= 1, f"guard={guard}")

# serialization
h2 = a.deserialize(a.serialize(h))
check("streak serialized", h2.task_streak == h.task_streak)
old = a.deserialize({k: v for k, v in a.serialize(h).items()
                     if k != "task_streak"})
check("old saves default streak 0", old.task_streak == 0)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
