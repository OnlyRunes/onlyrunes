"""The smoothness batch: goto auto-walk, Enter-repeat, autoeat,
bare chop/mine best-tier, travel auto-rest, gear <style>."""
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


def do(p, cmd):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a.dispatch(p, cmd)
    return buf.getvalue()


random.seed(7)

# ---- Enter repeats the last command ---------------------------------------
p = a.Player("Repeater")
do(p, "stats")
out = do(p, "")
check("Enter repeats the last command", "(again: stats)" in out, out[:200])
check("repeat actually ran it", "attack" in out.lower(), out[:300])
p2 = a.Player("Silent")
out = do(p2, "")
check("Enter with no history does nothing", out.strip() == "", out[:120])
out = do(p, "zzzznonsense")
out = do(p, "")
check("typos are not remembered for repeat", "(again: stats)" in out, out[:200])

# ---- Enter re-fights after a kill ------------------------------------------
p3 = a.Player("Grinder")
for s in ("attack", "strength", "defence", "hitpoints"):
    p3.skills[s] = a._XP_TABLE[60]
p3.hp = p3.max_hp
p3.location = "cow_field"
out = do(p3, "fight cow")
guard = 0
while p3.combat is not None and guard < 60:
    do(p3, "attack")
    guard += 1
check("fight ended", p3.combat is None)
out = do(p3, "")
check("Enter after a kill re-fights", "(again: fight cow)" in out
      and p3.combat is not None, out[:200])
while p3.combat is not None and guard < 120:
    do(p3, "attack")
    guard += 1

# ---- goto: auto-walk through discovered rooms ------------------------------
p4 = a.Player("Walker")
do(p4, "look")
do(p4, "go west")                    # castle -> cow field (discovers it)
check("walked to the cow field", p4.location == "cow_field")
if p4.combat:
    do(p4, "flee"); do(p4, "flee"); do(p4, "flee")
do(p4, "go east")
if p4.combat:
    do(p4, "flee"); do(p4, "flee"); do(p4, "flee")
p4.combat = None
p4.hp = p4.max_hp
out = do(p4, "goto cow field")
check("goto walks to a discovered room",
      "You walk:" in out and (p4.location == "cow_field"
                              or p4.combat is not None), out[:300])
p4.combat = None
p4.location = "cow_field"
out = do(p4, "goto bank")            # nearest discovered bank (the castle)
check("goto bank finds the nearest bank",
      p4.combat is not None or a.ROOMS[p4.location].get("bank"), out[:300])
p4.combat = None
out = do(p4, "goto varrock square")  # exists, but undiscovered
check("goto refuses undiscovered places", "haven't found the way" in out,
      out[:200])
out = do(p4, "goto xyzzyplace")
check("goto handles nonsense kindly", "don't know a place" in out, out[:200])
out = do(p4, "go bank")              # 'go <place>' falls through to goto
check("'go bank' auto-walks too", "right here" in out or "You walk:" in out,
      out[:200])
out = do(p4, "go north")             # cow field has no north exit
check("'go <compass>' still refuses cleanly", "can't go that way" in out
      or p4.location != "cow_field", out[:200])

# ---- autoeat ----------------------------------------------------------------
p5 = a.Player("Nibbler")
for s in ("attack", "strength", "defence", "hitpoints"):
    p5.skills[s] = a._XP_TABLE[40]
p5.hp = p5.max_hp
p5.inventory = {"swordfish": 5, "coins": 100}
p5.location = "cow_field"
do(p5, "fight cow")
check("in combat for autoeat test", p5.combat is not None)
fish0 = p5.count("swordfish")
p5.hp = max(2, int(p5.max_hp * 0.2))         # badly hurt
out = do(p5, "attack")
if p5.combat is None:                         # cow died first — restart once
    do(p5, "fight cow")
    p5.hp = max(2, int(p5.max_hp * 0.2))
    out = do(p5, "attack")
check("autoeat kicks in when badly hurt", "autoeat" in out
      and p5.count("swordfish") < fish0, out[-300:])
check("autoeat healed", p5.hp > p5.max_hp * 0.2 or p5.combat is None)
out = do(p5, "autoeat off")
check("autoeat toggles off in combat", "OFF" in out, out[:200])
p5.hp = max(2, int(p5.max_hp * 0.2))
fish1 = p5.count("swordfish")
out = do(p5, "attack")
check("no reflex eating when off", "autoeat:" not in out
      and p5.count("swordfish") == fish1, out[-200:])
p5.combat = None
out = do(p5, "autoeat on")
check("autoeat toggles back on", "ON" in out, out[:200])

# ---- bare chop/mine pick the best tier you can do ---------------------------
p6 = a.Player("Lumber")
p6.skills["woodcutting"] = a._XP_TABLE[30]
oak_room = next(r for r, d in a.ROOMS.items()
                if "oak" in d.get("trees", []) and "tree" in d.get("trees", []))
p6.location = oak_room
out = do(p6, "chop")
check("bare 'chop' picks the best tree (oak)", "oak" in out, out[:250])
p7 = a.Player("Digger")
p7.skills["mining"] = a._XP_TABLE[30]
iron_room = next(r for r, d in a.ROOMS.items()
                 if "iron" in d.get("rocks", []) and "copper" in d.get("rocks", []))
p7.location = iron_room
rocks_here = a.ROOMS[iron_room]["rocks"]
expect = max((x for x in rocks_here if a.ROCKS[x][1] <= 30),
             key=lambda x: a.ROCKS[x][1])
out = do(p7, "mine")
check(f"bare 'mine' picks the best rock ({expect})", expect in out, out[:250])

# ---- travel auto-rests in a city --------------------------------------------
p8 = a.Player("Roadie")
p8.location = "lumbridge_castle"
p8.run_energy = 0
out = do(p8, "travel varrock")
check("travel auto-rests in a city", "rest" in out.lower()
      and p8.location == a.TRAVEL_HUBS["varrock"], out[:300])
p8.combat = None

# ---- gear <style> ------------------------------------------------------------
p9 = a.Player("Fashion")
p9.skills["magic"] = a._XP_TABLE[45]
p9.skills["ranged"] = a._XP_TABLE[45]
p9.skills["defence"] = a._XP_TABLE[45]      # mystic/d'hide demand defence
p9.quests["dragon_slayer"] = "complete"     # d'hide body is quest-locked
p9.members = True
for it in ("mystic robe top", "mystic robe bottom", "staff of fire",
           "maple shortbow", "green d'hide body", "iron arrow"):
    if it in a.ITEMS:
        p9.add(it, 50 if it == "iron arrow" else 1)
out = do(p9, "gear magic")
check("gear magic switches style", p9.style == "magic", out[:300])
check("gear magic wears the robes",
      p9.equipment.get("body") == "mystic robe top"
      or "mystic" in (p9.equipment.get("body") or ""), str(p9.equipment))
out = do(p9, "gear ranged")
check("gear ranged switches back", p9.style == "ranged", out[:200])
check("gear ranged equips d'hide/bow",
      "bow" in (p9.equipment.get("weapon") or ""), str(p9.equipment))
out = do(p9, "gear")
check("bare 'gear' re-checks current style", "ranged" in out, out[:200])
out = do(p9, "gear cabbage")
check("gear rejects nonsense styles", "melee" in out and "magic" in out,
      out[:200])

# ---- seen/autoeat survive the save ------------------------------------------
p10 = a.Player("Saver")
do(p10, "go west")
p10.combat = None
p10.autoeat = False
data = a.player_to_json(p10)
q = a.player_from_json(data)
check("discovered rooms survive the save", "cow_field" in getattr(q, "seen", set()),
      str(getattr(q, "seen", None)))
check("autoeat setting survives the save", q.autoeat is False)

# older saves (no 'seen' data) get the free-to-travel cities seeded
import json
old = json.loads(data)
del old["seen"]
old["members"] = False
q2 = a.player_from_json(json.dumps(old))
check("old saves seed free travel hubs",
      a.TRAVEL_HUBS["varrock"] in q2.seen
      and a.TRAVEL_HUBS["lumbridge"] in q2.seen, str(sorted(q2.seen))[:200])
members_hub = next((r for r in set(a.TRAVEL_HUBS.values())
                    if a.ROOMS[r].get("members")), None)
if members_hub:
    check("old f2p saves don't learn members cities",
          members_hub not in q2.seen, members_hub)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
