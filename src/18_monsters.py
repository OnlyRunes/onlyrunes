# ===========================================================================
#  MONSTERS
# ===========================================================================
def mob(hp, attack, defence, max_hit, drops, weak=None, members=False, boss=False):
    return {"hp": hp, "attack": attack, "defence": defence,
            "max_hit": max_hit, "drops": drops, "weak": weak,
            "members": members, "boss": boss}


# drops: list of (item, min, max, chance)
MONSTERS = {
    "chicken": mob(3, 1, 1, 1, [("bones", 1, 1, 1.0), ("feather", 5, 15, 1.0),
                                ("raw chicken", 1, 1, 1.0)]),
    "cow": mob(8, 1, 1, 1, [("bones", 1, 1, 1.0), ("cowhide", 1, 1, 1.0),
                            ("raw beef", 1, 1, 1.0)]),
    "goblin": mob(5, 1, 1, 2, [("bones", 1, 1, 1.0), ("coins", 1, 12, 0.7)]),
    "giant rat": mob(5, 1, 1, 1, [("bones", 1, 1, 1.0), ("raw beef", 1, 1, 0.5)]),
    "barbarian": mob(18, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.8),
                                   ("bronze sword", 1, 1, 0.1)]),
    "guard": mob(22, 9, 8, 3, [("bones", 1, 1, 1.0), ("coins", 10, 40, 0.9)]),
    "scorpion": mob(10, 4, 3, 2, [("bones", 1, 1, 0.0)]),
    "skeleton": mob(16, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 25, 0.6)]),
    "zombie": mob(16, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.6)]),
    "dark wizard": mob(14, 7, 5, 4, [("bones", 1, 1, 1.0), ("mind rune", 1, 5, 0.5),
                                     ("chaos rune", 1, 2, 0.2)]),
    "hobgoblin": mob(28, 14, 10, 4, [("bones", 1, 1, 1.0), ("coins", 10, 50, 0.8),
                                     ("iron arrow", 5, 10, 0.2)]),
    "hill giant": mob(35, 18, 14, 5, [("big bones", 1, 1, 1.0), ("coins", 20, 80, 0.9),
                                      ("steel platelegs", 1, 1, 0.05),
                                      ("limpwurt root", 1, 1, 0.12),
                                      ("grimy ranarr", 1, 1, 0.06),
                                      ("giant key", 1, 1, 0.05),
                                      ("law rune", 1, 3, 0.1)]),
    "count draynor": mob(30, 12, 8, 4, [("bones", 1, 1, 1.0)], weak="stake"),
    # --- additional monsters ---
    "giant spider": mob(16, 8, 5, 2, [("bones", 1, 1, 1.0), ("coins", 1, 15, 0.5)]),
    "dwarf": mob(14, 8, 6, 2, [("bones", 1, 1, 1.0), ("coins", 3, 25, 0.9)]),
    "minotaur": mob(18, 10, 7, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.9),
                                   ("iron arrow", 5, 15, 0.4)]),
    "flesh crawler": mob(22, 11, 7, 2, [("bones", 1, 1, 1.0), ("coins", 10, 45, 0.9),
                                        ("mind rune", 2, 6, 0.3)]),
    "thug": mob(20, 12, 6, 3, [("bones", 1, 1, 1.0), ("coins", 8, 40, 0.8)]),
    "dark warrior": mob(28, 16, 12, 4, [("bones", 1, 1, 1.0), ("coins", 15, 60, 0.9)]),
    "imp": mob(6, 3, 2, 1, [("bones", 1, 1, 0.0), ("red bead", 1, 1, 0.25),
                            ("yellow bead", 1, 1, 0.25), ("black bead", 1, 1, 0.25),
                            ("white bead", 1, 1, 0.25), ("coins", 1, 8, 0.4)]),
    "man": mob(7, 1, 1, 1, [("bones", 1, 1, 1.0), ("coins", 1, 12, 0.8)]),
    "chicken farmer": mob(7, 1, 1, 1, [("bones", 1, 1, 1.0), ("coins", 1, 10, 0.7)]),
    "zombie rat": mob(6, 2, 1, 1, [("bones", 1, 1, 1.0)]),
    # --- members monsters (gated behind membership) ---
    "moss giant": mob(60, 24, 18, 6, [("big bones", 1, 1, 1.0), ("coins", 20, 120, 0.9),
                                      ("mithril sword", 1, 1, 0.06),
                                      ("grimy harralander", 1, 1, 0.12),
                                      ("grimy ranarr", 1, 1, 0.08),
                                      ("nature rune", 2, 6, 0.2)], members=True),
    "ice giant": mob(70, 28, 22, 8, [("big bones", 1, 1, 1.0), ("coins", 30, 150, 0.9),
                                     ("adamant arrow", 5, 15, 0.2)], members=True),
    "lesser demon": mob(79, 32, 24, 8, [("ashes", 1, 1, 1.0), ("coins", 30, 180, 0.9),
                                        ("rune full helm", 1, 1, 0.03),
                                        ("law rune", 2, 8, 0.2)], members=True),
    "greater demon": mob(87, 36, 26, 9, [("ashes", 1, 1, 1.0), ("coins", 40, 220, 0.9),
                                         ("rune kiteshield", 1, 1, 0.02)], members=True),
    "king black dragon": mob(240, 60, 40, 25, [("big bones", 1, 1, 1.0),
                             ("coins", 500, 3000, 1.0), ("rune platebody", 1, 1, 0.15),
                             ("dragon med helm", 1, 1, 0.05),
                             ("ranarr seed", 1, 3, 0.3)], members=True, boss=True),
    "obor": mob(120, 30, 22, 12, [("big bones", 1, 1, 1.0),
                ("coins", 200, 1200, 1.0), ("hill giant club", 1, 1, 0.10),
                ("grimy ranarr", 2, 4, 0.6), ("limpwurt root", 2, 5, 0.6),
                ("law rune", 3, 8, 0.4)], boss=True),
}

# Difficulty rank per monster (drives auto-kill caps). Bosses set below.
MONSTER_RANK = {
    # easy
    "chicken": "easy", "cow": "easy", "goblin": "easy", "giant rat": "easy",
    "man": "easy", "zombie rat": "easy", "imp": "easy",
    # medium
    "scorpion": "medium", "giant spider": "medium", "dwarf": "medium",
    "minotaur": "medium", "barbarian": "medium", "thug": "medium",
    "skeleton": "medium", "zombie": "medium", "dark wizard": "medium",
    "flesh crawler": "medium",
    # hard
    "guard": "hard", "hobgoblin": "hard", "dark warrior": "hard",
    "hill giant": "hard",
    # elite
    "moss giant": "elite", "ice giant": "elite", "lesser demon": "elite",
    "greater demon": "elite",
}
_BOSSES = {"king black dragon", "count draynor", "obor"}
for _name, _m in MONSTERS.items():
    _m["rank"] = "boss" if _name in _BOSSES else MONSTER_RANK.get(_name, "medium")
    if _name in _BOSSES:
        _m["boss"] = True

# How many of each rank you may auto-fight in one go. Bosses: none.
RANK_CAP = {"easy": 30, "medium": 20, "hard": 10, "elite": 5}
RANK_COLOR = {"easy": "bgreen", "medium": "byellow", "hard": "orange",
              "elite": "bred", "boss": "bmagenta"}


