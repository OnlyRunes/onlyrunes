# ===========================================================================
#  GOD WARS DUNGEON  (four generals, kill count, godswords)
# ===========================================================================
# A frozen chasm in the deep Wilderness. Slay a god's followers for kill
# count (10 opens their general's door — and is consumed). Each general
# fights differently; all drop godsword shards, rarely their hilt. Smith 3
# shards into a blade (smithing 80), then 'smith <god> godsword'.

GWD_FOLLOWERS = {"spiritual warrior": "bandos", "aviansie": "armadyl",
                 "bloodveld": "zamorak", "knight of saradomin": "saradomin"}

_add_mob("spiritual warrior",
    {"abonus": 15, "atktype": ["slash"], "att": 80, "cb": 115, "dstab": 40,
     "dslash": 40, "dcrush": 35, "dmagic": 20, "drange": 40, "def": 60,
     "hp": 65, "maxhit": 11, "str": 85, "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 80, 400, 0.8)],
    members=True, rank="elite")
_add_mob("aviansie",
    {"abonus": 25, "atktype": ["ranged"], "att": 70, "cb": 92, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 30, "drange": 45, "def": 55,
     "hp": 60, "maxhit": 10, "str": 60, "weak": "ranged"},
    [("bones", 1, 1, 1.0), ("coins", 60, 350, 0.8),
     ("adamant bar", 1, 2, 0.15)], members=True, rank="elite")
MONSTERS["aviansie"]["flying"] = True
_add_mob("bloodveld",
    {"abonus": 10, "atktype": ["crush"], "att": 75, "cb": 76, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 25, "drange": 25, "def": 50,
     "hp": 70, "maxhit": 10, "str": 80, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 60, 350, 0.8)],
    members=True, rank="elite")
_add_mob("knight of saradomin",
    {"abonus": 20, "atktype": ["slash"], "att": 85, "cb": 101, "dstab": 45,
     "dslash": 45, "dcrush": 40, "dmagic": 30, "drange": 45, "def": 65,
     "hp": 65, "maxhit": 11, "str": 80, "weak": "crush"},
    [("bones", 1, 1, 1.0), ("coins", 80, 400, 0.8)],
    members=True, rank="elite")

# --- the generals -------------------------------------------------------------
_GOD_ART = r'''
        \\  ______________  //
         \\/    \    /    \//
         |  (@)  |  |  (@)  |
          \_____/ || \_____/
           /##### || #####\
          |__/  WAAAGH  \__|
'''


def _god_intro(name):
    return [_tint(_GOD_ART, "grey"), _tint(_GOD_ART, "byellow", "bold"),
            _tint(_GOD_ART, "bred", "bold")]


def _god_death(name):
    return [_tint(_GOD_ART, "bred"), _tint(_GOD_ART, "grey", "dim")]


def _stomp_drain(p, m, dmg):
    p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
    print("  " + paint("The stomp rattles your armour! (-2 defence)", "bblue"))


GRAARDOR_ATTACKS = [
    {"label": "a fist like a falling boulder", "verb": "swings",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bred", "bold")],
     "mult": 1.3, "w": 4, "atype": "crush"},
    {"label": "a squall of skull-sized gravel", "verb": "hurls",
     "color": ("byellow",),
     "builder": lambda: [_tint(_GOD_ART, "byellow")],
     "mult": 0.9, "w": 3, "atype": "ranged"},
    {"label": "a ground-splitting stomp", "verb": "delivers",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "brown", "bold")],
     "mult": 1.1, "w": 2, "atype": "crush", "effect": _stomp_drain},
]

KREE_ATTACKS = [
    {"label": "a shrieking blast of wind", "verb": "summons",
     "color": ("bcyan", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bcyan", "bold")],
     "mult": 1.2, "w": 3, "atype": "ranged"},
    {"label": "a spiralling tornado", "verb": "conjures",
     "color": ("bwhite",),
     "builder": lambda: [_tint(_GOD_ART, "bwhite")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]

KRIL_ATTACKS = [
    {"label": "twin blazing scimitars", "verb": "whirls",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bred", "bold")],
     "mult": 1.2, "w": 3, "atype": "slash"},
    {"label": "a gout of demonfire", "verb": "breathes",
     "color": ("orange", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "orange", "bold")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]

ZILYANA_MELEE = [
    {"label": "her crackling blade", "verb": "flickers in with",
     "color": ("bwhite", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bwhite", "bold")],
     "mult": 1.0, "w": 1, "atype": "slash"},
]
ZILYANA_MAGIC = [
    {"label": "a bolt of searing light", "verb": "hurls",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "byellow", "bold")],
     "mult": 1.0, "w": 1, "atype": "magic"},
]


def _kril_take_turn(p, m):
    # his scythe smashes THROUGH protection prayers a quarter of the time
    if p.prayer_protects("melee") and random.random() < 0.25:
        dmg = random.randint(10, m["max_hit"] + 6)
        p.hp -= dmg
        drain = random.randint(8, 16)
        p.prayer_points = max(0, p.prayer_points - drain)
        say("K'ril Tsutsaroth roars — his scythe tears STRAIGHT THROUGH "
            f"your prayer for {dmg}! (-{drain} prayer)", "bred", "bold")
        print("  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        return "died" if p.hp <= 0 else None
    return _boss_take_turn(p, m, KRIL_ATTACKS)


def _zilyana_take_turn(p, m):
    if _boss_take_turn(p, m, ZILYANA_MELEE) == "died":
        return "died"
    say("She blurs with impossible speed — a second strike!", "bwhite")
    return _boss_take_turn(p, m, ZILYANA_MAGIC)


_GENERALS = {
    "general graardor": ("bandos",
        {"abonus": 40, "atktype": ["crush", "ranged"], "att": 180, "cb": 624,
         "dstab": 70, "dslash": 70, "dcrush": 60, "dmagic": 60, "drange": 70,
         "def": 90, "hp": 255, "maxhit": 26, "str": 190, "weak": "stab"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("bandos chestplate", 1, 1, 0.08), ("bandos tassets", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("bandos hilt", 1, 1, 0.05)],
        lambda p, m: _boss_take_turn(p, m, GRAARDOR_ATTACKS)),
    "kree'arra": ("armadyl",
        {"abonus": 45, "atktype": ["ranged", "magic"], "att": 160, "cb": 580,
         "dstab": 60, "dslash": 60, "dcrush": 60, "dmagic": 70, "drange": 75,
         "def": 80, "hp": 230, "maxhit": 20, "str": 150, "weak": "ranged"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("armadyl chestplate", 1, 1, 0.08),
         ("armadyl chainskirt", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("armadyl hilt", 1, 1, 0.05)],
        lambda p, m: _boss_take_turn(p, m, KREE_ATTACKS)),
    "k'ril tsutsaroth": ("zamorak",
        {"abonus": 40, "atktype": ["slash", "magic"], "att": 170, "cb": 650,
         "dstab": 65, "dslash": 65, "dcrush": 65, "dmagic": 65, "drange": 65,
         "def": 85, "hp": 255, "maxhit": 24, "str": 180, "weak": "slash"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("zamorakian spear", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("zamorak hilt", 1, 1, 0.05)],
        _kril_take_turn),
    "commander zilyana": ("saradomin",
        {"abonus": 50, "atktype": ["slash", "magic"], "att": 175, "cb": 596,
         "dstab": 60, "dslash": 60, "dcrush": 55, "dmagic": 70, "drange": 60,
         "def": 80, "hp": 240, "maxhit": 16, "str": 150, "weak": "crush"},
        [("bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("saradomin sword", 1, 1, 0.10),
         ("godsword shard", 1, 1, 0.25), ("saradomin hilt", 1, 1, 0.05)],
        _zilyana_take_turn),
}
for _g, (_god, _st, _drops, _turn) in _GENERALS.items():
    _add_mob(_g, _st, _drops, members=True)
    MONSTERS[_g]["boss"] = True
    MONSTERS[_g]["rank"] = "boss"
    _BOSSES.add(_g)
    BOSS_TURN[_g] = _turn
    BOSS_INTRO[_g] = _god_intro
    BOSS_DEATH[_g] = _god_death
MONSTERS["kree'arra"]["flying"] = True

# --- the rooms ------------------------------------------------------------------
ROOMS.update({
    "gwd_entrance": dict(name="God Wars Dungeon",
        desc="A frozen chasm where four god armies wage an endless war. "
             "Sealed doors bear each god's sigil — slay their followers for "
             "the kill count to enter (10 per door).",
        exits={"up": "deep_wilderness", "bandos": "bandos_stronghold",
               "armadyl": "armadyl_eyrie", "zamorak": "zamorak_fortress",
               "saradomin": "saradomin_encampment"},
        gwd=True, members=True),
    "bandos_stronghold": dict(name="Bandos' Stronghold",
        desc="Ogre-forged iron and the stink of war. Spiritual warriors "
             "drill for a battle that never ends.",
        exits={"out": "gwd_entrance", "door": "graardor_arena"},
        monsters=["spiritual warrior"], gwd=True, members=True),
    "graardor_arena": dict(name="Graardor's Arena",
        desc="A shattered throne room. GENERAL GRAARDOR bellows a challenge "
             "that cracks the ice.",
        exits={"out": "bandos_stronghold"},
        monsters=["general graardor"], kc_lock=("bandos", 10),
        gwd=True, members=True),
    "armadyl_eyrie": dict(name="Armadyl's Eyrie",
        desc="A wind-scoured spire open to the black sky. Aviansie wheel "
             "overhead on vast wings.",
        exits={"out": "gwd_entrance", "door": "kree_arena"},
        monsters=["aviansie"], gwd=True, members=True),
    "kree_arena": dict(name="Kree'arra's Roost",
        desc="The eyrie's summit. KREE'ARRA hangs in the howling air — "
             "blades will barely reach him up there.",
        exits={"out": "armadyl_eyrie"},
        monsters=["kree'arra"], kc_lock=("armadyl", 10),
        gwd=True, members=True),
    "zamorak_fortress": dict(name="Zamorak's Fortress",
        desc="Black iron and open flame. Bloodvelds drag their tongues "
             "across the ice.",
        exits={"out": "gwd_entrance", "door": "kril_arena"},
        monsters=["bloodveld"], gwd=True, members=True),
    "kril_arena": dict(name="K'ril's Sanctum",
        desc="A cathedral of fire. K'RIL TSUTSAROTH unfurls to his full "
             "height — prayers mean little to his scythe.",
        exits={"out": "zamorak_fortress"},
        monsters=["k'ril tsutsaroth"], kc_lock=("zamorak", 10),
        gwd=True, members=True),
    "saradomin_encampment": dict(name="Saradomin's Encampment",
        desc="White banners over cold ground. Knights of Saradomin hold "
             "their line with weary discipline.",
        exits={"out": "gwd_entrance", "door": "zilyana_arena"},
        monsters=["knight of saradomin"], gwd=True, members=True),
    "zilyana_arena": dict(name="Zilyana's Ground",
        desc="A ring of shattered ice. COMMANDER ZILYANA paces faster than "
             "the eye can follow.",
        exits={"out": "saradomin_encampment"},
        monsters=["commander zilyana"], kc_lock=("saradomin", 10),
        gwd=True, members=True),
})
ROOMS["deep_wilderness"]["exits"]["chasm"] = "gwd_entrance"
ROOMS["deep_wilderness"]["desc"] += (" A frozen chasm yawns in the north — "
                                     "the God Wars rage below ('chasm').")
for _rm in ("gwd_entrance", "bandos_stronghold", "graardor_arena",
            "armadyl_eyrie", "kree_arena", "zamorak_fortress", "kril_arena",
            "saradomin_encampment", "zilyana_arena"):
    REGIONS[_rm] = "Wilderness"

# --- god gear ----------------------------------------------------------------------
add_item("bandos chestplate", 2500000, members=True, equip={
    "dstab": 92, "dslash": 90, "dcrush": 88, "dmagic": -5, "drange": 92,
    "str": 4, "slot": "body", "req": {"defence": 65}})
add_item("bandos tassets", 2000000, members=True, equip={
    "dstab": 85, "dslash": 82, "dcrush": 80, "dmagic": -5, "drange": 85,
    "str": 2, "slot": "legs", "req": {"defence": 65}})
add_item("armadyl chestplate", 2500000, members=True, equip={
    "arange": 33, "dstab": 55, "dslash": 55, "dcrush": 55, "dmagic": 50,
    "drange": 90, "slot": "body", "req": {"ranged": 70}})
add_item("armadyl chainskirt", 2000000, members=True, equip={
    "arange": 20, "dstab": 50, "dslash": 50, "dcrush": 50, "dmagic": 45,
    "drange": 85, "slot": "legs", "req": {"ranged": 70}})
add_item("zamorakian spear", 2000000, members=True, equip={
    "astab": 85, "aslash": 65, "acrush": 65, "str": 75, "prayer": 2,
    "slot": "weapon", "req": {"attack": 70}})
add_item("saradomin sword", 1200000, members=True, equip={
    "aslash": 82, "acrush": 60, "str": 82, "prayer": 1,
    "slot": "weapon", "req": {"attack": 70}})
add_item("godsword shard", 100000, members=True)
add_item("godsword blade", 350000, members=True)
for _h in ("bandos hilt", "armadyl hilt", "zamorak hilt", "saradomin hilt"):
    add_item(_h, 500000, members=True)

_GS_EQUIP = {"aslash": 95, "acrush": 80, "str": 110, "slot": "weapon",
             "req": {"attack": 75}}
for _gs in ("bandos godsword", "armadyl godsword", "zamorak godsword",
            "saradomin godsword"):
    add_item(_gs, 3000000, members=True, equip=dict(_GS_EQUIP))


def _bgs_after(p, m):
    m["defence"] = max(1, m["defence"] - 15)
    print("  " + paint("The blow SHATTERS its defences!", "byellow"))


def _zgs_after(p, m):
    m["stunned"] = True
    print("  " + paint("Ice erupts — it is frozen solid and loses its "
                       "next turn!", "bcyan"))


def _sgs_after(p, m):
    heal = 15
    p.hp = min(p.max_hp, p.hp + heal)
    p.prayer_points = min(p.prayer_max(), p.prayer_points + 5)
    print("  " + paint(f"Holy light knits your wounds (+{heal} hp, "
                       "+5 prayer).", "bgreen"))


SPECIAL_ATTACKS.update({
    "bandos godsword": {"name": "Warstrike", "cost": 50, "hits": 1,
                        "acc": 1.2, "dmg": 1.21, "after": _bgs_after,
                        "desc": "a colossal blow that shatters the enemy's "
                                "defences"},
    "armadyl godsword": {"name": "Judgement", "cost": 50, "hits": 1,
                         "acc": 1.2, "dmg": 1.375,
                         "desc": "the heaviest single strike in the game"},
    "zamorak godsword": {"name": "Ice Cleave", "cost": 50, "hits": 1,
                         "acc": 1.1, "dmg": 1.1, "after": _zgs_after,
                         "desc": "freezes the enemy solid — it loses its "
                                 "next turn"},
    "saradomin godsword": {"name": "Healing Blade", "cost": 50, "hits": 1,
                           "acc": 1.1, "dmg": 1.1, "after": _sgs_after,
                           "desc": "restores your health and prayer as it "
                                   "strikes"},
})


def _smith_godsword(p, arg):
    """'smith godsword' (3 shards -> blade), 'smith <god> godsword'."""
    a = arg.strip().lower()
    god = next((g for g in ("bandos", "armadyl", "zamorak", "saradomin")
                if a.startswith(g)), None)
    if god:
        if not p.has("godsword blade"):
            say("You need a godsword blade (smith 3 godsword shards).",
                "byellow")
            return
        hilt = f"{god} hilt"
        if not p.has(hilt):
            say(f"You need a {hilt} — {god}'s general guards it.", "byellow")
            return
        p.take("godsword blade")
        p.take(hilt)
        sword = f"{god} godsword"
        p.add(sword)
        banner(sword.upper(), color="gold", line_color="gold")
        say(f"The hilt seats with a sound like a struck bell. The "
            f"{sword.upper()} is whole again.", "gold", "bold")
        p.gain_xp("smithing", 200)
        return
    if p.lvl("smithing") < 80:
        say("You need smithing level 80 to reforge a godsword blade.",
            "byellow")
        return
    if not p.has("godsword shard", 3):
        say(f"You need 3 godsword shards ({p.count('godsword shard')} held) "
            "— the generals drop them.", "byellow")
        return
    p.take("godsword shard", 3)
    p.add("godsword blade")
    say("You hammer the three shards into a single terrible GODSWORD BLADE. "
        "Now for a hilt... ('smith <god> godsword')", "gold", "bold")
    p.gain_xp("smithing", 400)


# items whose powers aren't visible in raw stats — shown by 'examine'
EFFECT_NOTES = {
    "ring of recoil": "when a monster hits you, it takes 1 damage back "
                      "(can't land the killing blow)",
    "ring of life": "at a tenth of your health it crumbles and teleports "
                    "you to Lumbridge, alive",
    "ring of forging": "iron bars never fail to smelt while worn",
    "ring of wealth": "+25% coins from monster drops",
    "slayer helmet": "+15% accuracy and damage against your slayer task",
    "anti-dragon shield": "soaks dragonfire — breath damage cut to a third",
    "fire cape": "proof you conquered the Fight Caves; the best cape there is",
    "spade": "digs into burial mounds and suspicious molehills",
}
_BARROWS_SET_NOTES = {
    "dharok": "SET (weapon+body): your max hit climbs as YOUR hp falls — "
              "up to double at death's door",
    "ahrim": "SET (weapon+body): magic hits may sap the monster's strength",
    "karil": "SET (weapon+body): ranged hits may corrode the monster's "
             "defence",
    "guthan": "SET (weapon+body): a quarter of your hits siphon life, "
              "healing you",
    "torag": "SET (weapon+body): hits may leave the monster reeling, "
             "losing its turn",
    "verac": "SET (weapon+body): a quarter of your misses strike true "
             "anyway",
}
for _piece in BARROWS_GEAR:
    EFFECT_NOTES[_piece] = _BARROWS_SET_NOTES[_piece.split("'")[0]]


def _barrows_set(p):
    """The brother whose weapon AND body you wear (else None)."""
    w = p.equipment.get("weapon") or ""
    b = p.equipment.get("body") or ""
    for bro in ("dharok", "ahrim", "karil", "guthan", "torag", "verac"):
        if w.startswith(bro) and b.startswith(bro):
            return bro
    return None


def _barrows_set_proc(p, m, bro, kind, dmg):
    """On-hit set effects (dharok & verac are handled in the hit roll)."""
    if bro == "guthan" and random.random() < 0.25 and p.hp < p.max_hp:
        heal = max(1, dmg // 2)
        p.hp = min(p.max_hp, p.hp + heal)
        print("  " + paint(f"Guthan's spear siphons life (+{heal} hp).",
                           "lime"))
    elif bro == "ahrim" and kind == "magic" and random.random() < 0.25:
        m["attack"] = max(1, m["attack"] - 5)
        print("  " + paint("Ahrim's blight saps its strength!", "bblue"))
    elif bro == "karil" and kind == "ranged" and random.random() < 0.25:
        m["defence"] = max(1, m["defence"] - 5)
        print("  " + paint("Karil's taint corrodes its defence!", "bblue"))
    elif bro == "torag" and random.random() < 0.15:
        m["stunned"] = True
        print("  " + paint("Torag's hammers leave it reeling!", "teal"))


def _cave_on_kill(p, target):
    """Advance the Fight Caves after each wave kill; crown the champion."""
    wave = getattr(p, "cave_wave", 0)
    if not wave or p.location != "fight_caves" \
            or target != CAVE_WAVES[wave - 1]:
        return
    if wave < len(CAVE_WAVES):
        p.cave_wave += 1
        nxt = CAVE_WAVES[p.cave_wave - 1]
        say(f"Wave {wave} cleared! Catch your breath, eat up — then 'next' "
            f"(wave {p.cave_wave}/{len(CAVE_WAVES)}: {nxt}).",
            "byellow", "bold")
    else:
        p.cave_wave = 0
        show_art(ART_QUEST, "gold", center=True)
        banner("THE FIGHT CAVES — CONQUERED", color="orange", line_color="red")
        p.add("fire cape")
        say("TzHaar-Mej-Jal: \"You defeated TzTok-Jad?! Unbelievable, JalYt! "
            "Take this — you have earned it.\"", "orange", "bold")
        say("You receive a FIRE CAPE! ('equip fire cape')", "bgreen", "bold")


