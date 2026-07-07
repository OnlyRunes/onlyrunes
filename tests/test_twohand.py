"""Two-handed weapons: no shield alongside godswords, bows, spears, mauls."""
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
    return " ".join(buf.getvalue().split())   # wrap-tolerant


for n in ("bandos godsword", "magic shortbow", "granite maul",
          "zamorakian spear", "hill giant club", "karil's crossbow",
          "dharok's greataxe", "saradomin sword", "yew longbow",
          "guthan's warspear", "torag's hammers", "verac's flail"):
    check(f"2h flag: {n}", a.ITEMS[n]["equip"].get("two_handed") is True)
for n in ("abyssal whip", "rune scimitar", "rune crossbow", "ahrim's staff",
          "dragon dagger", "bronze sword", "saradomin godsword"):
    expected = n == "saradomin godsword"
    check(f"{'2h' if expected else '1h'}: {n}",
          bool(a.ITEMS[n]["equip"].get("two_handed")) is expected)

p = a.Player("Tester")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[99]

p.add("rune kiteshield")
p.add("bandos godsword")
run(p.equip_item, "rune kiteshield", True)
out = run(p.equip_item, "bandos godsword")
check("2h evicts shield", p.equipment["shield"] is None
      and p.equipment["weapon"] == "bandos godsword", out)
check("shield back in pack", p.has("rune kiteshield"))
check("message explains", "needs both hands" in out, out)

out = run(p.equip_item, "rune kiteshield")
check("shield evicts 2h weapon", p.equipment["weapon"] is None
      and p.equipment["shield"] == "rune kiteshield", out)
check("weapon back in pack", p.has("bandos godsword"))

p.add("abyssal whip")
run(p.equip_item, "abyssal whip", True)
check("1h + shield coexist", p.equipment["weapon"] == "abyssal whip"
      and p.equipment["shield"] == "rune kiteshield")

melee = a._best_gear_for_style("melee")
check("melee BIS: 2h weapon, no shield",
      "godsword" in melee.get("weapon", "") and "shield" not in melee)
ranged = a._best_gear_for_style("ranged")
w = ranged.get("weapon", "")
is2h = a.ITEMS[w]["equip"].get("two_handed", False)
check("ranged BIS respects 2h", ("shield" not in ranged) == bool(is2h))

q = a.Player("Max")
a.BETA = True
run(a.cmd_devmax, q, "")
w = q.equipment.get("weapon")
if a.ITEMS.get(w, {}).get("equip", {}).get("two_handed"):
    check("maxme: no shield with 2h", q.equipment.get("shield") is None)
else:
    check("maxme: no shield with 2h", True)

r = a.Player("R")
r.members = True
for s in a.SKILLS:
    r.skills[s] = a._XP_TABLE[80]
r.style = "ranged"
r.add("magic shortbow")
r.add("rune arrow", 100)
run(r.equip_item, "magic shortbow", True)
run(r.equip_item, "rune arrow", True)
random.seed(1)
m = a._new_monster("cow")
out = run(a._resolve_player_hit, r, m)
check("2h bow shoots fine", "shoot" in out or "glances" in out
      or "fail" in out, out)

out = run(a.cmd_examine, p, "bandos godsword")
check("examine says two-handed", "two-handed" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
