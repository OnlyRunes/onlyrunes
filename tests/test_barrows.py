"""Morytania & Barrows: Priest in Peril, ghasts, six brothers, chest, sets."""
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
p.add("swordfish", 300)

# ===== PRIEST IN PERIL ========================================================
p.location = "varrock_palace"
out = run(a.cmd_talk, p, "")
check("roald starts quest", a._q(p, "priest_in_peril") == "started", out)
p.location = "varrock_east_bank"
out = run(a.cmd_go, p, "east")
check("paterdomus reachable", p.location == "paterdomus", out)
out = run(a.cmd_go, p, "cross")
check("canifis locked pre-quest", p.location == "paterdomus", out)
check("lock names the quest", "Priest in Peril" in out, out)
out = run(a.cmd_talk, p, "")
check("drezel spawns guardian", a._q(p, "priest_in_peril") == "guardian"
      and "temple guardian" in a._room_monsters(p, "paterdomus"), out)

random.seed(9)
prayer0 = p.skills["prayer"]
run(a.dispatch, p, "fight temple guardian")
n = 0
while p.combat is not None and p.hp > 0 and n < 200:
    run(a.dispatch, p, "attack")
    n += 1
check("guardian slain -> cleansed", a._q(p, "priest_in_peril") == "cleansed")
check("guardian removed from room",
      "temple guardian" not in a._room_monsters(p, "paterdomus"))
out = run(a.cmd_talk, p, "")
check("quest complete", a._q(p, "priest_in_peril") == "complete", out)
check("1406 prayer xp", p.skills["prayer"] - prayer0 >= 1406 * 2)  # XP_RATE 2

out = run(a.cmd_go, p, "cross")
check("canifis open post-quest", p.location == "canifis", out)

# ===== GHASTS ROT FOOD =========================================================
run(a.cmd_go, p, "south")
settle(p)
check("mort myre reachable", p.location == "mort_myre")
q = a._new_monster("ghast")
buf = ""
random.seed(4)
sw0 = p.count("swordfish")
for _ in range(80):
    buf += run(a._resolve_monster_hit, p, q)
    if "rots your" in buf:
        break
check("ghast rots food", "rots your" in buf and p.has("rotten food"), buf[-150:])

# ===== THE BARROWS ==============================================================
run(a.cmd_go, p, "south")
settle(p)
check("barrows reachable", p.location == "barrows_mounds")
out = run(a.cmd_dig, p, "")
check("dig needs spade", "spade" in out, out)
p.add("spade")
out = run(a.cmd_loot, p, "")
check("chest sealed while brothers stir", "sealed" in out, out)

random.seed(21)
p.hp = p.max_hp
p.prayer_points = p.prayer_max()
guard = 0
while len(p.barrows) < 6 and guard < 3000:
    guard += 1
    if p.combat is None:
        if p.hp < p.max_hp - 30 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")
        else:
            if p.prayer_points < 20:
                p.prayer_points = p.prayer_max()
            run(a.dispatch, p, "dig")
        continue
    if p.hp < 45 and p.has("swordfish"):
        run(a.dispatch, p, "eat swordfish")
    else:
        run(a.dispatch, p, "attack")
    if p.hp <= 0:
        break

check("all six brothers slain", len(p.barrows) == 6,
      f"slain={p.barrows} hp={p.hp} turns={guard}")
check("brothers in boss log", all(b in p.bosses for b in a.BROTHERS))

coins0 = p.count("coins")
random.seed(2)
out = run(a.cmd_loot, p, "")
check("chest loots coins", p.count("coins") > coins0, out)
check("chest loots runes", p.has("death rune"), out)
check("run resets after loot", p.barrows == [])
check("loot counted", p.barrows_loots == 1)
check("grave robber achievement", "grave_robber" in a._earned_achievements(p))

# loot until a barrows piece drops (30% each)
got_piece = None
for _ in range(40):
    p.barrows = list(a.BROTHERS)
    run(a.cmd_loot, p, "")
    got_piece = next((g for g in a.BARROWS_GEAR if p.has(g)), None)
    if got_piece:
        break
check("barrows gear drops from chest", bool(got_piece), str(got_piece))

# ===== SET EFFECTS ===============================================================
p.add("dharok's greataxe"); p.add("dharok's platebody")
run(p.equip_item, "dharok's greataxe", True)
run(p.equip_item, "dharok's platebody", True)
check("dharok set detected", a._barrows_set(p) == "dharok")
m = a._new_monster("cow")
p.hp = 1                                   # max dharok rage
random.seed(0)
hits = []
for _ in range(200):
    m["cur"] = m["hp"]
    buf = run(a._resolve_player_hit, p, m)
    if "for" in buf:
        try:
            hits.append(int(buf.split("for ")[1].split("!")[0].split(".")[0]))
        except Exception:
            pass
check("dharok low-hp hits exceed normal max", max(hits) > 40,
      f"max hit seen: {max(hits) if hits else 0}")

p.hp = p.max_hp
p.add("verac's flail"); p.add("verac's brassard")
run(p.equip_item, "verac's flail", True)
run(p.equip_item, "verac's brassard", True)
check("verac set detected", a._barrows_set(p) == "verac")
buf = ""
random.seed(1)
tough = a._new_monster("tztok-jad")        # def 100 — misses will happen
for _ in range(300):
    buf += run(a._resolve_player_hit, p, tough)
    if "pierces its guard" in buf:
        break
check("verac pierces defence", "pierces its guard" in buf)

p.add("guthan's warspear"); p.add("guthan's platebody")
run(p.equip_item, "guthan's warspear", True)
run(p.equip_item, "guthan's platebody", True)
p.hp = 20
buf = ""
random.seed(2)
g = a._new_monster("hill giant")
for _ in range(300):
    g["cur"] = g["hp"]
    buf += run(a._resolve_player_hit, p, g)
    if "siphons life" in buf:
        break
check("guthan heals on hit", "siphons life" in buf and p.hp > 20)

p.add("torag's hammers"); p.add("torag's platebody")
run(p.equip_item, "torag's hammers", True)
run(p.equip_item, "torag's platebody", True)
buf = ""
random.seed(3)
t = a._new_monster("hill giant")
for _ in range(400):
    t["cur"] = t["hp"]
    buf += run(a._resolve_player_hit, p, t)
    if t.get("stunned"):
        break
check("torag stuns", t.get("stunned") is True)
buf = run(a._resolve_monster_hit, p, t)
check("stunned monster misses turn", "misses its turn" in buf, buf)

# ===== brother mechanics spot-check: verac hits through prayer ==================
p.hp = p.max_hp
run(a.cmd_pray, p, "protect from melee")
v = a._new_monster("verac the defiled")
buf = ""
random.seed(5)
for _ in range(120):
    buf += run(a._brother_take_turn, p, v)
    if "THROUGH your prayer" in buf:
        break
    if p.hp < 30:
        p.hp = p.max_hp
    if p.prayer_points < 5:
        p.prayer_points = p.prayer_max()
check("verac strikes through prayer", "THROUGH your prayer" in buf, buf[-200:])

# dharok's rage: his max grows as he's wounded
d = a._new_monster("dharok the wretched")
d["cur"] = 1
p.active_prayers = []
big = 0
random.seed(6)
for _ in range(200):
    hp0 = p.hp
    run(a._brother_take_turn, p, d)
    big = max(big, hp0 - p.hp)
    p.hp = p.max_hp
check("wounded dharok hits huge", big > 16, str(big))

# ===== serialization ==============================================================
p.barrows = ["ahrim the blighted"]
p2 = a.deserialize(a.serialize(p))
check("barrows run serialized", p2.barrows == ["ahrim the blighted"])
check("loot count serialized", p2.barrows_loots == p.barrows_loots)

# web chips
p.location = "barrows_mounds"
chips = json.loads(a.web_room_actions(p))
names = [c["name"] for c in chips]
check("web dig chip", any("burial mounds" in n for n in names), str(names))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
