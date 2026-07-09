# ===========================================================================
#  TWO-HANDED WEAPONS  (both hands or none — no shield alongside these)
# ===========================================================================
_TWO_HANDED = [
    # every bow needs a draw arm (crossbows are one-handed, bar Karil's)
    "shortbow", "longbow", "oak shortbow", "oak longbow", "willow shortbow",
    "willow longbow", "maple shortbow", "maple longbow", "yew shortbow",
    "yew longbow", "magic shortbow", "magic longbow", "karil's crossbow",
    # great weapons
    "bandos godsword", "armadyl godsword", "zamorak godsword",
    "saradomin godsword", "dharok's greataxe", "guthan's warspear",
    "torag's hammers", "verac's flail", "zamorakian spear",
    "saradomin sword", "granite maul", "hill giant club",
    "abyssal bludgeon",
]
for _n in _TWO_HANDED:
    if _n in ITEMS and ITEMS[_n].get("equip"):
        ITEMS[_n]["equip"]["two_handed"] = True


# ===========================================================================
#  DESCRIPTION POLISH  (rooms that accumulated bolted-on hints get rewritten
#  as one clean paragraph — keep every 'keyword' players need)
# ===========================================================================
for _room, _desc in {
    "draynor_village": (
        "A run-down village where willows lean over the riverbank and "
        "fishing spots bubble in the shallows. Morgan looks terrified, "
        "Aggie's cauldron reeks, the Wise Old Man watches from his doorway, "
        "and a seed stall does quiet business in the market. A squat jail "
        "stands at the edge of town ('jail'), and the manor looms north."),
    "falador_square": (
        "The white-walled heart of Asgarnia. Doric the dwarf works his "
        "forge near the square, the White Knights' Castle rises north "
        "('castle'), Falador Park lies just beyond ('park'), and a mine "
        "shaft drops away to the south."),
    "port_sarim": (
        "A busy port smelling of tar and fish. Klarense tends the Lady "
        "Lumbridge at her mooring, boats run south to Karamja, and the "
        "fishing shop serves the docks. Mudskipper Point lies along the "
        "coast ('point')."),
    "edgeville": (
        "A frontier town on the Wilderness' doorstep, with a bank, a "
        "furnace, and old yews south of the wall. Vannaka the Slayer "
        "Master takes names here, Oziach's shabby hut sits by the river "
        "('hut'), and a dungeon mouth gapes below ('down'). North, past "
        "the ditch, the law runs out."),
    "varrock_east_bank": (
        "A bank on Varrock's east side. The road north leads to the Grand "
        "Exchange, standing stones rise to the north-east ('altar'), and "
        "the long road east runs for the River Salve and Paterdomus."),
    "karamja_port": (
        "A tropical island port under swaying banana palms ('pick'). The "
        "dock heaves with lobster pots and harpoon fishers, a volcano "
        "smokes inland ('volcano'), and Brimhaven lies east along the "
        "coast."),
    "rimmington": (
        "A small mining village with Doric's spare anvil and a scatter of "
        "copper, tin, iron and clay rocks. Your house plot sits west of "
        "the village ('house'), and the sealed ruin of Melzar's Maze "
        "stands to the north ('maze')."),
    "grand_exchange": (
        "Traders from across Gielinor shout prices under the great arches. "
        "A bank is on site, and a sawmill creaks just north ('mill')."),
    "monastery": (
        "A peaceful monastery where monks tend the altar — and their "
        "pockets jingle with coin. A path climbs toward the Mind Altar "
        "('altar'), and to the north the Black Knights' Fortress glowers "
        "on Ice Mountain ('fortress')."),
    "deep_wilderness": (
        "The lawless wastes stretch to the horizon. Dark warriors, giants "
        "and green dragons roam the blasted ground, an agility course "
        "sways over a ravine ('course'), the Chaos Temple squats to the "
        "north ('temple'), a frozen chasm yawns where the God Wars rage "
        "below ('chasm') — and west, the warlords keep their lairs "
        "('wastes')."),
    "ardougne": (
        "A grand split city. Market stalls line the square — baked goods, "
        "silk, glittering gems — pickpockets work the crowds, and paladins "
        "patrol the palace walls. Tilled farming patches sit north of the "
        "market, and hunting grounds stretch south. Baxtorian Falls "
        "thunders upriver ('falls'), the Tree Gnome Stronghold rises west "
        "('gnome'), and walled Yanille guards the far road ('yanille'). "
        "(members)"),
    "lumbridge_church": (
        "A quiet stone church where Father Aereck tends the altar and "
        "prayers are restored. Ancient yews shade the graveyard out back."),
}.items():
    ROOMS[_room]["desc"] = _desc


if __name__ == "__main__":
    main()
