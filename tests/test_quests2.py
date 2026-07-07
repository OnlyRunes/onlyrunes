"""End-to-end: The Knight's Sword, Prince Ali Rescue, journal hints."""
import io, sys, contextlib

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
    p.skills[s] = a._XP_TABLE[40]
p.hp = p.max_hp

# ===== THE KNIGHT'S SWORD ====================================================
p.location = "falador_square"
out = run(a.cmd_go, p, "castle")
check("castle reachable", p.location == "white_knights_castle", out)
out = run(a.cmd_talk, p, "")
check("squire starts quest", a._q(p, "knights_sword") == "started", out)

# thurgo wants pie
p.location = "mudskipper_point"
out = run(a.cmd_talk, p, "")
check("thurgo asks for pie", "REDBERRY PIE" in out, out)
check("still started", a._q(p, "knights_sword") == "started")
p.add("redberry pie")
out = run(a.cmd_talk, p, "")
check("pie -> stage forge", a._q(p, "knights_sword") == "forge", out)
check("pie consumed", not p.has("redberry pie"))

# mine blurite in the icy cavern
out = run(a.cmd_go, p, "cave")
check("icy cavern reachable", p.location == "icy_cavern", out)
for _ in range(20):                     # mining can miss; keep swinging
    out = run(a.cmd_mine, p, "blurite")
    if p.has("blurite ore"):
        break
check("blurite mined", p.has("blurite ore"), out)

# forge the sword
p.location = "mudskipper_point"
out = run(a.cmd_talk, p, "")
check("thurgo lists missing bars", "iron bars" in out, out)
p.add("iron bar", 2)
out = run(a.cmd_talk, p, "")
check("sword forged, stage sword", a._q(p, "knights_sword") == "sword", out)
check("has knight's sword", p.has("knight's sword"))
check("materials consumed", not p.has("iron bar") and not p.has("blurite ore"))

# hand it in — while EQUIPPED, to test the unequip path
run(p.equip_item, "knight's sword", True)
check("sword equips", p.equipment.get("weapon") == "knight's sword")
smith_before = p.skills["smithing"]
p.location = "white_knights_castle"
out = run(a.cmd_talk, p, "")
check("knight's sword complete", a._q(p, "knights_sword") == "complete", out)
check("12725 smithing xp", p.skills["smithing"] - smith_before >= 12725)
check("sword handed over", p.equipment.get("weapon") is None
      and not p.has("knight's sword"))

# ===== PRINCE ALI RESCUE =====================================================
p.location = "al_kharid_palace"
out = run(a.cmd_talk, p, "")
check("osman starts quest", a._q(p, "prince_ali") == "started", out)
out = run(a.cmd_talk, p, "")
check("osman lists needs", "balls of wool" in out, out)
p.add("ball of wool", 3); p.add("clay", 2); p.add("bronze bar")
out = run(a.cmd_talk, p, "")
check("stage rescue", a._q(p, "prince_ali") == "rescue", out)
check("got wig + key", p.has("blonde wig") and p.has("bronze key"))
check("materials consumed", not p.has("ball of wool") and not p.has("clay")
      and not p.has("bronze bar"))

# jail: search before/at the right place
p.location = "draynor_village"
out = run(a.cmd_go, p, "jail")
check("jail reachable", p.location == "draynor_jail", out)
out = run(a.cmd_search, p, "")
check("prince freed", a._q(p, "prince_ali") == "freed", out)
check("wig + key consumed", not p.has("blonde wig") and not p.has("bronze key"))

coins_before = p.count("coins")
p.location = "al_kharid_palace"
out = run(a.cmd_talk, p, "")
check("prince ali complete", a._q(p, "prince_ali") == "complete", out)
check("700 coins", p.count("coins") - coins_before == 700)

# toll gate now free
p.location = "al_kharid_gate"
c = p.count("coins")
out = run(a.cmd_go, p, "east")
check("toll gate free after quest", p.location == "al_kharid_square"
      and p.count("coins") == c, out)
check("free-passage message", "wave you through" in out, out)

# toll still charged for a fresh player
q = a.Player("Fresh")
q.location = "al_kharid_gate"
q.add("coins", 50)
out = run(a.cmd_go, q, "east")
check("toll still charged pre-quest", q.count("coins") == 65, out)  # 25+50-10

# ===== JOURNAL HINTS =========================================================
q.quests["dragon_slayer"] = "maps"
q.quests["knights_sword"] = "forge"
out = run(a.cmd_quests, q, "")
check("hint for dragon slayer stage", "Melzar's Maze" in out, out)
check("hint for knight's sword stage", "blurite" in out, out)
check("new quests in journal", "Prince Ali Rescue" in out)
check("dragon slayer listed last",
      out.rindex("Dragon Slayer") > out.rindex("Prince Ali Rescue"))

# ===== QP ECONOMY ============================================================
total = sum(a.QUEST_POINTS[k] for k in a.ALL_QUESTS if k != "dragon_slayer")
check("pre-DS quest points >= 27 (12-QP gate stays reachable)",
      total >= 27, str(total))

# serialize round-trip with new stages
p.quests["knights_sword"] = "forge"
p2 = a.deserialize(a.serialize(p))
check("round-trip keeps stage", p2.quests["knights_sword"] == "forge")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
