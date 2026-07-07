"""Special attacks: energy economy, the spec verb, refusal costs, and a
sample of signature specs. (Rewrite — the original suite was lost to tmp
cleanup.)"""
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


def fresh_max():
    p = a.Player("T")
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.hp = p.max_hp
    for slot, item in a._best_gear_for_style("melee").items():
        p.add(item)
        run(p.equip_item, item, True)
    run(a.dispatch, p, "style slash")
    return p


random.seed(21)

# registry sanity
for w, sp in a.SPECIAL_ATTACKS.items():
    if not all(k in sp for k in ("name", "cost", "hits", "acc", "dmg",
                                 "desc")):
        check(f"spec entry {w} well-formed", False, str(sp))
        break
else:
    check("every spec entry is well-formed", True)
check("classic specs present", all(w in a.SPECIAL_ATTACKS for w in
      ("dragon dagger", "granite maul", "abyssal whip", "excalibur")))

# energy: regen out of combat only, full on rest
p = fresh_max()
p.spec_energy = 0
run(a._regen_energy, p)
check("spec regens out of combat", p.spec_energy > 0)
p.spec_energy = 10
p.combat = {"name": "goblin", "cur": 5, "hp": 5}
e0 = p.spec_energy
run(a._regen_energy, p)
check("no spec regen mid-fight", p.spec_energy == e0)
p.combat = None
p.location = "lumbridge_castle"
run(a.cmd_rest, p, "")
check("rest restores spec to full", p.spec_energy == 100)

# spec in combat: cost paid, refusal at low energy keeps the turn
p = fresh_max()
p.add("dragon dagger")
run(p.equip_item, "dragon dagger", True)
p.location = "lumbridge_forest"
run(a.dispatch, p, "fight goblin")
if p.combat is not None:
    p.spec_energy = 100
    m0 = p.combat["cur"]
    out = run(a.dispatch, p, "spec")
    check("dragon dagger spec fires", p.spec_energy == 75
          or p.combat is None, out)
    if p.combat is not None:
        p.spec_energy = 5
        m1 = p.combat["cur"]
        out = run(a.dispatch, p, "spec")
        check("low energy refusal costs nothing",
              p.combat is None or (p.spec_energy == 5
                                   and p.combat["cur"] == m1), out)
    while p.combat is not None and p.hp > 0:
        run(a.dispatch, p, "attack")

# cmd_spec shows the meter anywhere
p2 = fresh_max()
out = run(a.cmd_spec, p2, "")
check("spec readout works", "%" in out or "energy" in out.lower(), out)

# godsword 'after' callbacks exist
check("godsword specs carry after-effects",
      all("after" in a.SPECIAL_ATTACKS[g] for g in
          ("bandos godsword", "saradomin godsword")))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
