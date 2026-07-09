# ===========================================================================
#  XP / LEVELS  (Old School RuneScape curve)
# ===========================================================================

_XP_TABLE = [0] * 100  # _XP_TABLE[level] = xp required for that level
_pts = 0
for _lvl in range(1, 99):
    _pts += int(_lvl + 300 * (2 ** (_lvl / 7.0)))
    _XP_TABLE[_lvl + 1] = _pts // 4


def level_from_xp(xp):
    level = 1
    for lvl in range(1, 100):
        if _XP_TABLE[lvl] <= xp:
            level = lvl
        else:
            break
    return level


def xp_progress(xp):
    """Progress toward the next level for a skill's total xp.

    Returns (level, xp_into_level, xp_for_this_level, xp_to_next). At level 99
    the span/remaining are 0 (maxed)."""
    lvl = level_from_xp(xp)
    if lvl >= 99:
        return (99, 0, 0, 0)
    floor = _XP_TABLE[lvl]
    nxt = _XP_TABLE[lvl + 1]
    into = xp - floor
    span = nxt - floor
    return (lvl, into, span, nxt - xp)


SKILLS = [
    "attack", "strength", "defence", "hitpoints", "ranged", "prayer", "magic",
    "cooking", "woodcutting", "fishing", "firemaking", "crafting", "smithing",
    "mining", "runecrafting",
    # members skills
    "thieving", "agility", "slayer", "herblore", "fletching", "farming",
    "construction", "hunter",
]
MEMBERS_SKILLS = {"thieving", "agility", "slayer", "herblore", "fletching",
                  "farming", "construction", "hunter"}


