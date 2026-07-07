"""Desert deep: Sophanem wiring, Pyramid Plunder, Desert Treasure e2e,
the four guardians, and the Ancient Magicks spellbook with its on-hit
effects."""
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
    if style == "magic":
        for r in ("air rune", "water rune", "earth rune", "fire rune",
                  "blood rune", "death rune", "chaos rune", "mind rune"):
            p.add(r, 5000)
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


random.seed(49)

print("=== 1. wiring ====================================================")
for rm in ("sophanem", "plunder_pyramid", "jaldraocht"):
    check(f"room {rm} exists", rm in a.ROOMS and rm in a.REGIONS)
check("nardah road south", a.ROOMS["nardah"]["exits"].get("south")
      == "sophanem")
check("sophanem is desert (heat applies)",
      a.ROOMS["sophanem"].get("desert") is True)

print("=== 2. pyramid plunder ===========================================")
lo = a.Player("Butterfingers")
lo.members = True
lo.location = "plunder_pyramid"
out = run(a.cmd_plunder, lo, "")
check("thieving 1 refused", "21" in out, out)
pp = fresh_max()
pp.location = "plunder_pyramid"
xp0 = pp.skills["thieving"]
c0 = pp.count("coins")
tiers = []
for _ in range(8):
    out = run(a.cmd_plunder, pp, "")
    for t in range(1, 9):
        if f"Room {t} of 8" in out:
            tiers.append(t)
check("eight rooms, deeper each time", tiers == list(range(1, 9)),
      str(tiers))
check("plunder pays", pp.count("coins") > c0)
check("thieving xp flows", pp.skills["thieving"] > xp0)
out = do(pp, "plunder 5")
check("plunder batches", "thieving xp" in out and "actions" in out,
      out[-200:])
# the sceptre, eventually (force the odds)
orig_r = a.random.random
a.random.random = lambda: 0.01
pp.plunder_tier = 7
run(a.cmd_plunder, pp, "")
a.random.random = orig_r
check("the sceptre waits in room 8", pp.has("pharaoh's sceptre"))
# leaving resets the depth
run(a.cmd_go, pp, "out")
run(a.cmd_go, pp, "pyramid")
out = run(a.cmd_plunder, pp, "")
check("leaving resets to room 1", "Room 1 of 8" in out, out)

print("=== 3. desert treasure, honestly =================================")
p = fresh_max()
p.quests.pop("desert_treasure", None)
p.location = "jaldraocht"
out = run(a.dispatch, p, "pray altar")
check("altar inert pre-quest", "Archaeologist" in out
      or "Desert Treasure" in out, out)
p.location = "sophanem"
out = do(p, "talk")
check("archaeologist starts the hunt",
      a._q(p, "desert_treasure") == "diamonds", out)
for g, (gem, room, _s) in a._DT_GUARDIANS.items():
    check(f"{g} guards {room}", g in a.ROOMS[room]["monsters"])
# save/load respawns unbeaten guardians
blob = a.player_to_json(p)
for g, (gem, room, _s) in a._DT_GUARDIANS.items():
    if g in a.ROOMS[room]["monsters"]:
        a.ROOMS[room]["monsters"].remove(g)
p = a.player_from_json(blob)
check("guardians respawn on load",
      all(g in a.ROOMS[room]["monsters"]
          for g, (gem, room, _s) in a._DT_GUARDIANS.items()))
for g, (gem, room, _s) in a._DT_GUARDIANS.items():
    p.location = room
    settle(p)
    won, _ = fight(p, g, style_pray="magic")
    check(f"{g} slain, {gem} taken", won and p.has(gem)
          and g not in a.ROOMS[room]["monsters"])
    p.hp = p.max_hp
p.location = "sophanem"
out = do(p, "talk")
check("four diamonds move the quest",
      a._q(p, "desert_treasure") == "pyramid", out)
qp0 = a.quest_points(p)
p.location = "jaldraocht"
out = run(a.dispatch, p, "pray altar")
check("the altar unlocks the ancients",
      a._q(p, "desert_treasure") == "complete"
      and p.spellbook == "ancient", out)
check("+3 QP", a.quest_points(p) == qp0 + 3)
check("diamonds consumed", not any(p.has(g)
      for g in ("smoke diamond", "ice diamond", "blood diamond",
                "shadow diamond")))

print("=== 4. the ancient spellbook =====================================")
out = run(a.cmd_autocast, p, "ice blitz")
check("ice blitz castable on ancients", p.autocast == "ice blitz", out)
out = run(a.dispatch, p, "pray altar")
check("altar swaps back to standard", p.spellbook == "standard", out)
out = run(a.cmd_autocast, p, "ice blitz")
check("standard book refuses ancient spells",
      p.autocast != "ice blitz" or "ancient" in out, out)
run(a.dispatch, p, "pray altar")
check("and swaps forward again", p.spellbook == "ancient")
# a fresh character can't touch the book
q = fresh_max("magic")
out = run(a.cmd_autocast, q, "blood blitz")
check("no quest, no ancients", "ancient" in out.lower(), out)

print("=== 5. ancient effects in combat =================================")
mon = dict(a.MONSTERS["troll general"])
mon["name"] = "troll general"
mon["cur"] = mon["hp"]
pz = fresh_max("magic")
pz.quests["desert_treasure"] = "complete"
pz.spellbook = "ancient"
run(a.cmd_autocast, pz, "ice blitz")
orig_r = a.random.random
a.random.random = lambda: 0.01          # always hit, always proc
out = run(a._resolve_player_hit, pz, mon)
a.random.random = orig_r
check("ice blitz freezes", mon.get("stunned") is True, out)
mon.pop("stunned", None)
run(a.cmd_autocast, pz, "blood blitz")
pz.hp = 50
a.random.random = lambda: 0.01
out = run(a._resolve_player_hit, pz, mon)
a.random.random = orig_r
check("blood blitz heals", pz.hp > 50, out)
run(a.cmd_autocast, pz, "shadow blitz")
att0 = mon["attack"]
a.random.random = lambda: 0.01
out = run(a._resolve_player_hit, pz, mon)
a.random.random = orig_r
check("shadow blitz saps attack", mon["attack"] <= att0 - 3, out)
run(a.cmd_autocast, pz, "smoke blitz")
mon["cur"] = mon["hp"]
a.random.random = lambda: 0.01
out = run(a._resolve_player_hit, pz, mon)
a.random.random = orig_r
check("smoke blitz chokes for extra", "chokes" in out, out)
# an ancient kill, end to end
pk = fresh_max("magic")
pk.quests["desert_treasure"] = "complete"
pk.spellbook = "ancient"
run(a.cmd_autocast, pk, "ice blitz")
pk.location = "vetion_rift"
won, tv = fight(pk, "vet'ion", style_pray="melee")
check("vet'ion falls to ice blitz", won, f"turns={tv}")

print("=== 6. serialization + journal ===================================")
ps = fresh_max()
ps.spellbook = "ancient"
ps.quests["desert_treasure"] = "diamonds"
ps.add("ice diamond")
blob = a.player_to_json(ps)
ps2 = a.player_from_json(blob)
check("spellbook + stage + diamond survive",
      ps2.spellbook == "ancient"
      and ps2.quests.get("desert_treasure") == "diamonds"
      and ps2.has("ice diamond"))
j = a.Player("J")
out = run(a.cmd_quests, j, "")
check("journal lists desert treasure", "Desert Treasure" in out
      and "start: the Archaeologist" in out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
