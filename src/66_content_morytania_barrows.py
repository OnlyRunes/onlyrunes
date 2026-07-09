# ===========================================================================
#  MORYTANIA & THE BARROWS  (Priest in Peril -> Canifis -> the six brothers)
# ===========================================================================
# Across the River Salve lies haunted Morytania: complete Priest in Peril
# (King Roald -> Drezel -> slay the temple guardian) to cross. Canifis prowls
# with werewolves, ghasts rot your food in Mort Myre, and at the Barrows you
# can 'dig' into six burial mounds, face each wight's signature power, and
# 'loot' the crypt chest for the famous barrows gear — with set effects.

add_item("spade", 3, tool="spade")
SHOPS["general"]["spade"] = 3
add_item("rotten food", 1)

# --- Morytania monsters ------------------------------------------------------
_add_mob("werewolf",
    {"abonus": 0, "atktype": ["slash"], "att": 60, "cb": 88, "dstab": 20,
     "dslash": 20, "dcrush": 20, "dmagic": 10, "drange": 20, "def": 50,
     "hp": 70, "maxhit": 10, "str": 70, "weak": "magic"},
    [("bones", 1, 1, 1.0), ("coins", 20, 150, 0.8),
     ("grimy ranarr", 1, 1, 0.05)], members=True, rank="hard")

_add_mob("ghast",
    {"abonus": 5, "atktype": ["crush"], "att": 50, "cb": 79, "dstab": 10,
     "dslash": 10, "dcrush": 10, "dmagic": 10, "drange": 10, "def": 40,
     "hp": 45, "maxhit": 8, "str": 55, "weak": "crush"},
    [("coins", 10, 60, 0.5)], members=True, rank="hard")

_add_mob("temple guardian",
    {"abonus": 0, "atktype": ["crush"], "att": 30, "cb": 30, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 0, "drange": 5, "def": 20,
     "hp": 49, "maxhit": 6, "str": 35, "weak": "slash"},
    [("bones", 1, 1, 1.0)], members=True, rank="medium")


def _ghast_rot(p, m, dmg):
    foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
    if foods:
        food = random.choice(foods)
        p.take(food)
        p.add("rotten food")
        print("  " + paint(f"The ghast's touch rots your {food}!", "green"))


MONSTER_EFFECTS["ghast"] = _ghast_rot

# --- The region ----------------------------------------------------------------
ROOMS.update({
    "paterdomus": dict(name="Paterdomus",
        desc="The temple over the River Salve, last light before Morytania. "
             "Drezel the priest keeps a nervous vigil.",
        exits={"west": "varrock_east_bank", "cross": "canifis"},
        npc="drezel", prayer_altar=True, monsters=[], members=True),
    "canifis": dict(name="Canifis",
        desc="A fog-bound town where the locals smile with too many teeth. "
             "A bank and a quiet tavern serve... whatever the locals are.",
        exits={"back": "paterdomus", "south": "mort_myre"},
        bank=True, monsters=["werewolf"], pickpocket=["man"], members=True),
    "mort_myre": dict(name="Mort Myre Swamp",
        desc="A drowned forest of grasping mist. Ghasts drift between the "
             "trees, hungry for the food in your pack.",
        exits={"north": "canifis", "south": "barrows_mounds"},
        monsters=["ghast"], members=True),
    "barrows_mounds": dict(name="The Barrows",
        desc="Six ancient burial mounds rise from the marsh. The air thrums "
             "with old wrath. ('dig' a mound — bring a spade)",
        exits={"north": "mort_myre"},
        barrows=True, members=True),
})
ROOMS["varrock_east_bank"]["exits"]["east"] = "paterdomus"
ROOMS["varrock_east_bank"]["desc"] += (" The road east runs toward the River "
                                       "Salve.")
ROOMS["canifis"]["qlock"] = (
    "priest_in_peril", ("complete",),
    "The temple doors to Morytania are sealed. (Quest: Priest in Peril — "
    "speak to King Roald in Varrock Palace)")
REGIONS.update({"paterdomus": "Morytania", "canifis": "Morytania",
                "mort_myre": "Morytania", "barrows_mounds": "Morytania"})
TRAVEL_HUBS["canifis"] = "canifis"
TRAVEL_NAMES.append("Canifis")

# --- Priest in Peril (the gate quest) --------------------------------------------
ALL_QUESTS["priest_in_peril"] = "Priest in Peril"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["priest_in_peril"] = 1
NPC_NAMES["priest_in_peril"] = "King Roald"
NPC_NAMES["drezel"] = "Drezel"


def talk_roald(p):
    stage = _q(p, "priest_in_peril")
    if stage == "not_started":
        banner("Quest Start: Priest in Peril", color="purple",
               line_color="bmagenta")
        say("King Roald: \"The priest DREZEL, who keeps the temple on the "
            "River Salve east of here, has not reported in weeks. Go east "
            "from the bank and see that he still stands his watch.\"")
        p.quests["priest_in_peril"] = "started"
    elif stage == "complete":
        say("King Roald: \"Varrock sleeps safer for your work at the Salve.\"")
    else:
        say("King Roald: \"The temple lies east of the east bank. See to "
            "Drezel!\"")


def talk_drezel(p):
    stage = _q(p, "priest_in_peril")
    if stage == "started":
        say("Drezel: \"Thank the gods! Something has crawled up from the "
            "crypt — a GUARDIAN of grave-dust and bone. I cannot bless the "
            "Salve while it prowls. Slay it, please!\"", "byellow")
        p.quests["priest_in_peril"] = "guardian"
    elif stage == "guardian":
        say("Drezel: \"The guardian still prowls the temple — 'fight temple "
            "guardian'!\"")
    elif stage == "cleansed":
        _complete_banner("Priest in Peril")
        say("Drezel blesses the river and throws open the eastern doors. "
            "\"Morytania lies beyond — tread carefully, friend.\" "
            "1406 prayer xp awarded!")
        p.gain_xp("prayer", 1406)
        p.quests["priest_in_peril"] = "complete"
    elif stage == "complete":
        say("Drezel: \"The Salve holds. May it always.\"")
    else:
        say("Drezel: \"A traveller? Speak to King Roald if you would aid "
            "Varrock.\"")


QUEST_TALK["priest_in_peril"] = talk_roald
QUEST_TALK["drezel"] = talk_drezel
ROOMS["varrock_palace"]["npc"] = "priest_in_peril"
ROOMS["varrock_palace"]["desc"] += " King Roald holds court within."
QUEST_HINTS["priest_in_peril"] = {
    "started": "find Drezel at Paterdomus — east from East Varrock's bank",
    "guardian": "slay the temple guardian at Paterdomus",
    "cleansed": "speak to Drezel to bless the Salve",
}

# --- The six brothers ---------------------------------------------------------------
# name -> (attack style key, signature note)
BROTHERS = {
    "ahrim the blighted": "magic",
    "dharok the wretched": "melee",
    "guthan the infested": "melee",
    "karil the tainted": "ranged",
    "torag the corrupted": "melee",
    "verac the defiled": "melee",
}

_BROTHER_STATS = {"abonus": 30, "att": 100, "cb": 115, "dstab": 60,
                  "dslash": 60, "dcrush": 60, "dmagic": 40, "drange": 60,
                  "def": 70, "hp": 100, "maxhit": 16, "str": 100,
                  "weak": "magic"}
for _b in BROTHERS:
    _s = dict(_BROTHER_STATS)
    _s["atktype"] = ["slash"]
    _add_mob(_b, _s, [("coins", 100, 600, 0.6)], members=True)
    MONSTERS[_b]["boss"] = True
    MONSTERS[_b]["rank"] = "boss"
    _BOSSES.add(_b)

BARROWS_ART = r'''
        _______
       /  RIP  \
      |  .-=-.  |
      | (  x  ) |
     _|__|___|__|_
'''
def _brother_intro(name):
    return [_tint(BARROWS_ART, "grey", "dim"), _tint(BARROWS_ART, "grey"),
            _tint(BARROWS_ART, "purple", "bold"),
            _tint(BARROWS_ART, "bmagenta", "bold")]


def _brother_death(name):
    return [_tint(BARROWS_ART, "purple"), _tint(BARROWS_ART, "grey"),
            _tint(BARROWS_ART, "grey", "dim")]


for _b in BROTHERS:
    MONSTER_ART[_b] = BARROWS_ART
    BOSS_INTRO[_b] = _brother_intro
    BOSS_DEATH[_b] = _brother_death


def _brother_take_turn(p, m):
    """Each wight fights with its brother's old power."""
    name = m["name"].split(" ")[0]
    style = BROTHERS[m["name"]]
    verb = {"magic": "hurls a gout of blighted fire",
            "ranged": "looses a volley of black bolts",
            "melee": "swings his weapon in a killing arc"}
    say(f"{m['name'].title()} {verb[style]}!", "purple", "bold")
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    dtype = {"magic": "magic", "ranged": "ranged"}.get(style, "crush")
    p_def_roll = _player_def_roll(p, dtype)
    max_hit = m["max_hit"]
    if name == "dharok":                # hits harder as HIS wounds deepen
        max_hit = int(max_hit * (1 + (1 - m["cur"] / m["hp"])))
    prot = {"magic": "magic", "ranged": "ranged"}.get(style, "melee")
    protected = p.prayer_protects(prot) and name != "verac"
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, max_hit)
        if protected:
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        hpbar = "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0),
                                                         p.max_hp, 18)
        if name == "verac" and dmg and p.prayer_protects("melee"):
            print("  " + paint(f"Verac's flail swings THROUGH your prayer "
                               f"for {dmg}!", "bmagenta") + hpbar)
        elif dmg == 0:
            print("  " + paint("Its blow grazes you. (0)", "grey") + hpbar)
        else:
            print("  " + paint(f"It hits you for {dmg}.", "bred") + hpbar)
        if p.hp > 0 and dmg > 0:
            _player_recoil(p, m, dmg)
            if name == "ahrim" and random.random() < 0.25:
                p.stat_drain["strength"] = p.stat_drain.get("strength", 0) + 2
                print("  " + paint("Ahrim's blight saps your strength! (-2)",
                                   "bblue"))
            elif name == "guthan" and m["cur"] < m["hp"]:
                heal = dmg // 2
                if heal:
                    m["cur"] = min(m["hp"], m["cur"] + heal)
                    print("  " + paint(f"Guthan's spear siphons your life "
                                       f"(+{heal}).", "lime"))
            elif name == "torag" and random.random() < 0.25:
                p.run_energy = max(0, getattr(p, "run_energy", 100) - 20)
                print("  " + paint("Torag's hammers crush your stamina "
                                   "(-20 energy).", "bblue"))
            elif name == "karil" and random.random() < 0.25:
                p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
                print("  " + paint("Karil's taint corrodes your defence! "
                                   "(-2)", "bblue"))
    else:
        print("  " + paint("You weather the wight's assault.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


for _b in BROTHERS:
    BOSS_TURN[_b] = _brother_take_turn

# --- dig / loot ------------------------------------------------------------------------
def cmd_dig(p, arg):
    if p.location == "falador_park":
        if not p.find_tool("spade"):
            say("You need a spade (general store).", "byellow")
            return
        say("You dig into the great molehill and tumble into a dark, "
            "earth-smelling burrow...", "brown")
        p.location = "mole_lair"
        return cmd_look(p, "")
    if p.location != "barrows_mounds":
        say("There's nothing worth digging here.", "grey")
        return
    if not p.find_tool("spade"):
        say("You need a spade (general store).", "byellow")
        return
    slain = set(getattr(p, "barrows", []))
    left = [b for b in BROTHERS if b not in slain]
    if not left:
        say("All six mounds lie quiet. The tunnel below is open — 'loot' "
            "the chest!", "bgreen")
        return
    want = arg.strip().lower()
    target = next((b for b in left if want and want in b), left[0])
    say(f"You dig into the mound... and drop into a burial crypt. "
        f"({len(slain)}/6 brothers at rest)", "purple")
    _start_combat(p, target)


def cmd_loot(p, _a):
    if p.location != "barrows_mounds":
        say("There's no chest to loot here.", "grey")
        return
    slain = set(getattr(p, "barrows", []))
    left = [b for b in BROTHERS if b not in slain]
    if left:
        say(f"The tunnel is sealed while brothers still stir — {len(left)} "
            "mound(s) to go. ('dig')", "byellow")
        return
    p.barrows = []
    p.barrows_loots = getattr(p, "barrows_loots", 0) + 1
    show_art(ART_QUEST, "gold", center=True)
    banner("THE BARROWS CHEST", color="purple", line_color="bmagenta")
    coins = random.randint(4000, 20000)
    p.add("coins", coins)
    say(f"  Coins x{coins:,}", "gold")
    for rune, lo, hi in [("death rune", 8, 40), ("chaos rune", 15, 60),
                         ("nature rune", 5, 25)]:
        q = random.randint(lo, hi)
        p.add(rune, q)
        say(f"  {rune} x{q}", "byellow")
    if random.random() < 0.30:
        piece = random.choice(BARROWS_GEAR)
        p.add(piece)
        say(f"  ✦ BARROWS: {piece}!", "bmagenta", "bold")
    else:
        say("  (No barrows equipment this time — the brothers stir again.)",
            "grey")
    say("The mounds seal themselves behind you. The dead do not stay dead "
        "here.", "purple")


HANDLERS["dig"] = cmd_dig
HANDLERS["loot"] = cmd_loot


def _barrows_on_kill(p, target):
    if target not in BROTHERS or p.location != "barrows_mounds":
        return
    if target not in p.barrows:
        p.barrows.append(target)
    n = len(p.barrows)
    if n >= len(BROTHERS):
        say("The last wight crumbles. Below the mounds, a tunnel grinds "
            "open — 'loot' the chest!", "bmagenta", "bold")
    else:
        say(f"{target.title()} returns to his rest. ({n}/6 — 'dig' the next "
            "mound)", "purple")


# --- Barrows gear (weapon + body per brother; wear both for the set effect) ---
BARROWS_GEAR = [
    "dharok's greataxe", "dharok's platebody",
    "ahrim's staff", "ahrim's robetop",
    "karil's crossbow", "karil's leathertop",
    "guthan's warspear", "guthan's platebody",
    "torag's hammers", "torag's platebody",
    "verac's flail", "verac's brassard",
]
add_item("dharok's greataxe", 800000, members=True, equip={
    "aslash": 90, "acrush": 70, "str": 105, "slot": "weapon",
    "req": {"attack": 70}})
add_item("dharok's platebody", 800000, members=True, equip={
    "dstab": 90, "dslash": 88, "dcrush": 85, "dmagic": -5, "drange": 90,
    "slot": "body", "req": {"defence": 70}})
add_item("ahrim's staff", 700000, members=True, equip={
    "amagic": 25, "dmagic": 15, "mdmg": 5, "slot": "weapon",
    "req": {"magic": 70}})
add_item("ahrim's robetop", 700000, members=True, equip={
    "amagic": 22, "dmagic": 60, "dstab": 35, "dslash": 30, "dcrush": 40,
    "slot": "body", "req": {"magic": 70}})
add_item("karil's crossbow", 700000, members=True, equip={
    "arange": 94, "slot": "weapon", "req": {"ranged": 70}})
add_item("karil's leathertop", 700000, members=True, equip={
    "drange": 90, "dmagic": 45, "dstab": 45, "dslash": 40, "dcrush": 45,
    "arange": 3, "slot": "body", "req": {"ranged": 70}})
add_item("guthan's warspear", 750000, members=True, equip={
    "astab": 85, "aslash": 70, "acrush": 70, "str": 85, "slot": "weapon",
    "req": {"attack": 70}})
add_item("guthan's platebody", 750000, members=True, equip={
    "dstab": 88, "dslash": 86, "dcrush": 83, "dmagic": -5, "drange": 88,
    "slot": "body", "req": {"defence": 70}})
add_item("torag's hammers", 700000, members=True, equip={
    "acrush": 90, "str": 90, "slot": "weapon", "req": {"attack": 70}})
add_item("torag's platebody", 700000, members=True, equip={
    "dstab": 92, "dslash": 90, "dcrush": 88, "dmagic": -4, "drange": 92,
    "slot": "body", "req": {"defence": 70}})
add_item("verac's flail", 750000, members=True, equip={
    "acrush": 88, "astab": 70, "str": 84, "prayer": 3, "slot": "weapon",
    "req": {"attack": 70}})
add_item("verac's brassard", 750000, members=True, equip={
    "dstab": 85, "dslash": 83, "dcrush": 84, "dmagic": 0, "drange": 85,
    "prayer": 3, "slot": "body", "req": {"defence": 70}})


