

# ===========================================================================
#  FOSSIL ISLAND, DRAGON SLAYER II & VORKATH  (the undead dragon of Ungael)
# ===========================================================================
# Sail from Port Phasmatys to Fossil Island, where Dallas Jones digs up the
# Dragonkin plot. DRAGON SLAYER II (grandmaster): hunt the metal dragons of
# the Lithkren vault for three relics, then face GALVEK on the shore of
# Ungael. Completing it opens the crater where VORKATH sleeps — the marquee
# solo boss, felled fastest by dragon-hunter gear and a dragonfire ward.

# --- dragon-hunter arsenal ----------------------------------------------------
add_item("superior dragon bones", 200, members=True, bury=("prayer", 150))
add_item("dragon bolts", 130, members=True,
         equip={"slot": "ammo", "rstr": 60})
EFFECT_NOTES["dragon bolts"] = "heavy dragon-tipped bolts for a crossbow"
add_item("draconic visage", 5000000, members=True)
EFFECT_NOTES["draconic visage"] = ("an ancient dragon mask — a smith can "
                                   "beat it into a dragonfire ward")
add_item("dragonfire ward", 4000000, members=True, equip={
    "slot": "shield", "dstab": 20, "dslash": 20, "dcrush": 20,
    "dmagic": 25, "drange": 22, "req": {"defence": 70, "smithing": 90}})
EFFECT_NOTES["dragonfire ward"] = ("soaks dragonfire like an anti-dragon "
                                   "shield, and guards your magic besides")
add_item("dragon hunter lance", 3600000, members=True, equip={
    "slot": "weapon", "astab": 85, "aslash": 55, "acrush": 55, "str": 78,
    "dragon_bane": True, "req": {"attack": 78}})
EFFECT_NOTES["dragon hunter lance"] = ("forged to butcher dragons — +25% "
                                       "against anything draconic")
add_item("dragon hunter crossbow", 4200000, members=True, equip={
    "slot": "weapon", "arange": 95, "two_handed": True,
    "dragon_bane": True, "req": {"ranged": 65}})
EFFECT_NOTES["dragon hunter crossbow"] = ("a dragonbone crossbow — tears "
                                          "into dragons, +25% draconic")
add_item("vorkath's head", 1000000, members=True)
EFFECT_NOTES["vorkath's head"] = ("the trophy skull of the undead dragon — "
                                  "proof you outlasted the spawn")
add_item("jar of decay", 2000000, members=True)
EFFECT_NOTES["jar of decay"] = "a jar of Ungael's rot — a collector's prize"

# smith the visage into a ward (needs the smithing an anti-dragon ward demands)
CRAFT_RECIPES["dragonfire ward"] = ("draconic visage", 1, 90, 2000)

# --- the metal dragons of Lithkren -------------------------------------------
# Regular (non-boss) dragons: dragon flag (dragon-hunter bonus applies),
# dragonfire flag (they breathe through the generic 30%/turn path). Their
# portraits come free from the "dragon" family silhouette.
_METAL_DRAGONS = {
    "adamant dragon": (
        {"abonus": 0, "atktype": ["slash", "dragonfire"], "att": 210,
         "cb": 338, "dstab": 90, "dslash": 90, "dcrush": 88, "dmagic": 80,
         "drange": 88, "def": 130, "hp": 240, "maxhit": 24, "str": 200,
         "weak": "stab"},
        [("adamant bar", 1, 2, 0.6), ("dragon bones", 1, 1, 1.0),
         ("dragon bolts", 8, 20, 0.4), ("coins", 3000, 9000, 1.0),
         ("grimy ranarr", 2, 5, 0.3)]),
    "rune dragon": (
        {"abonus": 0, "atktype": ["slash", "dragonfire", "ranged"],
         "att": 240, "cb": 380, "dstab": 100, "dslash": 100, "dcrush": 95,
         "dmagic": 90, "drange": 95, "def": 150, "hp": 255, "maxhit": 27,
         "str": 220, "weak": "stab"},
        [("rune bar", 1, 2, 0.5), ("dragon bones", 1, 1, 1.0),
         ("dragon bolts", 12, 30, 0.5), ("draconic visage", 1, 1, 0.02),
         ("coins", 5000, 14000, 1.0), ("grimy ranarr", 2, 6, 0.3)]),
    "mithril dragon": (
        {"abonus": 0, "atktype": ["slash", "dragonfire", "magic"],
         "att": 200, "cb": 304, "dstab": 85, "dslash": 85, "dcrush": 82,
         "dmagic": 78, "drange": 82, "def": 120, "hp": 220, "maxhit": 23,
         "str": 190, "weak": "stab"},
        [("mithril bar", 1, 3, 0.6), ("dragon bones", 1, 1, 1.0),
         ("dragon bolts", 8, 24, 0.4), ("draconic visage", 1, 1, 0.02),
         ("coins", 4000, 11000, 1.0)]),
}
for _d, (_st, _drops) in _METAL_DRAGONS.items():
    _add_mob(_d, _st, _drops, members=True, rank="elite")
    MONSTERS[_d]["dragon"] = True
    MONSTERS[_d]["dragonfire"] = True

# make sure the metal bars they drop exist (bronze/iron/steel already do)
for _bar in ("mithril bar", "adamant bar", "rune bar"):
    if _bar not in ITEMS:
        add_item(_bar, {"mithril bar": 420, "adamant bar": 1600,
                        "rune bar": 12000}[_bar])

# --- GALVEK  (Dragon Slayer II final boss) -----------------------------------
GALVEK_ART = r"""
        \___/                     \___/
     /\_(o o)_/\   ~ GALVEK ~   ___
    /  =\_v_/=  \  the Dragonkin's  \
   //    ) (    \\   last dragon    /
  ~~    /   \    ~~___          ___/
        ^^^^^     /  ~~~~~~~~~~~~
"""


def _galvek_bomb(p, m, dmg):
    if dmg > 0 and random.random() < 0.35:
        extra = min(random.randint(3, 8), max(0, p.hp - 1))
        if extra:
            p.hp -= extra
            print("  " + paint(f"A firebomb bursts at your feet for {extra} "
                               "more!", "orange"))


GALVEK_ATTACKS = [
    {"label": "a torrent of dragonfire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _fx_hellfire,
     "mult": 1.1, "w": 3, "atype": "magic", "dragonfire": True},
    {"label": "a barbed tail-lash", "verb": "sweeps",
     "color": ("bred", "bold"), "builder": _fx_charge,
     "mult": 1.0, "w": 2, "atype": "crush"},
    {"label": "a volley of firebombs", "verb": "hurls",
     "color": ("byellow", "bold"), "builder": _fx_slag,
     "mult": 0.9, "w": 2, "atype": "ranged", "effect": _galvek_bomb},
]


def _galvek_intro(name):
    return _fx((GALVEK_ART, "grey"), (GALVEK_ART, "bred", "bold"),
               (GALVEK_ART, "orange", "bold"))


def _galvek_death(name):
    return _fx((GALVEK_ART, "bred"), (GALVEK_ART, "grey", "dim"))


_add_mob("galvek",
    {"abonus": 40, "atktype": ["magic", "ranged", "crush"], "att": 260,
     "cb": 608, "dstab": 110, "dslash": 110, "dcrush": 105, "dmagic": 100,
     "drange": 105, "def": 160, "hp": 300, "maxhit": 28, "str": 230,
     "weak": "stab"},
    [("coins", 10000, 30000, 1.0), ("dragon bones", 2, 4, 1.0),
     ("draconic visage", 1, 1, 0.05)], members=True)
MONSTERS["galvek"]["boss"] = True
MONSTERS["galvek"]["rank"] = "boss"
MONSTERS["galvek"]["dragon"] = True
_BOSSES.add("galvek")
BOSS_TURN["galvek"] = lambda p, m: _boss_take_turn(p, m, GALVEK_ATTACKS)
BOSS_INTRO["galvek"] = _galvek_intro
BOSS_DEATH["galvek"] = _galvek_death
MONSTER_ART["galvek"] = GALVEK_ART

# --- VORKATH  (the undead dragon of Ungael) ----------------------------------
VORKATH_ART = r"""
          .====.        .====.
         / ^  ^ \      / (**) \
        | (xx)(xx)|===| ~~~~~~ |     V O R K A T H
         \  vvvv /     \  __  /   the undead dragon
      ___/`----'\___   /`----'\
     /  //|    |\\  \ //       \\
    ~~~ ` |    | ` ~~~~   acid  ~~~
          w    w
"""


def _vork_ice(p, m, dmg):
    if dmg > 0 and not getattr(p, "frozen", False) and random.random() < 0.5:
        p.frozen = True
        print("  " + paint("Vorkath's frostbreath freezes you solid — your "
                           "next action fails!", "bcyan"))


def _vork_venom(p, m, dmg):
    if dmg > 0 and getattr(p, "poison", 0) < 4 and random.random() < 0.5:
        p.poison = 4
        print("  " + paint("Acid spatters over you — VENOM courses in!",
                           "green"))


VORKATH_ATTACKS = [
    {"label": "a gout of undead dragonfire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _fx_hellfire,
     "mult": 1.1, "w": 3, "atype": "magic", "dragonfire": True},
    {"label": "a lash of frostbreath", "verb": "exhales",
     "color": ("bcyan", "bold"), "builder": _fx_bolt_blue,
     "mult": 0.9, "w": 2, "atype": "magic", "effect": _vork_ice},
    {"label": "a spray of acid", "verb": "vomits",
     "color": ("green", "bold"), "builder": _fx_miasma,
     "mult": 0.9, "w": 2, "atype": "ranged", "effect": _vork_venom},
    {"label": "a raking bite", "verb": "snaps with",
     "color": ("bred", "bold"), "builder": _fx_jaws,
     "mult": 1.0, "w": 2, "atype": "stab"},
]


def _vorkath_take_turn(p, m):
    t = m.get("vork_turn", 0)
    m["vork_turn"] = t + 1
    # every seventh turn a ZOMBIFIED SPAWN erupts and snuffs your prayers
    if t and t % 7 == 6:
        animate(_fx((FX_BILLOW1, "bmagenta"), (FX_BILLOW2, "green", "bold")),
                delay=0.13, center=True)
        say("Vorkath spits a ZOMBIFIED SPAWN — it shrieks, and your prayers "
            "gutter out! (kill it fast — keep attacking)", "bmagenta",
            "bold")
        if p.active_prayers or getattr(p, "prayer_points", 0) > 0:
            p.prayer_points = 0
            p.active_prayers = []
        dmg = min(random.randint(4, 11), max(0, p.hp - 1))
        if dmg:
            p.hp -= dmg
            print("  " + paint(f"The spawn savages you for {dmg} before you "
                               "cut it down.", "bred") + "  "
                  + paint("HP ", "white")
                  + bar_meter(max(p.hp, 0), p.max_hp, 18))
        return "died" if p.hp <= 0 else None
    return _boss_take_turn(p, m, VORKATH_ATTACKS)


def _vorkath_intro(name):
    return _fx((VORKATH_ART, "grey", "dim"), (VORKATH_ART, "green"),
               (VORKATH_ART, "bcyan", "bold"), (VORKATH_ART, "bred", "bold"))


def _vorkath_death(name):
    return _fx((VORKATH_ART, "bred"), (VORKATH_ART, "green", "dim"),
               (VORKATH_ART, "grey", "dim"))


_add_mob("vorkath",
    {"abonus": 50, "atktype": ["magic", "ranged", "stab"], "att": 280,
     "cb": 732, "dstab": 130, "dslash": 130, "dcrush": 125, "dmagic": 110,
     "drange": 125, "def": 214, "hp": 360, "maxhit": 30, "str": 250,
     "weak": "stab"},
    [("superior dragon bones", 1, 2, 1.0), ("dragon bolts", 20, 50, 0.6),
     ("coins", 12000, 40000, 1.0), ("vorkath's head", 1, 1, 0.03),
     ("draconic visage", 1, 1, 0.03),
     ("dragon hunter crossbow", 1, 1, 0.02), ("jar of decay", 1, 1, 0.01),
     ("grimy ranarr", 3, 8, 0.4)], members=True)
MONSTERS["vorkath"]["boss"] = True
MONSTERS["vorkath"]["rank"] = "boss"
MONSTERS["vorkath"]["dragon"] = True
_BOSSES.add("vorkath")
BOSS_TURN["vorkath"] = _vorkath_take_turn
BOSS_INTRO["vorkath"] = _vorkath_intro
BOSS_DEATH["vorkath"] = _vorkath_death
MONSTER_ART["vorkath"] = VORKATH_ART

# --- the region: Fossil Island, Lithkren, Ungael -----------------------------
ROOMS.update({
    "fossil_island": dict(name="Fossil Island",
        desc="A wild green island of tar swamps and birdhouse marshes. At "
             "the Museum Camp, DALLAS JONES pores over dragonkin bones and "
             "waves you over ('talk'). A flooded vault gapes to the north "
             "('vault'), and a longship rides the surf, bound for the "
             "frozen isle of Ungael ('ungael').",
        exits={"sail": "port_phasmatys", "vault": "lithkren_vault",
               "ungael": "ungael_shore"},
        npc="dragon_slayer_2", members=True),
    "lithkren_vault": dict(name="The Lithkren Vault",
        desc="A drowned Dragonkin laboratory under the waves. Metal dragons "
             "— mithril, adamant, rune — stalk the flooded halls, guarding "
             "relics of their makers.",
        exits={"out": "fossil_island"},
        monsters=["mithril dragon", "adamant dragon", "rune dragon"],
        members=True),
    "ungael_shore": dict(name="Ungael Shore",
        desc="A black volcanic beach under a bruised sky. The Dragonkin's "
             "ruined tower leans over a crater to the north ('crater'), "
             "where something vast and cold still breathes.",
        exits={"boat": "fossil_island", "crater": "vorkath_crater"},
        members=True),
    "vorkath_crater": dict(name="Vorkath's Crater",
        desc="A frozen crater strewn with dragon bones and the shells of "
             "old spawn. VORKATH uncoils from the ice — six eyes opening, "
             "one by one.",
        exits={"out": "ungael_shore"},
        monsters=["vorkath"], members=True,
        qlock=("dragon_slayer_2", ["complete"],
               "The Dragonkin ward seals the crater — only one who has "
               "finished DRAGON SLAYER II may enter.")),
})
ROOMS["port_phasmatys"]["exits"]["fossil"] = "fossil_island"
ROOMS["port_phasmatys"]["desc"] += (" A barge creaks at the pier, chartered "
                                    "for Fossil Island ('fossil').")
REGIONS.update({"fossil_island": "Morytania", "lithkren_vault": "Morytania",
                "ungael_shore": "Morytania", "vorkath_crater": "Morytania"})
TRAVEL_HUBS["fossil island"] = "fossil_island"
TRAVEL_HUBS["fossil"] = "fossil_island"
TRAVEL_NAMES.append("Fossil Island")

# --- Dragon Slayer II (5 QP) --------------------------------------------------
ALL_QUESTS["dragon_slayer_2"] = "Dragon Slayer II"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["dragon_slayer_2"] = 5
NPC_NAMES["dragon_slayer_2"] = "Dallas Jones"
QUEST_STARTS["dragon_slayer_2"] = "Dallas Jones, Fossil Island (sail from " \
                                  "Port Phasmatys)"
QUEST_HINTS["dragon_slayer_2"] = {
    "relics": "slay the metal dragons in the Lithkren vault ('vault') "
              "until you hold 3 dragonkin relics, then see Dallas",
    "galvek": "face GALVEK on the shore of Ungael ('ungael')",
}


def talk_dallas(p):
    stage = _q(p, "dragon_slayer_2")
    if stage == "not_started":
        if _q(p, "dragon_slayer") != "complete":
            say("Dallas Jones: \"You slew Elvarg? No? Come back when you've "
                "finished DRAGON SLAYER — a novice has no business with the "
                "Dragonkin.\"", "byellow")
            return
        banner("Quest Start: Dragon Slayer II", color="purple",
               line_color="bmagenta")
        say("Dallas Jones: \"The Dragonkin built dragons to end us — and "
            "Galvek, their last, still sails the northern sea. His metal "
            "brood guards three RELICS in the vault below. Bring me three, "
            "and I'll show you how to sink him.\"")
        p.quests["dragon_slayer_2"] = "relics"
    elif stage == "relics":
        relics = p.count("dragonkin relic")
        if relics >= 3:
            p.take("dragonkin relic", 3)
            p.quests["dragon_slayer_2"] = "galvek"
            say("Dallas fits the relics together: \"There! Galvek's binding "
                "— it'll draw him to the surface off Ungael. Go, slayer. "
                "End what the Dragonkin began.\"", "byellow")
        else:
            say(f"Dallas Jones: \"{relics}/3 relics. The metal dragons of "
                "the vault ('vault') still hold the rest.\"")
    elif stage == "galvek":
        say("Dallas Jones: \"Galvek waits off the shore of Ungael "
            "('ungael'). Anti-dragon protection and a dragon-hunter weapon, "
            "if you have them.\"")
    elif stage == "complete":
        say("Dallas Jones: \"Vorkath sleeps in the crater on Ungael now the "
            "ward is down — and the undead thing drops treasures worth the "
            "terror. Mind the zombified spawn.\"")


QUEST_TALK["dragon_slayer_2"] = talk_dallas

# Galvek only breaches while the quest is at its final stage
QUEST_SPAWNS.append(("ungael_shore", "galvek",
                     lambda pl: _q(pl, "dragon_slayer_2") == "galvek"))


# --- quest-on-kill: relic drops, Galvek's fall, Vorkath's trophy --------------
_prev_quest_on_kill_ds2 = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811  (wraps prior)
    _prev_quest_on_kill_ds2(p, target)
    if _q(p, "dragon_slayer_2") == "relics" and target in _METAL_DRAGONS \
            and p.count("dragonkin relic") < 3:
        p.add("dragonkin relic")
        say(f"The {target} was clutching a DRAGONKIN RELIC! "
            f"({p.count('dragonkin relic')}/3)", "bmagenta", "bold")
    if target == "galvek" and _q(p, "dragon_slayer_2") == "galvek":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Dragon Slayer II", color="byellow",
               line_color="gold")
        say("Galvek sinks beneath the waves at last. Dallas was right — the "
            "Dragonkin ward over Ungael's crater fades, and something old "
            "stirs within. 25,000 attack and 25,000 defence xp awarded, and "
            "Dallas presses the DRAGON HUNTER LANCE into your hands.",
            "bgreen")
        p.gain_xp("attack", 25000)
        p.gain_xp("defence", 25000)
        p.add("dragon hunter lance")
        p.quests["dragon_slayer_2"] = "complete"


# relic item (quest token)
add_item("dragonkin relic", 0, members=True)
EFFECT_NOTES["dragonkin relic"] = ("a shard of Dragonkin work — Dallas "
                                   "Jones wants three")
