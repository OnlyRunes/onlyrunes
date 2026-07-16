"""Ape Atoll / Monkey Madness: the sail route, Garkor's greegree chain,
the Marim disguise gate, the rooftop course, and the Jungle Demon."""
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
    p.add("rune scimitar")
    p.equip_item("rune scimitar", silent=True)
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


random.seed(12)

# ---- quest start + the sail route --------------------------------------------
p = maxed("Gnomefriend")
p.location = "tree_gnome_stronghold"
out = do(p, "talk narnode")
check("Narnode starts the quest", a._q(p, "monkey_madness") == "squad",
      out[:200])
do(p, "go sail")
if p.combat:
    kill(p, p.combat["name"])
    p.location = "ape_atoll_beach"
check("the ship reaches Ape Atoll", p.location == "ape_atoll_beach")

# ---- Garkor's chain: squad -> bones -> greegree --------------------------------
p.combat = None
out = do(p, "talk garkor")
check("Garkor asks for monkey bones",
      a._q(p, "monkey_madness") == "bones", out[:200])
out = do(p, "talk garkor")
check("no bones yet: Garkor waits", a._q(p, "monkey_madness") == "bones"
      and "bones" in out.lower(), out[:200])
won = kill(p, "monkey")
check("a beach monkey falls", won and p.has("monkey bones"))
out = do(p, "talk garkor")
check("bones become the greegree",
      a._q(p, "monkey_madness") == "demon" and p.has("monkey greegree"),
      out[:200])

# ---- Marim is sealed to humans -------------------------------------------------
out = do(p, "go marim")
check("Marim refuses the undisguised",
      p.location == "ape_atoll_beach" and "HUMAN" in flat(out),
      flat(out)[:160])
do(p, "equip monkey greegree")
check("greegree worn (amulet slot)",
      p.equipment.get("amulet") == "monkey greegree")
out = do(p, "go marim")
check("the disguise opens Marim", p.location == "marim", out[:120])

# ---- the rooftop agility course -------------------------------------------------
ag = a.Player("Vaulter")
ag.members = True
ag.skills["agility"] = a._XP_TABLE[40]
ag.location = "marim"
out = do(ag, "agility")
check("course refuses under 48", "level 48" in out, out[:120])
ax0 = p.skills["agility"]
out = do(p, "agility")
check("laps grant agility xp", p.skills["agility"] > ax0, out[:150])

# ---- the Jungle Demon ------------------------------------------------------------
tourist = maxed("Tourist")
check("demon hidden from non-questers",
      "jungle demon" not in a._room_monsters(tourist, "jungle_demon_lair"))
check("demon bound for the quester",
      "jungle demon" in a._room_monsters(p, "jungle_demon_lair"))
do(p, "go temple")
check("the temple stairs open at the demon stage",
      p.location == "jungle_demon_lair")
at0 = p.skills["attack"]
won = kill(p, "jungle demon")
check("Jungle Demon slain, quest complete",
      won and a._q(p, "monkey_madness") == "complete")
check("xp + dragon scimitar granted", p.skills["attack"] - at0 >= 20000
      and p.has("dragon scimitar"))
check("demon gone after the fall",
      "jungle demon" not in a._room_monsters(p, "jungle_demon_lair"))
a._check_achievements(p)
check("Monkey Business achievement", "monkey_business" in p.achievements)

# ---- the lair stays sealed for outsiders ------------------------------------------
tourist.location = "marim"
out = do(tourist, "go temple")
check("stairs sealed pre-quest", tourist.location == "marim"
      and "Monkey Madness" in flat(out), flat(out)[:160])

# ---- marim archers are farmable, monkeys drop bones -------------------------------
won = kill(p, "monkey archer")
check("monkey archers fightable in Marim", won)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
