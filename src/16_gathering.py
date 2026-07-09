# ===========================================================================
#  GATHERING TABLES
# ===========================================================================
# tree: (product, level, xp)
TREES = {
    "tree":   ("logs", 1, 25),
    "oak":    ("oak logs", 15, 37),
    "willow": ("willow logs", 30, 67),
}
# rock: (product, level, xp)
ROCKS = {
    "copper": ("copper ore", 1, 17), "tin": ("tin ore", 1, 17),
    "clay": ("clay", 1, 5), "iron": ("iron ore", 15, 35),
    "silver": ("silver ore", 20, 40), "coal": ("coal", 30, 50),
    "gold": ("gold ore", 40, 65), "mithril": ("mithril ore", 55, 80),
    "adamantite": ("adamantite ore", 70, 95),
    "rune essence": ("rune essence", 1, 5),
}
# fishing spot tool -> [(product, level, xp), ...]
FISH = {
    "net": [("raw shrimp", 1, 10), ("raw anchovies", 15, 40)],
    "rod": [("raw sardine", 5, 20), ("raw herring", 10, 30), ("raw pike", 25, 60)],
    "fly": [("raw trout", 20, 50), ("raw salmon", 30, 70)],
}
# smelting: bar -> ({ores}, level, xp)
SMELT = {
    "bronze bar": ({"copper ore": 1, "tin ore": 1}, 1, 6),
    "iron bar": ({"iron ore": 1}, 15, 12),
    "silver bar": ({"silver ore": 1}, 20, 14),
    "steel bar": ({"iron ore": 1, "coal": 2}, 30, 17),
    "gold bar": ({"gold ore": 1}, 40, 22),
    "mithril bar": ({"mithril ore": 1, "coal": 4}, 50, 30),
    "adamant bar": ({"adamantite ore": 1, "coal": 6}, 70, 37),
}
# smithable item -> (bar type, bar count, smithing level)
SMITH_BARS = {"dagger": 1, "sword": 1, "scimitar": 2, "full helm": 2,
              "kiteshield": 3, "platelegs": 3, "platebody": 5}
SMITH_METAL_LVL = {"bronze": 1, "iron": 15, "steel": 30, "mithril": 50, "adamant": 70}
# runecrafting: rune -> (level, xp)
RUNECRAFT = {"air rune": (1, 5), "mind rune": (2, 5.5), "water rune": (5, 6),
             "earth rune": (9, 6.5), "fire rune": (14, 7), "body rune": (20, 7.5)}

# Prayers: name -> (level, drain_per_round, {boost pct}, protect_style)
# boosts are fractional bonuses to effective combat levels while active.
PRAYERS = {
    "thick skin":          (1,  0.15, {"defence": 0.05}, None),
    "burst of strength":   (4,  0.15, {"strength": 0.05}, None),
    "clarity of thought":  (7,  0.15, {"attack": 0.05}, None),
    "rock skin":           (10, 0.30, {"defence": 0.10}, None),
    "superhuman strength": (13, 0.30, {"strength": 0.10}, None),
    "improved reflexes":   (16, 0.30, {"attack": 0.10}, None),
    "steel skin":          (28, 0.60, {"defence": 0.15}, None),
    "ultimate strength":   (31, 0.60, {"strength": 0.15}, None),
    "incredible reflexes": (34, 0.60, {"attack": 0.15}, None),
    "protect from magic":  (37, 0.60, {}, "magic"),
    "protect from missiles": (40, 0.60, {}, "ranged"),
    "protect from melee":  (43, 0.60, {}, "melee"),
}

# Thieving pickpocket targets: name -> (level, xp, max_coins, fail_damage)
PICKPOCKET = {
    "man": (1, 8, 12, 1), "woman": (1, 8, 12, 1),
    "farmer": (10, 15, 30, 2), "guard": (40, 47, 60, 3),
}
# Agility: course-name -> (level, xp, fail_damage)
AGILITY_COURSE = (1, 8, 2)  # (min level, xp per lap, fall damage)

# Monsters a Slayer Master may assign (all reachable). Slayer xp per kill = hp.
SLAYER_TARGETS = ["goblin", "cow", "giant rat", "scorpion", "skeleton",
                  "zombie", "giant spider", "minotaur", "flesh crawler",
                  "barbarian", "hobgoblin", "guard", "hill giant"]
SLAYER_POINTS = {"easy": 3, "medium": 5, "hard": 8, "elite": 12}


