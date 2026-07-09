# ===========================================================================
#  CRANDOR & ELVARG  (dragons — a Dragon-Slayer-flavoured expansion)
# ===========================================================================
# New loot loop: green dragons & Elvarg drop dragon bones (bury -> big prayer
# xp) and green dragonhide (tan -> craft the green d'hide armour that already
# exists in the gear tables).

add_item("dragon bones", 90, bury=("prayer", 72))
add_item("green dragonhide", 1500)
add_item("green dragon leather", 1700)

TAN_HIDES["green dragonhide"] = ("green dragon leather", 20)
CRAFT_RECIPES.update({
    "green d'hide vambraces": ("green dragon leather", 1, 57, 62),
    "green d'hide chaps": ("green dragon leather", 2, 60, 124),
    "green d'hide body": ("green dragon leather", 3, 63, 186),
})

# --- Elvarg the dragon: art + a dragonfire moveset -------------------------
_ELVARG_BRAILLE = '''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⣲⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠖⠋⢀⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠜⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠊⠀⠀⡠⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠊⡰⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⠀⠀⡜⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠚⠁⡜⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⠀⠀⠀⠀⢀⣀⣀⠤⠖⠈⠀⠀⢀⡜⠀⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠓⠲⢤⣸⠒⣊⣭⠛⠉⠀⠀⠀⠀⠀⢀⣠⢿⡶⠛⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⣹⠎⠀⠀⠑⡄⠀⢀⡠⠔⢊⡥⢺⠋
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠎⠀⠀⠀⣠⠞⠁⠀⠀⠀⢀⣾⠋⠁⣠⠞⠁⠀⢸⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠃⠀⡠⠊⡜⠁⠀⠀⠀⢀⡊⠁⠁⠀⢊⡀⠀⠀⠀⣀⣉⣓⣦⡤⠤
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡤⠊⠁⠸⠀⠀⠀⡠⡖⡝⠀⠀⠀⠀⠀⠈⢉⡩⠭⠒⢋⡟⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠁⠀⠀⠀⠑⠒⠛⠒⠋⠁⠀⠀⠀⠀⠀⠀⠘⠤⣀⡀⠈⣇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠜⠁⠀⠀⠀⠀⠀⠀⢀⣀⠤⠄⠀⠀⠀⡰⠚⢧⠉⠒⠒⠮⠽⣾⣦⣀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠋⠁⡠⣖⠂⠀⠀⠀⡠⠋⠉⠀⡀⠀⠀⢀⡴⠁⠀⠸⡄⠀⠀⠀⠀⡇⠙⢌⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠘⠐⠁⣀⡠⠔⠋⣀⣀⡴⠚⠓⡶⣞⣉⣀⣀⡠⢤⠇⠀⠀⠀⢰⣃⡀⠈⢳⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣀⣠⡊⠁⡀⣠⠞⠁⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⣿⠀⠈⠑⢄⢳
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣽⢻⡏⠁⠀⠀⠀⢀⠞⠑⠦⠤⠤⠤⠄⡸⠁⠀⠀⠀⢸⠉⣆⠀⠀⠘⡾
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠀⠃⠀⠀⠀⢀⢏⠀⠀⠀⠀⠀⠀⡰⠁⠀⠀⠀⠀⢸⠀⠘⡄⠀⠀⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠑⠦⠤⠤⠄⢲⠁⠀⠀⠀⠀⠀⠘⣆⣀⣹
'''
# blank braille (U+2800) -> real space so the negative space is empty, not a
# filled block; the dot glyphs remain to draw the dragon.
ELVARG_CALM = _ELVARG_BRAILLE.replace("⠀", " ")
ELVARG_FIRE = ELVARG_CALM
ELVARG_DIE = ELVARG_CALM


def _elvarg_intro(name):
    return [_tint(ELVARG_CALM, "green"), _tint(ELVARG_CALM, "bgreen", "bold"),
            _tint(ELVARG_FIRE, "orange", "bold"), _tint(ELVARG_FIRE, "byellow", "bold"),
            _tint(ELVARG_CALM, "bgreen", "bold")]


def _elvarg_death(name):
    return [_tint(ELVARG_CALM, "bred"), _tint(ELVARG_CALM, "grey"),
            _tint(ELVARG_DIE, "grey", "dim")]


def _elvarg_fire(_=None):
    return [_tint(ELVARG_FIRE, "orange", "bold"), _tint(ELVARG_FIRE, "byellow", "bold"),
            _tint(ELVARG_FIRE, "bred", "bold")]


def _elvarg_bite(_=None):
    return [_tint(ELVARG_CALM, "bgreen", "bold"), _tint(ELVARG_FIRE, "bred", "bold")]


ELVARG_ATTACKS = [
    {"label": "a searing blast of dragonfire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _elvarg_fire, "mult": 1.5, "w": 3,
     "atype": "magic", "dragonfire": True},
    {"label": "her great fangs", "verb": "snaps with", "color": ("bgreen", "bold"),
     "builder": _elvarg_bite, "mult": 1.0, "w": 3, "atype": "stab"},
    {"label": "a lashing tail swipe", "verb": "strikes with",
     "color": ("green", "bold"), "builder": _elvarg_bite, "mult": 1.1, "w": 2,
     "atype": "crush"},
]

BOSS_INTRO["elvarg"] = _elvarg_intro
BOSS_DEATH["elvarg"] = _elvarg_death
BOSS_TURN["elvarg"] = lambda p, m: _boss_take_turn(p, m, ELVARG_ATTACKS)
MONSTER_ART["elvarg"] = ELVARG_CALM

# --- Dragons (green dragon is farmable; Elvarg is the boss) ----------------
_add_mob("green dragon",
    {"abonus": 0, "atktype": ["slash", "dragonfire"], "att": 68, "cb": 79,
     "dstab": 20, "dslash": 20, "dcrush": 20, "dmagic": -20, "drange": 10,
     "def": 68, "hp": 75, "maxhit": 8, "str": 68, "weak": "ranged"},
    [("dragon bones", 1, 1, 1.0), ("green dragonhide", 1, 1, 1.0),
     ("coins", 30, 120, 0.8)], rank="hard")

_add_mob("elvarg",
    {"abonus": 0, "atktype": ["slash", "dragonfire"], "att": 120, "cb": 83,
     "dstab": 10, "dslash": 45, "dcrush": 45, "dmagic": 25, "drange": 30,
     "def": 75, "hp": 120, "maxhit": 10, "str": 120, "weak": "stab"},
    [("dragon bones", 1, 1, 1.0), ("green dragonhide", 2, 3, 1.0),
     ("coins", 1000, 3000, 1.0), ("dragon med helm", 1, 1, 0.04)])
MONSTERS["elvarg"]["boss"] = True
MONSTERS["elvarg"]["rank"] = "boss"
_BOSSES.add("elvarg")

# --- Crandor: a volcanic dragon isle reached by sailing from Karamja -------
ROOMS.update({
    "crandor": dict(name="Crandor",
        desc="A volcanic island long shunned by sailors. Black sand, the bones "
             "of failed adventurers, and green dragons basking in the heat. A "
             "dragon's roar rolls down from the caldera.",
        exits={"sail": "karamja_port", "caldera": "elvarg_lair"},
        monsters=["skeleton", "green dragon"]),
    "elvarg_lair": dict(name="Elvarg's Lair",
        desc="The molten heart of Crandor. Elvarg, the dread green dragon, "
             "coils atop a hoard of charred bones and gold.",
        exits={"out": "crandor"},
        monsters=["elvarg"]),
})
ROOMS["karamja_port"]["exits"]["sail"] = "crandor"

TRAVEL_HUBS["crandor"] = "crandor"
TRAVEL_NAMES.append("Crandor")


# ===========================================================================
#  DRAGON SLAYER  (the capstone quest)
# ===========================================================================
# Earn 12 quest points, talk to the Guildmaster at the Champions' Guild, then
# Oziach west of Edgeville. Gather the three map pieces, buy and repair the
# Lady Lumbridge at Port Sarim, and slay Elvarg. Rewards: 18,650 strength and
# defence xp and the right to wear the rune platebody / green d'hide body.

QUEST_POINTS = {
    "cooks_assistant": 1, "sheep_shearer": 1, "dorics_quest": 1,
    "romeo_juliet": 5, "vampyre_slayer": 3, "restless_ghost": 1,
    "rune_mysteries": 1, "imp_catcher": 1, "witch_potion": 1,
    "ernest_chicken": 4, "dragon_slayer": 2,
}
GUILD_QP = 12      # quest points needed to enter the Champions' Guild


def quest_points(p):
    return sum(QUEST_POINTS.get(k, 1) for k in ALL_QUESTS
               if _q(p, k) == "complete")


ALL_QUESTS["dragon_slayer"] = "Dragon Slayer"

MAP_PIECES = ["melzar's map piece", "wormbrain's map piece", "lozar's map piece"]
for _piece in MAP_PIECES:
    add_item(_piece, 1)
add_item("anti-dragon shield", 40, equip={
    "amagic": -8, "arange": -2, "dstab": 7, "dslash": 9, "dcrush": 8,
    "dmagic": 1, "drange": 9, "slot": "shield"})

# the classic rewards are locked behind the quest
ITEMS["rune platebody"]["equip"]["quest"] = "dragon_slayer"
ITEMS["green d'hide body"]["equip"]["quest"] = "dragon_slayer"

SHOPS["oziach"] = {"anti-dragon shield": 40, "rune platebody": 65000,
                   "green d'hide body": 7800}

ROOMS.update({
    "champions_guild": dict(name="Champions' Guild",
        desc="A proud hall south-west of Varrock where only proven "
             "adventurers may enter. The Guildmaster sizes you up from his "
             "chair by the fire.",
        exits={"east": "varrock_gate"}, npc="dragon_slayer"),
    "oziach_hut": dict(name="Oziach's Hut",
        desc="A shabby hut by the river west of Edgeville. Oziach, a "
             "wild-eyed armourer, mutters about dragons as he works.",
        exits={"east": "edgeville"}, npc="oziach", shop="oziach"),
    "melzars_maze": dict(name="Melzar's Maze",
        desc="A decaying stronghold north of Rimmington, sealed since Crandor "
             "fell. The shambling dead wander halls that still reek of ash.",
        exits={"out": "rimmington"},
        monsters=["zombie", "skeleton", "giant rat"]),
})
ROOMS["varrock_gate"]["exits"]["guild"] = "champions_guild"
ROOMS["edgeville"]["exits"]["hut"] = "oziach_hut"
ROOMS["rimmington"]["exits"]["maze"] = "melzars_maze"
ROOMS["port_sarim"]["exits"]["crandor"] = "crandor"
ROOMS["port_sarim"]["npc"] = "klarense"

REGIONS.update({"champions_guild": "Varrock", "oziach_hut": "Edgeville",
                "melzars_maze": "Rimmington"})

# Crandor is unreachable until the Lady Lumbridge is seaworthy
ROOMS["crandor"]["qlock"] = (
    "dragon_slayer", ("sail", "complete"),
    "The reefs around Crandor have sunk every ship that dared approach. You "
    "need a seaworthy ship and a route through the reef. (Quest: Dragon Slayer)")


def talk_guildmaster(p):
    stage = _q(p, "dragon_slayer")
    if stage == "not_started":
        qp = quest_points(p)
        if qp < GUILD_QP:
            say("Guildmaster: \"Champions only! Prove yourself on Gielinor's "
                f"quests and return with {GUILD_QP} quest points. You have "
                f"{qp}.\"", "byellow")
            say("  (Check your progress with 'quests'.)", "grey")
            return
        banner("Quest Start: Dragon Slayer", color="purple", line_color="bmagenta")
        say("Guildmaster: \"So you seek the right to wear rune armour? Then "
            "hear this: ELVARG, the dragon of Crandor, burned that isle to "
            "cinders and has never been slain. Speak to OZIACH, the armourer "
            "in a hut west of Edgeville — only he can grant you the honour.\"")
        p.quests["dragon_slayer"] = "started"
    elif stage == "complete":
        say("Guildmaster: \"The slayer of Elvarg! Drinks are on the guild, "
            "champion.\"")
    else:
        say("Guildmaster: \"Oziach's hut is west of Edgeville ('hut'). Elvarg "
            "awaits.\"")


def talk_oziach(p):
    stage = _q(p, "dragon_slayer")
    if stage == "started":
        banner("Dragon Slayer", color="purple", line_color="bmagenta")
        say("Oziach: \"Rune armour, is it? Slay ELVARG of Crandor and you've "
            "earned it. But no ship's route to Crandor survives whole — the "
            "map was torn in three:\"")
        say("  • MELZAR'S piece — search Melzar's Maze, north of Rimmington", "bcyan")
        say("  • WORMBRAIN'S piece — a goblin of Lumbridge Forest swallowed it", "bcyan")
        say("  • LOZAR'S piece — locked in a magic chest in Draynor Manor", "bcyan")
        say("Oziach: \"Take this as well — no shield, no dragon-slaying.\"")
        p.add("anti-dragon shield")
        say("(He hands you an ANTI-DRAGON SHIELD — equip it before facing "
            "dragonfire!)", "bgreen")
        say("\"With all three pieces, buy a ship from KLARENSE at Port Sarim.\"")
        p.quests["dragon_slayer"] = "maps"
    elif stage == "maps":
        missing = [i for i in MAP_PIECES if not p.has(i)]
        if missing:
            _need_msg("Oziach", missing)
        else:
            say("Oziach: \"The whole map! Now buy that ship off KLARENSE at "
                "Port Sarim and sail.\"")
    elif stage == "sail":
        say("Oziach: \"The Lady Lumbridge is ready — sail from Port Sarim "
            "('go crandor') and end Elvarg!\"")
    elif stage == "complete":
        say("Oziach: \"Dragon Slayer! My rune platebodies are yours to buy — "
            "and at last to wear. ('shop')\"")
    else:
        say("Oziach: \"I only deal with champions. See the Guildmaster at the "
            "Champions' Guild, south-west of Varrock.\"")


def talk_klarense(p):
    stage = _q(p, "dragon_slayer")
    if stage in ("sail", "complete"):
        say("Klarense: \"She's your ship now. Fair winds to Crandor! "
            "('go crandor')\"")
        return
    if stage != "maps":
        say("Klarense: \"Fine ship, the Lady Lumbridge. Not for sale, mind... "
            "unless a dragon-slaying came into it.\"")
        return
    missing = [i for i in MAP_PIECES if not p.has(i)]
    if missing:
        _need_msg("Klarense", missing)
        return
    needs = []
    if not p.has("coins", 2000):
        needs.append("2,000 coins")
    if not p.has("steel bar", 2):
        needs.append("2 steel bars (to patch the hull)")
    if not p.has("hammer"):
        needs.append("a hammer")
    if needs:
        say("Klarense: \"The Lady Lumbridge is yours for 2,000 coins — but "
            "her hull needs work. Bring " + ", ".join(needs) + ".\"", "byellow")
        return
    p.take("coins", 2000)
    p.take("steel bar", 2)
    for i in MAP_PIECES:
        p.take(i)
    banner("The Lady Lumbridge is seaworthy!", color="bcyan", line_color="bcyan")
    say("You hammer steel plate over her hull and chart the reef from the "
        "three map pieces. Klarense signs her over. Crandor lies dead ahead — "
        "'go crandor'. Bring your anti-dragon shield!", "bgreen")
    p.quests["dragon_slayer"] = "sail"


QUEST_TALK["dragon_slayer"] = talk_guildmaster
QUEST_TALK["oziach"] = talk_oziach
QUEST_TALK["klarense"] = talk_klarense


# ===========================================================================
#  THE KNIGHT'S SWORD  &  PRINCE ALI RESCUE
# ===========================================================================
# Two more classics. The Knight's Sword: help a Falador squire replace Sir
# Vyvin's lost blade — find Thurgo the Imcando dwarf (he loves redberry pie),
# mine blurite, and reforge it for a huge slug of smithing xp. Prince Ali
# Rescue: spring the prince from Draynor jail with a disguise; the grateful
# emirate makes the Al Kharid toll gate free forever.

add_item("redberry pie", 12, heal=5)
SHOPS["general"]["redberry pie"] = 12
add_item("blurite ore", 60)
ROCKS["blurite"] = ("blurite ore", 10, 18)
add_item("knight's sword", 100, equip={
    "astab": 6, "aslash": 9, "acrush": -2, "str": 8, "slot": "weapon",
    "req": {"attack": 5}})
add_item("blonde wig", 2)
add_item("bronze key", 1)

ROOMS.update({
    "white_knights_castle": dict(name="White Knights' Castle",
        desc="The great white keep of Falador. Knights drill in the courtyard "
             "while a young squire paces, looking close to tears.",
        exits={"south": "falador_square"}, npc="knights_sword"),
    "mudskipper_point": dict(name="Mudskipper Point",
        desc="A windswept spit south of Port Sarim. Thurgo, last of the "
             "Imcando dwarves, tends a forge by his hut. An icy cave mouth "
             "yawns nearby ('cave').",
        exits={"north": "port_sarim", "cave": "icy_cavern"},
        npc="thurgo", anvil=True),
    "icy_cavern": dict(name="Icy Cavern",
        desc="A frozen cavern beneath Asgarnia. Rare blurite veins glitter "
             "blue in the walls, guarded by hulking ice giants.",
        exits={"out": "mudskipper_point"},
        rocks=["blurite"], monsters=["ice giant"]),
    "draynor_jail": dict(name="Draynor Jail",
        desc="A squat stone jail on the village edge. Lady Keli holds court "
             "over her toughs while a hooded prisoner waits in the cell.",
        exits={"out": "draynor_village"}),
})
ROOMS["falador_square"]["exits"]["castle"] = "white_knights_castle"
ROOMS["port_sarim"]["exits"]["point"] = "mudskipper_point"
ROOMS["draynor_village"]["exits"]["jail"] = "draynor_jail"
ROOMS["al_kharid_palace"]["npc"] = "prince_ali"
ROOMS["falador_square"]["desc"] += " The White Knights' Castle rises north ('castle')."
ROOMS["port_sarim"]["desc"] += " Mudskipper Point lies south ('point')."
ROOMS["draynor_village"]["desc"] += " A squat jail stands at the edge of town ('jail')."
ROOMS["al_kharid_palace"]["desc"] += " Osman, the Emir's chancellor, beckons you over."

REGIONS.update({"white_knights_castle": "Falador",
                "mudskipper_point": "PortSarim", "icy_cavern": "PortSarim",
                "draynor_jail": "Draynor"})

ALL_QUESTS.update({"knights_sword": "The Knight's Sword",
                   "prince_ali": "Prince Ali Rescue"})
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS.update({"knights_sword": 1, "prince_ali": 3})


def talk_squire(p):
    stage = _q(p, "knights_sword")
    if stage == "not_started":
        banner("Quest Start: The Knight's Sword", color="purple",
               line_color="bmagenta")
        say("Squire: \"I've lost Sir Vyvin's family sword — I'm ruined! Only "
            "an IMCANDO DWARF could reforge such a blade. THURGO, the last of "
            "them, lives at Mudskipper Point south of Port Sarim ('point'). "
            "One thing: Imcando dwarves are mad for REDBERRY PIE...\"")
        p.quests["knights_sword"] = "started"
    elif stage == "sword":
        has = p.has("knight's sword")
        if not has and p.equipment.get("weapon") == "knight's sword":
            p.equipment["weapon"] = None            # hand it over off your back
            has = True
        elif has:
            p.take("knight's sword")
        if has:
            _complete_banner("The Knight's Sword")
            say("The squire nearly faints with relief. \"Sir Vyvin will never "
                "know!\" Watching Thurgo work has taught you much: 12,725 "
                "smithing xp awarded!")
            p.gain_xp("smithing", 12725)
            p.quests["knights_sword"] = "complete"
        else:
            say("Squire: \"Where is the sword?! Thurgo was our only hope!\"")
    elif stage == "complete":
        say("Squire: \"Sir Vyvin suspects nothing. Thank you, friend.\"")
    else:
        say("Squire: \"Thurgo's at Mudskipper Point, south of Port Sarim. "
            "Take him a redberry pie!\"")


def talk_thurgo(p):
    stage = _q(p, "knights_sword")
    if stage == "started":
        if p.has("redberry pie"):
            p.take("redberry pie")
            say("Thurgo devours the pie in two bites. \"Ahh! Fine, I'll forge "
                "your sword. Bring me 2 IRON BARS and 1 BLURITE ORE — there's "
                "a vein in the icy cavern ('cave'), if you can mine it (level "
                "10) and slip past the ice giants.\"", "bcyan")
            p.quests["knights_sword"] = "forge"
        else:
            say("Thurgo: \"Can't help you. ...Unless you happened to have a "
                "REDBERRY PIE? The general store in Lumbridge bakes them.\"")
    elif stage == "forge":
        needs = []
        if not p.has("iron bar", 2):
            needs.append("2 iron bars")
        if not p.has("blurite ore"):
            needs.append("1 blurite ore")
        if needs:
            _need_msg("Thurgo", needs)
        else:
            p.take("iron bar", 2)
            p.take("blurite ore")
            p.add("knight's sword")
            banner("Thurgo forges the blade!", color="bcyan", line_color="bcyan")
            say("Sparks fly from the Imcando forge. Thurgo hands you a perfect "
                "KNIGHT'S SWORD — take it to the squire in Falador!", "bgreen")
            p.quests["knights_sword"] = "sword"
    elif stage == "sword":
        say("Thurgo: \"Get that sword to your squire before I eat it too.\"")
    elif stage == "complete":
        say("Thurgo: \"Come by any time... especially with pie.\"")
    else:
        say("Thurgo: \"Mmm. I do love a good redberry pie.\"")


def talk_osman(p):
    stage = _q(p, "prince_ali")
    if stage == "not_started":
        banner("Quest Start: Prince Ali Rescue", color="purple",
               line_color="bmagenta")
        say("Osman: \"Prince Ali is held in DRAYNOR's jail by the bandit Lady "
            "Keli! We must smuggle him out in disguise. Bring me 3 BALLS OF "
            "WOOL for a wig, 2 CLAY for a key mould, and a BRONZE BAR to "
            "forge the key.\"")
        p.quests["prince_ali"] = "started"
    elif stage == "started":
        needs = []
        if not p.has("ball of wool", 3):
            needs.append("3 balls of wool")
        if not p.has("clay", 2):
            needs.append("2 clay")
        if not p.has("bronze bar"):
            needs.append("a bronze bar")
        if needs:
            _need_msg("Osman", needs)
        else:
            p.take("ball of wool", 3)
            p.take("clay", 2)
            p.take("bronze bar")
            p.add("blonde wig")
            p.add("bronze key")
            say("Osman works quickly: a BLONDE WIG and a forged BRONZE KEY. "
                "\"Go to the jail in Draynor ('jail') and 'search' for a way "
                "to free the prince!\"", "bgreen")
            p.quests["prince_ali"] = "rescue"
    elif stage == "rescue":
        say("Osman: \"The prince still rots in Draynor's jail — go, 'search' "
            "for his cell!\"")
    elif stage == "freed":
        _complete_banner("Prince Ali Rescue")
        say("Prince Ali embraces his family. Osman presses 700 coins into "
            "your hand — and the Al Kharid gate is forever free to you.")
        p.add("coins", 700)
        p.quests["prince_ali"] = "complete"
    else:
        say("Osman: \"Al Kharid remembers its friends. The gate is always "
            "open to you.\"")


QUEST_TALK["knights_sword"] = talk_squire
QUEST_TALK["thurgo"] = talk_thurgo
QUEST_TALK["prince_ali"] = talk_osman

# journal objective hints (quest -> stage -> what to do next)
QUEST_HINTS = {
    "cooks_assistant": {"started":
        "bring the Cook an egg, a bucket of milk and a pot of flour"},
    "sheep_shearer": {"started":
        "bring Fred 6 balls of wool ('shear' sheep, then 'spin' at Lumbridge)"},
    "dorics_quest": {"started":
        "bring Doric 6 clay, 4 copper ore and 2 iron ore"},
    "romeo_juliet": {"started":
        "'search' Draynor Village for Juliet, take her message to Romeo"},
    "vampyre_slayer": {"started":
        "slay Count Draynor in Draynor Manor (keep Morgan's stake!)"},
    "restless_ghost": {"started":
        "'search' the Varrock sewers for the skull, return to Father Aereck"},
    "rune_mysteries": {"started":
        "study the air talisman, then return it to Sedridor"},
    "imp_catcher": {"started":
        "slay imps at the Wizard's Tower for red, yellow, black & white beads"},
    "witch_potion": {"started":
        "bring Aggie raw rat meat, a bucket of milk and an egg"},
    "ernest_chicken": {"started":
        "'search' Draynor Manor for the oil can, pressure gauge & rubber tube"},
    "knights_sword": {
        "started": "find Thurgo at Mudskipper Point ('point' from Port Sarim) "
                   "— bring a redberry pie (Lumbridge general store)",
        "forge": "bring Thurgo 2 iron bars + 1 blurite ore (mine it in the "
                 "icy cavern)",
        "sword": "return the knight's sword to the squire in Falador"},
    "prince_ali": {
        "started": "bring Osman 3 balls of wool, 2 clay and a bronze bar",
        "rescue": "'search' the Draynor jail ('jail' from Draynor Village)",
        "freed": "return to Osman at the Al Kharid palace"},
    "dragon_slayer": {
        "started": "speak to Oziach in his hut west of Edgeville ('hut')",
        "maps": "search Melzar's Maze, slay goblins in Lumbridge Forest, and "
                "search Draynor Manor for the three map pieces",
        "sail": "see Klarense at Port Sarim, then 'go crandor' — bring your "
                "anti-dragon shield!"},
}


# ===========================================================================
#  BLACK KNIGHTS' FORTRESS
# ===========================================================================
# The other 12-QP quest. Sir Amik Varze of the White Knights sends you to
# infiltrate the Black Knights' fortress on Ice Mountain disguised in a
# bronze med helm + iron chainbody (Wayne's Chainmail Shop, East Falador),
# and ruin their invincibility potion with a well-placed cabbage.

# chainbodies + med helms (real OSRS-ish per-type defences, bronze -> rune)
for _mname, _req, _t in METALS:
    _v = TIER_VALUE[_t]
    add_item(f"{_mname} chainbody", 75 * _v, equip={
        "dstab": 7 + _t * 5, "dslash": 11 + _t * 7, "dcrush": 13 + _t * 8,
        "dmagic": 0, "drange": 7 + _t * 5, "slot": "body",
        "req": {"defence": _req}})
    add_item(f"{_mname} med helm", 18 * _v, equip={
        "dstab": 3 + _t * 2, "dslash": 4 + _t * 2, "dcrush": 3 + _t * 2,
        "dmagic": -1, "drange": 3 + _t * 2, "slot": "head",
        "req": {"defence": _req}})

SHOPS["chainmail"] = {"bronze chainbody": 60, "iron chainbody": 210,
                      "steel chainbody": 750, "bronze med helm": 24,
                      "iron med helm": 84, "steel med helm": 300}
ROOMS["falador_east"]["shop"] = "chainmail"
ROOMS["falador_east"]["desc"] += " Wayne's Chainmail Shop stands by the gate."

add_item("cabbage", 1, heal=2)
SHOPS["general"]["cabbage"] = 1

_add_mob("black knight",
    {"abonus": 10, "atktype": ["slash"], "att": 25, "cb": 33, "dstab": 15,
     "dslash": 17, "dcrush": 10, "dmagic": 5, "drange": 15, "def": 25,
     "hp": 42, "maxhit": 5, "str": 25, "weak": "crush"},
    [("bones", 1, 1, 1.0), ("coins", 5, 60, 0.8),
     ("black dagger", 1, 1, 0.04), ("black kiteshield", 1, 1, 0.02)],
    rank="medium")

ROOMS.update({
    "black_knights_fortress": dict(name="Black Knights' Fortress",
        desc="A grim fortress atop Ice Mountain. Black Knights drill in the "
             "yard, and somewhere below, a cauldron bubbles.",
        exits={"out": "monastery"},
        monsters=["black knight"],
        gear_lock=(["bronze med helm", "iron chainbody"],
                   "The gate guard bars your way: \"No entry to outsiders!\" "
                   "You'll need to look like one of them to get inside.")),
})
ROOMS["monastery"]["exits"]["fortress"] = "black_knights_fortress"
ROOMS["monastery"]["desc"] += (" To the north, the Black Knights' Fortress "
                               "glowers atop Ice Mountain ('fortress').")
REGIONS["black_knights_fortress"] = "Edgeville"

ALL_QUESTS["black_knights"] = "Black Knights' Fortress"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["black_knights"] = 3


def talk_amik(p):
    stage = _q(p, "black_knights")
    if stage == "not_started":
        qp = quest_points(p)
        if qp < GUILD_QP:
            say("Sir Amik Varze: \"This mission needs a proven adventurer — "
                f"return when you hold {GUILD_QP} quest points. You have "
                f"{qp}.\"", "byellow")
            return
        banner("Quest Start: Black Knights' Fortress", color="purple",
               line_color="bmagenta")
        say("Sir Amik Varze: \"The Black Knights are brewing an INVINCIBILITY "
            "POTION in their fortress on Ice Mountain, near the Edgeville "
            "monastery. Infiltrate it disguised as one of them — a BRONZE MED "
            "HELM and an IRON CHAINBODY should fool the guards (Wayne sells "
            "chainmail in East Falador). Then 'search' for their cauldron and "
            "ruin the brew. They say a CABBAGE would do horrid things to it.\"")
        p.quests["black_knights"] = "infiltrate"
    elif stage == "infiltrate":
        say("Sir Amik Varze: \"The potion still brews! Wear the bronze med "
            "helm and iron chainbody, slip into the fortress ('fortress' from "
            "the monastery), and 'search' — with a cabbage to hand.\"")
    elif stage == "sabotaged":
        _complete_banner("Black Knights' Fortress")
        say("Sir Amik Varze: \"The potion, ruined by a vegetable! Magnificent "
            "work.\" He counts out 2,500 coins.")
        p.add("coins", 2500)
        p.quests["black_knights"] = "complete"
    else:
        say("Sir Amik Varze: \"Falador sleeps easier thanks to you.\"")


QUEST_TALK["black_knights"] = talk_amik
ROOMS["white_knights_castle"]["npc"] = ["knights_sword", "black_knights"]
ROOMS["white_knights_castle"]["desc"] += (" Sir Amik Varze, captain of the "
                                          "White Knights, studies a map.")

QUEST_HINTS["black_knights"] = {
    "infiltrate": "wear a bronze med helm + iron chainbody (Wayne's, East "
                  "Falador), take a cabbage, and 'search' the fortress "
                  "('fortress' from the monastery)",
    "sabotaged": "report back to Sir Amik Varze at the White Knights' Castle",
}

# where every quest begins ('quests' shows this for unstarted ones)
QUEST_STARTS = {
    "cooks_assistant": "the Cook, Lumbridge Castle",
    "sheep_shearer": "Farmer Fred, Lumbridge Farm",
    "dorics_quest": "Doric, Falador",
    "romeo_juliet": "Romeo, Varrock Square",
    "vampyre_slayer": "Morgan, Draynor Village",
    "restless_ghost": "Father Aereck, Lumbridge Church",
    "rune_mysteries": "Sedridor, Wizard's Tower",
    "imp_catcher": "Wizard Mizgog, Wizard's Tower",
    "witch_potion": "Aggie, Draynor Village",
    "ernest_chicken": "Professor Oddenstein, Draynor Manor",
    "knights_sword": "the squire, White Knights' Castle",
    "prince_ali": "Osman, Al Kharid Palace",
    "black_knights": "Sir Amik Varze, White Knights' Castle (12 qp)",
    "priest_in_peril": "King Roald, Varrock Palace",
    "dragon_slayer": "the Guildmaster, Champions' Guild (12 qp)",
}


