"""Morytania completion: Phasmatys + Ectofuntus, Fenkenstrain e2e,
cave horrors + black mask, and THE NIGHTMARE (phases, spores, staff)."""
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
    run(a.dispatch, p, {"melee": "style slash", "ranged": "style ranged",
                        "magic": "style magic"}[style])
    p.add("shark", 800)
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
        if p.hp < 60 and p.has("shark"):
            run(a.dispatch, p, "eat shark")
            continue
        run(a.dispatch, p, "attack")
    return (p.hp > 0 and p.combat is None), n


random.seed(46)

print("=== 1. wiring ====================================================")
for rm in ("port_phasmatys", "fenkenstrain_castle", "mos_le_harmless",
           "harmless_caves", "slepe", "nightmare_arena"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} in Morytania", a.REGIONS.get(rm) == "Morytania")
check("canifis roads", a.ROOMS["canifis"]["exits"].get("east")
      == "port_phasmatys"
      and a.ROOMS["canifis"]["exits"].get("north") == "fenkenstrain_castle")
check("phasmatys hub", a.TRAVEL_HUBS.get("phasmatys") == "port_phasmatys")

print("=== 2. the ectofuntus ============================================")
pe = fresh_max()
pe.location = "lumbridge_castle"
out = run(a.cmd_worship, pe, "")
check("no ectofuntus outside phasmatys", "Phasmatys" in out, out)
pe.location = "port_phasmatys"
pe.add("dragon bones", 5)
xp0 = pe.skills["prayer"]
out = run(a.cmd_worship, pe, "dragon bones")
gained = pe.skills["prayer"] - xp0
bury_xp = a.ITEMS["dragon bones"]["bury"][1] * a.XP_RATE
check("worship beats burial 2.5x", gained == int(bury_xp * 2.5)
      or gained == int(a.ITEMS["dragon bones"]["bury"][1] * 2.5) * a.XP_RATE,
      f"gained={gained} bury={bury_xp}")
check("one bone consumed", pe.count("dragon bones") == 4)
out = do(pe, "worship all")
check("worship batches", pe.count("dragon bones") == 0, out)
check("worship is batchable", "worship" in a.BATCHABLE)

print("=== 3. creature of fenkenstrain ==================================")
pf = fresh_max()
pf.quests.pop("fenkenstrain", None)
pf.location = "fenkenstrain_castle"
out = do(pf, "talk")
check("doctor starts the quest", a._q(pf, "fenkenstrain") == "parts", out)
out = do(pf, "talk")
check("refused without materials", a._q(pf, "fenkenstrain") == "parts", out)
pf.add("big bones", 5)
pf.add("needle")
pf.add("thread")
out = do(pf, "talk")
check("creature stitched and loose", a._q(pf, "fenkenstrain") == "creature"
      and "the experiment" in a._room_monsters(pf, "fenkenstrain_castle"),
      out)
# save/load mid-stage: the creature derives from quest state, no respawn code
blob = a.player_to_json(pf)
pf = a.player_from_json(blob)
check("creature respawns on load",
      "the experiment" in a._room_monsters(pf, "fenkenstrain_castle")
      and "the experiment" not in
      a.ROOMS["fenkenstrain_castle"]["monsters"])
won, _ = fight(pf, "the experiment")
check("creature contained", won and a._q(pf, "fenkenstrain") == "loose")
qp0 = a.quest_points(pf)
out = do(pf, "talk")
check("quest complete +1 QP", a._q(pf, "fenkenstrain") == "complete"
      and a.quest_points(pf) == qp0 + 1 and pf.has("ring of charos"), out)
m = a.MONSTERS["experiment"]
check("experiments are xp pinatas", m["hp"] == 100 and m["max_hit"] == 3)

print("=== 4. cave horrors + black mask =================================")
lo = a.Player("Low")
lo.members = True
lo.skills["slayer"] = a._XP_TABLE[57]
lo.location = "harmless_caves"
out = run(a.cmd_fight, lo, "cave horror")
check("slayer 57 refused", "58" in out and lo.combat is None, out)
seen = False
pd = fresh_max()
for _ in range(600):
    out = run(a._roll_drops, pd, a.MONSTERS["cave horror"])
    if "black mask" in out:
        seen = True
        break
check("black mask drops", seen)
# ferocity: mask matches the slayer helmet on-task
pm = fresh_max()
pm.add("black mask")
run(pm.equip_item, "black mask", True)
pm.slayer_task = {"monster": "cave horror", "amount": 10, "remaining": 10}
mon = dict(a.MONSTERS["cave horror"])
mon["name"] = "cave horror"
mon["cur"] = mon["hp"]
dmg_mask = 0
for _ in range(250):
    mon["cur"] = mon["hp"]
    run(a._resolve_player_hit, pm, mon)
    dmg_mask += mon["hp"] - mon["cur"]
pm.equipment["head"] = None
dmg_bare = 0
for _ in range(250):
    mon["cur"] = mon["hp"]
    run(a._resolve_player_hit, pm, mon)
    dmg_bare += mon["hp"] - mon["cur"]
check("black mask ferocity on task", dmg_mask > dmg_bare * 1.05,
      f"mask={dmg_mask} bare={dmg_bare}")
check("cave horror on duradel's list", "cave horror" in a.DURADEL_TARGETS)

print("=== 5. the nightmare staff raises the spell cap ==================")
ps = fresh_max("magic")
ps.add("blood rune", 500)
ps.add("air rune", 500)
ps.add("fire rune", 500)
dummy = dict(a.MONSTERS["goblin"]); dummy["name"] = "goblin"
base = a._player_attack(ps, dummy)
ps.add("nightmare staff")
run(ps.equip_item, "nightmare staff", True)
boosted = a._player_attack(ps, dummy)
check("mdmg raises the spell cap (+2 from the nightmare staff)",
      base[3] >= 21 and boosted[3] == base[3] + 2,
      f"base={base[3]} staff={boosted[3]}")

print("=== 6. THE NIGHTMARE =============================================")
mon = dict(a.MONSTERS["the nightmare"])
mon["name"] = "the nightmare"
mon["cur"] = 190
pn = fresh_max()
pn.hp = pn.max_hp
out = run(a.BOSS_TURN["the nightmare"], pn, mon)
check("sleepwalkers feed her at 200", mon["cur"] == 230
      and mon.get("night_p2") and "drinks" in out.lower(), out)
mon["cur"] = 90
out = run(a.BOSS_TURN["the nightmare"], pn, mon)
check("and again at 100", mon["cur"] == 130 and mon.get("night_p3"))
mon["cur"] = 80
out = run(a.BOSS_TURN["the nightmare"], pn, mon)
check("no third feast", mon["cur"] <= 80 or "drinks" not in out.lower())
# spores freeze
orig = a.random.random
a.random.random = lambda: 0.1
pn.frozen = False
run(a._nightmare_spores, pn, mon, 5)
a.random.random = orig
check("spores bring sleep", pn.frozen is True)
pn.frozen = False
# the full fight: crush melee + protect magic
pk = fresh_max()
run(a.dispatch, pk, "style crush")
pk.quests["fenkenstrain"] = "complete"
pk.location = "nightmare_arena"
won, turns = fight(pk, "nightmare", style_pray="magic")
check("the nightmare falls to crush", won, f"turns={turns}")
check("boss logged + achievement", "the nightmare" in pk.bosses
      and "dreamless" in a._earned_achievements(pk))
print(f"      (kill took {turns} turns)")

print("=== 7. goal ladder ===============================================")
q = a.Player("Ladder")
q.members = True
q.kills = 500
for s in a.SKILLS:
    q.skills[s] = a._XP_TABLE[85]
for k in a.ALL_QUESTS:
    q.quests[k] = "complete"
q.barrows_loots = 3
q.add("rune defender")
q.bosses = ["obor", "tztok-jad", "general graardor", "kree'arra",
            "k'ril tsutsaroth", "commander zilyana", "kalphite queen",
            "dagannoth rex", "dagannoth prime", "dagannoth supreme"]
g = a._next_goal(q)
check("nightmare rung after the kings", "NIGHTMARE" in g, g)
q.bosses += ["the nightmare"]
g = a._next_goal(q)
check("then the warlords", "WARLORDS" in g, g)
q.bosses += ["callisto", "venenatis", "vet'ion", "corporeal beast"]
g = a._next_goal(q)
check("then the inferno", "INFERNO" in g, g)

print("=== 8. serialization + journal ===================================")
pz = fresh_max()
pz.quests["fenkenstrain"] = "parts"
pz.add("black mask")
blob = a.player_to_json(pz)
pz2 = a.player_from_json(blob)
check("stage + mask survive", pz2.quests.get("fenkenstrain") == "parts"
      and pz2.has("black mask"))
j = a.Player("J")
out = run(a.cmd_quests, j, "")
check("journal lists fenkenstrain", "Creature of Fenkenstrain" in out
      and "start: Dr Fenkenstrain" in out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
