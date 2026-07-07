"""Kandarin completion: Camelot + Merlin's Crystal, Baxtorian Falls +
Waterfall Quest, fire giants, gnome course, Fishing/Magic Guild gates,
sharks, and excalibur's ward."""
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


def settle(pl):
    guard = 0
    while getattr(pl, "combat", None) is not None and pl.hp > 0 and guard < 300:
        guard += 1
        run(a.dispatch, pl, "attack")


def fresh_max():
    p = a.Player("T")
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.hp = p.max_hp
    p.prayer_points = p.prayer_max()
    for slot, item in a._best_gear_for_style("melee").items():
        p.add(item)
        run(p.equip_item, item, True)
    run(a.dispatch, p, "style slash")
    p.add("swordfish", 500)
    return p


random.seed(44)

print("=== 1. wiring ====================================================")
for rm in ("camelot", "baxtorian_falls", "waterfall_cave",
           "tree_gnome_stronghold", "fishing_guild", "yanille",
           "magic_guild"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} in Kandarin", a.REGIONS.get(rm) == "Kandarin")
check("seers -> camelot", a.ROOMS["seers_village"]["exits"].get("castle")
      == "camelot")
check("ardougne -> falls/gnome/yanille",
      a.ROOMS["ardougne"]["exits"].get("falls") == "baxtorian_falls"
      and a.ROOMS["ardougne"]["exits"].get("gnome") == "tree_gnome_stronghold"
      and a.ROOMS["ardougne"]["exits"].get("yanille") == "yanille")
check("ardougne polish keeps the keywords",
      "falls" in a.ROOMS["ardougne"]["desc"]
      and "yanille" in a.ROOMS["ardougne"]["desc"])
check("hubs registered", a.TRAVEL_HUBS.get("yanille") == "yanille"
      and a.TRAVEL_HUBS.get("gnome stronghold") == "tree_gnome_stronghold")

print("=== 2. guild gates weigh the right skills ========================")
lo = a.Player("Low")
lo.members = True
lo.location = "seers_village"
out = run(a.cmd_go, lo, "guild")
check("fishing guild refuses fishing 1", lo.location == "seers_village"
      and "68" in out, out)
lo.skills["fishing"] = a._XP_TABLE[68]
run(a.cmd_go, lo, "guild")
check("fishing 68 admitted", lo.location == "fishing_guild")
lo.location = "yanille"
out = run(a.cmd_go, lo, "guild")
check("magic guild refuses magic 1", lo.location == "yanille"
      and "66" in out, out)
lo.skills["magic"] = a._XP_TABLE[66]
run(a.cmd_go, lo, "guild")
check("magic 66 admitted", lo.location == "magic_guild")
check("guild shop stocks blood runes",
      "blood rune" in a.SHOPS["magic_guild"])

print("=== 3. sharks ====================================================")
ps = fresh_max()
ps.location = "fishing_guild"
ps.add("harpoon")
got = False
for _ in range(60):
    run(a.cmd_fish, ps, "")
    if ps.has("raw shark"):
        got = True
        break
check("level 99 harpoons sharks", got)
mid = a.Player("Mid")
mid.members = True
mid.skills["fishing"] = a._XP_TABLE[70]   # below 76: swordfish, not shark
mid.location = "fishing_guild"
mid.add("harpoon")
for _ in range(60):
    run(a.cmd_fish, mid, "")
check("fishing 70 gets swordfish, never sharks",
      not mid.has("raw shark") and mid.has("raw swordfish"))
ps.location = "catherby"
ps.add("raw shark", 5)
run(a.cmd_light, ps, "") if hasattr(a, "cmd_light") else None
cooked = 0
ps.location = "lumbridge_castle"       # castle range
for _ in range(12):
    if not ps.has("raw shark"):
        break
    run(a.cmd_cook, ps, "raw shark")
    cooked = ps.count("shark")
check("sharks cook on a range", cooked >= 1, str(cooked))
check("shark heals 20", a.ITEMS["shark"]["heal"] == 20)

print("=== 4. waterfall quest, honestly =================================")
p4 = fresh_max()
p4.location = "baxtorian_falls"
out = run(a.cmd_go, p4, "cave")
check("cave sealed pre-amulet", p4.location == "baxtorian_falls"
      and "Waterfall" in out, out)
out = do(p4, "talk")
check("almera starts the quest", a._q(p4, "waterfall_quest") == "started",
      out)
out = run(a.cmd_search, p4, "")
check("tombstone yields the amulet", p4.has("glarial's amulet")
      and a._q(p4, "waterfall_quest") == "amulet", out)
atk0, str0 = p4.skills["attack"], p4.skills["strength"]
qp0 = a.quest_points(p4)
run(a.cmd_go, p4, "cave")
settle(p4)
check("cave opens with the amulet", p4.location == "waterfall_cave")
out = run(a.cmd_search, p4, "")
check("chalice completes the quest",
      a._q(p4, "waterfall_quest") == "complete", out)
check("+1 QP", a.quest_points(p4) == qp0 + 1)
check("13,750 attack AND strength xp",
      p4.skills["attack"] - atk0 >= 27500
      and p4.skills["strength"] - str0 >= 27500,
      f"atk +{p4.skills['attack']-atk0}")

print("=== 5. merlin's crystal ==========================================")
p5 = fresh_max()
p5.quests.pop("merlins_crystal", None)
p5.location = "camelot"
out = do(p5, "talk")
check("arthur sends you to the lady",
      a._q(p5, "merlins_crystal") == "excalibur", out)
out = run(a.cmd_search, p5, "")
check("crystal shrugs off bare hands", "EXCALIBUR" in out
      and a._q(p5, "merlins_crystal") == "excalibur", out)
p5.location = "catherby"
for it in list(p5.inventory):
    if it == "bread":
        p5.take("bread", p5.count("bread"))
out = do(p5, "talk")
check("lady tests with bread (refused empty-handed)",
      not p5.has("excalibur"), out)
p5.add("bread")
out = do(p5, "talk")
check("bread buys the blade", p5.has("excalibur")
      and not p5.has("bread")
      and a._q(p5, "merlins_crystal") == "shatter", out)
qp0 = a.quest_points(p5)
p5.location = "camelot"
out = run(a.cmd_search, p5, "")
check("excalibur shatters the crystal",
      a._q(p5, "merlins_crystal") == "complete", out)
check("+6 QP", a.quest_points(p5) == qp0 + 6)
run(p5.equip_item, "excalibur", True)
check("excalibur wearable post-quest",
      p5.equipment.get("weapon") == "excalibur")
# the ward: spec grants +8 defence for the fight
p5.location = "lumbridge_forest"
run(a.dispatch, p5, "fight goblin")
if p5.combat is not None:
    p5.spec_energy = 100
    out = do(p5, "spec")
    check("Sanctuary hardens the guard",
          p5.stat_boost.get("defence", 0) >= 8 or p5.combat is None, out)
    settle(p5)
check("excalibur ward clears after combat",
      p5.stat_boost.get("defence", 0) == 0)

print("=== 6. fire giants + gnome course ================================")
check("fire giant registered", "fire giant" in a.MONSTERS
      and a.MONSTERS["fire giant"]["level"] == 86)
check("rune scimitar on the table",
      any(d[0] == "rune scimitar"
          for d in a.MONSTERS["fire giant"]["drops"]))
p6 = fresh_max()
p6.location = "waterfall_cave"
run(a.dispatch, p6, "fight fire giant")
settle(p6)
check("fire giant killable", p6.combat is None and p6.hp > 0)
g = a.Player("Gnomeling")
g.members = True
g.location = "tree_gnome_stronghold"
xp0 = g.skills["agility"]
for _ in range(6):
    run(a.dispatch, g, "agility")
    g.hp = g.max_hp
check("gnome course trains level-1 agility", g.skills["agility"] > xp0)

print("=== 7. serialization =============================================")
p7 = fresh_max()
p7.quests["waterfall_quest"] = "amulet"
p7.quests["merlins_crystal"] = "shatter"
p7.add("excalibur")
blob = a.player_to_json(p7)
p72 = a.player_from_json(blob)
check("stages + excalibur survive",
      p72.quests.get("waterfall_quest") == "amulet"
      and p72.quests.get("merlins_crystal") == "shatter"
      and p72.has("excalibur"))

print("=== 8. journal ===================================================")
j = a.Player("J")
out = run(a.cmd_quests, j, "")
check("journal lists both quests", "Waterfall Quest" in out
      and "Merlin's Crystal" in out)
check("start hints shown", "start: Almera" in out
      and "start: King Arthur" in out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
