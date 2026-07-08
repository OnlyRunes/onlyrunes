"""Art coverage and hygiene: every monster shows SOMETHING evocative —
bespoke portrait, family silhouette, or a boss intro — and every piece
fits a narrow terminal."""
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


# 1. every portrait belongs to a real monster (catches renames/typos)
strays = [k for k in a.MONSTER_ART if k not in a.MONSTERS]
check("every portrait matches a real monster", not strays, str(strays))

# 2. every boss has an art path: bespoke intro animation or a portrait
#    (the generic intro flashes the portrait)
bare_bosses = [b for b, d in a.MONSTERS.items() if d.get("boss")
               and b not in a.BOSS_INTRO and b not in a.MONSTER_ART]
check("every boss has art (intro or portrait)", not bare_bosses,
      str(bare_bosses))

# 3. every regular monster resolves to a portrait or a family silhouette
sworded = [m for m, d in a.MONSTERS.items() if not d.get("boss")
           and m not in a.MONSTER_ART and not a._fallback_art(m)]
check("no monster falls back to bare crossed swords", not sworded,
      str(sworded))

# 4. hygiene: width, height, no tabs
pieces = dict(a.MONSTER_ART)
pieces.update({f"family:{keys[0]}": art for keys, art in a._FAMILY_ART})
for name, art in sorted(pieces.items()):
    lines = art.splitlines()
    wide = max((len(l) for l in lines), default=0)
    if wide > 64 or len(lines) > 22 or "\t" in art:
        check(f"art fits a terminal: {name}", False,
              f"width {wide}, lines {len(lines)}")
        break
else:
    check("all art fits a terminal (<=64 wide, <=22 tall, no tabs)", True)

# 5. the generic boss intro flashes the boss's own portrait
frames = a._generic_boss_intro("kraken")
check("generic boss intro uses the portrait", any("KRAKEN" in f
      for f in frames), frames[0][:120])
frames = a._generic_boss_death("venenatis")
check("generic boss death uses the portrait", any("VENENATIS" in f
      for f in frames))
frames = a._generic_boss_intro("some unnamed future boss")
check("unknown boss still gets the roar", bool(frames))

# 6. family art actually shows up in a real fight
random.seed(6)
p = a.Player("Beastmaster")
for s in ("attack", "strength", "defence", "hitpoints"):
    p.skills[s] = a._XP_TABLE[80]
p.hp = p.max_hp
p.members = True
p.skills["slayer"] = a._XP_TABLE[95]
room = next(r for r, d in a.ROOMS.items()
            if "hellhound" in d.get("monsters", []))
p.location = room
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    a.dispatch(p, "fight hellhound")
out = buf.getvalue()
check("hellhound fight shows the fang family art", "snarling BEAST" in out,
      out[:300])
guard = 0
while p.combat is not None and guard < 120:
    p.hp = p.max_hp
    with contextlib.redirect_stdout(io.StringIO()):
        a.dispatch(p, "attack")
    guard += 1

# 7. a new-art boss fight opens with its portrait (kraken needs slayer 87)
p.combat = None
p.location = next(r for r, d in a.ROOMS.items()
                  if "kraken" in d.get("monsters", []))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    a.dispatch(p, "fight kraken")
out = buf.getvalue()
check("kraken intro flashes its own art", "KRAKEN rises" in out, out[:300])
with contextlib.redirect_stdout(io.StringIO()):
    a.dispatch(p, "flee")
    a.dispatch(p, "flee")
    a.dispatch(p, "flee")

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
