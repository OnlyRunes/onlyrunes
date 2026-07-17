

# ===========================================================================
#  THE NORTHERN ISLES  (Miscellania's kingdom & Lunar Isle's dream magic)
# ===========================================================================
# Two ships leave Rellekka's docks. One sails to MISCELLANIA, where ailing
# King Vargas will crown a helpful adventurer regent — and a regent can run
# the kingdom: fill the coffers, set the workers, and collect what the
# island produces while you adventure elsewhere. The other sails to LUNAR
# ISLE, where the Moonclan dream in shifts: pass their dream trial (a fight
# against yourself) and their ASTRAL ALTAR opens the LUNAR SPELLBOOK —
# Vengeance, Cure Me, Humidify, and the moonclan teleport.

# --- items -----------------------------------------------------------------------
add_item("astral rune", 120, members=True)
EFFECT_NOTES["astral rune"] = ("moonclan rune — fuels the lunar spellbook")
add_item("seal of passage", 2000, members=True)
EFFECT_NOTES["seal of passage"] = ("the Oneiromancer's mark — proof the "
                                   "dream did not keep you")

# --- Miscellania ---------------------------------------------------------------------
ROOMS.update({
    "miscellania": dict(name="Miscellania",
        desc="A green island kingdom of maple groves and fishing jetties. "
             "Subjects bustle about the little castle where KING VARGAS "
             "slumps on his throne, buried in paperwork ('talk'). Maples "
             "line the shore and tuna run deep off the jetty.",
        exits={"sail": "rellekka"},
        trees=["maple"], fish_tools=["harpoon"],
        npc="throne_of_miscellania", members=True),
})
ROOMS["rellekka"]["exits"]["misc"] = "miscellania"
ROOMS["rellekka"]["exits"]["moon"] = "lunar_isle"
ROOMS["rellekka"]["desc"] += (" Two ships ride at the dock: one flies "
                              "Miscellania's colours ('misc'), the other "
                              "the moon-sail of Lunar Isle ('moon').")
REGIONS.update({"miscellania": "Fremennik", "lunar_isle": "Fremennik",
                "dream_world": "Fremennik"})
TRAVEL_HUBS["miscellania"] = "miscellania"
TRAVEL_NAMES.append("Miscellania")

# --- Throne of Miscellania (2 QP) ----------------------------------------------------
ALL_QUESTS["throne_of_miscellania"] = "Throne of Miscellania"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["throne_of_miscellania"] = 2
NPC_NAMES["throne_of_miscellania"] = "King Vargas"
QUEST_STARTS["throne_of_miscellania"] = "King Vargas, Miscellania (sail " \
                                        "'misc' from Rellekka)"
QUEST_HINTS["throne_of_miscellania"] = {
    "favor": "win the islanders' favor: bring King Vargas 10 maple logs "
             "and 10 raw tuna (both from the island itself)",
}


def talk_vargas(p):
    stage = _q(p, "throne_of_miscellania")
    if stage == "not_started":
        banner("Quest Start: Throne of Miscellania", color="purple",
               line_color="bmagenta")
        say("King Vargas: \"I am unwell, adventurer, and my kingdom "
            "drifts. Show my people you can provide — TEN MAPLE LOGS and "
            "TEN RAW TUNA, from our own shores — and I will name you "
            "REGENT, with the kingdom's coffers at your command.\"")
        p.quests["throne_of_miscellania"] = "favor"
    elif stage == "favor":
        if p.has("maple logs", 10) and p.has("raw tuna", 10):
            p.take("maple logs", 10)
            p.take("raw tuna", 10)
            p.quests["throne_of_miscellania"] = "complete"
            p.kingdom = {"coffers": 0, "focus": "wood",
                         "at": getattr(p, "actions", 0)}
            show_art(ART_QUEST, "gold", center=True)
            banner("QUEST COMPLETE: Throne of Miscellania",
                   color="byellow", line_color="gold")
            say("The islanders cheer as Vargas names you REGENT OF "
                "MISCELLANIA. 10,000 woodcutting and 10,000 fishing xp "
                "awarded. The kingdom now works for you: 'kingdom' to "
                "rule it — deposit coins, set the focus, and 'collect' "
                "here for what your subjects gather while you're away.",
                "bgreen")
            p.gain_xp("woodcutting", 10000)
            p.gain_xp("fishing", 10000)
        else:
            say(f"King Vargas: \"Maple logs {p.count('maple logs')}/10, "
                f"raw tuna {p.count('raw tuna')}/10. The groves and the "
                "jetty are right outside, regent-to-be.\"")
    else:
        say("King Vargas: \"The kingdom prospers under your regency — "
            "'kingdom' to rule, 'collect' for the stores.\"")


QUEST_TALK["throne_of_miscellania"] = talk_vargas

# --- the kingdom: passive production on the action clock ----------------------------
_KINGDOM_YIELD = {"wood": "maple logs", "fish": "raw tuna",
                  "mining": "coal", "herbs": "grimy ranarr"}
_KINGDOM_COST = 75          # coins per work unit
_KINGDOM_RATE = 8           # actions per work unit
_KINGDOM_MAX_UNITS = 30     # stockpile cap per collection


def _kingdom_pending(p):
    k = getattr(p, "kingdom", None)
    if not k:
        return 0
    elapsed = max(0, getattr(p, "actions", 0) - k.get("at", 0))
    return min(elapsed // _KINGDOM_RATE, _KINGDOM_MAX_UNITS,
               k.get("coffers", 0) // _KINGDOM_COST)


def cmd_kingdom(p, arg):
    if _q(p, "throne_of_miscellania") != "complete" or \
            getattr(p, "kingdom", None) is None:
        say("You rule nothing — yet. King Vargas of Miscellania is "
            "looking for a regent. (sail 'misc' from Rellekka)", "grey")
        return
    k = p.kingdom
    a = arg.strip().lower().split()
    if a and a[0] == "deposit":
        amt = 0
        if len(a) > 1 and a[1].isdigit():
            amt = min(int(a[1]), p.count("coins"), 500_000 - k["coffers"])
        if amt <= 0:
            say("Deposit how much? 'kingdom deposit 5000' (coffers cap "
                "500,000).", "grey")
            return
        p.take("coins", amt)
        k["coffers"] += amt
        say(f"You fund the coffers with {amt:,} coins "
            f"(now {k['coffers']:,}).", "gold")
        return
    if a and a[0] in ("focus", "assign") and len(a) > 1 \
            and a[1] in _KINGDOM_YIELD:
        k["focus"] = a[1]
        say(f"The workers turn to {a[1]} — they'll gather "
            f"{_KINGDOM_YIELD[a[1]]}.", "bgreen")
        return
    pend = _kingdom_pending(p)
    banner("The Kingdom of Miscellania", color="gold", line_color="brown")
    print("  " + paint(f"Coffers: {k['coffers']:,} coins", "gold")
          + paint(f"   Focus: {k['focus']} ({_KINGDOM_YIELD[k['focus']]})",
                  "bgreen"))
    print("  " + paint(f"Ready to collect: {pend} load"
                       f"{'s' if pend != 1 else ''}", "bcyan")
          + paint("  ('collect' on Miscellania)", "grey"))
    say("Rule with: kingdom deposit <coins> | kingdom focus "
        "wood/fish/mining/herbs", "grey")


HANDLERS["kingdom"] = cmd_kingdom
HANDLERS["rule"] = cmd_kingdom

_prev_cmd_collect_misc = cmd_collect


def cmd_collect(p, _a):                              # noqa: F811 (wraps prior)
    if p.location == "miscellania" and \
            _q(p, "throne_of_miscellania") == "complete" and \
            getattr(p, "kingdom", None):
        k = p.kingdom
        units = _kingdom_pending(p)
        if units <= 0:
            say("The stores are bare — fund the coffers ('kingdom "
                "deposit'), then adventure a while: your subjects work "
                "as you do.", "grey")
            return
        item = _KINGDOM_YIELD[k["focus"]]
        qty = units * 2
        cost = units * _KINGDOM_COST
        k["coffers"] -= cost
        k["at"] = getattr(p, "actions", 0)
        p.add(item, qty)
        say(f"Your subjects present the harvest: {qty}x {item} "
            f"(wages: {cost:,} coins from the coffers).", "bgreen")
        if random.random() < 0.25:
            gem = random.choices(list(GEM_CUT), weights=[8, 5, 2, 1])[0]
            p.add(gem)
            say(f"A grateful islander adds an {gem} to the pile.", "bcyan")
        return
    _prev_cmd_collect_misc(p, _a)


HANDLERS["collect"] = cmd_collect

# --- Lunar Isle -------------------------------------------------------------------------
ROOMS.update({
    "lunar_isle": dict(name="Lunar Isle",
        desc="A pale island under a moon that never quite sets. The "
             "Moonclan drift between houses inlaid with astral script; "
             "the ONEIROMANCER studies you with eyes full of sleep "
             "('talk'). Their bank vault hums, their store sells starlit "
             "runes, and the ASTRAL ALTAR glows at the isle's heart "
             "('pray altar').",
        exits={"sail": "rellekka", "dream": "dream_world"},
        bank=True, shop="moonclan", prayer_altar=True,
        npc="lunar_diplomacy", members=True),
    "dream_world": dict(name="The Dream World",
        desc="A shifting nowhere of moonlit water and doorways that open "
             "onto themselves. Something waits in the middle distance, "
             "wearing your face.",
        exits={"wake": "lunar_isle"},
        members=True,
        qlock=("lunar_diplomacy", ["dream", "complete"],
               "Only those the Oneiromancer has steeped in dream-potion "
               "may sleep this deep. (Quest: Lunar Diplomacy)")),
})
SHOPS["moonclan"] = {"astral rune": 120, "law rune": 240,
                     "earth rune": 8, "water rune": 8, "cosmic rune": 150,
                     "death rune": 310}

# --- Lunar Diplomacy (2 QP) --------------------------------------------------------------
ALL_QUESTS["lunar_diplomacy"] = "Lunar Diplomacy"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # keep it last
QUEST_POINTS["lunar_diplomacy"] = 2
NPC_NAMES["lunar_diplomacy"] = "the Oneiromancer"
QUEST_STARTS["lunar_diplomacy"] = "the Oneiromancer, Lunar Isle (sail " \
                                  "'moon' from Rellekka)"
QUEST_HINTS["lunar_diplomacy"] = {
    "dream": "enter the Dream World ('dream') and defeat the one who "
             "wears your face",
}


def talk_oneiromancer(p):
    stage = _q(p, "lunar_diplomacy")
    if stage == "not_started":
        banner("Quest Start: Lunar Diplomacy", color="purple",
               line_color="bmagenta")
        say("The Oneiromancer: \"Outsider. Our magic is dreamt, not "
            "memorised — and no one wields it who has not faced the "
            "dreamer's trial. Sleep, and beat the only opponent who "
            "knows your every move: YOURSELF.\" She presses a warm "
            "potion into your hands and points to the dream door "
            "('dream').")
        p.quests["lunar_diplomacy"] = "dream"
    elif stage == "dream":
        say("The Oneiromancer: \"The dream waits ('dream'). You will "
            "know the opponent when you see them.\"")
    elif stage == "complete":
        say("The Oneiromancer: \"You out-dreamt yourself. The astral "
            "altar is open to you ('pray altar') — Vengeance suits you, "
            "I think.\"")


QUEST_TALK["lunar_diplomacy"] = talk_oneiromancer

# --- 'Me': the dream trial ------------------------------------------------------------
ME_ART = r"""
        .-''''''-.
       /  ______  \
      | |( .  . )| |       ME — it has your stance,
      | |   ..   | |        your scars, your grin.
      | | '----' | |
       \ \______/ /
        |_|    |_|
"""

ME_ATTACKS = [
    {"label": "your own favourite feint", "verb": "opens with",
     "color": ("bwhite", "bold"), "builder": _fx_jaws,
     "mult": 1.05, "w": 3, "atype": "slash"},
    {"label": "the spell you'd have cast", "verb": "counters with",
     "color": ("bmagenta", "bold"), "builder": _fx_bolt,
     "mult": 1.0, "w": 2, "atype": "magic"},
    {"label": "the arrow you didn't see", "verb": "looses",
     "color": ("bgreen", "bold"), "builder": _fx_bolt_blue,
     "mult": 0.95, "w": 2, "atype": "ranged"},
]


def _me_intro(name):
    return _fx((ME_ART, "grey", "dim"), (ME_ART, "bwhite"),
               (ME_ART, "bmagenta", "bold"))


def _me_death(name):
    return _fx((ME_ART, "bmagenta"), (ME_ART, "grey", "dim"))


_add_mob("me",
    {"abonus": 30, "atktype": ["slash", "magic", "ranged"], "att": 160,
     "cb": 314, "dstab": 70, "dslash": 70, "dcrush": 70, "dmagic": 70,
     "drange": 70, "def": 100, "hp": 220, "maxhit": 18, "str": 150,
     "weak": "crush"},
    [("astral rune", 10, 30, 1.0), ("coins", 4000, 12000, 1.0),
     ("grimy ranarr", 1, 4, 0.5)], members=True)
MONSTERS["me"]["boss"] = True
MONSTERS["me"]["rank"] = "boss"
_BOSSES.add("me")
BOSS_TURN["me"] = lambda p, m: _boss_take_turn(p, m, ME_ATTACKS)
BOSS_INTRO["me"] = _me_intro
BOSS_DEATH["me"] = _me_death
MONSTER_ART["me"] = ME_ART

QUEST_SPAWNS.append(("dream_world", "me",
                     lambda pl: _q(pl, "lunar_diplomacy") == "dream"))

# --- the lunar spellbook -------------------------------------------------------------
def _lunar_venge(p):
    if getattr(p, "venge", False):
        say("Vengeance already crackles around you.", "grey")
        return
    p.venge = True
    say("You raise your hand: the next blow that lands will REBOUND. "
        "\"Taste vengeance\" waits on your lips.", "bmagenta", "bold")


def _lunar_cure(p):
    if getattr(p, "poison", 0) > 0:
        p.poison = 0
        say("Moonlight washes the venom from your blood — cured.",
            "bcyan")
    else:
        say("Your blood is already clean.", "grey")


def _lunar_humidify(p):
    if p.count("waterskin") >= 12:
        say("You can't carry more water than that.", "grey")
        return
    p.add("waterskin", 4)
    say("Dew gathers from nothing — 4 waterskins condense into your "
        f"pack ({p.count('waterskin')} held).", "bblue")


SPELLS.update({
    "moonclan teleport": {"type": "tele", "dest": "lunar_isle", "lvl": 69,
                          "xp": 66, "book": "lunar",
                          "runes": {"astral rune": 2, "law rune": 1,
                                    "earth rune": 2}},
    "vengeance":  {"type": "lunar", "lvl": 62, "xp": 112, "book": "lunar",
                   "effect": _lunar_venge,
                   "runes": {"astral rune": 4, "death rune": 2,
                             "earth rune": 10}},
    "cure me":    {"type": "lunar", "lvl": 71, "xp": 69, "book": "lunar",
                   "effect": _lunar_cure,
                   "runes": {"astral rune": 2, "cosmic rune": 2}},
    "humidify":   {"type": "lunar", "lvl": 68, "xp": 65, "book": "lunar",
                   "effect": _lunar_humidify,
                   "runes": {"astral rune": 1, "water rune": 3,
                             "fire rune": 1}},
})


def _astral_altar(p):
    """Praying at Lunar Isle's altar swaps lunar <-> standard (post-quest)."""
    if _q(p, "lunar_diplomacy") != "complete":
        say("The astral altar hums, indifferent — the Moonclan do not "
            "share their dreams with strangers. (Quest: Lunar Diplomacy)",
            "grey")
        return
    book = getattr(p, "spellbook", "standard")
    p.spellbook = "lunar" if book != "lunar" else "standard"
    if p.spellbook == "lunar":
        say("The altar fills your mind with moonlit patterns — the LUNAR "
            "SPELLBOOK is yours (vengeance, cure me, humidify, moonclan "
            "teleport).", "bmagenta", "bold")
    else:
        say("The dream recedes; your STANDARD spellbook returns.",
            "bmagenta")


# --- kill hook: out-dream yourself ---------------------------------------------------
_prev_quest_on_kill_lunar = _quest_on_kill


def _quest_on_kill(p, target):                      # noqa: F811 (wraps prior)
    _prev_quest_on_kill_lunar(p, target)
    if target == "me" and _q(p, "lunar_diplomacy") == "dream":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Lunar Diplomacy", color="byellow",
               line_color="gold")
        say("Your double smiles your smile, bows your bow, and comes "
            "apart into moonlight. You wake holding a SEAL OF PASSAGE — "
            "and the astral altar's patterns suddenly make sense. "
            "15,000 magic xp awarded. ('pray altar' on Lunar Isle to "
            "take up the lunar spellbook.)", "bgreen")
        p.gain_xp("magic", 15000)
        p.add("seal of passage")
        p.add("astral rune", 30)
        p.quests["lunar_diplomacy"] = "complete"
