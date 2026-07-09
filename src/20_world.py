# ===========================================================================
#  WORLD MAP
# ===========================================================================
# Each room: name, desc, exits{dir:roomkey}, plus optional service flags:
#   bank, range, furnace, anvil, ge, spinning_wheel, altar(rune name)
#   trees[], rocks[], fish_tools[], monsters[], shop, npc(quest key)
ROOMS = {
    # ---- Lumbridge -------------------------------------------------------
    "lumbridge_castle": dict(
        name="Lumbridge Castle",
        desc="The home of Duke Horacio. A cooking range warms the kitchen, a "
             "bank sits upstairs, and a spinning wheel hums in the hall. The "
             "Cook frets by the ovens.",
        exits={"north": "general_store", "east": "river_lum", "south": "swamp",
               "west": "cow_field", "church": "lumbridge_church"},
        bank=True, range=True, spinning_wheel=True, npc="cooks_assistant"),
    "general_store": dict(
        name="Lumbridge General Store",
        desc="A well-stocked shop selling adventuring basics.",
        exits={"south": "lumbridge_castle", "north": "lumbridge_forest",
               "east": "lumbridge_farm"},
        shop="general"),
    "lumbridge_forest": dict(
        name="Lumbridge Forest",
        desc="Trees crowd the road north to Varrock. Goblins grunt in the brush.",
        exits={"south": "general_store", "north": "varrock_gate"},
        trees=["tree", "oak"], monsters=["goblin"]),
    "lumbridge_farm": dict(
        name="Lumbridge Farm",
        desc="Chickens, a cow, a wheat field and sheep. Farmer Fred is here.",
        exits={"west": "general_store", "north": "windmill"},
        monsters=["chicken"], npc="sheep_shearer", pickpocket=["farmer"]),
    "windmill": dict(
        name="Lumbridge Windmill",
        desc="Grain becomes flour here if you have an empty pot.",
        exits={"south": "lumbridge_farm"}),
    "river_lum": dict(
        name="River Lum",
        desc="A fishing spot teeming with shrimp. A toll bridge leads east to "
             "Al Kharid.",
        exits={"west": "lumbridge_castle", "east": "al_kharid_gate"},
        fish_tools=["net"]),
    "swamp": dict(
        name="Lumbridge Swamp",
        desc="Copper and tin rocks dot the misty ground.",
        exits={"north": "lumbridge_castle"}, rocks=["copper", "tin", "clay"]),
    "cow_field": dict(
        name="Lumbridge Cow Field",
        desc="A fenced field full of cows and sheep. Good for combat, hides, "
             "and wool.",
        exits={"east": "lumbridge_castle", "west": "draynor_path"},
        monsters=["cow"]),
    # ---- Al Kharid -------------------------------------------------------
    "al_kharid_gate": dict(
        name="Al Kharid Toll Gate",
        desc="A gate guard demands 10 coins to pass east into Al Kharid.",
        exits={"west": "river_lum", "east": "al_kharid_square"}, toll=10),
    "al_kharid_square": dict(
        name="Al Kharid",
        desc="A desert city with a bank, furnace, range, a scimitar shop and a "
             "tanner. Scorpions skitter at the edges.",
        exits={"west": "al_kharid_gate", "north": "al_kharid_mine",
               "east": "al_kharid_palace"},
        bank=True, furnace=True, range=True, tanner=True, shop="scimitar",
        monsters=["scorpion"], pickpocket=["man"]),
    "al_kharid_mine": dict(
        name="Al Kharid Mine",
        desc="A rich mine: iron, silver, coal, gold, mithril and adamantite.",
        exits={"south": "al_kharid_square"},
        rocks=["iron", "silver", "coal", "gold", "mithril", "adamantite"]),
    "al_kharid_palace": dict(
        name="Al Kharid Palace",
        desc="The palace of Emir. Guards watch the gleaming halls.",
        exits={"west": "al_kharid_square"}),
    # ---- Draynor ---------------------------------------------------------
    "draynor_path": dict(
        name="Draynor Path",
        desc="A path winding west to Draynor Village.",
        exits={"east": "cow_field", "west": "draynor_village"}),
    "draynor_village": dict(
        name="Draynor Village",
        desc="A run-down village with a bank, willow trees by the river, a "
             "wheat field, and Morgan, who looks terrified.",
        exits={"east": "draynor_path", "north": "draynor_manor",
               "south": "wizard_tower"},
        bank=True, trees=["willow"], npc=["vampyre_slayer", "witch_potion"]),
    "draynor_manor": dict(
        name="Draynor Manor",
        desc="A gloomy manor. Skeletons and zombies roam, and Count Draynor "
             "lurks within.",
        exits={"south": "draynor_village"},
        monsters=["skeleton", "zombie"], npc="ernest_chicken"),
    # ---- Varrock ---------------------------------------------------------
    "varrock_gate": dict(
        name="Varrock South Gate",
        desc="The southern entrance to Varrock, capital of Misthalin. The "
             "Champions' Guild stands to the south-west ('guild').",
        exits={"south": "lumbridge_forest", "north": "varrock_square"}),
    "varrock_square": dict(
        name="Varrock Square",
        desc="A bustling plaza with a fountain. Romeo paces, lovesick, and "
             "townsfolk mill about.",
        exits={"south": "varrock_gate", "west": "varrock_west_bank",
               "east": "varrock_east_bank", "north": "varrock_palace"},
        npc="romeo_juliet", pickpocket=["man", "woman"]),
    "varrock_west_bank": dict(
        name="West Varrock",
        desc="A bank, the sword shop, an anvil for smithing, and Aubury's rune "
             "shop with a portal to the rune essence mine.",
        exits={"east": "varrock_square", "west": "barbarian_village",
               "essence": "essence_mine"},
        bank=True, anvil=True, shop="rune"),
    "varrock_east_bank": dict(
        name="East Varrock",
        desc="A bank near the road north to the Grand Exchange.",
        exits={"west": "varrock_square", "north": "grand_exchange"}, bank=True),
    "grand_exchange": dict(
        name="Grand Exchange",
        desc="Traders from across Gielinor buy and sell here. A bank is on site.",
        exits={"south": "varrock_east_bank"}, bank=True, ge=True),
    "varrock_palace": dict(
        name="Varrock Palace",
        desc="King Roald's palace, patrolled by guards.",
        exits={"south": "varrock_square", "down": "varrock_sewers"},
        monsters=["guard"], pickpocket=["guard"]),
    "essence_mine": dict(
        name="Rune Essence Mine",
        desc="A mystical cavern of pure rune essence. A portal leads back out.",
        exits={"out": "varrock_west_bank"}, rocks=["rune essence"]),
    # ---- Barbarian Village / Edgeville / Wilderness ----------------------
    "barbarian_village": dict(
        name="Barbarian Village",
        desc="Rowdy barbarians, a mine, and a river for fly fishing trout and "
             "salmon.",
        exits={"east": "varrock_west_bank", "west": "falador_east",
               "north": "edgeville", "down": "stronghold_security",
               "agility": "agility_course"},
        rocks=["copper", "tin", "iron", "coal"], fish_tools=["fly"],
        monsters=["barbarian"]),
    "edgeville": dict(
        name="Edgeville",
        desc="A frontier town with a bank and furnace. Vannaka the Slayer "
             "Master is here, and Oziach the armourer keeps a hut by the "
             "river ('hut'). A dungeon lies below, and the Wilderness ditch "
             "is to the north.",
        exits={"south": "barbarian_village", "north": "wilderness_edge",
               "down": "edgeville_dungeon"},
        bank=True, furnace=True, npc="slayer_master", shop="herblore"),
    "edgeville_dungeon": dict(
        name="Edgeville Dungeon",
        desc="A dank dungeon. Hobgoblins and hill giants prowl the dark. A "
             "huge locked door bars the way to a giant's lair — a giant key "
             "would open it.",
        exits={"up": "edgeville", "deeper": "members_dungeon",
               "giant": "giant_lair"},
        monsters=["hobgoblin", "hill giant", "giant spider"]),
    "giant_lair": dict(
        name="Obor's Lair",
        desc="A cavernous vault littered with shattered bones. Obor, the Hill "
             "Giant boss, looms in the gloom.",
        exits={"out": "edgeville_dungeon"},
        monsters=["obor"], key="giant key"),
    "wilderness_edge": dict(
        name="Edge of the Wilderness",
        desc="Past this ditch lies the lawless Wilderness. Dark wizards and "
             "skeletons haunt the wastes. Tread carefully.",
        exits={"south": "edgeville", "deep": "kbd_lair"},
        monsters=["dark wizard", "skeleton", "dark warrior"]),
    # ---- Falador / Dwarven Mine ------------------------------------------
    "falador_east": dict(
        name="East Falador",
        desc="The eastern gate of Falador, with a bank.",
        exits={"east": "barbarian_village", "west": "falador_square"},
        bank=True),
    "falador_square": dict(
        name="Falador",
        desc="The white-walled city of Asgarnia. Doric the dwarf works nearby, "
             "and a mine lies south.",
        exits={"east": "falador_east", "west": "falador_west",
               "south": "dwarven_mine"},
        npc="dorics_quest"),
    "falador_west": dict(
        name="West Falador",
        desc="A bank and the road south toward Rimmington.",
        exits={"east": "falador_square", "south": "rimmington",
               "altar": "air_altar"}, bank=True),
    "dwarven_mine": dict(
        name="Dwarven Mine",
        desc="A deep mine of coal, iron, mithril and gold. Scorpions lurk.",
        exits={"north": "falador_square"},
        rocks=["iron", "coal", "gold", "mithril"], monsters=["scorpion", "dwarf"]),
    # ---- Rimmington / Port Sarim / Karamja -------------------------------
    "rimmington": dict(
        name="Rimmington",
        desc="A small mining village with Doric's anvil. Copper, tin, iron and "
             "clay rocks are here. To the north loom the ruins of Melzar's "
             "Maze ('maze').",
        exits={"north": "falador_west", "east": "port_sarim"},
        rocks=["copper", "tin", "iron", "clay"], anvil=True),
    "port_sarim": dict(
        name="Port Sarim",
        desc="A busy port with a fishing shop and a food shop. Boats sail south "
             "to Karamja, and Klarense tends his ship, the Lady Lumbridge, at "
             "the dock.",
        exits={"west": "rimmington", "south": "karamja_port"},
        shop="fishing"),
    "karamja_port": dict(
        name="Karamja (Musa Point)",
        desc="A tropical island port. Fishing spots line the docks; a volcano "
             "smokes in the distance.",
        exits={"north": "port_sarim"}, fish_tools=["net", "rod"]),
    # ---- New areas ---------------------------------------------------
    "lumbridge_church": dict(
        name="Lumbridge Church",
        desc="A quiet stone church with a graveyard out back. Father Aereck "
             "tends the altar, and prayers can be restored here.",
        exits={"out": "lumbridge_castle"},
        prayer_altar=True, npc="restless_ghost"),
    "varrock_sewers": dict(
        name="Varrock Sewers",
        desc="A reeking warren beneath the palace, crawling with rats, zombies "
             "and giant spiders.",
        exits={"up": "varrock_palace"},
        monsters=["giant rat", "zombie", "giant spider"]),
    "wizard_tower": dict(
        name="Wizard's Tower",
        desc="A tower of mages south of Draynor. Sedridor studies runes in the "
             "basement, and mischievous imps flit about.",
        exits={"north": "draynor_village"},
        monsters=["imp"], npc=["rune_mysteries", "imp_catcher"]),
    "stronghold_security": dict(
        name="Stronghold of Security",
        desc="A monster-filled dungeon beneath Barbarian Village. Minotaurs and "
             "flesh crawlers roam its halls — and treasure awaits the brave.",
        exits={"up": "barbarian_village"},
        monsters=["minotaur", "flesh crawler", "zombie rat"], stronghold=True),
    "air_altar": dict(
        name="Air Altar",
        desc="A mystical altar humming with air magic. Bind rune essence into "
             "air runes here.",
        exits={"out": "falador_west"}, altar="air"),
    # ---- Members areas (require membership) -------------------------------
    "members_dungeon": dict(
        name="Deep Dungeon",
        desc="A forbidding cavern far below Edgeville. Moss giants and demons "
             "lurk in the gloom. (members)",
        exits={"up": "edgeville_dungeon"},
        monsters=["moss giant", "ice giant", "lesser demon", "greater demon"],
        members=True),
    "kbd_lair": dict(
        name="Lair of the King Black Dragon",
        desc="A scorched lair deep in the Wilderness. The King Black Dragon "
             "broods over a hoard of treasure. (members)",
        exits={"out": "wilderness_edge"},
        monsters=["king black dragon"], members=True),
    "agility_course": dict(
        name="Barbarian Agility Course",
        desc="A rickety obstacle course of ropes, beams and ledges. Run laps to "
             "train agility. (members)",
        exits={"out": "barbarian_village"}, members=True, agility_course=True),
}


