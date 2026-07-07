"""Zulrah: the rotating forms, live weakness swaps, venom pressure, the
toxic arsenal (blowpipe self-ammo, serpentine immunity, swamp trident)."""
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


def run(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


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


random.seed(50)

print("=== 1. wiring ====================================================")
for rm in ("zul_andra", "zulrah_shrine"):
    check(f"room {rm} exists", rm in a.ROOMS and rm in a.REGIONS)
check("shilo river boat", a.ROOMS["shilo_village"]["exits"].get("river")
      == "zul_andra")
check("zul-andra travel hub", a.TRAVEL_HUBS.get("zul-andra") == "zul_andra")

print("=== 2. the forms rotate and the walls move =======================")
mon = dict(a.MONSTERS["zulrah"])
mon["name"] = "zulrah"
mon["cur"] = mon["hp"]
pz = fresh_max()
pz.active_prayers = []
forms = []
for _ in range(9):
    pz.hp = pz.max_hp
    out = run(a.BOSS_TURN["zulrah"], pz, mon)
    if "GREEN" in out:
        forms.append(("green", dict(mon["dbonus"])))
    elif "CRIMSON" in out:
        forms.append(("red", dict(mon["dbonus"])))
    elif "BLUE" in out:
        forms.append(("blue", dict(mon["dbonus"])))
check("three forms in nine turns",
      [f[0] for f in forms] == ["green", "red", "blue"],
      str([f[0] for f in forms]))
check("green opens to magic", forms[0][1]["magic"] == 10
      and forms[0][1]["slash"] == 120)
check("red opens to steel", forms[1][1]["slash"] == 10
      and forms[1][1]["magic"] == 120)
check("blue opens to arrows", forms[2][1]["ranged"] == 10
      and forms[2][1]["magic"] == 120)

print("=== 3. venom + the serpentine helm ===============================")
orig_r = a.random.random
a.random.random = lambda: 0.1
pv = fresh_max()
pv.poison = 0
run(a._zulrah_poison, pv, mon, 5)
a.random.random = orig_r
check("zulrah envenoms", pv.poison > 0)
pv.add("serpentine helm")
run(pv.equip_item, "serpentine helm", True)
out = run(a._tick_poison, pv)
check("serpentine helm drinks the venom", pv.poison == 0
      and "harmlessly" in out, out)

print("=== 4. the toxic arsenal =========================================")
pb = fresh_max("ranged")
pb.add("toxic blowpipe")
run(pb.equip_item, "toxic blowpipe", True)
pb.equipment["ammo"] = None             # no ammo at all
dummy = dict(a.MONSTERS["goblin"]); dummy["name"] = "goblin"
atk = a._player_attack(pb, dummy)
check("blowpipe shoots without ammo", atk is not None
      and atk[0] == "ranged", str(atk))
pc = fresh_max()
pc.add("tanzanite fang")
pc.add("needle")
pc.add("thread", 5)
out = run(a.cmd_craft, pc, "toxic blowpipe")
check("fang fletches the blowpipe", pc.has("toxic blowpipe"), out)
pc.add("serpentine visage")
out = run(a.cmd_craft, pc, "serpentine helm")
check("visage crafts the helm", pc.has("serpentine helm"), out)
pc.add("magic fang")
out = run(a.cmd_craft, pc, "trident of the swamp")
check("swamp trident needs the sea trident too",
      not pc.has("trident of the swamp"), out)
pc.add("trident of the seas")
out = run(a.cmd_craft, pc, "trident of the swamp")
check("fang + trident forge the swamp trident",
      pc.has("trident of the swamp")
      and not pc.has("trident of the seas"), out)
check("swamp trident is the stronger staff",
      a.ITEMS["trident of the swamp"]["equip"]["powered"] == 25)

print("=== 5. the serpent falls =========================================")
pk = fresh_max("magic")
pk.add("trident of the swamp")
run(pk.equip_item, "trident of the swamp", True)
pk.add("serpentine helm")
run(pk.equip_item, "serpentine helm", True)
pk.add("antipoison", 10)
pk.location = "zulrah_shrine"
run(a.dispatch, pk, "fight zulrah")
n = 0
while pk.combat is not None and pk.hp > 0 and n < 600:
    n += 1
    pk.prayer_points = pk.prayer_max()
    if pk.hp < 65 and pk.has("shark"):
        run(a.dispatch, pk, "eat shark")
        continue
    run(a.dispatch, pk, "attack")
won = pk.hp > 0 and pk.combat is None
check("zulrah slain by the swamp trident", won, f"turns={n}")
print(f"      (kill took {n} turns)")
check("snake charmer achievement",
      "snake_charmer" in a._earned_achievements(pk))
seen = set()
pd = fresh_max()
for _ in range(500):
    out = run(a._roll_drops, pd, a.MONSTERS["zulrah"])
    for f in ("tanzanite fang", "magic fang", "serpentine visage"):
        if f in out:
            seen.add(f)
check("all three uniques drop", len(seen) == 3, str(seen))

print("=== 6. serialization =============================================")
ps = fresh_max()
ps.add("toxic blowpipe")
ps.bosses = ["zulrah"]
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("blowpipe + boss survive", ps2.has("toxic blowpipe")
      and "zulrah" in ps2.bosses)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
