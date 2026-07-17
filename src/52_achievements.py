# ===========================================================================
#  ACHIEVEMENTS
# ===========================================================================
ACHIEVEMENTS = {
    "first_blood":  ("First Blood", "Defeat your first monster."),
    "apprentice":   ("Apprentice", "Reach total level 100."),
    "adventurer":   ("Adventurer", "Reach total level 500."),
    "veteran":      ("Veteran", "Reach total level 1000."),
    "skill_master": ("Skill Master", "Reach level 99 in any skill."),
    "quester":      ("Quester", "Complete 3 quests."),
    "hero":         ("Hero of Gielinor", "Complete every quest."),
    "herbalist":    ("Herbalist", "Brew your first potion."),
    "dragonslayer": ("Dragonslayer", "Defeat the King Black Dragon."),
    "giant_slayer": ("Giant Slayer", "Defeat Obor, the Hill Giant boss."),
    "crandor_saved": ("Crandor's Saviour", "Complete the Dragon Slayer quest."),
    "fire_cape": ("JalYt Champion", "Conquer the Fight Caves and earn the "
                  "fire cape."),
    "grave_robber": ("Grave Robber", "Put all six Barrows brothers to rest "
                     "and loot the chest."),
    "whack_a_mole": ("Whack-a-Mole", "Defeat the Giant Mole beneath "
                     "Falador Park."),
    "green_thumb": ("Green Thumb", "Harvest 25 crops from your patches."),
    "god_slayer": ("God Slayer", "Defeat all four generals of the God Wars "
                   "Dungeon."),
    "taskmaster": ("Taskmaster", "Reach a 10-task slayer streak."),
    "hive_slayer": ("Hive Slayer", "Defeat both bodies of the Kalphite "
                    "Queen."),
    "king_slayer": ("Kingsbane", "Defeat all three Dagannoth Kings."),
    "infernal": ("The Infernal", "Defeat TzKal-Zuk at the bottom of the "
                 "Inferno."),
    "dreamless": ("Dreamless", "Wake Slepe: defeat the Nightmare."),
    "warlord": ("Lord of the Wastes", "Defeat Callisto, Venenatis, "
                "Vet'ion and the Corporeal Beast."),
    "apex_slayer": ("Apex Predator", "Defeat all five slayer "
                    "superbosses."),
    "snake_charmer": ("Snake Charmer", "Defeat Zulrah, the serpent of "
                      "Zul-Andra."),
    "dragonkin_bane": ("Dragonkin's Bane", "Complete Dragon Slayer II."),
    "vorkath":      ("Vorkath", "Slay Vorkath, the undead dragon of "
                     "Ungael."),
    "crystal_singer": ("Crystal Singer", "Complete Song of the Elves and "
                       "open Prifddinas."),
    "monkey_business": ("Monkey Business", "Complete Monkey Madness and "
                        "avenge the 10th squad."),
    "regent": ("Regent", "Be crowned regent of Miscellania."),
    "dreamer": ("Dreamer", "Out-dream yourself and earn the lunar "
                "spellbook."),
    "gauntleted":   ("Gauntleted", "Defeat the Crystalline Hunllef."),
    "stonebreaker": ("Stonebreaker", "Crack Zalcano with a pickaxe."),
    "rich":         ("Wealthy", "Hold 100,000 coins."),
}


def _earned_achievements(p):
    got = set()
    total = sum(p.base_lvl(s) for s in SKILLS)
    if getattr(p, "kills", 0) >= 1:
        got.add("first_blood")
    if total >= 100:
        got.add("apprentice")
    if total >= 500:
        got.add("adventurer")
    if total >= 1000:
        got.add("veteran")
    if any(p.base_lvl(s) >= 99 for s in SKILLS):
        got.add("skill_master")
    done = sum(1 for k in ALL_QUESTS if _q(p, k) == "complete")
    if done >= 3:
        got.add("quester")
    if done >= len(ALL_QUESTS):
        got.add("hero")
    if getattr(p, "potions_made", 0) >= 1:
        got.add("herbalist")
    bosses = getattr(p, "bosses", [])
    if "king black dragon" in bosses:
        got.add("dragonslayer")
    if "obor" in bosses:
        got.add("giant_slayer")
    if _q(p, "dragon_slayer") == "complete":
        got.add("crandor_saved")
    if "tztok-jad" in bosses:
        got.add("fire_cape")
    if getattr(p, "barrows_loots", 0) >= 1:
        got.add("grave_robber")
    if "giant mole" in bosses:
        got.add("whack_a_mole")
    if getattr(p, "crops", 0) >= 25:
        got.add("green_thumb")
    if all(g in bosses for g in ("general graardor", "kree'arra",
                                 "k'ril tsutsaroth", "commander zilyana")):
        got.add("god_slayer")
    if getattr(p, "task_streak", 0) >= 10:
        got.add("taskmaster")
    if "kalphite queen" in bosses:
        got.add("hive_slayer")
    if all(k in bosses for k in ("dagannoth rex", "dagannoth prime",
                                 "dagannoth supreme")):
        got.add("king_slayer")
    if "tzkal-zuk" in bosses:
        got.add("infernal")
    if "the nightmare" in bosses:
        got.add("dreamless")
    if all(w in bosses for w in ("callisto", "venenatis", "vet'ion",
                                 "corporeal beast")):
        got.add("warlord")
    if all(b in bosses for b in ("kraken", "cerberus", "abyssal sire",
                                 "grotesque guardians",
                                 "thermonuclear smoke devil")):
        got.add("apex_slayer")
    if "zulrah" in bosses:
        got.add("snake_charmer")
    if _q(p, "dragon_slayer_2") == "complete":
        got.add("dragonkin_bane")
    if "vorkath" in bosses:
        got.add("vorkath")
    if _q(p, "song_of_the_elves") == "complete":
        got.add("crystal_singer")
    if _q(p, "monkey_madness") == "complete":
        got.add("monkey_business")
    if _q(p, "throne_of_miscellania") == "complete":
        got.add("regent")
    if _q(p, "lunar_diplomacy") == "complete":
        got.add("dreamer")
    if "crystalline hunllef" in bosses:
        got.add("gauntleted")
    if "zalcano" in bosses:
        got.add("stonebreaker")
    if p.coins >= 100000:
        got.add("rich")
    return got


def _check_achievements(p):
    """Unlock + announce any newly earned achievements."""
    have = getattr(p, "achievements", None)
    if have is None:
        p.achievements = have = []
    for key in _earned_achievements(p):
        if key not in have:
            have.append(key)
            title, desc = ACHIEVEMENTS[key]
            print()
            banner("ACHIEVEMENT UNLOCKED", color="gold", line_color="byellow")
            print("  " + paint("★ " + title, "byellow", "bold")
                  + paint("  —  " + desc, "grey"))


def cmd_achievements(p, _a):
    have = set(getattr(p, "achievements", []))
    banner(f"Achievements  ({len(have)}/{len(ACHIEVEMENTS)})", color="gold")
    for key, (title, desc) in ACHIEVEMENTS.items():
        if key in have:
            print("  " + paint("★ ", "byellow")
                  + paint(f"{title:18}", "byellow", "bold") + paint(desc, "grey"))
        else:
            print("  " + paint("☆ ", "grey")
                  + paint(f"{title:18}", "grey") + paint(desc, "grey"))


def cmd_task(p, _a):
    if not getattr(p, "members", False):
        say("Slayer is members-only. Type 'membership' to unlock it.", "bmagenta")
        return
    banner("Slayer", color="teal", line_color="teal")
    print("  " + paint(f"Slayer level {p.lvl('slayer')}", "teal")
          + paint(f"    Points: {p.slayer_points}", "white"))
    t = getattr(p, "slayer_task", None)
    if t and t["remaining"] > 0:
        print("  " + paint(f"Task: slay {t['remaining']}/{t['amount']} "
                           f"{t['monster']}s", "white"))
        locs = sorted({ROOMS[k]["name"] for k, r in ROOMS.items()
                       if t["monster"] in r.get("monsters", [])})
        if locs:
            print("  " + paint("Found at: " + ", ".join(locs[:4]), "grey"))
    else:
        print("  " + paint("No active task — see Vannaka, the Slayer Master in "
                           "Edgeville.", "grey"))
    print("  " + paint(f"Task streak: {getattr(p, 'task_streak', 0)} "
                       "(bonus points at every 5th and 10th)", "teal"))
    print("  " + paint("Spend points with 'slayerbuy' (helmet, gear, xp, "
                       "skips \u2014 skipping resets your streak).", "grey"))


def cmd_search(p, _a):
    loc = p.location
    if loc == "draynor_village" and _q(p, "romeo_juliet") == "started" \
            and not p.has("message"):
        p.add("message")
        say("You find Juliet here. She gives you a heartfelt message for Romeo. "
            "Take it back to Varrock Square!")
        return
    if loc == "varrock_sewers" and _q(p, "restless_ghost") == "started" \
            and not p.has("ghost's skull"):
        p.add("ghost's skull")
        say("Among the filth you spot a grinning skull — the ghost's! You pocket it.")
        return
    if loc == "draynor_manor" and _q(p, "ernest_chicken") == "started":
        for part in ["oil can", "pressure gauge", "rubber tube"]:
            if not p.has(part):
                p.add(part)
                say(f"You rummage through the manor and find a {part}.")
                return
    if _q(p, "dragon_slayer") == "maps":
        if loc == "melzars_maze" and not p.has("melzar's map piece"):
            p.add("melzar's map piece")
            say("Behind a crumbling wall you find Melzar's old strongbox — "
                "inside lies MELZAR'S MAP PIECE, one third of the route to "
                "Crandor!", "bgreen")
            return
        if loc == "draynor_manor" and not p.has("lozar's map piece"):
            p.add("lozar's map piece")
            say("In the manor's cellar a magic chest clicks open at your "
                "touch — LOZAR'S MAP PIECE is yours!", "bgreen")
            return
    if loc == "black_knights_fortress" and _q(p, "black_knights") == "infiltrate":
        if p.has("cabbage"):
            p.take("cabbage")
            p.quests["black_knights"] = "sabotaged"
            say("You creep to a listening-hole. Below, a witch stirs a vast "
                "cauldron — the invincibility potion! You drop your CABBAGE "
                "down the chimney. The brew hisses, turns pink, and curdles. "
                "Sabotage complete — report to Sir Amik Varze!", "bgreen")
        else:
            say("You find the chimney over the witch's cauldron. Something "
                "vile dropped in would ruin the potion forever... a CABBAGE, "
                "say. (The general store sells them.)", "byellow")
        return
    if loc == "draynor_jail" and _q(p, "prince_ali") == "rescue":
        p.take("blonde wig")
        p.take("bronze key")
        p.quests["prince_ali"] = "freed"
        say("You slip the bronze key into the lock while Lady Keli's back is "
            "turned. Prince Ali dons the wig and strolls out disguised — free! "
            "Return to Osman at the Al Kharid palace.", "bgreen")
        return
    if loc == "baxtorian_falls" and _q(p, "waterfall_quest") == "started":
        p.add("glarial's amulet")
        p.quests["waterfall_quest"] = "amulet"
        say("Beneath a moss-grown tombstone you find GLARIAL'S AMULET. The "
            "roar of the falls seems to open like a door — the cave behind "
            "the water will admit you now ('cave').", "bgreen")
        return
    if loc == "waterfall_cave" and _q(p, "waterfall_quest") == "amulet":
        _complete_banner("Waterfall Quest")
        say("Past the sleeping guardians you set Glarial's amulet on the "
            "altar of Baxtorian. The chalice fills with light — and with "
            "understanding. 13,750 attack AND strength xp awarded!",
            "gold", "bold")
        p.gain_xp("attack", 13750)
        p.gain_xp("strength", 13750)
        p.quests["waterfall_quest"] = "complete"
        return
    if loc == "camelot" and _q(p, "merlins_crystal") in ("excalibur",
                                                         "shatter"):
        if p.has("excalibur") or "excalibur" in p.equipment.values():
            _complete_banner("Merlin's Crystal")
            say("You climb the tower and strike the crystal with EXCALIBUR. "
                "It rings once, like a bell, and falls away in shards. "
                "Merlin steps out, brushing centuries off his robes: "
                "\"Took your time.\" King Arthur is overjoyed!",
                "gold", "bold")
            p.quests["merlins_crystal"] = "complete"
        else:
            say("The crystal atop the tower shrugs off everything you try. "
                "Only EXCALIBUR will crack it.", "byellow")
        return
    say("You find nothing of interest.")


