"""World-state purity: quest-story monsters are a per-player view
(QUEST_SPAWNS overlay) and the shared ROOMS map is never mutated per
player. This is the invariant that keeps saves honest today and the
engine ready for many players in one world tomorrow."""
import io, sys, contextlib, random, os, json, copy

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


def do(p, cmd):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a.dispatch(p, cmd)
    return buf.getvalue()


random.seed(11)
MANOR_BASE = list(a.ROOMS["draynor_manor"]["monsters"])

# ---- two players, one world, different stories ------------------------------
slayer = a.Player("VanHelsing")
tourist = a.Player("Tourist")
for s in ("attack", "strength", "defence", "hitpoints"):
    slayer.skills[s] = a._XP_TABLE[70]
slayer.hp = slayer.max_hp
slayer.location = "draynor_village"
out = do(slayer, "talk morgan")
check("quest started", slayer.quests.get("vampyre_slayer") == "started", out)
check("world map NOT mutated by quest start",
      a.ROOMS["draynor_manor"]["monsters"] == MANOR_BASE,
      str(a.ROOMS["draynor_manor"]["monsters"]))
check("slayer sees the count",
      "count draynor" in a._room_monsters(slayer, "draynor_manor"))
check("tourist does NOT see the count",
      "count draynor" not in a._room_monsters(tourist, "draynor_manor"))

# the count is visible in look and fightable
slayer.location = "draynor_manor"
out = do(slayer, "look")
check("look lists the count for the quester", "count draynor" in out,
      out[-300:])
tourist.location = "draynor_manor"
out = do(tourist, "look")
check("look hides the count from the tourist", "count draynor" not in out,
      out[-300:])
out = do(tourist, "fight count draynor")
check("tourist can't fight the count", tourist.combat is None, out[:200])

out = do(slayer, "fight count draynor")
check("quester can fight the count", slayer.combat is not None, out[:200])
guard = 0
while slayer.combat is not None and guard < 200:
    do(slayer, "attack")
    guard += 1
    if slayer.hp < slayer.max_hp * 0.3:
        slayer.hp = slayer.max_hp          # keep the demo on rails
check("count slain, quest complete",
      slayer.quests.get("vampyre_slayer") == "complete")
check("count gone after the kill (predicate flip)",
      "count draynor" not in a._room_monsters(slayer, "draynor_manor"))
check("world map still pristine after kill",
      a.ROOMS["draynor_manor"]["monsters"] == MANOR_BASE)

# ---- save/load needs no respawn bookkeeping ---------------------------------
mid = a.Player("Midquest")
mid.quests["priest_in_peril"] = "guardian"
data = a.player_to_json(mid)
back = a.player_from_json(data)
check("save stamps a format version", json.loads(data).get("v") == 1)
check("mid-quest monster visible after load, no respawn code",
      "temple guardian" in a._room_monsters(back, "paterdomus"))
check("paterdomus map untouched by the load",
      "temple guardian" not in a.ROOMS["paterdomus"]["monsters"])

# ---- DT guardians: alive while the diamond is unclaimed ----------------------
dt = a.Player("Raider")
dt.members = True
dt.quests["desert_treasure"] = "diamonds"
gem, room, _s = a._DT_GUARDIANS["kamil"]
check("DT guardian up while gem unclaimed",
      "kamil" in a._room_monsters(dt, room))
dt.add(gem)
check("DT guardian gone once gem is held",
      "kamil" not in a._room_monsters(dt, room))
dt.take(gem)
check("dropping the gem wakes the guardian again",
      "kamil" in a._room_monsters(dt, room))

# ---- the whole map holds no player-conjured monsters at rest -----------------
strays = [(rm, m) for rm, m, _fn in a.QUEST_SPAWNS
          if m in a.ROOMS[rm].get("monsters", [])]
check("no quest-story monster baked into the static map", not strays,
      str(strays))
# every QUEST_SPAWNS entry names a real room + a real monster, and the
# roster covers the known quest-story spawns (grows as content is added)
bad_spawns = [(rm, m) for rm, m, _f in a.QUEST_SPAWNS
              if rm not in a.ROOMS or m not in a.MONSTERS]
check("every QUEST_SPAWNS entry is a real room+monster", not bad_spawns,
      str(bad_spawns))
spawn_mons = {m for _r, m, _f in a.QUEST_SPAWNS}
check("QUEST_SPAWNS covers the quest-story monsters",
      {"count draynor", "temple guardian", "the draugen", "the experiment",
       "galvek"} <= spawn_mons and len(a.QUEST_SPAWNS) >= 9,
      str(sorted(spawn_mons)))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
