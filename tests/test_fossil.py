"""Fossil Island / Dragon Slayer II / Vorkath: the quest chain, the Ungael
gate, dragon-bane gear, and the dragonfire ward."""
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


def maxed(name):
    p = a.Player(name)
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.quests["dragon_slayer"] = "complete"   # lance req is quest-free here
    p.add("dragon hunter lance")
    p.equip_item("dragon hunter lance", silent=True)   # real damage vs dragons
    p.style = "melee"
    p.attack_type = "stab"
    p.hp = p.max_hp
    return p


def flat(s):
    return " ".join(s.split())              # collapse word-wrap for matching


random.seed(5)

# ---- DS2 is gated behind Dragon Slayer --------------------------------------
p = maxed("Novice")
p.quests.pop("dragon_slayer", None)          # undo the helper's completion
p.location = "fossil_island"
out = do(p, "talk")
check("DS2 refused before Dragon Slayer", a._q(p, "dragon_slayer_2")
      == "not_started" and "DRAGON SLAYER" in flat(out), flat(out)[:200])

# ---- start DS2 --------------------------------------------------------------
p.quests["dragon_slayer"] = "complete"
out = do(p, "talk")
check("DS2 starts once Dragon Slayer is done",
      a._q(p, "dragon_slayer_2") == "relics", out[:200])

# ---- metal dragons drop relics on the relic stage ---------------------------
p.location = "lithkren_vault"
for mon in ("mithril dragon", "adamant dragon", "rune dragon"):
    do(p, f"fight {mon}")
    n = 0
    while p.combat is not None and n < 200:
        p.hp = p.max_hp
        do(p, "attack")
        n += 1
check("three metal dragon kills yield three relics",
      p.count("dragonkin relic") == 3, f"got {p.count('dragonkin relic')}")

# extra kills don't over-grant
do(p, "fight mithril dragon")
n = 0
while p.combat is not None and n < 200:
    p.hp = p.max_hp
    do(p, "attack")
    n += 1
check("relics cap at three", p.count("dragonkin relic") == 3)

# ---- hand in relics -> galvek stage -----------------------------------------
p.location = "fossil_island"
out = do(p, "talk")
check("relics advance the quest to galvek",
      a._q(p, "dragon_slayer_2") == "galvek"
      and p.count("dragonkin relic") == 0, out[:200])

# ---- Galvek only appears on the shore during the galvek stage ---------------
check("galvek breaches at ungael during the quest",
      "galvek" in a._room_monsters(p, "ungael_shore"))
tourist = maxed("Tourist")
check("galvek hidden from non-questers",
      "galvek" not in a._room_monsters(tourist, "ungael_shore"))

# ---- Vorkath's crater is sealed until DS2 is complete -----------------------
p.location = "ungael_shore"
out = do(p, "go crater")
check("crater sealed before DS2 complete",
      p.location == "ungael_shore" and "DRAGON SLAYER II" in flat(out),
      flat(out)[:200])

# ---- kill Galvek -> quest complete + lance reward ---------------------------
p.location = "ungael_shore"
do(p, "fight galvek")
n = 0
while p.combat is not None and n < 300:
    p.hp = p.max_hp
    do(p, "attack")
    n += 1
check("Galvek falls and completes DS2",
      a._q(p, "dragon_slayer_2") == "complete", a._q(p, "dragon_slayer_2"))
check("DS2 awards the dragon hunter lance", p.has("dragon hunter lance"))
check("DS2 is worth 5 QP", a.QUEST_POINTS["dragon_slayer_2"] == 5)
a._check_achievements(p)
check("Dragonkin's Bane achievement", "dragonkin_bane" in
      getattr(p, "achievements", []))

# ---- crater opens; Vorkath is fightable -------------------------------------
out = do(p, "go crater")
check("crater opens after DS2", p.location == "vorkath_crater", out[:150])
p.hp = p.max_hp
do(p, "fight vorkath")
check("Vorkath is a boss fight", p.combat is not None
      and a.MONSTERS["vorkath"].get("boss"))
saw_spawn = False
n = 0
while p.combat is not None and n < 400:
    p.hp = p.max_hp
    out = do(p, "attack")
    if "ZOMBIFIED SPAWN" in out:
        saw_spawn = True
    n += 1
check("Vorkath slain", "vorkath" in getattr(p, "bosses", []))
check("the zombified spawn mechanic fired", saw_spawn)
a._check_achievements(p)
check("Vorkath achievement", "vorkath" in getattr(p, "achievements", []))

# ---- dragon-bane: the lance hits a dragon harder than a non-dragon ----------
random.seed(1)
db = maxed("Baner")
db.add("dragon hunter lance")
db.equip_item("dragon hunter lance", silent=True)
db.style = "melee"
db.attack_type = "stab"


def total_dmg(seed, dragon_flag):
    random.seed(seed)
    a.MONSTERS["rune dragon"]["dragon"] = dragon_flag
    tot = 0
    for _ in range(400):
        m = a._new_monster("rune dragon")
        m["cur"] = 10 ** 9
        with contextlib.redirect_stdout(io.StringIO()):
            a._resolve_player_hit(db, m)
        tot += 10 ** 9 - m["cur"]
    return tot


with_bane = total_dmg(3, True)
without = total_dmg(3, False)
a.MONSTERS["rune dragon"]["dragon"] = True      # restore
check("dragon-bane boosts damage vs dragons", with_bane > without,
      f"{with_bane} vs {without}")

# ---- dragonfire ward soaks flames -------------------------------------------
w = maxed("Warded")
w.equipment["shield"] = "dragonfire ward"
with contextlib.redirect_stdout(io.StringIO()):
    soaked = a._dragonfire_adjust(w, 30)
w.equipment["shield"] = None
with contextlib.redirect_stdout(io.StringIO()):
    raw = a._dragonfire_adjust(w, 30)
check("dragonfire ward soaks flames like the anti-dragon shield",
      soaked == 10 and raw == 45, f"soaked {soaked}, raw {raw}")

# ---- gear requirements ------------------------------------------------------
low = a.Player("Weak")
low.members = True
low.add("dragon hunter lance")
out = do(low, "equip dragon hunter lance")
check("lance needs attack 78", low.equipment.get("weapon")
      != "dragon hunter lance" and "attack level 78" in out, out[:120])

# ---- travel hub + region ----------------------------------------------------
check("fossil island is a travel hub",
      a.TRAVEL_HUBS.get("fossil island") == "fossil_island")
check("phasmatys sails to fossil island",
      a.ROOMS["port_phasmatys"]["exits"].get("fossil") == "fossil_island")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
