

# ===========================================================================
#  NEX & THE THEATRE OF BLOOD  (the pre-ToA apex)
# ===========================================================================
# Two of Gielinor's hardest doors. In the frozen heart of the God Wars
# Dungeon a fifth prison holds NEX, the Zarosian angel of death, four
# phases of shifting elements behind a 40-kill frozen door. And beneath
# Ver Sinhaza in Morytania, the vampyre matriarch VERZIK VITUR runs her
# THEATRE OF BLOOD — three acts of blood magic that end with the scythe
# of vitur, the deadliest weapon in the world.

# --- the ancient (Zarosian) armoury ------------------------------------------------
for _piece, _slot, _stats, _val in [
    ("torva full helm", "head",
     {"dstab": 59, "dslash": 61, "dcrush": 58, "dmagic": -3, "drange": 60,
      "str": 4}, 6_000_000),
    ("torva platebody", "body",
     {"dstab": 111, "dslash": 106, "dcrush": 118, "dmagic": -14,
      "drange": 113, "str": 6}, 12_000_000),
    ("torva platelegs", "legs",
     {"dstab": 87, "dslash": 84, "dcrush": 92, "dmagic": -11, "drange": 89,
      "str": 4}, 10_000_000),
]:
    _eq = {"slot": _slot, "req": {"defence": 80}}
    _eq.update(_stats)
    add_item(_piece, _val, members=True, equip=_eq)
EFFECT_NOTES["torva platebody"] = ("ancient Zarosian plate torn from Nex — "
                                   "the finest melee body in Gielinor")
add_item("nexling", 800000, members=True)
EFFECT_NOTES["nexling"] = "a tiny shadow that followed you out of Nex's prison"
add_item("zaryte crossbow", 8_000_000, members=True, equip={
    "slot": "weapon", "arange": 95, "rstr": 65, "two_handed": True,
    "self_ammo": True, "req": {"ranged": 80}})
EFFECT_NOTES["zaryte crossbow"] = ("Nex's own crossbow — needs no ammo, its "
                                   "bolts are drawn from shadow")

# --- NEX (four phases behind the frozen door) --------------------------------------
NEX_ART = r"""
        __/\  /\__
       /  o \/ o  \       N E X —
      |    /\/\    |       Angel of Death,
      |   ( <> )   |        Zaros's blade.
       \___\  /___/
      __/ | \/ | \__
     /   /|    |\   \
    ~   ' '    ' '   ~
"""

_NEX_PHASES = {
    "smoke": ("bwhite", "\"Fear the shadow!\" — NEX drapes herself in "
                        "SMOKE, and her strikes choke. (magic)"),
    "shadow": ("purple", "\"Embrace the SHADOW!\" — NEX drinks the light "
                         "and darkens. (magic, drains your stats)"),
    "blood": ("bred", "\"Flee, before I bleed you dry!\" — NEX turns to "
                      "BLOOD, healing on every hit. (ranged)"),
    "ice": ("bcyan", "\"Die now, in a prison of ICE!\" — NEX freezes the "
                     "chamber. (ranged, freezes)"),
}
_NEX_ORDER = ["smoke", "shadow", "blood", "ice"]


def _nex_take_turn(p, m):
    hp_frac = m["cur"] / m["hp"] if m["hp"] else 0
    phase_idx = min(3, int((1 - hp_frac) * 4))       # a phase per quarter hp
    phase = _NEX_ORDER[phase_idx]
    if m.get("nex_phase") != phase:
        m["nex_phase"] = phase
        color, cry = _NEX_PHASES[phase]
        say(cry, color, "bold")
        animate(_fx((NEX_ART, "grey"), (NEX_ART, color, "bold")),
                delay=0.12, center=True)
    atype = "magic" if phase in ("smoke", "shadow") else "ranged"
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    p_def_roll = _player_def_roll(p, atype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, m["max_hit"])
        if p.prayer_protects(atype):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        print("  " + paint(f"Nex strikes for {dmg}.", "bred") + "  "
              + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        if dmg > 0 and p.hp > 0:
            if phase == "blood":                    # siphons your blood
                heal = min(max(1, dmg // 4), m["hp"] - m["cur"])
                m["cur"] += heal
                print("  " + paint(f"She drinks it in — Nex heals {heal}.",
                                   "bred"))
            elif phase == "shadow":                 # shadow saps your stats
                sd = getattr(p, "stat_drain", None) or {}
                p.stat_drain = sd
                for s in ("attack", "strength", "defence"):
                    sd[s] = sd.get(s, 0) + 1
                print("  " + paint("Shadow drains your strength. (-1 combat "
                                   "stats)", "purple"))
            elif phase == "ice" and not getattr(p, "frozen", False) \
                    and random.random() < 0.4:
                p.frozen = True
                print("  " + paint("A prison of ice locks around you — "
                                   "FROZEN!", "bcyan"))
    else:
        print("  " + paint("You throw yourself clear of the blow.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer "
                               "points).", "bmagenta"))
    return "died" if p.hp <= 0 else None


def _nex_intro(name):
    return _fx((NEX_ART, "grey", "dim"), (NEX_ART, "bwhite"),
               (NEX_ART, "purple", "bold"), (NEX_ART, "bred", "bold"))


def _nex_death(name):
    return _fx((NEX_ART, "bred"), (NEX_ART, "bcyan", "dim"),
               (NEX_ART, "grey", "dim"))


_add_mob("nex",
    {"abonus": 55, "atktype": ["magic", "ranged"], "att": 300, "cb": 1001,
     "dstab": 130, "dslash": 130, "dcrush": 130, "dmagic": 130,
     "drange": 130, "def": 140, "hp": 400, "maxhit": 26, "str": 250,
     "weak": "stab"},
    [("torva full helm", 1, 1, 0.03), ("torva platebody", 1, 1, 0.02),
     ("torva platelegs", 1, 1, 0.02), ("zaryte crossbow", 1, 1, 0.02),
     ("nexling", 1, 1, 0.1), ("blood rune", 30, 90, 1.0),
     ("death rune", 30, 90, 1.0), ("coins", 20000, 60000, 1.0)],
    members=True)
MONSTERS["nex"]["boss"] = True
MONSTERS["nex"]["rank"] = "boss"
_BOSSES.add("nex")
BOSS_TURN["nex"] = _nex_take_turn
BOSS_INTRO["nex"] = _nex_intro
BOSS_DEATH["nex"] = _nex_death
MONSTER_ART["nex"] = NEX_ART

# Nex's frozen prison, off the God Wars entrance, behind a 40-kill door.
ROOMS.update({
    "ancient_prison": dict(name="The Ancient Prison",
        desc="A vault older than the gods' war, sealed in black ice. "
             "Zarosian followers — the last of the Ancients — stand "
             "eternal guard, and behind a frozen door of forty locks, "
             "something with wings waits to wake.",
        exits={"out": "gwd_entrance", "frozen door": "nex_lair"},
        monsters=["spiritual warrior"], gwd=True, hostile=True,
        members=True),
    "nex_lair": dict(name="Nex's Lair",
        desc="A cathedral of ice around a single throne. NEX opens four "
             "eyes — smoke, shadow, blood and ice — and rises. \"There "
             "is no escape.\"",
        exits={"out": "ancient_prison"},
        monsters=["nex"], members=True,
        kc_lock=("ancient", 40)),
})
ROOMS["gwd_entrance"]["exits"]["prison"] = "ancient_prison"
ROOMS["gwd_entrance"]["desc"] += (" A side-passage of black ice descends to "
                                  "an ANCIENT PRISON ('prison') — colder "
                                  "than the war above.")
REGIONS.update({"ancient_prison": "Wilderness", "nex_lair": "Wilderness"})

# spiritual warriors here feed the 'ancient' kill count that opens Nex's door
_prev_victory_nex = _victory


def _victory(p, m):                                 # noqa: F811 (wraps prior)
    _prev_victory_nex(p, m)
    if m["name"] == "spiritual warrior" and p.location == "ancient_prison":
        kc = getattr(p, "gwd_kc", None)
        if kc is None:
            kc = p.gwd_kc = {}
        kc["ancient"] = kc.get("ancient", 0) + 1
        say(f"  Ancient kill count: {kc['ancient']}/40 "
            "(the frozen door listens).", "bcyan")


# ===========================================================================
#  THE THEATRE OF BLOOD  (Ver Sinhaza — three acts to Verzik Vitur)
# ===========================================================================
# --- the scythe & vampyric arsenal -------------------------------------------------
add_item("scythe of vitur", 15_000_000, members=True, equip={
    "slot": "weapon", "astab": 30, "aslash": 110, "acrush": 70, "str": 105,
    "two_handed": True, "req": {"attack": 80, "strength": 80}})
EFFECT_NOTES["scythe of vitur"] = ("a vampyre matriarch's scythe — it "
                                   "reaps in a wide arc, the deadliest "
                                   "slash ever forged")
add_item("justiciar faceguard", 5_000_000, members=True, equip={
    "slot": "head", "dstab": 65, "dslash": 68, "dcrush": 71, "dmagic": 5,
    "drange": 70, "req": {"defence": 75}})
EFFECT_NOTES["justiciar faceguard"] = ("saradomin justiciar plate, recovered "
                                       "from the Theatre — a wall of defence")
add_item("avernic defender", 4_000_000, members=True, equip={
    "slot": "shield", "astab": 30, "aslash": 30, "acrush": 30, "str": 8,
    "dstab": 65, "dslash": 68, "dcrush": 71, "req": {"defence": 70}})
EFFECT_NOTES["avernic defender"] = ("the finest defender in Gielinor — "
                                    "offhand offence and defence both")

# --- the three acts ------------------------------------------------------------------
MAIDEN_ART = r"""
        .-=========-.
       / (o)     (o) \      THE MAIDEN OF
      |    \  ^  /    |       SUGADINTI —
       \    '---'    /        blood boils up!
        './|_____|\.'
      ~~~ (  ) (  ) ~~~
"""
XARPUS_ART = r"""
         ___________
        /  \_/ \_/  \       XARPUS —
       | (o)  .  (o) |       the acid-spitter
        \  '-----'  /         drags itself close.
       __\_|_|_|_/__
      /  //     \\  \
"""
VERZIK_ART = r"""
        __/VVVV\__
       / (O)  (O) \        VERZIK VITUR —
      |  \  ||  /  |        matriarch of Ver Sinhaza,
      |   '-VV-'   |         mistress of the Theatre.
       \__|    |__/
      __/  \  /  \__
     /   \  ||  /   \
    ~     ''    ''    ~
"""


def _maiden_bloodspawn(p, m, dmg):
    if dmg > 0 and random.random() < 0.4:
        extra = min(random.randint(3, 8), max(0, p.hp - 1))
        if extra:
            p.hp -= extra
            m["cur"] = min(m["hp"], m["cur"] + extra)
            print("  " + paint(f"Blood-spawn skitter in — {extra} more, and "
                               "the Maiden drinks it.", "bred"))


def _xarpus_venom(p, m, dmg):
    if dmg > 0 and getattr(p, "poison", 0) < 4 and random.random() < 0.5:
        p.poison = 4
        print("  " + paint("Xarpus spits acid — VENOM burns in.", "green"))


def _verzik_web(p, m, dmg):
    if dmg > 0 and not getattr(p, "frozen", False) and random.random() < 0.35:
        p.frozen = True
        print("  " + paint("Verzik's web pins you fast — FROZEN!", "purple"))


MAIDEN_ATTACKS = [
    {"label": "a tide of boiling blood", "verb": "raises",
     "color": ("bred", "bold"), "builder": _fx_hellfire,
     "mult": 1.1, "w": 3, "atype": "magic", "effect": _maiden_bloodspawn},
    {"label": "a raking claw", "verb": "lashes with",
     "color": ("bred",), "builder": _fx_jaws,
     "mult": 0.95, "w": 2, "atype": "slash"},
]
XARPUS_ATTACKS = [
    {"label": "a mouthful of acid", "verb": "spits",
     "color": ("green", "bold"), "builder": _fx_miasma,
     "mult": 1.05, "w": 3, "atype": "ranged", "effect": _xarpus_venom},
    {"label": "a sweep of barbed legs", "verb": "scythes with",
     "color": ("bgreen",), "builder": _fx_tail,
     "mult": 0.95, "w": 2, "atype": "stab"},
]
VERZIK_ATTACKS = [
    {"label": "a bolt of raw blood-magic", "verb": "hurls",
     "color": ("bred", "bold"), "builder": _fx_bolt,
     "mult": 1.15, "w": 3, "atype": "magic"},
    {"label": "a cage of crimson web", "verb": "weaves",
     "color": ("purple", "bold"), "builder": _fx_web,
     "mult": 0.9, "w": 2, "atype": "ranged", "effect": _verzik_web},
    {"label": "a matriarch's lunge", "verb": "strikes with",
     "color": ("bmagenta", "bold"), "builder": _fx_charge,
     "mult": 1.05, "w": 2, "atype": "stab"},
]

_TOB = {
    "the maiden": (MAIDEN_ART, MAIDEN_ATTACKS,
        {"abonus": 45, "atktype": ["magic", "slash"], "att": 200,
         "cb": 560, "dstab": 100, "dslash": 100, "dcrush": 80,
         "dmagic": 100, "drange": 100, "def": 150, "hp": 280,
         "maxhit": 22, "str": 190, "weak": "crush"},
        [("coins", 8000, 20000, 1.0), ("blood rune", 20, 60, 0.8)]),
    "xarpus": (XARPUS_ART, XARPUS_ATTACKS,
        {"abonus": 47, "atktype": ["ranged", "stab"], "att": 210,
         "cb": 580, "dstab": 105, "dslash": 105, "dcrush": 90,
         "dmagic": 100, "drange": 105, "def": 160, "hp": 300,
         "maxhit": 23, "str": 195, "weak": "crush"},
        [("coins", 9000, 22000, 1.0), ("uncut diamond", 1, 3, 0.5)]),
    "verzik vitur": (VERZIK_ART, VERZIK_ATTACKS,
        {"abonus": 55, "atktype": ["magic", "ranged", "stab"], "att": 260,
         "cb": 1040, "dstab": 130, "dslash": 130, "dcrush": 110,
         "dmagic": 130, "drange": 130, "def": 220, "hp": 420,
         "maxhit": 27, "str": 240, "weak": "crush"},
        [("scythe of vitur", 1, 1, 0.02),
         ("justiciar faceguard", 1, 1, 0.03),
         ("avernic defender", 1, 1, 0.05), ("blood rune", 40, 120, 1.0),
         ("coins", 25000, 70000, 1.0)]),
}
for _b, (_art, _atk, _st, _drops) in _TOB.items():
    _add_mob(_b, _st, _drops, members=True)
    MONSTERS[_b]["boss"] = True
    MONSTERS[_b]["rank"] = "boss"
    _BOSSES.add(_b)
    BOSS_TURN[_b] = (lambda atk: (lambda p, m:
                                  _boss_take_turn(p, m, atk)))(_atk)
    MONSTER_ART[_b] = _art

# --- the theatre --------------------------------------------------------------------
ROOMS.update({
    "ver_sinhaza": dict(name="Ver Sinhaza",
        desc="A drowned vampyre town on Morytania's east coast, every "
             "window lit red. At its heart looms the THEATRE OF BLOOD — "
             "and the vampyre LADY who runs the door studies you like "
             "a ticket-holder ('talk'). The theatre gapes within "
             "('theatre').",
        exits={"west": "port_phasmatys", "theatre": "tob_maiden"},
        npc="theatre_of_blood", members=True),
    "tob_maiden": dict(name="Theatre of Blood — Act I",
        desc="The first stage: a pit of rising blood where the MAIDEN OF "
             "SUGADINTI holds court. A blood-slick exit leads back to the "
             "lobby ('leave').",
        exits={"leave": "ver_sinhaza"}, members=True,
        qlock=("theatre_of_blood", ["maiden", "xarpus", "verzik",
                                    "complete"],
               "The Theatre admits no one who hasn't paid the Lady's "
               "price. (speak to her at Ver Sinhaza)")),
    "tob_xarpus": dict(name="Theatre of Blood — Act II",
        desc="The stage shifts: a sunken arena of acid and bone where "
             "XARPUS, all eyes and venom, waits to be entertained "
             "('leave' quits the raid).",
        exits={"leave": "ver_sinhaza"}, members=True, quest_entry=True),
    "tob_verzik": dict(name="Theatre of Blood — Finale",
        desc="The grand stage, red-curtained and roaring. VERZIK VITUR "
             "descends from her throne to a standing ovation of the "
             "damned. \"Let us give them a SHOW.\" ('leave' quits)",
        exits={"leave": "ver_sinhaza"}, members=True, quest_entry=True),
})
ROOMS["port_phasmatys"]["exits"]["coast"] = "ver_sinhaza"
ROOMS["port_phasmatys"]["desc"] += (" The red lights of Ver Sinhaza burn "
                                    "along the coast east ('coast').")
REGIONS.update({"ver_sinhaza": "Morytania", "tob_maiden": "Morytania",
                "tob_xarpus": "Morytania", "tob_verzik": "Morytania"})
TRAVEL_HUBS["ver sinhaza"] = "ver_sinhaza"
TRAVEL_NAMES.append("Ver Sinhaza")

# --- The Theatre of Blood (quest-as-raid, 4 QP) ----------------------------------------
ALL_QUESTS["theatre_of_blood"] = "The Theatre of Blood"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["theatre_of_blood"] = 4
NPC_NAMES["theatre_of_blood"] = "the Lady of Ver Sinhaza"
QUEST_STARTS["theatre_of_blood"] = "the Lady of Ver Sinhaza (sail 'coast' " \
                                   "east of Port Phasmatys)"
QUEST_HINTS["theatre_of_blood"] = {
    "maiden": "enter the theatre and best the Maiden of Sugadinti (Act I)",
    "xarpus": "survive Xarpus, the acid-spitter (Act II)",
    "verzik": "face VERZIK VITUR herself for the scythe (Finale)",
}


def talk_tob_lady(p):
    stage = _q(p, "theatre_of_blood")
    if stage == "not_started":
        banner("Quest Start: The Theatre of Blood", color="purple",
               line_color="bmagenta")
        say("The Lady smiles, all teeth: \"An outsider, seeking the "
            "stage? How BRAVE. Three acts, adventurer — the Maiden, "
            "Xarpus, and my mistress VERZIK VITUR at the finale. Survive "
            "them and the scythe is yours. Die, and you were only ever "
            "the warm-up.\" She waves you through ('theatre').")
        p.quests["theatre_of_blood"] = "maiden"
    elif stage in ("maiden", "xarpus", "verzik"):
        hint = QUEST_HINTS["theatre_of_blood"].get(stage, "")
        say(f"The Lady: \"The show must go on. {hint.capitalize()}.\"")
    elif stage == "complete":
        say("The Lady inclines her head: \"You gave them a SHOW. Ver "
            "Sinhaza will speak of it for a century. Come back anytime — "
            "the theatre is always hungry.\"")


QUEST_TALK["theatre_of_blood"] = talk_tob_lady

# each act's boss is present only during its stage
for _b, _room, _stg in [("the maiden", "tob_maiden", "maiden"),
                        ("xarpus", "tob_xarpus", "xarpus"),
                        ("verzik vitur", "tob_verzik", "verzik")]:
    QUEST_SPAWNS.append(
        (_room, _b,
         (lambda s: lambda pl: _q(pl, "theatre_of_blood") == s)(_stg)))


# --- kill hook: act by act, then the matriarch ----------------------------------------
_prev_quest_on_kill_tob = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811 (wraps prior)
    _prev_quest_on_kill_tob(p, target)
    stage = _q(p, "theatre_of_blood")
    if target == "the maiden" and stage == "maiden":
        p.quests["theatre_of_blood"] = "xarpus"
        p.location = "tob_xarpus"
        say("The Maiden bursts like a struck vein — and the stage sinks, "
            "carrying you to Act II. XARPUS is already watching.",
            "bred", "bold")
        cmd_look(p, "")
    elif target == "xarpus" and stage == "xarpus":
        p.quests["theatre_of_blood"] = "verzik"
        p.location = "tob_verzik"
        say("Xarpus folds up, still hissing, and the red curtain rises on "
            "the FINALE. VERZIK VITUR takes the stage.", "bred", "bold")
        cmd_look(p, "")
    elif target == "verzik vitur" and stage == "verzik":
        show_art(ART_QUEST, "gold", center=True)
        banner("THEATRE COMPLETE: VERZIK VITUR SLAIN", color="byellow",
               line_color="gold")
        say("Verzik Vitur falls from her own stage to silence, then to a "
            "roar — and the SCYTHE OF VITUR is yours, still warm. The "
            "deadliest weapon in Gielinor. 40,000 attack and 40,000 "
            "strength xp awarded. The Lady says the theatre is always "
            "open ('theatre' from Ver Sinhaza).", "bgreen")
        p.gain_xp("attack", 40000)
        p.gain_xp("strength", 40000)
        p.add("scythe of vitur")
        p.quests["theatre_of_blood"] = "complete"
        p.location = "ver_sinhaza"
