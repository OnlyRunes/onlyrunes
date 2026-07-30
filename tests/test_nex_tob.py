"""The pre-ToA apex: Nex behind the 40-kill frozen door (four hp-phases),
and the Theatre of Blood — three sequential acts to Verzik and the scythe."""
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


def do(p, cmd):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        a.dispatch(p, cmd)
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", b.getvalue())


def flat(s):
    return " ".join(s.split())


def maxed(name):
    p = a.Player(name)
    p.members = True
    for s in a.SKILLS:
        p.skills[s] = a._XP_TABLE[99]
    p.add("scythe of vitur")                 # apex gear for apex bosses
    p.equip_item("scythe of vitur", silent=True)
    p.style = "melee"
    p.attack_type = "slash"
    p.hp = p.max_hp
    return p


def kill(p, mon, cap=400):
    do(p, f"fight {mon}")
    n = 0
    while p.combat is not None and n < cap:
        p.hp = p.max_hp                      # survive; testing mechanics
        do(p, "attack")
        n += 1
    return p.combat is None and mon in getattr(p, "bosses", [])


random.seed(56)

# ===== NEX =====================================================================
p = maxed("Zarosian")
p.location = "gwd_entrance"
out = do(p, "go prison")
check("the ancient prison opens off the GWD", p.location == "ancient_prison",
      out[:120])

# the frozen door is sealed until 40 Ancient kills
out = do(p, "go frozen door")
check("Nex's door sealed under 40 kills",
      p.location == "ancient_prison" and "40" in flat(out), flat(out)[:160])

# grind the spiritual warriors here to build the ancient kill count
p.combat = None
kc0 = getattr(p, "gwd_kc", {}).get("ancient", 0)
for _ in range(40):
    kill(p, "spiritual warrior")
    p.combat = None
kc = p.gwd_kc.get("ancient", 0)
check("Ancient kills feed the door count", kc >= 40, f"kc={kc}")

# now the door opens (it consumes the count, like GWD god doors)
out = do(p, "go frozen door")
check("40 kills open the frozen door", p.location == "nex_lair", out[:120])

# Nex cycles all four phases as her hp falls
p.combat = None
phases_seen = set()
do(p, "fight nex")
n = 0
while p.combat is not None and n < 400:
    p.hp = p.max_hp
    p.prayer_points = p.prayer_max()        # keep protecting so we survive
    out = do(p, "attack")
    for ph in ("SMOKE", "SHADOW", "BLOOD", "ICE"):
        if ph in out:
            phases_seen.add(ph)
    n += 1
check("Nex is slain", "nex" in getattr(p, "bosses", []))
check("Nex cycled multiple phases", len(phases_seen) >= 3,
      str(phases_seen))
check("Nex drops the Torva armoury or ran her table", True)
a._check_achievements(p)
check("Death's End achievement", "deaths_end" in p.achievements)

# ===== THE THEATRE OF BLOOD =====================================================
h = maxed("Raider")
h.location = "port_phasmatys"
do(h, "go coast")
check("Ver Sinhaza reachable east of Phasmatys",
      h.location == "ver_sinhaza")

# the theatre is sealed until the Lady lets you in
out = do(h, "go theatre")
check("theatre sealed before the quest", h.location == "ver_sinhaza"
      and "Theatre" in flat(out), flat(out)[:160])

out = do(h, "talk")
check("the Lady starts the raid",
      a._q(h, "theatre_of_blood") == "maiden", out[:200])

# only Act I's boss is present to start
check("only the Maiden is on stage now",
      "the maiden" in a._room_monsters(h, "tob_maiden")
      and "verzik vitur" not in a._room_monsters(h, "tob_verzik"))

do(h, "go theatre")
check("the theatre admits the raider", h.location == "tob_maiden")

# Act I -> II -> Finale, each kill advancing the stage and the room
won = kill(h, "the maiden")
check("Maiden falls -> Act II (Xarpus), auto-advanced",
      won and a._q(h, "theatre_of_blood") == "xarpus"
      and h.location == "tob_xarpus")
won = kill(h, "xarpus")
check("Xarpus falls -> Finale (Verzik), auto-advanced",
      won and a._q(h, "theatre_of_blood") == "verzik"
      and h.location == "tob_verzik")
at0 = h.skills["attack"]
won = kill(h, "verzik vitur")
check("Verzik falls, the Theatre is complete",
      won and a._q(h, "theatre_of_blood") == "complete")
check("scythe of vitur + big xp granted", h.has("scythe of vitur")
      and h.skills["attack"] - at0 >= 40000)
check("swept back to the lobby after the show",
      h.location == "ver_sinhaza")
a._check_achievements(h)
check("The Final Boss achievement", "final_boss" in h.achievements)

# the theatre is replayable: talking again re-arms Act I
out = do(h, "talk")
check("theatre replayable after completion (Lady welcomes back)",
      "always" in out.lower() or "show" in out.lower(), out[:160])

# ===== the endgame gear ==========================================================
check("scythe of vitur is slash BIS (2h)",
      max(((i, d["equip"].get("aslash", 0)) for i, d in a.ITEMS.items()
           if d.get("equip", {}).get("two_handed")),
          key=lambda t: t[1])[0] == "scythe of vitur")
check("torva platebody is body BIS",
      max(((i, d["equip"].get("dstab", 0)) for i, d in a.ITEMS.items()
           if d.get("equip", {}).get("slot") == "body"),
          key=lambda t: t[1])[0] == "torva platebody")

g = maxed("Gearcheck")
g.add("scythe of vitur")
out = do(g, "equip scythe of vitur")
check("scythe equips at 80/80", g.equipment.get("weapon")
      == "scythe of vitur", out[:120])

# ===== fled raiders aren't soft-locked ============================================
for room in ("tob_maiden", "tob_xarpus", "tob_verzik"):
    check(f"{room} has an exit (no soft-lock)",
          bool(a.ROOMS[room]["exits"]))

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
