# ===========================================================================
#  HELP & DISPATCH
# ===========================================================================
def cmd_help(_p, _a):
    banner("Commands")
    groups = {
        "Move": "look (l), go <dir>, n/s/e/w, up/down, "
                "goto <place|bank|ge…> (auto-walk anywhere you've explored), "
                "exits — and Enter on an empty line repeats your last command",
        "Info": "me (character card), stats [skill], inventory (i), "
                "equipment, quests, examine <item|creature>, bestiary",
        "Combat": "fight [monster], spec (special attack), "
                  "train <attack|strength|defence|shared>, "
                  "style <melee|ranged|magic|stab|slash|crush>, "
                  "autocast <spell>, eat [food], drink [potion], "
                  "autoeat on/off (reflex-eat when badly hurt)",
        "Gear": "equip <item>, unequip <slot>, "
                "gear <melee|ranged|magic> (wear your best kit + switch "
                "style), drop <item> [n|all]",
        "Skilling": "chop [tree], mine [rock], fish, cook [food], light [logs], "
                    "bury [bones], smelt <bar>, smith <metal> <item>, spin, tan, "
                    "craft <item>, cut <gem>, fletch <bow>, craftrune, "
                    "skillcape <skill>, "
                    "plant <seed>, harvest, farm (your patches), "
                    "saw <logs>, build (your house), home, "
                    "settrap <creature>, check (traps) — "
                    "add a count or 'all' to repeat: 'mine iron 10', 'cook all'",
        "Magic": "cast <spell> (teleports/alchemy), autocast <combat spell>, "
                 "enchant <ring>",
        "Town": "bank, deposit/withdraw <item> [n], shop, buy/sell <item> [n], "
                "ge buy/sell <item> [n]",
        "Quests": "talk, search",
        "System": "save, tutorial, feedback, help, quit",
    }
    for g, c in groups.items():
        say(f"\n{g}:")
        say("  " + c)


GITHUB_ISSUES = "https://github.com/OnlyRunes/onlyrunes/issues"


def _intro_tips():
    """A concise getting-started guide for brand-new players."""
    banner("Getting Started", color="bgreen", line_color="green")
    for k, v in [
        ("Move", "type a direction (n/s/e/w) — or tap the arrow buttons. "
                 "'goto <place>' walks anywhere you've been."),
        ("Look", "'look' shows what's here, who's around, and your exits."),
        ("Fight", "'fight chicken' (or tap a creature). Win XP and loot."),
        ("Repeat", "Enter on an empty line repeats your last command — "
                   "great for grinding."),
        ("Progress", "'me' for your character card; 'stats', 'inventory', "
                     "'equipment' for detail."),
        ("Spend", "'bank' to store loot; 'shop' and 'ge' to buy & sell."),
        ("Help", "'help' lists every command; 'tutorial' shows this again."),
    ]:
        print("  " + paint(f"{k}: ", "byellow") + paint(v, "white"))
    print("  " + paint("First goal: ", "bcyan")
          + paint("head west to the cow field, win a few fights, then bank your "
                  "loot and cook the raw beef.", "white"))
    print("  " + paint("⚑ Heads up: ", "byellow")
          + paint("your progress saves in THIS browser only. Type ", "grey")
          + paint("save export", "byellow")
          + paint(" to back it up (vital before switching devices).", "grey"))


def cmd_tutorial(_p, _a):
    _intro_tips()


def cmd_feedback(_p, _a):
    banner("Feedback & Bug Reports", color="bcyan", line_color="teal")
    say("  Found a bug, got stuck, or have an idea? We'd love to hear it!", "white")
    print("  " + paint("Report it here: ", "white")
          + paint(GITHUB_ISSUES, "bcyan", "bold"))
    say("  Tip: include what you were doing and (if you can) your character name.",
        "grey")


def _drop_rarity(chance):
    """Bucket a drop chance into a coloured rarity label."""
    if chance >= 1.0:
        return ("always", "white")
    if chance >= 0.5:
        return ("common", "bgreen")
    if chance >= 0.15:
        return ("uncommon", "bcyan")
    if chance >= 0.04:
        return ("rare", "bmagenta")
    return ("very rare", "gold")


def _examine_monster(p, name):
    m = MONSTERS[name]
    log = getattr(p, "kill_log", {}) or {}
    killed = log.get(name, 0)
    title = name.title()
    if m.get("level"):
        title += f"  —  combat level {m['level']}"
    banner(title, color="bred", line_color="red")
    print("  " + paint(f"Hitpoints {m['hp']}", "bred")
          + paint(f"    Max hit {m['max_hit']}", "white")
          + paint(f"    Attacks with {'/'.join(m.get('atktype', ['crush']))}",
                  "grey"))
    weak = m.get("weakness") or m.get("weak")
    if weak:
        print("  " + paint(f"Weakness: {weak}", "byellow"))
    print("  " + paint(f"Slain: {killed}", "bcyan")
          + (paint("   [members]", "bmagenta") if m.get("members") else "")
          + (paint("   [BOSS]", "bred", "bold") if m.get("boss") else ""))
    say("  Drops:", "grey")
    for item, lo, hi, chance in sorted(m["drops"], key=lambda d: -d[3]):
        rlabel, rcolor = _drop_rarity(chance)
        qty = f"{lo}-{hi}" if hi > lo else f"{lo}"
        print("    " + paint(f"{item} ", item_rarity_color(item))
              + paint(f"x{qty}", "grey")
              + paint(f"  ({rlabel})", rcolor))


def cmd_examine(p, arg):
    name = arg.strip().lower()
    if not name:
        say("Examine what? (an item or a creature)")
        return
    if name not in MONSTERS and name not in ITEMS:
        # forgiving lookup: unique substring match (creatures first)
        hits = [m for m in MONSTERS if name in m] or \
               [i for i in ITEMS if name in i]
        if len(hits) == 1:
            name = hits[0]
        elif len(hits) > 1:
            say("Which one? " + ", ".join(sorted(hits)[:8]))
            return
    if name in MONSTERS:
        return _examine_monster(p, name)
    if name not in ITEMS:
        say("No such item or creature to examine.")
        return
    info = ITEMS[name]
    bits = [f"value {info['value']}"]
    if "heal" in info:
        bits.append(f"heals {info['heal']}")
    if "equip" in info:
        eq = info["equip"]
        bits.append("slot " + eq["slot"])
        if eq.get("two_handed"):
            bits.append("two-handed")
        labels = [("astab", "stab"), ("aslash", "slash"), ("acrush", "crush"),
                  ("amagic", "atk-mage"), ("arange", "atk-rng"),
                  ("str", "str"), ("rstr", "rng-str"), ("mdmg", "mage-dmg%"),
                  ("dstab", "def-stab"), ("dslash", "def-slash"),
                  ("dcrush", "def-crush"), ("dmagic", "def-mage"),
                  ("drange", "def-rng"), ("prayer", "prayer")]
        for f, lbl in labels:
            if eq.get(f):
                bits.append(f"{lbl} {eq[f]:+d}")
        for skill, req in eq.get("req", {}).items():
            bits.append(f"needs {skill} {req}")
        if eq.get("quest"):
            bits.append(f"quest-locked: {ALL_QUESTS.get(eq['quest'], eq['quest'])}")
    if info.get("members"):
        bits.append("members")
    say(f"{name}: " + ", ".join(bits))
    sp = SPECIAL_ATTACKS.get(name)
    if sp:
        say(f"  special: {sp['name']} ({sp['cost']}%) — {sp['desc']}", "teal")
    note = EFFECT_NOTES.get(name)
    if note:
        say(f"  effect: {note}", "bmagenta")


def cmd_bestiary(p, _a):
    log = {k: v for k, v in (getattr(p, "kill_log", {}) or {}).items() if v > 0}
    total = getattr(p, "kills", 0)
    banner(f"Bestiary  —  {total:,} kills", color="bred", line_color="red")
    if not log:
        say("  You haven't slain anything yet. Go forth and fight!", "grey")
        return
    say(f"  {len(log)} unique creatures slain.", "grey")
    for name, n in sorted(log.items(), key=lambda kv: -kv[1]):
        is_boss = MONSTERS.get(name, {}).get("boss")
        mark = paint(" ☠", "bred") if is_boss else ""
        print("  " + paint(f"{name:22}", "white")
              + paint(f"x{n}", "bcyan") + mark)
    say("\n  Tip: 'examine <creature>' shows stats, weakness and drops.", "grey")


DIRECTIONS = {"n": "north", "s": "south", "e": "east", "w": "west",
              "u": "up", "d": "down"}

def _gear_score(eq, style):
    """How much an equip block helps a combat style (bigger = better)."""
    defsum = sum(eq.get(k, 0) for k in ("dstab", "dslash", "dcrush",
                                        "dmagic", "drange"))
    if style == "ranged":
        return eq.get("arange", 0) * 2 + eq.get("rstr", 0) * 3 + defsum * 0.05
    if style == "magic":
        return eq.get("amagic", 0) * 3 + eq.get("mdmg", 0) * 2 + defsum * 0.05
    best_atk = max(eq.get("astab", 0), eq.get("aslash", 0), eq.get("acrush", 0))
    return best_atk + eq.get("str", 0) * 2 + defsum * 0.05


def _best_gear_for_style(style):
    """Best-in-slot item per equipment slot for a combat style (ignores reqs)."""
    best, best_score = {}, {}
    for name, info in ITEMS.items():
        eq = info.get("equip")
        slot = eq.get("slot") if eq else None
        if not slot:
            continue
        sc = _gear_score(eq, style)
        if sc <= 0:                       # irrelevant to this style
            continue
        if slot not in best_score or sc > best_score[slot]:
            best_score[slot], best[slot] = sc, name
    # a two-handed weapon leaves no hand for a shield
    w = best.get("weapon")
    if w and ITEMS[w].get("equip", {}).get("two_handed"):
        best.pop("shield", None)
    return best


def cmd_gear(p, arg):
    """Equip the best kit you're carrying for a style, and switch to it:
    'gear magic'. The one-command loadout swap (free mid-fight, as in OSRS)."""
    want = arg.strip().lower()
    style = {"mage": "magic", "range": "ranged", "ranging": "ranged",
             "melee": "melee", "ranged": "ranged", "magic": "magic"}.get(want)
    if want and not style:
        say("'gear melee', 'gear ranged' or 'gear magic' — equips the best "
            "kit in your pack and switches style.", "grey")
        return
    style = style or p.style

    def wearable(item):
        info = ITEMS.get(item, {})
        eq = info.get("equip")
        if not eq:
            return None
        if info.get("members") and not getattr(p, "members", False):
            return None
        if any(p.lvl(sk) < req for sk, req in eq.get("req", {}).items()):
            return None
        q = eq.get("quest")
        if q and p.quests.get(q) != "complete":
            return None
        return eq
    pool = set(p.inventory) | set(filter(None, p.equipment.values()))
    best = {}
    for item in pool:
        eq = wearable(item)
        if not eq:
            continue
        sc = _gear_score(eq, style)
        if sc <= 0:
            continue
        slot = eq["slot"]
        if slot not in best or sc > best[slot][1]:
            best[slot] = (item, sc)
    if "weapon" in best and \
            ITEMS[best["weapon"][0]]["equip"].get("two_handed"):
        best.pop("shield", None)            # both hands on the big one
    changes = []
    for slot in EQUIP_SLOTS:                # weapon first: settles 2H/shield
        pick = best.get(slot)
        if not pick or p.equipment.get(slot) == pick[0]:
            continue
        if p.equip_item(pick[0], silent=True):
            changes.append(pick[0])
    if changes:
        say("You kit up: " + ", ".join(changes) + ".", "bcyan")
    else:
        say(f"You're already wearing your best {style} kit.", "grey")
    cmd_style(p, style)


def cmd_devmax(p, arg):
    """[beta only] Max all skills + equip best gear for the current style."""
    if not BETA:
        return say("You don't know how to do that. Type 'help'.")
    for s in SKILLS:
        p.skills[s] = _XP_TABLE[99]
    p.members = True
    p.quests = {k: "complete" for k in ALL_QUESTS}   # unlocks quest-gated gear
    p.hp = p.max_hp
    p.prayer_points = p.prayer_max()
    p.run_energy = 100
    # stock every rune so magic always works
    runes = set()
    for sp in SPELLS.values():
        runes.update(sp.get("runes", {}))
    for r in runes:
        if r in ITEMS:
            p.add(r, 100000)
    p.add("giant key")     # so you can reach Obor's lair to test bosses
    # wipe loadout, then equip best-in-slot for the active style
    for slot in list(p.equipment):
        p.equipment[slot] = None
    for slot, item in _best_gear_for_style(p.style).items():
        p.add(item)
        p.equip_item(item, silent=True)
    if p.style == "ranged" and p.equipment.get("ammo"):
        p.add(p.equipment["ammo"], 100000)          # a full quiver
    if p.style == "magic":
        book = getattr(p, "spellbook", "standard")
        combat = [s for s, d in SPELLS.items() if d.get("type") == "combat"
                  and d.get("book", "standard") == book]
        if combat:
            p.autocast = max(combat, key=lambda s: SPELLS[s]["max"])
    banner("DEV MODE", color="bmagenta", line_color="purple")
    say(f"All skills set to 99, members unlocked, all quests complete, best "
        f"{p.style} gear equipped.", "bmagenta", "bold")
    if p.style == "magic":
        say(f"Autocasting {p.autocast}; runes stocked.", "grey")
    elif p.style == "ranged":
        say("Quiver stocked with arrows.", "grey")
    say("Tip: change style with 'style', then run 'maxme' again to re-gear.",
        "grey")
    cmd_equipment(p, "")


def cmd_spawn(p, arg):
    """[beta only] Spawn any item: 'spawn <item> [qty]'."""
    if not BETA:
        return say("You don't know how to do that. Type 'help'.")
    words = arg.strip().lower().split()
    qty = 1
    if words and words[-1].isdigit():
        qty = max(1, int(words[-1]))
        words = words[:-1]
    name = " ".join(words)
    if not name:
        return say("Spawn what? 'spawn <item> [qty]' — any item in the "
                   "game.", "grey")
    if name not in ITEMS:
        near = [i for i in ITEMS if name in i][:6]
        if len(near) == 1:
            name = near[0]
        elif near:
            return say("Which one? " + ", ".join(near), "grey")
        else:
            return say(f"No item called '{name}'.", "grey")
    p.add(name, qty)
    say(f"[dev] Spawned {qty} x {name}.", "bmagenta", "bold")


def cmd_god(p, arg):
    """[beta only] Toggle god mode: hp pinned to full, death refused."""
    if not BETA:
        return say("You don't know how to do that. Type 'help'.")
    p.god = not getattr(p, "god", False)
    if p.god:
        p.hp = p.max_hp
        say("[dev] GOD MODE ON — your hp is pinned to full and death "
            "cannot take you.", "bmagenta", "bold")
    else:
        say("[dev] God mode off. Mortality restored.", "bmagenta")


HANDLERS = {
    "look": cmd_look, "l": cmd_look, "exits": cmd_look,
    "go": cmd_go, "goto": cmd_goto, "walk": cmd_goto,
    "stats": cmd_stats, "skills": cmd_stats,
    "inventory": cmd_inventory, "inv": cmd_inventory, "i": cmd_inventory,
    "equipment": cmd_equipment, "worn": cmd_equipment,
    "equip": cmd_equip, "wield": cmd_equip, "wear": cmd_equip,
    "unequip": cmd_unequip, "remove": cmd_unequip,
    "style": cmd_style, "autocast": cmd_autocast,
    "spec": cmd_spec, "special": cmd_spec,
    "drop": cmd_drop, "discard": cmd_drop,
    "chop": cmd_chop, "cut": cmd_chop,
    "mine": cmd_mine,
    "fish": cmd_fish,
    "cook": cmd_cook,
    "light": cmd_light, "firemake": cmd_light,
    "bury": cmd_bury,
    "smelt": cmd_smelt, "smith": cmd_smith,
    "spin": cmd_spin, "tan": cmd_tan, "craft": cmd_craft, "craftrune": cmd_craftrune,
    "eat": cmd_eat, "autoeat": cmd_autoeat,
    "gear": cmd_gear, "loadout": cmd_gear, "outfit": cmd_gear,
    "clean": cmd_clean, "brew": cmd_brew, "mix": cmd_brew, "drink": cmd_drink,
    "cast": cmd_cast,
    "bank": cmd_bank, "deposit": cmd_deposit, "withdraw": cmd_withdraw,
    "shop": cmd_shop, "store": cmd_shop, "buy": cmd_buy, "sell": cmd_sell,
    "ge": cmd_ge, "exchange": cmd_ge,
    "fight": cmd_fight, "attack": cmd_fight, "kill": cmd_fight,
    "talk": cmd_talk, "search": cmd_search,
    "collect": cmd_collect, "milk": cmd_milk, "pick": cmd_pick,
    "mill": cmd_mill, "shear": cmd_shear,
    "quests": cmd_quests, "quest": cmd_quests, "journal": cmd_quests,
    "achievements": cmd_achievements, "achievement": cmd_achievements,
    "diary": cmd_achievements,
    "examine": cmd_examine, "inspect": cmd_examine,
    "bestiary": cmd_bestiary, "kills": cmd_bestiary, "killlog": cmd_bestiary,
    "map": cmd_map, "automap": cmd_automap, "membership": cmd_membership,
    "pray": cmd_pray, "prayer": cmd_pray, "prayers": cmd_pray,
    "pickpocket": cmd_pickpocket, "thieve": cmd_pickpocket, "steal": cmd_pickpocket,
    "agility": cmd_agility, "lap": cmd_agility, "course": cmd_agility,
    "travel": cmd_travel, "rest": cmd_rest,
    "task": cmd_task, "slayer": cmd_task,
    "save": cmd_save, "load": cmd_load,
    "tutorial": cmd_tutorial, "guide": cmd_tutorial, "intro": cmd_tutorial,
    "feedback": cmd_feedback, "bug": cmd_feedback, "report": cmd_feedback,
    "help": cmd_help, "commands": cmd_help, "?": cmd_help,
    # dev/test only — no-op unless enable_beta() was called (beta/localhost).
    # Hidden from web autocomplete/help even on beta (see web_commands()).
    "maxme": cmd_devmax, "devmax": cmd_devmax, "dev": cmd_devmax,
    "spawn": cmd_spawn, "god": cmd_god, "godmode": cmd_god,
}

# verbs kept out of the web tab-completion list (dev tools; still runnable)
_HIDDEN_VERBS = {"maxme", "devmax", "dev", "spawn", "god", "godmode"}


def _backup_nudge(p):
    """One-time reminder to export a save once a player has some progress."""
    seen = getattr(p, "tips_seen", None)
    if seen is None:
        seen = p.tips_seen = []
    if "backup" in seen:
        return
    if p.combat_level() >= 10 or sum(p.lvl(s) for s in SKILLS) >= 60:
        seen.append("backup")
        print()
        print("  " + paint("⚑ Tip: ", "byellow")
              + paint("you're making progress! Your game saves in this browser "
                      "only — type ", "grey")
              + paint("save export", "byellow")
              + paint(" to back it up so you never lose your character.", "grey"))


# skilling verbs that accept a count: 'mine iron 10', 'cook all', 'bury 5'
BATCHABLE = {"chop", "cut", "mine", "fish", "cook", "smelt", "bury",
             "clean", "tan", "spin", "worship"}
BATCH_CAP = 28      # one inventory's worth, like a proper JalYt


def _split_count(arg):
    """Split a trailing/leading count (or 'all') off a command argument."""
    parts = (arg or "").strip().lower().split()
    if parts and (parts[-1].isdigit() or parts[-1] == "all"):
        n = BATCH_CAP if parts[-1] == "all" else \
            max(1, min(BATCH_CAP, int(parts[-1])))
        return " ".join(parts[:-1]), n
    if parts and parts[0].isdigit():
        return " ".join(parts[1:]), max(1, min(BATCH_CAP, int(parts[0])))
    return (arg or "").strip(), 1


def _run_batch(p, handler, arg, n):
    """Repeat a skilling action up to n times, then print a compact summary.
    Handlers return True/False (action happened) or None (blocked — stop)."""
    global _QUIET
    inv0 = dict(p.inventory)
    sk0 = dict(p.skills)
    done = 0
    for i in range(n):
        _QUIET = True
        try:
            r = handler(p, arg)
        finally:
            _QUIET = False
        if r is None:               # blocked (no materials/tool/level)
            handler(p, arg)         # replay once, loudly, to say why
            break
        done += 1
        if i < n - 1:               # each batched action moves the world
            _regen_energy(p)        # (dispatch ticks once more at the end)
    if not done:
        return
    parts = []
    for item in sorted(set(p.inventory) | set(inv0)):
        d = p.inventory.get(item, 0) - inv0.get(item, 0)
        if d:
            parts.append(f"{'+' if d > 0 else ''}{d} {item}")
    for s in SKILLS:
        d = p.skills[s] - sk0.get(s, 0)
        if d:
            parts.append(f"+{int(d):,} {s} xp")
    say(f"({done} action{'s' if done != 1 else ''})  "
        + ("  ".join(parts) if parts else "nothing to show for it"), "bcyan")


def dispatch(player, raw):
    """Execute a single command line. Returns False if the player quit."""
    raw = raw.strip()
    if getattr(player, "god", False):   # [dev] god mode pins hp to full
        player.hp = player.max_hp
    if not hasattr(player, "seen"):     # you always know where you stand
        player.seen = set()
    player.seen.add(player.location)
    if getattr(player, "auto", None) is not None:
        player.auto = None
        say("(You break off the auto-fight.)", "byellow")
        if raw.lower() == "stop" or not raw:    # Enter/stop: just stand down
            return True
    # interactive combat captures every command (Enter = attack); quit still works
    if getattr(player, "combat", None) is not None:
        if raw.lower() in ("quit", "exit", "q"):
            say("Farewell, adventurer. May your bank be ever full.", "gold")
            return False
        combat_action(player, raw)
        _regen_energy(player)
        _check_achievements(player)
        _backup_nudge(player)
        return True
    if not raw:                         # empty Enter repeats your last command
        raw = getattr(player, "last_cmd", "")
        if not raw:
            return True
        say(f"(again: {raw})", "grey")
    parts = raw.split(maxsplit=1)
    verb = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    if verb in ("quit", "exit", "q"):
        say("Farewell, adventurer. May your bank be ever full.", "gold")
        return False
    if verb in DIRECTIONS or verb in ROOMS[player.location]["exits"] \
            or verb in HANDLERS:
        player.last_cmd = raw           # something real: remember it for Enter
    if verb in DIRECTIONS:
        cmd_go(player, DIRECTIONS[verb])
    elif verb in ROOMS[player.location]["exits"]:
        cmd_go(player, verb)
    else:
        handler = HANDLERS.get(verb)
        if handler:
            if verb in BATCHABLE:
                barg, n = _split_count(arg)
                if n > 1:
                    _run_batch(player, handler, barg, n)
                else:
                    handler(player, barg)
            else:
                handler(player, arg)
        else:
            close = difflib.get_close_matches(
                verb, list(HANDLERS) + list(ROOMS[player.location]["exits"]),
                n=1, cutoff=0.65)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            say(f"You don't know how to do that.{hint} Type 'help'.")
    # acting (anything but travelling) slowly restores run energy
    if verb not in ("travel", "rest"):
        _regen_energy(player)
    _check_achievements(player)
    _backup_nudge(player)
    return True


def run(player, greet=True):
    if greet:
        print(paint(f"\nWelcome to Gielinor, {player.name}! ", "bgreen", "bold")
              + paint("Type 'help' for commands.", "grey"))
        _intro_tips()
        print()
        cmd_look(player, "")
    while True:
        try:
            raw = input(paint("\n> ", "bgreen", "bold"))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not dispatch(player, raw):
            break


def main():
    show_art(LOGO, "gold")
    print(paint("        Adventures in Gielinor".center(78), "bgreen"))
    print(paint("   A love letter to Old School RuneScape".center(78),
                "grey"))
    rule("brown")
    player = None
    if os.path.exists(SAVE_PATH):
        choice = input(paint("\nA saved game exists. Load it? (y/n) ",
                             "byellow")).strip().lower()
        if choice.startswith("y"):
            player = load_game()
            _resume_summary(player)
            run(player, greet=False)
            return
    name = input(paint("\nWhat is your name, adventurer? ",
                       "bcyan")).strip() or "Guest"
    run(Player(name))


