"""Regional gap-fill: mole, chaos temple, fishing choice, picks, yews."""
import io, sys, contextlib, json, random

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


p = a.Player("Tester")
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[90]
p.hp = p.max_hp
p.members = True
for slot, item in a._best_gear_for_style("melee").items():
    p.add(item)
    run(p.equip_item, item, True)
p.add("swordfish", 100)

# --- pickables -----------------------------------------------------------------
p.location = "karamja_port"
out = run(a.dispatch, p, "pick banana 5")
check("banana batch picking", p.count("banana") == 5, out)
p.location = "seers_village"
run(a.cmd_pick, p, "")
check("flax pickable at seers", p.has("flax"))
p.location = "falador_east"
run(a.cmd_pick, p, "")
check("cabbage patch works", p.has("cabbage"))
p.location = "lumbridge_farm"
run(a.cmd_pick, p, "")
check("wheat still picks grain", p.has("grain"))

# --- fishing: new spots + tool choice --------------------------------------------
p.add("lobster pot"); p.add("harpoon"); p.add("small fishing net")
p.location = "karamja_port"
random.seed(3)
got = False
for _ in range(40):
    run(a.cmd_fish, p, "lobster")
    if p.has("raw lobster"):
        got = True
        break
check("musa point lobsters by name", got)
out = run(a.cmd_fish, p, "boot")
check("unknown fish lists spots", "Spots:" in out, out)
p.location = "draynor_village"
random.seed(3)
got = False
for _ in range(30):
    run(a.cmd_fish, p, "")
    if p.has("raw shrimp") or p.has("raw anchovies"):
        got = True
        break
check("draynor net fishing", got)

# --- edgeville yews ----------------------------------------------------------------
p.location = "edgeville"
p.add("rune axe")
random.seed(1)
got = False
for _ in range(40):
    run(a.cmd_chop, p, "yew")
    if p.has("yew logs"):
        got = True
        break
check("edgeville yews", got)

# --- chaos temple ---------------------------------------------------------------------
p.location = "wilderness_edge"
run(a.cmd_go, p, "north")
settle(p)
out = run(a.cmd_go, p, "temple")
settle(p)
check("chaos temple reachable", p.location == "chaos_temple", out)
p.add("big bones")
xp0 = p.skills["prayer"]
out = run(a.cmd_bury, p, "big bones")
check("chaos altar +50%", p.skills["prayer"] - xp0 == int(15 * 1.5) * 2,
      f"gained {p.skills['prayer'] - xp0}")
check("green dragons in deep wild",
      "green dragon" in a.ROOMS["deep_wilderness"]["monsters"])

# --- giant mole ---------------------------------------------------------------------------
p.location = "falador_square"
run(a.cmd_go, p, "park")
out = run(a.cmd_dig, p, "")
check("dig needs spade at park", "spade" in out and p.location == "falador_park", out)
p.add("spade")
out = run(a.cmd_dig, p, "")
check("dig enters mole lair", p.location == "mole_lair", out)
random.seed(8)
p.hp = p.max_hp
run(a.dispatch, p, "fight giant mole")
n = 0
saw_burrow = False
while p.combat is not None and p.hp > 0 and n < 300:
    out = run(a.dispatch, p, "attack" if p.hp > 40 or not p.has("swordfish")
              else "eat swordfish")
    saw_burrow = saw_burrow or "burrows away" in out
    n += 1
check("giant mole slain", p.combat is None and p.hp > 0, f"hp={p.hp} n={n}")
check("mole burrow-heal seen", saw_burrow)
check("mole drops", p.has("mole claw") and p.has("mole skin"))
check("whack-a-mole achievement", "whack_a_mole" in a._earned_achievements(p))

# --- look + web chips ------------------------------------------------------------------------
p.location = "karamja_port"
out = run(a.cmd_look, p, "")
check("look lists picks", "'pick': banana" in out, out)
chips = json.loads(a.web_room_actions(p))
check("web Pick chip", any(c["actions"][0]["label"] == "Pick" for c in chips),
      str([c["name"] for c in chips]))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
