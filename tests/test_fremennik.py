"""Fremennik Province: the Trials quest end-to-end, Waterbirth lock,
rock crabs, the three Dagannoth Kings (style walls, snipes, drops, rings),
the dragon axe, and serialization."""
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
        p.add(p.equipment["ammo"], 10000)
    if style == "magic":
        for r in ("air rune", "water rune", "earth rune", "fire rune",
                  "mind rune", "chaos rune", "death rune", "blood rune"):
            p.add(r, 5000)
    run(a.dispatch, p, {"melee": "style slash", "ranged": "style ranged",
                        "magic": "style magic"}[style])
    p.add("swordfish", 2000)
    return p


def fight(p, mname, style_pray=None, max_turns=600):
    food0 = p.count("swordfish")
    run(a.dispatch, p, f"fight {mname}")
    n = 0
    while p.combat is not None and p.hp > 0 and n < max_turns:
        n += 1
        if p.prayer_points < 12:
            p.prayer_points = p.prayer_max()
        if style_pray and not p.prayer_protects(style_pray):
            nm = {"ranged": "missiles"}.get(style_pray, style_pray)
            run(a.dispatch, p, f"pray protect from {nm}")
            if not p.prayer_protects(style_pray):
                run(a.dispatch, p, "attack")
            continue
        if p.hp < 60 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")
        else:
            run(a.dispatch, p, "attack")
    return (p.hp > 0 and p.combat is None), n, food0 - p.count("swordfish")


random.seed(20260706)

print("=== 1. wiring ====================================================")
for rm in ("rellekka", "rock_crab_coast", "neitiznot", "waterbirth_island",
           "waterbirth_dungeon", "dks_lair"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} in Fremennik region", a.REGIONS.get(rm) == "Fremennik")
check("seers' road north", a.ROOMS["seers_village"]["exits"].get("north")
      == "rellekka")
check("rellekka travel hub", a.TRAVEL_HUBS.get("rellekka") == "rellekka")
check("dagannoth on duradel's list", "dagannoth" in a.DURADEL_TARGETS)
check("neitiznot shop sells the helm",
      "helm of neitiznot" in a.SHOPS["neitiznot"])

print("=== 2. waterbirth locked before the trials ======================")
p = fresh_max()
p.location = "rellekka"
out = run(a.cmd_go, p, "sail")
check("sail refused pre-quest", p.location == "rellekka"
      and "Fremennik Trials" in out, out)

print("=== 3. the trials, honestly ======================================")
out = do(p, "talk brundt")
check("quest starts at hunt", a._q(p, "fremennik_trials") == "hunt", out)
check("draugen spawned on the coast",
      "the draugen" in a._room_monsters(p, "rock_crab_coast"))
# save/load mid-hunt: the draugen derives from quest state, no respawn code
blob = a.player_to_json(p)
p = a.player_from_json(blob)
check("draugen respawns on load",
      "the draugen" in a._room_monsters(p, "rock_crab_coast")
      and "the draugen" not in a.ROOMS["rock_crab_coast"]["monsters"])
p.location = "rock_crab_coast"
won, _, _ = fight(p, "the draugen")
check("draugen slain", won and a._q(p, "fremennik_trials") == "hunted")
check("draugen despawned",
      "the draugen" not in a._room_monsters(p, "rock_crab_coast"))
p.location = "rellekka"
do(p, "talk brundt")
check("song trial assigned", a._q(p, "fremennik_trials") == "lyre")
out = do(p, "talk olaf")
check("olaf refuses without materials", "maple" in out.lower()
      and not p.has("lyre"), out)
p.add("maple logs")
p.add("ball of wool", 2)
out = do(p, "talk olaf")
check("lyre crafted, mats consumed", p.has("lyre")
      and not p.has("maple logs") and p.count("ball of wool") == 0
      and a._q(p, "fremennik_trials") == "song", out)
out = do(p, "talk brundt")
check("performance moves to feast", a._q(p, "fremennik_trials") == "feast",
      out)
stash = p.count("swordfish")
p.take("swordfish", stash)              # pockets empty for the refusal check
out = do(p, "talk brundt")
check("feast refused without fish (fish kept)",
      a._q(p, "fremennik_trials") == "feast", out)
p.add("swordfish", stash)
qp0 = a.quest_points(p)
xp0 = p.skills["fishing"]
fish0 = p.count("swordfish")
out = do(p, "talk brundt")
check("trials complete", a._q(p, "fremennik_trials") == "complete", out)
check("3 quest points", a.quest_points(p) == qp0 + 3)
check("xp awarded", p.skills["fishing"] > xp0)
check("exactly 3 swordfish eaten", p.count("swordfish") == fish0 - 3)
check("fremennik name announced", any(n.upper() in out for n in
      a._FREM_NAMES), out[-300:])
out = run(a.cmd_go, p, "sail")
check("waterbirth open after trials", p.location == "waterbirth_island", out)
settle(p)

print("=== 4. journal + goal ladder =====================================")
q = a.Player("Ladder")
q.members = True
out = run(a.cmd_quests, q, "")
check("journal lists the trials", "Fremennik Trials" in out)
check("journal shows the start hint", "start: Brundt the Chieftain" in out)
q.kills = 500
for s in a.SKILLS:
    q.skills[s] = a._XP_TABLE[85]
for k in a.ALL_QUESTS:
    q.quests[k] = "complete"
q.barrows_loots = 3
q.add("rune defender")
q.bosses = ["obor", "tztok-jad", "general graardor", "kree'arra",
            "k'ril tsutsaroth", "commander zilyana", "kalphite queen"]
g = a._next_goal(q)
check("goal points at the Kings", "Waterbirth" in g, g)
q.bosses += ["dagannoth rex", "dagannoth prime", "dagannoth supreme",
             "tzkal-zuk", "the nightmare", "callisto", "venenatis",
             "vet'ion", "corporeal beast", "vorkath",
             "crystalline hunllef"]
g = a._next_goal(q)
check("then the 99 chase", "99" in g, g)

print("=== 5. rock crabs: tanky, harmless ===============================")
m = a.MONSTERS["rock crab"]
check("crab stats (hp 50, maxhit 1)", m["hp"] == 50 and m["max_hit"] == 1)
lo = a.Player("Low")
lo.members = True
lo.location = "rock_crab_coast"
won, _, _ = fight(lo, "rock crab", max_turns=300)
check("fresh character can farm crabs", won, f"hp={lo.hp}")

print("=== 6. the Kings' style walls ====================================")
# accuracy vs Rex: slash (walled) vs magic (open door)
rex = a.MONSTERS["dagannoth rex"]
pm = fresh_max("melee")
atk_roll = (99 + 9) * (a._style_atk_bonus(pm) + 64) if hasattr(a, "_style_atk_bonus") else None
def acc_vs(style_bonus, dbonus):
    return a._accuracy((99 + 9) * (style_bonus + 64),
                       (rex["defence"] + 9) * (dbonus + 64))
walled = acc_vs(90, rex["dbonus"]["slash"])
open_ = acc_vs(20, rex["dbonus"]["magic"])
check("magic doorway >> melee wall vs Rex", open_ > walled * 1.8,
      f"open={open_:.2f} walled={walled:.2f}")
sup = a.MONSTERS["dagannoth supreme"]
check("supreme open to melee", sup["dbonus"]["slash"] < 30
      and sup["dbonus"]["ranged"] >= 200)
pri = a.MONSTERS["dagannoth prime"]
check("prime open to ranged", pri["dbonus"]["ranged"] < 30
      and pri["dbonus"]["magic"] >= 200)

print("=== 6b. wave spells give magic a top end =========================")
pmw = fresh_max("magic")
check("style magic auto-picks the best spell", pmw.autocast == "fire wave",
      pmw.autocast)
check("fire wave caps at 20", a.SPELLS["fire wave"]["max"] == 20)
check("blood runes purchasable", "blood rune" in a.SHOPS["rune"])
low = a.Player("Low2")
run(a.dispatch, low, "style magic")
check("level-1 mage keeps wind strike", low.autocast == "wind strike",
      low.autocast)

print("=== 7. the off-King snipe ========================================")
p7 = fresh_max()
p7.hp = p7.max_hp
m7 = a._start_combat if False else None
mon = dict(a.MONSTERS["dagannoth rex"])
mon["name"] = "dagannoth rex"
mon["cur"] = mon["hp"]
snipes = blocks = 0
p7.active_prayers = ["protect from magic", "protect from missiles",
                     "protect from melee"]
for _ in range(300):
    p7.hp = p7.max_hp
    p7.prayer_points = 99
    out = run(a.BOSS_TURN["dagannoth rex"], p7, mon)
    if "REX barrels" in out or "PRIME rears" in out or "SUPREME wheels" in out:
        snipes += 1
        if "turns the ambush aside" in out:
            blocks += 1
check("snipes fire (~22%)", 30 <= snipes <= 110, str(snipes))
check("matching prayer blocks every snipe", blocks == snipes,
      f"{blocks}/{snipes}")
p7.active_prayers = []
raw = 0
for _ in range(200):
    p7.hp = p7.max_hp
    out = run(a.BOSS_TURN["dagannoth rex"], p7, mon)
    if "strikes from nowhere" in out:
        raw += 1
check("unprayed snipes deal damage", raw > 5, str(raw))

print("=== 8. killing all three, with proper tactics ====================")
random.seed(7)
kills = {}
# Rex: magic gear, pray melee
pk = fresh_max("magic")
pk.quests["fremennik_trials"] = "complete"
pk.location = "dks_lair"
won, turns, food = fight(pk, "dagannoth rex", style_pray="melee")
kills["rex"] = (won, turns, food)
check("Rex falls to magic", won, str(kills["rex"]))
check("Rex dies in a reasonable fight (waves)", turns < 200, str(turns))
# Prime: ranged gear, pray magic
pk2 = fresh_max("ranged")
pk2.quests["fremennik_trials"] = "complete"
pk2.location = "dks_lair"
won, turns, food = fight(pk2, "dagannoth prime", style_pray="magic")
kills["prime"] = (won, turns, food)
check("Prime falls to arrows", won, str(kills["prime"]))
# Supreme: melee gear, pray missiles
pk3 = fresh_max("melee")
pk3.quests["fremennik_trials"] = "complete"
pk3.location = "dks_lair"
won, turns, food = fight(pk3, "dagannoth supreme", style_pray="ranged")
kills["supreme"] = (won, turns, food)
check("Supreme falls to steel", won, str(kills["supreme"]))
print(f"      (turns/food — rex {kills['rex'][1]}/{kills['rex'][2]}, "
      f"prime {kills['prime'][1]}/{kills['prime'][2]}, "
      f"supreme {kills['supreme'][1]}/{kills['supreme'][2]})")
pk.bosses = ["dagannoth rex", "dagannoth prime", "dagannoth supreme"]
got = run(a.cmd_achievements, pk, "") if hasattr(a, "cmd_achievements") else ""
check("Kingsbane achievement", "king_slayer" in a._earned_achievements(pk))

print("=== 9. drops + rings =============================================")
seen = set()
pd = fresh_max()
for _ in range(400):
    out = run(a._roll_drops, pd, a.MONSTERS["dagannoth rex"])
    for it in ("berserker ring", "warrior ring", "dragon axe"):
        if it in out:
            seen.add(it)
check("rex ring/axe drops appear over 400 kills",
      {"berserker ring", "warrior ring"} <= seen, str(seen))
check("berserker ring is a strength ring",
      a.ITEMS["berserker ring"]["equip"]["str"] == 4)
check("dagannoth bones bury for prayer",
      a.ITEMS["dagannoth bones"].get("bury", (None,))[0] == "prayer")
pr = fresh_max()
pr.add("berserker ring")
run(pr.equip_item, "berserker ring", True)
check("ring equips in ring slot", pr.equipment.get("ring")
      == "berserker ring")

print("=== 10. helm of neitiznot quest lock =============================")
ph = fresh_max()
ph.add("helm of neitiznot")
ph.quests.pop("fremennik_trials", None)
out = run(ph.equip_item, "helm of neitiznot", True)
check("helm refused pre-quest", ph.equipment.get("head")
      != "helm of neitiznot", out)
ph.quests["fremennik_trials"] = "complete"
run(ph.equip_item, "helm of neitiznot", True)
check("helm worn post-quest", ph.equipment.get("head")
      == "helm of neitiznot")

print("=== 11. dragon axe bites deeper ==================================")
recorded = []
orig = a.gather_chance
def spy(level, req):
    recorded.append(level)
    return orig(level, req)
a.gather_chance = spy
pw = fresh_max()
pw.location = "seers_village"
run(pw.equip_item, pw.equipment["weapon"], True) if False else None
for it in list(pw.inventory):
    pass
run(a.cmd_chop, pw, "maple")
base_lvl = recorded[-1]
pw.add("dragon axe")
run(a.cmd_chop, pw, "maple")
daxe_lvl = recorded[-1]
a.gather_chance = orig
check("dragon axe grants +3 effective levels", daxe_lvl == base_lvl + 3,
      f"{base_lvl} -> {daxe_lvl}")

print("=== 12. serialization ============================================")
ps = fresh_max()
ps.quests["fremennik_trials"] = "complete"
ps.add("seers ring")
ps.bosses = ["dagannoth rex"]
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("quest + ring + boss survive save",
      ps2.quests.get("fremennik_trials") == "complete"
      and ps2.has("seers ring") and "dagannoth rex" in ps2.bosses)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
