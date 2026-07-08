"""Every one of the 23 skills, exercised end-to-end: the canonical training
action runs, grants XP, and is reachable from level 1 (no dead-ends like the
old herblore / fletching unstartable bugs). RNG gathers loop with a seed."""
import io, sys, contextlib, random, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".."))
import adventure as a

FAILS = []
_CHECKED = []      # first word of every check label (for the coverage guard)


def check(label, cond, extra=""):
    _CHECKED.append(label.split()[0])
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


def newp(name, **skills):
    p = a.Player(name)
    p.members = True
    for s, lv in skills.items():
        p.skills[s] = a._XP_TABLE[lv]
    p.hp = p.max_hp
    return p


def xp(p, s):
    return p.skills[s]


def trained(skill, p, cmd, tries=1, setup=None):
    """Run cmd (up to `tries` for RNG) from level 1 unless setup raised it;
    pass if the target skill gained xp."""
    if setup:
        setup(p)
    x = xp(p, skill)
    for _ in range(tries):
        do(p, cmd)
        if xp(p, skill) > x:
            break
    check(f"{skill} trains ({cmd})", xp(p, skill) > x,
          f"+{xp(p, skill) - x} xp")


random.seed(11)

# ---- gathering --------------------------------------------------------------
p = newp("wc")
p.location = next(r for r, d in a.ROOMS.items() if "tree" in d.get("trees", []))
trained("woodcutting", p, "chop tree", tries=40)

p = newp("mine")
p.location = next(r for r, d in a.ROOMS.items() if "copper" in d.get("rocks", []))
trained("mining", p, "mine copper", tries=40)

p = newp("fish")
p.location = next(r for r, d in a.ROOMS.items() if d.get("fish_tools"))
trained("fishing", p, "fish", tries=40)

# hunter: needs a trap item + a real creature name
p = newp("hunt")
p.location = "feldip_hills"
p.add("bird snare", 2)
x = xp(p, "hunter")
do(p, "settrap crimson swift")
for _ in range(40):
    do(p, "look")
    do(p, "checktraps")
    if xp(p, "hunter") > x:
        break
check("hunter trains (trap crimson swift)", xp(p, "hunter") > x,
      f"+{xp(p, 'hunter') - x} xp")

# farming: xp on planting
p = newp("farm")
p.location = "lumbridge_farm"
p.add("potato seed", 2)
trained("farming", p, "plant potato seed")

# ---- production -------------------------------------------------------------
p = newp("cook")
p.location = "lumbridge_castle"
p.add("raw shrimp", 12)
trained("cooking", p, "cook raw shrimp 12")   # batch dodges single-attempt burn

p = newp("fm")
p.location = "lumbridge_forest"
p.add("logs", 5)
p.add("tinderbox")
trained("firemaking", p, "light logs")

p = newp("smelt")
p.location = "al_kharid_square"
p.add("copper ore", 2)
p.add("tin ore", 2)
trained("smithing", p, "smelt bronze bar")

p = newp("smith", smithing=5)
p.location = "varrock_west_bank"
p.add("bronze bar", 3)
p.add("hammer")
trained("smithing", p, "smith bronze dagger")   # (again — the anvil path)

p = newp("craft")
p.location = "lumbridge_castle"
p.add("flax", 3)
trained("crafting", p, "spin flax")

p = newp("herb")
p.add("grimy guam", 3)
trained("herblore", p, "clean grimy guam")

p = newp("fletch")
p.add("knife")
p.add("logs", 3)
trained("fletching", p, "fletch shortbow (u)")

p = newp("rc")
p.location = "air_altar"
p.add("rune essence", 5)
trained("runecrafting", p, "craftrune air")

p = newp("con")
p.location = "your_house"
p.add("plank", 6)
p.add("saw")
p.add("hammer")
trained("construction", p, "build crude chair")

# ---- support ---------------------------------------------------------------
p = newp("agi")
p.location = "agility_course"
trained("agility", p, "agility", tries=20)

p = newp("thief")
p.location = "varrock_square"       # has a level-1 'man'
trained("thieving", p, "pickpocket man", tries=40)

p = newp("pray")
p.add("bones", 3)
trained("prayer", p, "bury bones")

# ---- combat ----------------------------------------------------------------
def fight_to_death(p, mon, focus=None):
    if focus:
        do(p, f"train {focus}")
    do(p, f"fight {mon}")
    n = 0
    while p.combat is not None and n < 100:
        p.hp = p.max_hp
        do(p, "attack")
        n += 1


p = newp("melee", attack=20, strength=20, defence=20)
p.location = "cow_field"
xa, xh = xp(p, "attack"), xp(p, "hitpoints")
fight_to_death(p, "cow", focus="attack")
check("attack trains (melee)", xp(p, "attack") > xa, f"+{xp(p, 'attack') - xa}")
check("hitpoints trains (combat)", xp(p, "hitpoints") > xh,
      f"+{xp(p, 'hitpoints') - xh}")

p = newp("str", attack=20, strength=20, defence=20)
p.location = "cow_field"
xs = xp(p, "strength")
fight_to_death(p, "cow", focus="strength")
check("strength trains (train strength)", xp(p, "strength") > xs,
      f"+{xp(p, 'strength') - xs}")

p = newp("def", attack=20, strength=20, defence=20)
p.location = "cow_field"
xd = xp(p, "defence")
fight_to_death(p, "cow", focus="defence")
check("defence trains (train defence)", xp(p, "defence") > xd,
      f"+{xp(p, 'defence') - xd}")

p = newp("range", ranged=20)
p.location = "cow_field"
p.add("shortbow")
p.add("bronze arrow", 100)
do(p, "equip shortbow")
do(p, "equip bronze arrow")
do(p, "style ranged")
xr = xp(p, "ranged")
fight_to_death(p, "cow")
check("ranged trains", xp(p, "ranged") > xr, f"+{xp(p, 'ranged') - xr}")

p = newp("mage", magic=20)
p.location = "cow_field"
p.add("air rune", 60)
p.add("mind rune", 60)
do(p, "autocast wind strike")
xm = xp(p, "magic")
do(p, "fight cow")
n = 0
while p.combat is not None and n < 100:
    p.hp = p.max_hp
    out = do(p, "attack")
    if "out of" in out.lower() and "rune" in out.lower():
        break
    n += 1
check("magic trains (autocast)", xp(p, "magic") > xm, f"+{xp(p, 'magic') - xm}")

# slayer: take a task, kill the assigned monster
p = newp("slay", attack=60, strength=60, defence=60, slayer=10)
p.location = "edgeville"
xsl = xp(p, "slayer")
do(p, "talk vannaka")
task = getattr(p, "slayer_task", None)
if task:
    mon = task["monster"]
    spot = next((r for r, d in a.ROOMS.items()
                 if mon in d.get("monsters", [])), None)
    if spot:
        p.location = spot
        for _ in range(8):
            if p.combat is None:
                do(p, f"fight {mon}")
            n = 0
            while p.combat is not None and n < 100:
                p.hp = p.max_hp
                do(p, "attack")
                n += 1
            if xp(p, "slayer") > xsl:
                break
check("slayer trains (on-task kill)", xp(p, "slayer") > xsl,
      f"+{xp(p, 'slayer') - xsl} xp; task={task['monster'] if task else None}")

# ---- coverage guard: every skill in SKILLS was exercised above -------------
missing = [s for s in a.SKILLS if s not in _CHECKED]
check("all 23 skills exercised", not missing, str(missing))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
