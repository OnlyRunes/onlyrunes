"""Skilling expansion: gems/jewellery, RC altars, yew/magic + fletching, capes."""
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


p = a.Player("Tester")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[80]
p.hp = p.max_hp
p.members = True

# --- mining strikes gems ------------------------------------------------------
p.location = "al_kharid_mine"
random.seed(1)
found = False
for _ in range(300):
    run(a.cmd_mine, p, "iron")
    if any(p.has(g) for g in a.GEM_CUT):
        found = True
        break
check("mining strikes gems", found)

# --- cutting -------------------------------------------------------------------
p.add("uncut sapphire")
out = run(a.dispatch, p, "cut sapphire")
check("cut needs chisel", "chisel" in out, out)
p.add("chisel")
out = run(a.dispatch, p, "cut sapphire")
check("gem cut", p.has("sapphire"), out)
check("crafting xp for cut", "crafting xp" in out, out)
p.add("uncut ruby", 3)
out = run(a.dispatch, p, "cut ruby 3")
check("batch gem cutting", p.count("ruby") == 3, out)

# --- jewellery -------------------------------------------------------------------
out = run(a.cmd_craft, p, "sapphire amulet")
check("jewellery needs furnace", "furnace" in out, out)
p.location = "al_kharid_square"      # has furnace
out = run(a.cmd_craft, p, "sapphire amulet")
check("jewellery needs gold bar", "gold bar" in out, out)
p.add("gold bar", 5)
out = run(a.cmd_craft, p, "sapphire amulet")
check("sapphire amulet crafted", p.has("sapphire amulet"), out)
out = run(a.cmd_craft, p, "gold ring")
check("gold ring crafted (no gem)", p.has("gold ring"), out)
out = run(a.dispatch, p, "craft ruby ring 5")   # only 3 rubies/gold bars left
check("batch jewellery stops when out", p.count("ruby ring") == 3
      and ("need a ruby" in out or "need a gold bar" in out),
      f"rings={p.count('ruby ring')} {out[-200:]}")
run(p.equip_item, "sapphire amulet", True)
check("amulet wearable", p.equipment["amulet"] == "sapphire amulet")
check("amulet carries stats",
      a.ITEMS["sapphire amulet"]["equip"]["amagic"] == 2)

# --- runecrafting altars ------------------------------------------------------------
p.location = "al_kharid_square"
out = run(a.cmd_go, p, "altar")
check("fire altar reachable", p.location == "fire_altar", out)
p.add("rune essence", 10)
out = run(a.cmd_craftrune, p, "")
check("fire runes crafted", p.count("fire rune") >= 10, out)
check("mastery multiplier fired", "x3" in out or "x2" in out, out)
for room, rune in [("mind_altar", "mind rune"), ("water_altar", "water rune"),
                   ("earth_altar", "earth rune"), ("body_altar", "body rune")]:
    p.location = room
    p.add("rune essence", 2)
    out = run(a.cmd_craftrune, p, "")
    check(f"{rune} craftable", p.has(rune), out)

# altars are connected both ways
for hub, ex, altar in [("monastery", "altar", "mind_altar"),
                       ("swamp", "altar", "water_altar"),
                       ("varrock_east_bank", "altar", "earth_altar"),
                       ("barbarian_village", "altar", "body_altar")]:
    ok = a.ROOMS[hub]["exits"].get(ex) == altar and \
         a.ROOMS[altar]["exits"].get("out") == hub
    check(f"{altar} wired", ok)

# --- yew & magic trees + fletching ---------------------------------------------------
p.location = "lumbridge_church"
p.add("bronze axe")
random.seed(3)
got = False
for _ in range(40):
    run(a.cmd_chop, p, "yew")
    if p.has("yew logs"):
        got = True
        break
check("yew chopped at the church", got)
p.location = "catherby"
random.seed(3)
got = False
for _ in range(60):
    run(a.cmd_chop, p, "magic")
    if p.has("magic logs"):
        got = True
        break
check("magic tree chopped at catherby", got)
p.add("knife")
p.add("magic logs", 1)
out = run(a.cmd_fletch, p, "magic shortbow (u)")
check("magic shortbow fletched (u)", p.has("magic shortbow (u)"), out)
p.add("bow string")
out = run(a.cmd_fletch, p, "magic shortbow")
check("magic shortbow strung", p.has("magic shortbow"), out)
check("fletched bow has the spec", "magic shortbow" in a.SPECIAL_ATTACKS)

# --- skill capes ----------------------------------------------------------------------
p.location = "draynor_village"
out = run(a.cmd_skillcape, p, "cooking")
check("cape refused below 99", "level 99" in out, out)
p.skills["cooking"] = a._XP_TABLE[99]
out = run(a.cmd_skillcape, p, "cooking")
check("cape needs coins", "99,000" in out, out)
p.add("coins", 200000)
out = run(a.cmd_skillcape, p, "cooking")
check("cooking cape bought", p.has("cooking cape"), out)
run(p.equip_item, "cooking cape", True)
check("cape wearable at 99", p.equipment["cape"] == "cooking cape")
check("cape has +9 defences", p.equip_bonus("dslash") >= 9)
q = a.Player("Noob")
q.add("cooking cape")
out = run(q.equip_item, "cooking cape")
check("cape blocked below 99", q.equipment["cape"] is None, out)
out = run(a.cmd_talk, p, "wise")
check("wise old man lists mastery", "cooking cape" in out, out)
p.location = "lumbridge_castle"
out = run(a.cmd_skillcape, p, "cooking")
check("skillcape needs draynor", "Draynor" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
