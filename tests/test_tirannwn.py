"""Tirannwn: the Underground Pass route, Song of the Elves, the sealed
city, the Gauntlet's Hunllef, Zalcano's pickaxe rule, crystal crafting."""
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


random.seed(9)

# ---- the route: Ardougne -> Underground Pass -> Isafdar ----------------------
p = maxed("Elfriend")
p.location = "ardougne"
out = do(p, "go pass")
check("the pass opens west of Ardougne", p.location == "underground_pass",
      out[:120])
p.combat = None
p.location = "underground_pass"
do(p, "go west")
if p.combat:                       # hostile corridor may ambush
    kill(p, p.combat["name"])
    p.location = "isafdar"
check("the pass leads to Isafdar", p.location == "isafdar")

# ---- the city is sealed before the quest --------------------------------------
p.combat = None
p.location = "prifddinas_gates"
out = do(p, "go city")
check("Prifddinas sealed pre-quest", p.location == "prifddinas_gates"
      and "Song of the Elves" in flat(out), flat(out)[:160])
tr = a.Player("Tourist")
tr.members = True
out = do(tr, "travel prifddinas")
check("travel refuses the sealed city too",
      tr.location != "prifddinas", flat(out)[:160])

# ---- Song of the Elves ---------------------------------------------------------
check("fragment hidden before the quest",
      "fragment of seren" not in a._room_monsters(p, "prifddinas_gates"))
p.location = "isafdar"
p.combat = None
out = do(p, "talk")
check("Eluned starts the quest",
      a._q(p, "song_of_the_elves") == "seren", out[:200])
check("the Fragment now stands vigil",
      "fragment of seren" in a._room_monsters(p, "prifddinas_gates"))
p.location = "prifddinas_gates"
ag0 = p.skills["agility"]
won = kill(p, "fragment of seren")
check("Fragment of Seren slain", won and
      a._q(p, "song_of_the_elves") == "complete")
check("quest xp + shards granted", p.skills["agility"] - ag0 >= 20000
      and p.count("crystal shard") >= 20)
check("fragment despawns after the fall",
      "fragment of seren" not in a._room_monsters(p, "prifddinas_gates"))
a._check_achievements(p)
check("Crystal Singer achievement", "crystal_singer" in p.achievements)

# ---- the city opens ------------------------------------------------------------
out = do(p, "go city")
check("Prifddinas opens after the quest", p.location == "prifddinas",
      out[:120])
check("the city banks and trades",
      a.ROOMS["prifddinas"].get("bank") and a.ROOMS["prifddinas"].get("ge"))

# ---- the Gauntlet ---------------------------------------------------------------
do(p, "go gauntlet")
check("gauntlet reachable", p.location == "the_gauntlet")
saw_swap, saw_nado = False, False
do(p, "fight crystalline hunllef")
n = 0
while p.combat is not None and n < 250:
    p.hp = p.max_hp
    out = do(p, "attack")
    if "incoming" in out:
        saw_swap = True
    if "tornadoes" in out:
        saw_nado = True
    n += 1
check("Hunllef slain", "crystalline hunllef" in p.bosses)
check("style-swap mechanic fired", saw_swap)
check("tornado mechanic fired", saw_nado)
a._check_achievements(p)
check("Gauntleted achievement", "gauntleted" in p.achievements)

# ---- Zalcano: the pickaxe rule ---------------------------------------------------
p.location = "prifddinas"
p.combat = None
do(p, "go mine")
check("zalcano's mine reachable", p.location == "zalcano_chamber")

# without a pickaxe the stone shrugs steel off
bare = maxed("Bare")
for it in list(bare.inventory):
    if a.ITEMS.get(it, {}).get("tool") == "pickaxe":
        bare.take(it, bare.count(it))
m = a._new_monster("zalcano")
m["cur"] = 10 ** 9
random.seed(4)
tot_bare = 0
for _ in range(300):
    with contextlib.redirect_stdout(io.StringIO()):
        a._resolve_player_hit(bare, m)
tot_bare = 10 ** 9 - m["cur"]
m2 = a._new_monster("zalcano")
m2["cur"] = 10 ** 9
random.seed(4)
for _ in range(300):
    with contextlib.redirect_stdout(io.StringIO()):
        a._resolve_player_hit(p, m2)          # p carries a bronze pickaxe
tot_pick = 10 ** 9 - m2["cur"]
check("pickaxe cracks Zalcano harder", tot_pick > tot_bare * 1.5,
      f"pick {tot_pick} vs bare {tot_bare}")

# the kill pays mining xp
mx0 = p.skills["mining"]
won = kill(p, "zalcano")
check("Zalcano slain", won and "zalcano" in p.bosses)
check("kill pays mining xp", p.skills["mining"] - mx0 >= 1500)
a._check_achievements(p)
check("Stonebreaker achievement", "stonebreaker" in p.achievements)

# ---- crystal crafting -------------------------------------------------------------
c = a.Player("Singer")
c.members = True
c.skills["crafting"] = a._XP_TABLE[85]
c.skills["attack"] = a._XP_TABLE[80]
c.skills["defence"] = a._XP_TABLE[75]
c.add("enhanced crystal weapon seed")
c.add("crystal armour seed", 2)
c.add("needle")
c.add("thread", 3)          # thread is consumed per craft
out = do(c, "craft blade of saeldor")
check("blade of saeldor crafted", c.has("blade of saeldor"), out[:150])
do(c, "craft crystal body")
do(c, "craft crystal legs")
check("crystal armour crafted", c.has("crystal body")
      and c.has("crystal legs"))
out = do(c, "equip blade of saeldor")
check("blade equips at 80 attack",
      c.equipment.get("weapon") == "blade of saeldor", out[:120])

# ---- goal rungs + hub --------------------------------------------------------------
check("prifddinas is a travel hub",
      a.TRAVEL_HUBS.get("prifddinas") == "prifddinas")
q = maxed("Ladder")
for k in a.ALL_QUESTS:
    q.quests[k] = "complete"
q.quests["song_of_the_elves"] = "not_started"
q.barrows_loots = 3
q.add("rune defender")
q.kills = 500
q.slayer_points = 5
q.bosses = ["obor", "tztok-jad", "general graardor", "kree'arra",
            "k'ril tsutsaroth", "commander zilyana", "kalphite queen",
            "dagannoth rex", "dagannoth prime", "dagannoth supreme",
            "the nightmare", "callisto", "venenatis", "vet'ion",
            "corporeal beast", "kraken", "cerberus", "abyssal sire",
            "grotesque guardians", "thermonuclear smoke devil", "vorkath"]
g = a._next_goal(q)
check("goal points at Song of the Elves", "SONG OF THE ELVES" in g, g)
q.quests["song_of_the_elves"] = "complete"
g = a._next_goal(q)
check("then the Gauntlet", "GAUNTLET" in g, g)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
