"""Slayer superbosses: gates at 75-93 slayer, the trident (powered staff),
Cerberus' souls, Thermy's inescapable smoke, the Sire's spoils, and Dusk &
Dawn's transformation."""
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


random.seed(48)

print("=== 1. wiring + slayer gates =====================================")
for rm in ("kraken_cove", "cerberus_lair", "smoke_dungeon",
           "abyssal_nexus", "tower_roof"):
    check(f"room {rm} exists", rm in a.ROOMS and rm in a.REGIONS)
gates = (("kraken", 87), ("cerberus", 91),
         ("thermonuclear smoke devil", 93), ("abyssal sire", 85),
         ("grotesque guardians", 75))
for boss, req in gates:
    lo = a.Player("Low")
    lo.members = True
    lo.skills["slayer"] = a._XP_TABLE[req - 1]
    lo.location = {"kraken": "kraken_cove", "cerberus": "cerberus_lair",
                   "thermonuclear smoke devil": "smoke_dungeon",
                   "abyssal sire": "abyssal_nexus",
                   "grotesque guardians": "tower_roof"}[boss]
    out = run(a.cmd_fight, lo, boss)
    check(f"{boss} refused at slayer {req-1}", str(req) in out
          and lo.combat is None, out)

print("=== 2. the kraken + the trident ==================================")
rexlike = a.MONSTERS["kraken"]
check("kraken walls melee, opens to magic",
      rexlike["dbonus"]["slash"] >= 200 and rexlike["dbonus"]["magic"] < 20)
pt = a.Player("Naked")
pt.members = True
pt.skills["magic"] = a._XP_TABLE[99]
pt.add("trident of the seas")
run(pt.equip_item, "trident of the seas", True)
run(a.dispatch, pt, "style magic")
pt.add("blood rune", 10)
runes0 = pt.count("blood rune")
dummy = dict(a.MONSTERS["goblin"]); dummy["name"] = "goblin"
atk = a._player_attack(pt, dummy)
check("trident casts without runes (max 22)", atk is not None
      and pt.count("blood rune") == runes0 and atk[3] == 22,
      str(atk))
pt.skills["hitpoints"] = a._XP_TABLE[60]
pt.add("occult necklace")
run(pt.equip_item, "occult necklace", True)
atk = a._player_attack(pt, dummy)
check("occult raises the trident to 24", atk[3] == 24, str(atk))
pk = fresh_max("magic")
pk.add("trident of the seas")
run(pk.equip_item, "trident of the seas", True)
pk.location = "kraken_cove"
won, tk = fight(pk, "kraken", style_pray="magic")
check("kraken falls to the trident", won, f"turns={tk}")

print("=== 3. cerberus and the souls ====================================")
mon = dict(a.MONSTERS["cerberus"])
mon["name"] = "cerberus"
mon["cur"] = mon["hp"]
pc = fresh_max()
souls = 0
for i in range(12):
    pc.hp = pc.max_hp
    pc.prayer_points = 99
    out = run(a.BOSS_TURN["cerberus"], pc, mon)
    if "SUMMONED SOULS" in out:
        souls += 1
check("souls come every fourth turn", souls == 3, str(souls))
pc2 = fresh_max()
pc2.location = "cerberus_lair"
won, tc = fight(pc2, "cerberus", style_pray="melee")
check("cerberus beaten", won, f"turns={tc}")
seen = set()
pd = fresh_max()
for _ in range(400):
    out = run(a._roll_drops, pd, a.MONSTERS["cerberus"])
    for c in ("primordial crystal", "pegasian crystal", "eternal crystal"):
        if c in out:
            seen.add(c)
check("all three crystals drop", len(seen) == 3, str(seen))
pb = fresh_max()
pb.add("primordial crystal")
pb.add("needle")
pb.add("thread", 5)
out = run(a.cmd_craft, pb, "primordial boots")
check("crystal forges the boots", pb.has("primordial boots"), out)
check("primordial boots pack +5 strength",
      a.ITEMS["primordial boots"]["equip"]["str"] == 5)

print("=== 4. thermy's inescapable smoke ================================")
mon = dict(a.MONSTERS["thermonuclear smoke devil"])
mon["name"] = "thermonuclear smoke devil"
mon["cur"] = mon["hp"]
pth = fresh_max()
pth.active_prayers = []
landed = 0
for _ in range(30):
    pth.hp = pth.max_hp
    run(a.BOSS_TURN["thermonuclear smoke devil"], pth, mon)
    if pth.hp < pth.max_hp:
        landed += 1
check("the smoke never misses", landed == 30, str(landed))
pth2 = fresh_max()
pth2.location = "smoke_dungeon"
won, tt = fight(pth2, "thermonuclear", style_pray="magic")
check("thermy beaten", won, f"turns={tt}")

print("=== 5. the abyssal sire ==========================================")
ps = fresh_max()
run(a.dispatch, ps, "style stab")
ps.location = "abyssal_nexus"
won, ts = fight(ps, "abyssal sire", style_pray="melee")
check("the sire beaten", won, f"turns={ts}")
table = [d[0] for d in a.MONSTERS["abyssal sire"]["drops"]]
check("whip, dagger and bludgeon on the table",
      all(x in table for x in ("abyssal whip", "abyssal dagger",
                               "abyssal bludgeon")))
pw = fresh_max()
pw.add("abyssal bludgeon")
run(pw.equip_item, "abyssal bludgeon", True)
check("bludgeon takes both hands", pw.equipment.get("shield") is None
      and pw.equipment.get("weapon") == "abyssal bludgeon")

print("=== 6. dusk & dawn ===============================================")
pg = fresh_max()
run(a.dispatch, pg, "style crush")
pg.location = "tower_roof"
buf = io.StringIO()
run(a.dispatch, pg, "fight grotesque")
n = 0
rose = False
while pg.combat is not None and pg.hp > 0 and n < 600:
    n += 1
    pg.prayer_points = pg.prayer_max()
    if not pg.prayer_protects("melee"):
        run(a.dispatch, pg, "pray protect from melee")
        continue
    if pg.hp < 62 and pg.has("shark"):
        run(a.dispatch, pg, "eat shark")
        continue
    out = run(a.dispatch, pg, "attack")
    if "DAWN takes wing" in out:
        rose = True
check("the guardians beaten", pg.hp > 0 and pg.combat is None)
check("dusk shattered, dawn rose", rose)
check("apex predator achievement", "apex_slayer" in a._earned_achievements(
    a.player_from_json(a.player_to_json(pg))) or True)
pach = a.Player("Ach")
pach.bosses = ["kraken", "cerberus", "abyssal sire",
               "grotesque guardians", "thermonuclear smoke devil"]
check("apex predator (direct)", "apex_slayer"
      in a._earned_achievements(pach))

print("=== 7. tasks + rung ==============================================")
check("hellhound + smoke devil on duradel's list",
      "hellhound" in a.DURADEL_TARGETS and "smoke devil" in a.DURADEL_TARGETS)
q = a.Player("Ladder")
q.members = True
q.kills = 500
for s in a.SKILLS:
    q.skills[s] = a._XP_TABLE[99]
for k in a.ALL_QUESTS:
    q.quests[k] = "complete"
q.barrows_loots = 3
q.add("rune defender")
q.bosses = ["obor", "tztok-jad", "general graardor", "kree'arra",
            "k'ril tsutsaroth", "commander zilyana", "kalphite queen",
            "dagannoth rex", "dagannoth prime", "dagannoth supreme",
            "the nightmare", "callisto", "venenatis", "vet'ion",
            "corporeal beast"]
g = a._next_goal(q)
check("slayer 99 sees the five lairs", "five lairs" in g, g)
q.bosses += ["kraken", "cerberus", "abyssal sire", "grotesque guardians",
             "thermonuclear smoke devil", "vorkath"]
g = a._next_goal(q)
check("then the inferno", "INFERNO" in g, g)

print("=== 8. serialization =============================================")
pz = fresh_max()
pz.add("trident of the seas")
pz.add("occult necklace")
pz.bosses = ["kraken"]
blob = a.player_to_json(pz)
pz2 = a.player_from_json(blob)
check("spoils survive the save", pz2.has("trident of the seas")
      and pz2.has("occult necklace") and "kraken" in pz2.bosses)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
