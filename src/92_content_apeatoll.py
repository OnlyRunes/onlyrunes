

# ===========================================================================
#  APE ATOLL  (Monkey Madness: the 10th squad, the greegree, and the
#              Jungle Demon)
# ===========================================================================
# King Narnode's 10th gnome squad vanished over the sea. The trail ends on
# Ape Atoll — an island of armed monkeys where humans are shot on sight.
# Garkor of the 10th squad can carve you a MONKEY GREEGREE (wear it and the
# guards see just another monkey), opening Marim and its rooftop agility
# course — and beneath the temple, the JUNGLE DEMON the squad came to stop.

# --- items ---------------------------------------------------------------------
add_item("monkey bones", 40, members=True, bury=("prayer", 18))
add_item("monkey greegree", 30000, members=True,
         equip={"slot": "amulet"})
EFFECT_NOTES["monkey greegree"] = ("carved monkey bone and old magic — "
                                   "wear it and monkeys see a monkey")
if "banana" not in ITEMS:
    add_item("banana", 8, heal=2)

# --- the monkeys ------------------------------------------------------------------
_add_mob("monkey",
    {"abonus": 5, "atktype": ["crush"], "att": 30, "cb": 32,
     "dstab": 10, "dslash": 12, "dcrush": 10, "dmagic": 15, "drange": 14,
     "def": 30, "hp": 40, "maxhit": 4, "str": 30, "weak": "slash"},
    [("monkey bones", 1, 1, 1.0), ("banana", 1, 3, 0.7),
     ("coins", 20, 120, 0.8)], members=True, rank="easy")
_add_mob("monkey archer",
    {"abonus": 25, "atktype": ["ranged"], "att": 110, "cb": 86,
     "dstab": 40, "dslash": 45, "dcrush": 40, "dmagic": 40, "drange": 50,
     "def": 70, "hp": 90, "maxhit": 10, "str": 95, "weak": "crush"},
    [("monkey bones", 1, 1, 1.0), ("iron arrow", 4, 12, 0.6),
     ("coins", 150, 700, 1.0)], members=True, rank="hard")

# --- the Jungle Demon ---------------------------------------------------------------
JUNGLE_DEMON_ART = r"""
         \  \      /  /
         (\_\O----O/_/)
          \ ( o  o ) /        the JUNGLE DEMON
           \| \^^/ |/          tears free of its circle!
         ___|______|___
        /   |  ||  |   \
       ~~   ^^    ^^   ~~
"""


def _jdemon_quake(p, m, dmg):
    if dmg > 0 and random.random() < 0.3:
        p.run_energy = max(0, getattr(p, "run_energy", 100) - 15)
        print("  " + paint("The island itself bucks underfoot. (-15 run "
                           "energy)", "brown"))


JUNGLE_DEMON_ATTACKS = [
    {"label": "a fistful of jungle-fire", "verb": "hurls",
     "color": ("orange", "bold"), "builder": _fx_hellfire,
     "mult": 1.1, "w": 3, "atype": "magic"},
    {"label": "a temple-cracking slam", "verb": "brings down",
     "color": ("brown", "bold"), "builder": _fx_smash,
     "mult": 1.0, "w": 2, "atype": "crush", "effect": _jdemon_quake},
]


def _jdemon_intro(name):
    return _fx((JUNGLE_DEMON_ART, "grey", "dim"),
               (JUNGLE_DEMON_ART, "green"),
               (JUNGLE_DEMON_ART, "bred", "bold"))


def _jdemon_death(name):
    return _fx((JUNGLE_DEMON_ART, "bred"),
               (JUNGLE_DEMON_ART, "grey", "dim"))


_add_mob("jungle demon",
    {"abonus": 35, "atktype": ["magic", "crush"], "att": 170, "cb": 412,
     "dstab": 75, "dslash": 75, "dcrush": 55, "dmagic": 80, "drange": 75,
     "def": 110, "hp": 260, "maxhit": 20, "str": 160, "weak": "crush"},
    [("coins", 5000, 15000, 1.0), ("monkey bones", 2, 4, 1.0),
     ("uncut ruby", 1, 2, 0.4)], members=True)
MONSTERS["jungle demon"]["boss"] = True
MONSTERS["jungle demon"]["rank"] = "boss"
_BOSSES.add("jungle demon")
BOSS_TURN["jungle demon"] = \
    lambda p, m: _boss_take_turn(p, m, JUNGLE_DEMON_ATTACKS)
BOSS_INTRO["jungle demon"] = _jdemon_intro
BOSS_DEATH["jungle demon"] = _jdemon_death
MONSTER_ART["jungle demon"] = JUNGLE_DEMON_ART

# --- the island -----------------------------------------------------------------------
ROOMS.update({
    "ape_atoll_beach": dict(name="Ape Atoll Beach",
        desc="A white-sand shore under screaming jungle. Monkeys pelt "
             "intruders from the treeline, and a ragged gnome — GARKOR of "
             "the 10th squad — waves you into cover ('talk'). The walled "
             "monkey city of Marim drums to the north ('marim').",
        exits={"sail": "tree_gnome_stronghold", "marim": "marim"},
        monsters=["monkey"], npc="mm_garkor", hostile=True, members=True),
    "marim": dict(name="Marim",
        desc="The monkey capital — thatched roofs, banana stores, and "
             "archers on every wall who see everything. A rooftop course "
             "circles the city ('agility'), and stairs descend beneath "
             "the temple ('temple').",
        exits={"beach": "ape_atoll_beach", "temple": "jungle_demon_lair"},
        monsters=["monkey archer"], agility_course=(48, 380, 8),
        members=True,
        gear_lock=(["monkey greegree"],
                   "The wall-archers screech and draw — no HUMAN sets foot "
                   "in Marim alive.")),
    "jungle_demon_lair": dict(name="Beneath the Temple",
        desc="A ritual cavern scarred by claws, the summoning circle at "
             "its heart burnt black. This is what the 10th squad came to "
             "stop.",
        exits={"up": "marim"},
        members=True,
        qlock=("monkey_madness", ["demon", "complete"],
               "The temple stairs are sealed with gnome-wards — Garkor on "
               "the beach knows the way in. (Quest: Monkey Madness)")),
})
ROOMS["tree_gnome_stronghold"]["exits"]["sail"] = "ape_atoll_beach"
ROOMS["tree_gnome_stronghold"]["npc"] = "monkey_madness"
ROOMS["tree_gnome_stronghold"]["desc"] = (
    ROOMS["tree_gnome_stronghold"].get("desc", "") +
    " KING NARNODE paces the grand tree's roots, sick with worry "
    "('talk'), and a gnome ship rides at anchor ('sail').")
REGIONS.update({"ape_atoll_beach": "ApeAtoll", "marim": "ApeAtoll",
                "jungle_demon_lair": "ApeAtoll"})

# --- Monkey Madness (3 QP) -----------------------------------------------------------
ALL_QUESTS["monkey_madness"] = "Monkey Madness"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["monkey_madness"] = 3
NPC_NAMES["monkey_madness"] = "King Narnode"
NPC_NAMES["mm_garkor"] = "Garkor"
QUEST_STARTS["monkey_madness"] = "King Narnode, Tree Gnome Stronghold " \
                                 "(west of Ardougne, 'gnome')"
QUEST_HINTS["monkey_madness"] = {
    "squad": "sail from the Stronghold to Ape Atoll and find Garkor "
             "('talk' on the beach)",
    "bones": "bring Garkor MONKEY BONES (the beach monkeys drop them)",
    "demon": "wear the greegree, enter Marim, and slay the JUNGLE DEMON "
             "beneath the temple",
}


def talk_narnode(p):
    stage = _q(p, "monkey_madness")
    if stage == "not_started":
        banner("Quest Start: Monkey Madness", color="purple",
               line_color="bmagenta")
        say("King Narnode: \"My 10th squad flew east and never returned. "
            "The wreckage points to APE ATOLL — an island that kills "
            "humans on principle. Take my ship ('sail'). Find my "
            "gnomes.\"")
        p.quests["monkey_madness"] = "squad"
    elif stage in ("squad", "bones"):
        say("King Narnode: \"The ship waits ('sail'). Find the 10th "
            "squad!\"")
    elif stage == "demon":
        say("King Narnode: \"Garkor lives? Then finish what they "
            "started — the demon beneath the temple!\"")
    elif stage == "complete":
        say("King Narnode: \"The Stronghold owes you everything. Wear "
            "that greegree with pride, friend of gnomes.\"")


def talk_garkor(p):
    stage = _q(p, "monkey_madness")
    if stage == "not_started":
        say("The ragged gnome waves you off: \"Get down! If you want to "
            "help, King Narnode sent you — didn't he? Talk to him "
            "first.\"")
        return
    if stage == "squad":
        p.quests["monkey_madness"] = "bones"
        say("Garkor: \"You made it! Listen — the monkeys summoned "
            "something under their temple, and my squad is scattered or "
            "worse. I can carve you a GREEGREE to walk among them, but I "
            "need MONKEY BONES. The beach monkeys have plenty. Grim "
            "work. Do it anyway.\"", "byellow")
        return
    if stage == "bones":
        if p.has("monkey bones"):
            p.take("monkey bones")
            p.add("monkey greegree")
            p.quests["monkey_madness"] = "demon"
            say("Garkor whittles fast, whispering gnome-words over the "
                "bone. \"Done — the MONKEY GREEGREE. Wear it and Marim "
                "will see a monkey. The temple stairs lead down to the "
                "thing they summoned. End it.\"", "bgreen")
        else:
            say("Garkor: \"Monkey bones, friend — the beach monkeys "
                "drop them. I'll do the carving.\"")
        return
    if stage == "demon":
        say("Garkor: \"Wear the greegree, walk into Marim ('marim'), "
            "and take the temple stairs. The JUNGLE DEMON dies today.\"")
        return
    say("Garkor salutes, gnome-style: \"The 10th squad won't forget "
        "you.\"")


QUEST_TALK["monkey_madness"] = talk_narnode
QUEST_TALK["mm_garkor"] = talk_garkor

# the demon is bound beneath the temple only while the quest rages
QUEST_SPAWNS.append(("jungle_demon_lair", "jungle demon",
                     lambda pl: _q(pl, "monkey_madness") == "demon"))


# --- kill hook: the demon falls, the squad is avenged --------------------------------
_prev_quest_on_kill_mm = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811  (wraps prior)
    _prev_quest_on_kill_mm(p, target)
    if target == "jungle demon" and _q(p, "monkey_madness") == "demon":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Monkey Madness", color="byellow",
               line_color="gold")
        say("The Jungle Demon collapses into the circle that birthed it, "
            "and somewhere above, monkey drums fall silent. 20,000 attack "
            "and 20,000 strength xp awarded — and Garkor presses a DRAGON "
            "SCIMITAR into your hands: \"Gnome-forged. Squad's thanks.\"",
            "bgreen")
        p.gain_xp("attack", 20000)
        p.gain_xp("strength", 20000)
        p.add("dragon scimitar")
        p.quests["monkey_madness"] = "complete"
