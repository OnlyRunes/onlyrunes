"""End-to-end: the Fight Caves + TzTok-Jad prayer-switching + fire cape."""
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


PRAY = {"magic": "protect from magic", "ranged": "protect from missiles",
        "melee": "protect from melee"}

p = a.Player("Tester")
p.members = True
for s in a.SKILLS:
    p.skills[s] = a._XP_TABLE[99]
p.hp = p.max_hp
p.prayer_points = p.prayer_max()
for slot, item in a._best_gear_for_style("melee").items():
    p.add(item)
    run(p.equip_item, item, True)
p.add("swordfish", 500)
p.quests = {k: "complete" for k in a.ALL_QUESTS}

# --- setup / guards -----------------------------------------------------------
out = run(a.cmd_challenge, p, "")
check("challenge refused outside caves", "nothing to challenge" in out.lower(), out)
p.location = "karamja_volcano"
out = run(a.cmd_go, p, "caves")
check("caves reachable from volcano", p.location == "fight_caves", out)
out = run(a.cmd_talk, p, "")
check("tzhaar explains the deal", "Seven waves" in out and "challenge" in out, out)
out = run(a.cmd_next, p, "")
check("next refused with no run", "challenge" in out, out)

# --- run the seven waves ---------------------------------------------------------
random.seed(42)
out = run(a.dispatch, p, "challenge")
check("wave 1 starts", getattr(p, "cave_wave", 0) == 1 and p.combat is not None, out)
check("wave 1 is tz-kih", p.combat["name"] == "tz-kih", str(p.combat["name"]))

# each TzHaar's attack style -> what to pray against it
WAVE_PRAY = {"tz-kih": "melee", "tz-kek": "melee", "tok-xil": "ranged",
             "yt-mejkot": "melee", "ket-zek": "magic"}
turns = 0
waves_seen = {1}
mobs_fought = set()
saw_drain = saw_recoil = saw_heal = False
while turns < 4000:
    turns += 1
    if p.hp <= 0:
        break
    if p.combat is None:
        if p.cave_wave == 0:
            break                        # conquered (or wiped)
        waves_seen.add(p.cave_wave)
        if p.hp < p.max_hp - 20 and p.has("swordfish"):
            run(a.dispatch, p, "eat swordfish")   # heal between waves
        else:
            run(a.dispatch, p, "next")
        continue
    m = p.combat
    mobs_fought.add(m["name"])
    if p.prayer_points < 15:
        p.prayer_points = p.prayer_max()          # simulate prayer potions
    if m["name"] == "tztok-jad":
        nxt = m.get("jad_next")
        if nxt and not p.prayer_protects(nxt):
            run(a.dispatch, p, f"pray {PRAY[nxt]}")
            continue
    else:
        want = WAVE_PRAY[m["name"]]
        if not p.prayer_protects(want):
            run(a.dispatch, p, f"pray {PRAY[want]}")
            continue
    if p.hp < 40 and p.has("swordfish"):
        out = run(a.dispatch, p, "eat swordfish")
    else:
        out = run(a.dispatch, p, "attack")
    saw_drain = saw_drain or "drains" in out
    saw_recoil = saw_recoil or "recoils" in out
    saw_heal = saw_heal or "knits its obsidian" in out

check("survived the caves", p.hp > 0, f"hp={p.hp} wave={p.cave_wave} turns={turns}")
check("all 7 waves seen", waves_seen == {1, 2, 3, 4, 5, 6, 7}, str(waves_seen))
check("fought all five TzHaar kin + Jad",
      mobs_fought == {"tz-kih", "tz-kek", "tok-xil", "yt-mejkot", "ket-zek",
                      "tztok-jad"}, str(mobs_fought))
# tz-kih dies too fast vs a maxed player to land a drain — test it directly
q1 = a.Player("Prayerful")
q1.prayer_points = 40
random.seed(9)
buf = ""
q1.combat = a._new_monster("tz-kih")
for _ in range(60):
    buf += run(a._resolve_monster_hit, q1, q1.combat)
    if q1.prayer_points < 40 or q1.hp <= 3:
        break
check("tz-kih drained prayer", "drains" in buf and q1.prayer_points < 40,
      f"pp={q1.prayer_points} " + buf[-200:])

# yt-mejkot self-heal is also seed-sensitive in the big run — test directly
q3 = a.Player("Healbait")
q3.hp = 500  # survive long enough (fake pool; not used for max_hp math)
mej = a._new_monster("yt-mejkot")
mej["cur"] = mej["hp"] // 2
random.seed(13)
buf = ""
for _ in range(120):
    buf += run(a._resolve_monster_hit, q3, mej)
    if "knits its obsidian" in buf or q3.hp <= 5:
        break
check("yt-mejkot heals (direct)", "knits its obsidian" in buf, buf[-150:])
check("yt-mejkot fought", "yt-mejkot" in mobs_fought)   # heal tested directly below
check("earned tokkul", p.has("tokkul"), str(p.count("tokkul")))
check("run complete (wave reset)", p.cave_wave == 0)
check("fire cape awarded", p.has("fire cape"))
check("jad in boss log", "tztok-jad" in p.bosses)
check("achievement earned", "fire_cape" in a._earned_achievements(p))
out = run(p.equip_item, "fire cape")
check("fire cape wearable", p.equipment.get("cape") == "fire cape", out)

# tz-kek recoil: hit it directly and watch the spikes
q2 = a.Player("Spiky")
for s in a.SKILLS:
    q2.skills[s] = a._XP_TABLE[90]
q2.hp = q2.max_hp
random.seed(5)
buf = ""
run(a._start_combat, q2, "tz-kek")
q2.combat = a._new_monster("tz-kek")
for _ in range(30):
    buf += run(a._resolve_player_hit, q2, q2.combat)
    if q2.combat["cur"] <= 0:
        break
check("tz-kek recoil stings", "recoils" in buf, buf[-200:])
check("recoil never lethal", q2.hp >= 1, str(q2.hp))

# --- leaving abandons -------------------------------------------------------------
random.seed(1)
run(a.dispatch, p, "challenge")
while p.combat is not None and p.hp > 0:
    run(a.dispatch, p, "attack")
check("wave 2 after clearing 1", p.cave_wave == 2, str(p.cave_wave))
out = run(a.cmd_go, p, "out")
check("leaving abandons run", p.cave_wave == 0 and "abandoned" in out, out)

# travel also abandons
run(a.cmd_go, p, "caves")
run(a.dispatch, p, "challenge")
while p.combat is not None and p.hp > 0:
    run(a.dispatch, p, "attack")
out = run(a.cmd_travel, p, "varrock")
check("travel abandons run", p.cave_wave == 0 and "abandoned" in out, out)

# --- death resets ------------------------------------------------------------------
p.cave_wave = 3
p.hp = 1
out = run(a._handle_death, p)
check("death ends the run", p.cave_wave == 0 and "run is over" in out, out)

# --- web chip + serialize -------------------------------------------------------------
p.location = "fight_caves"
chips = json.loads(a.web_room_actions(p))
labels = [x["actions"][0]["label"] for x in chips]
check("web Challenge chip", "Challenge" in labels, str(labels))
p.cave_wave = 4
chips = json.loads(a.web_room_actions(p))
labels = [x["actions"][0]["label"] for x in chips]
check("web Next-wave chip mid-run", "Next wave" in labels, str(labels))
p2 = a.deserialize(a.serialize(p))
check("round-trip keeps wave", p2.cave_wave == 4)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
