

# ===========================================================================
#  TIRANNWN  (the Underground Pass, Song of the Elves, Prifddinas,
#             the Gauntlet, and Zalcano)
# ===========================================================================
# West of Ardougne a tunnel swallows the light: the Underground Pass opens
# onto Isafdar, the elven forest, where Eluned begins SONG OF THE ELVES —
# slay the Fragment of Seren at the gates and the crystal city of
# PRIFDDINAS opens: a bank amid singing towers, THE GAUNTLET (Crystalline
# Hunllef, source of the crystal armoury) and Zalcano's mine (the skilling
# boss only a pickaxe can crack).

# --- the crystal armoury -------------------------------------------------------
add_item("crystal shard", 1200, members=True)
EFFECT_NOTES["crystal shard"] = ("a splinter of living crystal — Prifddinas "
                                 "hums with them")
add_item("crystal armour seed", 800000, members=True)
EFFECT_NOTES["crystal armour seed"] = ("sing it into crystal armour "
                                       "('craft crystal body' / 'legs')")
add_item("enhanced crystal weapon seed", 4500000, members=True)
EFFECT_NOTES["enhanced crystal weapon seed"] = ("the rarest song of the "
                                                "Gauntlet — becomes the "
                                                "blade of saeldor")
add_item("blade of saeldor", 5200000, members=True, equip={
    "slot": "weapon", "astab": 55, "aslash": 94, "acrush": 40, "str": 89,
    "req": {"attack": 80}})
EFFECT_NOTES["blade of saeldor"] = ("a sword sung from crystal — the "
                                    "sharpest slash in Gielinor")
add_item("crystal body", 1500000, members=True, equip={
    "slot": "body", "arange": 14, "amagic": 10, "dstab": 70, "dslash": 78,
    "dcrush": 72, "dmagic": 55, "drange": 80,
    "req": {"defence": 70, "crafting": 72}})
add_item("crystal legs", 1100000, members=True, equip={
    "slot": "legs", "arange": 9, "amagic": 6, "dstab": 45, "dslash": 50,
    "dcrush": 47, "dmagic": 35, "drange": 52,
    "req": {"defence": 70, "crafting": 72}})
EFFECT_NOTES["crystal body"] = ("hybrid crystal plate — arrows and spells "
                                "both fly truer")
CRAFT_RECIPES.update({
    "blade of saeldor": ("enhanced crystal weapon seed", 1, 82, 1500),
    "crystal body": ("crystal armour seed", 1, 74, 900),
    "crystal legs": ("crystal armour seed", 1, 72, 700),
})

# --- the elves of Isafdar --------------------------------------------------------
_add_mob("elf warrior",
    {"abonus": 20, "atktype": ["stab", "ranged"], "att": 90, "cb": 108,
     "dstab": 35, "dslash": 40, "dcrush": 35, "dmagic": 40, "drange": 45,
     "def": 80, "hp": 105, "maxhit": 11, "str": 90, "weak": "crush"},
    [("coins", 200, 900, 1.0), ("crystal shard", 1, 2, 0.15),
     ("grimy ranarr", 1, 3, 0.2)], members=True, rank="hard")

# --- Fragment of Seren (Song of the Elves finale) --------------------------------
SEREN_ART = r"""
          .    /\    .
         / \  /  \  / \
        <   \/ () \/   >     the FRAGMENT OF SEREN —
         \   |    |   /       grief given crystal form
        < \  |    |  / >
         \ \_|____|_/ /
          '   \  /   '
               \/
"""


def _seren_heal(p, m, dmg):
    if m["cur"] > 0 and m["cur"] < m["hp"] and random.random() < 0.35:
        heal = min(random.randint(4, 10), m["hp"] - m["cur"])
        m["cur"] += heal
        print("  " + paint(f"Shards sing themselves whole again. "
                           f"(+{heal})", "bcyan"))


SEREN_ATTACKS = [
    {"label": "a lance of crystal light", "verb": "focuses",
     "color": ("bcyan", "bold"), "builder": _fx_bolt_blue,
     "mult": 1.1, "w": 3, "atype": "magic"},
    {"label": "a storm of singing shards", "verb": "scatters",
     "color": ("bwhite", "bold"), "builder": _fx_slag,
     "mult": 0.9, "w": 2, "atype": "ranged", "effect": _seren_heal},
]


def _seren_intro(name):
    return _fx((SEREN_ART, "grey", "dim"), (SEREN_ART, "bcyan"),
               (SEREN_ART, "bwhite", "bold"))


def _seren_death(name):
    return _fx((SEREN_ART, "bcyan"), (SEREN_ART, "grey", "dim"))


_add_mob("fragment of seren",
    {"abonus": 40, "atktype": ["magic", "ranged"], "att": 200, "cb": 494,
     "dstab": 90, "dslash": 90, "dcrush": 60, "dmagic": 95, "drange": 90,
     "def": 130, "hp": 250, "maxhit": 22, "str": 170, "weak": "crush"},
    [("crystal shard", 6, 14, 1.0), ("coins", 6000, 18000, 1.0)],
    members=True)
MONSTERS["fragment of seren"]["boss"] = True
MONSTERS["fragment of seren"]["rank"] = "boss"
_BOSSES.add("fragment of seren")
BOSS_TURN["fragment of seren"] = \
    lambda p, m: _boss_take_turn(p, m, SEREN_ATTACKS)
BOSS_INTRO["fragment of seren"] = _seren_intro
BOSS_DEATH["fragment of seren"] = _seren_death
MONSTER_ART["fragment of seren"] = SEREN_ART

# --- the Crystalline Hunllef (the Gauntlet) ---------------------------------------
HUNLLEF_ART = r"""
        /\_/\ ______ /\_/\
       ( >< )/      \( >< )
        \  /| (^^) |\  /       the CRYSTALLINE HUNLLEF
         \/ |  --  | \/         stalks the Gauntlet!
        /|  '------'  |\
       ' |  |  ||  |  | '
         w  w  ww  w  w
"""

_HUNLLEF_STYLES = {
    "magic": ("bblue", "the Hunllef's horns crackle — CRYSTAL MAGIC "
                       "incoming! (protect from magic)"),
    "ranged": ("bgreen", "the Hunllef rears — CRYSTAL SPINES incoming! "
                         "(protect from missiles)"),
}


def _hunllef_take_turn(p, m):
    t = m.get("hun_turn", 0)
    m["hun_turn"] = t + 1
    if t % 4 == 0:                       # swap attack style every 4 turns
        style = "magic" if (t // 4) % 2 == 0 else "ranged"
        m["hun_style"] = style
        color, cry = _HUNLLEF_STYLES[style]
        say(cry, color, "bold")
    if t % 5 == 4:                       # crystal tornadoes sweep the floor
        animate(_fx((FX_SMASH1, "bcyan"), (FX_SMASH2, "bwhite", "bold")),
                delay=0.13, center=True)
        dmg = min(random.randint(4, 12), max(0, p.hp - 1))
        if dmg:
            p.hp -= dmg
            print("  " + paint(f"Crystal tornadoes rake you for {dmg} — "
                               "keep moving!", "bcyan") + "  "
                  + paint("HP ", "white")
                  + bar_meter(max(p.hp, 0), p.max_hp, 18))
        return "died" if p.hp <= 0 else None
    atype = m.get("hun_style", "magic")
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    p_def_roll = _player_def_roll(p, atype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, m["max_hit"])
        if p.prayer_protects(atype):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        print("  " + paint(f"The Hunllef strikes for {dmg}.", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
    else:
        print("  " + paint("You weave between the crystal bolts.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer "
                               "points).", "bmagenta"))
    return "died" if p.hp <= 0 else None


def _hunllef_intro(name):
    return _fx((HUNLLEF_ART, "grey", "dim"), (HUNLLEF_ART, "bcyan"),
               (HUNLLEF_ART, "bwhite", "bold"), (HUNLLEF_ART, "bcyan", "bold"))


def _hunllef_death(name):
    return _fx((HUNLLEF_ART, "bred"), (HUNLLEF_ART, "bcyan", "dim"),
               (HUNLLEF_ART, "grey", "dim"))


_add_mob("crystalline hunllef",
    {"abonus": 45, "atktype": ["magic", "ranged"], "att": 240, "cb": 674,
     "dstab": 60, "dslash": 95, "dcrush": 95, "dmagic": 95, "drange": 95,
     "def": 150, "hp": 300, "maxhit": 24, "str": 200, "weak": "stab"},
    [("crystal shard", 8, 20, 1.0), ("crystal armour seed", 1, 1, 0.08),
     ("enhanced crystal weapon seed", 1, 1, 0.02),
     ("coins", 8000, 24000, 1.0), ("grimy ranarr", 2, 6, 0.4)],
    members=True)
MONSTERS["crystalline hunllef"]["boss"] = True
MONSTERS["crystalline hunllef"]["rank"] = "boss"
_BOSSES.add("crystalline hunllef")
BOSS_TURN["crystalline hunllef"] = _hunllef_take_turn
BOSS_INTRO["crystalline hunllef"] = _hunllef_intro
BOSS_DEATH["crystalline hunllef"] = _hunllef_death
MONSTER_ART["crystalline hunllef"] = HUNLLEF_ART

# --- Zalcano (the skilling boss — pickaxes only) -----------------------------------
ZALCANO_ART = r"""
           _____________
          /  (o)   (o)  \
         |   _________   |     ZALCANO — a demon
        /|  |  ##### |   |\     bound in stone.
       ( |  |__#####_|   | )
        \|_____________ /|/     (only a PICKAXE
         //  ||    ||  \\        cracks her!)
        ^^   ||    ||   ^^
"""


def _zalcano_rocks(p, m, dmg):
    if dmg > 0 and random.random() < 0.35:
        extra = min(random.randint(2, 7), max(0, p.hp - 1))
        if extra:
            p.hp -= extra
            print("  " + paint(f"Falling rubble batters you for {extra} "
                               "more!", "brown"))


ZALCANO_ATTACKS = [
    {"label": "a hail of molten stone", "verb": "hurls",
     "color": ("orange", "bold"), "builder": _fx_slag,
     "mult": 1.0, "w": 3, "atype": "ranged", "effect": _zalcano_rocks},
    {"label": "a shockwave through the floor", "verb": "slams",
     "color": ("brown", "bold"), "builder": _fx_smash,
     "mult": 0.9, "w": 2, "atype": "crush"},
]


def _zalcano_intro(name):
    return _fx((ZALCANO_ART, "grey", "dim"), (ZALCANO_ART, "brown"),
               (ZALCANO_ART, "orange", "bold"))


def _zalcano_death(name):
    return _fx((ZALCANO_ART, "orange"), (ZALCANO_ART, "grey", "dim"))


_add_mob("zalcano",
    {"abonus": 35, "atktype": ["ranged", "crush"], "att": 180, "cb": 336,
     "dstab": 100, "dslash": 100, "dcrush": 40, "dmagic": 100,
     "drange": 100, "def": 140, "hp": 300, "maxhit": 18, "str": 160,
     "weak": "crush"},
    [("crystal shard", 4, 10, 1.0), ("gold ore", 3, 10, 0.7),
     ("uncut ruby", 1, 3, 0.4), ("adamant bar", 1, 3, 0.4),
     ("coins", 5000, 16000, 1.0), ("crystal armour seed", 1, 1, 0.04)],
    members=True)
MONSTERS["zalcano"]["boss"] = True
MONSTERS["zalcano"]["rank"] = "boss"
MONSTERS["zalcano"]["pick_only"] = True
_BOSSES.add("zalcano")
BOSS_TURN["zalcano"] = lambda p, m: _boss_take_turn(p, m, ZALCANO_ATTACKS)
BOSS_INTRO["zalcano"] = _zalcano_intro
BOSS_DEATH["zalcano"] = _zalcano_death
MONSTER_ART["zalcano"] = ZALCANO_ART

# --- the region --------------------------------------------------------------------
ROOMS.update({
    "underground_pass": dict(name="The Underground Pass",
        desc="A tunnel of rope bridges and old traps under the mountains, "
             "lit by guttering torches. Something skitters in the dark. "
             "Daylight glimmers far to the west.",
        exits={"east": "ardougne", "west": "isafdar"},
        monsters=["skeleton", "giant spider", "dark wizard"],
        hostile=True, members=True),
    "isafdar": dict(name="Isafdar",
        desc="An ancient elven forest, deep-shadowed and trapped. Elf "
             "warriors watch from the leaves — and ELUNED, a priestess of "
             "Seren, beckons urgently ('talk'). Crystal spires glitter "
             "north at the city gates ('gates').",
        exits={"east": "underground_pass", "gates": "prifddinas_gates"},
        monsters=["elf warrior"], npc="song_of_the_elves",
        hostile=True, members=True),
    "prifddinas_gates": dict(name="The Gates of Prifddinas",
        desc="Towering crystal gates, sealed for an age. The city hums "
             "behind them like a struck chord.",
        exits={"south": "isafdar", "city": "prifddinas"},
        members=True),
    "prifddinas": dict(name="Prifddinas",
        desc="The crystal city, singing softly. Elves work looms and "
             "forges of light between towers grown from seed. A bank "
             "shines like cut glass; below, the GAUNTLET's maw glows "
             "('gauntlet'), and Zalcano rages in her mine ('mine').",
        exits={"gates": "prifddinas_gates", "gauntlet": "the_gauntlet",
               "mine": "zalcano_chamber"},
        bank=True, ge=True, prayer_altar=True, members=True,
        qlock=("song_of_the_elves", ["complete"],
               "The crystal gates are sealed — the Fragment of Seren bars "
               "the way. (Quest: Song of the Elves — Eluned in Isafdar)")),
    "the_gauntlet": dict(name="The Gauntlet",
        desc="A shifting maze of crystal where the city sends its "
             "champions. At its heart, the CRYSTALLINE HUNLLEF paces — "
             "its armoury is the finest crystal in the world.",
        exits={"out": "prifddinas"},
        monsters=["crystalline hunllef"], members=True),
    "zalcano_chamber": dict(name="Zalcano's Mine",
        desc="A gutted mine glowing furnace-red. ZALCANO, a demon bound "
             "into living stone, tears ore from the walls and hurls it "
             "molten. Steel means nothing here — bring a pickaxe.",
        exits={"out": "prifddinas"},
        monsters=["zalcano"], members=True),
})
ROOMS["ardougne"]["exits"]["pass"] = "underground_pass"
ROOMS["ardougne"]["desc"] += (" West of the city, a dark tunnel mouth opens "
                              "under the mountains ('pass').")
REGIONS.update({"underground_pass": "Kandarin", "isafdar": "Tirannwn",
                "prifddinas_gates": "Tirannwn", "prifddinas": "Tirannwn",
                "the_gauntlet": "Tirannwn", "zalcano_chamber": "Tirannwn"})
TRAVEL_HUBS["prifddinas"] = "prifddinas"
TRAVEL_NAMES.append("Prifddinas")

# --- Song of the Elves (5 QP) ---------------------------------------------------
ALL_QUESTS["song_of_the_elves"] = "Song of the Elves"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["song_of_the_elves"] = 5
NPC_NAMES["song_of_the_elves"] = "Eluned"
QUEST_STARTS["song_of_the_elves"] = "Eluned, Isafdar (through the " \
                                    "Underground Pass west of Ardougne)"
QUEST_HINTS["song_of_the_elves"] = {
    "seren": "slay the FRAGMENT OF SEREN at the gates of Prifddinas "
             "('gates' from Isafdar)",
}


def talk_eluned(p):
    stage = _q(p, "song_of_the_elves")
    if stage == "not_started":
        banner("Quest Start: Song of the Elves", color="purple",
               line_color="bmagenta")
        say("Eluned: \"Prifddinas has been sealed for an age — and what "
            "seals it is no gate. A FRAGMENT OF SEREN, our own goddess's "
            "grief, stands vigil and strikes down all who approach. End "
            "her sorrow at the gates, and the city will sing again.\"")
        p.quests["song_of_the_elves"] = "seren"
    elif stage == "seren":
        say("Eluned: \"The Fragment waits at the gates ('gates'). Crush "
            "weapons shatter crystal best — and go blessed, her light "
            "burns.\"")
    elif stage == "complete":
        say("Eluned: \"The city sings because of you. The Gauntlet and "
            "Zalcano's mine test even heroes — go well.\"")


QUEST_TALK["song_of_the_elves"] = talk_eluned

# the Fragment stands vigil only while the quest demands it
QUEST_SPAWNS.append(("prifddinas_gates", "fragment of seren",
                     lambda pl: _q(pl, "song_of_the_elves") == "seren"))


# --- kill hooks: Seren's fall opens the city; Zalcano pays in xp ------------------
_prev_quest_on_kill_sote = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811  (wraps prior)
    _prev_quest_on_kill_sote(p, target)
    if target == "fragment of seren" and \
            _q(p, "song_of_the_elves") == "seren":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Song of the Elves", color="byellow",
               line_color="gold")
        say("The Fragment sighs into a rain of gentle light, and the "
            "gates of Prifddinas swing wide for the first time in an age. "
            "20,000 agility and 20,000 crafting xp awarded — and the "
            "elves press CRYSTAL SHARDS into your hands.", "bgreen")
        p.gain_xp("agility", 20000)
        p.gain_xp("crafting", 20000)
        p.add("crystal shard", 20)
        p.quests["song_of_the_elves"] = "complete"
    if target == "zalcano":
        mxp, sxp = 1500, 1000
        p.gain_xp("mining", mxp)
        p.gain_xp("smithing", sxp)
        say("Prospecting her shattered core pays in kind.", "brown")
