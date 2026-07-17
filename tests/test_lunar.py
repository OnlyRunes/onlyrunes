"""The northern isles: Throne of Miscellania (+ the kingdom's passive
production), Lunar Diplomacy (fight yourself), the third spellbook, and
Vengeance's combat rebound."""
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


random.seed(21)

# ---- Throne of Miscellania ---------------------------------------------------
p = maxed("Regent")
p.location = "rellekka"
do(p, "go misc")
check("the ship reaches Miscellania", p.location == "miscellania")
out = do(p, "talk")
check("Vargas starts the quest",
      a._q(p, "throne_of_miscellania") == "favor", out[:200])
out = do(p, "kingdom")
check("no kingdom before the crown", "rule nothing" in out, out[:150])
p.add("maple logs", 10)
p.add("raw tuna", 10)
out = do(p, "talk")
check("favor won, crowned regent",
      a._q(p, "throne_of_miscellania") == "complete"
      and p.kingdom is not None, out[:200])
check("tribute consumed", not p.has("maple logs") and not p.has("raw tuna"))
a._check_achievements(p)
check("Regent achievement", "regent" in p.achievements)

# ---- the kingdom works the action clock ---------------------------------------
p.add("coins", 10000)
do(p, "kingdom deposit 6000")
check("coffers funded", p.kingdom["coffers"] == 6000)
do(p, "kingdom focus fish")
check("focus set", p.kingdom["focus"] == "fish")
out = do(p, "collect")
check("nothing to collect yet", "bare" in out, out[:150])
for _ in range(90):                     # the world turns while you act
    do(p, "stats")
tuna0 = p.count("raw tuna")
cof0 = p.kingdom["coffers"]
out = do(p, "collect")
check("subjects gathered while you adventured",
      p.count("raw tuna") > tuna0, out[:200])
check("wages drawn from the coffers", p.kingdom["coffers"] < cof0,
      f"{cof0} -> {p.kingdom['coffers']}")
out = do(p, "collect")
check("stockpile resets after collection", "bare" in out, out[:150])

# ---- kingdom survives the save ------------------------------------------------
q2 = a.player_from_json(a.player_to_json(p))
check("kingdom survives save/load", q2.kingdom is not None
      and q2.kingdom["focus"] == "fish")

# ---- Lunar Diplomacy ------------------------------------------------------------
p.location = "rellekka"
p.combat = None
do(p, "go moon")
check("the moon-ship reaches Lunar Isle", p.location == "lunar_isle")
out = do(p, "go dream")
check("the dream refuses the unprepared", p.location == "lunar_isle"
      and "Lunar Diplomacy" in flat(out), flat(out)[:160])
out = do(p, "pray altar")
check("altar indifferent pre-quest", p.spellbook == "standard"
      and "strangers" in out, out[-160:])
out = do(p, "talk")
check("Oneiromancer starts the trial",
      a._q(p, "lunar_diplomacy") == "dream", out[:200])
check("'me' waits in the dream",
      "me" in a._room_monsters(p, "dream_world"))
do(p, "go dream")
check("the dream now admits you", p.location == "dream_world")
mg0 = p.skills["magic"]
won = kill(p, "me")
check("you out-fight yourself", won
      and a._q(p, "lunar_diplomacy") == "complete")
check("magic xp + seal + astral runes granted",
      p.skills["magic"] - mg0 >= 15000 and p.has("seal of passage")
      and p.count("astral rune") >= 30)
a._check_achievements(p)
check("Dreamer achievement", "dreamer" in p.achievements)

# ---- the lunar spellbook ---------------------------------------------------------
p.location = "lunar_isle"
out = do(p, "cast vengeance")
check("lunar spells refused on the standard book",
      "lunar spellbook" in out and not getattr(p, "venge", False), out[:160])
out = do(p, "pray altar")
check("the altar opens the lunar book", p.spellbook == "lunar",
      out[:200])
p.add("astral rune", 30)
p.add("death rune", 10)
p.add("earth rune", 40)
p.add("cosmic rune", 10)
p.add("water rune", 10)
p.add("fire rune", 10)
p.add("law rune", 5)
out = do(p, "cast vengeance")
check("vengeance arms", getattr(p, "venge", False), out[:150])

# the rebound fires in combat (drop defence so the cow can land a blow)
p.location = "cow_field"
p.skills["defence"] = 0
saw_venge = False
for _ in range(20):
    if saw_venge or not getattr(p, "venge", False):
        break
    do(p, "fight cow")
    n = 0
    while p.combat is not None and n < 40:
        p.hp = p.max_hp
        out = do(p, "attack")
        if "rebounds" in out:
            saw_venge = True
        n += 1
check("vengeance rebounds in combat", saw_venge)
check("vengeance is spent after one rebound", not getattr(p, "venge", False))

# cure me + humidify
p.poison = 3
do(p, "cast cure me")
check("cure me clears poison", p.poison == 0)
w0 = p.count("waterskin")
do(p, "cast humidify")
check("humidify condenses waterskins", p.count("waterskin") == w0 + 4)

# moonclan teleport
p.location = "cow_field"
do(p, "cast moonclan teleport")
check("moonclan teleport returns home", p.location == "lunar_isle")

# altar toggles back
do(p, "pray altar")
check("altar swaps back to standard", p.spellbook == "standard")

# ---- the moonclan store stocks the runes ------------------------------------------
p.add("coins", 5000)
out = do(p, "buy astral rune 10")
check("moonclan shop sells astral runes", p.count("astral rune") >= 10,
      out[:150])

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
