# ===========================================================================
#  KANDARIN COMPLETION  (Camelot, the Waterfall, gnomes, and two guilds)
# ===========================================================================
# Camelot rises by Seers' Village; Baxtorian Falls thunders north of
# Ardougne; the Tree Gnome Stronghold and Yanille fill the west. The
# Fishing Guild (68) and Magic Guild (66) reuse the stat_lock gate, and
# sharks arrive as the endgame food.

# --- sharks: the food upgrade -------------------------------------------------
add_item("raw shark", 300, members=True)
add_item("shark", 450, heal=20, members=True)
FISH["harpoon"].append(("raw shark", 76, 110))
RAW_TO_COOKED["raw shark"] = ("shark", "burnt fish", 80)
COOK_XP["raw shark"] = 140

# --- excalibur + odds and ends ------------------------------------------------
add_item("excalibur", 20000, members=True,
         equip={"slot": "weapon", "astab": 20, "aslash": 29, "str": 25,
                "req": {"attack": 30}, "quest": "merlins_crystal"})


def _excal_guard(p, m):
    p.stat_boost["defence"] = p.stat_boost.get("defence", 0) + 8
    print("  " + paint("Excalibur flares — your guard hardens! (+8 defence "
                       "for this fight)", "bcyan"))


SPECIAL_ATTACKS["excalibur"] = {
    "name": "Sanctuary", "cost": 100, "hits": 1, "acc": 1.0, "dmg": 0.5,
    "desc": "a warding strike: +8 defence for the rest of the fight",
    "after": _excal_guard}
EFFECT_NOTES["excalibur"] = ("the Lady of the Lake's blade — its special "
                             "hardens your defence by 8 for the fight")
add_item("gnome cocktail", 30, heal=5, members=True)
add_item("glarial's amulet", 100, members=True)
SHOPS["gnome"] = {"gnome cocktail": 30, "banana": 5}
SHOPS["fishing_guild"] = {"harpoon": 5, "lobster pot": 20,
                          "small fishing net": 5}
SHOPS["magic_guild"] = {"air rune": 4, "water rune": 4, "earth rune": 4,
                        "fire rune": 4, "mind rune": 3, "chaos rune": 90,
                        "death rune": 180, "cosmic rune": 100,
                        "law rune": 240, "nature rune": 180,
                        "blood rune": 380, "mystic hat": 15000}

# --- fire giants ----------------------------------------------------------------
_add_mob("fire giant",
    {"abonus": 25, "atktype": ["slash"], "att": 70, "cb": 86, "dstab": 40,
     "dslash": 40, "dcrush": 40, "dmagic": 15, "drange": 45, "def": 65,
     "hp": 111, "maxhit": 10, "str": 80, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 30, 300, 0.8),
     ("fire rune", 10, 30, 0.6), ("blood rune", 2, 5, 0.1),
     ("grimy ranarr", 1, 1, 0.05), ("rune scimitar", 1, 1, 0.015)],
    members=True, rank="elite")

# --- the region -------------------------------------------------------------------
ROOMS.update({
    "camelot": dict(name="Camelot Castle",
        desc="White towers over blue banners. King Arthur keeps an "
             "improbable court here — and high in the tallest tower, "
             "something glitters man-shaped in a shard of crystal "
             "('search').",
        exits={"south": "seers_village"},
        npc="merlins_crystal", members=True),
    "baxtorian_falls": dict(name="Baxtorian Falls",
        desc="The river throws itself off the cliff in a standing wall of "
             "thunder. Almera's cottage clings to the bank, an old "
             "tombstone leans in the spray ('search'), and a ledge runs "
             "behind the water ('cave').",
        exits={"south": "ardougne", "cave": "waterfall_cave"},
        npc="waterfall_quest", members=True),
    "waterfall_cave": dict(name="Chambers of Baxtorian",
        desc="A drowned elven hall behind the falls. FIRE GIANTS doze "
             "against pillars that remember better kings, and an altar "
             "waits at the heart of it ('search').",
        exits={"out": "baxtorian_falls"},
        monsters=["fire giant"], hostile=True, members=True,
        qlock=("waterfall_quest", ("amulet", "complete"),
               "The wall of water hurls you back. (Quest: Waterfall Quest "
               "— Almera at the falls; Glarial's amulet opens the way)")),
    "tree_gnome_stronghold": dict(name="Tree Gnome Stronghold",
        desc="A city in the boughs of a single vast tree. Gnome gliders "
             "creak overhead, cocktail waiters weave along the walkways, "
             "and the beginners' agility course loops the roots "
             "('agility').",
        exits={"east": "ardougne"},
        shop="gnome", agility_course=(1, 10, 1), members=True),
    "fishing_guild": dict(name="Fishing Guild",
        desc="Hemenster's guild of master anglers — harpoon wharves, "
             "lobster pools, and water that practically boils with "
             "SHARKS.",
        exits={"out": "seers_village"},
        bank=True, fish_tools=["harpoon", "cage"],
        shop="fishing_guild", members=True,
        stat_lock=(["fishing"], 68,
                   "The guild master blocks the gate: 'Members catch "
                   "their own weight, friend. Fishing 68 and you're "
                   "in.'")),
    "yanille": dict(name="Yanille",
        desc="A walled frontier town at Kandarin's southern edge, all "
             "watchtowers and wizardry. The Magic Guild's spire hums "
             "behind the market ('guild').",
        exits={"north": "ardougne", "guild": "magic_guild"},
        bank=True, members=True),
    "magic_guild": dict(name="Magic Guild",
        desc="The Wizards' Guild of Yanille: floating candles, arguing "
             "portals, and a shop that sells every rune a war could "
             "want.",
        exits={"out": "yanille"},
        shop="magic_guild", members=True,
        stat_lock=(["magic"], 66,
                   "The doorman's eyes glow: 'Magic 66, or the door "
                   "stays a wall.'")),
})
ROOMS["seers_village"]["exits"]["castle"] = "camelot"
ROOMS["seers_village"]["exits"]["guild"] = "fishing_guild"
ROOMS["seers_village"]["desc"] += (" Camelot's banners fly to the "
                                   "north-east ('castle'), and the Fishing "
                                   "Guild works the water at Hemenster "
                                   "('guild').")
ROOMS["ardougne"]["exits"]["falls"] = "baxtorian_falls"
ROOMS["ardougne"]["exits"]["gnome"] = "tree_gnome_stronghold"
ROOMS["ardougne"]["exits"]["yanille"] = "yanille"
for _rm in ("camelot", "baxtorian_falls", "waterfall_cave",
            "tree_gnome_stronghold", "fishing_guild", "yanille",
            "magic_guild"):
    REGIONS[_rm] = "Kandarin"
TRAVEL_HUBS["yanille"] = "yanille"
TRAVEL_NAMES.append("Yanille")
TRAVEL_HUBS["gnome stronghold"] = "tree_gnome_stronghold"
TRAVEL_NAMES.append("Gnome Stronghold")

# --- Waterfall Quest (1 QP) -----------------------------------------------------
ALL_QUESTS["waterfall_quest"] = "Waterfall Quest"
QUEST_POINTS["waterfall_quest"] = 1
NPC_NAMES["waterfall_quest"] = "Almera"
QUEST_STARTS["waterfall_quest"] = "Almera, Baxtorian Falls (north of " \
                                  "Ardougne)"
QUEST_HINTS["waterfall_quest"] = {
    "started": "search the tombstone by the falls for Glarial's amulet",
    "amulet": "enter the cave behind the falls and 'search' the altar",
}


def talk_almera(p):
    stage = _q(p, "waterfall_quest")
    if stage == "not_started":
        banner("Quest Start: Waterfall Quest", color="purple",
               line_color="bmagenta")
        say("Almera: \"My boy Hudon's obsessed with the treasure of "
            "BAXTORIAN, the elf-king drowned under these falls. They say "
            "only Glarial's amulet opens his halls — her grave lies "
            "somewhere by the water. Mind the currents, dear.\"")
        p.quests["waterfall_quest"] = "started"
    elif stage == "started":
        say("Almera: \"Glarial's grave is close — 'search' by the "
            "falls.\"")
    elif stage == "amulet":
        say("Almera: \"The amulet! Then the way behind the water is open "
            "('cave'). Mind the giants, dear.\"")
    else:
        say("Almera: \"Hudon still hasn't done the dishes, treasure or "
            "no.\"")


QUEST_TALK["waterfall_quest"] = talk_almera

# --- Merlin's Crystal (6 QP) -----------------------------------------------------
ALL_QUESTS["merlins_crystal"] = "Merlin's Crystal"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["merlins_crystal"] = 6
NPC_NAMES["merlins_crystal"] = "King Arthur"
NPC_NAMES["lady_lake"] = "The Lady of the Lake"
QUEST_STARTS["merlins_crystal"] = "King Arthur, Camelot (by Seers' Village)"
QUEST_HINTS["merlins_crystal"] = {
    "excalibur": "seek the Lady of the Lake in Catherby — bring bread",
    "shatter": "strike the crystal atop Camelot ('search') with Excalibur",
}


def talk_arthur(p):
    stage = _q(p, "merlins_crystal")
    if stage == "not_started":
        banner("Quest Start: Merlin's Crystal", color="purple",
               line_color="bmagenta")
        say("King Arthur: \"My wizard MERLIN out-clevered himself and is "
            "sealed in his own crystal atop the tower. Steel won't scratch "
            "it — only EXCALIBUR. The Lady of the Lake keeps it; she "
            "waits at Catherby. A warning: she tests strangers.\"")
        p.quests["merlins_crystal"] = "excalibur"
    elif stage == "excalibur":
        say("King Arthur: \"The Lady of the Lake, at Catherby. Take her "
            "test — and take bread, is my advice.\"")
    elif stage == "shatter":
        say("King Arthur: \"You bear Excalibur! The tower stair is yours "
            "— 'search' and set my wizard free.\"")
    elif stage == "complete":
        say("Merlin (mid-argument with Arthur): \"— and I MEANT to be in "
            "the crystal. Ah, my rescuer! Camelot thanks you.\"")


def talk_lady(p):
    stage = _q(p, "merlins_crystal")
    if stage == "excalibur":
        if p.has("bread"):
            p.take("bread")
            p.add("excalibur")
            p.quests["merlins_crystal"] = "shatter"
            say("A beggar woman asks you for bread. You hand it over — and "
                "she stands transformed, robed in lake-light. \"Kindness "
                "before strength. The sword is yours.\" She lays EXCALIBUR "
                "in your hands.", "bcyan", "bold")
        else:
            say("A beggar woman by the shore asks: \"Spare a loaf of "
                "bread, traveller?\" (You have none. The general store "
                "sells bread.)")
    elif stage == "shatter":
        say("The Lady of the Lake: \"The sword knows its work. To "
            "Camelot.\"")
    else:
        say("A woman watches the water at the shore's edge. Lake-light "
            "clings to her.")


QUEST_TALK["merlins_crystal"] = talk_arthur
QUEST_TALK["lady_lake"] = talk_lady
ROOMS["camelot"]["npc"] = "merlins_crystal"
ROOMS["catherby"]["npc"] = "lady_lake"
ROOMS["catherby"]["desc"] += (" A woman stands at the water's edge, "
                              "watching the lake.")


# ===========================================================================
#  KARAMJA COMPLETION  (the deep jungle, dragon dungeon, and THE INFERNO)
# ===========================================================================
# South of Brimhaven the jungle swallows the road: Tai Bwo Wannai's
# tribesmen poison their spears, Shilo Village mines nothing but gems, and
# Saniboch charges admission to a dungeon full of dragons. Inside the
# volcano, the TzHaar city Mor Ul Rek trades in tokkul — and beneath it
# the INFERNO burns: eight waves, then TzKal-Zuk, then the infernal cape.

# --- red dragonhide line (ranged tier above green) ---------------------------
add_item("red dragonhide", 160, members=True)
add_item("red dragon leather", 200, members=True)
add_item("red d'hide body", 15000, members=True,
         equip={"amagic": -15, "arange": 20, "dstab": 24, "dslash": 33,
                "dcrush": 30, "dmagic": 26, "drange": 41, "slot": "body",
                "req": {"ranged": 60, "defence": 40}})
add_item("red d'hide chaps", 7000, members=True,
         equip={"amagic": -8, "arange": 10, "dstab": 12, "dslash": 15,
                "dcrush": 14, "dmagic": 12, "drange": 20, "slot": "legs",
                "req": {"ranged": 60}})
add_item("red d'hide vambraces", 3500, members=True,
         equip={"amagic": -6, "arange": 9, "dstab": 3, "dslash": 3,
                "dcrush": 3, "slot": "gloves", "req": {"ranged": 60}})
TAN_HIDES["red dragonhide"] = ("red dragon leather", 40)
CRAFT_RECIPES.update({
    "red d'hide vambraces": ("red dragon leather", 1, 73, 156),
    "red d'hide chaps": ("red dragon leather", 2, 75, 312),
    "red d'hide body": ("red dragon leather", 3, 77, 468),
})

# --- obsidian gear (tokkul-priced in Mor Ul Rek) ------------------------------
add_item("obsidian cape", 25000, members=True,
         equip={"dstab": 9, "dslash": 9, "dcrush": 9, "dmagic": 9,
                "drange": 9, "slot": "cape"})
add_item("toktz-xil-ak", 40000, members=True,
         equip={"slot": "weapon", "astab": 47, "aslash": 40, "str": 49,
                "req": {"attack": 60}})
add_item("toktz-ket-xil", 35000, members=True,
         equip={"slot": "shield", "dstab": 40, "dslash": 42, "dcrush": 38,
                "drange": 42, "str": 5, "req": {"defence": 60}})
add_item("infernal cape", 200000, members=True,
         equip={"astab": 4, "aslash": 4, "acrush": 4, "amagic": 4,
                "arange": 4, "dstab": 12, "dslash": 12, "dcrush": 12,
                "dmagic": 12, "drange": 12, "str": 6, "prayer": 2,
                "slot": "cape"})
EFFECT_NOTES["infernal cape"] = ("the greatest cape in Gielinor, quenched "
                                 "in TzKal-Zuk's own fire")
TOKKUL_SHOP = {"obsidian cape": 9000, "toktz-ket-xil": 12000,
               "toktz-xil-ak": 15000}


def cmd_redeem(p, arg):
    if p.location != "mor_ul_rek":
        say("Only the TzHaar of Mor Ul Rek trade in tokkul.", "grey")
        return
    want = arg.strip().lower()
    if not want:
        say("The TzHaar armoury (pay in tokkul — 'redeem <item>'):",
            "orange", "bold")
        for it, cost in TOKKUL_SHOP.items():
            say(f"  {it:<16} {cost:,} tokkul", "grey")
        say(f"  (You carry {p.count('tokkul'):,} tokkul.)", "grey")
        return
    match = next((it for it in TOKKUL_SHOP if want in it), None)
    if not match:
        say("The TzHaar shrugs: no such ware. ('redeem' lists the "
            "armoury.)")
        return
    cost = TOKKUL_SHOP[match]
    if p.count("tokkul") < cost:
        say(f"TzHaar-Hur: \"{cost:,} tokkul. You carry "
            f"{p.count('tokkul'):,}. Go fight, JalYt.\"", "byellow")
        return
    p.take("tokkul", cost)
    p.add(match)
    say(f"You trade {cost:,} tokkul for the {match.upper()}.", "bgreen",
        "bold")
    return True


HANDLERS["redeem"] = cmd_redeem
HANDLERS["exchange"] = cmd_redeem

# --- jungle creatures + dragons -----------------------------------------------
def _tribes_poison(p, m, dmg):
    if dmg > 0 and not getattr(p, "poison", 0) and random.random() < 0.4:
        p.poison = 2
        print("  " + paint("The spear's coating burns — you are POISONED!",
                           "green"))


_add_mob("tribesman",
    {"abonus": 10, "atktype": ["stab"], "att": 30, "cb": 32, "dstab": 15,
     "dslash": 15, "dcrush": 15, "dmagic": 5, "drange": 15, "def": 25,
     "hp": 32, "maxhit": 4, "str": 30, "weak": "slash"},
    [("bones", 1, 1, 1.0), ("coins", 5, 60, 0.6),
     ("grimy harralander", 1, 1, 0.15)],
    members=True, rank="medium")
MONSTER_EFFECTS["tribesman"] = _tribes_poison

_DRAGON_KIN = {
    "red dragon": (
        {"abonus": 30, "atktype": ["slash"], "att": 90, "cb": 152,
         "dstab": 50, "dslash": 50, "dcrush": 50, "dmagic": 60,
         "drange": 55, "def": 90, "hp": 140, "maxhit": 13, "str": 95,
         "weak": "stab"},
        [("dragon bones", 1, 1, 1.0), ("red dragonhide", 2, 3, 1.0),
         ("coins", 100, 500, 0.8), ("fire rune", 10, 30, 0.4)]),
    "bronze dragon": (
        {"abonus": 35, "atktype": ["slash"], "att": 100, "cb": 131,
         "dstab": 70, "dslash": 70, "dcrush": 60, "dmagic": 30,
         "drange": 80, "def": 100, "hp": 122, "maxhit": 13, "str": 100,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("bronze bar", 2, 4, 1.0),
         ("coins", 200, 800, 0.8), ("adamantite ore", 1, 2, 0.2)]),
    "iron dragon": (
        {"abonus": 40, "atktype": ["slash"], "att": 120, "cb": 189,
         "dstab": 85, "dslash": 85, "dcrush": 70, "dmagic": 35,
         "drange": 95, "def": 110, "hp": 165, "maxhit": 15, "str": 120,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("iron bar", 3, 5, 1.0),
         ("coins", 300, 1200, 0.9), ("dragon med helm", 1, 1, 0.015)]),
    "steel dragon": (
        {"abonus": 45, "atktype": ["slash"], "att": 140, "cb": 246,
         "dstab": 100, "dslash": 100, "dcrush": 80, "dmagic": 40,
         "drange": 110, "def": 120, "hp": 190, "maxhit": 17, "str": 140,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("steel bar", 3, 6, 1.0),
         ("coins", 500, 2000, 1.0), ("dragon platelegs", 1, 1, 0.012),
         ("dragon dagger", 1, 1, 0.02)]),
}
for _dk, (_st, _drops) in _DRAGON_KIN.items():
    _add_mob(_dk, _st, _drops, members=True, rank="elite")
    MONSTERS[_dk]["dragonfire"] = True
DURADEL_TARGETS.extend(["fire giant", "steel dragon"])

# --- the Inferno roster ---------------------------------------------------------
_INFERNO_MOBS = {
    "jal-nib": ({"abonus": 5, "atktype": ["crush"], "att": 15, "cb": 32,
                 "dstab": 5, "dslash": 5, "dcrush": 5, "dmagic": 5,
                 "drange": 5, "def": 10, "hp": 10, "maxhit": 2, "str": 15,
                 "weak": "crush"},
                [("tokkul", 10, 30, 1.0)], "easy"),
    "jal-mejrah": ({"abonus": 20, "atktype": ["ranged"], "att": 60,
                    "cb": 85, "dstab": 30, "dslash": 30, "dcrush": 30,
                    "dmagic": 30, "drange": 30, "def": 55, "hp": 40,
                    "maxhit": 7, "str": 60, "weak": "crush"},
                   [("tokkul", 20, 60, 1.0)], "hard"),
    "jal-ak": ({"abonus": 30, "atktype": ["magic", "ranged"], "att": 90,
                "cb": 165, "dstab": 45, "dslash": 45, "dcrush": 45,
                "dmagic": 45, "drange": 45, "def": 70, "hp": 70,
                "maxhit": 10, "str": 90, "weak": "crush"},
               [("tokkul", 40, 100, 1.0)], "elite"),
    "jal-imkot": ({"abonus": 40, "atktype": ["crush"], "att": 120,
                   "cb": 240, "dstab": 60, "dslash": 60, "dcrush": 60,
                   "dmagic": 50, "drange": 60, "def": 85, "hp": 100,
                   "maxhit": 14, "str": 130, "weak": "slash"},
                  [("tokkul", 60, 140, 1.0)], "elite"),
    "jal-xil": ({"abonus": 45, "atktype": ["ranged"], "att": 140,
                 "cb": 370, "dstab": 65, "dslash": 65, "dcrush": 65,
                 "dmagic": 55, "drange": 70, "def": 90, "hp": 125,
                 "maxhit": 16, "str": 140, "weak": "crush"},
                [("tokkul", 80, 180, 1.0)], "elite"),
    "jal-zek": ({"abonus": 50, "atktype": ["magic"], "att": 160,
                 "cb": 490, "dstab": 70, "dslash": 70, "dcrush": 70,
                 "dmagic": 70, "drange": 75, "def": 95, "hp": 150,
                 "maxhit": 18, "str": 160, "weak": "crush"},
                [("tokkul", 100, 220, 1.0)], "elite"),
}
for _im, (_st, _drops, _rank) in _INFERNO_MOBS.items():
    _add_mob(_im, _st, _drops, members=True, rank=_rank)
MONSTER_EFFECTS["jal-mejrah"] = MONSTER_EFFECTS["tz-kih"]   # prayer-eater

_add_mob("jaltok-jad",
    {"abonus": 60, "atktype": ["magic", "ranged", "crush"], "att": 200,
     "cb": 900, "dstab": 65, "dslash": 65, "dcrush": 65, "dmagic": 65,
     "drange": 65, "def": 100, "hp": 250, "maxhit": 30, "str": 200,
     "weak": "crush"},
    [("tokkul", 300, 800, 1.0)], members=True)
MONSTERS["jaltok-jad"]["boss"] = True
MONSTERS["jaltok-jad"]["rank"] = "boss"
_BOSSES.add("jaltok-jad")
BOSS_TURN["jaltok-jad"] = _jad_take_turn      # telegraphs like his little kin
BOSS_INTRO["jaltok-jad"] = BOSS_INTRO.get("tztok-jad")
BOSS_DEATH["jaltok-jad"] = BOSS_DEATH.get("tztok-jad")

ZUK_ART = r"""
       \\  |  //        \\  |  //
    ====[#######]====[#######]====
      .-'  ___________________ '-.
     /    /  \   _______   /  \   \
    |    | () |  \     /  | () |   |
     \    \__/    \   /    \__/   /
      '-.          \ /         .-'
         '========= V ========='
"""


def _zuk_intro(name):
    return [_tint(ZUK_ART, "grey"), _tint(ZUK_ART, "orange", "bold"),
            _tint(ZUK_ART, "bred", "bold")]


def _zuk_death(name):
    return [_tint(ZUK_ART, "bred"), _tint(ZUK_ART, "grey", "dim")]


def _zuk_take_turn(p, m):
    """Zuk's barrage burns through prayer; every third turn the obsidian
    shield glides between you and the fire."""
    cyc = m.get("zuk_cycle", 0)
    m["zuk_cycle"] = cyc + 1
    if cyc % 3 == 2:
        say("The obsidian shield glides across — you shelter in its "
            "shadow. TzKal-Zuk's fire breaks around you!", "bcyan")
    else:
        style = "magic" if cyc % 2 else "ranged"
        say(f"TzKal-Zuk hurls a wall of burning {style}!", "bred", "bold")
        dmg = random.randint(10, m["max_hit"])
        if p.prayer_protects(style):
            dmg = int(dmg * 0.85)
            print("  " + paint("Zuk's fury burns THROUGH your prayer — it "
                               "barely softens the blow.", "bmagenta"))
        p.hp -= dmg
        print("  " + paint(f"The fire takes {dmg} from you.", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer "
                               "points).", "bmagenta"))
    return "died" if p.hp <= 0 else None


_add_mob("tzkal-zuk",
    {"abonus": 70, "atktype": ["ranged", "magic"], "att": 260, "cb": 1400,
     "dstab": 250, "dslash": 250, "dcrush": 250, "dmagic": 60,
     "drange": 80, "def": 100, "hp": 300, "maxhit": 26, "str": 260,
     "weak": "ranged"},
    [("tokkul", 1000, 3000, 1.0), ("uncut diamond", 1, 3, 0.5)],
    members=True)
MONSTERS["tzkal-zuk"]["boss"] = True
MONSTERS["tzkal-zuk"]["rank"] = "boss"
_BOSSES.add("tzkal-zuk")
BOSS_TURN["tzkal-zuk"] = _zuk_take_turn
BOSS_INTRO["tzkal-zuk"] = _zuk_intro
BOSS_DEATH["tzkal-zuk"] = _zuk_death
MONSTER_ART["tzkal-zuk"] = ZUK_ART

# --- the Inferno machinery -------------------------------------------------------
INFERNO_WAVES = ["jal-nib", "jal-mejrah", "jal-ak", "jal-imkot", "jal-xil",
                 "jal-zek", "jaltok-jad", "tzkal-zuk"]


def _inferno_start_wave(p):
    mon = INFERNO_WAVES[p.inferno_wave - 1]
    say(f"— Inferno wave {p.inferno_wave} of {len(INFERNO_WAVES)} —",
        "bred", "bold")
    _start_combat(p, mon)


def _inferno_challenge(p):
    if getattr(p, "inferno_wave", 0):
        say(f"You're mid-run — wave {p.inferno_wave}/{len(INFERNO_WAVES)}. "
            "Type 'next' to continue.", "byellow")
        return
    banner("THE INFERNO", color="bred", line_color="red")
    say("TzHaar-Ket-Keh: \"The Fight Caves was the door, JalYt. This is "
        "the furnace. Eight waves. ZUK waits at the bottom.\"",
        "orange", "bold")
    p.inferno_wave = 1
    _inferno_start_wave(p)


def _inferno_on_kill(p, target):
    """Advance the Inferno after each wave kill; forge the champion."""
    wave = getattr(p, "inferno_wave", 0)
    if not wave or not ROOMS[p.location].get("inferno") \
            or target != INFERNO_WAVES[wave - 1]:
        return
    if wave < len(INFERNO_WAVES):
        p.inferno_wave += 1
        nxt = INFERNO_WAVES[p.inferno_wave - 1]
        say(f"Wave {wave} survived! Breathe, eat, rethink — then 'next' "
            f"(wave {p.inferno_wave}/{len(INFERNO_WAVES)}: {nxt}).",
            "byellow", "bold")
    else:
        p.inferno_wave = 0
        show_art(ART_QUEST, "gold", center=True)
        banner("THE INFERNO — EXTINGUISHED", color="bred", line_color="red")
        p.add("infernal cape")
        say("TzHaar-Ket-Keh stares into the cooling dark: \"...Zuk is "
            "beaten. Take the cape, JalYt. It is quenched in his fire.\"",
            "orange", "bold")
        say("You receive the INFERNAL CAPE! ('equip infernal cape')",
            "bgreen", "bold")


# --- the region --------------------------------------------------------------------
ROOMS.update({
    "tai_bwo_wannai": dict(name="Tai Bwo Wannai",
        desc="A machete-hacked clearing where the Wannai tribe drums "
             "against the jungle dark. The spears here weep green at the "
             "tip — mind the TRIBESMEN. Shilo's gem road runs south.",
        exits={"north": "brimhaven", "south": "shilo_village"},
        monsters=["tribesman"], shop="tai_bwo", hostile=True,
        members=True),
    "shilo_village": dict(name="Shilo Village",
        desc="A stockaded mining town on the Shilo river. The famous GEM "
             "MINE glitters even in torchlight ('mine gem rock'), and "
             "fly-fishers work the rapids.",
        exits={"north": "tai_bwo_wannai"},
        bank=True, rocks=["gem rock"], fish_tools=["fly", "rod"],
        members=True),
    "brimhaven_dungeon": dict(name="Brimhaven Dungeon",
        desc="Saniboch's damp stairwell opens into a cavern of red "
             "scales and old gold. RED DRAGONS nest here, and an iron "
             "door glows at the deep end ('deeper').",
        exits={"out": "brimhaven", "deeper": "dragon_forge"},
        monsters=["red dragon", "moss giant"], hostile=True, members=True,
        fee=(875, "Saniboch grins: 'The dungeon eats adventurers, "
                  "friend. 875 coins to feed it you.'")),
    "dragon_forge": dict(name="The Dragon Forge",
        desc="A vault of ancient dwarven fire where METAL DRAGONS pace "
             "on iron claws — bronze, iron, steel. Bring an anti-dragon "
             "shield or bring a will.",
        exits={"back": "brimhaven_dungeon"},
        monsters=["bronze dragon", "iron dragon", "steel dragon"],
        hostile=True, members=True),
    "mor_ul_rek": dict(name="Mor Ul Rek",
        desc="The obsidian city of the TzHaar, lit by lava-light. "
             "TzHaar-Hur traders take TOKKUL for obsidian ('redeem'), "
             "and a sealed crack in the floor breathes white heat "
             "('inferno').",
        exits={"out": "karamja_volcano", "inferno": "the_inferno"},
        members=True),
    "the_inferno": dict(name="The Inferno",
        desc="The bottom of the world. Everything here is fire that "
             "learned to want things. ('challenge' — eight waves, then "
             "ZUK)",
        exits={"out": "mor_ul_rek"},
        inferno=True, members=True,
        gear_lock=(["fire cape|infernal cape"],
                   "TzHaar-Ket-Keh bars the crack: 'The furnace is for "
                   "PROVEN JalYt. Wear your fire cape.'")),
})
SHOPS["tai_bwo"] = {"antipoison": 120, "machete": 40, "banana": 3}
add_item("machete", 40, members=True,
         equip={"slot": "weapon", "aslash": 7, "str": 6})
ROOMS["brimhaven"]["exits"]["south"] = "tai_bwo_wannai"
ROOMS["brimhaven"]["exits"]["dungeon"] = "brimhaven_dungeon"
ROOMS["brimhaven"]["desc"] += (" A jungle track vanishes south toward "
                               "Tai Bwo Wannai, and Saniboch loiters by "
                               "a dungeon mouth ('dungeon').")
ROOMS["karamja_volcano"]["exits"]["city"] = "mor_ul_rek"
ROOMS["karamja_volcano"]["desc"] += (" Deeper in the rock, lava-light "
                                     "marks the TzHaar city of Mor Ul Rek "
                                     "('city').")
ROCKS["gem rock"] = ("uncut sapphire", 40, 65)
for _rm in ("tai_bwo_wannai", "shilo_village", "brimhaven_dungeon",
            "dragon_forge", "mor_ul_rek", "the_inferno"):
    REGIONS[_rm] = "Karamja"
TRAVEL_HUBS["shilo"] = "shilo_village"
TRAVEL_NAMES.append("Shilo")


