# ===========================================================================
#  THE WORLD PUSHES BACK  (ambushes, training focus, nests, ambience)
# ===========================================================================

# --- melee training focus ----------------------------------------------------
def cmd_train(p, arg):
    """Aim your melee xp: attack (accurate), strength (aggressive),
    defence (defensive), or shared."""
    want = arg.strip().lower()
    names = {"attack": "attack", "accurate": "attack",
             "strength": "strength", "aggressive": "strength",
             "str": "strength",
             "defence": "defence", "defensive": "defence", "def": "defence",
             "shared": "shared", "controlled": "shared", "all": "shared"}
    if not want:
        cur = getattr(p, "train", "shared")
        say(f"Melee training focus: {cur}. "
            "('train attack|strength|defence|shared' \u2014 ranged and magic "
            "train themselves)", "bcyan")
        return
    focus = names.get(want)
    if not focus:
        say("Train what? attack (accurate), strength (aggressive), "
            "defence (defensive), or shared.", "grey")
        return
    p.train = focus
    if focus == "shared":
        say("You balance your technique \u2014 melee xp is shared across "
            "attack, strength and defence.", "bcyan")
    else:
        say(f"You focus your technique \u2014 melee kills now train {focus}.",
            "bcyan")


HANDLERS["train"] = cmd_train
HANDLERS["focus"] = cmd_train

# --- bird's nests (woodcutting's little jackpot) --------------------------------
_NEST_LOOT = [("potato seed", 18), ("onion seed", 14), ("cabbage seed", 12),
              ("guam seed", 12), ("marrentill seed", 8), ("tarromin seed", 6),
              ("sweetcorn seed", 5), ("gold ring", 10), ("sapphire ring", 6),
              ("emerald ring", 4), ("ranarr seed", 3), ("watermelon seed", 2)]


def _birds_nest(p):
    prize = random.choices([i for i, _ in _NEST_LOOT],
                           weights=[w for _, w in _NEST_LOOT])[0]
    p.add(prize)
    print("  " + paint(f"\u2726 A bird's nest tumbles from the branches "
                       f"\u2014 inside: {prize}!", "gold", "bold"))


# --- hostile territory: some places attack YOU ----------------------------------
for _rm in ("wilderness_edge", "deep_wilderness", "chaos_temple",
            "wilderness_course", "varrock_sewers", "edgeville_dungeon",
            "stronghold_security", "members_dungeon", "taverley_dungeon",
            "melzars_maze", "icy_cavern", "draynor_manor",
            "black_knights_fortress", "mort_myre", "crandor",
            "karamja_volcano", "gwd_entrance", "bandos_stronghold",
            "armadyl_eyrie", "zamorak_fortress", "saradomin_encampment"):
    if _rm in ROOMS:
        ROOMS[_rm]["hostile"] = True


def _maybe_ambush(p):
    """Entering hostile ground can start a fight on THEIR terms. Strong
    adventurers get left alone (double a monster's level and it ignores
    you), and bosses never lurk."""
    r = ROOMS[p.location]
    if not r.get("hostile") or getattr(p, "combat", None) is not None:
        return
    if getattr(p, "auto", None) is not None:
        return
    cb = p.combat_level()
    lurkers = [m for m in _room_monsters(p)
               if not MONSTERS[m].get("boss")
               and (MONSTERS[m].get("level") or 1) * 2 >= cb
               and p.lvl("slayer") >= MONSTERS[m].get("slayer_req", 0)]
    if not lurkers or random.random() > 0.30:
        return
    m = random.choice(lurkers)
    say(f"\u26a0 Ambush! A {m} lunges at you from the shadows!",
        "bred", "bold")
    _start_combat(p, m)


# --- ambient flavour on the road --------------------------------------------------
REGION_AMBIENT = {
    "Wilderness": [
        "A cold wind drags ash across the wastes.",
        "Somewhere out in the grey, something howls.",
        "Old bones crunch underfoot.",
    ],
    "Morytania": [
        "The mist thickens, and the light gives up early here.",
        "Something watches from between the trees. It does not blink.",
        "A church bell tolls, far off and wrong.",
    ],
    "Karamja": [
        "Parrots shriek somewhere in the green.",
        "The volcano grumbles in its sleep.",
        "The air is thick enough to drink.",
    ],
    "AlKharid": [
        "Heat shimmers off the dunes.",
        "Sand hisses across the road.",
    ],
    "Kandarin": [
        "Bees drone through the long grass.",
        "A cart rattles by on the King's road.",
    ],
}


REGIONS.update({
    "giant_lair": "Edgeville", "mining_guild": "Falador",
    "crafting_guild": "Falador", "monastery": "Edgeville",
    "deep_wilderness": "Wilderness", "taverley": "Kandarin",
    "taverley_dungeon": "Kandarin", "white_wolf_mountain": "Kandarin",
    "catherby": "Kandarin", "seers_village": "Kandarin",
    "ardougne": "Kandarin", "brimhaven": "Karamja",
    "karamja_volcano": "Karamja", "crandor": "Crandor",
    "elvarg_lair": "Crandor",
})


def _ambient(p):
    lines = REGION_AMBIENT.get(REGIONS.get(p.location, ""))
    if lines and random.random() < 0.22:
        say(random.choice(lines), "grey")


