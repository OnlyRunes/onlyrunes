# ===========================================================================
#  DESERT DEEP  (Sophanem, Pyramid Plunder, Desert Treasure -> ANCIENTS)
# ===========================================================================
# South of Nardah the desert ends in Sophanem, city of the dead. Its great
# pyramid is a thieving playground of eight ever-richer rooms — and an
# archaeologist's dig points to four diamonds, four guardians, and the
# pyramid of Jaldraocht, where Azzanadra's ANCIENT MAGICKS wait.

# --- pyramid plunder ---------------------------------------------------------
add_item("pharaoh's sceptre", 250000, members=True,
         equip={"slot": "weapon", "amagic": 5, "dmagic": 3})
EFFECT_NOTES["pharaoh's sceptre"] = ("the golden prize of Pyramid Plunder "
                                     "— proof you robbed the dead blind")
PLUNDER_TIERS = [(21, 60), (31, 90), (41, 125), (51, 165),
                 (61, 215), (71, 275), (81, 350), (91, 450)]


def cmd_plunder(p, arg):
    if p.location != "plunder_pyramid":
        say("The Sophanem pyramid is where the plundering happens.",
            "grey")
        return
    if p.lvl("thieving") < 21:
        say("You need thieving level 21 for even the first room.")
        return None
    tier = min(getattr(p, "plunder_tier", 0) + 1, len(PLUNDER_TIERS))
    while tier > 1 and p.lvl("thieving") < PLUNDER_TIERS[tier - 1][0]:
        tier -= 1
    p.plunder_tier = tier
    req, xp = PLUNDER_TIERS[tier - 1]
    say(f"— Room {tier} of 8 —", "byellow", "bold")
    if random.random() < 0.25:
        dmg = min(random.randint(2, 6), max(0, p.hp - 1))
        p.hp -= dmg
        say(f"A snake strikes from an urn — it bites you for {dmg}!",
            "green")
    coins = random.randint(20 * tier, 90 * tier)
    p.add("coins", coins)
    say(f"You rifle the urns for {coins} coins.")
    if random.random() < 0.10:
        gem = random.choices(list(GEM_CUT), weights=[8, 5, 2, 1])[0]
        p.add(gem)
        say(f"Something glitters in the dust — an {gem}!", "bcyan")
    if tier == len(PLUNDER_TIERS) and random.random() < 0.04:
        p.add("pharaoh's sceptre")
        say("Inside the golden sarcophagus lies the PHARAOH'S SCEPTRE!",
            "gold", "bold")
    p.gain_xp("thieving", xp)
    return True


HANDLERS["plunder"] = cmd_plunder
BATCHABLE.add("plunder")

# --- ancient magicks -----------------------------------------------------------
def _anc_ice(p, m, dmg):
    if not m.get("boss") or random.random() < 0.5:
        m["stunned"] = True
        print("  " + paint("Ice locks its limbs — FROZEN for a turn!",
                           "bcyan"))


def _anc_blood(p, m, dmg):
    heal = max(1, dmg // 4)
    p.hp = min(p.max_hp, p.hp + heal)
    print("  " + paint(f"Blood magic feeds you. (+{heal} hp)", "bred"))


def _anc_shadow(p, m, dmg):
    if m["attack"] > 10:
        m["attack"] = max(10, m["attack"] - 3)
        print("  " + paint("Shadow saps its aim. (-3 attack)", "purple"))


def _anc_smoke(p, m, dmg):
    if m["cur"] > 1:
        extra = min(random.randint(1, 4), m["cur"] - 1)
        m["cur"] -= extra
        print("  " + paint(f"The smoke chokes it for {extra} more.",
                           "grey"))


SPELLS.update({
    "smoke rush":  {"type": "combat", "max": 13, "lvl": 50, "xp": 30,
                    "book": "ancient", "effect": _anc_smoke,
                    "runes": {"fire rune": 1, "air rune": 1,
                              "chaos rune": 2, "death rune": 2}},
    "shadow rush": {"type": "combat", "max": 14, "lvl": 52, "xp": 31,
                    "book": "ancient", "effect": _anc_shadow,
                    "runes": {"earth rune": 1, "chaos rune": 2,
                              "death rune": 2}},
    "blood rush":  {"type": "combat", "max": 15, "lvl": 56, "xp": 33,
                    "book": "ancient", "effect": _anc_blood,
                    "runes": {"chaos rune": 2, "death rune": 2,
                              "blood rune": 1}},
    "ice rush":    {"type": "combat", "max": 16, "lvl": 58, "xp": 34,
                    "book": "ancient", "effect": _anc_ice,
                    "runes": {"water rune": 2, "chaos rune": 2,
                              "death rune": 2}},
    "smoke blitz": {"type": "combat", "max": 23, "lvl": 74, "xp": 42,
                    "book": "ancient", "effect": _anc_smoke,
                    "runes": {"fire rune": 2, "air rune": 2,
                              "death rune": 2, "blood rune": 2}},
    "shadow blitz": {"type": "combat", "max": 24, "lvl": 76, "xp": 43,
                     "book": "ancient", "effect": _anc_shadow,
                     "runes": {"earth rune": 2, "death rune": 2,
                               "blood rune": 2}},
    "blood blitz": {"type": "combat", "max": 25, "lvl": 80, "xp": 45,
                    "book": "ancient", "effect": _anc_blood,
                    "runes": {"death rune": 2, "blood rune": 4}},
    "ice blitz":   {"type": "combat", "max": 26, "lvl": 82, "xp": 46,
                    "book": "ancient", "effect": _anc_ice,
                    "runes": {"water rune": 3, "death rune": 2,
                              "blood rune": 2}},
})


def _jaldraocht_altar(p):
    stage = _q(p, "desert_treasure")
    if stage == "pyramid":
        _complete_banner("Desert Treasure")
        say("You set the four diamonds in the altar's carvings. The "
            "pyramid HUMS — and knowledge older than the gods floods "
            "your mind. ANCIENT MAGICKS unlocked: smoke, shadow, blood "
            "and ICE. ('autocast ice blitz' — the altar swaps your "
            "spellbook any time)", "bmagenta", "bold")
        for gem in ("smoke diamond", "shadow diamond", "blood diamond",
                    "ice diamond"):
            if p.has(gem):
                p.take(gem)
        p.quests["desert_treasure"] = "complete"
        p.spellbook = "ancient"
        p.gain_xp("magic", 20000)
    elif stage == "complete":
        p.spellbook = "ancient" if getattr(p, "spellbook", "standard") \
            == "standard" else "standard"
        say(f"The altar turns its pages through your mind — spellbook "
            f"swapped to {p.spellbook.upper()}.", "bmagenta", "bold")
    else:
        say("The altar's carvings show four empty settings, cut for "
            "diamonds. (Quest: Desert Treasure — the archaeologist at "
            "Sophanem)", "grey")


# --- the four guardians -----------------------------------------------------------
_DT_GUARDIANS = {
    "dessous": ("blood diamond", "mort_myre",
        {"abonus": 30, "atktype": ["slash", "magic"], "att": 120,
         "cb": 139, "dstab": 45, "dslash": 45, "dcrush": 40, "dmagic": 50,
         "drange": 45, "def": 70, "hp": 105, "maxhit": 13, "str": 115,
         "weak": "crush"}),
    "kamil": ("ice diamond", "white_wolf_mountain",
        {"abonus": 32, "atktype": ["magic"], "att": 125, "cb": 154,
         "dstab": 50, "dslash": 50, "dcrush": 45, "dmagic": 55,
         "drange": 50, "def": 75, "hp": 110, "maxhit": 14, "str": 120,
         "weak": "slash"}),
    "fareed": ("smoke diamond", "smoke_dungeon",
        {"abonus": 34, "atktype": ["magic", "crush"], "att": 130,
         "cb": 167, "dstab": 55, "dslash": 55, "dcrush": 50, "dmagic": 55,
         "drange": 55, "def": 78, "hp": 115, "maxhit": 15, "str": 125,
         "weak": "crush"}),
    "damis": ("shadow diamond", "varrock_sewers",
        {"abonus": 36, "atktype": ["crush"], "att": 135, "cb": 174,
         "dstab": 55, "dslash": 55, "dcrush": 50, "dmagic": 60,
         "drange": 55, "def": 80, "hp": 120, "maxhit": 15, "str": 130,
         "weak": "crush"}),
}
def _dt_guardian_alive(gem):
    return lambda p: (_q(p, "desert_treasure") == "diamonds"
                      and not p.has(gem))


for _g, (_gem, _room, _st) in _DT_GUARDIANS.items():
    add_item(_gem, 5000, members=True)
    _add_mob(_g, _st, [("coins", 500, 2000, 1.0)], members=True,
             rank="elite")
    MONSTERS[_g]["boss"] = True
    MONSTERS[_g]["rank"] = "boss"
    _BOSSES.add(_g)
    QUEST_SPAWNS.append((_room, _g, _dt_guardian_alive(_gem)))

# --- the region --------------------------------------------------------------------
ROOMS.update({
    "sophanem": dict(name="Sophanem",
        desc="The city of the dead, half-swallowed by sand. Priests "
             "whisper behind cat-masks, the great plunder pyramid stands "
             "open ('pyramid'), and an ARCHAEOLOGIST waves you over, "
             "dusty with excitement. Jaldraocht rises west ('west').",
        exits={"north": "nardah", "pyramid": "plunder_pyramid",
               "west": "jaldraocht"},
        npc="desert_treasure", desert=True, members=True),
    "plunder_pyramid": dict(name="The Plunder Pyramid",
        desc="Eight chambers of urns, snakes and sarcophagi, each richer "
             "and meaner than the last. ('plunder' — batch it if you "
             "dare; leaving resets your depth)",
        exits={"out": "sophanem"},
        desert=True, members=True),
    "jaldraocht": dict(name="Pyramid of Jaldraocht",
        desc="A black pyramid the sand refuses to touch. At its heart "
             "stands Azzanadra's altar, carved with four empty settings "
             "('pray altar').",
        exits={"east": "sophanem"},
        prayer_altar=True, desert=True, members=True),
})
ROOMS["nardah"]["exits"]["south"] = "sophanem"
ROOMS["nardah"]["desc"] += (" South, the road dies at Sophanem, city of "
                            "the dead.")
REGIONS.update({"sophanem": "AlKharid", "plunder_pyramid": "AlKharid",
                "jaldraocht": "AlKharid"})

# --- Desert Treasure (3 QP) --------------------------------------------------------
ALL_QUESTS["desert_treasure"] = "Desert Treasure"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["desert_treasure"] = 3
NPC_NAMES["desert_treasure"] = "The Archaeologist"
QUEST_STARTS["desert_treasure"] = "the Archaeologist, Sophanem (south of " \
                                  "Nardah)"
QUEST_HINTS["desert_treasure"] = {
    "diamonds": "slay the four guardians: Dessous (Mort Myre), Kamil "
                "(White Wolf Mtn), Fareed (the smoke dungeon), Damis "
                "(Varrock sewers)",
    "pyramid": "carry the four diamonds to Jaldraocht and 'pray altar'",
}


def talk_archaeologist(p):
    stage = _q(p, "desert_treasure")
    if stage == "not_started":
        banner("Quest Start: Desert Treasure", color="purple",
               line_color="bmagenta")
        say("The Archaeologist: \"Four DIAMONDS — blood, ice, smoke, "
            "shadow — each guarded by something that should be dead. "
            "Bring all four to the black pyramid west of here, and the "
            "magic sealed inside is yours. I'd do it myself, but I've "
            "got a trowel.\"")
        p.quests["desert_treasure"] = "diamonds"   # the four guardians wake
    elif stage == "diamonds":
        have = [g for g, (gem, _r, _s) in _DT_GUARDIANS.items()
                if p.has(gem)]
        if len(have) == 4:
            p.quests["desert_treasure"] = "pyramid"
            say("The Archaeologist goes pale: \"All FOUR? Then go — "
                "Jaldraocht, west of the city. Pray at the altar and "
                "take what Azzanadra left.\"", "byellow")
        else:
            say(f"The Archaeologist: \"{len(have)}/4 diamonds. Dessous "
                "haunts Mort Myre, Kamil the white peaks, Fareed the "
                "smoke below Pollnivneach, Damis the sewers of "
                "Varrock.\"")
    elif stage == "pyramid":
        say("The Archaeologist: \"Jaldraocht! West! Pray at the "
            "altar!\"")
    elif stage == "complete":
        say("The Archaeologist: \"Careful with those spells — the last "
            "owner is still technically alive.\"")


QUEST_TALK["desert_treasure"] = talk_archaeologist


# ===========================================================================
#  ZULRAH  (the toxic serpent of Zul-Andra, and the gear it bleeds)
# ===========================================================================
# Up the jungle river from Shilo, the snake-priests of Zul-Andra feed
# their god. ZULRAH rotates through three forms mid-fight — green, red,
# blue — each attacking differently and each soft to a different style.
# Its fangs and scales build the toxic arsenal: blowpipe, serpentine
# helm, swamp trident.

# --- the toxic arsenal --------------------------------------------------------
add_item("tanzanite fang", 800000, members=True)
add_item("magic fang", 800000, members=True)
add_item("serpentine visage", 800000, members=True)
add_item("toxic blowpipe", 2500000, members=True, equip={
    "slot": "weapon", "arange": 60, "rstr": 40, "self_ammo": True,
    "req": {"ranged": 75}})
EFFECT_NOTES["toxic blowpipe"] = ("chews its own scales for darts — "
                                  "ranged with no ammo needed")
add_item("serpentine helm", 1800000, members=True, equip={
    "slot": "head", "dstab": 30, "dslash": 32, "dcrush": 34, "dmagic": 10,
    "drange": 30, "str": 3, "req": {"defence": 75}})
EFFECT_NOTES["serpentine helm"] = ("venom cannot touch you while it "
                                   "watches from your brow")
add_item("trident of the swamp", 3000000, members=True, equip={
    "slot": "weapon", "amagic": 28, "dmagic": 3, "powered": 25,
    "req": {"magic": 78}})
EFFECT_NOTES["trident of the swamp"] = ("the sea trident, envenomed — "
                                        "runeless magic, max 25")
CRAFT_RECIPES.update({
    "toxic blowpipe": ("tanzanite fang", 1, 73, 500),
    "serpentine helm": ("serpentine visage", 1, 52, 400),
})

# --- the serpent ----------------------------------------------------------------
ZULRAH_ART = r"""
              ______
           .-'      '-.
          /   .-""-.   \
         |   /  @@  \   |
          \  \ vvvv /  /
        ~~~\  '----' /~~~
      ~~~~  '-.____.-'  ~~~~
"""

_ZULRAH_FORMS = {
    "green": {"atype": "ranged", "weak": "magic",
              "dbonus": {"stab": 120, "slash": 120, "crush": 120,
                         "magic": 10, "ranged": 120},
              "cry": "ZULRAH surfaces GREEN — scales rattle and venom "
                     "spines fan wide! (magic bites deepest now)"},
    "red": {"atype": "crush", "weak": "slash",
            "dbonus": {"stab": 10, "slash": 10, "crush": 10,
                       "magic": 120, "ranged": 120},
            "cry": "ZULRAH surfaces CRIMSON — it rears to strike with "
                   "its whole body! (steel bites deepest now)"},
    "blue": {"atype": "magic", "weak": "ranged",
             "dbonus": {"stab": 120, "slash": 120, "crush": 120,
                        "magic": 120, "ranged": 10},
             "cry": "ZULRAH surfaces BLUE — sea-magic crackles along "
                    "its hood! (arrows bite deepest now)"},
}
_ZULRAH_ORDER = ["green", "red", "blue"]


def _zulrah_poison(p, m, dmg):
    if dmg > 0 and not getattr(p, "poison", 0) and random.random() < 0.4:
        p.poison = 3
        print("  " + paint("Zulrah's venom takes hold — POISONED!",
                           "green"))


def _zulrah_take_turn(p, m):
    turn = m.get("zul_turn", 0)
    m["zul_turn"] = turn + 1
    if turn % 3 == 0:                    # a new form every three turns
        form = _ZULRAH_ORDER[(turn // 3) % 3]
        f = _ZULRAH_FORMS[form]
        m["zul_form"] = form
        m["dbonus"] = dict(f["dbonus"])
        m["weakness"] = f["weak"]
        say(f["cry"], {"green": "bgreen", "red": "bred",
                       "blue": "bblue"}[form], "bold")
    f = _ZULRAH_FORMS[m.get("zul_form", "green")]
    atype = f["atype"]
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    p_def_roll = _player_def_roll(p, atype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, m["max_hit"])
        prot = "magic" if atype == "magic" else \
            ("ranged" if atype == "ranged" else "melee")
        if p.prayer_protects(prot):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        print("  " + paint(f"Zulrah strikes for {dmg}.", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        if dmg > 0 and p.hp > 0:
            _zulrah_poison(p, m, dmg)
    else:
        print("  " + paint("You slip aside from the strike.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer "
                               "points).", "bmagenta"))
    return "died" if p.hp <= 0 else None


def _zulrah_intro(name):
    return [_tint(ZULRAH_ART, "grey"), _tint(ZULRAH_ART, "bgreen", "bold")]


def _zulrah_death(name):
    return [_tint(ZULRAH_ART, "bgreen"), _tint(ZULRAH_ART, "grey", "dim")]


_add_mob("zulrah",
    {"abonus": 50, "atktype": ["ranged", "magic"], "att": 190, "cb": 725,
     "dstab": 120, "dslash": 120, "dcrush": 120, "dmagic": 10,
     "drange": 120, "def": 100, "hp": 300, "maxhit": 21, "str": 190,
     "weak": "magic"},
    [("tanzanite fang", 1, 1, 0.03), ("magic fang", 1, 1, 0.03),
     ("serpentine visage", 1, 1, 0.03), ("coins", 8000, 25000, 1.0),
     ("raw shark", 4, 10, 0.8), ("grimy ranarr", 3, 8, 0.5),
     ("antipoison", 2, 4, 0.6)], members=True)
MONSTERS["zulrah"]["boss"] = True
MONSTERS["zulrah"]["rank"] = "boss"
_BOSSES.add("zulrah")
BOSS_TURN["zulrah"] = _zulrah_take_turn
BOSS_INTRO["zulrah"] = _zulrah_intro
BOSS_DEATH["zulrah"] = _zulrah_death
MONSTER_ART["zulrah"] = ZULRAH_ART

# --- zul-andra --------------------------------------------------------------------
ROOMS.update({
    "zul_andra": dict(name="Zul-Andra",
        desc="A stilt-village where the jungle river meets the sea. "
             "Snake-priests chant over a sacrificial pool that breathes "
             "green mist — ZULRAH waits below ('pool').",
        exits={"river": "shilo_village", "pool": "zulrah_shrine"},
        members=True),
    "zulrah_shrine": dict(name="Zulrah's Shrine",
        desc="A drowned altar ringed by offerings. The water heaves — "
             "and the serpent god rises, form flowing into form.",
        exits={"out": "zul_andra"},
        monsters=["zulrah"], members=True),
})
ROOMS["shilo_village"]["exits"]["river"] = "zul_andra"
ROOMS["shilo_village"]["desc"] += (" A reed boat waits on the river, "
                                   "poled by a silent snake-priest "
                                   "('river').")
REGIONS.update({"zul_andra": "Karamja", "zulrah_shrine": "Karamja"})
TRAVEL_HUBS["zul-andra"] = "zul_andra"
TRAVEL_NAMES.append("Zul-Andra")


