# ===========================================================================
#  QUESTS
# ===========================================================================
# npc key -> the name players see (and can 'talk <name>' to)
NPC_NAMES = {
    "cooks_assistant": "the Cook", "sheep_shearer": "Farmer Fred",
    "dorics_quest": "Doric", "romeo_juliet": "Romeo",
    "vampyre_slayer": "Morgan", "restless_ghost": "Father Aereck",
    "rune_mysteries": "Sedridor", "imp_catcher": "Wizard Mizgog",
    "witch_potion": "Aggie", "ernest_chicken": "Professor Oddenstein",
    "slayer_master": "Vannaka", "dragon_slayer": "the Guildmaster",
    "oziach": "Oziach", "klarense": "Klarense",
    "knights_sword": "the squire", "thurgo": "Thurgo",
    "prince_ali": "Osman", "black_knights": "Sir Amik Varze",
}


def cmd_talk(p, arg=""):
    npc = ROOMS[p.location].get("npc")
    if not npc:
        say("There's no one here to talk to.")
        return
    npcs = npc if isinstance(npc, list) else [npc]
    want = (arg or "").strip().lower()
    if want:                       # 'talk <name>' picks a specific person
        picks = [k for k in npcs if want in NPC_NAMES.get(k, k).lower()]
        if not picks:
            say("No one by that name here. You can talk to: "
                + ", ".join(NPC_NAMES.get(k, k) for k in npcs) + ".")
            return
        target = picks[0]
    else:
        # talk to whoever still has an unfinished quest; else the last NPC
        target = next((k for k in npcs if _q(p, k) != "complete"), npcs[-1])
        if len(npcs) > 1:
            say("(Here: " + ", ".join(NPC_NAMES.get(k, k) for k in npcs)
                + " — 'talk <name>' to pick.)", "grey")
    QUEST_TALK[target](p)


def _q(p, key):
    return p.quests.get(key, "not_started")


def talk_cook(p):
    stage = _q(p, "cooks_assistant")
    if stage == "not_started":
        banner("Quest Start: Cook's Assistant", color="purple", line_color="bmagenta")
        say("\"It's the Duke's birthday and I've ruined the cake! Fetch me an "
            "EGG, a BUCKET OF MILK and a POT OF FLOUR. The farm is past "
            "the general store — north, then east!\"")
        say("He hands you an empty bucket and pot.")
        p.add("bucket")
        p.add("pot")
        p.quests["cooks_assistant"] = "started"
    elif stage == "started":
        need = ["egg", "bucket of milk", "pot of flour"]
        missing = [i for i in need if not p.has(i)]
        if missing:
            say("\"Still missing: " + ", ".join(missing) + "!\"")
        else:
            for i in need:
                p.take(i)
            show_art(ART_QUEST, "gold", center=True)
            banner("QUEST COMPLETE: Cook's Assistant", color="byellow", line_color="gold")
            say("\"The cake is saved!\" 300 cooking xp and 200 coins.")
            p.add("coins", 200)
            p.gain_xp("cooking", 300)
            p.quests["cooks_assistant"] = "complete"
    else:
        say("\"Thanks again for saving the cake!\"")


def talk_farmer(p):
    stage = _q(p, "sheep_shearer")
    if stage == "not_started":
        banner("Quest Start: Sheep Shearer", color="purple", line_color="bmagenta")
        say("Farmer Fred: \"Shear my sheep and spin the wool — bring me 6 balls "
            "of wool and I'll reward you.\" ('shear' sheep, then 'spin' wool at "
            "Lumbridge Castle.)")
        p.quests["sheep_shearer"] = "started"
    elif stage == "started":
        if p.count("ball of wool") >= 6:
            p.take("ball of wool", 6)
            show_art(ART_QUEST, "gold", center=True)
            banner("QUEST COMPLETE: Sheep Shearer", color="byellow", line_color="gold")
            say("Farmer Fred pays you 60 coins and 150 crafting xp.")
            p.add("coins", 60)
            p.gain_xp("crafting", 150)
            p.quests["sheep_shearer"] = "complete"
        else:
            say(f"\"You've got {p.count('ball of wool')}/6 balls of wool.\"")
    else:
        say("Farmer Fred: \"Fine work, shepherd.\"")


def talk_doric(p):
    stage = _q(p, "dorics_quest")
    if stage == "not_started":
        banner("Quest Start: Doric's Quest", color="purple", line_color="bmagenta")
        say("Doric: \"Use my anvils? First fetch me 6 CLAY, 4 COPPER ORE and 2 "
            "IRON ORE for my work.\"")
        p.quests["dorics_quest"] = "started"
    elif stage == "started":
        need = {"clay": 6, "copper ore": 4, "iron ore": 2}
        missing = [f"{q}x {i}" for i, q in need.items() if not p.has(i, q)]
        if missing:
            say("\"Still need: " + ", ".join(missing) + "\"")
        else:
            for i, q in need.items():
                p.take(i, q)
            show_art(ART_QUEST, "gold", center=True)
            banner("QUEST COMPLETE: Doric's Quest", color="byellow", line_color="gold")
            say("Doric gives you 180 mining xp and 200 coins.")
            p.gain_xp("mining", 180)
            p.add("coins", 200)
            p.quests["dorics_quest"] = "complete"
    else:
        say("Doric: \"Use the anvils any time!\"")


def talk_romeo(p):
    stage = _q(p, "romeo_juliet")
    if stage == "not_started":
        banner("Quest Start: Romeo & Juliet", color="purple", line_color="bmagenta")
        say("Romeo: \"Find my Juliet and bring me a MESSAGE of her love! She's "
            "in the house west of here.\" (He gives you a token to find her.)")
        p.add("message")
        ITEMS.setdefault("message", {"value": 1})
        p.quests["romeo_juliet"] = "started"
    elif stage == "started":
        if p.has("message"):
            p.take("message")
            show_art(ART_QUEST, "gold", center=True)
            banner("QUEST COMPLETE: Romeo & Juliet", color="byellow", line_color="gold")
            say("Romeo weeps with joy. 5 quest points... and 150 coins.")
            p.add("coins", 150)
            p.quests["romeo_juliet"] = "complete"
        else:
            say("Romeo: \"Where is her message?!\"")
    else:
        say("Romeo: \"My thanks, friend!\"")


def talk_morgan(p):
    stage = _q(p, "vampyre_slayer")
    if stage == "not_started":
        banner("Quest Start: Vampyre Slayer", color="purple", line_color="bmagenta")
        say("Morgan: \"Count Draynor, a vampyre, terrorises us! Take this STAKE "
            "and a HAMMER, and slay him in the manor to the north!\"")
        p.add("stake")
        p.quests["vampyre_slayer"] = "started"   # the count now stalks the manor
    elif stage == "complete":
        say("Morgan: \"You saved us all!\"")
    else:
        say("Morgan: \"The Count still lives! Slay him in the manor!\"")


def _need_msg(npc, missing):
    say(f"{npc}: \"You still need: " + ", ".join(missing) + ".\"")


def _complete_banner(title):
    show_art(ART_QUEST, "gold", center=True)
    banner(f"QUEST COMPLETE: {title}", color="byellow", line_color="gold")


def talk_aereck(p):
    stage = _q(p, "restless_ghost")
    if stage == "not_started":
        banner("Quest Start: The Restless Ghost", color="purple", line_color="bmagenta")
        say("Father Aereck: \"A ghost haunts my graveyard! He lost his SKULL — "
            "it's down in the Varrock sewers. 'search' there, fetch it, and lay "
            "him to rest.\"")
        p.quests["restless_ghost"] = "started"
    elif stage == "started":
        if p.has("ghost's skull"):
            p.take("ghost's skull")
            _complete_banner("The Restless Ghost")
            say("You return the skull and the ghost fades away in peace. "
                "1125 prayer xp awarded!")
            p.gain_xp("prayer", 1125)
            p.quests["restless_ghost"] = "complete"
        else:
            say("Father Aereck: \"The skull is in the Varrock sewers — 'search' "
                "the muck down there.\"")
    else:
        say("Father Aereck: \"Bless you for freeing that poor soul.\"")


def talk_sedridor(p):
    stage = _q(p, "rune_mysteries")
    if stage == "not_started":
        banner("Quest Start: Rune Mysteries", color="purple", line_color="bmagenta")
        say("Sedridor: \"Take this AIR TALISMAN, study it, and bring it back — "
            "and I'll teach you the secret of runecrafting.\"")
        p.add("air talisman")
        p.quests["rune_mysteries"] = "started"
    elif stage == "started":
        if p.has("air talisman"):
            p.take("air talisman")
            _complete_banner("Rune Mysteries")
            say("Sedridor teaches you the basics of runecrafting! "
                "100 runecrafting and 100 magic xp awarded.")
            p.gain_xp("runecrafting", 100)
            p.gain_xp("magic", 100)
            p.quests["rune_mysteries"] = "complete"
        else:
            say("Sedridor: \"Hmm, where did that talisman go? Come back with it.\"")
    else:
        say("Sedridor: \"The runes reveal themselves to you now.\"")


def talk_mizgog(p):
    stage = _q(p, "imp_catcher")
    beads = ["red bead", "yellow bead", "black bead", "white bead"]
    if stage == "not_started":
        banner("Quest Start: Imp Catcher", color="purple", line_color="bmagenta")
        say("Wizard Mizgog: \"Those imps stole my magic beads! Bring me a RED, "
            "YELLOW, BLACK and WHITE bead — slay the imps here to get them.\"")
        p.quests["imp_catcher"] = "started"
    elif stage == "started":
        missing = [b for b in beads if not p.has(b)]
        if missing:
            _need_msg("Mizgog", missing)
        else:
            for b in beads:
                p.take(b)
            _complete_banner("Imp Catcher")
            say("Mizgog cheers and rewards you with 875 magic xp!")
            p.gain_xp("magic", 875)
            p.quests["imp_catcher"] = "complete"
    else:
        say("Mizgog: \"My beads are safe, thank you!\"")


def talk_aggie(p):
    stage = _q(p, "witch_potion")
    need = ["raw rat meat", "bucket of milk", "egg"]
    if stage == "not_started":
        banner("Quest Start: Witch's Potion", color="purple", line_color="bmagenta")
        say("Aggie: \"Brew my potion and I'll boost your magic. Bring me RAW RAT "
            "MEAT, a BUCKET OF MILK and an EGG.\"")
        p.quests["witch_potion"] = "started"
    elif stage == "started":
        missing = [i for i in need if not p.has(i)]
        if missing:
            _need_msg("Aggie", missing)
        else:
            for i in need:
                p.take(i)
            _complete_banner("Witch's Potion")
            say("Aggie brews a bubbling potion. 325 magic xp awarded!")
            p.gain_xp("magic", 325)
            p.quests["witch_potion"] = "complete"
    else:
        say("Aggie: \"That potion did you good, didn't it?\"")


def talk_oddenstein(p):
    stage = _q(p, "ernest_chicken")
    parts = ["oil can", "pressure gauge", "rubber tube"]
    if stage == "not_started":
        banner("Quest Start: Ernest the Chicken", color="purple", line_color="bmagenta")
        say("Professor Oddenstein: \"My machine turned Ernest into a chicken! "
            "To fix it, 'search' the manor for an OIL CAN, a PRESSURE GAUGE and "
            "a RUBBER TUBE.\"")
        p.quests["ernest_chicken"] = "started"
    elif stage == "started":
        missing = [i for i in parts if not p.has(i)]
        if missing:
            _need_msg("Oddenstein", missing)
        else:
            for i in parts:
                p.take(i)
            _complete_banner("Ernest the Chicken")
            say("The machine whirs and Ernest is restored! 300 coins awarded.")
            p.add("coins", 300)
            p.quests["ernest_chicken"] = "complete"
    else:
        say("Oddenstein: \"Ernest is most grateful to you!\"")


def talk_slayer_master(p):
    if not getattr(p, "members", False):
        say("Vannaka: \"Slayer is a members art, friend. Get membership and "
            "I'll set you a task.\"", "bmagenta")
        return
    task = p.slayer_task
    if task and task["remaining"] > 0:
        say(f"Vannaka: \"You're still on the hunt — {task['remaining']} of "
            f"{task['amount']} {task['monster']}s to go. Get to it!\"", "teal")
        return
    mon = random.choice(SLAYER_TARGETS)
    amt = random.randint(10, 25)
    p.slayer_task = {"monster": mon, "amount": amt, "remaining": amt}
    banner("Slayer Assignment", color="teal", line_color="teal")
    say(f"Vannaka: \"Your task: slay {amt} {mon}s.\"", "teal")
    locs = sorted({ROOMS[k]["name"] for k, r in ROOMS.items()
                   if mon in r.get("monsters", [])})
    if locs:
        say("  Find them at: " + ", ".join(locs[:4]), "grey")
    say("  (Check progress with 'task'; spend points with 'slayerbuy'.)",
        "grey")


QUEST_TALK = {
    "cooks_assistant": talk_cook,
    "sheep_shearer": talk_farmer,
    "dorics_quest": talk_doric,
    "romeo_juliet": talk_romeo,
    "vampyre_slayer": talk_morgan,
    "restless_ghost": talk_aereck,
    "rune_mysteries": talk_sedridor,
    "imp_catcher": talk_mizgog,
    "witch_potion": talk_aggie,
    "ernest_chicken": talk_oddenstein,
    "slayer_master": talk_slayer_master,
}


# Quest-story monsters exist FOR YOU, derived from your quest state — the
# shared world map is never mutated per player. This keeps saves honest (no
# respawn-on-load bookkeeping) and the engine ready for many players in one
# world. Entries: (room, monster, alive(p)). Content blocks append to it.
QUEST_SPAWNS = [
    ("draynor_manor", "count draynor",
     lambda p: _q(p, "vampyre_slayer") == "started"),
    ("paterdomus", "temple guardian",
     lambda p: _q(p, "priest_in_peril") == "guardian"),
    ("rock_crab_coast", "the draugen",
     lambda p: _q(p, "fremennik_trials") == "hunt"),
    ("fenkenstrain_castle", "the experiment",
     lambda p: _q(p, "fenkenstrain") == "creature"),
]


def _room_monsters(p, room=None):
    """The monsters THIS player finds in a room: the room's own list plus
    any quest-story spawns their journal conjures. Always read monsters
    through here — never ROOMS[...]["monsters"] directly."""
    room = room or p.location
    base = ROOMS[room].get("monsters", [])
    extra = [m for rm, m, alive in QUEST_SPAWNS
             if rm == room and m not in base and alive(p)]
    return base + extra if extra else base


def _quest_on_kill(p, target):
    if target == "count draynor" and _q(p, "vampyre_slayer") == "started":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Vampyre Slayer", color="byellow", line_color="gold")
        say("With the stake through its heart, Count Draynor crumbles to dust! "
            "4825 attack xp awarded.")
        p.gain_xp("attack", 4825)
        p.quests["vampyre_slayer"] = "complete"
    if target == "goblin" and _q(p, "dragon_slayer") == "maps" \
            and not p.has("wormbrain's map piece"):
        p.add("wormbrain's map piece")
        say("This goblin was Wormbrain — the wretch had swallowed a scrap of "
            "parchment. WORMBRAIN'S MAP PIECE is yours!", "bgreen")
    if target == "elvarg" and _q(p, "dragon_slayer") == "sail":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Dragon Slayer", color="byellow", line_color="gold")
        say("Elvarg is slain and Crandor is avenged! Word of your deed spreads "
            "across Gielinor. 18,650 strength and defence xp awarded — and you "
            "have earned the right to wear the RUNE PLATEBODY and GREEN D'HIDE "
            "BODY. (Oziach sells both.)")
        p.gain_xp("strength", 18650)
        p.gain_xp("defence", 18650)
        p.quests["dragon_slayer"] = "complete"
    if target == "temple guardian" and _q(p, "priest_in_peril") == "guardian":
        p.quests["priest_in_peril"] = "cleansed"
        say("The guardian collapses into grave-dust. Tell Drezel the crypt "
            "is safe!", "bgreen")
    if target == "the draugen" and _q(p, "fremennik_trials") == "hunt":
        p.quests["fremennik_trials"] = "hunted"
        say("The Draugen unravels into cold sea-mist. Brundt will want to "
            "hear of this!", "bgreen")
    if target == "dad" and _q(p, "troll_stronghold") == "started":
        p.quests["troll_stronghold"] = "dad"
        say("DAD crashes down and the gate-hall stands open. Somewhere "
            "deeper, chains rattle — find Godric! ('talk godric')",
            "bgreen")
    if _q(p, "desert_treasure") == "diamonds" and \
            target in _DT_GUARDIANS:
        gem, _room, _s = _DT_GUARDIANS[target]
        if not p.has(gem):
            p.add(gem)
            say(f"From the guardian's ashes you take the {gem.upper()}!",
                "bmagenta", "bold")
    if target == "the experiment" and _q(p, "fenkenstrain") == "creature":
        p.quests["fenkenstrain"] = "loose"
        say("The creature slumps, contained at last. The doctor will want "
            "a word.", "bgreen")
    if target == "cyclops" and random.random() < 0.20:
        nxt = _best_defender(p) + 1     # each tier you hold earns the next
        if nxt < len(DEFENDER_ORDER):
            p.add(DEFENDER_ORDER[nxt])
            say(f"The cyclops was guarding a {DEFENDER_ORDER[nxt].upper()}!",
                "gold", "bold")
    _cave_on_kill(p, target)            # Fight Caves wave progression
    _inferno_on_kill(p, target)         # Inferno wave progression
    _barrows_on_kill(p, target)         # Barrows brothers put to rest
    duel = getattr(p, "duel", None)
    if duel and target == "arena duelist":
        winnings = duel["stake"] * 2
        p.add("coins", winnings)
        p.duel = None
        banner("DUEL WON", color="gold", line_color="gold")
        say(f"The crowd roars! The Duelmaster pays out {winnings:,} coins.",
            "gold", "bold")
    god = GWD_FOLLOWERS.get(target)     # god followers grant kill count
    if god and ROOMS[p.location].get("gwd"):
        kc = getattr(p, "gwd_kc", {})
        kc[god] = kc.get(god, 0) + 1
        p.gwd_kc = kc
        print("  " + paint(f"{god.title()} kill count: {kc[god]}", "bmagenta"))
    # slayer task progress
    task = getattr(p, "slayer_task", None)
    if task and target == task["monster"] and task["remaining"] > 0:
        p.gain_xp("slayer", MONSTERS[target]["hp"])
        task["remaining"] -= 1
        if task["remaining"] <= 0:
            pts = SLAYER_POINTS.get(MONSTERS[target].get("rank", "medium"), 5)
            p.task_streak = getattr(p, "task_streak", 0) + 1
            mult = 5 if p.task_streak % 10 == 0 else \
                3 if p.task_streak % 5 == 0 else 1
            pts *= mult
            p.slayer_points += pts
            banner("SLAYER TASK COMPLETE", color="teal", line_color="teal")
            say(f"You finish your task of {task['amount']} {target}s! "
                f"+{pts} Slayer points (total {p.slayer_points}). See a Slayer "
                "Master for another.", "teal", "bold")
            if mult > 1:
                say(f"  \u2726 Task streak {p.task_streak} \u2014 "
                    f"\u00d7{mult} points!", "gold", "bold")
            else:
                say(f"  (Task streak: {p.task_streak} \u2014 bonuses at "
                    "every 5th and 10th.)", "grey")
            p.slayer_task = None
        else:
            print("  " + paint(f"Slayer: {task['remaining']} {target}s to go.",
                               "teal"))


ALL_QUESTS = {
    "cooks_assistant": "Cook's Assistant", "sheep_shearer": "Sheep Shearer",
    "dorics_quest": "Doric's Quest", "romeo_juliet": "Romeo & Juliet",
    "vampyre_slayer": "Vampyre Slayer", "restless_ghost": "The Restless Ghost",
    "rune_mysteries": "Rune Mysteries", "imp_catcher": "Imp Catcher",
    "witch_potion": "Witch's Potion", "ernest_chicken": "Ernest the Chicken",
}


def cmd_quests(p, _a):
    done = sum(1 for k in ALL_QUESTS if _q(p, k) == "complete")
    banner(f"Quest Journal  ({done}/{len(ALL_QUESTS)})", color="gold")
    print("  " + paint(f"Quest points: {quest_points(p)}", "byellow")
          + paint(f"   ({GUILD_QP} needed for the Champions' Guild)", "grey"))
    for key, title in ALL_QUESTS.items():
        raw = _q(p, key)
        st = raw if raw in ("not_started", "started", "complete") else "started"
        st = st.replace("_", " ")
        color = {"complete": "bgreen", "started": "byellow"}.get(st, "grey")
        print(f"  {title:20} " + paint(st, color)
              + paint(f"  ({QUEST_POINTS.get(key, 1)} qp)", "grey"))
        if raw == "not_started":                        # where it begins
            start = QUEST_STARTS.get(key)
            if start:
                print("    " + paint("start: " + start, "grey"))
        elif raw != "complete":                         # current objective
            hint = QUEST_HINTS.get(key, {}).get(raw)
            if hint:
                print("    " + paint("→ " + hint, "bcyan"))


