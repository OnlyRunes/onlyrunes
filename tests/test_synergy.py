"""Skilling synergies: campfires, ring enchanting, thieving stalls."""
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


p = a.Player("Tester")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[80]
p.hp = p.max_hp
p.members = True

# --- campfires enable cooking ---------------------------------------------------
p.location = "lumbridge_forest"          # no range here
p.add("raw trout", 2)
out = run(a.cmd_cook, p, "raw trout")
check("cooking blocked without fire", "fire" in out and p.has("raw trout"), out)
p.add("tinderbox")
p.add("logs", 2)
out = run(a.dispatch, p, "light logs")
check("fire lit", a._has_fire(p), out)
out = run(a.cmd_cook, p, "raw trout")
check("cooked on campfire", p.count("raw trout") <= 1, out)  # burns count too
p.fire["left"] = 1
run(a.dispatch, p, "look")               # tick burns it out
check("fire burns out", not a._has_fire(p))
out = run(a.cmd_cook, p, "raw trout")
check("no cooking after burnout", p.has("raw trout"), out)

# --- enchanting -------------------------------------------------------------------
out = run(a.cmd_enchant, p, "")
check("enchant lists rings", "ring of recoil" in out, out)
p.add("sapphire ring")
out = run(a.cmd_enchant, p, "sapphire ring")
check("enchant needs runes", "cosmic" in out and p.has("sapphire ring"), out)
p.add("cosmic rune", 10); p.add("water rune", 10); p.add("air rune", 10)
p.add("fire rune", 10); p.add("earth rune", 20)
out = run(a.cmd_enchant, p, "sapphire ring")
check("ring of recoil made", p.has("ring of recoil"), out)
check("base ring consumed", not p.has("sapphire ring"))
check("magic xp granted", "magic xp" in out, out)
p.add("emerald ring"); p.add("ruby ring"); p.add("diamond ring")
run(a.cmd_enchant, p, "emerald ring")
run(a.cmd_enchant, p, "ruby ring")
run(a.cmd_enchant, p, "diamond ring")
check("all four enchants", all(p.has(r) for r in
      ("ring of life", "ring of forging", "ring of wealth")))

# --- ring of recoil ------------------------------------------------------------------
run(p.equip_item, "ring of recoil", True)
q = a._new_monster("cow")
q["cur"] = 5
random.seed(0)
buf = ""
for _ in range(60):
    buf += run(a._resolve_monster_hit, p, q)
    if "recoil bites back" in buf:
        break
check("recoil bites back", "recoil bites back" in buf and q["cur"] < 5, buf[-150:])
q["cur"] = 1
buf = run(a._player_recoil, p, q, 5)
check("recoil can't kill", q["cur"] == 1)

# --- ring of life ---------------------------------------------------------------------
run(p.equip_item, "ring of life", True)
p.location = "wilderness_edge"
p.combat = a._new_monster("skeleton")
p.hp = max(1, p.max_hp // 10)
out = run(a.combat_action, p, "attack")
check("ring of life saves you", p.location == "lumbridge_castle"
      and p.combat is None, out[-200:])
check("ring consumed", p.equipment["ring"] is None)

# --- ring of forging ---------------------------------------------------------------------
p.add("ring of forging")
run(p.equip_item, "ring of forging", True)
p.location = "al_kharid_square"
p.add("iron ore", 10)
out = run(a.dispatch, p, "smelt iron 10")
check("forging never fails", p.count("iron bar") == 10, out)

# --- ring of wealth -------------------------------------------------------------------------
m_fake = {"drops": [("coins", 100, 100, 1.0)], "name": "test"}
p.equipment["ring"] = None
c0 = p.count("coins")
run(a._roll_drops, p, m_fake)
plain = p.count("coins") - c0
p.add("ring of wealth")
run(p.equip_item, "ring of wealth", True)
c0 = p.count("coins")
run(a._roll_drops, p, m_fake)
rich = p.count("coins") - c0
check("wealth boosts coins 25%", plain == 100 and rich == 125,
      f"{plain} vs {rich}")

# --- thieving stalls ---------------------------------------------------------------------------
p.location = "varrock_square"
random.seed(2)
for _ in range(15):                      # guards get lucky sometimes
    run(a.dispatch, p, "steal")
    if p.has("cup of tea"):
        break
check("tea stall stealable", p.has("cup of tea"))
p.location = "ardougne"
got = False
random.seed(5)
for _ in range(30):
    run(a.cmd_steal, p, "gem")
    if any(p.count(g) > 0 for g in a.GEM_CUT):
        got = True
        break
check("gem stall yields uncut gems", got)
out = run(a.dispatch, p, "steal silk 10")
check("batch stealing works", "actions)" in out, out)
q2 = a.Player("Low")
q2.members = True
q2.location = "ardougne"
out = run(a.cmd_steal, q2, "gem")
check("stall level gate", "level 75" in out, out)
q2.hp = 2
random.seed(1)
for _ in range(30):
    run(a.cmd_steal, q2, "baker")   # too low level? baker needs 20 — gate
q2.skills["thieving"] = a._XP_TABLE[21]
for _ in range(40):
    run(a.cmd_steal, q2, "baker")
check("guards never kill you", q2.hp >= 1, str(q2.hp))

# --- look + web wiring -----------------------------------------------------------------------------
out = run(a.cmd_look, p, "")
check("look lists stalls", "steal" in out and "gem stall" in out, out)
chips = json.loads(a.web_room_actions(p))
labels = [c["actions"][0]["label"] for c in chips if c["kind"] == "gather"]
check("web Steal chips", labels.count("Steal") == 3, str(labels))

# cup of tea is food
p.add("cup of tea")
p.hp = p.max_hp - 5
out = run(a.cmd_eat, p, "cup of tea")
check("tea heals", p.hp == p.max_hp - 2, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
