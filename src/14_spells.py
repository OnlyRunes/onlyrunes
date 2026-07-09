# ===========================================================================
#  SPELLS  (standard spellbook)
# ===========================================================================
# combat spells: max_hit + rune cost + magic level + xp
SPELLS = {
    "wind strike":  {"type": "combat", "max": 2, "lvl": 1,  "xp": 5.5,
                     "runes": {"air rune": 1, "mind rune": 1}},
    "water strike": {"type": "combat", "max": 4, "lvl": 5,  "xp": 7.5,
                     "runes": {"water rune": 1, "air rune": 1, "mind rune": 1}},
    "earth strike": {"type": "combat", "max": 6, "lvl": 9,  "xp": 9.5,
                     "runes": {"earth rune": 2, "air rune": 1, "mind rune": 1}},
    "fire strike":  {"type": "combat", "max": 8, "lvl": 13, "xp": 11.5,
                     "runes": {"fire rune": 3, "air rune": 2, "mind rune": 1}},
    "wind bolt":    {"type": "combat", "max": 9, "lvl": 17, "xp": 13.5,
                     "runes": {"air rune": 2, "chaos rune": 1}},
    "water bolt":   {"type": "combat", "max": 10, "lvl": 23, "xp": 16.5,
                     "runes": {"water rune": 2, "air rune": 2, "chaos rune": 1}},
    "earth bolt":   {"type": "combat", "max": 11, "lvl": 29, "xp": 19.5,
                     "runes": {"earth rune": 3, "air rune": 2, "chaos rune": 1}},
    "fire bolt":    {"type": "combat", "max": 12, "lvl": 35, "xp": 22.5,
                     "runes": {"fire rune": 4, "air rune": 3, "chaos rune": 1}},
    # utility
    "low alchemy":  {"type": "alch", "ratio": 0.4, "lvl": 21, "xp": 31,
                     "runes": {"fire rune": 3, "nature rune": 1}},
    "high alchemy": {"type": "alch", "ratio": 0.6, "lvl": 55, "xp": 65,
                     "runes": {"fire rune": 5, "nature rune": 1}},
    "lumbridge teleport": {"type": "tele", "dest": "lumbridge_castle", "lvl": 31,
                           "xp": 41, "runes": {"earth rune": 1, "air rune": 3, "law rune": 1}},
    "varrock teleport":   {"type": "tele", "dest": "varrock_square", "lvl": 25,
                           "xp": 35, "runes": {"fire rune": 1, "air rune": 3, "law rune": 1}},
    "falador teleport":   {"type": "tele", "dest": "falador_square", "lvl": 37,
                           "xp": 48, "runes": {"water rune": 1, "air rune": 3, "law rune": 1}},
}


