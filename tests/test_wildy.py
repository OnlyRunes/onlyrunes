"""Wilderness warlords: the trio (incl. Vet'ion's rebirth), Scorpia,
the Chaos Elemental's disrobe, Kolodion's magic-only arena, and the
Corporeal Beast's spear rule."""
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


def settle(pl):
    guard = 0
    while getattr(pl, "combat", None) is not None and pl.hp > 0 and guard < 400:
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
    if style == "magic":
        for r in ("air rune", "water rune", "earth rune", "fire rune",
                  "blood rune", "death rune", "chaos rune", "mind rune"):
            p.add(r, 5000)
    run(a.dispatch, p, {"melee": "style slash", "ranged": "style ranged",
                        "magic": "style magic"}[style])
    p.add("shark", 1000)
    return p


def fight(p, mname, style_pray=None, max_turns=600):
    run(a.dispatch, p, f"fight {mname}")
    n = 0
    while p.combat is not None and p.hp > 0 and n < max_turns:
        n += 1
        if p.prayer_points < 12:
            p.prayer_points = p.prayer_max()
        if style_pray and not p.prayer_protects(style_pray):
            nm = {"ranged": "missiles"}.get(style_pray, style_pray)
            run(a.dispatch, p, f"pray protect from {nm}")
            continue
        if p.hp < 62 and p.has("shark"):
            run(a.dispatch, p, "eat shark")
            continue
        run(a.dispatch, p, "attack")
    return (p.hp > 0 and p.combat is None), n


random.seed(47)

print("=== 1. wiring ====================================================")
for rm in ("wilderness_wastes", "callisto_den", "venenatis_lair",
           "vetion_rift", "scorpia_pit", "chaos_ele_lair", "mage_arena",
           "corp_cave"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} in Wilderness", a.REGIONS.get(rm) == "Wilderness")
check("deep wilderness opens west",
      a.ROOMS["deep_wilderness"]["exits"].get("wastes")
      == "wilderness_wastes")
check("polish kept the wastes keyword",
      "wastes" in a.ROOMS["deep_wilderness"]["desc"])

print("=== 2. the trio fall (and Vet'ion rises twice) ===================")
p = fresh_max()
run(a.dispatch, p, "style stab")     # callisto is weak to stab
p.location = "callisto_den"
won, t1 = fight(p, "callisto", style_pray="melee")
check("callisto beaten", won, f"turns={t1}")
p2 = fresh_max()
run(a.dispatch, p2, "style crush")
p2.location = "venenatis_lair"
won, t2 = fight(p2, "venenatis", style_pray="magic")
check("venenatis beaten", won, f"turns={t2}")
p3 = fresh_max()
run(a.dispatch, p3, "style crush")
p3.location = "vetion_rift"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    run(a.dispatch, p3, "fight vet'ion")
    n = 0
    while p3.combat is not None and p3.hp > 0 and n < 600:
        n += 1
        p3.prayer_points = p3.prayer_max()
        if not p3.prayer_protects("melee"):
            run(a.dispatch, p3, "pray protect from melee")
            continue
        if p3.hp < 62 and p3.has("shark"):
            run(a.dispatch, p3, "eat shark")
            continue
        out = run(a.dispatch, p3, "attack")
        buf.write(out)
won3 = p3.hp > 0 and p3.combat is None
check("vet'ion beaten", won3)
check("vet'ion rose twice", "TWICE-RISEN" in buf.getvalue())
print(f"      (callisto {t1}, venenatis {t2} turns)")

print("=== 3. scorpia + chaos elemental =================================")
p4 = fresh_max()
run(a.dispatch, p4, "style crush")
p4.add("antipoison", 10)
p4.location = "scorpia_pit"
won, _ = fight(p4, "scorpia", style_pray="melee")
check("scorpia beaten", won)
p5 = fresh_max()
p5.location = "chaos_ele_lair"
buf = io.StringIO()
run(a.dispatch, p5, "fight chaos elemental")
n = 0
disrobed = False
while p5.combat is not None and p5.hp > 0 and n < 600:
    n += 1
    p5.prayer_points = p5.prayer_max()
    if p5.hp < 62 and p5.has("shark"):
        run(a.dispatch, p5, "eat shark")
        continue
    out = run(a.dispatch, p5, "attack")
    if "into the mud" in out:
        disrobed = True
check("chaos elemental beaten", p5.hp > 0 and p5.combat is None)
orig_r = a.random.random
a.random.random = lambda: 0.1
pdis = fresh_max()
cmon = dict(a.MONSTERS["chaos elemental"])
cmon["name"] = "chaos elemental"
out = run(a._chaos_disrobe, pdis, cmon, 5)
a.random.random = orig_r
check("the tendril disrobes", "into the mud" in out
      and any(v is None for k, v in pdis.equipment.items()
              if k != "weapon" and k != "ammo") or disrobed, out)

print("=== 4. kolodion: magic only ======================================")
pm = fresh_max()                      # melee char punches uselessly
pm.location = "mage_arena"
mon = dict(a.MONSTERS["kolodion"])
mon["name"] = "kolodion"
mon["cur"] = mon["hp"]
run(a.dispatch, pm, "fight kolodion")
dealt = 0
for _ in range(12):
    if pm.combat is None:
        break
    before = pm.combat["cur"]
    run(a.dispatch, pm, "attack")
    if pm.combat is not None:
        dealt += before - pm.combat["cur"]
check("melee does nothing to kolodion", dealt == 0, str(dealt))
run(a.dispatch, pm, "flee") if pm.combat else None
pw = fresh_max("magic")
pw.location = "mage_arena"
won, _ = fight(pw, "kolodion", style_pray="magic")
check("magic wins the arena", won)
check("god cape + staff claimed", pw.has("god cape") and pw.has("god staff"))
run(pw.equip_item, "god cape", True)
check("god cape is the mage's cape",
      pw.equipment.get("cape") == "god cape")

print("=== 5. the corporeal beast demands a spear =======================")
mon = dict(a.MONSTERS["corporeal beast"])
mon["name"] = "corporeal beast"
pc = fresh_max()                      # whip: not a spear
dmg_hide = 0
for _ in range(250):
    mon["cur"] = mon["hp"]
    run(a._resolve_player_hit, pc, mon)
    dmg_hide += mon["hp"] - mon["cur"]
soft = dict(mon)
soft.pop("corporeal")
soft["cur"] = soft["hp"]
dmg_soft = 0
for _ in range(250):
    soft["cur"] = soft["hp"]
    run(a._resolve_player_hit, pc, soft)
    dmg_soft += soft["hp"] - soft["cur"]
check("hide halves non-spear damage", dmg_hide < dmg_soft * 0.65,
      f"hide={dmg_hide} soft={dmg_soft}")
pk = fresh_max()
pk.add("zamorakian spear")
run(pk.equip_item, "zamorakian spear", True)
run(a.dispatch, pk, "style stab")
pk.location = "corp_cave"
won, tc = fight(pk, "corporeal beast", style_pray="magic")
check("corporeal beast slain by spear", won, f"turns={tc}")
print(f"      (corp took {tc} turns)")
pach = a.Player("Ach")
pach.bosses = ["callisto", "venenatis", "vet'ion", "corporeal beast"]
check("warlord achievement", "warlord" in a._earned_achievements(pach))

print("=== 6. spoils =====================================================")
seen = set()
pd = fresh_max()
for boss, want in (("callisto", "tyrannical ring"),
                   ("venenatis", "treasonous ring"),
                   ("vet'ion", "ring of the gods"),
                   ("corporeal beast", "spirit shield")):
    for _ in range(400):
        out = run(a._roll_drops, pd, a.MONSTERS[boss])
        if want in out:
            seen.add(want)
            break
check("all signature drops appear", len(seen) == 4, str(seen))
# dragon pickaxe: +3 effective mining
recorded = []
orig = a.gather_chance
def spy(level, req):
    recorded.append(level)
    return orig(level, req)
a.gather_chance = spy
pw2 = fresh_max()
pw2.location = "shilo_village"
run(a.cmd_mine, pw2, "gem rock")
base_lvl = recorded[-1]
pw2.add("dragon pickaxe")
run(a.cmd_mine, pw2, "gem rock")
daxe_lvl = recorded[-1]
a.gather_chance = orig
check("dragon pickaxe grants +3 mining", daxe_lvl == base_lvl + 3,
      f"{base_lvl} -> {daxe_lvl}")
# shards -> wards
pcraft = fresh_max()
pcraft.add("odium shard", 3)
pcraft.add("needle")
pcraft.add("thread", 5)
out = run(a.cmd_craft, pcraft, "odium ward")
check("3 shards craft the odium ward", pcraft.has("odium ward"), out)
# bless at an altar
pb = fresh_max()
pb.add("spirit shield")
pb.add("holy elixir")
pb.location = "lumbridge_castle"
out = run(a.cmd_bless, pb, "")
check("blessing needs an altar", not pb.has("blessed spirit shield"), out)
pb.location = "lumbridge_church"
out = run(a.cmd_bless, pb, "")
check("altar blesses the shield", pb.has("blessed spirit shield")
      and not pb.has("spirit shield"), out)

print("=== 7. serialization =============================================")
ps = fresh_max()
ps.add("tyrannical ring")
ps.bosses = ["callisto"]
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("ring + boss survive", ps2.has("tyrannical ring")
      and "callisto" in ps2.bosses)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
