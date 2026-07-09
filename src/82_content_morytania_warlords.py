# ===========================================================================
#  MORYTANIA COMPLETION  (Phasmatys, Fenkenstrain, Mos Le'Harmless, SLEPE)
# ===========================================================================
# East of Canifis the dead do business: Port Phasmatys banks in silence
# and grinds bones at the Ectofuntus, Dr Fenkenstrain stitches in his
# castle, pirates drink off Mos Le'Harmless while CAVE HORRORS wear the
# dark below — and in plague-hushed Slepe, THE NIGHTMARE feeds on sleep.

# --- items -------------------------------------------------------------------
add_item("black mask", 800000, members=True, equip={
    "astab": 1, "aslash": 1, "acrush": 1, "dstab": 6, "dslash": 6,
    "dcrush": 6, "drange": 5, "slot": "head", "req": {"defence": 10}})
EFFECT_NOTES["black mask"] = ("+15% accuracy and damage against your "
                              "slayer task (the slayer helmet's dark "
                              "heart)")
add_item("bottle of rum", 30, heal=5, members=True)
add_item("ring of charos", 1200, members=True,
         equip={"slot": "ring", "dmagic": 2})
EFFECT_NOTES["ring of charos"] = ("Fenkenstrain's payment — a charming "
                                  "little thing")
add_item("nightmare staff", 350000, members=True, equip={
    "amagic": 16, "dmagic": 5, "mdmg": 15, "acrush": 25, "str": 30,
    "slot": "weapon", "req": {"magic": 65, "hitpoints": 50}})
EFFECT_NOTES["nightmare staff"] = ("dreams given heft: +15% magic damage "
                                   "raises your spell cap")
SHOPS["pirate"] = {"bottle of rum": 30, "harpoon": 5, "bread": 10}

# --- ectofuntus ----------------------------------------------------------------
def cmd_worship(p, arg):
    if not ROOMS[p.location].get("ectofuntus"):
        say("There's no Ectofuntus here — the ghosts grind bones at Port "
            "Phasmatys.", "grey")
        return
    bone = arg.strip().lower()
    if not bone:
        bone = next((b for b in ("dragon bones", "dagannoth bones",
                                 "big bones", "bones") if p.has(b)), "")
    if not bone or bone not in ITEMS or "bury" not in ITEMS.get(bone, {}):
        say("Bring bones to grind — the Ectofuntus takes any of them.")
        return None
    if not p.has(bone):
        say(f"You have no {bone}.")
        return None
    p.take(bone)
    skill, xp = ITEMS[bone]["bury"]
    xp = int(xp * 2.5)                  # slime + bonemeal beats a hole
    say(f"You grind the {bone}, add ectoplasm, and pour the mix into the "
        "Ectofuntus. Green fire answers.")
    p.gain_xp(skill, xp)
    return True


HANDLERS["worship"] = cmd_worship

# --- creatures ------------------------------------------------------------------
_add_mob("experiment",
    {"abonus": 0, "atktype": ["crush"], "att": 10, "cb": 25, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 5, "drange": 5, "def": 10,
     "hp": 100, "maxhit": 3, "str": 20, "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 1, 20, 0.3)],
    members=True, rank="easy")
_add_mob("the experiment",
    {"abonus": 15, "atktype": ["crush"], "att": 45, "cb": 51, "dstab": 25,
     "dslash": 25, "dcrush": 20, "dmagic": 15, "drange": 25, "def": 40,
     "hp": 80, "maxhit": 6, "str": 50, "weak": "crush"},
    [("big bones", 1, 1, 1.0)], members=True, rank="hard")
_add_mob("pirate",
    {"abonus": 12, "atktype": ["slash"], "att": 50, "cb": 57, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 10, "drange": 25, "def": 45,
     "hp": 60, "maxhit": 7, "str": 52, "weak": "stab"},
    [("bones", 1, 1, 1.0), ("coins", 20, 200, 0.9),
     ("bottle of rum", 1, 1, 0.3)], members=True, rank="hard")
_add_mob("cave horror",
    {"abonus": 25, "atktype": ["crush"], "att": 70, "cb": 80, "dstab": 40,
     "dslash": 40, "dcrush": 35, "dmagic": 30, "drange": 40, "def": 60,
     "hp": 55, "maxhit": 8, "str": 75, "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 40, 250, 0.7),
     ("black mask", 1, 1, 0.01), ("grimy ranarr", 1, 1, 0.08),
     ("grimy harralander", 1, 2, 0.2)], members=True, rank="elite")
MONSTERS["cave horror"]["slayer_req"] = 58
DURADEL_TARGETS.append("cave horror")

# --- THE NIGHTMARE ----------------------------------------------------------------
NIGHTMARE_ART = r"""
        .-.      _______      .-.
       (   `-._.'       `._.-'   )
        )    ___    _    ___    (
       (    ( o )  (_)  ( o )    )
        )    `-'  _____  `-'    (
       (         (     )        )
        `-.___.-' `---' `-.___.-'
             )_____________(
"""


def _nightmare_intro(name):
    return [_tint(NIGHTMARE_ART, "grey", "dim"),
            _tint(NIGHTMARE_ART, "purple", "bold"),
            _tint(NIGHTMARE_ART, "bmagenta", "bold")]


def _nightmare_death(name):
    return [_tint(NIGHTMARE_ART, "bmagenta"),
            _tint(NIGHTMARE_ART, "grey", "dim")]


def _nightmare_spores(p, m, dmg):
    if random.random() < 0.35 and not p.frozen:
        p.frozen = True
        print("  " + paint("Numbing spores burst around you — your next "
                           "attack will falter! (sleep)", "bmagenta"))


NIGHTMARE_ATTACKS = [
    {"label": "a husk-handed swipe", "verb": "lashes out with",
     "color": ("purple", "bold"),
     "builder": lambda: [_tint(NIGHTMARE_ART, "purple", "bold")],
     "mult": 1.2, "w": 3, "atype": "crush"},
    {"label": "a surge of drowning shadow", "verb": "wills forth",
     "color": ("bmagenta", "bold"),
     "builder": lambda: [_tint(NIGHTMARE_ART, "bmagenta", "bold")],
     "mult": 1.1, "w": 3, "atype": "magic"},
    {"label": "a cloud of grave-spores", "verb": "exhales",
     "color": ("green",),
     "builder": lambda: [_tint(NIGHTMARE_ART, "green")],
     "mult": 0.8, "w": 2, "atype": "magic", "effect": _nightmare_spores},
]


def _nightmare_take_turn(p, m):
    for thr, flag in ((200, "night_p2"), (100, "night_p3")):
        if m["cur"] <= thr and not m.get(flag):
            m[flag] = True
            m["cur"] = min(m["hp"], m["cur"] + 40)
            say("Sleepwalkers shamble from the dark and the Nightmare "
                "DRINKS their dreams — her wounds knit closed! (+40)",
                "bmagenta", "bold")
            return None
    return _boss_take_turn(p, m, NIGHTMARE_ATTACKS)


_add_mob("the nightmare",
    {"abonus": 45, "atktype": ["crush", "magic"], "att": 180, "cb": 814,
     "dstab": 70, "dslash": 70, "dcrush": 55, "dmagic": 70, "drange": 70,
     "def": 100, "hp": 300, "maxhit": 20, "str": 170, "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 5000, 20000, 1.0),
     ("nightmare staff", 1, 1, 0.01), ("grimy ranarr", 2, 5, 0.4),
     ("uncut diamond", 1, 2, 0.25)], members=True)
MONSTERS["the nightmare"]["boss"] = True
MONSTERS["the nightmare"]["rank"] = "boss"
_BOSSES.add("the nightmare")
BOSS_TURN["the nightmare"] = _nightmare_take_turn
BOSS_INTRO["the nightmare"] = _nightmare_intro
BOSS_DEATH["the nightmare"] = _nightmare_death
MONSTER_ART["the nightmare"] = NIGHTMARE_ART

# --- the region --------------------------------------------------------------------
ROOMS.update({
    "port_phasmatys": dict(name="Port Phasmatys",
        desc="A harbour town of the polite dead: ghost bankers, ghost "
             "dockers, ghost queues. The ECTOFUNTUS burns green over the "
             "town ('worship' your bones for rich prayer xp), and a "
             "charter ship rocks at the quay ('sail').",
        exits={"west": "canifis", "sail": "mos_le_harmless",
               "south": "slepe"},
        bank=True, ectofuntus=True, members=True),
    "fenkenstrain_castle": dict(name="Fenkenstrain's Castle",
        desc="A lightning-rodded pile above a graveyard that won't stay "
             "filled. Dr Fenkenstrain needs a steady hand, and his "
             "escaped EXPERIMENTS lumber harmlessly about — tough as "
             "walls, slow as grief.",
        exits={"south": "canifis"},
        npc="fenkenstrain", monsters=["experiment"], members=True),
    "mos_le_harmless": dict(name="Mos Le'Harmless",
        desc="A pirate haven of rum, dice and regret. The tavern never "
             "shuts, and a cave mouth in the cliffs breathes cold air "
             "('caves').",
        exits={"sail": "port_phasmatys", "caves": "harmless_caves"},
        bank=True, shop="pirate", monsters=["pirate"], members=True),
    "harmless_caves": dict(name="Mos Le'Harmless Caves",
        desc="Wet black tunnels where the dark itself grows faces. CAVE "
             "HORRORS stalk between the stalagmites — slayers prize the "
             "masks they wear.",
        exits={"out": "mos_le_harmless"},
        monsters=["cave horror"], hostile=True, members=True),
    "slepe": dict(name="Slepe",
        desc="A town asleep on its feet: doors ajar, hearths cold, "
             "townsfolk curled where they fell. Something in the "
             "cathedral is EATING their dreams ('cathedral').",
        exits={"north": "port_phasmatys", "cathedral": "nightmare_arena"},
        members=True),
    "nightmare_arena": dict(name="The Sisterhood Sanctuary",
        desc="Beneath Slepe's cathedral, sleepers ring a pit of violet "
             "mist. THE NIGHTMARE hangs in the air above them, vast and "
             "wrong, drinking sleep.",
        exits={"out": "slepe"},
        monsters=["the nightmare"], members=True),
})
ROOMS["canifis"]["exits"]["east"] = "port_phasmatys"
ROOMS["canifis"]["exits"]["north"] = "fenkenstrain_castle"
ROOMS["canifis"]["desc"] += (" The road east runs for Port Phasmatys, and "
                             "Fenkenstrain's castle broods north.")
for _rm in ("port_phasmatys", "fenkenstrain_castle", "mos_le_harmless",
            "harmless_caves", "slepe", "nightmare_arena"):
    REGIONS[_rm] = "Morytania"
TRAVEL_HUBS["phasmatys"] = "port_phasmatys"
TRAVEL_NAMES.append("Phasmatys")

# --- Creature of Fenkenstrain (1 QP) ---------------------------------------------
ALL_QUESTS["fenkenstrain"] = "Creature of Fenkenstrain"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["fenkenstrain"] = 1
NPC_NAMES["fenkenstrain"] = "Dr Fenkenstrain"
QUEST_STARTS["fenkenstrain"] = "Dr Fenkenstrain, his castle north of Canifis"
QUEST_HINTS["fenkenstrain"] = {
    "parts": "bring the doctor 5 big bones, a needle and thread",
    "creature": "his creature broke loose — 'fight the experiment'!",
    "loose": "report the escape to Dr Fenkenstrain",
}


def talk_fenkenstrain(p):
    stage = _q(p, "fenkenstrain")
    if stage == "not_started":
        banner("Quest Start: Creature of Fenkenstrain", color="purple",
               line_color="bmagenta")
        say("Dr Fenkenstrain: \"Science requires MATERIALS. Bring me five "
            "big bones, a needle and thread, and together we shall give "
            "death a stern talking-to.\"")
        p.quests["fenkenstrain"] = "parts"
    elif stage == "parts":
        if p.count("big bones") >= 5 and p.has("needle") and p.has("thread"):
            p.take("big bones", 5)
            p.take("needle")
            p.take("thread")
            p.quests["fenkenstrain"] = "creature"
            say("The doctor stitches, hums, and throws the great switch. "
                "LIGHTNING — and the thing on the slab sits up, looks at "
                "you both... and goes BERSERK! \"Contain it! CONTAIN "
                "IT!\"", "bmagenta", "bold")
        else:
            say("Dr Fenkenstrain: \"Five big bones, a needle, thread! "
                "Graveyards are FULL of donors, none of them using their "
                "bones.\"")
    elif stage == "creature":
        say("Dr Fenkenstrain (from behind a cabinet): \"CONTAIN IT! "
            "'fight the experiment'!\"")
    elif stage == "loose":
        _complete_banner("Creature of Fenkenstrain")
        say("Dr Fenkenstrain mops his brow: \"Science thanks you. Take "
            "this ring — I shan't be needing charm where I'm hiding.\" "
            "4,000 crafting and prayer xp awarded!", "gold", "bold")
        p.add("ring of charos")
        p.gain_xp("crafting", 4000)
        p.gain_xp("prayer", 4000)
        p.quests["fenkenstrain"] = "complete"
    elif stage == "complete":
        say("Dr Fenkenstrain: \"The experiments outside? Harmless. "
            "Mostly. Splendid training, actually.\"")


QUEST_TALK["fenkenstrain"] = talk_fenkenstrain


# ===========================================================================
#  WILDERNESS WARLORDS  (the boss trio, Scorpia, Chaos Ele, Kolodion, CORP)
# ===========================================================================
# West of the deep Wilderness the wastes belong to monsters with names:
# Callisto the bear, Venenatis the weaver, Vet'ion the twice-buried,
# Scorpia in her pit, the Chaos Elemental over the mud — Kolodion's Mage
# Arena where only magic counts — and in a cave of old dark, the
# CORPOREAL BEAST, whose hide only spears pierce.

# --- items -----------------------------------------------------------------
add_item("tyrannical ring", 400000, members=True,
         equip={"slot": "ring", "acrush": 4, "dcrush": 8})
add_item("treasonous ring", 400000, members=True,
         equip={"slot": "ring", "astab": 4, "dstab": 8})
add_item("ring of the gods", 500000, members=True,
         equip={"slot": "ring", "prayer": 4, "dstab": 2, "dslash": 2,
                "dcrush": 2})
add_item("dragon pickaxe", 900000, members=True, tool="pickaxe", tier=7,
         equip={"slot": "weapon", "astab": 28, "acrush": 22, "str": 30,
                "req": {"attack": 60, "mining": 61}})
EFFECT_NOTES["dragon pickaxe"] = ("the miner's dream — its point counts "
                                  "as +3 mining levels while you dig")
add_item("odium shard", 60000, members=True)
add_item("malediction shard", 60000, members=True)
add_item("odium ward", 220000, members=True,
         equip={"slot": "shield", "arange": 12, "drange": 30, "dstab": 20,
                "dslash": 20, "dcrush": 20, "req": {"defence": 60}})
add_item("malediction ward", 220000, members=True,
         equip={"slot": "shield", "amagic": 12, "dmagic": 30, "dstab": 20,
                "dslash": 20, "dcrush": 20, "req": {"defence": 60}})
CRAFT_RECIPES.update({
    "odium ward": ("odium shard", 3, 75, 300),
    "malediction ward": ("malediction shard", 3, 75, 300),
})
add_item("spirit shield", 150000, members=True,
         equip={"slot": "shield", "dstab": 30, "dslash": 30, "dcrush": 30,
                "dmagic": 30, "drange": 30, "req": {"defence": 65}})
add_item("holy elixir", 100000, members=True)
add_item("blessed spirit shield", 600000, members=True,
         equip={"slot": "shield", "dstab": 45, "dslash": 45, "dcrush": 45,
                "dmagic": 45, "drange": 45, "prayer": 3,
                "req": {"defence": 70, "prayer": 60}})
add_item("god cape", 80000, members=True,
         equip={"slot": "cape", "amagic": 10, "dmagic": 10})
EFFECT_NOTES["god cape"] = ("imbued at the Mage Arena by the god you "
                            "chose — the mage's cape")
add_item("god staff", 60000, members=True,
         equip={"slot": "weapon", "amagic": 6, "dmagic": 2,
                "req": {"magic": 60}})


def cmd_bless(p, arg):
    """Spirit shield + holy elixir at an altar -> blessed spirit shield."""
    if not ROOMS[p.location].get("prayer_altar"):
        say("You need an altar to bless anything.")
        return
    if not (p.has("spirit shield") and p.has("holy elixir")):
        say("Blessing takes a spirit shield and a holy elixir — the "
            "Corporeal Beast guards both.")
        return
    if p.lvl("prayer") < 85:
        say("You need prayer level 85 to channel the blessing.")
        return
    p.take("spirit shield")
    p.take("holy elixir")
    p.add("blessed spirit shield")
    p.gain_xp("prayer", 1500)
    say("Light pools in the shield's heart — you raise a BLESSED SPIRIT "
        "SHIELD.", "gold", "bold")
    return True


HANDLERS["bless"] = cmd_bless

# --- the warlords ---------------------------------------------------------------
def _chaos_disrobe(p, m, dmg):
    slots = [s for s, it in p.equipment.items() if it and s != "weapon"]
    if slots and random.random() < 0.4:
        s = random.choice(slots)
        it = p.equipment[s]
        p.equipment[s] = None
        p.add(it)
        print("  " + paint(f"A tendril flicks your {it} into the mud! "
                           "(re-equip it)", "bmagenta"))


def _scorpia_sting(p, m, dmg):
    if dmg > 0 and not getattr(p, "poison", 0) and random.random() < 0.5:
        p.poison = 3
        print("  " + paint("Scorpia's sting pumps venom into you — "
                           "POISONED!", "green"))


def _venenatis_web(p, m, dmg):
    if dmg > 0 and random.random() < 0.3:
        p.run_energy = max(0, getattr(p, "run_energy", 100) - 20)
        print("  " + paint("Sticky silk tangles your legs. (-20 run "
                           "energy)", "grey"))


_WARLORDS = {
    "callisto": (
        {"abonus": 45, "atktype": ["crush"], "att": 180, "cb": 470,
         "dstab": 40, "dslash": 75, "dcrush": 75, "dmagic": 70,
         "drange": 75, "def": 95, "hp": 255, "maxhit": 25, "str": 190,
         "weak": "stab"},
        [("big bones", 1, 1, 1.0), ("coins", 3000, 15000, 1.0),
         ("tyrannical ring", 1, 1, 0.04), ("dragon pickaxe", 1, 1, 0.03),
         ("grimy ranarr", 2, 5, 0.4)],
        [{"label": "a mauling charge", "verb": "barrels in with",
          "color": ("bred", "bold"), "builder": _fx_charge,
          "mult": 1.2, "w": 3, "atype": "crush"},
         {"label": "a ground-shaking roar", "verb": "erupts with",
          "color": ("orange",), "builder": _fx_roar,
          "mult": 0.9, "w": 2, "atype": "crush"}]),
    "venenatis": (
        {"abonus": 40, "atktype": ["magic"], "att": 170, "cb": 464,
         "dstab": 70, "dslash": 70, "dcrush": 40, "dmagic": 70,
         "drange": 70, "def": 90, "hp": 255, "maxhit": 23, "str": 160,
         "weak": "crush"},
        [("big bones", 1, 1, 1.0), ("coins", 3000, 15000, 1.0),
         ("treasonous ring", 1, 1, 0.04), ("dragon pickaxe", 1, 1, 0.03),
         ("grimy ranarr", 2, 5, 0.4)],
        [{"label": "a bolt of woven lightning", "verb": "spits",
          "color": ("bmagenta", "bold"), "builder": _fx_bolt,
          "mult": 1.1, "w": 3, "atype": "magic"},
         {"label": "a cast of clinging web", "verb": "throws",
          "color": ("grey",), "builder": _fx_web,
          "mult": 0.8, "w": 2, "atype": "ranged",
          "effect": _venenatis_web}]),
    "vet'ion": (
        {"abonus": 45, "atktype": ["crush"], "att": 175, "cb": 454,
         "dstab": 70, "dslash": 70, "dcrush": 45, "dmagic": 65,
         "drange": 70, "def": 90, "hp": 220, "maxhit": 24, "str": 180,
         "weak": "crush"},
        [("big bones", 1, 1, 1.0), ("coins", 3000, 15000, 1.0),
         ("ring of the gods", 1, 1, 0.04), ("dragon pickaxe", 1, 1, 0.03),
         ("grimy ranarr", 2, 5, 0.4)],
        [{"label": "a sledge of grave-iron", "verb": "swings",
          "color": ("purple", "bold"), "builder": _fx_smash,
          "mult": 1.15, "w": 3, "atype": "crush"},
         {"label": "a crackle of earth-lightning", "verb": "calls down",
          "color": ("bmagenta",), "builder": _fx_bolt,
          "mult": 1.0, "w": 2, "atype": "magic"}]),
    "scorpia": (
        {"abonus": 35, "atktype": ["stab"], "att": 140, "cb": 225,
         "dstab": 60, "dslash": 60, "dcrush": 40, "dmagic": 55,
         "drange": 60, "def": 80, "hp": 200, "maxhit": 16, "str": 140,
         "weak": "crush"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("odium shard", 1, 1, 0.2), ("malediction shard", 1, 1, 0.2),
         ("antipoison", 1, 2, 0.4)],
        [{"label": "her barbed tail", "verb": "whips over with",
          "color": ("green", "bold"), "builder": _fx_tail,
          "mult": 1.1, "w": 3, "atype": "stab", "effect": _scorpia_sting},
         {"label": "a crushing pincer", "verb": "snaps",
          "color": ("byellow",), "builder": _fx_smash,
          "mult": 1.0, "w": 2, "atype": "crush"}]),
    "chaos elemental": (
        {"abonus": 40, "atktype": ["magic", "ranged", "crush"], "att": 160,
         "cb": 305, "dstab": 65, "dslash": 45, "dcrush": 65, "dmagic": 65,
         "drange": 65, "def": 90, "hp": 250, "maxhit": 21, "str": 150,
         "weak": "slash"},
        [("coins", 3000, 12000, 1.0), ("dragon pickaxe", 1, 1, 0.03),
         ("uncut ruby", 1, 3, 0.4), ("blood rune", 5, 20, 0.5)],
        [{"label": "a lash of raw chaos", "verb": "whips out",
          "color": ("bmagenta", "bold"), "builder": _fx_bolt,
          "mult": 1.1, "w": 3, "atype": "magic"},
         {"label": "a discombobulating tendril", "verb": "flicks",
          "color": ("purple",), "builder": _fx_lash,
          "mult": 0.7, "w": 2, "atype": "ranged",
          "effect": _chaos_disrobe}]),
    "kolodion": (
        {"abonus": 45, "atktype": ["magic"], "att": 150, "cb": 204,
         "dstab": 80, "dslash": 80, "dcrush": 80, "dmagic": 60,
         "drange": 80, "def": 85, "hp": 170, "maxhit": 18, "str": 140,
         "weak": "magic"},
        [("god cape", 1, 1, 1.0), ("god staff", 1, 1, 1.0),
         ("blood rune", 10, 30, 1.0), ("coins", 1000, 5000, 1.0)],
        [{"label": "a searing bolt of pure magic", "verb": "hurls",
          "color": ("bblue", "bold"), "builder": _fx_bolt_blue,
          "mult": 1.1, "w": 3, "atype": "magic"},
         {"label": "a shapeshifted maul-swing", "verb": "morphs into",
          "color": ("purple",), "builder": _fx_smash,
          "mult": 0.9, "w": 2, "atype": "crush"}]),
    "corporeal beast": (
        {"abonus": 50, "atktype": ["magic", "stab"], "att": 220, "cb": 785,
         "dstab": 65, "dslash": 90, "dcrush": 90, "dmagic": 80,
         "drange": 90, "def": 110, "hp": 320, "maxhit": 26, "str": 220,
         "weak": "stab"},
        [("big bones", 1, 1, 1.0), ("coins", 8000, 25000, 1.0),
         ("spirit shield", 1, 1, 0.06), ("holy elixir", 1, 1, 0.03),
         ("uncut diamond", 2, 4, 0.5)],
        [{"label": "a gore of black horn", "verb": "lowers into",
          "color": ("grey", "bold"), "builder": _fx_charge,
          "mult": 1.15, "w": 3, "atype": "stab"},
         {"label": "a scything blast of dark energy", "verb": "exhales",
          "color": ("bmagenta", "bold"), "builder": _fx_darkness,
          "mult": 1.05, "w": 3, "atype": "magic"}]),
}
for _w, (_st, _drops, _atk) in _WARLORDS.items():
    _add_mob(_w, _st, _drops, members=True)
    MONSTERS[_w]["boss"] = True
    MONSTERS[_w]["rank"] = "boss"
    _BOSSES.add(_w)
    BOSS_TURN[_w] = (lambda atk: (lambda p, m: _boss_take_turn(p, m, atk)))(_atk)
MONSTERS["vet'ion"]["transform"] = True
MONSTERS["vet'ion"]["transform_msg"] = ("VET'ION collapses — and claws "
                                        "straight back out of the mud, "
                                        "wreathed in purple flame. "
                                        "TWICE-BURIED, TWICE-RISEN!")
MONSTERS["kolodion"]["mage_only"] = True
MONSTERS["corporeal beast"]["corporeal"] = True

# --- the wastes -------------------------------------------------------------------
ROOMS.update({
    "wilderness_wastes": dict(name="Western Wastes",
        desc="A mud-flat of old battlefields under a bruised sky. Lairs "
             "pock the wastes: a bear-den ('bear'), a web-choked hollow "
             "('spider'), a burial rift ('skeleton'), a scorpion pit "
             "('scorpion'), churned ground where the air argues with "
             "itself ('chaos'), Kolodion's arena ('arena') and a cave "
             "mouth of utter dark ('beast').",
        exits={"east": "deep_wilderness", "bear": "callisto_den",
               "spider": "venenatis_lair", "skeleton": "vetion_rift",
               "scorpion": "scorpia_pit", "chaos": "chaos_ele_lair",
               "arena": "mage_arena", "beast": "corp_cave"},
        monsters=["dark warrior", "green dragon"], hostile=True,
        members=True),
    "callisto_den": dict(name="Callisto's Den",
        desc="Bones of every size carpet the clearing. CALLISTO rises on "
             "his hind legs — a bear the size of a barn, and angrier.",
        exits={"out": "wilderness_wastes"},
        monsters=["callisto"], members=True),
    "venenatis_lair": dict(name="Venenatis' Hollow",
        desc="Webs thick as ship-rope sag between dead trees. VENENATIS "
             "descends slowly, tasting the air with her forelegs.",
        exits={"out": "wilderness_wastes"},
        monsters=["venenatis"], members=True),
    "vetion_rift": dict(name="Vet'ion's Rift",
        desc="A grave that wouldn't stay shut. VET'ION stands in the "
             "broken earth, purple fire in his empty eyes.",
        exits={"out": "wilderness_wastes"},
        monsters=["vet'ion"], members=True),
    "scorpia_pit": dict(name="Scorpia's Pit",
        desc="A chalk-white pit that clicks and rustles. SCORPIA scuttles "
             "up from the dark, tail curling overhead.",
        exits={"out": "wilderness_wastes"},
        monsters=["scorpia"], members=True),
    "chaos_ele_lair": dict(name="The Churned Ground",
        desc="The mud here is wrong — it flows uphill. THE CHAOS "
             "ELEMENTAL drifts over it, a storm with opinions.",
        exits={"out": "wilderness_wastes"},
        monsters=["chaos elemental"], members=True),
    "mage_arena": dict(name="The Mage Arena",
        desc="A ring of scorched obsidian in the wastes. KOLODION grins: "
             "'Rules are rules — MAGIC ONLY. Beat me and choose your "
             "god.' (his prize: a god cape and staff)",
        exits={"out": "wilderness_wastes"},
        monsters=["kolodion"], members=True),
    "corp_cave": dict(name="Cave of the Corporeal Beast",
        desc="Dark that eats your torchlight. THE CORPOREAL BEAST fills "
             "the cavern wall to wall — bring a SPEAR, or bring regret.",
        exits={"out": "wilderness_wastes"},
        monsters=["corporeal beast"], members=True),
})
ROOMS["deep_wilderness"]["exits"]["wastes"] = "wilderness_wastes"
for _rm in ("wilderness_wastes", "callisto_den", "venenatis_lair",
            "vetion_rift", "scorpia_pit", "chaos_ele_lair", "mage_arena",
            "corp_cave"):
    REGIONS[_rm] = "Wilderness"


