"""End-to-end playthrough of the Dragon Slayer quest (headless)."""
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
for s in a.SKILLS:                       # endgame stats so gear reqs pass
    p.skills[s] = a._XP_TABLE[80]
p.hp = p.max_hp

# --- 0. equip gate on a fresh player ---------------------------------------
p.add("rune platebody")
out = run(p.equip_item, "rune platebody")
check("rune platebody blocked pre-quest", "Dragon Slayer" in out, out)
p.take("rune platebody")

# --- 1. guildmaster refuses without QP --------------------------------------
p.location = "varrock_gate"
out = run(a.cmd_go, p, "guild")
check("guild room reachable", p.location == "champions_guild", out)
out = run(a.cmd_talk, p, "")
check("guildmaster refuses at 0 qp", "quest points" in out.lower(), out)
check("quest not started", a._q(p, "dragon_slayer") == "not_started")

# --- 2. earn 12 qp, start the quest -----------------------------------------
for q in ["romeo_juliet", "vampyre_slayer", "ernest_chicken"]:   # 5+3+4 = 12
    p.quests[q] = "complete"
check("quest_points == 12", a.quest_points(p) == 12, str(a.quest_points(p)))
out = run(a.cmd_talk, p, "")
check("quest starts at 12 qp", a._q(p, "dragon_slayer") == "started", out)
check("start banner", "Dragon Slayer" in out, out)

# --- 3. crandor locked before the ship --------------------------------------
p.location = "port_sarim"
out = run(a.cmd_go, p, "crandor")
check("crandor locked (go)", p.location == "port_sarim", out)
check("lock message mentions quest", "Dragon Slayer" in out, out)
out = run(a.cmd_travel, p, "crandor")
check("crandor locked (travel)", p.location == "port_sarim", out)

# --- 4. oziach: shield + stage maps -----------------------------------------
p.location = "oziach_hut"
out = run(a.cmd_talk, p, "")
check("stage -> maps", a._q(p, "dragon_slayer") == "maps", out)
check("got anti-dragon shield", p.has("anti-dragon shield"))

# --- 5. the three map pieces -------------------------------------------------
p.location = "melzars_maze"
out = run(a.cmd_search, p, "")
check("melzar piece", p.has("melzar's map piece"), out)
p.location = "draynor_manor"
out = run(a.cmd_search, p, "")
check("lozar piece", p.has("lozar's map piece"), out)
out = run(a._quest_on_kill, p, "goblin")
check("wormbrain piece", p.has("wormbrain's map piece"), out)

# --- 6. klarense: needs materials, then sells the ship ----------------------
p.location = "port_sarim"
out = run(a.cmd_talk, p, "")
check("klarense lists needs", "2,000 coins" in out, out)
check("still stage maps", a._q(p, "dragon_slayer") == "maps")
p.add("coins", 2500); p.add("steel bar", 2); p.add("hammer")
out = run(a.cmd_talk, p, "")
check("stage -> sail", a._q(p, "dragon_slayer") == "sail", out)
check("map pieces consumed", not any(p.has(i) for i in a.MAP_PIECES))
check("coins consumed", p.count("coins") == 525, str(p.count("coins")))  # 25 start
check("bars consumed", not p.has("steel bar"))

# --- 7. sail + slay Elvarg ---------------------------------------------------
out = run(a.cmd_go, p, "crandor")
check("crandor open at stage sail", p.location == "crandor", out)
out = run(a.cmd_go, p, "caldera")
check("reach elvarg's lair", p.location == "elvarg_lair", out)

# crandor is hostile — fight off any ambush before facing the dragon
while getattr(p, "combat", None) is not None and p.hp > 0:
    run(a.dispatch, p, "attack")

# gear up like a real endgame player and fight for real
p.hp = p.max_hp
for slot, item in a._best_gear_for_style("melee").items():
    p.add(item)
    run(p.equip_item, item, True)
run(p.equip_item, "anti-dragon shield", True)   # swap in the ADS
p.add("abyssal whip")                # the ADS evicts a 2h godsword —
run(p.equip_item, "abyssal whip", True)   # wield a 1h like a real player
p.add("swordfish", 28)
str_before, def_before = p.skills["strength"], p.skills["defence"]
random.seed(7)
out = run(a.dispatch, p, "fight elvarg")
n = 0
while getattr(p, "combat", None) is not None and p.hp > 0 and n < 400:
    if p.hp < 35 and p.has("swordfish"):
        out += run(a.dispatch, p, "eat swordfish")
    else:
        out += run(a.dispatch, p, "attack")
    n += 1
check("elvarg killed & quest complete", a._q(p, "dragon_slayer") == "complete",
      out[-600:])
check("dragonfire shield message seen",
      "anti-dragon shield deflects" in out or "dragonfire" not in out.lower(), "")
check("18650 str xp", p.skills["strength"] - str_before >= 18650)
check("18650 def xp", p.skills["defence"] - def_before >= 18650)

# --- 8. rewards unlocked ------------------------------------------------------
p.add("rune platebody")
out = run(p.equip_item, "rune platebody")
check("rune platebody wearable post-quest", p.equipment.get("body") == "rune platebody", out)
check("achievement earned", "crandor_saved" in a._earned_achievements(p))

# --- 9. dragonfire shield math ------------------------------------------------
out = run(lambda: check("shielded fire reduced", a._dragonfire_adjust(p, 12) == 4))
p.equipment["shield"] = None
out = run(lambda: check("unshielded fire boosted", a._dragonfire_adjust(p, 12) == 18))

# --- 10. serialize round-trip with mid-quest stage -----------------------------
p.quests["dragon_slayer"] = "maps"
data = a.serialize(p)
p2 = a.deserialize(data)
check("save round-trip keeps stage", p2.quests["dragon_slayer"] == "maps")

# --- 11. journal renders -------------------------------------------------------
out = run(a.cmd_quests, p2, "")
check("journal shows qp", "Quest points" in out, out)
check("journal lists Dragon Slayer", "Dragon Slayer" in out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
