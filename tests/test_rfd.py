"""Recipe for Disaster: the 40-QP gate, the frozen banquet's sequential
courses, Flambeed's bucket-of-water rule, cooking gauntlets, and the
barrows gloves."""
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
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        a.dispatch(p, cmd)
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", b.getvalue())


def flat(s):
    return " ".join(s.split())


def maxed(name):
    p = a.Player(name)
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.add("dragon scimitar")
    p.equip_item("dragon scimitar", silent=True)
    p.style = "melee"
    p.attack_type = "crush"
    p.hp = p.max_hp
    return p


def kill(p, mon, cap=250):
    do(p, f"fight {mon}")
    n = 0
    while p.combat is not None and n < cap:
        p.hp = p.max_hp
        do(p, "attack")
        n += 1
    return p.combat is None


random.seed(30)

# ---- the 40 QP gate -----------------------------------------------------------
novice = maxed("Novice")
novice.location = "lumbridge_castle"
out = do(novice, "talk gypsy")
check("gate refuses under 40 QP",
      a._q(novice, "recipe_for_disaster") == "not_started"
      and "forty quest points" in flat(out).lower(), flat(out)[:180])
out = do(novice, "go banquet")
check("the banquet is sealed", novice.location == "lumbridge_castle"
      and "Recipe for Disaster" in flat(out), flat(out)[:160])

# ---- a seasoned hero starts it -------------------------------------------------
p = maxed("Hero")
for k in a.ALL_QUESTS:
    if k != "recipe_for_disaster":
        p.quests[k] = "complete"
check("hero holds 40+ QP", a.quest_points(p) >= 40, a.quest_points(p))
p.location = "lumbridge_castle"
out = do(p, "talk gypsy")
check("Gypsy Aris starts the quest",
      a._q(p, "recipe_for_disaster") == "agrith", out[:200])

# ---- courses arrive one at a time ----------------------------------------------
mons = a._room_monsters(p, "banquet_hall")
check("only the first course is served", mons.count("agrith-na-na") == 1
      and "flambeed" not in mons and "culinaromancer" not in mons,
      str(mons))
do(p, "go banquet")
check("the frozen banquet admits the quester",
      p.location == "banquet_hall")
won = kill(p, "agrith-na-na")
check("Agrith-Na-Na falls, Flambeed is served",
      won and a._q(p, "recipe_for_disaster") == "flambeed")
check("the next course replaces the last",
      "flambeed" in a._room_monsters(p, "banquet_hall")
      and "agrith-na-na" not in a._room_monsters(p, "banquet_hall"))

# ---- Flambeed's heat: measured with and without water ---------------------------
dry = maxed("Dry")
m = a._new_monster("flambeed")
m["cur"] = 10 ** 9
random.seed(6)
for _ in range(300):
    with contextlib.redirect_stdout(io.StringIO()):
        a._resolve_player_hit(dry, m)
dmg_dry = 10 ** 9 - m["cur"]
wet = maxed("Wet")
wet.add("bucket of water")
m2 = a._new_monster("flambeed")
m2["cur"] = 10 ** 9
random.seed(6)
for _ in range(300):
    with contextlib.redirect_stdout(io.StringIO()):
        a._resolve_player_hit(wet, m2)
dmg_wet = 10 ** 9 - m2["cur"]
check("a bucket of water keeps your blade cool",
      dmg_wet > dmg_dry * 1.5, f"wet {dmg_wet} vs dry {dmg_dry}")

# the questing hero carries water and finishes the course
p.add("bucket of water")
won = kill(p, "flambeed")
check("Flambeed gutters out, gauntlets found",
      won and a._q(p, "recipe_for_disaster") == "karamel"
      and p.has("cooking gauntlets"))

# ---- cooking gauntlets steady the pan -------------------------------------------
chef = a.Player("Chef")
chef.members = True
chef.skills["cooking"] = a._XP_TABLE[52]     # swordfish needs 50; still burny
chef.location = "lumbridge_castle"


def burns(wear):
    random.seed(8)
    chef.inventory.clear()
    chef.add("raw swordfish", 200)
    if wear:
        chef.add("cooking gauntlets")
        chef.equip_item("cooking gauntlets", silent=True)
    else:
        chef.equipment["gloves"] = None
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(8):
            a.dispatch(chef, "cook raw swordfish 25")
    return chef.count("burnt swordfish")


bare_burns = burns(False)
glove_burns = burns(True)
check("cooking gauntlets burn less food", glove_burns < bare_burns,
      f"gloves {glove_burns} vs bare {bare_burns}")

# ---- Karamel, then the chef himself ----------------------------------------------
p.location = "banquet_hall"
won = kill(p, "karamel")
check("Karamel shatters, the chef steps through",
      won and a._q(p, "recipe_for_disaster") == "culinaromancer")
ck0 = p.skills["cooking"]
won = kill(p, "culinaromancer")
check("the Culinaromancer falls, quest complete",
      won and a._q(p, "recipe_for_disaster") == "complete")
check("barrows gloves + xp granted", p.has("barrows gloves")
      and p.skills["cooking"] - ck0 >= 25000)
check("the hall stands empty at last",
      a._room_monsters(p, "banquet_hall") == [])
a._check_achievements(p)
check("Gloved achievement", "gloved" in p.achievements)

# ---- barrows gloves are the new best-in-slot --------------------------------------
do(p, "equip barrows gloves")
check("barrows gloves equip", p.equipment.get("gloves") == "barrows gloves")
best = max(((i, d["equip"].get("str", 0)) for i, d in a.ITEMS.items()
            if d.get("equip", {}).get("slot") == "gloves"),
           key=lambda t: t[1])
check("barrows gloves are the strongest gloves",
      best[0] == "barrows gloves", str(best))

# ---- the goal ladder points at dessert --------------------------------------------
q = maxed("Ladder")
for k in a.ALL_QUESTS:
    q.quests[k] = "complete"
q.quests["recipe_for_disaster"] = "not_started"
q.barrows_loots = 3
q.add("rune defender")
q.kills = 500
q.bosses = ["obor", "tztok-jad", "general graardor", "kree'arra",
            "k'ril tsutsaroth", "commander zilyana", "kalphite queen",
            "dagannoth rex", "dagannoth prime", "dagannoth supreme",
            "the nightmare", "callisto", "venenatis", "vet'ion",
            "corporeal beast", "kraken", "cerberus", "abyssal sire",
            "grotesque guardians", "thermonuclear smoke devil", "vorkath",
            "crystalline hunllef"]
g = a._next_goal(q)
check("goal points at Recipe for Disaster", "RECIPE FOR DISASTER" in g, g)
q.quests["recipe_for_disaster"] = "complete"
g = a._next_goal(q)
check("then the Inferno", "INFERNO" in g, g)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
