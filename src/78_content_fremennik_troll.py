# ===========================================================================
#  THE FREMENNIK PROVINCE  (the Trials, rock crabs, and the three Kings)
# ===========================================================================
# Rellekka lies north of Seers' Village. The Fremennik Trials earn you a
# Fremennik name and the sail to Waterbirth Island, where the Dagannoth
# Kings circle beneath the rock — a tribrid trio: magic fells Rex, arrows
# fell Prime, steel fells Supreme. Their rings have no equal.

# --- items -----------------------------------------------------------------
add_item("lyre", 40, members=True)
add_item("yak-hide", 60, members=True)
add_item("dagannoth bones", 110, bury=("prayer", 62), members=True)
add_item("helm of neitiznot", 55000, members=True,
         equip={"slot": "head", "dstab": 31, "dslash": 29, "dcrush": 34,
                "dmagic": 3, "drange": 30, "str": 3, "prayer": 3,
                "quest": "fremennik_trials"})
add_item("berserker ring", 45000, members=True,
         equip={"slot": "ring", "str": 4, "dstab": 4, "dslash": 4,
                "dcrush": 4})
add_item("warrior ring", 30000, members=True,
         equip={"slot": "ring", "aslash": 4, "dslash": 4})
add_item("archers ring", 42000, members=True,
         equip={"slot": "ring", "arange": 4, "drange": 4})
add_item("seers ring", 38000, members=True,
         equip={"slot": "ring", "amagic": 6, "dmagic": 6})
add_item("dragon axe", 61000, members=True, tool="axe", tier=7,
         equip={"slot": "weapon", "aslash": 38, "acrush": 32, "str": 42,
                "req": {"woodcutting": 61}})
EFFECT_NOTES["dragon axe"] = ("the finest axe in Gielinor — its edge counts "
                              "as +3 woodcutting levels while you chop")
EFFECT_NOTES["helm of neitiznot"] = ("the Jarl's gift: a berserker helm "
                                     "without the drawbacks, blessed for "
                                     "prayer")
SHOPS["neitiznot"] = {"helm of neitiznot": 55000, "harpoon": 5,
                      "lobster pot": 20}

# --- creatures ---------------------------------------------------------------
_add_mob("rock crab",
    {"abonus": 0, "atktype": ["crush"], "att": 5, "cb": 13, "dstab": 8,
     "dslash": 8, "dcrush": 8, "dmagic": 0, "drange": 8, "def": 5,
     "hp": 50, "maxhit": 1, "str": 10, "weak": "crush"},
    [("coins", 1, 12, 0.3), ("raw tuna", 1, 1, 0.1)],
    members=True, rank="easy")
_add_mob("yak",
    {"abonus": 0, "atktype": ["crush"], "att": 10, "cb": 22, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 0, "drange": 5, "def": 10,
     "hp": 50, "maxhit": 2, "str": 15, "weak": "stab"},
    [("yak-hide", 1, 1, 1.0), ("bones", 1, 1, 1.0)],
    members=True, rank="easy")
_add_mob("dagannoth",
    {"abonus": 30, "atktype": ["ranged"], "att": 80, "cb": 90, "dstab": 60,
     "dslash": 60, "dcrush": 60, "dmagic": 30, "drange": 60, "def": 70,
     "hp": 70, "maxhit": 9, "str": 80, "weak": "magic"},
    [("bones", 1, 1, 1.0), ("coins", 40, 220, 0.8),
     ("blood rune", 2, 6, 0.15), ("grimy ranarr", 1, 1, 0.05),
     ("steel arrow", 5, 20, 0.3)],
    members=True, rank="elite")
_add_mob("the draugen",
    {"abonus": 20, "atktype": ["magic"], "att": 60, "cb": 69, "dstab": 30,
     "dslash": 30, "dcrush": 20, "dmagic": 40, "drange": 30, "def": 50,
     "hp": 60, "maxhit": 7, "str": 60, "weak": "crush"},
    [("coins", 200, 500, 1.0)], members=True, rank="hard")
DURADEL_TARGETS.append("dagannoth")

# --- wave spells (magic's missing top end — Rex demands a real spellbook) ----
add_item("blood rune", 400, members=True)
SHOPS["rune"]["blood rune"] = 450
SPELLS.update({
    "wind wave":  {"type": "combat", "max": 17, "lvl": 62, "xp": 36,
                   "runes": {"air rune": 5, "blood rune": 1}},
    "water wave": {"type": "combat", "max": 18, "lvl": 65, "xp": 37.5,
                   "runes": {"water rune": 7, "air rune": 5, "blood rune": 1}},
    "earth wave": {"type": "combat", "max": 19, "lvl": 70, "xp": 40,
                   "runes": {"earth rune": 7, "air rune": 5, "blood rune": 1}},
    "fire wave":  {"type": "combat", "max": 20, "lvl": 75, "xp": 42.5,
                   "runes": {"fire rune": 7, "air rune": 5, "blood rune": 1}},
})

# --- the three Kings ----------------------------------------------------------
DK_ART = r"""
              ,--.___
         __.-'   \o  `\__
     _.-'    /\   \      `--.
   ,'   /\  /  \   \  /\     `.
  /    /  \/    \   \/  \      \
  ~^~^~/    ~^~^~\   ~^~^\~^~^~^~
"""

_DK_TINT = {"dagannoth rex": "bred", "dagannoth prime": "bcyan",
            "dagannoth supreme": "bgreen"}


def _dk_intro(name):
    c = _DK_TINT.get(name, "bcyan")
    return [_tint(DK_ART, "grey"), _tint(DK_ART, c, "bold")]


def _dk_death(name):
    c = _DK_TINT.get(name, "bcyan")
    return [_tint(DK_ART, c), _tint(DK_ART, "grey", "dim")]


# while you fight one King, the other two circle the lair
_DK_SNIPE = {
    "dagannoth rex": ("melee",
        "REX barrels through the shallows, jaws snapping at your blind side"),
    "dagannoth prime": ("magic",
        "PRIME rears from the water and spits a crackling bolt at your back"),
    "dagannoth supreme": ("ranged",
        "SUPREME wheels past and rakes you with a volley of spikes"),
}


def _dk_take_turn(p, m, attacks):
    if random.random() < 0.22:
        name = random.choice([k for k in _DK_SNIPE if k != m["name"]])
        style, flavor = _DK_SNIPE[name]
        print("  " + paint(flavor + "!", "bcyan"))
        if p.prayer_protects(style):
            print("  " + paint("Your prayer turns the ambush aside.", "teal"))
        else:
            dmg = random.randint(2, 13)
            p.hp -= dmg
            print("  " + paint(f"It strikes from nowhere for {dmg}. "
                               f"(protect from {style}!)", "bred"))
            if p.hp <= 0:
                return "died"
    return _boss_take_turn(p, m, attacks)


REX_ATTACKS = [
    {"label": "jaws like a ship's ram", "verb": "lunges with",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(DK_ART, "bred", "bold")],
     "mult": 1.2, "w": 3, "atype": "stab"},
    {"label": "a tail-sweep that shakes the cavern", "verb": "spins into",
     "color": ("orange",),
     "builder": lambda: [_tint(DK_ART, "orange")],
     "mult": 1.0, "w": 2, "atype": "crush"},
]
PRIME_ATTACKS = [
    {"label": "a bolt of deep-water lightning", "verb": "spits",
     "color": ("bcyan", "bold"),
     "builder": lambda: [_tint(DK_ART, "bcyan", "bold")],
     "mult": 1.2, "w": 3, "atype": "magic"},
    {"label": "a scalding geyser", "verb": "summons",
     "color": ("bblue",),
     "builder": lambda: [_tint(DK_ART, "bblue")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]
SUPREME_ATTACKS = [
    {"label": "a storm of barbed spikes", "verb": "launches",
     "color": ("bgreen", "bold"),
     "builder": lambda: [_tint(DK_ART, "bgreen", "bold")],
     "mult": 1.2, "w": 3, "atype": "ranged"},
    {"label": "a darting peck", "verb": "snaps out",
     "color": ("green",),
     "builder": lambda: [_tint(DK_ART, "green")],
     "mult": 0.8, "w": 1, "atype": "stab"},
]

_DK_KINGS = {
    "dagannoth rex": (
        {"abonus": 45, "atktype": ["stab"], "att": 180, "cb": 303,
         "dstab": 220, "dslash": 220, "dcrush": 220, "dmagic": 0,
         "drange": 220, "def": 90, "hp": 255, "maxhit": 26, "str": 180,
         "weak": "magic"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("berserker ring", 1, 1, 0.05), ("warrior ring", 1, 1, 0.05),
         ("dragon axe", 1, 1, 0.03), ("grimy ranarr", 1, 3, 0.25)],
        REX_ATTACKS),
    "dagannoth prime": (
        {"abonus": 45, "atktype": ["magic"], "att": 180, "cb": 303,
         "dstab": 220, "dslash": 220, "dcrush": 220, "dmagic": 220,
         "drange": 0, "def": 90, "hp": 255, "maxhit": 25, "str": 180,
         "weak": "ranged"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("seers ring", 1, 1, 0.05), ("dragon axe", 1, 1, 0.03),
         ("blood rune", 5, 20, 0.5), ("nature rune", 10, 40, 0.4)],
        PRIME_ATTACKS),
    "dagannoth supreme": (
        {"abonus": 45, "atktype": ["ranged"], "att": 180, "cb": 303,
         "dstab": 10, "dslash": 10, "dcrush": 10, "dmagic": 220,
         "drange": 220, "def": 90, "hp": 255, "maxhit": 24, "str": 180,
         "weak": "slash"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("archers ring", 1, 1, 0.05), ("dragon axe", 1, 1, 0.03),
         ("raw swordfish", 2, 5, 0.5)],
        SUPREME_ATTACKS),
}
for _k, (_st, _drops, _atk) in _DK_KINGS.items():
    _add_mob(_k, _st, _drops, members=True)
    MONSTERS[_k]["boss"] = True
    MONSTERS[_k]["rank"] = "boss"
    _BOSSES.add(_k)
    BOSS_TURN[_k] = (lambda atk: (lambda p, m: _dk_take_turn(p, m, atk)))(_atk)
    BOSS_INTRO[_k] = _dk_intro
    BOSS_DEATH[_k] = _dk_death
    MONSTER_ART[_k] = DK_ART

# --- the province --------------------------------------------------------------
ROOMS.update({
    "rellekka": dict(name="Rellekka",
        desc="A palisaded seafarers' town of longhalls, woodsmoke and "
             "gull-cry. Brundt the Chieftain holds court, Olaf the Bard "
             "hums over his strings, and longships rock at the dock "
             "('sail'). Rock crabs bask along the coast ('coast'), and the "
             "Jarl's isle of Neitiznot lies over the water ('isles').",
        exits={"south": "seers_village", "coast": "rock_crab_coast",
               "sail": "waterbirth_island", "isles": "neitiznot"},
        bank=True, npc=["fremennik_trials", "olaf"], members=True),
    "rock_crab_coast": dict(name="Rock Crab Coast",
        desc="A cold grey shore where boulders sprout legs if you step too "
             "close. Warriors come from across Gielinor to batter the "
             "crabs' shells — they hit like pebbles and last like rocks.",
        exits={"west": "rellekka"},
        monsters=["rock crab"], fish_tools=["cage", "harpoon"],
        members=True),
    "neitiznot": dict(name="Neitiznot",
        desc="A tidy isle of yak-paddocks and fresh-cut timber. The Jarl's "
             "armoury sells his famous helm — to those the Fremennik call "
             "kin.",
        exits={"sail": "rellekka"},
        monsters=["yak"], shop="neitiznot", members=True),
    "waterbirth_island": dict(name="Waterbirth Island",
        desc="A storm-lashed rock where dagannoths boil out of blowholes. "
             "A sea-cave mouth yawns at the waterline ('cave').",
        exits={"sail": "rellekka", "cave": "waterbirth_dungeon"},
        monsters=["dagannoth", "rock crab"], hostile=True, members=True,
        qlock=("fremennik_trials", ("complete",),
               "Jarvald bars the gangplank: 'Waterbirth is FREMENNIK "
               "water, outerlander.' (Quest: The Fremennik Trials — speak "
               "to Brundt in Rellekka)")),
    "waterbirth_dungeon": dict(name="Waterbirth Dungeon",
        desc="Sea-cut tunnels booming with surf. Dagannoths swarm the "
             "dark, and the deepest shaft breathes like something asleep "
             "('deep').",
        exits={"up": "waterbirth_island", "deep": "dks_lair"},
        monsters=["dagannoth"], hostile=True, members=True),
    "dks_lair": dict(name="The Kings' Lair",
        desc="A drowned cathedral of rock. THREE KINGS circle in the black "
             "water: REX the crusher, PRIME the storm-caller, SUPREME the "
             "spike-thrower. Fight one and the others circle...",
        exits={"up": "waterbirth_dungeon"},
        monsters=["dagannoth rex", "dagannoth prime", "dagannoth supreme"],
        members=True),
})
ROOMS["seers_village"]["exits"]["north"] = "rellekka"
ROOMS["seers_village"]["desc"] += (" North, the road runs cold toward "
                                   "Rellekka and the Fremennik Province.")
for _rm in ("rellekka", "rock_crab_coast", "neitiznot", "waterbirth_island",
            "waterbirth_dungeon", "dks_lair"):
    REGIONS[_rm] = "Fremennik"
TRAVEL_HUBS["rellekka"] = "rellekka"
TRAVEL_NAMES.append("Rellekka")
REGION_AMBIENT["Fremennik"] = [
    "Gulls scream over the grey water.",
    "Somewhere in the longhall, a saga finds its chorus.",
    "The surf drags cold fingers up the shingle.",
    "A war-horn sounds far out across the sound, and falls silent.",
]

# --- The Fremennik Trials (3 QP) ---------------------------------------------
ALL_QUESTS["fremennik_trials"] = "The Fremennik Trials"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["fremennik_trials"] = 3
NPC_NAMES["fremennik_trials"] = "Brundt the Chieftain"
NPC_NAMES["olaf"] = "Olaf the Bard"
QUEST_STARTS["fremennik_trials"] = "Brundt the Chieftain, Rellekka"
QUEST_HINTS["fremennik_trials"] = {
    "hunt": "slay the Draugen haunting the rock crab coast east of Rellekka",
    "hunted": "report your kill to Brundt the Chieftain",
    "lyre": "bring Olaf the Bard maple logs and 2 balls of wool",
    "song": "perform in the longhall — talk to Brundt, lyre in hand",
    "feast": "bring Brundt 3 swordfish (cooked) for the longhall table",
}

_FREM_NAMES = ["Skulgrimen", "Thorvald", "Sigli", "Manni", "Swensen",
               "Peer", "Thora", "Asleif", "Borrokar", "Freygerd"]


def _frem_name(p):
    return _FREM_NAMES[sum(ord(c) for c in p.name) % len(_FREM_NAMES)]


def talk_brundt(p):
    stage = _q(p, "fremennik_trials")
    if stage == "not_started":
        banner("Quest Start: The Fremennik Trials", color="purple",
               line_color="bmagenta")
        say("Brundt the Chieftain: \"An outerlander wants to sail OUR "
            "waters? Then become one of us. Three trials: the HUNT, the "
            "SONG, and the FEAST. First — a DRAUGEN, a drowned man's "
            "spite, haunts the crab coast. Slay it.\"")
        p.quests["fremennik_trials"] = "hunt"
    elif stage == "hunt":
        say("Brundt: \"The Draugen still walks the coast east of here. "
            "'fight the draugen'!\"")
    elif stage == "hunted":
        say("Brundt: \"The Draugen unmade! You hunt like one of us. Now "
            "the SONG — Olaf the Bard will build you a lyre, if you bring "
            "him maple logs and two balls of wool.\"", "byellow")
        p.quests["fremennik_trials"] = "lyre"
    elif stage == "lyre":
        say("Brundt: \"Speak to Olaf — maple logs and two balls of wool "
            "for your lyre.\"")
    elif stage == "song":
        if not p.has("lyre"):
            say("Brundt: \"You'd perform empty-handed? Where is your "
                "lyre?\"")
            return
        say("You strike the strings. The longhall falls quiet... then "
            "stamps and roars along until the rafters shake!", "bcyan",
            "bold")
        say("Brundt: \"HA! The song is yours. Last comes the FEAST — "
            "bring three swordfish, cooked and steaming, for the long "
            "table.\"", "byellow")
        p.quests["fremennik_trials"] = "feast"
    elif stage == "feast":
        if p.count("swordfish") < 3:
            say("Brundt: \"Three cooked swordfish for the table! Catherby "
                "and Musa Point run thick with them — bring a harpoon.\"")
            return
        p.take("swordfish", 3)
        _complete_banner("The Fremennik Trials")
        name = _frem_name(p)
        say(f"The feast is laid and the horns are drained. The longhall "
            f"rises as one and roars your Fremennik name: {name.upper()}! "
            "2,812 xp awarded across six skills — and the sail to "
            "WATERBIRTH ISLAND is yours.", "gold", "bold")
        for _s in ("attack", "strength", "defence", "hitpoints",
                   "fishing", "woodcutting"):
            p.gain_xp(_s, 2812)
        p.quests["fremennik_trials"] = "complete"
    elif stage == "complete":
        say(f"Brundt: \"{_frem_name(p)}! The Kings still circle beneath "
            "Waterbirth, if your arm itches for glory.\"")


def talk_olaf(p):
    stage = _q(p, "fremennik_trials")
    if stage == "lyre":
        if p.has("maple logs") and p.count("ball of wool") >= 2:
            p.take("maple logs", 1)
            p.take("ball of wool", 2)
            p.add("lyre")
            p.quests["fremennik_trials"] = "song"
            say("Olaf carves the maple, twists the wool to strings, and "
                "hands you a LYRE. \"Now play it for the chieftain — and "
                "don't you dare go flat.\"", "bgreen")
        else:
            say("Olaf: \"Maple logs and two balls of wool. Seers' maples "
                "stand south of here, and their spinning wheel isn't "
                "far.\"")
    elif stage == "song":
        say("Olaf: \"You have the lyre — go play the longhall, "
            "outerlander!\"")
    else:
        say("Olaf hums a saga of three Kings beneath Waterbirth: the "
            "crusher, the storm-caller, the spike-thrower — and the rings "
            "they hoard.")


QUEST_TALK["fremennik_trials"] = talk_brundt
QUEST_TALK["olaf"] = talk_olaf


# ===========================================================================
#  TROLL COUNTRY  (Burthorpe, the Warriors' Guild, and the Troll Stronghold)
# ===========================================================================
# Burthorpe sits north of Taverley. The Warriors' Guild weighs your arm at
# the door (attack + strength 130) and its cyclopes yield DEFENDERS tier by
# tier; Death Plateau climbs to the Troll Stronghold and the peak of
# Trollheim — where a crack in the mountain drops into the God Wars.

# --- defenders: off-hand weapons, earned in order ---------------------------
_DEFENDER_TIERS = [("bronze", 3, 1, 300), ("iron", 5, 2, 700),
                   ("steel", 8, 3, 1500), ("black", 11, 4, 3000),
                   ("mithril", 14, 5, 6000), ("adamant", 17, 5, 12000),
                   ("rune", 20, 6, 35000)]
DEFENDER_ORDER = [f"{n} defender" for n, _a, _s, _v in _DEFENDER_TIERS]
for _dn, _da, _ds, _dv in _DEFENDER_TIERS:
    add_item(f"{_dn} defender", _dv, members=True,
             equip={"slot": "shield", "astab": _da, "aslash": _da,
                    "acrush": _da, "dstab": _da, "dslash": _da,
                    "dcrush": _da, "str": _ds})
EFFECT_NOTES["rune defender"] = ("an off-hand blade — attack bonuses in the "
                                 "shield slot; guild cyclopes award each "
                                 "tier in order")


def _best_defender(p):
    """Index of the best defender the player owns anywhere, or -1."""
    best = -1
    for i, d in enumerate(DEFENDER_ORDER):
        if p.has(d) or d in p.equipment.values() \
                or d in getattr(p, "bank", {}):
            best = i
    return best


# --- creatures ---------------------------------------------------------------
_add_mob("cyclops",
    {"abonus": 15, "atktype": ["crush"], "att": 50, "cb": 56, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 10, "drange": 25, "def": 45,
     "hp": 60, "maxhit": 7, "str": 50, "weak": "stab"},
    [("big bones", 1, 1, 1.0), ("coins", 20, 120, 0.7)],
    members=True, rank="hard")
_add_mob("mountain troll",
    {"abonus": 20, "atktype": ["crush"], "att": 60, "cb": 69, "dstab": 40,
     "dslash": 40, "dcrush": 30, "dmagic": 20, "drange": 40, "def": 55,
     "hp": 60, "maxhit": 8, "str": 65, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 20, 150, 0.7),
     ("earth rune", 5, 20, 0.3), ("grimy ranarr", 1, 1, 0.04)],
    members=True, rank="hard")
_add_mob("thrower troll",
    {"abonus": 25, "atktype": ["ranged"], "att": 65, "cb": 76, "dstab": 40,
     "dslash": 40, "dcrush": 35, "dmagic": 25, "drange": 45, "def": 60,
     "hp": 64, "maxhit": 9, "str": 70, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 30, 180, 0.7),
     ("law rune", 1, 4, 0.15)],
    members=True, rank="hard")
_add_mob("troll general",
    {"abonus": 30, "atktype": ["crush"], "att": 90, "cb": 91, "dstab": 55,
     "dslash": 55, "dcrush": 45, "dmagic": 30, "drange": 55, "def": 75,
     "hp": 90, "maxhit": 11, "str": 90, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 100, 500, 0.9),
     ("nature rune", 5, 15, 0.3), ("grimy ranarr", 1, 2, 0.08)],
    members=True, rank="elite")

# --- DAD, the gatekeeper ------------------------------------------------------
DAD_ART = r"""
        ______
     .-'      '-.
    /  O      O  \
   |      __      |
   |  \________/  |
    \   ______   /
   .-'-.|      |.-'-.
  /     '------'     \
"""


def _dad_intro(name):
    return [_tint(DAD_ART, "grey"), _tint(DAD_ART, "byellow", "bold")]


def _dad_death(name):
    return [_tint(DAD_ART, "byellow"), _tint(DAD_ART, "grey", "dim")]


def _dad_stagger(p, m, dmg):
    p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
    print("  " + paint("The slam rattles your bones! (-2 defence)", "bblue"))


DAD_ATTACKS = [
    {"label": "a haymaker like a falling pine", "verb": "swings",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(DAD_ART, "byellow", "bold")],
     "mult": 1.3, "w": 3, "atype": "crush"},
    {"label": "a boulder the size of a cartwheel", "verb": "hurls",
     "color": ("grey", "bold"),
     "builder": lambda: [_tint(DAD_ART, "grey", "bold")],
     "mult": 1.0, "w": 2, "atype": "ranged"},
    {"label": "a ground-slam", "verb": "drops into",
     "color": ("brown",),
     "builder": lambda: [_tint(DAD_ART, "brown")],
     "mult": 0.8, "w": 2, "atype": "crush", "effect": _dad_stagger},
]

_add_mob("dad",
    {"abonus": 35, "atktype": ["crush", "ranged"], "att": 100, "cb": 101,
     "dstab": 60, "dslash": 60, "dcrush": 50, "dmagic": 35, "drange": 60,
     "def": 80, "hp": 120, "maxhit": 13, "str": 100, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 300, 1200, 1.0),
     ("law rune", 2, 8, 0.4)], members=True)
MONSTERS["dad"]["boss"] = True
MONSTERS["dad"]["rank"] = "boss"
_BOSSES.add("dad")
BOSS_TURN["dad"] = lambda p, m: _boss_take_turn(p, m, DAD_ATTACKS)
BOSS_INTRO["dad"] = _dad_intro
BOSS_DEATH["dad"] = _dad_death
MONSTER_ART["dad"] = DAD_ART

# --- the region ----------------------------------------------------------------
ROOMS.update({
    "burthorpe": dict(name="Burthorpe",
        desc="A garrison town under the mountains, all drill-yards and "
             "watchfires. Denulth of the Imperial Guard frets over his "
             "maps, the Warriors' Guild stands open to proven arms "
             "('guild'), and Death Plateau looms above ('plateau').",
        exits={"south": "taverley", "guild": "warriors_guild",
               "plateau": "death_plateau"},
        bank=True, npc="troll_stronghold", members=True),
    "warriors_guild": dict(name="Warriors' Guild",
        desc="Ghommal's hall of clashing steel. In the cyclops pen, "
             "one-eyed giants guard the armoury's DEFENDERS — hold your "
             "best and slay for the next tier.",
        exits={"out": "burthorpe"},
        monsters=["cyclops"], members=True,
        stat_lock=(["attack", "strength"], 130,
                   "Ghommal bars the door: 'Da Warriors' Guild is for "
                   "WARRIORS. Come back wiv attack an' strength what add "
                   "to 130.'")),
    "death_plateau": dict(name="Death Plateau",
        desc="A wind-scoured shelf of scree where trolls squat among the "
             "boulders — some of the boulders squat back. The stronghold "
             "gate is carved into the cliff above ('up').",
        exits={"down": "burthorpe", "up": "troll_stronghold"},
        monsters=["mountain troll", "thrower troll"], hostile=True,
        members=True),
    "troll_stronghold": dict(name="Troll Stronghold",
        desc="A reeking warren of tunnels behind a gate of lashed pines. "
             "DAD fills the gate-hall, and somewhere deeper a prisoner "
             "rattles his chains.",
        exits={"out": "death_plateau", "peak": "trollheim"},
        monsters=["dad", "troll general"], hostile=True, members=True,
        npc="godric",
        qlock=("troll_stronghold",
               ("started", "dad", "freed", "complete"),
               "The stronghold gate is barred from within. (Quest: Troll "
               "Stronghold — speak to Denulth in Burthorpe)")),
    "trollheim": dict(name="Trollheim",
        desc="The roof of Troll Country. From the summit you can see half "
             "of Gielinor — and a crack in the mountainside that breathes "
             "frost, descending into the God Wars ('chasm').",
        exits={"down": "troll_stronghold", "chasm": "gwd_entrance"},
        members=True),
})
ROOMS["taverley"]["exits"]["north"] = "burthorpe"
ROOMS["taverley"]["desc"] += " Burthorpe's watchfires glow to the north."
ROOMS["gwd_entrance"]["exits"]["climb"] = "trollheim"
REGIONS.update({"burthorpe": "Asgarnia", "warriors_guild": "Asgarnia",
                "death_plateau": "Trollheim", "troll_stronghold": "Trollheim",
                "trollheim": "Trollheim"})
TRAVEL_HUBS["burthorpe"] = "burthorpe"
TRAVEL_NAMES.append("Burthorpe")
REGION_AMBIENT["Trollheim"] = [
    "Wind screams over the scree.",
    "Somewhere above, rock grinds on rock — or a troll laughs.",
    "Loose stones clatter away down the mountainside.",
]

# --- Troll Stronghold (1 QP) ---------------------------------------------------
ALL_QUESTS["troll_stronghold"] = "Troll Stronghold"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["troll_stronghold"] = 1
NPC_NAMES["troll_stronghold"] = "Denulth"
NPC_NAMES["godric"] = "Godric"
QUEST_STARTS["troll_stronghold"] = "Denulth, Burthorpe"
QUEST_HINTS["troll_stronghold"] = {
    "started": "climb Death Plateau and breach the Troll Stronghold ('up')",
    "dad": "DAD is beaten — find Godric in the stronghold and set him free",
    "freed": "return to Denulth in Burthorpe",
}


def talk_denulth(p):
    stage = _q(p, "troll_stronghold")
    if stage == "not_started":
        banner("Quest Start: Troll Stronghold", color="purple",
               line_color="bmagenta")
        say("Denulth: \"The trolls have taken GODRIC of the Imperial Guard "
            "and dragged him to their stronghold above Death Plateau. "
            "Their gatekeeper is a brute they call DAD. Beat the troll, "
            "breach the gate, bring our man home.\"")
        p.quests["troll_stronghold"] = "started"
    elif stage in ("started", "dad"):
        say("Denulth: \"The stronghold is up the plateau — beat DAD at the "
            "gate and find Godric!\"")
    elif stage == "freed":
        _complete_banner("Troll Stronghold")
        say("Godric limps into the drill-yard behind you and the garrison "
            "erupts. Denulth: \"The Guard owes you a debt.\" 8,000 "
            "agility and strength xp awarded!", "gold", "bold")
        p.gain_xp("agility", 8000)
        p.gain_xp("strength", 8000)
        p.quests["troll_stronghold"] = "complete"
    elif stage == "complete":
        say("Denulth: \"Burthorpe sleeps easier with you on the wall, "
            "friend.\"")


def talk_godric(p):
    stage = _q(p, "troll_stronghold")
    if stage == "dad":
        say("You snap the crude troll chains. Godric: \"Thought I was "
            "stew, friend. Let's get off this mountain — Denulth will "
            "want to see us both.\"", "bgreen")
        p.quests["troll_stronghold"] = "freed"
    elif stage == "started":
        say("Godric (from the shadows): \"The gatekeeper! Deal with DAD "
            "first or we'll never walk out — 'fight dad'!\"")
    elif stage in ("freed", "complete"):
        say("The empty chains rattle in the draught.")
    else:
        say("A prisoner's voice echoes somewhere deeper in the warren.")


QUEST_TALK["troll_stronghold"] = talk_denulth
QUEST_TALK["godric"] = talk_godric


