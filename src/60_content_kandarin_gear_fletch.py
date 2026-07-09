# ===========================================================================
#  WORLD EXPANSION  (Kandarin route, Karamja, guilds, wilderness, fishing)
# ===========================================================================
# --- Catherby fishing food (lobster / tuna / swordfish) -------------------
add_item("lobster pot", 20, tool="cage")
for _raw, _cooked, _heal, _val, _cxp, _clvl in [
        ("raw tuna", "tuna", 10, 60, 100, 30),
        ("raw lobster", "lobster", 12, 80, 120, 40),
        ("raw swordfish", "swordfish", 14, 100, 140, 50)]:
    add_item(_raw, _val // 2)
    add_item(_cooked, _val, heal=_heal)
    add_item("burnt " + _cooked, 1)
    RAW_TO_COOKED[_raw] = (_cooked, "burnt " + _cooked, _clvl)
    COOK_XP[_raw] = _cxp
FISH["harpoon"] = [("raw tuna", 35, 80), ("raw swordfish", 50, 100)]
FISH["cage"] = [("raw lobster", 40, 90)]
SHOPS["fishing"]["harpoon"] = 5
SHOPS["fishing"]["lobster pot"] = 20
SHOPS["crafting"] = {"needle": 1, "thread": 5, "chisel": 1, "ball of wool": 12,
                     "leather": 20}
PICKPOCKET["monk"] = (5, 12, 20, 2)


def _add_mob(name, s, drops, members=False, rank="hard"):
    m = mob(s["hp"], s["att"], s["def"], s["maxhit"], drops, members=members)
    m["rank"] = rank
    m["level"] = s.get("cb")
    m["abonus"] = s.get("abonus", 0)
    m["atktype"] = s.get("atktype", ["crush"])
    m["weakness"] = s.get("weak", "crush")
    m["dbonus"] = {"stab": s["dstab"], "slash": s["dslash"], "crush": s["dcrush"],
                   "magic": s["dmagic"], "ranged": s["drange"]}
    MONSTERS[name] = m


_add_mob("chaos druid", {"abonus":0,"atktype":["crush"],"att":8,"cb":13,"dcrush":0,"def":12,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":20,"maxhit":2,"str":8,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 1, 28, 0.7),
    ("grimy guam", 1, 2, 0.3), ("grimy marrentill", 1, 2, 0.25),
    ("grimy tarromin", 1, 1, 0.15), ("grimy ranarr", 1, 1, 0.05),
    ("law rune", 1, 3, 0.1)], members=True, rank="medium")
_add_mob("white wolf", {"abonus":0,"atktype":["stab"],"att":20,"cb":25,"dcrush":0,"def":22,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":34,"maxhit":3,"str":16,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 1, 20, 0.5)],
    members=True, rank="hard")
_add_mob("deadly red spider", {"abonus":0,"atktype":["stab"],"att":30,"cb":34,"dcrush":7,"def":30,"dmagic":12,"drange":16,"dslash":16,"dstab":15,"hp":35,"maxhit":3,"str":25,"weak":"crush"}, [("bones", 1, 1, 1.0), ("coins", 5, 40, 0.6),
    ("grimy harralander", 1, 2, 0.2), ("steel arrow", 5, 15, 0.3)],
    members=True, rank="hard")
_add_mob("jogre", {"abonus":22,"atktype":["crush"],"att":43,"cb":53,"dcrush":0,"def":43,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":60,"maxhit":7,"str":43,"weak":"stab"}, [("bones", 1, 1, 1.0), ("big bones", 1, 1, 0.3),
    ("coins", 10, 60, 0.8)], members=True, rank="elite")
_add_mob("paladin", {"abonus":0,"atktype":["slash"],"att":134,"cb":49,"dcrush":40,"def":28,"dmagic":30,"drange":20,"dslash":40,"dstab":20,"hp":55,"maxhit":6,"str":48,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 80, 220, 1.0),
    ("law rune", 1, 4, 0.2)], members=True, rank="elite")

# --- New rooms ------------------------------------------------------------
ROOMS.update({
    "mining_guild": dict(name="Mining Guild",
        desc="A bustling guild mine rich with coal, gold, mithril and "
             "adamantite ore.",
        exits={"out": "dwarven_mine"},
        rocks=["coal", "gold", "mithril", "adamantite"]),
    "crafting_guild": dict(name="Crafting Guild",
        desc="Master crafters work here. A tannery, a spinning wheel and a "
             "supply shop serve members of the guild.",
        exits={"out": "falador_west"},
        tanner=True, spinning_wheel=True, shop="crafting"),
    "monastery": dict(name="Edgeville Monastery",
        desc="A peaceful monastery. Monks tend an altar where prayer can be "
             "restored — and their pockets jingle with coin.",
        exits={"east": "edgeville"},
        prayer_altar=True, pickpocket=["monk"]),
    "deep_wilderness": dict(name="Deep Wilderness",
        desc="The lawless wastes stretch north. Dark warriors and giants roam, "
             "and the air hums with danger.",
        exits={"south": "wilderness_edge"},
        monsters=["dark warrior", "hill giant", "hobgoblin"]),
    # ---- Kandarin (members) via Taverley -----------------------------------
    "taverley": dict(name="Taverley",
        desc="A druidic village west of Falador, gateway to Kandarin. A bank "
             "stands by the road, and a dungeon yawns below. (members)",
        exits={"east": "falador_west", "down": "taverley_dungeon",
               "west": "white_wolf_mountain"},
        bank=True, members=True),
    "taverley_dungeon": dict(name="Taverley Dungeon",
        desc="A sprawling cavern. Chaos druids gather herbs while giants stomp "
             "in the dark. (members)",
        exits={"up": "taverley"},
        monsters=["chaos druid", "hill giant", "deadly red spider"], members=True),
    "white_wolf_mountain": dict(name="White Wolf Mountain",
        desc="A snow-capped pass between Taverley and Catherby, prowled by "
             "white wolves. (members)",
        exits={"east": "taverley", "west": "catherby"},
        monsters=["white wolf"], members=True),
    "catherby": dict(name="Catherby",
        desc="A seaside town with the finest fishing in Kandarin — tuna, "
             "swordfish and lobster. A bank sits by the shore. (members)",
        exits={"east": "white_wolf_mountain", "north": "seers_village"},
        bank=True, fish_tools=["net", "harpoon", "cage"], members=True),
    "seers_village": dict(name="Seers' Village",
        desc="A quiet village beside Camelot, with a bank and roads west to "
             "Ardougne. (members)",
        exits={"south": "catherby", "west": "ardougne"},
        bank=True, members=True),
    "ardougne": dict(name="Ardougne",
        desc="A grand split city. The market square bustles with stalls and "
             "pickpocketable crowds; paladins patrol the palace. (members)",
        exits={"east": "seers_village"},
        bank=True, pickpocket=["man", "woman"], monsters=["paladin"],
        members=True),
    # ---- Karamja extension (members) ---------------------------------------
    "brimhaven": dict(name="Brimhaven",
        desc="A tropical port on eastern Karamja. Jogres lumber through the "
             "jungle and a bank serves adventurers. (members)",
        exits={"west": "karamja_port"},
        bank=True, monsters=["jogre", "scorpion"], members=True),
    "karamja_volcano": dict(name="Karamja Volcano",
        desc="A smoking caldera riddled with lava tunnels and deadly red "
             "spiders. (members)",
        exits={"out": "karamja_port"},
        monsters=["deadly red spider"], members=True),
})

# --- Wire new exits into existing rooms -----------------------------------
ROOMS["dwarven_mine"]["exits"]["guild"] = "mining_guild"
ROOMS["falador_west"]["exits"]["guild"] = "crafting_guild"
ROOMS["falador_west"]["exits"]["west"] = "taverley"
ROOMS["edgeville"]["exits"]["west"] = "monastery"
ROOMS["wilderness_edge"]["exits"]["north"] = "deep_wilderness"
ROOMS["karamja_port"]["exits"]["east"] = "brimhaven"
ROOMS["karamja_port"]["exits"]["volcano"] = "karamja_volcano"

# --- New travel destinations ----------------------------------------------
TRAVEL_HUBS.update({"taverley": "taverley", "catherby": "catherby",
                    "seers village": "seers_village", "seers": "seers_village",
                    "ardougne": "ardougne", "brimhaven": "brimhaven"})
TRAVEL_NAMES.extend(["Taverley", "Catherby", "Seers' Village", "Ardougne",
                     "Brimhaven"])

# ===========================================================================
#  COMBAT-TRIANGLE GEAR EXPANSION  (real OSRS gear for all 3 styles)
# ===========================================================================
# Obtainable at the Grand Exchange ('ge buy <item>'); top-tier also drops.
add_item('dragon scimitar', 100000, equip={'astab': 8, 'aslash': 67, 'acrush': -2, 'dslash': 1, 'str': 66, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('abyssal whip', 120001, equip={'aslash': 82, 'str': 82, 'slot': 'weapon', 'req': {'attack': 70}}, members=True)
add_item('dragon mace', 50000, equip={'astab': 40, 'aslash': -2, 'acrush': 60, 'str': 55, 'prayer': 5, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('dragon longsword', 100000, equip={'astab': 58, 'aslash': 69, 'acrush': -2, 'dslash': 3, 'dcrush': 2, 'str': 71, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('granite maul', 50000, equip={'acrush': 81, 'str': 79, 'slot': 'weapon', 'req': {'attack': 50, 'strength': 50}}, members=True)
add_item('dragon platelegs', 270000, equip={'amagic': -21, 'arange': -11, 'dstab': 68, 'dslash': 66, 'dcrush': 63, 'dmagic': -4, 'drange': 65, 'slot': 'legs', 'req': {'defence': 60}}, members=True)
add_item('dragon chainbody', 250000, equip={'amagic': -15, 'dstab': 81, 'dslash': 93, 'dcrush': 98, 'dmagic': -3, 'drange': 82, 'slot': 'body', 'req': {'defence': 60}}, members=True)
add_item('dragon kiteshield', 1600000, equip={'amagic': -8, 'arange': -3, 'dstab': 56, 'dslash': 60, 'dcrush': 58, 'dmagic': -1, 'drange': 58, 'slot': 'shield', 'req': {'defence': 60}}, members=True)
add_item('dragon boots', 20000, equip={'amagic': -3, 'arange': -1, 'dstab': 16, 'dslash': 17, 'dcrush': 18, 'str': 4, 'slot': 'boots', 'req': {'defence': 60}}, members=True)
add_item('berserker helm', 60000, equip={'amagic': -5, 'arange': -5, 'dstab': 31, 'dslash': 29, 'dcrush': 33, 'drange': 30, 'str': 3, 'slot': 'head', 'req': {'defence': 45}}, members=True)
add_item('maple shortbow', 400, equip={'arange': 29, 'slot': 'weapon', 'req': {'ranged': 30}})
add_item('magic shortbow', 1600, equip={'arange': 69, 'slot': 'weapon', 'req': {'ranged': 50}}, members=True)
add_item('rune crossbow', 16200, equip={'arange': 90, 'slot': 'weapon', 'req': {'ranged': 61}}, members=True)
add_item('runite bolts', 300, equip={'rstr': 115, 'slot': 'ammo', 'req': {'ranged': 61}}, members=True)
add_item('adamant bolts', 58, equip={'rstr': 100, 'slot': 'ammo', 'req': {'ranged': 36}}, members=True)
add_item("green d'hide body", 7800, equip={'amagic': -15, 'arange': 15, 'dstab': 18, 'dslash': 27, 'dcrush': 24, 'dmagic': 20, 'drange': 35, 'slot': 'body', 'req': {'ranged': 40, 'defence': 40}})
add_item("green d'hide chaps", 3900, equip={'amagic': -10, 'arange': 8, 'dstab': 12, 'dslash': 15, 'dcrush': 18, 'dmagic': 8, 'drange': 17, 'slot': 'legs', 'req': {'ranged': 40}})
add_item("green d'hide vambraces", 2500, equip={'amagic': -10, 'arange': 8, 'dstab': 1, 'dslash': 2, 'dcrush': 2, 'dmagic': 2, 'slot': 'gloves', 'req': {'ranged': 40}})
add_item('coif', 200, equip={'amagic': -1, 'arange': 2, 'dstab': 4, 'dslash': 6, 'dcrush': 8, 'dmagic': 4, 'drange': 4, 'slot': 'head'})
add_item('snakeskin body', 1250, equip={'amagic': -5, 'arange': 12, 'dstab': 25, 'dslash': 28, 'dcrush': 32, 'dmagic': 15, 'drange': 35, 'slot': 'body', 'req': {'ranged': 30, 'defence': 30}}, members=True)
add_item('mystic hat', 15000, equip={'amagic': 4, 'dmagic': 4, 'slot': 'head', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic robe top', 120000, equip={'amagic': 20, 'dmagic': 20, 'slot': 'body', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic robe bottom', 80000, equip={'amagic': 15, 'dmagic': 15, 'slot': 'legs', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic gloves', 10000, equip={'amagic': 3, 'dmagic': 3, 'slot': 'gloves', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic boots', 10000, equip={'amagic': 3, 'dmagic': 3, 'slot': 'boots', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('amulet of glory', 17625, equip={'astab': 10, 'aslash': 10, 'acrush': 10, 'amagic': 10, 'arange': 10, 'dstab': 3, 'dslash': 3, 'dcrush': 3, 'dmagic': 3, 'drange': 3, 'str': 6, 'prayer': 3, 'slot': 'amulet'}, members=True)

SPELLS.update({
    "wind blast":  {"type":"combat","max":13,"lvl":41,"xp":25.5,"runes":{"air rune":3,"death rune":1}},
    "water blast": {"type":"combat","max":14,"lvl":47,"xp":28.5,"runes":{"water rune":3,"air rune":3,"death rune":1}},
    "earth blast": {"type":"combat","max":15,"lvl":53,"xp":31.5,"runes":{"earth rune":4,"air rune":3,"death rune":1}},
    "fire blast":  {"type":"combat","max":16,"lvl":59,"xp":34.5,"runes":{"fire rune":5,"air rune":4,"death rune":1}},
})

MONSTERS["king black dragon"]["drops"].append(("dragon platelegs", 1, 1, 0.03))
MONSTERS["obor"]["drops"].append(("dragon mace", 1, 1, 0.06))
# (the abyssal whip is earned from abyssal demons in the Slayer Tower)



# ===========================================================================
#  MONSTER SPRITES  (art shown at the start of a fight)
# ===========================================================================
MONSTER_ART.update({
    'man': '\n       o\n      /|\\    a man\n      / \\\n',
    'chicken farmer': '\n      _o_\n      /|\\    a chicken farmer\n      / \\\n',
    'imp': "\n     ,vv,\n     (oo)   an imp\n     /''\\\n",
    'dwarf': '\n      ___\n     (o o)   a dwarf\n     )WWW(\n',
    'minotaur': '\n     \\(oo)/   a minotaur\n      /||\\\n     _/  \\_\n',
    'thug': '\n      [--]\n     ([oo])   a thug\n      /||\\\n',
    'dark warrior': '\n      .--.\n     |x  x|   a dark warrior\n     /|##|\\\n',
    'giant spider': '\n    /\\(oo)/\\   a giant spider\n    \\/_/\\_\\/\n',
    'deadly red spider': '\n    /\\(xx)/\\   a deadly red spider\n    \\/>><<\\/\n',
    'flesh crawler': '\n    (((o)))   a flesh crawler\n     >====<\n     ^^^^^^\n',
    'zombie rat': '\n     (\\_/)\n    =(x.x)=   a zombie rat\n     (")(")\n',
    'moss giant': '\n     #####\n    ( o  o )   a moss giant\n    /|####|\\\n',
    'ice giant': '\n     *****\n    ( o  o )   an ice giant\n    /|::::|\\\n',
    'lesser demon': '\n     \\(oo)/   a lesser demon\n      )##(\n      /VV\\\n',
    'greater demon': '\n    \\\\(@@)//   a GREATER demon\n      )###(\n     /|VVV|\\\n',
    'chaos druid': '\n      ,-.\n     (o o)   a chaos druid\n     )~~~(\n',
    'jogre': '\n      ____\n    ( o  o )   a jogre\n    |  ==  |\n    /|    |\\\n',
    'paladin': '\n      .+.\n     [o o]   a paladin\n     /|+|\\\n',
    'white wolf': '\n     /\\_/\\\n    ( o o )   a white wolf\n     >\\^/<\n',
})


# ===========================================================================
#  FLETCHING  (members skill: carve logs into bows, string them with flax)
# ===========================================================================
add_item("knife", 6, tool="knife")
add_item("flax", 4)
add_item("bow string", 12)
add_item("maple logs", 64, log_fm_xp=135)
add_item("longbow", 80, equip={"slot": "weapon", "arange": 8, "req": {"ranged": 1}})
add_item("oak longbow", 160, equip={"slot": "weapon", "arange": 14, "req": {"ranged": 5}})
add_item("willow longbow", 320, members=True,
         equip={"slot": "weapon", "arange": 20, "req": {"ranged": 20}})
add_item("maple longbow", 640, members=True,
         equip={"slot": "weapon", "arange": 29, "req": {"ranged": 30}})
for _u in ["shortbow (u)", "longbow (u)", "oak shortbow (u)", "oak longbow (u)",
           "willow shortbow (u)", "willow longbow (u)", "maple shortbow (u)",
           "maple longbow (u)"]:
    add_item(_u, 8)

FLETCH_CUT = {
    # a plain shortbow is the level-1 entry point (like arrow shafts in OSRS) —
    # without it Fletching would be unstartable, no xp source below level 5
    "logs": [("shortbow (u)", 1, 5), ("longbow (u)", 10, 10)],
    "oak logs": [("oak shortbow (u)", 20, 16), ("oak longbow (u)", 25, 25)],
    "willow logs": [("willow shortbow (u)", 35, 33), ("willow longbow (u)", 40, 42)],
    "maple logs": [("maple shortbow (u)", 50, 50), ("maple longbow (u)", 55, 58)],
}
FLETCH_STRING = {
    "shortbow (u)": ("shortbow", 1, 5), "longbow (u)": ("longbow", 10, 10),
    "oak shortbow (u)": ("oak shortbow", 20, 16), "oak longbow (u)": ("oak longbow", 25, 25),
    "willow shortbow (u)": ("willow shortbow", 35, 33),
    "willow longbow (u)": ("willow longbow", 40, 42),
    "maple shortbow (u)": ("maple shortbow", 50, 50),
    "maple longbow (u)": ("maple longbow", 55, 58),
}


def cmd_fletch(p, arg):
    if not getattr(p, "members", False):
        say("Fletching is members-only. Type 'membership' to unlock it.", "bmagenta")
        return
    name = arg.strip().lower()
    cut = {u: (log, lvl, xp) for log, opts in FLETCH_CUT.items()
           for u, lvl, xp in opts}
    if not name:
        opts = []
        if p.has("knife"):
            for u, (log, lvl, xp) in cut.items():
                if p.has(log) and p.lvl("fletching") >= lvl:
                    opts.append(u)
        for u, (bow, lvl, xp) in FLETCH_STRING.items():
            if p.has(u) and p.has("bow string") and p.lvl("fletching") >= lvl:
                opts.append(bow)
        say("Fletch what? You can make: " + (", ".join(opts) if opts else
            "(need a knife + logs, or an unstrung bow + a bow string)"), "bcyan")
        return
    for u, (bow, lvl, xp) in FLETCH_STRING.items():
        if name == bow:
            if not p.has(u):
                say(f"You need a {u} first - fletch one from logs.", "byellow")
                return
            if not p.has("bow string"):
                say("You need a bow string (spin flax on a spinning wheel).", "byellow")
                return
            if p.lvl("fletching") < lvl:
                say(f"You need Fletching level {lvl} to make a {bow}.", "byellow")
                return
            p.take(u); p.take("bow string"); p.add(bow)
            say(f"You string the {u} into a {bow}.", "bcyan")
            p.gain_xp("fletching", xp)
            return True
    if name in cut:
        log, lvl, xp = cut[name]
        if not p.has("knife"):
            say("You need a knife to fletch.", "byellow")
            return
        if not p.has(log):
            say(f"You need {log} to fletch a {name}.", "byellow")
            return
        if p.lvl("fletching") < lvl:
            say(f"You need Fletching level {lvl} to fletch a {name}.", "byellow")
            return
        p.take(log); p.add(name)
        say(f"You carve the {log} into a {name}.", "bcyan")
        p.gain_xp("fletching", xp)
        return True
    say("You can't fletch that. Type 'fletch' to see options.", "grey")


HANDLERS["fletch"] = cmd_fletch
HANDLERS["string"] = cmd_fletch
BATCHABLE.add("fletch")     # 'fletch willow shortbow (u) 10' cuts a batch
BATCHABLE.add("string")     # 'string maple longbow 10' strings a batch

# Sources in Kandarin + supply shops
TREES["maple"] = ("maple logs", 45, 100)
ROOMS["seers_village"]["trees"] = ["maple"]
ROOMS["seers_village"]["spinning_wheel"] = True
ROOMS["catherby"]["trees"] = ["tree", "oak", "willow"]
SHOPS["general"]["knife"] = 6
SHOPS["crafting"]["knife"] = 6
SHOPS["crafting"]["flax"] = 4
SHOPS["crafting"]["bow string"] = 12


