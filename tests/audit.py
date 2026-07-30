"""Full integrity audit of adventure.py. Prints ISSUE/WARN lines; exits clean if none."""
import io, contextlib, json, random, sys
import adventure as a

ISSUES, WARN = [], []
def issue(msg): ISSUES.append(msg)
def warn(msg): WARN.append(msg)

ITEMS, ROOMS, MONSTERS = a.ITEMS, a.ROOMS, a.MONSTERS
ATK_TYPES = set(a.ATK_TYPES)

# ---------- 1. ROOMS ----------
for rid, r in ROOMS.items():
    for d, dest in r.get("exits", {}).items():
        if dest not in ROOMS:
            issue(f"room '{rid}' exit '{d}' -> unknown room '{dest}'")
    for m in r.get("monsters", []):
        if m not in MONSTERS:
            issue(f"room '{rid}' monster '{m}' not in MONSTERS")
    for t in r.get("trees", []):
        if t not in a.TREES:
            issue(f"room '{rid}' tree '{t}' not in TREES")
    for rock in r.get("rocks", []):
        if rock not in a.ROCKS:
            issue(f"room '{rid}' rock '{rock}' not in ROCKS")
    if r.get("shop") and r["shop"] not in a.SHOPS:
        issue(f"room '{rid}' shop '{r['shop']}' not in SHOPS")
    for tgt in r.get("pickpocket", []):
        if tgt not in a.PICKPOCKET:
            issue(f"room '{rid}' pickpocket '{tgt}' not in PICKPOCKET")
    if r.get("key") and r["key"] not in ITEMS:
        issue(f"room '{rid}' key '{r['key']}' not in ITEMS")
    if r.get("altar") and (r["altar"] + " rune") not in a.RUNECRAFT:
        warn(f"room '{rid}' altar '{r['altar']}' has no RUNECRAFT entry")

# ---------- 2. Connectivity (BFS as a member, can use keys) ----------
start = "lumbridge_castle"
seen, stack = {start}, [start]
while stack:
    cur = stack.pop()
    for dest in ROOMS[cur].get("exits", {}).values():
        if dest not in seen:
            seen.add(dest); stack.append(dest)
orphans = {r for r in set(ROOMS) - seen
           if not ROOMS[r].get("dig_entry")     # dig-entered rooms are fine
           and not ROOMS[r].get("quest_entry")}  # quest auto-advance rooms too
if orphans:
    warn(f"{len(orphans)} room(s) unreachable from {start}: {sorted(orphans)}")

# every room should belong to a region (map labels + ambience depend on it)
_noregion = [r for r in ROOMS if r not in a.REGIONS]
if _noregion:
    warn(f"{len(_noregion)} room(s) missing a REGIONS entry: {sorted(_noregion)}")

# reverse reachability: can you get back? (one-way traps)
rev = {rid: set() for rid in ROOMS}
for rid, r in ROOMS.items():
    for dest in r.get("exits", {}).values():
        rev[dest].add(rid)
backseen, stack = {start}, [start]
while stack:
    cur = stack.pop()
    for src in rev[cur]:
        if src not in backseen:
            backseen.add(src); stack.append(src)
trapped = (seen - backseen) - {start}
if trapped:
    warn(f"room(s) you can enter but not return from: {sorted(trapped)}")

# ---------- 3. MONSTERS ----------
for name, m in MONSTERS.items():
    for f in ("hp", "attack", "defence", "max_hit", "drops"):
        if f not in m:
            issue(f"monster '{name}' missing field '{f}'")
    for d in m.get("drops", []):
        item = d[0]
        if item not in ITEMS:
            issue(f"monster '{name}' drops unknown item '{item}'")
    w = m.get("weakness") or m.get("weak")
    if w and w not in ATK_TYPES:
        warn(f"monster '{name}' weakness '{w}' not a valid attack type")
    for at in (m.get("atktype") or []):
        if at not in ATK_TYPES and at not in ("melee", "dragonfire", "ranged"):
            warn(f"monster '{name}' atktype '{at}' unusual")
    if not m.get("level"):
        warn(f"monster '{name}' has no combat level (cb)")

# ---------- 4. ITEMS / equipment ----------
OLD_KEYS = {"att", "def", "ranged", "magic"}
for name, info in ITEMS.items():
    eq = info.get("equip")
    if not eq:
        continue
    leftover = OLD_KEYS & set(eq)
    if leftover:
        issue(f"item '{name}' still uses OLD equip keys {sorted(leftover)} "
              f"(broken in per-type combat)")
    if eq.get("slot") not in a.EQUIP_SLOTS:
        issue(f"item '{name}' equip slot '{eq.get('slot')}' invalid")
    for sk in eq.get("req", {}):
        if sk not in a.SKILLS:
            issue(f"item '{name}' req skill '{sk}' invalid")

# ---------- 5. SHOPS ----------
for sname, stock in a.SHOPS.items():
    for item in stock:
        if item not in ITEMS:
            issue(f"shop '{sname}' sells unknown item '{item}'")

# ---------- 6. recipes / gathering ----------
for src, (prod, lvl, xp) in a.TREES.items():
    if prod not in ITEMS: issue(f"TREES '{src}' product '{prod}' not in ITEMS")
for src, (prod, lvl, xp) in a.ROCKS.items():
    if prod not in ITEMS: issue(f"ROCKS '{src}' product '{prod}' not in ITEMS")
for tool, lst in a.FISH.items():
    for prod, lvl, xp in lst:
        if prod not in ITEMS: issue(f"FISH '{tool}' product '{prod}' not in ITEMS")
for raw, (cooked, burnt, lvl) in a.RAW_TO_COOKED.items():
    for it in (raw, cooked, burnt):
        if it not in ITEMS: issue(f"RAW_TO_COOKED references unknown item '{it}'")
for bar, (ores, lvl, xp) in a.SMELT.items():
    if bar not in ITEMS: issue(f"SMELT bar '{bar}' not in ITEMS")
    for ore in ores:
        if ore not in ITEMS: issue(f"SMELT '{bar}' ore '{ore}' not in ITEMS")
for rune in a.RUNECRAFT:
    if rune not in ITEMS: issue(f"RUNECRAFT rune '{rune}' not in ITEMS")
# herblore
for grimy, (clean, lvl, xp) in a.HERBS.items():
    for it in (grimy, clean):
        if it not in ITEMS: issue(f"HERBS references unknown item '{it}'")
for pot, d in a.POTIONS.items():
    if pot not in ITEMS: issue(f"POTION '{pot}' not in ITEMS")
    for it in (d["herb"], d["second"]):
        if it not in ITEMS: issue(f"POTION '{pot}' ingredient '{it}' not in ITEMS")
    kind = d["effect"][0]
    if kind == "boost" and d["effect"][1] not in a.SKILLS:
        issue(f"POTION '{pot}' boosts unknown skill '{d['effect'][1]}'")
# fletching
for log, opts in a.FLETCH_CUT.items():
    if log not in ITEMS: issue(f"FLETCH_CUT log '{log}' not in ITEMS")
    for u, lvl, xp in opts:
        if u not in ITEMS: issue(f"FLETCH_CUT product '{u}' not in ITEMS")
for u, (bow, lvl, xp) in a.FLETCH_STRING.items():
    for it in (u, bow):
        if it not in ITEMS: issue(f"FLETCH_STRING references unknown item '{it}'")

# ---------- 6b. SMITH menu resolves to real items ----------
for metal in a.SMITH_METAL_LVL:
    for item_type in a.SMITH_BARS:
        result = f"{metal} {item_type}"
        if result not in ITEMS:
            warn(f"SMITH menu offers '{result}' but no such item exists")

# ---------- 7. SPELLS ----------
for sp, d in a.SPELLS.items():
    for rune in d.get("runes", {}):
        if rune not in ITEMS: issue(f"SPELL '{sp}' rune '{rune}' not in ITEMS")
    if d.get("type") == "combat" and "max" not in d:
        issue(f"combat SPELL '{sp}' missing 'max'")

# ---------- 8. SLAYER / pickpocket ----------
for t in a.SLAYER_TARGETS:
    if t not in MONSTERS:
        issue(f"SLAYER_TARGET '{t}' not in MONSTERS")

# ---------- 9. HANDLERS callable ----------
for verb, fn in a.HANDLERS.items():
    if not callable(fn):
        issue(f"HANDLER '{verb}' not callable")

# ---------- 10. SKILL_COLOR coverage ----------
for s in a.SKILLS:
    if s not in a.SKILL_COLOR:
        warn(f"skill '{s}' missing SKILL_COLOR entry")

# ---------- 11. Combat smoke + examine for every monster ----------
def silent(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()

random.seed(1)
for name in list(MONSTERS):
    p = a.Player("Auditor")
    # max the player so fights resolve quickly
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.members = True
    p.hp = p.max_hp
    try:
        silent(a._examine_monster, p, name)
    except Exception as e:
        issue(f"examine '{name}' raised {type(e).__name__}: {e}")
    try:
        p.combat = a._new_monster(name)
        for _ in range(400):
            if p.combat is None or p.hp <= 0:
                break
            silent(a.combat_action, p, "attack")
    except Exception as e:
        issue(f"combat with '{name}' raised {type(e).__name__}: {e}")

# ---------- 11b. each style kills a cow with proper gear ----------
a.enable_beta()
for style in ("melee", "ranged", "magic"):
    p = a.Player("StyleTest"); p.style = style
    silent(a.cmd_devmax, p, "")          # equips best-in-slot for the style
    p.combat = a._new_monster("cow")
    for _ in range(60):
        if p.combat is None: break
        silent(a.combat_action, p, "attack")
    if p.combat is not None:
        issue(f"{style} (geared) failed to kill a cow in 60 turns")

# ---------- 12. stats <skill> for every skill ----------
p = a.Player("Auditor")
for s in a.SKILLS:
    try:
        silent(a.cmd_stats, p, s)
    except Exception as e:
        issue(f"stats '{s}' raised {type(e).__name__}: {e}")

# ---------- 13. serialize / deserialize round-trip ----------
p = a.Player("RoundTrip")
p.skills["attack"] = a._XP_TABLE[50]
p.kill_log = {"goblin": 3}
p.add("coins", 999)
d = a.serialize(p)
p2 = a.deserialize(d)
for f in ("name", "location", "skills", "inventory", "kill_log", "members"):
    if getattr(p, f) != getattr(p2, f):
        issue(f"serialize round-trip mismatch on '{f}'")

# ---------- 14. web API smoke ----------
p = a.Player("WebTester")
for fn in (a.web_logo,):
    try: fn()
    except Exception as e: issue(f"{fn.__name__} raised {e}")
for fn in (a.web_welcome, a.web_status, a.web_room_actions):
    try: fn(p)
    except Exception as e: issue(f"{fn.__name__} raised {e}")
try:
    a.web_command(p, "look"); a.web_command(p, "stats attack")
except Exception as e:
    issue(f"web_command raised {e}")
# in-combat web_status (enemy bar)
p.combat = a._new_monster("goblin")
try:
    st = json.loads(a.web_status(p))
    if not st.get("enemy"): issue("web_status enemy missing during combat")
    json.loads(a.web_room_actions(p))
except Exception as e:
    issue(f"web combat status raised {e}")

# ---------- report ----------
print(f"=== AUDIT: {len(ISSUES)} issues, {len(WARN)} warnings ===\n")
if ISSUES:
    print("ISSUES (should fix):")
    for m in ISSUES: print("  ✗", m)
    print()
if WARN:
    print("WARNINGS (review):")
    for m in WARN: print("  ·", m)
sys.exit(1 if ISSUES else 0)
