# ===========================================================================
#  THE FIGHT CAVES  (wave minigame -> TzTok-Jad -> fire cape)
# ===========================================================================
# 'challenge' in the Fight Caves starts a run: seven waves of TzHaar-kin,
# 'next' between waves (heal up first!), leaving or dying abandons the run.
# Each TzHaar has its OSRS signature: Tz-Kih drains prayer, Tz-Kek's spikes
# recoil, Tok-Xil shoots, Yt-MejKot heals itself, Ket-Zek blasts magic. The
# final wave is TzTok-Jad, who telegraphs every attack — switch to the right
# protection prayer or be flattened. Reward: the fire cape (and tokkul).

add_item("tokkul", 1)     # the obsidian currency of the TzHaar

_add_mob("tz-kih",
    {"abonus": 0, "atktype": ["crush"], "att": 32, "cb": 22, "dstab": 0,
     "dslash": 0, "dcrush": 0, "dmagic": 0, "drange": 0, "def": 12,
     "hp": 10, "maxhit": 4, "str": 30, "weak": "crush"},
    [("tokkul", 3, 9, 1.0)], members=True, rank="easy")

_add_mob("tz-kek",
    {"abonus": 0, "atktype": ["crush"], "att": 40, "cb": 45, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 5, "drange": 5, "def": 28,
     "hp": 20, "maxhit": 7, "str": 40, "weak": "slash"},
    [("tokkul", 6, 15, 1.0)], members=True, rank="medium")
MONSTERS["tz-kek"]["recoil"] = 1        # spiked hide: melee hits bite back

_add_mob("tok-xil",
    {"abonus": 20, "atktype": ["ranged"], "att": 65, "cb": 90, "dstab": 20,
     "dslash": 20, "dcrush": 20, "dmagic": 10, "drange": 25, "def": 45,
     "hp": 40, "maxhit": 13, "str": 60, "weak": "stab"},
    [("tokkul", 15, 40, 1.0)], members=True, rank="hard")

_add_mob("yt-mejkot",
    {"abonus": 10, "atktype": ["slash"], "att": 90, "cb": 180, "dstab": 40,
     "dslash": 45, "dcrush": 40, "dmagic": 30, "drange": 40, "def": 65,
     "hp": 80, "maxhit": 20, "str": 95, "weak": "stab"},
    [("tokkul", 30, 90, 1.0)], members=True, rank="elite")

_add_mob("ket-zek",
    {"abonus": 40, "atktype": ["magic"], "att": 130, "cb": 360, "dstab": 45,
     "dslash": 60, "dcrush": 60, "dmagic": 70, "drange": 60, "def": 80,
     "hp": 160, "maxhit": 22, "str": 120, "weak": "stab"},
    [("tokkul", 90, 270, 1.0)], members=True, rank="elite")

MONSTER_ART["tz-kih"] = r'''
      /\  ~  /\
     ( o \_/ o )
      \|/ ' \|/
'''
MONSTER_ART["tz-kek"] = r'''
      /\/\/\/\/\
     <  o    o  >
     <    __    >
      \/\/\/\/\/
'''
MONSTER_ART["tok-xil"] = r'''
       |\   /|
      ( >o.o< )    }---->
       /|| ||\
'''
MONSTER_ART["yt-mejkot"] = r'''
       _/=====\_
      (  o _ o  )
      /|   W   |\
      \|_______|/
        |     |
'''
MONSTER_ART["ket-zek"] = r'''
      \ /       \ /
     --#---------#--
      ( ((o) (o)) )
       \   ___   /
       /|_______|\
      /_/       \_\
'''


def _kih_drain(p, m, dmg):
    if p.prayer_points > 0:
        drain = dmg + 2
        p.prayer_points = max(0, p.prayer_points - drain)
        print("  " + paint(f"The Tz-Kih latches on and drains {drain} prayer "
                           f"points!", "bmagenta"))


def _mejkot_heal(p, m, dmg):
    if m["cur"] < m["hp"]:
        heal = random.randint(3, 8)
        m["cur"] = min(m["hp"], m["cur"] + heal)
        print("  " + paint(f"The Yt-MejKot knits its obsidian flesh back "
                           f"together. (+{heal})", "lime"))


MONSTER_EFFECTS["tz-kih"] = _kih_drain
MONSTER_EFFECTS["yt-mejkot"] = _mejkot_heal

CAVE_WAVES = ["tz-kih", "tz-kek", "tok-xil", "yt-mejkot", "ket-zek",
              "ket-zek", "tztok-jad"]

add_item("fire cape", 50000, members=True, equip={
    "astab": 1, "aslash": 1, "acrush": 1, "amagic": 1, "arange": 1,
    "dstab": 11, "dslash": 11, "dcrush": 11, "dmagic": 11, "drange": 11,
    "str": 4, "prayer": 2, "slot": "cape"})

JAD_ART = r'''
        \ /             \ /
      ---#---------------#---
        /_\ ___________ /_\
       /   (  (o)  (o)  )   \
      |     \____ _____/     |
       \     /VVVVVVVVV\    /
        \___|           |__/
        /   \___________/   \
       /_/|  |    |    |  |\_\
          |__|    |____|__|
'''


def _jad_intro(name):
    return [_tint(JAD_ART, "brown"), _tint(JAD_ART, "orange", "bold"),
            _tint(JAD_ART, "bred", "bold"), _tint(JAD_ART, "orange", "bold")]


def _jad_death(name):
    return [_tint(JAD_ART, "orange"), _tint(JAD_ART, "grey"),
            _tint(JAD_ART, "grey", "dim")]


_add_mob("tztok-jad",
    {"abonus": 0, "atktype": ["crush", "magic", "ranged"], "att": 160,
     "cb": 702, "dstab": 0, "dslash": 0, "dcrush": 0, "dmagic": 0,
     "drange": 0, "def": 100, "hp": 250, "maxhit": 25, "str": 160,
     "weak": "ranged"},
    [("coins", 5000, 20000, 1.0), ("tokkul", 1000, 3000, 1.0)], members=True)
MONSTERS["tztok-jad"]["boss"] = True
MONSTERS["tztok-jad"]["rank"] = "boss"
_BOSSES.add("tztok-jad")
BOSS_INTRO["tztok-jad"] = _jad_intro
BOSS_DEATH["tztok-jad"] = _jad_death
MONSTER_ART["tztok-jad"] = JAD_ART

JAD_CUES = {
    "magic": "TzTok-Jad rears back, flame gathering between his horns — "
             "MAGIC is coming! (pray 'protect from magic')",
    "ranged": "TzTok-Jad slams his forelegs into the rock — a boulder "
              "barrage is coming! (pray 'protect from missiles')",
    "melee": "TzTok-Jad crouches low, jaws gaping wide — a MELEE bite is "
             "coming! (pray 'protect from melee')",
}


def _jad_take_turn(p, m):
    """Jad telegraphs each attack a turn ahead: pray right or be flattened."""
    style = m.get("jad_next")
    if style:
        animate([_tint(JAD_ART, "orange", "bold"), _tint(JAD_ART, "bred", "bold")],
                delay=0.12, center=True)
        say(f"{m['name'].title()} unleashes his {style} attack!",
            "orange", "bold")
        if p.prayer_protects(style):
            print("  " + paint("Your prayer holds — the attack breaks "
                               "harmlessly over you!", "bcyan"))
        else:
            dmg = random.randint(8, m["max_hit"])
            p.hp -= dmg
            print("  " + paint(f"It smashes into you for a devastating {dmg}!",
                               "bred") + "  " + paint("HP ", "white")
                  + bar_meter(max(p.hp, 0), p.max_hp, 18))
    else:
        say(f"{m['name'].title()} sizes you up, embers dripping from his "
            "jaws...", "orange")
    nxt = random.choice(["magic", "ranged", "melee"])
    m["jad_next"] = nxt
    print("  " + paint(JAD_CUES[nxt], "byellow"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


BOSS_TURN["tztok-jad"] = _jad_take_turn

ROOMS.update({
    "fight_caves": dict(name="The Fight Caves",
        desc="A scorched arena deep in the volcano. TzHaar-Mej-Jal guards "
             "the entrance, sizing up challengers. Seven waves await the "
             "brave — and TzTok-Jad awaits the foolish. (members)",
        exits={"out": "karamja_volcano"},
        npc="tzhaar", fight_caves=True, members=True),
})
ROOMS["karamja_volcano"]["exits"]["caves"] = "fight_caves"
ROOMS["karamja_volcano"]["desc"] += " A heat-shimmering tunnel leads to the Fight Caves ('caves')."
REGIONS["fight_caves"] = "Karamja"
NPC_NAMES["tzhaar"] = "TzHaar-Mej-Jal"


def talk_tzhaar(p):
    wave = getattr(p, "cave_wave", 0)
    if wave:
        say(f"TzHaar-Mej-Jal: \"You fight good so far, JalYt — wave {wave} of "
            f"{len(CAVE_WAVES)}. Type 'next' when ready. Leave, and you start "
            "over.\"", "orange")
        return
    if p.has("fire cape") or "tztok-jad" in getattr(p, "bosses", []):
        say("TzHaar-Mej-Jal: \"The JalYt who slew TzTok-Jad! You fight again "
            "any time — 'challenge'.\"", "orange")
        return
    say("TzHaar-Mej-Jal: \"You want good fight, JalYt? Seven waves of my "
        "kin, no mercy, no leaving. TZ-KIH drinks your prayers. TZ-KEK's "
        "spikes bite back. TOK-XIL shoots true. YT-MEJKOT mends its own "
        "flesh. KET-ZEK burns with sorcery — twice. Survive them all and "
        "face TZTOK-JAD: watch his moves and pray right, or die fast. Beat "
        "him and the FIRE CAPE is yours. Bring food, prayer potions, your "
        "best gear. Type 'challenge' to begin.\"", "orange")


QUEST_TALK["tzhaar"] = talk_tzhaar


def _cave_start_wave(p):
    mon = CAVE_WAVES[p.cave_wave - 1]
    say(f"— Wave {p.cave_wave} of {len(CAVE_WAVES)} —", "byellow", "bold")
    _start_combat(p, mon)


def cmd_challenge(p, _a):
    if ROOMS[p.location].get("inferno"):
        return _inferno_challenge(p)
    if p.location != "fight_caves":
        say("There's nothing to challenge here.", "grey")
        return
    if getattr(p, "cave_wave", 0):
        say(f"You're mid-run — wave {p.cave_wave}/{len(CAVE_WAVES)}. "
            "Type 'next' to continue.", "byellow")
        return
    banner("THE FIGHT CAVES", color="orange", line_color="red")
    say("TzHaar-Mej-Jal: \"Seven waves. No mercy. Fight good, JalYt!\"",
        "orange", "bold")
    p.cave_wave = 1
    _cave_start_wave(p)


def cmd_next(p, _a):
    if ROOMS[p.location].get("inferno") and getattr(p, "inferno_wave", 0):
        return _inferno_start_wave(p)
    if p.location != "fight_caves" or not getattr(p, "cave_wave", 0):
        say("Nothing to continue. (In the Fight Caves, 'challenge' starts "
            "a run.)", "grey")
        return
    _cave_start_wave(p)


HANDLERS["challenge"] = cmd_challenge
HANDLERS["next"] = cmd_next
HANDLERS["wave"] = cmd_next


# ===========================================================================
#  SKILLING EXPANSION  (gems & jewellery, runecrafting altars, yew/magic
#  trees + high fletching, skill capes)
# ===========================================================================

# --- Gem cutting (mining rocks can strike gems; cut them with a chisel) -----
# uncut gem -> (cut gem, crafting level, xp). Order matters: mining strike
# weights (8/5/2/1) follow this order, common -> rare.
GEM_CUT = {
    "uncut sapphire": ("sapphire", 20, 50),
    "uncut emerald": ("emerald", 27, 67),
    "uncut ruby": ("ruby", 34, 85),
    "uncut diamond": ("diamond", 43, 107),
}


def _gem_uncut(name):
    if name in GEM_CUT:
        return name
    if "uncut " + name in GEM_CUT:
        return "uncut " + name
    return None


def cmd_cutgem(p, arg):
    name = arg.strip().lower()
    uncut = _gem_uncut(name) if name else \
        next((g for g in GEM_CUT if p.has(g)), None)
    if not uncut:
        say("Cut what? You have no uncut gems. (Mining sometimes strikes "
            "them.)", "grey")
        return
    if not p.has(uncut):
        say(f"You have no {uncut}.")
        return
    if not p.find_tool("chisel"):
        say("You need a chisel (general or crafting shop).")
        return
    cut, lvl, xp = GEM_CUT[uncut]
    if p.lvl("crafting") < lvl:
        say(f"You need crafting level {lvl} to cut a {uncut}.")
        return
    p.take(uncut)
    p.add(cut)
    say(f"You carefully chisel the {uncut} into a sparkling {cut}.", "bcyan")
    p.gain_xp("crafting", xp)
    return True


# --- Jewellery (furnace + gold bar [+ gem] -> rings and amulets) ------------
# product -> (gem or None, crafting level, xp)
JEWELLERY = {
    "gold ring": (None, 5, 15),
    "sapphire ring": ("sapphire", 20, 40),
    "emerald ring": ("emerald", 27, 55),
    "ruby ring": ("ruby", 34, 70),
    "diamond ring": ("diamond", 43, 85),
    "gold amulet": (None, 8, 30),
    "sapphire amulet": ("sapphire", 24, 65),
    "emerald amulet": ("emerald", 31, 70),
    "ruby amulet": ("ruby", 50, 85),
    "diamond amulet": ("diamond", 70, 100),
}

add_item("gold ring", 315, equip={"slot": "ring"})
add_item("sapphire ring", 900, equip={"slot": "ring"})
add_item("emerald ring", 1275, equip={"slot": "ring"})
add_item("ruby ring", 2025, equip={"slot": "ring"})
add_item("diamond ring", 3525, equip={"slot": "ring"})
add_item("gold amulet", 350, equip={"slot": "amulet"})
add_item("sapphire amulet", 900, equip={
    "amagic": 2, "dmagic": 2, "slot": "amulet"})
add_item("emerald amulet", 1250, equip={
    "arange": 3, "drange": 2, "slot": "amulet"})
add_item("ruby amulet", 2000, equip={
    "astab": 4, "aslash": 4, "acrush": 4, "str": 2, "slot": "amulet"})
add_item("diamond amulet", 3500, equip={
    "astab": 6, "aslash": 6, "acrush": 6, "amagic": 3, "arange": 3,
    "str": 3, "slot": "amulet"})


def _craft_jewellery(p, name):
    gem, lvl, xp = JEWELLERY[name]
    if not ROOMS[p.location].get("furnace"):
        say("You need a furnace to work gold (Lumbridge, Falador, Al Kharid, "
            "Edgeville).")
        return
    if p.lvl("crafting") < lvl:
        say(f"You need crafting level {lvl} to make a {name}.")
        return
    if not p.has("gold bar"):
        say("You need a gold bar (smelt gold ore).")
        return
    if gem and not p.has(gem):
        say(f"You need a {gem} (cut an uncut {gem} with a chisel).")
        return
    p.take("gold bar")
    if gem:
        p.take(gem)
    p.add(name)
    say(f"You pour the gold into a mould and set it — a {name}!", "byellow")
    p.gain_xp("crafting", xp)
    return True


# --- Runecrafting altars across the realm -----------------------------------
# (the air altar has stood alone long enough; craftrune works at each)
ROOMS.update({
    "mind_altar": dict(name="Mind Altar",
        desc="A wind-scoured shrine on Ice Mountain's shoulder. Thoughts "
             "hum in the stones. ('craftrune' with rune essence)",
        exits={"out": "monastery"}, altar="mind"),
    "water_altar": dict(name="Water Altar",
        desc="A glassy pool deep in the swamp mist. The air tastes of rain. "
             "('craftrune' with rune essence)",
        exits={"out": "swamp"}, altar="water"),
    "earth_altar": dict(name="Earth Altar",
        desc="A ring of standing stones north-east of Varrock, thick with "
             "the smell of loam. ('craftrune' with rune essence)",
        exits={"out": "varrock_east_bank"}, altar="earth"),
    "fire_altar": dict(name="Fire Altar",
        desc="A scorched ruin in the dunes where the sand has turned to "
             "glass. ('craftrune' with rune essence)",
        exits={"out": "al_kharid_square"}, altar="fire"),
    "body_altar": dict(name="Body Altar",
        desc="A squat stone shrine below Ice Mountain, humming with a slow "
             "heartbeat. ('craftrune' with rune essence)",
        exits={"out": "barbarian_village"}, altar="body"),
})
ROOMS["monastery"]["exits"]["altar"] = "mind_altar"
ROOMS["swamp"]["exits"]["altar"] = "water_altar"
ROOMS["varrock_east_bank"]["exits"]["altar"] = "earth_altar"
ROOMS["al_kharid_square"]["exits"]["altar"] = "fire_altar"
ROOMS["barbarian_village"]["exits"]["altar"] = "body_altar"
ROOMS["swamp"]["desc"] += " A still pool glimmers oddly ('altar')."
ROOMS["monastery"]["desc"] += " A path climbs toward the Mind Altar ('altar')."
ROOMS["varrock_east_bank"]["desc"] += " Standing stones rise to the north-east ('altar')."
ROOMS["al_kharid_square"]["desc"] += " Scorched ruins shimmer in the dunes ('altar')."
ROOMS["barbarian_village"]["desc"] += " A humming shrine squats by the rocks ('altar')."
REGIONS.update({"mind_altar": "Edgeville", "water_altar": "Lumbridge",
                "earth_altar": "Varrock", "fire_altar": "AlKharid",
                "body_altar": "Barbarian"})

# --- Yew & magic trees + high-tier fletching ---------------------------------
add_item("yew logs", 160, log_fm_xp=202)
add_item("magic logs", 640, log_fm_xp=303)
TREES["yew"] = ("yew logs", 60, 175)
TREES["magic"] = ("magic logs", 75, 250)
ROOMS["lumbridge_church"]["trees"] = ["yew"]
ROOMS["lumbridge_church"]["desc"] += " Ancient yews shade the graveyard."
ROOMS["seers_village"]["trees"].append("yew")
ROOMS["catherby"]["trees"].append("magic")
ROOMS["catherby"]["desc"] += " A lone magic tree sparkles north of the bank."

for _u, _v in [("yew shortbow (u)", 400), ("yew longbow (u)", 480),
               ("magic shortbow (u)", 800), ("magic longbow (u)", 1050)]:
    add_item(_u, _v)
add_item("yew shortbow", 800, members=True,
         equip={"arange": 47, "slot": "weapon", "req": {"ranged": 40}})
add_item("yew longbow", 960, members=True,
         equip={"arange": 55, "slot": "weapon", "req": {"ranged": 40}})
add_item("magic longbow", 2100, members=True,
         equip={"arange": 71, "slot": "weapon", "req": {"ranged": 50}})
FLETCH_CUT["yew logs"] = [("yew shortbow (u)", 65, 67),
                          ("yew longbow (u)", 70, 75)]
FLETCH_CUT["magic logs"] = [("magic shortbow (u)", 80, 83),
                            ("magic longbow (u)", 85, 91)]
FLETCH_STRING.update({
    "yew shortbow (u)": ("yew shortbow", 65, 67),
    "yew longbow (u)": ("yew longbow", 70, 75),
    "magic shortbow (u)": ("magic shortbow", 80, 83),
    "magic longbow (u)": ("magic longbow", 85, 91),
})

# --- Skill capes (99 mastery; the Wise Old Man sells them in Draynor) --------
SKILLCAPE_PRICE = 99000
for _s in SKILLS:
    add_item(f"{_s} cape", SKILLCAPE_PRICE, equip={
        "dstab": 9, "dslash": 9, "dcrush": 9, "dmagic": 9, "drange": 9,
        "prayer": 1, "slot": "cape", "req": {_s: 99}})


def talk_wise_old_man(p):
    mastered = [s for s in SKILLS if p.base_lvl(s) >= 99]
    if not mastered:
        say("Wise Old Man: \"Master any skill — level 99 — and I'll sell you "
            "its cape of accomplishment. Off you go; greatness takes "
            "grinding.\"")
        return
    say("Wise Old Man: \"Ah, a true master! I can sell you: "
        + ", ".join(f"{s} cape" for s in mastered)
        + f" — {SKILLCAPE_PRICE:,} coins each. Type 'skillcape <skill>'.\"",
        "gold")


def cmd_skillcape(p, arg):
    if p.location != "draynor_village":
        say("The Wise Old Man sells skill capes in Draynor Village.", "grey")
        return
    skill = _resolve_skill(arg)
    if not skill:
        return talk_wise_old_man(p)
    if p.base_lvl(skill) < 99:
        say(f"Wise Old Man: \"Come back when your {skill} is level 99 — it's "
            f"{p.base_lvl(skill)} now.\"", "byellow")
        return
    if not p.has("coins", SKILLCAPE_PRICE):
        say(f"Wise Old Man: \"The cape costs {SKILLCAPE_PRICE:,} coins — "
            "mastery must be celebrated properly.\"", "byellow")
        return
    p.take("coins", SKILLCAPE_PRICE)
    p.add(f"{skill} cape")
    banner("CAPE OF ACCOMPLISHMENT", color="gold", line_color="gold")
    say(f"The Wise Old Man drapes the {skill} cape over your shoulders. "
        "Wear it with pride, master.", "gold", "bold")


QUEST_TALK["skillcape"] = talk_wise_old_man
NPC_NAMES["skillcape"] = "the Wise Old Man"
ROOMS["draynor_village"]["npc"] = ["vampyre_slayer", "witch_potion",
                                   "skillcape"]
ROOMS["draynor_village"]["desc"] += (" The Wise Old Man watches the street "
                                     "from his doorway.")
HANDLERS["skillcape"] = cmd_skillcape
BATCHABLE.add("craft")      # jewellery & leatherwork batch nicely now


# ===========================================================================
#  SKILLING SYNERGIES  (jewellery enchanting, thieving stalls)
# ===========================================================================
# Enchanting: gem rings become magic rings with real effects (cosmic runes,
# magic xp). Stalls: Varrock's tea stall and the Ardougne market give
# thieving a proper ladder beyond pickpocketing.

SHOPS["rune"]["cosmic rune"] = 120

# base ring -> (enchanted ring, magic level, xp, runes)
ENCHANT = {
    "sapphire ring": ("ring of recoil", 7, 17,
                      {"cosmic rune": 1, "water rune": 1}),
    "emerald ring": ("ring of life", 27, 37,
                     {"cosmic rune": 1, "air rune": 3}),
    "ruby ring": ("ring of forging", 49, 59,
                  {"cosmic rune": 1, "fire rune": 5}),
    "diamond ring": ("ring of wealth", 57, 67,
                     {"cosmic rune": 1, "earth rune": 10}),
}
add_item("ring of recoil", 900, equip={"slot": "ring"})
add_item("ring of life", 1200, equip={"slot": "ring"})
add_item("ring of forging", 2100, equip={"slot": "ring"})
add_item("ring of wealth", 3600, equip={"slot": "ring"})


def cmd_enchant(p, arg):
    name = arg.strip().lower()
    if not name:
        say("Enchant which ring? " + ", ".join(
            f"{base} → {e[0]} (magic {e[1]})" for base, e in ENCHANT.items()),
            "bcyan")
        say("  Each needs cosmic + elemental runes (rune shop, or craft "
            "them).", "grey")
        return
    base = name if name in ENCHANT else \
        next((b for b, e in ENCHANT.items()
              if name in b or name in e[0]), None)
    if not base:
        say("You can't enchant that. ('enchant' lists the rings.)", "grey")
        return
    enchanted, lvl, xp, runes = ENCHANT[base]
    if not p.has(base):
        say(f"You have no {base} (craft one at a furnace).", "byellow")
        return
    if p.lvl("magic") < lvl:
        say(f"You need magic level {lvl} to enchant a {base}.", "byellow")
        return
    if not _consume_runes(p, runes):
        say("You need: " + ", ".join(f"{q}x {r}" for r, q in runes.items())
            + ".", "byellow")
        return
    p.take(base)
    p.add(enchanted)
    say(f"The gem flares with power — your {base} is now a {enchanted}!",
        "bmagenta", "bold")
    p.gain_xp("magic", xp)
    return True


HANDLERS["enchant"] = cmd_enchant
BATCHABLE.add("enchant")

# ring effects live in: _player_recoil (combat), _ring_of_life (combat),
# cmd_smelt (forging), _roll_drops (wealth)

# --- Thieving stalls ---------------------------------------------------------
# stall -> (thieving level, xp, [(loot, weight), ...])
STALLS = {
    "tea stall": (5, 16, [("cup of tea", 1.0)]),
    "baker's stall": (20, 24, [("bread", 0.7), ("cake", 0.3)]),
    "silk stall": (35, 48, [("silk", 1.0)]),
    "gem stall": (75, 160, [("uncut sapphire", 0.55), ("uncut emerald", 0.30),
                            ("uncut ruby", 0.12), ("uncut diamond", 0.03)]),
}
add_item("cup of tea", 10, heal=3)
add_item("silk", 60)


def cmd_steal(p, arg):
    if not getattr(p, "members", False):
        say("Thieving is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    stalls = ROOMS[p.location].get("stalls", [])
    if not stalls:
        say("There are no stalls to steal from here.")
        return
    want = arg.strip().lower()
    stall = next((s for s in stalls if want and want in s),
                 None if want else stalls[0])
    if not stall:
        say(f"No such stall. Here: {', '.join(stalls)}")
        return
    lvl, xp, loot = STALLS[stall]
    if p.lvl("thieving") < lvl:
        say(f"You need thieving level {lvl} for the {stall}.", "byellow")
        return
    say(f"You wait for the stallkeeper to look away...")
    if random.random() < gather_chance(p.lvl("thieving"), lvl):
        item = random.choices([i for i, _ in loot],
                              weights=[w for _, w in loot])[0]
        p.add(item)
        say(f"You swipe {item} from the {stall}!", "purple")
        p.gain_xp("thieving", xp)
        return True
    dmg = min(random.randint(1, 3), max(0, p.hp - 1))   # guards won't kill you
    p.hp -= dmg
    say(f"A guard spots you and clubs you for {dmg}! You stumble away, "
        "stunned.", "bred")
    return False


HANDLERS["steal"] = cmd_steal
BATCHABLE.add("steal")
BATCHABLE.add("light")

ROOMS["varrock_square"]["stalls"] = ["tea stall"]
ROOMS["varrock_square"]["desc"] += " A tea stall steams by the fountain."
ROOMS["ardougne"]["stalls"] = ["baker's stall", "silk stall", "gem stall"]
ROOMS["ardougne"]["desc"] += (" Market stalls line the square: baked goods, "
                              "silk, and glittering gems.")


