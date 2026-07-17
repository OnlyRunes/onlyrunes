

# ===========================================================================
#  RECIPE FOR DISASTER  (the Culinaromancer, the frozen banquet, and the
#                        BARROWS GLOVES)
# ===========================================================================
# The Duke's centenary banquet goes horribly wrong: the CULINAROMANCER, a
# chef-mage older than kingdoms, crashes the feast. Gypsy Aris freezes the
# hall in a bubble of stopped time — and only a hero seasoned by many
# quests (40 QP) can step inside and fight the courses he sends, one dish
# at a time, before facing the chef himself. His larder chest holds the
# finest gloves ever stitched.

# --- items ---------------------------------------------------------------------
add_item("bucket of water", 8)
SHOPS["general"]["bucket of water"] = 8
add_item("cooking gauntlets", 30000, members=True,
         equip={"slot": "gloves", "dstab": 2, "dslash": 2, "dcrush": 2})
EFFECT_NOTES["cooking gauntlets"] = ("heatproof chef's gauntlets — food "
                                     "burns far less often on your watch")
add_item("barrows gloves", 1500000, members=True, equip={
    "slot": "gloves", "astab": 12, "aslash": 12, "acrush": 12,
    "arange": 12, "amagic": 6, "str": 12, "dstab": 12, "dslash": 12,
    "dcrush": 12, "dmagic": 12, "drange": 12,
    "req": {"defence": 40}})
EFFECT_NOTES["barrows gloves"] = ("the Culinaromancer's masterwork — the "
                                  "finest gloves ever stitched, for any "
                                  "style of fight")

# --- the courses ------------------------------------------------------------------
AGRITH_ART = r"""
        \    _____    /
        (\ /     \ /)
         ( o     o )        AGRITH-NA-NA —
         /|  ___  |\         a demon of boiling banana!
        ( | (___) | )
         \|_______|/
          )/     \(
"""
FLAMBEED_ART = r"""
        (  )  (   )  (
       ) ____________ (
      ( /  (o)  (o)  \ )      FLAMBEED — a giant
       |     ____     |        served flambé!
      /|    (____)    |\
     ( |______________| )
        //    ||    \\
"""
KARAMEL_ART = r"""
         *   /\   *
          __/  \__
         | (o  o) |   *       KARAMEL — the ice
       * |   ..   |            queen of dessert!
         |  '--'  |  *
        /|________|\
       * _|_    _|_  *
"""
CULINAROMANCER_ART = r"""
           _______
          (  ___  )
          | (o o) |          the CULINAROMANCER —
         /|  \_/  |\          chef of the last supper!
        / |_______| \
       (__|  ) (  |__)
          |__| |__|
"""


def _karamel_freeze(p, m, dmg):
    if dmg > 0 and not getattr(p, "frozen", False) and random.random() < 0.4:
        p.frozen = True
        print("  " + paint("Caramel hardens around your legs — FROZEN "
                           "solid!", "bcyan"))


AGRITH_ATTACKS = [
    {"label": "a jet of boiling banana", "verb": "spews",
     "color": ("byellow", "bold"), "builder": _fx_miasma,
     "mult": 1.05, "w": 3, "atype": "magic"},
    {"label": "a peel-slick haymaker", "verb": "swings",
     "color": ("bred", "bold"), "builder": _fx_smash,
     "mult": 1.0, "w": 2, "atype": "crush"},
]
FLAMBEED_ATTACKS = [
    {"label": "a wave of kitchen-fire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _fx_hellfire,
     "mult": 1.1, "w": 3, "atype": "magic"},
    {"label": "a white-hot fist", "verb": "brings down",
     "color": ("bred", "bold"), "builder": _fx_smash,
     "mult": 1.0, "w": 2, "atype": "crush"},
]
KARAMEL_ATTACKS = [
    {"label": "a lance of frozen sugar", "verb": "hurls",
     "color": ("bcyan", "bold"), "builder": _fx_bolt_blue,
     "mult": 1.05, "w": 3, "atype": "magic", "effect": _karamel_freeze},
    {"label": "a brittle shriek", "verb": "lets out",
     "color": ("bwhite",), "builder": _fx_roar,
     "mult": 0.85, "w": 2, "atype": "ranged"},
]
CULINAROMANCER_ATTACKS = [
    {"label": "a volley of enchanted cutlery", "verb": "conjures",
     "color": ("bwhite", "bold"), "builder": _fx_bolt,
     "mult": 1.1, "w": 3, "atype": "ranged"},
    {"label": "a pot of scalding stew", "verb": "upends",
     "color": ("orange", "bold"), "builder": _fx_slag,
     "mult": 1.0, "w": 2, "atype": "magic"},
    {"label": "time itself, briefly", "verb": "pinches",
     "color": ("bmagenta", "bold"), "builder": _fx_bolt_blue,
     "mult": 0.9, "w": 1, "atype": "magic", "effect": _karamel_freeze},
]

_RFD_BOSSES = {
    "agrith-na-na": (AGRITH_ART, AGRITH_ATTACKS,
        {"abonus": 30, "atktype": ["magic", "crush"], "att": 150,
         "cb": 146, "dstab": 60, "dslash": 60, "dcrush": 45, "dmagic": 65,
         "drange": 60, "def": 90, "hp": 180, "maxhit": 15, "str": 130,
         "weak": "crush"},
        [("banana", 3, 8, 1.0), ("coins", 2000, 6000, 1.0)]),
    "flambeed": (FLAMBEED_ART, FLAMBEED_ATTACKS,
        {"abonus": 34, "atktype": ["magic", "crush"], "att": 160,
         "cb": 149, "dstab": 70, "dslash": 70, "dcrush": 50, "dmagic": 70,
         "drange": 70, "def": 100, "hp": 200, "maxhit": 17, "str": 150,
         "weak": "crush"},
        [("coins", 2500, 8000, 1.0), ("uncut ruby", 1, 2, 0.4)]),
    "karamel": (KARAMEL_ART, KARAMEL_ATTACKS,
        {"abonus": 36, "atktype": ["magic", "ranged"], "att": 170,
         "cb": 170, "dstab": 75, "dslash": 75, "dcrush": 55, "dmagic": 80,
         "drange": 75, "def": 105, "hp": 210, "maxhit": 18, "str": 150,
         "weak": "crush"},
        [("coins", 3000, 9000, 1.0), ("uncut diamond", 1, 1, 0.3)]),
    "culinaromancer": (CULINAROMANCER_ART, CULINAROMANCER_ATTACKS,
        {"abonus": 42, "atktype": ["ranged", "magic"], "att": 210,
         "cb": 510, "dstab": 90, "dslash": 90, "dcrush": 70, "dmagic": 95,
         "drange": 90, "def": 130, "hp": 280, "maxhit": 22, "str": 180,
         "weak": "crush"},
        [("coins", 10000, 30000, 1.0), ("uncut diamond", 1, 2, 0.5)]),
}
for _b, (_art, _atk, _st, _drops) in _RFD_BOSSES.items():
    _add_mob(_b, _st, _drops, members=True)
    MONSTERS[_b]["boss"] = True
    MONSTERS[_b]["rank"] = "boss"
    _BOSSES.add(_b)
    BOSS_TURN[_b] = (lambda atk: (lambda p, m:
                                  _boss_take_turn(p, m, atk)))(_atk)
    MONSTER_ART[_b] = _art
MONSTERS["flambeed"]["needs_water"] = True

# --- the frozen banquet --------------------------------------------------------------
ROOMS.update({
    "banquet_hall": dict(name="The Frozen Banquet",
        desc="The Duke's great hall, stopped mid-toast: goblets hang in "
             "the air, laughter frozen on a hundred faces. In the bubble "
             "of stopped time, something the Culinaromancer sent is "
             "moving — and it smells like dinner gone very wrong.",
        exits={"out": "lumbridge_castle"},
        members=True,
        qlock=("recipe_for_disaster",
               ["agrith", "flambeed", "karamel", "culinaromancer",
                "complete"],
               "The castle doors are sealed inside a shimmer of stopped "
               "time. Gypsy Aris beckons urgently ('talk gypsy'). "
               "(Quest: Recipe for Disaster)")),
})
ROOMS["lumbridge_castle"]["exits"]["banquet"] = "banquet_hall"
_castle_npc = ROOMS["lumbridge_castle"].get("npc")
ROOMS["lumbridge_castle"]["npc"] = (
    [_castle_npc, "recipe_for_disaster"] if isinstance(_castle_npc, str)
    else (_castle_npc or []) + ["recipe_for_disaster"])
ROOMS["lumbridge_castle"]["desc"] += (" Today the great hall glimmers "
                                      "strangely — GYPSY ARIS wrings her "
                                      "hands outside it ('talk gypsy').")
REGIONS["banquet_hall"] = "Lumbridge"

# --- Recipe for Disaster (6 QP, 40 QP to start) ---------------------------------------
ALL_QUESTS["recipe_for_disaster"] = "Recipe for Disaster"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["recipe_for_disaster"] = 6
NPC_NAMES["recipe_for_disaster"] = "Gypsy Aris"
QUEST_STARTS["recipe_for_disaster"] = "Gypsy Aris, Lumbridge Castle " \
                                      "(requires 40 quest points)"
QUEST_HINTS["recipe_for_disaster"] = {
    "agrith": "enter the frozen banquet ('banquet') and defeat "
              "AGRITH-NA-NA, the banana demon",
    "flambeed": "defeat FLAMBEED — carry a BUCKET OF WATER or his heat "
                "will soften your blade",
    "karamel": "defeat KARAMEL, the ice queen of dessert (she freezes)",
    "culinaromancer": "face the CULINAROMANCER himself",
}

_RFD_ORDER = ["agrith-na-na", "flambeed", "karamel", "culinaromancer"]
_RFD_STAGE = {"agrith-na-na": "agrith", "flambeed": "flambeed",
              "karamel": "karamel", "culinaromancer": "culinaromancer"}


def talk_gypsy(p):
    stage = _q(p, "recipe_for_disaster")
    if stage == "not_started":
        qp = quest_points(p)
        if qp < 40:
            say(f"Gypsy Aris: \"The magic sealing that hall would unmake "
                f"a novice. Come back a HERO — forty quest points, no "
                f"less. (You have {qp}.)\"", "byellow")
            return
        banner("Quest Start: Recipe for Disaster", color="purple",
               line_color="bmagenta")
        say("Gypsy Aris: \"The CULINAROMANCER crashed the Duke's banquet "
            "— a chef-mage old as hunger itself. I froze the hall around "
            "him, but my magic is a cork in a flood. He is sending his "
            "COURSES through, one dish at a time. Fight them in the "
            "frozen hall ('banquet') — and gods help you at dessert.\"")
        p.quests["recipe_for_disaster"] = "agrith"
    elif stage in ("agrith", "flambeed", "karamel", "culinaromancer"):
        hint = QUEST_HINTS["recipe_for_disaster"].get(stage, "")
        say(f"Gypsy Aris: \"The hall holds — barely. {hint.capitalize()}!\"")
    elif stage == "complete":
        say("Gypsy Aris: \"The banquet resumed as if nothing happened — "
            "nobody but us remembers. Wear those gloves well, hero.\"")


QUEST_TALK["recipe_for_disaster"] = talk_gypsy


def _rfd_alive(boss):
    return lambda pl: _q(pl, "recipe_for_disaster") == _RFD_STAGE[boss]


for _b in _RFD_ORDER:
    QUEST_SPAWNS.append(("banquet_hall", _b, _rfd_alive(_b)))


# --- kill hook: course by course, then the chef ---------------------------------------
_prev_quest_on_kill_rfd = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811 (wraps prior)
    _prev_quest_on_kill_rfd(p, target)
    stage = _q(p, "recipe_for_disaster")
    if target == "agrith-na-na" and stage == "agrith":
        p.quests["recipe_for_disaster"] = "flambeed"
        say("The banana demon splatters — and the air shimmers as the "
            "next course arrives: FLAMBEED, wreathed in kitchen-fire. "
            "(Carry a bucket of water!)", "byellow", "bold")
    elif target == "flambeed" and stage == "flambeed":
        p.quests["recipe_for_disaster"] = "karamel"
        p.add("cooking gauntlets")
        say("Flambeed gutters out. In the hiss of steam you find COOKING "
            "GAUNTLETS, forge-cooled and perfect — and the hall grows "
            "suddenly, sweetly COLD. KARAMEL is served.", "byellow",
            "bold")
    elif target == "karamel" and stage == "karamel":
        p.quests["recipe_for_disaster"] = "culinaromancer"
        say("The ice queen shatters into sugar-glass — and the frozen "
            "feast falls silent. HE steps through the shimmer himself: "
            "the CULINAROMANCER.", "byellow", "bold")
    elif target == "culinaromancer" and stage == "culinaromancer":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Recipe for Disaster", color="byellow",
               line_color="gold")
        say("The Culinaromancer comes apart into spilt flour and old "
            "hunger, and time snaps back — the banquet resumes "
            "mid-toast, none the wiser. In his larder chest you find his "
            "masterwork: the BARROWS GLOVES, the finest ever stitched. "
            "25,000 cooking and 15,000 defence xp awarded.", "bgreen")
        p.gain_xp("cooking", 25000)
        p.gain_xp("defence", 15000)
        p.add("barrows gloves")
        p.quests["recipe_for_disaster"] = "complete"
