# ===========================================================================
#  WEB / BROWSER API  (driven by index.html via Pyodide)
# ===========================================================================
# These let JavaScript run the game one command at a time, capturing the
# coloured (ANSI) text output so xterm.js can render it in the browser.

def enable_web():
    """Force ANSI colour on (Pyodide stdout is not a TTY) + enable web anims."""
    global COLOR, WEB
    COLOR = True
    WEB = True


def enable_beta():
    """Unlock dev/test-only commands (the browser calls this on beta/localhost)."""
    global BETA
    BETA = True


def _capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


def web_logo():
    """Splash logo + tagline for the title screen."""
    def _show():
        show_art(LOGO, "gold")
        print(paint("        Adventures in Gielinor".center(78), "bgreen"))
        print(paint("   A love letter to Old School RuneScape".center(78),
                    "grey"))
        rule("brown")
    return _capture(_show)


def web_welcome(player):
    """Welcome line + getting-started guide + room, for a brand-new session."""
    def _show():
        print(paint(f"\nWelcome to Gielinor, {player.name}! ", "bgreen", "bold")
              + paint("New here? This will get you going:", "grey"))
        _intro_tips()
        print()
        cmd_look(player, "")
    return _capture(_show)


def _next_goal(p):
    """The game's living compass: one suggestion matched to where you are.
    Ordered from first steps to the end of everything."""
    qp = quest_points(p)
    cb = p.combat_level()
    done = {k for k in ALL_QUESTS if _q(p, k) == "complete"}
    if getattr(p, "kills", 0) == 0:
        return ("Win your first fight — cows and chickens graze west of "
                "Lumbridge. ('fight cow')")
    if _q(p, "cooks_assistant") == "not_started":
        return ("Start your first quest: the Cook is fretting in Lumbridge "
                "Castle. ('talk')")
    if cb < 12:
        return ("Train your combat on the goblins in Lumbridge Forest — "
                "'fight goblin auto' handles a few at once.")
    if max(p.lvl(s) for s in ("woodcutting", "mining", "fishing")) < 15:
        return ("Pick up a trade: chop trees, mine rocks or fish — and "
                "batch the work ('mine copper 10', 'fish all').")
    if len(done) < 3:
        return ("Work your quest journal — 'quests' shows where every story "
                "starts and what to do next.")
    if cb < 25:
        return ("The Stronghold of Security under Barbarian Village is "
                "made for your level — and Al Kharid's mine pays well.")
    if qp < 12:
        return (f"Earn 12 quest points ({qp} so far) — the Champions' Guild "
                "and the Black Knights' Fortress both demand a proven "
                "adventurer.")
    if _q(p, "dragon_slayer") != "complete":
        return ("DRAGON SLAYER awaits — speak to the Guildmaster at the "
                "Champions' Guild and earn the right to rune armour. "
                "('quests' tracks each step)")
    if not getattr(p, "members", False):
        return ("The members' world is open in this tribute — type "
                "'membership' and the map doubles.")
    if p.lvl("slayer") < 20:
        return ("Take a slayer task from Vannaka in Edgeville — focused "
                "kills, bonus xp, and points for the reward shop.")
    if cb < 70:
        return ("Push toward combat 70 — green dragons in the Wilderness "
                "and the Giant Mole under Falador Park are worthy prey.")
    if p.lvl("attack") + p.lvl("strength") >= 130 and \
            not any(p.has(d) or d in p.equipment.values()
                    or d in getattr(p, "bank", {}) for d in DEFENDER_ORDER):
        return ("The Warriors' Guild in Burthorpe will weigh your arm now "
                "— its cyclopes yield DEFENDERS, tier by tier up to rune.")
    if "obor" not in getattr(p, "bosses", []):
        return ("A giant key sometimes drops from hill giants — Obor waits "
                "behind the locked door in Edgeville Dungeon.")
    if _q(p, "priest_in_peril") != "complete":
        return ("King Roald in Varrock Palace has work east of the Salve — "
                "Morytania (and the Barrows) lie beyond.")
    if getattr(p, "barrows_loots", 0) == 0:
        return ("Six brothers stir beneath the Barrows mounds in Morytania. "
                "Bring a spade, food, and prayers.")
    if p.lvl("slayer") < 60:
        return ("The Slayer Tower rises over Canifis \u2014 three floors of "
                "horrors, and masters in Taverley, Edgeville and Brimhaven "
                "to send you up them.")
    if "tztok-jad" not in getattr(p, "bosses", []):
        return ("The Fight Caves smoulder in the Karamja volcano — seven "
                "waves, then TzTok-Jad, then the fire cape.")
    if not all(g in getattr(p, "bosses", []) for g in
               ("general graardor", "kree'arra", "k'ril tsutsaroth",
                "commander zilyana")):
        return ("The God Wars rage beneath the deep Wilderness ('chasm') — "
                "four generals, four godswords.")
    if "kalphite queen" not in getattr(p, "bosses", []):
        return ("Beneath the Kharidian sands the Kalphite Queen waits in "
                "two bodies \u2014 bring crush weapons, waterskins, and "
                "nerve ('south' from Al Kharid).")
    if not all(k in getattr(p, "bosses", []) for k in
               ("dagannoth rex", "dagannoth prime", "dagannoth supreme")):
        return ("Three Kings circle beneath Waterbirth Island \u2014 magic "
                "fells Rex, arrows fell Prime, steel fells Supreme, and "
                "their rings have no equal. (Fremennik Trials first \u2014 "
                "Rellekka, north of Seers')")
    if "the nightmare" not in getattr(p, "bosses", []):
        return ("Slepe has stopped waking \u2014 beneath its cathedral THE "
                "NIGHTMARE drinks the town's dreams. Crush weapons bite "
                "deepest. (east of Canifis, then south)")
    if not all(w in getattr(p, "bosses", []) for w in
               ("callisto", "venenatis", "vet'ion", "corporeal beast")):
        return ("The WARLORDS of the western Wilderness hold rings, wards "
                "and the dragon pickaxe \u2014 and the Corporeal Beast falls "
                "only to SPEARS. ('wastes' off the deep Wilderness)")
    if p.lvl("slayer") >= 87 and not all(
            b in getattr(p, "bosses", []) for b in
            ("kraken", "cerberus", "abyssal sire", "grotesque guardians",
             "thermonuclear smoke devil")):
        return ("Your slayer mastery opens five lairs \u2014 the Kraken's "
                "cove, Cerberus' gate, Pollnivneach's smoking well, the "
                "tower's rift and its roof. Trident, boots and the occult "
                "await.")
    if "tzkal-zuk" not in getattr(p, "bosses", []):
        return ("The INFERNO smoulders beneath Mor Ul Rek ('city' in the "
                "volcano) \u2014 wear your fire cape in, survive eight waves, "
                "and TzKal-Zuk guards the infernal cape at the bottom.")
    if not any(p.base_lvl(s) >= 99 for s in SKILLS):
        return ("Chase your first level 99 — the Wise Old Man in Draynor "
                "sells the cape to prove it.")
    mastered = sum(1 for s in SKILLS if p.base_lvl(s) >= 99)
    if mastered < len(SKILLS):
        return (f"{mastered}/{len(SKILLS)} skills mastered. The grind is "
                "the destination.")
    return ("You have conquered Gielinor — every god, every skill, every "
            "story. Thank you for playing.")


def cmd_goal(p, _a):
    banner("Next Up", color="bcyan", line_color="teal")
    say("  " + _next_goal(p), "bcyan")
    say("  ('quests', 'me' and 'stats' for the full picture)", "grey")


def cmd_stop(p, _a):
    say("Nothing left to stop.", "grey")


HANDLERS["stop"] = cmd_stop
HANDLERS["goal"] = cmd_goal
HANDLERS["goals"] = cmd_goal
HANDLERS["hint"] = cmd_goal


def _resume_summary(player):
    """Print a 'welcome back' status block + current room (shared web/CLI)."""
    done = sum(1 for s in player.quests.values() if s == "complete")
    total_lvl = sum(player.lvl(s) for s in SKILLS)
    banner(f"Welcome back, {player.name}!", color="gold")
    print("  " + paint("Combat level ", "white")
          + paint(str(player.combat_level()), "byellow", "bold")
          + paint("    Hitpoints ", "white")
          + bar_meter(player.hp, player.max_hp, 16)
          + paint(f"    Coins: {player.coins:,}", "gold"))
    print("  " + paint(f"Total level: {total_lvl}", "white")
          + paint(f"    Quests completed: {done}", "bmagenta")
          + paint(f"    Style: {player.style}", "grey"))
    print("  " + paint("You were last at: ", "grey")
          + paint(ROOMS[player.location]["name"], "bcyan", "bold"))
    print("  " + paint("Next up: ", "bcyan", "bold")
          + paint(_next_goal(player), "bcyan"))
    print()
    cmd_look(player, "")


def web_resume(player):
    """Status summary + location, shown when a saved game is loaded."""
    return _capture(_resume_summary, player)


def web_command(player, line):
    """Run one command; return JSON {text, alive, auto} for the browser."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        alive = dispatch(player, line)
    return json.dumps({"text": buf.getvalue(), "alive": alive,
                       "auto": getattr(player, "auto", None) is not None})


def web_autostep(player):
    """One autopilot kill, browser-paced. Same shape as web_command."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _auto_step(player)
        _check_achievements(player)
    return json.dumps({"text": buf.getvalue(), "alive": True,
                       "auto": getattr(player, "auto", None) is not None})


def web_status(player):
    """Compact live status for the browser status bar (HUD)."""
    drain = getattr(player, "stat_drain", {}) or {}
    m = getattr(player, "combat", None)
    enemy = None
    if m:
        enemy = {"name": m["name"], "hp": max(0, m["cur"]), "max": m["hp"],
                 "level": m.get("level")}
    return json.dumps({
        "name": player.name,
        "combat": player.combat_level(),
        "hp": player.hp,
        "max_hp": player.max_hp,
        "coins": player.coins,
        "total": sum(player.lvl(s) for s in SKILLS),
        "location": ROOMS[player.location]["name"],
        "style": player.style,
        "stance": getattr(player, "attack_type", "slash"),
        "energy": int(getattr(player, "run_energy", 100)),
        "spec": int(getattr(player, "spec_energy", 100)),
        "members": bool(getattr(player, "members", False)),
        "prayer": int(getattr(player, "prayer_points", 0)),
        "prayer_max": player.prayer_max(),
        "in_combat": m is not None,
        "enemy": enemy,
        "poison": int(getattr(player, "poison", 0)),
        "frozen": bool(getattr(player, "frozen", False)),
        "drain": max(drain.values()) if drain else 0,
        "exits": _room_exits(player),
    })


def _room_exits(player):
    """Ordered list of the current room's exits, for clickable nav buttons."""
    ex = ROOMS[player.location].get("exits", {})
    order = ["north", "east", "south", "west", "up", "down"]
    return [d for d in order if d in ex] + [d for d in ex if d not in order]


def web_commands():
    """Sorted command verbs for the browser's tab-completion / history."""
    verbs = set(HANDLERS) | set(DIRECTIONS)
    # dev tools stay runnable on beta but are hidden from autocomplete/help
    verbs -= _HIDDEN_VERBS
    verbs.discard("?")
    return json.dumps(sorted(verbs))


def web_panel(player):
    """Live sidebar data: goal, slayer standing, farm patches, traps."""
    task = getattr(player, "slayer_task", None)
    patches = []
    for pid, crop in sorted(getattr(player, "farm", {}).items()):
        room, ptype = pid.split(":")
        ready, left = _patch_state(player, crop)
        patches.append({"place": ROOMS[room]["name"], "type": ptype,
                        "crop": crop["seed"].replace(" seed", ""),
                        "ready": ready, "left": left})
    traps = []
    for slot in sorted(getattr(player, "traps", {}), key=int):
        info = player.traps[slot]
        trap, lvl, spring, xp, loot = HUNT[info["creature"]]
        elapsed = getattr(player, "actions", 0) - info["at"]
        traps.append({"creature": info["creature"],
                      "ready": elapsed >= spring,
                      "left": max(0, spring - elapsed)})
    return json.dumps({
        "goal": _next_goal(player),
        "task": ({"monster": task["monster"], "amount": task["amount"],
                  "remaining": task["remaining"]}
                 if task and task.get("remaining", 0) > 0 else None),
        "streak": getattr(player, "task_streak", 0),
        "points": getattr(player, "slayer_points", 0),
        "patches": patches,
        "traps": traps,
    })


def web_room_actions(player):
    """Interactable entities in the current room, for clickable UI chips."""
    # in interactive combat, show the combat moves instead of room entities
    if getattr(player, "combat", None) is not None:
        m = player.combat
        foods = [i for i in player.inventory if "heal" in ITEMS.get(i, {})]
        pots = [i for i in player.inventory if ITEMS.get(i, {}).get("potion")]
        acts = [{"label": "Attack", "cmd": "attack"}]
        sp = SPECIAL_ATTACKS.get(player.equipment.get("weapon"))
        if sp:
            e = int(getattr(player, "spec_energy", 100))
            acts.append({"label": f"⚡ {sp['name']} ({e}%)", "cmd": "spec"})
        if foods:
            acts.append({"label": f"Eat {foods[0]}", "cmd": f"eat {foods[0]}"})
        if pots:
            acts.append({"label": f"Drink {pots[0]}", "cmd": f"drink {pots[0]}"})
        acts.append({"label": "Pray", "cmd": "pray"})
        acts.append({"label": "Examine", "cmd": f"examine {m['name']}"})
        acts.append({"label": "Flee", "cmd": "flee"})
        return json.dumps([{"name": f"fighting {m['name']}", "kind": "monster",
                            "actions": acts}])
    r = ROOMS[player.location]
    out = []
    for m in _room_monsters(player):
        out.append({"name": m, "kind": "monster", "actions": [
            {"label": "Attack", "cmd": f"fight {m}"},
            {"label": "Auto ×5", "cmd": f"fight {m} 5"},
            {"label": "Auto all", "cmd": f"fight {m} all"},
            {"label": "Examine", "cmd": f"examine {m}"},
        ]})
    for t in r.get("trees", []):
        label = "tree" if t == "tree" else f"{t} tree"
        out.append({"name": label, "kind": "tree",
                    "actions": [{"label": "Chop", "cmd": f"chop {t}"}]})
    for rock in r.get("rocks", []):
        out.append({"name": f"{rock} rocks", "kind": "rock",
                    "actions": [{"label": "Mine", "cmd": f"mine {rock}"}]})
    if r.get("fish_tools"):
        out.append({"name": "fishing spot", "kind": "fish",
                    "actions": [{"label": "Fish", "cmd": "fish"}]})
    npc = r.get("npc")
    if npc:
        keys = npc if isinstance(npc, list) else [npc]
        for k in keys:
            nm = NPC_NAMES.get(k, "someone to talk to")
            out.append({"name": nm, "kind": "npc", "actions": [
                {"label": "Talk", "cmd": f"talk {nm}" if len(keys) > 1
                 else "talk"}]})
    for tgt in r.get("pickpocket", []):
        out.append({"name": tgt, "kind": "npc",
                    "actions": [{"label": "Pickpocket", "cmd": f"pickpocket {tgt}"}]})
    for stall in r.get("stalls", []):
        out.append({"name": stall, "kind": "gather",
                    "actions": [{"label": "Steal", "cmd": f"steal {stall}"}]})
    for item in r.get("pick", []):
        out.append({"name": item, "kind": "gather",
                    "actions": [{"label": "Pick", "cmd": f"pick {item}"}]})
    for ptype in r.get("patches", []):
        crop = getattr(player, "farm", {}).get(f"{player.location}:{ptype}")
        if crop:
            ready, left = _patch_state(player, crop)
            nm = crop["seed"].replace(" seed", "")
            out.append({"name": f"{ptype}: {nm}"
                        + ("" if ready else f" (~{left})"), "kind": "gather",
                        "actions": [{"label": "Harvest",
                                     "cmd": f"harvest {ptype}"}]})
        else:
            out.append({"name": f"{ptype} patch", "kind": "gather",
                        "actions": [{"label": "Plant", "cmd": "farm"}]})
    if r.get("agility_course"):
        out.append({"name": "obstacle course", "kind": "gather",
                    "actions": [{"label": "Run a lap", "cmd": "agility"}]})
    if r.get("fight_caves"):
        if getattr(player, "cave_wave", 0):
            out.append({"name": f"wave {player.cave_wave}", "kind": "monster",
                        "actions": [{"label": "Next wave", "cmd": "next"}]})
        else:
            out.append({"name": "the Fight Caves", "kind": "monster",
                        "actions": [{"label": "Challenge", "cmd": "challenge"}]})
    if r.get("inferno"):
        if getattr(player, "inferno_wave", 0):
            out.append({"name": f"wave {player.inferno_wave}",
                        "kind": "monster",
                        "actions": [{"label": "Next wave", "cmd": "next"}]})
        else:
            out.append({"name": "the Inferno", "kind": "monster",
                        "actions": [{"label": "Challenge", "cmd": "challenge"}]})
    if r.get("barrows"):
        slain = set(getattr(player, "barrows", []))
        left = [b for b in BROTHERS if b not in slain]
        if left:
            nm = left[0].split(" ")[0]
            out.append({"name": f"burial mounds ({len(left)} left)",
                        "kind": "monster",
                        "actions": [{"label": f"Dig ({nm})", "cmd": "dig"}]})
        else:
            out.append({"name": "the crypt chest", "kind": "gather",
                        "actions": [{"label": "Loot chest", "cmd": "loot"}]})
    # location-specific gathering
    specials = {
        "lumbridge_farm": [
            ("chicken coop", [("Collect egg", "collect")]),
            ("cow", [("Milk", "milk")]),
            ("wheat field", [("Pick", "pick")]),
            ("sheep", [("Shear", "shear")]),
        ],
        "cow_field": [("sheep", [("Shear", "shear")])],
        "windmill": [("hopper", [("Mill flour", "mill")])],
    }
    for name, acts in specials.get(player.location, []):
        out.append({"name": name, "kind": "gather",
                    "actions": [{"label": lbl, "cmd": cmd} for lbl, cmd in acts]})
    # services
    svc = [("bank", "Bank", "bank"), ("shop", "Shop", "shop"),
           ("ge", "Grand Exchange", "ge"), ("range", "Cook", "cook"),
           ("furnace", "Smelt", "smelt"), ("anvil", "Smith", "smith"),
           ("spinning_wheel", "Spin", "spin"), ("tanner", "Tan", "tan")]
    for flag, label, cmd in svc:
        if r.get(flag):
            out.append({"name": label, "kind": "service",
                        "actions": [{"label": label, "cmd": cmd}]})
    if r.get("prayer_altar"):
        out.append({"name": "prayer altar", "kind": "service",
                    "actions": [{"label": "Recharge prayer", "cmd": "pray recharge"}]})
    if player.location in set(TRAVEL_HUBS.values()):
        out.append({"name": "rest spot", "kind": "service",
                    "actions": [{"label": "Rest (restore energy)", "cmd": "rest"}]})
    return json.dumps(out)


def player_to_json(player):
    return json.dumps(serialize(player))


def player_from_json(text):
    return deserialize(json.loads(text))


