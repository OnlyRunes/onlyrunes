# ===========================================================================
#  SLAYER SUPERBOSSES  (Kraken, Cerberus, Thermy, the Sire, the Guardians)
# ===========================================================================
# Five lairs open only to master slayers: the Kraken off the Fishing
# Guild's cove (87), Cerberus beneath Taverley (91), the Thermonuclear
# smoke devil under Pollnivneach (93), the Abyssal Sire through a rift in
# the Slayer Tower (85) — and Dusk & Dawn on the tower's roof (75).

# --- spoils -----------------------------------------------------------------
add_item("trident of the seas", 1200000, members=True, equip={
    "slot": "weapon", "amagic": 25, "dmagic": 3, "powered": 22,
    "req": {"magic": 75}})
EFFECT_NOTES["trident of the seas"] = ("a powered staff — casts its own "
                                       "magic, no runes needed (max 22, "
                                       "raised by magic-damage gear)")
add_item("occult necklace", 800000, members=True, equip={
    "slot": "amulet", "amagic": 12, "mdmg": 10, "req": {"magic": 70}})
EFFECT_NOTES["occult necklace"] = ("+10% magic damage — the mage's neck")
add_item("smoke battlestaff", 300000, members=True, equip={
    "slot": "weapon", "amagic": 15, "dmagic": 3, "mdmg": 5,
    "req": {"magic": 60}})
add_item("primordial crystal", 300000, members=True)
add_item("pegasian crystal", 300000, members=True)
add_item("eternal crystal", 300000, members=True)
add_item("primordial boots", 900000, members=True, equip={
    "slot": "boots", "str": 5, "dstab": 12, "dslash": 12, "dcrush": 12,
    "req": {"defence": 75}})
add_item("pegasian boots", 800000, members=True, equip={
    "slot": "boots", "arange": 12, "drange": 12, "dstab": 5, "dslash": 5,
    "req": {"ranged": 75, "defence": 75}})
add_item("eternal boots", 700000, members=True, equip={
    "slot": "boots", "amagic": 8, "dmagic": 8, "dstab": 5, "dslash": 5,
    "req": {"magic": 75, "defence": 75}})
CRAFT_RECIPES.update({
    "primordial boots": ("primordial crystal", 1, 60, 200),
    "pegasian boots": ("pegasian crystal", 1, 60, 200),
    "eternal boots": ("eternal crystal", 1, 60, 200),
})
add_item("abyssal dagger", 1500000, members=True, equip={
    "slot": "weapon", "astab": 75, "aslash": 40, "str": 75,
    "req": {"attack": 70}})
add_item("abyssal bludgeon", 2000000, members=True, equip={
    "slot": "weapon", "acrush": 102, "str": 85,
    "req": {"strength": 70, "attack": 70}})
EFFECT_NOTES["abyssal bludgeon"] = ("two hands of pure crush — the "
                                    "carapace-cracker")
add_item("granite gloves", 120000, members=True, equip={
    "slot": "gloves", "str": 2, "dstab": 8, "dslash": 8, "dcrush": 8,
    "req": {"defence": 50}})
add_item("granite ring", 150000, members=True, equip={
    "slot": "ring", "str": 2, "dcrush": 8, "dstab": 4})
add_item("granite hammer", 400000, members=True, equip={
    "slot": "weapon", "acrush": 57, "str": 56, "req": {"attack": 50,
                                                       "strength": 50}})

# --- the everyday horrors -------------------------------------------------------
_add_mob("hellhound",
    {"abonus": 30, "atktype": ["slash"], "att": 100, "cb": 122,
     "dstab": 30, "dslash": 30, "dcrush": 30, "dmagic": 30, "drange": 30,
     "def": 90, "hp": 116, "maxhit": 11, "str": 100, "weak": "slash"},
    [("bones", 1, 1, 1.0), ("coins", 50, 300, 0.7)],
    members=True, rank="elite")
_add_mob("smoke devil",
    {"abonus": 35, "atktype": ["magic"], "att": 110, "cb": 160,
     "dstab": 45, "dslash": 45, "dcrush": 45, "dmagic": 50, "drange": 50,
     "def": 80, "hp": 90, "maxhit": 12, "str": 110, "weak": "slash"},
    [("bones", 1, 1, 1.0), ("coins", 100, 500, 0.8),
     ("fire rune", 20, 60, 0.5), ("grimy ranarr", 1, 2, 0.15)],
    members=True, rank="elite")
MONSTERS["smoke devil"]["slayer_req"] = 93
ROOMS["taverley_dungeon"]["monsters"].append("hellhound")
DURADEL_TARGETS.extend(["hellhound", "smoke devil"])

# --- the five ---------------------------------------------------------------------
def _cerb_take_turn(p, m):
    cyc = m.get("cerb_cycle", 0)
    m["cerb_cycle"] = cyc + 1
    if cyc % 4 == 3:
        animate(_fx_souls(), delay=0.14, center=True)
        say("CERBERUS howls — three SUMMONED SOULS streak in, sword, bow "
            "and staff!", "bred", "bold")
        total = 0
        for style in ("melee", "ranged", "magic"):
            dmg = random.randint(0, 8)
            if p.prayer_protects(style):
                dmg = 0
            total += dmg
        p.hp -= total
        print("  " + paint(f"The souls tear {total} from you. (each is "
                           "blocked only by its matching prayer)", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        if p.active_prayers:
            p.prayer_points -= p.prayer_drain()
        return "died" if p.hp <= 0 else None
    return _boss_take_turn(p, m, CERB_ATTACKS)


def _thermy_take_turn(p, m):
    animate(_fx_smoke(), delay=0.13, center=True)
    say("The smoke itself attacks — there is nowhere it isn't.",
        "grey", "bold")
    dmg = random.randint(2, 16)
    if p.prayer_protects("magic"):
        dmg = int(dmg * 0.5)
    p.hp -= dmg
    print("  " + paint(f"The smoke scours your lungs for {dmg}.", "bred")
          + "  " + paint("HP ", "white")
          + bar_meter(max(p.hp, 0), p.max_hp, 18))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
    return "died" if p.hp <= 0 else None


def _sire_miasma(p, m, dmg):
    if dmg > 0 and not getattr(p, "poison", 0) and random.random() < 0.4:
        p.poison = 3
        print("  " + paint("Miasma seeps into the wound — POISONED!",
                           "green"))


CERB_ATTACKS = [
    {"label": "a lunge of three sets of jaws", "verb": "snaps with",
     "color": ("bred", "bold"), "builder": _fx_jaws,
     "mult": 1.15, "w": 3, "atype": "slash"},
    {"label": "a lash of hellfire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _fx_hellfire,
     "mult": 1.0, "w": 2, "atype": "magic"},
]
KRAKEN_ATTACKS = [
    {"label": "a pillar of crushing water", "verb": "hurls",
     "color": ("bblue", "bold"), "builder": _fx_pillar,
     "mult": 1.15, "w": 3, "atype": "magic"},
    {"label": "a flailing tentacle", "verb": "sweeps",
     "color": ("teal",), "builder": _fx_tentacle,
     "mult": 0.9, "w": 2, "atype": "crush"},
]
SIRE_ATTACKS = [
    {"label": "a scythe of abyssal tentacles", "verb": "lashes out",
     "color": ("purple", "bold"), "builder": _fx_lash,
     "mult": 1.15, "w": 3, "atype": "crush", "effect": _sire_miasma},
    {"label": "a wave of choking miasma", "verb": "vents",
     "color": ("green",), "builder": _fx_miasma,
     "mult": 0.9, "w": 2, "atype": "magic"},
]
GROTESQUE_ATTACKS = [
    {"label": "a wrecking swing of stone fists", "verb": "hammers down",
     "color": ("grey", "bold"), "builder": _fx_smash,
     "mult": 1.1, "w": 3, "atype": "crush"},
    {"label": "a volley of molten slag", "verb": "rains",
     "color": ("orange",), "builder": _fx_slag,
     "mult": 1.0, "w": 2, "atype": "ranged"},
]

_SUPERBOSSES = {
    "kraken": (87,
        {"abonus": 40, "atktype": ["magic"], "att": 160, "cb": 291,
         "dstab": 220, "dslash": 220, "dcrush": 220, "dmagic": 10,
         "drange": 220, "def": 90, "hp": 255, "maxhit": 20, "str": 150,
         "weak": "magic"},
        [("trident of the seas", 1, 1, 0.04), ("raw shark", 3, 8, 0.8),
         ("coins", 3000, 12000, 1.0), ("blood rune", 10, 30, 0.5)],
        lambda p, m: _boss_take_turn(p, m, KRAKEN_ATTACKS)),
    "cerberus": (91,
        {"abonus": 45, "atktype": ["slash", "magic"], "att": 180,
         "cb": 318, "dstab": 75, "dslash": 60, "dcrush": 75, "dmagic": 75,
         "drange": 75, "def": 100, "hp": 260, "maxhit": 23, "str": 180,
         "weak": "slash"},
        [("primordial crystal", 1, 1, 0.05),
         ("pegasian crystal", 1, 1, 0.05), ("eternal crystal", 1, 1, 0.05),
         ("big bones", 1, 1, 1.0), ("coins", 4000, 15000, 1.0)],
        _cerb_take_turn),
    "thermonuclear smoke devil": (93,
        {"abonus": 40, "atktype": ["magic"], "att": 170, "cb": 301,
         "dstab": 65, "dslash": 50, "dcrush": 65, "dmagic": 70,
         "drange": 70, "def": 95, "hp": 240, "maxhit": 16, "str": 160,
         "weak": "slash"},
        [("occult necklace", 1, 1, 0.04), ("smoke battlestaff", 1, 1, 0.03),
         ("coins", 4000, 15000, 1.0), ("fire rune", 30, 90, 0.8)],
        _thermy_take_turn),
    "abyssal sire": (85,
        {"abonus": 45, "atktype": ["crush", "magic"], "att": 185,
         "cb": 350, "dstab": 60, "dslash": 80, "dcrush": 80, "dmagic": 75,
         "drange": 80, "def": 105, "hp": 280, "maxhit": 24, "str": 190,
         "weak": "stab"},
        [("abyssal whip", 1, 1, 0.04), ("abyssal dagger", 1, 1, 0.03),
         ("abyssal bludgeon", 1, 1, 0.02), ("coins", 5000, 18000, 1.0),
         ("grimy ranarr", 2, 5, 0.4)],
        lambda p, m: _boss_take_turn(p, m, SIRE_ATTACKS)),
    "grotesque guardians": (75,
        {"abonus": 40, "atktype": ["crush", "ranged"], "att": 170,
         "cb": 328, "dstab": 70, "dslash": 70, "dcrush": 50, "dmagic": 70,
         "drange": 70, "def": 95, "hp": 228, "maxhit": 22, "str": 170,
         "weak": "crush"},
        [("granite gloves", 1, 1, 0.06), ("granite ring", 1, 1, 0.05),
         ("granite hammer", 1, 1, 0.04), ("coins", 4000, 14000, 1.0),
         ("big bones", 1, 1, 1.0)],
        lambda p, m: _boss_take_turn(p, m, GROTESQUE_ATTACKS)),
}
for _sb, (_req, _st, _drops, _turn) in _SUPERBOSSES.items():
    _add_mob(_sb, _st, _drops, members=True)
    MONSTERS[_sb]["boss"] = True
    MONSTERS[_sb]["rank"] = "boss"
    MONSTERS[_sb]["slayer_req"] = _req
    _BOSSES.add(_sb)
    BOSS_TURN[_sb] = _turn
MONSTERS["grotesque guardians"]["transform"] = True
MONSTERS["grotesque guardians"]["transform_flies"] = True
MONSTERS["grotesque guardians"]["transform_msg"] = (
    "DUSK shatters — and from the rubble DAWN takes wing, screaming!")

# --- the lairs ---------------------------------------------------------------------
ROOMS.update({
    "kraken_cove": dict(name="Kraken Cove",
        desc="A sea-cave north of the guild where the water is the wrong "
             "kind of calm. Below the surface, something the size of a "
             "chapel unfolds. (magic bites where steel cannot)",
        exits={"out": "fishing_guild"},
        monsters=["kraken"], members=True),
    "cerberus_lair": dict(name="Cerberus' Lair",
        desc="A gate of black iron under Taverley, warm to the touch. "
             "CERBERUS waits behind it, three heads breathing in turn — "
             "and every fourth breath, the souls come.",
        exits={"out": "taverley_dungeon"},
        monsters=["cerberus"], members=True),
    "smoke_dungeon": dict(name="Smoke Devil Dungeon",
        desc="Down Pollnivneach's old well, the air is smoke that thinks. "
             "Devils coil through it — and the THERMONUCLEAR one waits "
             "at the heart, impossible to dodge.",
        exits={"up": "pollnivneach"},
        monsters=["smoke devil", "thermonuclear smoke devil"],
        hostile=True, members=True),
    "abyssal_nexus": dict(name="The Abyssal Nexus",
        desc="A rift off the tower's top floor opens on somewhere that "
             "isn't anywhere. THE ABYSSAL SIRE slumbers at its heart, "
             "tentacles drifting like kelp.",
        exits={"out": "slayer_tower_3"},
        monsters=["abyssal sire"], members=True),
    "tower_roof": dict(name="Slayer Tower Rooftop",
        desc="Wind and gargoyle-grit over Canifis. DUSK and DAWN uncoil "
             "from the parapets — stone that remembered how to hate.",
        exits={"down": "slayer_tower_3"},
        monsters=["grotesque guardians"], members=True),
})
ROOMS["fishing_guild"]["exits"]["cove"] = "kraken_cove"
ROOMS["fishing_guild"]["desc"] += (" North along the rocks, a cove holds "
                                   "the wrong kind of calm ('cove').")
ROOMS["taverley_dungeon"]["exits"]["gate"] = "cerberus_lair"
ROOMS["taverley_dungeon"]["desc"] += (" Hellhounds howl by a black iron "
                                      "gate ('gate').")
ROOMS["pollnivneach"]["exits"]["well"] = "smoke_dungeon"
ROOMS["pollnivneach"]["desc"] += (" The old well breathes smoke "
                                  "('well').")
ROOMS["slayer_tower_3"]["exits"]["rift"] = "abyssal_nexus"
ROOMS["slayer_tower_3"]["exits"]["roof"] = "tower_roof"
ROOMS["slayer_tower_3"]["desc"] += (" A rift hums in the far wall "
                                    "('rift'), and stairs wind to the "
                                    "roof ('roof').")
REGIONS.update({"kraken_cove": "Kandarin", "cerberus_lair": "Asgarnia",
                "smoke_dungeon": "AlKharid", "abyssal_nexus": "Morytania",
                "tower_roof": "Morytania"})


