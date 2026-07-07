"""God Wars Dungeon: kc gates, four generals' mechanics, godswords."""
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


p = a.Player("Tester")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[99]
p.hp = p.max_hp
p.prayer_points = p.prayer_max()
for slot, item in a._best_gear_for_style("melee").items():
    p.add(item)
    run(p.equip_item, item, True)
p.add("swordfish", 800)

def settle(pl):
    guard = 0
    while getattr(pl, "combat", None) is not None and pl.hp > 0 and guard < 300:
        guard += 1
        run(a.dispatch, pl, "attack")


p.location = "deep_wilderness"
run(a.cmd_go, p, "chasm")
settle(p)
check("gwd reachable", p.location == "gwd_entrance")
out = run(a.cmd_look, p, "")
check("look shows kc", "kill count" in out, out)
run(a.cmd_go, p, "bandos")
settle(p)                        # ambush kills grant kc; pin it for the check
p.gwd_kc["bandos"] = 0
out = run(a.cmd_go, p, "door")
check("door sealed at 0 kc", p.location == "bandos_stronghold"
      and "0/10" in out, out)

random.seed(5)
guard = 0
while p.gwd_kc.get("bandos", 0) < 10 and guard < 900:
    guard += 1
    if p.combat is None:
        if p.hp < 50 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")
        else:
            run(a.dispatch, p, "fight spiritual warrior")
    else:
        run(a.dispatch, p, "attack")
check("kc earned", p.gwd_kc.get("bandos", 0) >= 10, str(p.gwd_kc))
out = run(a.cmd_go, p, "door")
check("door opens and consumes kc", p.location == "graardor_arena"
      and "drinks" in out, out)
check("kc consumed", p.gwd_kc["bandos"] < 10)

random.seed(9)
p.hp = p.max_hp
run(a.dispatch, p, "fight general graardor")
n = 0
while p.combat is not None and p.hp > 0 and n < 500:
    if p.hp < 55 and p.has("swordfish"):
        run(a.dispatch, p, "eat swordfish")
    else:
        run(a.dispatch, p, "attack")
    n += 1
check("graardor slain", p.combat is None and p.hp > 0, f"hp={p.hp} n={n}")
check("graardor in bosses", "general graardor" in p.bosses)

kree = a._new_monster("kree'arra")
check("kree flying flag", kree.get("flying") is True)

random.seed(3)
p.hp = p.max_hp
run(a.cmd_pray, p, "protect from melee")
kril = a._new_monster("k'ril tsutsaroth")
buf = ""
for _ in range(80):
    buf += run(a._kril_take_turn, p, kril)
    if "STRAIGHT THROUGH" in buf:
        break
    p.hp = p.max_hp
    if p.prayer_points < 20:
        p.prayer_points = p.prayer_max()
check("kril smashes through prayer", "STRAIGHT THROUGH" in buf)

p.active_prayers = []
zil = a._new_monster("commander zilyana")
buf = run(a._zilyana_take_turn, p, zil)
check("zilyana attacks twice", "second strike" in buf, buf[-200:])

# godsword assembly + specs
p.add("godsword shard", 3)
p.location = "varrock_west_bank"
out = run(a.cmd_smith, p, "godsword")
check("blade forged", p.has("godsword blade"), out)
p.add("bandos hilt")
run(a.cmd_smith, p, "bandos godsword")
check("bgs assembled", p.has("bandos godsword"))
run(p.equip_item, "bandos godsword", True)
p.spec_energy = 100
g = a._new_monster("hill giant")
g["cur"] = 999
g["hp"] = 999
def0 = g["defence"]
random.seed(1)
out = run(a._do_special, p, g)
check("bgs spec shatters defence", "SHATTERS" in out
      and g["defence"] == def0 - 15, out)

p.add("godsword shard", 3)
p.add("zamorak hilt")
run(a.cmd_smith, p, "godsword")
run(a.cmd_smith, p, "zamorak godsword")
run(p.equip_item, "zamorak godsword", True)
p.spec_energy = 100
g2 = a._new_monster("hill giant")
g2["cur"] = 999
g2["hp"] = 999
random.seed(2)
out = run(a._do_special, p, g2)
check("zgs freezes", g2.get("stunned") is True, out)
buf = run(a._resolve_monster_hit, p, g2)
check("frozen foe misses its turn", "misses its turn" in buf, buf)

p.add("godsword shard", 3)
p.add("saradomin hilt")
run(a.cmd_smith, p, "godsword")
run(a.cmd_smith, p, "saradomin godsword")
run(p.equip_item, "saradomin godsword", True)
p.spec_energy = 100
p.hp = 30
p.prayer_points = 5
g3 = a._new_monster("hill giant")
g3["cur"] = 999
g3["hp"] = 999
random.seed(4)
out = run(a._do_special, p, g3)
check("sgs heals", p.hp > 30 and p.prayer_points > 5, out)

p2 = a.deserialize(a.serialize(p))
check("gwd_kc serialized", p2.gwd_kc == p.gwd_kc)
old = a.deserialize({k: v for k, v in a.serialize(p).items()
                     if k != "gwd_kc"})
check("old saves default no kc", old.gwd_kc == {})

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
