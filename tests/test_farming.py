"""Farming — the 21st skill: plant, grow on the action clock, harvest."""
import io, sys, contextlib, json, random

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


# --- registration -------------------------------------------------------------
check("farming registered", "farming" in a.SKILLS and len(a.SKILLS) >= 21)
check("farming is members", "farming" in a.MEMBERS_SKILLS)
check("farming cape exists", "farming cape" in a.ITEMS)

p = a.Player("Tester")
p.members = True
p.location = "lumbridge_farm"

# --- gates ---------------------------------------------------------------------
q = a.Player("F2P")
q.location = "lumbridge_farm"
out = run(a.cmd_plant, q, "potato")
check("farming members-gated", "members skill" in out, out)

out = run(a.cmd_plant, p, "potato")
check("plant needs the seed", "no potato seed" in out, out)
p.add("potato seed", 2)
p.add("ranarr seed")
p.location = "falador_park"                # has a herb patch
out = run(a.cmd_plant, p, "ranarr")
check("level gate", "level 32" in out, out)
p.location = "lumbridge_farm"

# --- plant, grow, harvest ---------------------------------------------------------
out = run(a.cmd_plant, p, "potato")
check("planted", "sow the potato seed" in out and p.farm, out)
check("seed consumed", p.count("potato seed") == 1)
check("plant xp granted", p.skills["farming"] > 0)
out = run(a.cmd_plant, p, "potato")
check("occupied patch refused", "already grows" in out, out)
out = run(a.cmd_harvest, p, "")
check("not ready yet", "isn't ready" in out, out)

for _ in range(31):                        # the world turns
    run(a.dispatch, p, "look")
out = run(a.cmd_look, p, "")
check("look shows READY", "READY" in out, out)
random.seed(1)
xp0 = p.skills["farming"]
out = run(a.cmd_harvest, p, "")
check("harvest yields potatoes", p.count("potato") >= 3, out)
check("harvest xp", p.skills["farming"] > xp0)
check("patch cleared", not p.farm)
check("crops counted", p.crops >= 3)

# --- farm overview across the world ------------------------------------------------
p.add("guam seed"); p.add("cabbage seed")
p.skills["farming"] = a._XP_TABLE[40]
p.location = "falador_park"
run(a.cmd_plant, p, "guam")
p.location = "catherby"
run(a.cmd_plant, p, "cabbage")
out = run(a.cmd_farm, p, "")
check("farm lists all patches", "Falador Park" in out and "Catherby" in out, out)
check("farm shows countdown", "actions to go" in out, out)

# herb patch product feeds herblore
for _ in range(46):
    run(a.dispatch, p, "look")
p.location = "falador_park"
random.seed(2)
run(a.cmd_harvest, p, "herb")
check("herb patch gives grimy guam", p.has("grimy guam"))

# --- seed stall + shop ----------------------------------------------------------------
p.location = "draynor_village"
p.skills["thieving"] = a._XP_TABLE[40]
random.seed(3)
got = False
for _ in range(30):
    run(a.cmd_steal, p, "seed")
    if any(p.has(s) for s in a.SEEDS if s != "potato seed"):
        got = True
        break
check("seed stall yields seeds", got)
p.location = "falador_park"
out = run(a.cmd_shop, p, "")
check("farming shop stocked", "potato seed" in out, out)

# --- monster seed drops registered ------------------------------------------------------
check("goblins drop seeds",
      any(d[0] == "potato seed" for d in a.MONSTERS["goblin"]["drops"]))

# --- web chips + serialization ------------------------------------------------------------
p.add("onion seed")
run(a.cmd_plant, p, "onion")
chips = json.loads(a.web_room_actions(p))
names = " ".join(c["name"] for c in chips)
check("web patch chips", "allotment" in names, names)
p2 = a.deserialize(a.serialize(p))
check("farm serialized", p2.farm == p.farm and p2.actions == p.actions
      and p2.crops == p.crops)
old = a.deserialize({k: v for k, v in a.serialize(p).items()
                     if k not in ("farm", "actions", "crops")})
check("old saves default clean", old.farm == {} and old.lvl("farming") >= 1)

# --- cape at 99 ------------------------------------------------------------------------------
p.skills["farming"] = a._XP_TABLE[99]
p.add("coins", 99000)
p.location = "draynor_village"
run(a.cmd_skillcape, p, "farming")
check("farming cape purchasable", p.has("farming cape"))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
