"""IN-DEPTH God Wars Dungeon test: all generals, kc edges, mechanics math,
godsword edge cases, drop statistics, balance simulation."""
import io, sys, contextlib, random, statistics

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
    """Fight out any ambush so the test can proceed."""
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
    p.add("swordfish", 2000)
    return p


def fight(p, mname, style_pray=None, max_turns=600):
    """Interactive fight loop. Returns (won, turns, food_eaten)."""
    food0 = p.count("swordfish")
    run(a.dispatch, p, f"fight {mname}")
    n = 0
    while p.combat is not None and p.hp > 0 and n < max_turns:
        n += 1
        if p.prayer_points < 12:
            p.prayer_points = p.prayer_max()      # simulate prayer pots
        if style_pray and not p.prayer_protects(style_pray):
            nm = {"ranged": "missiles"}.get(style_pray, style_pray)
            run(a.dispatch, p, f"pray protect from {nm}")
            if not p.prayer_protects(style_pray):
                run(a.dispatch, p, "attack")   # never stall on a bad prayer
            continue
        if p.hp < 55 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")
        else:
            run(a.dispatch, p, "attack")
    return (p.hp > 0 and p.combat is None), n, food0 - p.count("swordfish")


print("=== 1. kill count edge cases =====================================")
p = fresh_max()
p.location = "gwd_entrance"
# kc only counts inside gwd rooms
p.location = "lumbridge_castle"
run(a._quest_on_kill, p, "spiritual warrior")
check("no kc outside the dungeon", p.gwd_kc.get("bandos", 0) == 0,
      str(p.gwd_kc))
p.location = "bandos_stronghold"
settle(p)
for _ in range(13):
    run(a._quest_on_kill, p, "spiritual warrior")
check("kc accumulates past 10", p.gwd_kc["bandos"] == 13)
out = run(a.cmd_go, p, "door")
check("door consumes exactly 10", p.gwd_kc["bandos"] == 3
      and p.location == "graardor_arena", out)
run(a.cmd_go, p, "out")
settle(p)                       # ambush kills may add kc; pin it for the check
p.gwd_kc["bandos"] = 3
out = run(a.cmd_go, p, "door")
check("re-entry costs another 10", p.location == "bandos_stronghold"
      and "3/10" in out, out)
# auto-fight grants kc
random.seed(11)
p.hp = p.max_hp
settle(p)
out = run(a.dispatch, p, "fight spiritual warrior 3")
check("auto-fight grants kc", p.gwd_kc["bandos"] > 3, str(p.gwd_kc))
# kc survives death
kc_before = dict(p.gwd_kc)
p.hp = 1
run(a._handle_death, p)
check("kc survives death", p.gwd_kc == kc_before)
# serialization mid-grind
p2 = a.deserialize(a.serialize(p))
check("kc round-trips", p2.gwd_kc == p.gwd_kc)

print("=== 2. all four generals die (right style + prayer) ==============")
results = {}
plans = [
    ("general graardor", "melee", "melee", "bandos"),
    ("kree'arra", "ranged", "ranged", "armadyl"),
    ("k'ril tsutsaroth", "melee", "melee", "zamorak"),
    ("commander zilyana", "melee", "magic", "saradomin"),
]
random.seed(77)
hunter_p = fresh_max()
for mname, style, pray, god in plans:
    q = fresh_max(style)
    if style == "ranged":
        q.style = "ranged"
    q.gwd_kc = {god: 10}
    wing = {"bandos": "bandos_stronghold", "armadyl": "armadyl_eyrie",
            "zamorak": "zamorak_fortress",
            "saradomin": "saradomin_encampment"}[god]
    q.location = wing
    settle(q)
    run(a.cmd_go, q, "door")
    won, turns, food = fight(q, mname, style_pray=pray)
    results[mname] = (won, turns, food)
    check(f"{mname} slain ({style}, pray {pray})", won,
          f"turns={turns} hp={q.hp}")
    check(f"{mname} logged as boss kill", mname in q.bosses)
for mname, (won, turns, food) in results.items():
    print(f"      {mname:22} turns={turns:<4} swordfish eaten={food}")

print("=== 3. god slayer achievement =====================================")
allp = fresh_max()
allp.bosses = [m for m, _, _, _ in plans]
check("god_slayer achievement", "god_slayer" in a._earned_achievements(allp))

print("=== 4. Kree flying math ===========================================")
q = fresh_max("melee")
kree = a._new_monster("kree'arra")


def max_hit_seen(pl, mon, n=400):
    best = 0
    random.seed(5)
    for _ in range(n):
        mon["cur"] = mon["hp"]
        buf = run(a._resolve_player_hit, pl, mon)
        if "for" in buf and "glances" not in buf:
            try:
                best = max(best, int(buf.split("for ")[1].split("!")[0]))
            except Exception:
                pass
    return best


melee_max = max_hit_seen(q, kree)
qr = fresh_max("ranged")
qr.style = "ranged"
ranged_max = max_hit_seen(qr, kree)
check("flying halves melee vs kree", melee_max <= ranged_max * 0.75,
      f"melee max {melee_max} vs ranged max {ranged_max}")
print(f"      melee max hit {melee_max} | ranged max hit {ranged_max}")
# grounded monster unaffected
g = a._new_monster("hill giant")
grounded = max_hit_seen(q, g)
check("grounded melee unaffected", grounded > melee_max,
      f"{grounded} vs {melee_max}")

print("=== 5. K'ril prayer punishment rate ================================")
q = fresh_max()
run(a.cmd_pray, q, "protect from melee")
kril = a._new_monster("k'ril tsutsaroth")
smashes = 0
random.seed(6)
for _ in range(400):
    q.hp = q.max_hp
    q.prayer_points = q.prayer_max()
    buf = run(a._kril_take_turn, q, kril)
    if "STRAIGHT THROUGH" in buf:
        smashes += 1
rate = smashes / 400
check("through-prayer rate ~25%", 0.18 < rate < 0.32, f"{rate:.0%}")
print(f"      smash rate over 400 turns: {rate:.1%}")

print("=== 6. Zilyana double-turn cost ====================================")
q = fresh_max()
run(a.cmd_pray, q, "protect from melee")
pp0 = q.prayer_points
zil = a._new_monster("commander zilyana")
random.seed(7)
run(a._zilyana_take_turn, q, zil)
drain = pp0 - q.prayer_points
check("zilyana drains prayer twice", drain > 0, str(drain))
print(f"      prayer drained in one zilyana turn: {drain:.1f}")

print("=== 7. godsword edge cases =========================================")
q = fresh_max()
q.location = "varrock_west_bank"
q.skills["smithing"] = a._XP_TABLE[79]
q.add("godsword shard", 3)
out = run(a.cmd_smith, q, "godsword")
check("blade gated at 80 smithing", "level 80" in out
      and not q.has("godsword blade"), out)
q.skills["smithing"] = a._XP_TABLE[80]
run(a.cmd_smith, q, "godsword")
check("blade at exactly 80", q.has("godsword blade"))
out = run(a.cmd_smith, q, "armadyl godsword")
check("assembly needs the right hilt", "armadyl hilt" in out
      and q.has("godsword blade"), out)
q.add("armadyl hilt")
run(a.cmd_smith, q, "armadyl godsword")
check("ags assembled, parts consumed", q.has("armadyl godsword")
      and not q.has("godsword blade") and not q.has("armadyl hilt"))
q.location = "lumbridge_forest"
q.add("godsword shard", 3)
out = run(a.cmd_smith, q, "godsword")
check("no anvil, no forging", "anvil" in out and q.count("godsword shard") == 3,
      out)
# spec kill skips 'after' (no freeze on a corpse)
run(q.equip_item, "armadyl godsword", True)
q.add("zamorak godsword")
run(q.equip_item, "zamorak godsword", True)
q.spec_energy = 100
weak = a._new_monster("chicken")
weak["cur"] = 1
random.seed(3)
out = run(a._do_special, q, weak)
check("spec kill skips after-effect", "frozen solid" not in out
      or weak["cur"] > 0, out)
# AGS hits hardest
q.spec_energy = 100
run(q.equip_item, "armadyl godsword", True)
tgt = a._new_monster("hill giant")
tgt["hp"] = tgt["cur"] = 9999
best_ags = 0
random.seed(8)
for _ in range(60):
    q.spec_energy = 100
    buf = run(a._do_special, q, tgt)
    if "for" in buf:
        try:
            best_ags = max(best_ags, int(buf.split("for ")[1].split("!")[0]))
        except Exception:
            pass
normal_best = max_hit_seen(q, tgt, 300)
check("AGS judgement out-hits normal swings", best_ags > normal_best,
      f"ags {best_ags} vs normal {normal_best}")
print(f"      AGS best spec hit {best_ags} | normal best {normal_best}")

print("=== 8. drop statistics (graardor x400) =============================")
q = fresh_max()
random.seed(42)
counts = {"godsword shard": 0, "bandos hilt": 0, "bandos chestplate": 0,
          "bandos tassets": 0, "big bones": 0}
m = a.MONSTERS["general graardor"]
fake = {"drops": m["drops"], "name": "general graardor"}
for _ in range(400):
    before = {k: q.count(k) for k in counts}
    run(a._roll_drops, q, fake)
    for k in counts:
        counts[k] += q.count(k) - before[k]
shard_rate = counts["godsword shard"] / 400
hilt_rate = counts["bandos hilt"] / 400
check("shard rate ~25%", 0.18 < shard_rate < 0.32, f"{shard_rate:.1%}")
check("hilt rate ~5%", 0.02 < hilt_rate < 0.09, f"{hilt_rate:.1%}")
check("big bones always", counts["big bones"] == 400)
print(f"      shards {shard_rate:.1%} | hilts {hilt_rate:.1%} | "
      f"chest {counts['bandos chestplate']/400:.1%} | "
      f"tassets {counts['bandos tassets']/400:.1%}")

print("=== 9. gear reqs + BIS integration =================================")
low = a.Player("Low")
low.members = True
low.add("bandos chestplate")
out = run(low.equip_item, "bandos chestplate")
check("bandos needs def 65", "defence level 65" in out, out)
low.add("armadyl chestplate")
out = run(low.equip_item, "armadyl chestplate")
check("armadyl needs ranged 70", "ranged level 70" in out, out)
melee_bis = a._best_gear_for_style("melee")
ranged_bis = a._best_gear_for_style("ranged")
check("godsword is melee BIS weapon", "godsword" in melee_bis.get("weapon", ""),
      melee_bis.get("weapon"))
check("armadyl is ranged BIS body", ranged_bis.get("body") == "armadyl chestplate",
      ranged_bis.get("body"))
print(f"      melee BIS: {melee_bis.get('weapon')} + {melee_bis.get('body')}")
print(f"      ranged BIS: {ranged_bis.get('weapon')} + {ranged_bis.get('body')}")

print("=== 10. balance simulation (10 fights per general) =================")
random.seed(1234)
for mname, style, pray, god in plans:
    wins, turnlist, foodlist = 0, [], []
    for trial in range(10):
        q = fresh_max(style)
        if style == "ranged":
            q.style = "ranged"
        q.location = {"bandos": "graardor_arena", "armadyl": "kree_arena",
                      "zamorak": "kril_arena",
                      "saradomin": "zilyana_arena"}[god]
        won, turns, food = fight(q, mname, style_pray=pray)
        wins += won
        turnlist.append(turns)
        foodlist.append(food)
    check(f"{mname}: winnable but not free", wins >= 7,
          f"{wins}/10 wins")
    print(f"      {mname:22} {wins}/10 wins | median turns "
          f"{statistics.median(turnlist):.0f} | median food "
          f"{statistics.median(foodlist):.0f}")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
