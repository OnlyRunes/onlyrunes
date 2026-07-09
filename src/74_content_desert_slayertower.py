# ===========================================================================
#  THE KHARIDIAN DESERT  (heat, thieves, the Duel Arena, and the Queen)
# ===========================================================================
# South through the Shantay Pass the sun becomes a monster: carry waterskins
# or burn. Pollnivneach fences stolen goods, Nardah's fountain restores the
# faithful, gamblers stake coins at the Duel Arena — and beneath the sands,
# the Kalphite Queen waits in two bodies.

add_item("waterskin", 10)
add_item("kebab", 12, heal=6)

SHOPS["shantay"] = {"waterskin": 10, "knife": 6, "bread": 12}
SHOPS["kebab"] = {"kebab": 12, "waterskin": 12}

PICKPOCKET["menaphite thug"] = (65, 137, 140, 5)

_add_mob("desert bandit",
    {"abonus": 10, "atktype": ["slash"], "att": 40, "cb": 41, "dstab": 15,
     "dslash": 15, "dcrush": 15, "dmagic": 10, "drange": 15, "def": 30,
     "hp": 40, "maxhit": 6, "str": 40, "weak": "crush"},
    [("coins", 20, 180, 0.9), ("waterskin", 1, 2, 0.3)],
    members=True, rank="medium")

_add_mob("kalphite worker",
    {"abonus": 5, "atktype": ["crush"], "att": 25, "cb": 28, "dstab": 20,
     "dslash": 20, "dcrush": 10, "dmagic": 15, "drange": 20, "def": 22,
     "hp": 32, "maxhit": 4, "str": 25, "weak": "crush"},
    [("coins", 10, 80, 0.7), ("waterskin", 1, 1, 0.1)],
    members=True, rank="medium")

_add_mob("kalphite soldier",
    {"abonus": 20, "atktype": ["crush"], "att": 75, "cb": 85, "dstab": 45,
     "dslash": 45, "dcrush": 25, "dmagic": 35, "drange": 45, "def": 60,
     "hp": 90, "maxhit": 12, "str": 80, "weak": "crush"},
    [("coins", 80, 400, 0.9), ("mithril bar", 1, 1, 0.1)],
    members=True, rank="elite")

# --- the Queen: two bodies, one grudge ------------------------------------------
KQ_ART = r"""
       \_          _/
        \ \__    __/ /
     ____\/##\==/##\/____
    <=((  \(@)==(@)/  ))=>
        \_/|/    \|\_/
      _/  /|      |\  \_
     <__ / |______| \ __>
"""


def _kq_intro(name):
    return [_tint(KQ_ART, "brown"), _tint(KQ_ART, "byellow", "bold"),
            _tint(KQ_ART, "orange", "bold")]


def _kq_death(name):
    return [_tint(KQ_ART, "orange"), _tint(KQ_ART, "grey", "dim")]


KQ_ATTACKS = [
    {"label": "her scything mandibles", "verb": "snaps with",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(KQ_ART, "byellow", "bold")],
     "mult": 1.2, "w": 3, "atype": "crush"},
    {"label": "a hail of hardened chitin", "verb": "flings",
     "color": ("brown",),
     "builder": lambda: [_tint(KQ_ART, "brown")],
     "mult": 1.0, "w": 2, "atype": "ranged"},
    {"label": "a crackling bolt of hive-magic", "verb": "spits",
     "color": ("bmagenta", "bold"),
     "builder": lambda: [_tint(KQ_ART, "bmagenta", "bold")],
     "mult": 1.1, "w": 2, "atype": "magic"},
]

_add_mob("kalphite queen",
    {"abonus": 35, "atktype": ["crush", "ranged", "magic"], "att": 150,
     "cb": 333, "dstab": 70, "dslash": 70, "dcrush": 50, "dmagic": 60,
     "drange": 70, "def": 85, "hp": 255, "maxhit": 22, "str": 150,
     "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 3000, 12000, 1.0),
     ("dragon chainbody", 1, 1, 0.04), ("uncut diamond", 1, 2, 0.15),
     ("grimy ranarr", 1, 3, 0.3), ("waterskin", 2, 4, 0.5)], members=True)
MONSTERS["kalphite queen"]["boss"] = True
MONSTERS["kalphite queen"]["rank"] = "boss"
MONSTERS["kalphite queen"]["carapace"] = True
MONSTERS["kalphite queen"]["transform"] = True
MONSTERS["kalphite queen"]["transform_flies"] = True
_BOSSES.add("kalphite queen")
BOSS_INTRO["kalphite queen"] = _kq_intro
BOSS_DEATH["kalphite queen"] = _kq_death
BOSS_TURN["kalphite queen"] = lambda p, m: _boss_take_turn(p, m, KQ_ATTACKS)
MONSTER_ART["kalphite queen"] = KQ_ART

# --- the region -------------------------------------------------------------------
ROOMS.update({
    "shantay_pass": dict(name="Shantay Pass",
        desc="The gate to the Kharidian Desert. Shantay eyes your pack: "
             "'Waterskins, friend. The sun out there is a murderer.'",
        exits={"north": "al_kharid_square", "south": "desert_road"},
        shop="shantay", desert=True, members=True),
    "desert_road": dict(name="Kharidian Dunes",
        desc="An ocean of sand rolling south. Bandits shadow the caravan "
             "routes, and something vast has tunnelled under the western "
             "dunes ('hive').",
        exits={"north": "shantay_pass", "south": "pollnivneach",
               "hive": "kalphite_hive"},
        monsters=["desert bandit", "scorpion"], hostile=True, desert=True,
        members=True),
    "pollnivneach": dict(name="Pollnivneach",
        desc="A lawless town of thieves and kebab smoke, halfway to "
             "nowhere. Menaphite thugs swagger between the tents — light "
             "fingers could live well here.",
        exits={"north": "desert_road", "south": "nardah"},
        pickpocket=["menaphite thug", "man"], shop="kebab", desert=True,
        members=True),
    "nardah": dict(name="Nardah",
        desc="A shrine town at the desert's edge, built around a holy "
             "fountain said to wash away any weariness ('pray altar').",
        exits={"north": "pollnivneach"},
        bank=True, prayer_altar=True, desert=True, members=True),
    "kalphite_hive": dict(name="Kalphite Hive",
        desc="A honeycomb of waxy tunnels breathing hot, sweet air. "
             "Workers boil out of the dark, and a deeper shaft descends "
             "('down').",
        exits={"out": "desert_road", "down": "kq_lair"},
        monsters=["kalphite worker", "kalphite soldier"], hostile=True,
        desert=True, members=True),
    "kq_lair": dict(name="The Queen's Chamber",
        desc="The heart of the hive. THE KALPHITE QUEEN towers over her "
             "eggs, carapace glinting like wet amber.",
        exits={"up": "kalphite_hive"},
        monsters=["kalphite queen"], desert=True, members=True),
    "duel_arena": dict(name="Duel Arena",
        desc="A colosseum of hot sandstone east of Al Kharid. The "
             "Duelmaster takes stakes and the crowd takes sides. "
             "('duel <coins>' to fight under the rules of the house)",
        exits={"west": "al_kharid_square"},
        npc="duelmaster", desert=True, members=True),
})
ROOMS["al_kharid_square"]["exits"]["south"] = "shantay_pass"
ROOMS["al_kharid_square"]["exits"]["arena"] = "duel_arena"
ROOMS["al_kharid_square"]["desc"] += (" The Shantay Pass opens south, and "
                                      "the Duel Arena roars east ('arena').")
for _rm in ("shantay_pass", "desert_road", "pollnivneach", "nardah",
            "kalphite_hive", "kq_lair", "duel_arena"):
    REGIONS[_rm] = "AlKharid"
TRAVEL_HUBS["pollnivneach"] = "pollnivneach"
TRAVEL_NAMES.append("Pollnivneach")

# the Nardah fountain washes away everything
def _nardah_blessing(p):
    p.hp = p.max_hp
    p.poison = 0
    p.stat_drain = {}


# --- the Duel Arena -----------------------------------------------------------------
_add_mob("arena duelist",
    {"abonus": 15, "atktype": ["slash"], "att": 60, "cb": 70, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 25, "drange": 30, "def": 50,
     "hp": 70, "maxhit": 9, "str": 60, "weak": "crush"},
    [], members=True, rank="hard")

DUEL_RULES = ["no food", "no prayer", "no specials", "anything goes"]


def talk_duelmaster(p):
    say("Duelmaster: \"Stake your coins and fight my champions \u2014 "
        "matched to your measure, under the rules of the house. Win and "
        "I pay DOUBLE. 'duel <coins>' (minimum 100). Lose \u2014 or "
        "yield \u2014 and the stake is mine.\"", "gold")


QUEST_TALK["duelmaster"] = talk_duelmaster
NPC_NAMES["duelmaster"] = "the Duelmaster"


def cmd_duel(p, arg):
    if not getattr(p, "members", False):
        say("The Duel Arena is members-only. Type 'membership'.", "bmagenta")
        return
    if p.location != "duel_arena":
        say("The Duel Arena is east of Al Kharid.", "grey")
        return
    if getattr(p, "combat", None) is not None:
        say("You're already fighting!", "bred")
        return
    try:
        stake = int(arg.strip().split()[0])
    except (ValueError, IndexError):
        say("Stake how much? 'duel 500' (minimum 100 coins).", "bcyan")
        return
    if stake < 100:
        say("The Duelmaster sneers: \"Minimum stake is 100 coins.\"",
            "grey")
        return
    if not p.has("coins", stake):
        say(f"You don't have {stake:,} coins to stake.", "byellow")
        return
    p.take("coins", stake)
    rule = random.choice(DUEL_RULES)
    p.duel = {"stake": stake, "rule": rule}
    banner("DUEL!", color="gold", line_color="gold")
    say(f"Stake: {stake:,} coins.  House rule: {rule.upper()}.",
        "gold", "bold")
    _start_combat(p, "arena duelist")
    # the house matches champions to your measure
    m = p.combat
    cb = p.combat_level()
    m["attack"] = max(20, int(cb * 0.9))
    m["defence"] = max(15, int(cb * 0.7))
    m["max_hit"] = max(4, cb // 9)
    m["hp"] = m["cur"] = max(40, p.max_hp - 10)
    m["level"] = cb


def _duel_loss(p):
    duel = getattr(p, "duel", None)
    p.duel = None
    p.combat = None
    _clear_status(p)
    p.hp = max(p.hp, 1)
    stake = duel["stake"] if duel else 0
    say(f"The Duelmaster collects your stake of {stake:,} coins. The "
        "medics drag you out \u2014 beaten, breathing, and poorer.",
        "byellow")
    p.location = "duel_arena"
    return True


HANDLERS["duel"] = cmd_duel


# ===========================================================================
#  THE SLAYER TOWER & SLAYER OVERHAUL
# ===========================================================================
# Three floors of horrors over Canifis, each gated by slayer level, several
# demanding the right counter-gear. Masters now come in tiers: Turael
# (Taverley, gentle), Vannaka (Edgeville, standard), Duradel (Brimhaven,
# brutal). Task streaks pay bonus points at every 5th and 10th task.

# --- counter-gear -------------------------------------------------------------
add_item("earmuffs", 200, members=True, equip={
    "dstab": 1, "dslash": 1, "dcrush": 1, "slot": "head"})
add_item("mirror shield", 5000, members=True, equip={
    "dstab": 20, "dslash": 22, "dcrush": 20, "dmagic": 25, "drange": 22,
    "slot": "shield", "req": {"defence": 20}})
add_item("rock hammer", 500, members=True, tool="rock hammer")

SLAYER_REWARDS.update({
    "earmuffs": (5, "blocks a banshee's mind-splitting scream"),
    "mirror shield": (15, "turns a basilisk's gaze back on itself"),
    "rock hammer": (10, "shatters a dying gargoyle before it reforms"),
})


def _has_slayer_helm(p):
    return p.equipment.get("head") == "slayer helmet"


def _banshee_scream(p, m, dmg):
    if _has_slayer_helm(p) or p.equipment.get("head") == "earmuffs":
        return
    for s in ("attack", "strength"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 2
    print("  " + paint("The banshee's SCREAM splits your mind! (-2 attack & "
                       "strength \u2014 earmuffs would block it)", "bblue"))


def _basilisk_gaze(p, m, dmg):
    if p.equipment.get("shield") == "mirror shield":
        return
    for s in ("attack", "defence"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 3
    print("  " + paint("You meet the basilisk's gaze! (-3 attack & defence "
                       "\u2014 a mirror shield would protect you)", "bblue"))


def _spectre_stench(p, m, dmg):
    if _has_slayer_helm(p):
        return
    for s in ("attack", "strength", "defence"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 3
    print("  " + paint("The spectre's stench sears your lungs! (-3 combat "
                       "stats \u2014 a slayer helmet would seal it out)",
                       "bblue"))


MONSTER_EFFECTS["banshee"] = _banshee_scream
MONSTER_EFFECTS["basilisk"] = _basilisk_gaze
MONSTER_EFFECTS["aberrant spectre"] = _spectre_stench

# --- the tower's residents -----------------------------------------------------
_add_mob("crawling hand",
    {"abonus": 0, "atktype": ["crush"], "att": 8, "cb": 8, "dstab": 0,
     "dslash": 0, "dcrush": 0, "dmagic": 0, "drange": 0, "def": 6,
     "hp": 16, "maxhit": 2, "str": 8, "weak": "crush"},
    [("coins", 2, 30, 0.7), ("leather gloves", 1, 1, 0.15)],
    members=True, rank="easy")
MONSTERS["crawling hand"]["slayer_req"] = 5

_add_mob("banshee",
    {"abonus": 10, "atktype": ["magic"], "att": 20, "cb": 23, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 10, "drange": 5, "def": 15,
     "hp": 22, "maxhit": 3, "str": 15, "weak": "crush"},
    [("coins", 10, 60, 0.7), ("grimy guam", 1, 2, 0.2),
     ("grimy marrentill", 1, 1, 0.12)], members=True, rank="medium")
MONSTERS["banshee"]["slayer_req"] = 15

_add_mob("basilisk",
    {"abonus": 15, "atktype": ["slash"], "att": 55, "cb": 61, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 15, "drange": 25, "def": 45,
     "hp": 75, "maxhit": 9, "str": 55, "weak": "crush"},
    [("coins", 40, 200, 0.8), ("grimy ranarr", 1, 1, 0.05),
     ("uncut sapphire", 1, 1, 0.06), ("mithril bar", 1, 1, 0.1)],
    members=True, rank="hard")
MONSTERS["basilisk"]["slayer_req"] = 40

_add_mob("aberrant spectre",
    {"abonus": 25, "atktype": ["magic"], "att": 70, "cb": 96, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 35, "drange": 30, "def": 55,
     "hp": 90, "maxhit": 11, "str": 70, "weak": "ranged"},
    [("coins", 50, 250, 0.7), ("grimy ranarr", 1, 2, 0.18),
     ("grimy tarromin", 1, 2, 0.15), ("grimy guam", 1, 3, 0.2),
     ("ranarr seed", 1, 1, 0.04)], members=True, rank="elite")
MONSTERS["aberrant spectre"]["slayer_req"] = 60

_add_mob("gargoyle",
    {"abonus": 20, "atktype": ["crush"], "att": 90, "cb": 111, "dstab": 55,
     "dslash": 55, "dcrush": 40, "dmagic": 40, "drange": 55, "def": 70,
     "hp": 105, "maxhit": 11, "str": 90, "weak": "crush"},
    [("coins", 400, 1500, 0.9), ("adamant bar", 1, 2, 0.2),
     ("gold ore", 2, 5, 0.2), ("rune full helm", 1, 1, 0.03),
     ("granite maul", 1, 1, 0.01)], members=True, rank="elite")
MONSTERS["gargoyle"]["slayer_req"] = 75
MONSTERS["gargoyle"]["finisher"] = "rock hammer"

_add_mob("abyssal demon",
    {"abonus": 45, "atktype": ["slash"], "att": 95, "cb": 124, "dstab": 45,
     "dslash": 45, "dcrush": 45, "dmagic": 45, "drange": 45, "def": 75,
     "hp": 150, "maxhit": 8, "str": 85, "weak": "slash"},
    [("coins", 200, 1200, 0.9), ("abyssal whip", 1, 1, 0.02),
     ("grimy ranarr", 1, 1, 0.08), ("chaos rune", 5, 20, 0.3)],
    members=True, rank="elite")
MONSTERS["abyssal demon"]["slayer_req"] = 85

# --- the tower ------------------------------------------------------------------
ROOMS.update({
    "slayer_tower_1": dict(name="Slayer Tower \u2014 Ground Floor",
        desc="A crumbling gothic tower over Canifis. Severed hands drag "
             "themselves across the flagstones, and something upstairs is "
             "screaming.",
        exits={"out": "canifis", "up": "slayer_tower_2"},
        monsters=["crawling hand", "banshee"], hostile=True, members=True),
    "slayer_tower_2": dict(name="Slayer Tower \u2014 First Floor",
        desc="Scaled things slither between the pillars, and the fleshy "
             "walls pulse. Don't meet anything's eye.",
        exits={"down": "slayer_tower_1", "up": "slayer_tower_3"},
        monsters=["basilisk", "bloodveld"], hostile=True, members=True),
    "slayer_tower_3": dict(name="Slayer Tower \u2014 Top Floor",
        desc="Stone sentinels perch in the rafters over a floor scarred "
             "with teleport burns. The air smells of sulphur and rot.",
        exits={"down": "slayer_tower_2"},
        monsters=["aberrant spectre", "gargoyle", "abyssal demon"],
        hostile=True, members=True),
})
ROOMS["canifis"]["exits"]["tower"] = "slayer_tower_1"
ROOMS["canifis"]["desc"] += (" The Slayer Tower looms over the town "
                             "('tower').")
REGIONS.update({"slayer_tower_1": "Morytania", "slayer_tower_2": "Morytania",
                "slayer_tower_3": "Morytania"})

# --- masters in tiers --------------------------------------------------------------
TURAEL_TARGETS = ["chicken", "cow", "goblin", "giant rat", "scorpion",
                  "giant spider", "imp", "skeleton", "zombie"]
DURADEL_TARGETS = ["bloodveld", "basilisk", "aberrant spectre", "gargoyle",
                   "abyssal demon", "green dragon", "werewolf", "ice giant",
                   "greater demon", "hill giant"]


def _assign_task(p, master, targets, lo, hi):
    task = p.slayer_task
    if task and task["remaining"] > 0:
        say(f"{master}: \"You're still on the hunt \u2014 "
            f"{task['remaining']} of {task['amount']} "
            f"{task['monster']}s to go.\"", "teal")
        return
    pool = [t for t in targets if t in MONSTERS
            and p.lvl("slayer") >= MONSTERS[t].get("slayer_req", 0)]
    if not pool:
        pool = [t for t in targets if t in MONSTERS][:1]
    mon = random.choice(pool)
    amt = random.randint(lo, hi)
    p.slayer_task = {"monster": mon, "amount": amt, "remaining": amt}
    banner("Slayer Assignment", color="teal", line_color="teal")
    say(f"{master}: \"Your task: slay {amt} {mon}s.\"", "teal")
    locs = sorted({ROOMS[k]["name"] for k, r in ROOMS.items()
                   if mon in r.get("monsters", [])})
    if locs:
        say("  Find them at: " + ", ".join(locs[:4]), "grey")
    say("  (Check progress with 'task'; spend points with 'slayerbuy'.)",
        "grey")


def talk_turael(p):
    if not getattr(p, "members", False):
        say("Turael: \"Slayer is a members art, friend.\"", "bmagenta")
        return
    _assign_task(p, "Turael", TURAEL_TARGETS, 8, 15)


def talk_duradel(p):
    if not getattr(p, "members", False):
        say("Duradel: \"Members only, and I don't repeat myself.\"",
            "bmagenta")
        return
    if p.combat_level() < 100 or p.lvl("slayer") < 50:
        say("Duradel: \"Come back at combat 100 and slayer 50. I don't "
            "waste my lists on the soft.\"", "byellow")
        return
    _assign_task(p, "Duradel", DURADEL_TARGETS, 15, 35)


QUEST_TALK["turael"] = talk_turael
QUEST_TALK["duradel"] = talk_duradel
NPC_NAMES["turael"] = "Turael"
NPC_NAMES["duradel"] = "Duradel"
ROOMS["taverley"]["npc"] = "turael"
ROOMS["taverley"]["desc"] += " Turael, the gentlest of slayer masters, trims his hedge."
ROOMS["brimhaven"]["npc"] = "duradel"
ROOMS["brimhaven"]["desc"] += " Duradel watches the docks, arms crossed."

EFFECT_NOTES.update({
    "earmuffs": "blocks a banshee's scream (a slayer helmet also works)",
    "mirror shield": "reflects a basilisk's gaze",
    "rock hammer": "shatters dying gargoyles before their stone reforms",
})
EFFECT_NOTES["slayer helmet"] = ("+15% accuracy and damage against your "
                                 "slayer task; blocks banshee screams and "
                                 "spectre stench")


