"""Karamja completion: jungle wiring, Saniboch's fee, the gem mine, red
d'hide, dragonfire breath, tokkul trading, and the INFERNO end to end."""
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


def do(p, cmd):
    return run(a.dispatch, p, cmd)


def settle(pl):
    guard = 0
    while getattr(pl, "combat", None) is not None and pl.hp > 0 and guard < 300:
        guard += 1
        run(a.dispatch, pl, "attack")


def fresh_max(style="melee"):
    p = a.Player("T")
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.hp = p.max_hp
    p.prayer_points = p.prayer_max()
    for slot, item in a._best_gear_for_style(style).items():
        p.add(item)
        run(p.equip_item, item, True)
    if style == "ranged" and p.equipment.get("ammo"):
        p.add(p.equipment["ammo"], 20000)
    run(a.dispatch, p, {"melee": "style slash", "ranged": "style ranged",
                        "magic": "style magic"}[style])
    p.add("shark", 1000)
    return p


random.seed(45)

print("=== 1. wiring ====================================================")
for rm in ("tai_bwo_wannai", "shilo_village", "brimhaven_dungeon",
           "dragon_forge", "mor_ul_rek", "the_inferno"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} in Karamja", a.REGIONS.get(rm) == "Karamja")
check("brimhaven roads", a.ROOMS["brimhaven"]["exits"].get("south")
      == "tai_bwo_wannai"
      and a.ROOMS["brimhaven"]["exits"].get("dungeon") == "brimhaven_dungeon")
check("volcano hides the city",
      a.ROOMS["karamja_volcano"]["exits"].get("city") == "mor_ul_rek")
check("shilo travel hub", a.TRAVEL_HUBS.get("shilo") == "shilo_village")
check("tai bwo sells antipoison", "antipoison" in a.SHOPS["tai_bwo"])

print("=== 2. saniboch's fee ============================================")
poor = a.Player("Poor")
poor.members = True
poor.location = "brimhaven"
poor.take("coins", poor.count("coins"))
out = run(a.cmd_go, poor, "dungeon")
check("no coins, no dungeon", poor.location == "brimhaven"
      and "875" in out, out)
rich = fresh_max()
rich.location = "brimhaven"
rich.add("coins", 1000)
c0 = rich.count("coins")
out = run(a.cmd_go, rich, "dungeon")
check("875 coins charged on entry", rich.location == "brimhaven_dungeon"
      and rich.count("coins") == c0 - 875, out)
settle(rich)

print("=== 3. the gem mine ==============================================")
pg = fresh_max()
pg.location = "shilo_village"
gems = 0
for _ in range(40):
    out = run(a.cmd_mine, pg, "gem rock")
    if "uncut" in out:
        gems += 1
check("gem rock pays only in gems", gems > 10
      and any(pg.has(g) for g in a.GEM_CUT), str(gems))

print("=== 4. red d'hide line ===========================================")
pr = fresh_max()
pr.add("red dragonhide", 3)
pr.add("coins", 1000)
pr.location = "al_kharid_square"          # tanner
out = run(a.cmd_tan, pr, "red dragonhide")
check("red hide tans", pr.has("red dragon leather"), out)
pr.add("red dragon leather", 5)
pr.add("needle")
pr.add("thread", 10)
out = run(a.cmd_craft, pr, "red d'hide body")
check("red d'hide body crafted at 77", pr.has("red d'hide body"), out)
check("red beats green at range",
      a.ITEMS["red d'hide body"]["equip"]["drange"]
      > a.ITEMS["green d'hide body"]["equip"]["drange"])

print("=== 5. dragonfire breath =========================================")
steel = dict(a.MONSTERS["steel dragon"])
steel["name"] = "steel dragon"
steel["cur"] = steel["hp"]
orig_random = a.random.random
a.random.random = lambda: 0.1             # breath branch always fires
pd = fresh_max()
pd.hp = pd.max_hp
naked_dmg = 0
for _ in range(120):
    pd.hp = pd.max_hp
    run(a._resolve_monster_hit, pd, steel)
    naked_dmg += pd.max_hp - pd.hp
run(pd.equip_item, "anti-dragon shield", True) if "anti-dragon shield" in pd.inventory else pd.add("anti-dragon shield")
run(pd.equip_item, "anti-dragon shield", True)
shielded_dmg = 0
for _ in range(120):
    pd.hp = pd.max_hp
    out = run(a._resolve_monster_hit, pd, steel)
    shielded_dmg += pd.max_hp - pd.hp
a.random.random = orig_random
check("anti-dragon shield tames the flames",
      shielded_dmg < naked_dmg * 0.45,
      f"naked={naked_dmg} shielded={shielded_dmg}")

print("=== 6. tribesman poison ==========================================")
pt = fresh_max()
pt.poison = 0
a.random.random = lambda: 0.1
run(a.MONSTER_EFFECTS["tribesman"], pt, a.MONSTERS["tribesman"], 4)
a.random.random = orig_random
check("jungle spears poison", pt.poison > 0)
pt.poison = 0

print("=== 7. tokkul trading ============================================")
pk = fresh_max()
pk.location = "mor_ul_rek"
out = run(a.cmd_redeem, pk, "")
check("armoury lists in tokkul", "obsidian cape" in out
      and "tokkul" in out, out)
out = run(a.cmd_redeem, pk, "obsidian cape")
check("poor jalyt refused", not pk.has("obsidian cape"), out)
pk.add("tokkul", 9000)
out = run(a.cmd_redeem, pk, "obsidian cape")
check("9,000 tokkul buys the cape", pk.has("obsidian cape")
      and pk.count("tokkul") == 0, out)
pk.location = "lumbridge_castle"
out = run(a.cmd_redeem, pk, "obsidian cape")
check("tokkul only spends in the city", "Mor Ul Rek" in out, out)

print("=== 8. the inferno gate ==========================================")
pi = fresh_max("ranged")
pi.equipment["cape"] = None          # BIS kit includes the infernal cape now
pi.location = "mor_ul_rek"
out = run(a.cmd_go, pi, "inferno")
check("no fire cape, no furnace", pi.location == "mor_ul_rek"
      and "fire cape" in out, out)
pi.add("fire cape")
run(pi.equip_item, "fire cape", True)
run(a.cmd_go, pi, "inferno")
check("fire cape opens the crack", pi.location == "the_inferno")

print("=== 9. eight waves, honestly =====================================")
out = run(a.cmd_challenge, pi, "")
check("challenge lights wave 1", pi.inferno_wave == 1
      and pi.combat is not None, out)
guard = 0
food = 0
while pi.inferno_wave and guard < 4000 and pi.hp > 0:
    guard += 1
    pi.prayer_points = pi.prayer_max()
    if pi.combat is None:
        run(a.cmd_next, pi, "")
        continue
    m = pi.combat
    if m["name"] == "jaltok-jad":
        nxt = m.get("jad_next")
        if nxt and not pi.prayer_protects(nxt):
            nm = {"ranged": "missiles"}.get(nxt, nxt)
            run(a.dispatch, pi, f"pray protect from {nm}")
            continue
    if pi.hp < 68 and pi.has("shark"):
        food += 1
        run(a.dispatch, pi, "eat shark")
        continue
    run(a.dispatch, pi, "attack")
check("TzKal-Zuk extinguished", pi.hp > 0 and pi.inferno_wave == 0
      and "tzkal-zuk" in pi.bosses, f"hp={pi.hp} wave={pi.inferno_wave} "
      f"guard={guard}")
check("infernal cape earned", pi.has("infernal cape"))
check("The Infernal achievement", "infernal" in a._earned_achievements(pi))
print(f"      (run took {guard} turns, {food} sharks)")
run(pi.equip_item, "infernal cape", True)
check("infernal cape is BIS", pi.equipment.get("cape") == "infernal cape"
      and a.ITEMS["infernal cape"]["equip"]["str"] == 6)

print("=== 10. abandonment ==============================================")
pa = fresh_max()
pa.add("fire cape")
run(pa.equip_item, "fire cape", True)
pa.location = "the_inferno"
pa.inferno_wave = 3
out = run(a.cmd_go, pa, "out")
check("walking out abandons the run", pa.inferno_wave == 0
      and "abandoned" in out, out)
pa.inferno_wave = 5
pa.hp = 0
out = run(a._handle_death, pa)
check("death ends the run", pa.inferno_wave == 0, out)

print("=== 11. serialization ============================================")
ps = fresh_max()
ps.inferno_wave = 4
ps.add("toktz-xil-ak")
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("inferno wave + obsidian survive save", ps2.inferno_wave == 4
      and ps2.has("toktz-xil-ak"))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
