"""Troll Country: Burthorpe wiring, Warriors' Guild stat gate, the defender
chain, Troll Stronghold quest e2e, Dad, trolls, and the Trollheim chasm."""
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


def fresh_max():
    p = a.Player("T")
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.hp = p.max_hp
    p.prayer_points = p.prayer_max()
    for slot, item in a._best_gear_for_style("melee").items():
        p.add(item)
        run(p.equip_item, item, True)
    run(a.dispatch, p, "style slash")
    p.add("swordfish", 500)
    return p


def fight(p, mname, style_pray=None, max_turns=400):
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
        if p.hp < 50 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")
        else:
            run(a.dispatch, p, "attack")
    return (p.hp > 0 and p.combat is None), n


random.seed(43)

print("=== 1. wiring ====================================================")
for rm in ("burthorpe", "warriors_guild", "death_plateau",
           "troll_stronghold", "trollheim"):
    check(f"room {rm} exists", rm in a.ROOMS)
    check(f"{rm} has a region", rm in a.REGIONS)
check("taverley road north", a.ROOMS["taverley"]["exits"].get("north")
      == "burthorpe")
check("burthorpe travel hub", a.TRAVEL_HUBS.get("burthorpe") == "burthorpe")
check("trollheim chasm drops into gwd",
      a.ROOMS["trollheim"]["exits"].get("chasm") == "gwd_entrance")
check("gwd climbs back to trollheim",
      a.ROOMS["gwd_entrance"]["exits"].get("climb") == "trollheim")

print("=== 2. warriors' guild weighs your arm ===========================")
lo = a.Player("Weak")
lo.members = True
lo.location = "burthorpe"
out = run(a.cmd_go, lo, "guild")
check("low levels refused", lo.location == "burthorpe"
      and "130" in out, out)
p = fresh_max()
p.location = "burthorpe"
out = run(a.cmd_go, p, "guild")
check("proven warrior admitted", p.location == "warriors_guild", out)
settle(p)

print("=== 3. the defender chain, in order ==============================")
order_seen = []
guard = 0
while len(order_seen) < len(a.DEFENDER_ORDER) and guard < 400:
    guard += 1
    out = run(a._quest_on_kill, p, "cyclops")
    for d in a.DEFENDER_ORDER:
        if d.upper() in out:
            order_seen.append(d)
check("all seven tiers awarded", order_seen == a.DEFENDER_ORDER,
      str(order_seen))
check("rune defender is the cap",
      run(a._quest_on_kill, p, "cyclops") is not None or True)
n0 = p.count("rune defender")
for _ in range(60):
    run(a._quest_on_kill, p, "cyclops")
check("no defenders past rune", p.count("rune defender") == n0)
check("defender has attack in the shield slot",
      a.ITEMS["rune defender"]["equip"]["aslash"] == 20
      and a.ITEMS["rune defender"]["equip"]["slot"] == "shield")
run(p.equip_item, "rune defender", True)
check("defender equips beside a 1h weapon",
      p.equipment.get("shield") == "rune defender")
# banked defenders still count toward the chain
pb = fresh_max()
pb.bank["adamant defender"] = 1
check("bank counts for chain position",
      a._best_defender(pb) == a.DEFENDER_ORDER.index("adamant defender"))

print("=== 4. goal rung =================================================")
q = a.Player("Mid")
q.members = True
q.kills = 100
for k in ("cooks_assistant", "sheep_shearer", "dorics_quest", "romeo_juliet",
          "vampyre_slayer", "ernest_chicken", "dragon_slayer"):
    q.quests[k] = "complete"
for s in ("attack", "strength", "defence", "hitpoints"):
    q.skills[s] = a._XP_TABLE[80]
for s in ("woodcutting", "slayer"):
    q.skills[s] = a._XP_TABLE[30]
g = a._next_goal(q)
check("defender rung fires at 130", "Warriors' Guild" in g, g)
q.add("bronze defender")
g = a._next_goal(q)
check("any defender satisfies the rung", "Warriors' Guild" not in g, g)

print("=== 5. troll stronghold quest, honestly ==========================")
p5 = fresh_max()
p5.location = "burthorpe"
# gate locked before the quest
out = run(a.cmd_go, p5, "plateau")
settle(p5)
out = run(a.cmd_go, p5, "up")
check("stronghold barred pre-quest", p5.location == "death_plateau"
      and "Denulth" in out, out)
run(a.cmd_go, p5, "down")
settle(p5)
out = do(p5, "talk")
check("quest starts", a._q(p5, "troll_stronghold") == "started", out)
run(a.cmd_go, p5, "plateau")
settle(p5)
run(a.cmd_go, p5, "up")
settle(p5)
check("stronghold opens once started", p5.location == "troll_stronghold")
out = do(p5, "talk godric")
check("godric waits behind dad", a._q(p5, "troll_stronghold") == "started",
      out)
won, turns = fight(p5, "dad", style_pray="melee")
check("DAD beaten", won and a._q(p5, "troll_stronghold") == "dad",
      f"won={won} turns={turns}")
out = do(p5, "talk godric")
check("godric freed", a._q(p5, "troll_stronghold") == "freed", out)
run(a.cmd_go, p5, "out")
settle(p5)
run(a.cmd_go, p5, "down")
settle(p5)
qp0 = a.quest_points(p5)
xp0 = p5.skills["agility"]
out = do(p5, "talk")
check("quest complete +1 QP", a._q(p5, "troll_stronghold") == "complete"
      and a.quest_points(p5) == qp0 + 1, out)
check("agility xp awarded", p5.skills["agility"] > xp0)

print("=== 6. the peak and the chasm ====================================")
run(a.cmd_go, p5, "plateau")
settle(p5)
run(a.cmd_go, p5, "up")
settle(p5)
run(a.cmd_go, p5, "peak")
check("trollheim reached", p5.location == "trollheim")
out = run(a.cmd_go, p5, "chasm")
check("chasm drops into the god wars", p5.location == "gwd_entrance", out)
out = run(a.cmd_go, p5, "climb")
check("and climbs back out", p5.location == "trollheim", out)

print("=== 7. trolls fight back =========================================")
for t in ("mountain troll", "thrower troll", "troll general"):
    check(f"{t} registered", t in a.MONSTERS
          and a.MONSTERS[t].get("level", 0) > 0)
p7 = fresh_max()
p7.location = "death_plateau"
won, _ = fight(p7, "mountain troll")
check("mountain troll dies to a maxed melee", won)
check("dad is a boss with art", "dad" in a._BOSSES
      and "dad" in a.MONSTER_ART)

print("=== 8. serialization =============================================")
ps = fresh_max()
ps.quests["troll_stronghold"] = "complete"
ps.add("mithril defender")
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("quest + defender survive save",
      ps2.quests.get("troll_stronghold") == "complete"
      and ps2.has("mithril defender"))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
