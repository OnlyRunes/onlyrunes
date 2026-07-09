# ===========================================================================
#  REGIONAL GAP-FILL  (the world's completed regions get their missing bits)
# ===========================================================================

# --- Pickables (data-driven 'pick') ------------------------------------------
add_item("banana", 2, heal=2)
ROOMS["lumbridge_farm"]["pick"] = ["grain"]
ROOMS["draynor_village"]["pick"] = ["grain"]
ROOMS["karamja_port"]["pick"] = ["banana"]
ROOMS["karamja_port"]["desc"] += " Banana palms sway overhead."
ROOMS["seers_village"]["pick"] = ["flax"]
ROOMS["seers_village"]["desc"] += " A blue flax field ripples south of town."
ROOMS["falador_east"]["pick"] = ["cabbage"]
ROOMS["falador_east"]["desc"] += " The famous cabbage patch grows by the wall."
BATCHABLE.add("pick")

# --- Fishing spots the regions were missing -----------------------------------
ROOMS["draynor_village"]["fish_tools"] = ["net"]
ROOMS["draynor_village"]["desc"] += " Fishing spots bubble along the riverbank."
ROOMS["karamja_port"]["fish_tools"] = ["net", "rod", "cage", "harpoon"]
ROOMS["karamja_port"]["desc"] += (" The dock heaves with lobster pots and "
                                  "harpoon fishers.")

# --- Edgeville's famous yews ----------------------------------------------------
ROOMS["edgeville"]["trees"] = ["yew"]
ROOMS["edgeville"]["desc"] += " A stand of old yews grows south of the bank."

# --- The Wilderness gets its green dragons + the Chaos Temple -------------------
ROOMS["deep_wilderness"]["monsters"].append("green dragon")
ROOMS["deep_wilderness"]["desc"] += (" Green dragons wheel over the blasted "
                                     "ground.")
ROOMS.update({
    "chaos_temple": dict(name="Chaos Temple",
        desc="A ruined shrine to the god of chaos, deep in the wastes. "
             "Burying bones at its blood-stained altar honours something "
             "hungry. (bones buried here give +50% prayer xp)",
        exits={"south": "deep_wilderness"},
        prayer_altar=True, chaos_altar=True, monsters=["dark wizard"]),
})
ROOMS["deep_wilderness"]["exits"]["temple"] = "chaos_temple"
REGIONS["chaos_temple"] = "Wilderness"

# --- The Giant Mole beneath Falador Park -----------------------------------------
add_item("mole claw", 3500)
add_item("mole skin", 1500)

MOLE_ART = r'''
        ______________
       /  .-.    .-.  \
      |  ( o )  ( o )  |__
      |   `-'.--.`-'   |  \__
       \    (####)    /  \/..\
     ___\__ `~~~~' __/____\/\/
    /_/\_\/_______\/_/\_\_\/
'''


def _mole_intro(name):
    return [_tint(MOLE_ART, "brown"), _tint(MOLE_ART, "byellow"),
            _tint(MOLE_ART, "brown", "bold")]


def _mole_death(name):
    return [_tint(MOLE_ART, "brown"), _tint(MOLE_ART, "grey", "dim")]


def _mole_dirt(p, m, dmg):
    p.stat_drain["attack"] = p.stat_drain.get("attack", 0) + 2
    print("  " + paint("Dirt sprays into your eyes! (-2 attack)", "bblue"))


MOLE_ATTACKS = [
    {"label": "a raking claw swipe", "verb": "lashes out with",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(MOLE_ART, "brown", "bold")],
     "mult": 1.2, "w": 4, "atype": "slash"},
    {"label": "a spray of blinding dirt", "verb": "kicks up",
     "color": ("byellow",),
     "builder": lambda: [_tint(MOLE_ART, "byellow")],
     "mult": 0.8, "w": 2, "atype": "ranged", "effect": _mole_dirt},
    {"label": "a burrowing charge from below", "verb": "erupts in",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(MOLE_ART, "brown")],
     "mult": 1.4, "w": 2, "atype": "crush"},
]


def _mole_take_turn(p, m):
    if m["cur"] < m["hp"] and random.random() < 0.2:
        heal = random.randint(8, 15)
        m["cur"] = min(m["hp"], m["cur"] + heal)
        say("The Giant Mole burrows away in a spray of soil... and "
            f"resurfaces, refreshed. (+{heal})", "brown")
        return None
    return _boss_take_turn(p, m, MOLE_ATTACKS)


_add_mob("giant mole",
    {"abonus": 10, "atktype": ["slash", "crush"], "att": 60, "cb": 90,
     "dstab": 30, "dslash": 40, "dcrush": 40, "dmagic": 20, "drange": 40,
     "def": 60, "hp": 120, "maxhit": 12, "str": 70, "weak": "stab"},
    [("big bones", 1, 1, 1.0), ("mole claw", 1, 1, 1.0),
     ("mole skin", 1, 3, 1.0), ("coins", 200, 1500, 0.9)], rank="boss")
MONSTERS["giant mole"]["boss"] = True
_BOSSES.add("giant mole")
BOSS_INTRO["giant mole"] = _mole_intro
BOSS_DEATH["giant mole"] = _mole_death
BOSS_TURN["giant mole"] = _mole_take_turn
MONSTER_ART["giant mole"] = MOLE_ART

ROOMS.update({
    "falador_park": dict(name="Falador Park",
        desc="A tidy garden of hedges and flowerbeds — ruined by an "
             "enormous molehill in the lawn. ('dig' it, if you dare)",
        exits={"south": "falador_square"}),
    "mole_lair": dict(name="Mole Lair",
        desc="A vast earthen warren beneath the park. Something huge moves "
             "in the dark, showering soil from the ceiling.",
        exits={"up": "falador_park"},
        monsters=["giant mole"], dig_entry=True),
})
ROOMS["falador_square"]["exits"]["park"] = "falador_park"
ROOMS["falador_square"]["desc"] += " Falador Park lies north ('park')."
REGIONS.update({"falador_park": "Falador", "mole_lair": "Falador"})


# ===========================================================================
#  SKILLING EXPANSION III  (high runecrafting, wilderness agility, slayer
#  rewards)
# ===========================================================================

# --- High runecrafting altars -------------------------------------------------
RUNECRAFT.update({"chaos rune": (35, 8.5), "nature rune": (44, 9),
                  "law rune": (54, 9.5), "death rune": (65, 10)})
ROOMS["chaos_temple"]["altar"] = "chaos"     # the temple earns its name
ROOMS["chaos_temple"]["desc"] += (" The blood-stained altar also binds "
                                  "essence into chaos runes ('craftrune').")
ROOMS.update({
    "nature_altar": dict(name="Nature Altar",
        desc="A living shrine deep in the Karamja jungle, vines coiling "
             "over ancient stone. ('craftrune' with rune essence)",
        exits={"out": "brimhaven"}, altar="nature", members=True),
    "law_altar": dict(name="Law Altar",
        desc="A wind-swept holy islet off Catherby's shore, humming with "
             "order. ('craftrune' with rune essence)",
        exits={"boat": "catherby"}, altar="law", members=True),
    "death_altar": dict(name="Death Altar",
        desc="A lightless crypt beneath Paterdomus where the air itself "
             "feels thin. ('craftrune' with rune essence)",
        exits={"up": "paterdomus"}, altar="death", members=True,
        qlock=("priest_in_peril", ("complete",),
               "Drezel bars the crypt stair. (Quest: Priest in Peril)")),
})
ROOMS["brimhaven"]["exits"]["altar"] = "nature_altar"
ROOMS["brimhaven"]["desc"] += " A vine-choked shrine glows in the jungle ('altar')."
ROOMS["catherby"]["exits"]["islet"] = "law_altar"
ROOMS["catherby"]["desc"] += " A ferryman poles out to a holy islet ('islet')."
ROOMS["paterdomus"]["exits"]["crypt"] = "death_altar"
REGIONS.update({"nature_altar": "Karamja", "law_altar": "Kandarin",
                "death_altar": "Morytania"})

# --- Wilderness agility course (level 52; great xp, real teeth) ---------------
ROOMS.update({
    "wilderness_course": dict(name="Wilderness Agility Course",
        desc="A gauntlet of rope swings and log balances strung over a "
             "ravine in the wastes. Only the sure-footed survive. "
             "('agility' to run a lap)",
        exits={"south": "deep_wilderness"},
        agility_course=(52, 48, 9)),
})
ROOMS["deep_wilderness"]["exits"]["course"] = "wilderness_course"
ROOMS["deep_wilderness"]["desc"] += (" Ropes and logs of an agility course "
                                     "sway over a ravine ('course').")
REGIONS["wilderness_course"] = "Wilderness"

# --- Slayer rewards (Vannaka trades slayer points) ------------------------------
add_item("slayer helmet", 50000, members=True, equip={
    "dstab": 30, "dslash": 32, "dcrush": 27, "dmagic": -1, "drange": 30,
    "slot": "head", "req": {"defence": 10}})

SLAYER_REWARDS = {
    "slayer helmet": (60, "a snarling helmet: +15% accuracy & damage "
                          "against your slayer task"),
    "slayer tome": (25, "Vannaka's teachings: +2,500 slayer xp, instantly"),
    "task skip": (8, "abandon your current task and get a fresh one"),
}


def cmd_slayerbuy(p, arg):
    if not getattr(p, "members", False):
        say("Slayer is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    if p.location != "edgeville":
        say("Vannaka trades slayer points in Edgeville.", "grey")
        return
    want = arg.strip().lower()
    if not want:
        banner("Slayer Rewards", color="teal", line_color="teal")
        print("  " + paint(f"Your points: {p.slayer_points}", "white"))
        for name, (cost, desc) in SLAYER_REWARDS.items():
            print(f"  {name:14} " + paint(f"{cost:>3} pts", "teal")
                  + "  " + paint(desc, "grey"))
        say("  Buy with 'slayerbuy <reward>'.", "grey")
        return
    name = next((n for n in SLAYER_REWARDS if want in n), None)
    if not name:
        say("Vannaka doesn't trade that. ('slayerbuy' lists rewards.)", "grey")
        return
    cost, _desc = SLAYER_REWARDS[name]
    if p.slayer_points < cost:
        say(f"You need {cost} slayer points ({p.slayer_points} held). "
            "Complete tasks to earn more.", "byellow")
        return
    if name == "task skip" and not getattr(p, "slayer_task", None):
        say("You have no task to skip — see Vannaka ('talk').", "grey")
        return
    p.slayer_points -= cost
    if name in ("earmuffs", "mirror shield", "rock hammer"):
        p.add(name)
        say(f"Vannaka hands over the {name}. Use it well.", "teal")
        return
    if name == "slayer helmet":
        p.add("slayer helmet")
        say("Vannaka hands you a snarling SLAYER HELMET. Wear it on task "
            "and strike true.", "teal", "bold")
    elif name == "slayer tome":
        say("You absorb Vannaka's hard-won knowledge.", "teal")
        p.gain_xp("slayer", 2500)
    elif name == "task skip":
        p.slayer_task = None
        p.task_streak = 0
        say("Vannaka waves the task away. 'Talk' to me for a new one.",
            "teal")


HANDLERS["slayerbuy"] = cmd_slayerbuy
HANDLERS["rewards"] = cmd_slayerbuy


# ===========================================================================
#  INTERFACE REFINEMENTS  (character dashboard + item effect notes)
# ===========================================================================
def cmd_me(p, _a):
    """One-screen character dashboard."""
    banner(f"{p.name} — Combat level {p.combat_level()}", color="gold")
    total = sum(p.lvl(s) for s in SKILLS)
    txp = sum(p.skills[s] for s in SKILLS)
    done = sum(1 for k in ALL_QUESTS if _q(p, k) == "complete")
    ach = len(getattr(p, "achievements", []))
    bosses = getattr(p, "bosses", [])
    bank_val = sum(ITEMS.get(i, {}).get("value", 0) * q
                   for i, q in p.bank.items())
    task = getattr(p, "slayer_task", None)
    task_str = (f"  ·  task: {task['remaining']}/{task['amount']} "
                f"{task['monster']}s" if task and task.get("remaining")
                else "")
    rows = [
        ("Total level", f"{total}   ({txp:,} xp)"),
        ("Quests", f"{done}/{len(ALL_QUESTS)} complete  ·  "
                   f"{quest_points(p)} quest points"),
        ("Achievements", f"{ach}/{len(ACHIEVEMENTS)} unlocked"),
        ("Combat", f"{getattr(p, 'kills', 0):,} kills  ·  "
                   f"{len(bosses)}/{len(_BOSSES)} bosses slain"),
        ("Slayer", f"level {p.lvl('slayer')}  ·  "
                   f"{p.slayer_points} points{task_str}"),
        ("Barrows", f"{getattr(p, 'barrows_loots', 0)} chest(s) looted"),
        ("Wealth", f"{p.coins:,} coins held  ·  bank worth ~{bank_val:,} gp"),
        ("Location", ROOMS[p.location]["name"]
                     + ("  ·  member" if p.members else "")),
    ]
    for k, v in rows:
        print("  " + paint(f"{k:13}", "byellow") + paint(v, "white"))
    if bosses:
        say("  Bosses: " + ", ".join(sorted(bosses)), "grey")
    print("  " + paint("Next up      ", "bcyan", "bold")
          + paint(_next_goal(p), "bcyan"))
    say("  ('stats' for skills, 'quests', 'achievements', 'bestiary')", "grey")


HANDLERS["me"] = cmd_me
HANDLERS["character"] = cmd_me
HANDLERS["profile"] = cmd_me

