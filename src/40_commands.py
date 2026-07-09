# ===========================================================================
#  COMMAND HANDLERS
# ===========================================================================
def gather_chance(level, req):
    return clamp(0.45 + (level - req) * 0.03, 0.45, 0.95)


# ===========================================================================
#  WORLD MAP
# ===========================================================================
# Each room belongs to a region; the region map highlights where you are.
REGIONS = {
    "lumbridge_castle": "Lumbridge", "general_store": "Lumbridge",
    "lumbridge_forest": "Lumbridge", "lumbridge_farm": "Lumbridge",
    "windmill": "Lumbridge", "river_lum": "Lumbridge", "swamp": "Lumbridge",
    "cow_field": "Lumbridge",
    "al_kharid_gate": "AlKharid", "al_kharid_square": "AlKharid",
    "al_kharid_mine": "AlKharid", "al_kharid_palace": "AlKharid",
    "draynor_path": "Draynor", "draynor_village": "Draynor",
    "draynor_manor": "Draynor",
    "varrock_gate": "Varrock", "varrock_square": "Varrock",
    "varrock_west_bank": "Varrock", "varrock_east_bank": "Varrock",
    "grand_exchange": "Grand Exchange", "varrock_palace": "Varrock",
    "essence_mine": "Varrock",
    "barbarian_village": "Barbarian",
    "edgeville": "Edgeville", "edgeville_dungeon": "Edgeville",
    "wilderness_edge": "Wilderness",
    "falador_east": "Falador", "falador_square": "Falador",
    "falador_west": "Falador", "dwarven_mine": "Falador",
    "rimmington": "Rimmington", "port_sarim": "PortSarim",
    "karamja_port": "Karamja",
    "lumbridge_church": "Lumbridge", "varrock_sewers": "Varrock",
    "wizard_tower": "Draynor", "stronghold_security": "Barbarian",
    "air_altar": "Falador", "members_dungeon": "Edgeville",
    "kbd_lair": "Wilderness", "agility_course": "Barbarian",
}

REGION_MAP = r"""
                   [Wilderness]  [Grand Exch]
                        |              |
    [Edgeville]----[Barbarian]----[Varrock]
         |              |              |
    [Falador]----------/          [Lumbridge]----[AlKharid]
         |                          /       \
    [Rimmington]               [Draynor]   (desert)
         |
    [PortSarim]----[Karamja]
"""

# token in REGION_MAP for each region (for highlighting current location)
_REGION_TOKEN = {
    "Wilderness": "[Wilderness]", "Edgeville": "[Edgeville]",
    "Barbarian": "[Barbarian]", "Varrock": "[Varrock]",
    "Falador": "[Falador]", "Lumbridge": "[Lumbridge]",
    "AlKharid": "[AlKharid]", "Rimmington": "[Rimmington]",
    "Draynor": "[Draynor]", "PortSarim": "[PortSarim]", "Karamja": "[Karamja]",
    "Grand Exchange": "[Grand Exch]",
}


def render_region_map(current_region):
    m = REGION_MAP
    tok = _REGION_TOKEN.get(current_region)
    if tok and tok in m:
        m = m.replace(tok, paint(tok, "byellow", "bold"), 1)
    # tint the remaining brackets faintly
    return m


def local_compass(p):
    """A compact compass of the immediate exits — the always-on mini-map."""
    ex = ROOMS[p.location]["exits"]

    def nm(d):
        return ROOMS[ex[d]]["name"]
    out = []
    if "north" in ex:
        out.append("          " + paint("N ↑ ", "bcyan") + nm("north"))
    left = (paint("W ← ", "bcyan") + nm("west") + "   ") if "west" in ex else ""
    here = paint(f"[ {ROOMS[p.location]['name']} ]", "byellow", "bold")
    right = ("   " + paint("→ E ", "bcyan") + nm("east")) if "east" in ex else ""
    out.append("  " + left + here + right)
    if "south" in ex:
        out.append("          " + paint("S ↓ ", "bcyan") + nm("south"))
    others = [d for d in ex if d not in ("north", "south", "east", "west")]
    if others:
        out.append("  " + paint("also: ", "grey")
                   + paint(", ".join(others), "bcyan"))
    return "\n".join(out)


def _show_automap(p):
    mode = getattr(p, "automap", "compass")
    if mode == "compass":
        print(local_compass(p))
    elif mode == "full":
        print(render_region_map(REGIONS.get(p.location, "")))
        print(local_compass(p))


def cmd_map(p, arg):
    arg = arg.strip().lower()
    if arg in ("off", "compass", "full", "local", "on"):
        p.automap = {"on": "compass", "local": "compass"}.get(arg, arg)
        say(f"Auto-map is now: {p.automap}", "bgreen")
        return
    region = REGIONS.get(p.location, "")
    banner("World Map of Gielinor", color="bcyan", line_color="teal")
    print(render_region_map(region))
    print("  " + paint("You are in: ", "grey")
          + paint(region or "the unknown", "byellow", "bold")
          + paint(f"  ·  {ROOMS[p.location]['name']}", "white"))
    print()
    print(local_compass(p))
    say("\n  tip: 'map off|compass|full' sets the mini-map shown on each move.",
        "grey")


def cmd_automap(p, arg):
    if not arg.strip():
        say(f"Mini-map mode: {getattr(p, 'automap', 'compass')}  "
            f"(use 'automap off|compass|full')", "grey")
        return
    cmd_map(p, arg)


def cmd_membership(p, arg):
    arg = arg.strip().lower()
    if arg in ("off", "cancel"):
        p.members = False
        say("Membership disabled. Members areas are locked again.", "grey")
        return
    if p.members:
        say("You are already a member! Members areas and skills are unlocked.",
            "bmagenta")
        return
    p.members = True
    banner("MEMBERSHIP UNLOCKED", color="bmagenta", line_color="magenta")
    say("Welcome, member! You can now reach members areas (Deep Dungeon, the "
        "King Black Dragon's lair) and train members skills (thieving, "
        "agility). This tribute game grants it free.", "bmagenta")
    say("(Type 'membership off' to disable members content.)", "grey")


def cmd_pray(p, arg):
    arg = arg.strip().lower()
    mx = p.prayer_max()
    if p.prayer_points > mx:
        p.prayer_points = mx
    if arg in ("recharge", "altar", "restore"):
        if ROOMS[p.location].get("prayer_altar") or _house_perk(p, "chapel altar"):
            p.prayer_points = mx
            say(f"You pray at the altar. Prayer points restored to {int(mx)}.",
                "bmagenta")
            if p.location == "nardah":
                _nardah_blessing(p)
                say("The fountain's blessing washes over you \u2014 wounds, "
                    "poison and weariness, all gone.", "bcyan")
            if p.location == "jaldraocht":
                _jaldraocht_altar(p)
        else:
            say("You need a prayer altar (e.g. Lumbridge Church) to recharge.")
        return
    if arg in ("off", "none", "clear"):
        p.active_prayers = []
        say("You close your mind and deactivate all prayers.", "grey")
        return
    # players say 'ranged'; the old gods say 'missiles'
    arg = arg.replace("protect from ranged", "protect from missiles") \
             .replace("protect from range", "protect from missiles")
    if not arg:
        banner("Prayer", color="bmagenta", line_color="magenta")
        print("  " + paint(f"Prayer level {p.lvl('prayer')}", "bmagenta")
              + paint(f"   Points: {int(p.prayer_points)}/{mx}", "white"))
        if p.active_prayers:
            print("  " + paint("Active: " + ", ".join(p.active_prayers),
                               "bmagenta", "bold"))
        say()
        any_avail = False
        for name, (lvl, drain, boost, prot) in PRAYERS.items():
            if p.lvl("prayer") >= lvl:
                any_avail = True
                mark = "x" if name in p.active_prayers else " "
                desc = ", ".join(f"+{int(v*100)}% {k}" for k, v in boost.items()) \
                    or f"protect from {prot}"
                print(f"  [{mark}] {name:20} (lvl {lvl:2})  {desc}")
        if not any_avail:
            say("  You haven't unlocked any prayers yet (bury bones to train).",
                "grey")
        say("\n  'pray <name>' to toggle · 'pray off' · 'pray recharge' at an altar.",
            "grey")
        return
    if arg not in PRAYERS:
        say(f"There's no prayer called '{arg}'. Type 'pray' to list them.")
        return
    lvl, drain, boost, prot = PRAYERS[arg]
    if p.lvl("prayer") < lvl:
        say(f"You need prayer level {lvl} to use {arg}.")
        return
    if arg in p.active_prayers:
        p.active_prayers.remove(arg)
        say(f"You deactivate {arg}.", "grey")
        return
    if p.prayer_points <= 0:
        say("You have no prayer points left. Recharge at an altar.", "bmagenta")
        return
    p.active_prayers.append(arg)
    say(f"You activate {arg}.", "bmagenta", "bold")


def cmd_pickpocket(p, arg):
    if not getattr(p, "members", False):
        say("Thieving is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    targets = ROOMS[p.location].get("pickpocket", [])
    if not targets:
        say("There's no one here worth pickpocketing.")
        return
    target = arg.strip().lower() or targets[0]
    if target not in targets:
        say(f"You can't pickpocket a {target} here. Targets: {', '.join(targets)}")
        return
    lvl, xp, maxc, dmg = PICKPOCKET[target]
    if p.lvl("thieving") < lvl:
        say(f"You need thieving level {lvl} to pickpocket the {target}.")
        return
    chance = clamp(0.5 + (p.lvl("thieving") - lvl) * 0.02, 0.4, 0.95)
    if random.random() < chance:
        coins = random.randint(1, maxc)
        p.add("coins", coins)
        say(f"You slip a hand into the {target}'s pocket and lift {coins} coins.",
            "bgreen")
        p.gain_xp("thieving", xp)
    else:
        p.hp = max(0, p.hp - dmg)
        say(f"The {target} catches you! You're stunned for {dmg} damage. "
            f"(HP: {max(p.hp,0)}/{p.max_hp})", "bred")
        if p.hp <= 0:
            _handle_death(p)


def cmd_agility(p, arg):
    if not getattr(p, "members", False):
        say("Agility is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    course = ROOMS[p.location].get("agility_course")
    if not course:
        say("You need an agility course (the one at Barbarian Village).")
        return
    lvl, xp, dmg = AGILITY_COURSE if course is True else course
    if p.lvl("agility") < lvl:
        say(f"You need agility level {lvl} for this course.", "byellow")
        return
    if random.random() < clamp(0.6 + p.lvl("agility") * 0.01, 0.6, 0.97):
        say("You vault the obstacles and complete a clean lap!", "bgreen")
        p.gain_xp("agility", xp)
    else:
        p.hp = max(0, p.hp - dmg)
        say(f"You slip and take {dmg} damage, but pick yourself up. "
            f"(HP: {max(p.hp,0)}/{p.max_hp})", "bred")
        p.gain_xp("agility", xp // 2)
        if p.hp <= 0:
            _handle_death(p)


# ===========================================================================
#  TRAVEL & RUN ENERGY
# ===========================================================================
TRAVEL_HUBS = {
    "lumbridge": "lumbridge_castle", "varrock": "varrock_square",
    "falador": "falador_square", "al kharid": "al_kharid_square",
    "alkharid": "al_kharid_square", "draynor": "draynor_village",
    "edgeville": "edgeville", "barbarian village": "barbarian_village",
    "barbarian": "barbarian_village", "port sarim": "port_sarim",
    "portsarim": "port_sarim", "rimmington": "rimmington",
    "karamja": "karamja_port",
}
TRAVEL_NAMES = ["Lumbridge", "Varrock", "Falador", "Al Kharid", "Draynor",
                "Edgeville", "Barbarian Village", "Port Sarim", "Rimmington",
                "Karamja"]
ENERGY_REGEN = 5   # gained per non-travel action


def _travel_cost(p):
    # higher agility = cheaper running (30 down to a floor of 10)
    return int(clamp(30 - p.lvl("agility") * 0.25, 10, 30))


def _teleport_for(dest_room):
    for name, s in SPELLS.items():
        if s.get("type") == "tele" and s.get("dest") == dest_room:
            return name
    return None


def _regen_energy(p):
    p.actions = getattr(p, "actions", 0) + 1     # the world's clock ticks
    if getattr(p, "run_energy", 100) < 100:
        p.run_energy = min(100, p.run_energy + ENERGY_REGEN)
    # special energy and hitpoints recover slowly, out of combat only
    # (but nothing recovers under the desert sun)
    in_desert = ROOMS.get(p.location, {}).get("desert")
    if getattr(p, "combat", None) is None:
        if getattr(p, "spec_energy", 100) < 100:
            p.spec_energy = min(100, p.spec_energy + 10)
        if 0 < p.hp < p.max_hp and not in_desert:
            p.hp += 1
    if in_desert:                                   # the sun is a monster too
        p.heat = getattr(p, "heat", 0) + 1
        if p.heat >= 8:
            p.heat = 0
            if p.has("waterskin"):
                p.take("waterskin")
                say("You take a pull from a waterskin against the heat. "
                    f"({p.count('waterskin')} left)", "bcyan")
            else:
                dmg = min(random.randint(2, 4), max(0, p.hp - 1))
                if dmg > 0:
                    p.hp -= dmg
                    print("  " + paint(f"The desert sun sears you for {dmg}! "
                                       "(carry waterskins — Shantay sells "
                                       "them)", "orange"))
    f = getattr(p, "fire", None)         # campfires burn down over time
    if f:
        f["left"] -= 1
        if f["left"] <= 0:
            p.fire = None
            if p.location == f["room"]:
                say("Your fire burns down to embers.", "grey")


def cmd_travel(p, arg):
    dest = arg.strip().lower()
    if not dest:
        say("Travel to which city? " + ", ".join(TRAVEL_NAMES), "bcyan")
        say(f"Run energy: {int(getattr(p,'run_energy',100))}/100. Walking with "
            "n/s/e/w is always free.", "grey")
        return
    room = TRAVEL_HUBS.get(dest)
    if not room:
        close = difflib.get_close_matches(dest, list(TRAVEL_HUBS), 1, 0.6)
        hint = f" Did you mean '{close[0]}'?" if close else ""
        say(f"You don't know the way to '{arg}'.{hint} Cities: "
            + ", ".join(TRAVEL_NAMES))
        return
    if ROOMS[room].get("members") and not getattr(p, "members", False):
        say(f"{ROOMS[room]['name']} is in members' lands — you can't travel "
            "there yet. Type 'membership' to unlock it.", "bmagenta")
        return
    ql = ROOMS[room].get("qlock")
    if ql and _q(p, ql[0]) not in ql[1]:
        say(ql[2], "byellow")
        return
    if p.location == room:
        say(f"You're already in {ROOMS[room]['name']}.")
        return
    if p.location == "fight_caves" and getattr(p, "cave_wave", 0):
        p.cave_wave = 0
        say("You leave the Fight Caves — your run is abandoned.", "byellow")
    if ROOMS[p.location].get("inferno") and getattr(p, "inferno_wave", 0):
        p.inferno_wave = 0
        say("You leave the Inferno — your run is abandoned.", "byellow")
    # use a teleport spell if you can (runes + magic level) — no energy cost
    tp = _teleport_for(room)
    if tp:
        s = SPELLS[tp]
        if p.lvl("magic") >= s["lvl"] and _consume_runes(p, s["runes"]):
            p.location = room
            p.gain_xp("magic", s["xp"])
            say(f"You cast {tp} and vanish in a flash of light!", "bblue")
            cmd_look(p, "")
            _ambient(p)
            _maybe_ambush(p)
            return
    # otherwise run there, spending energy (cheaper with agility)
    cost = _travel_cost(p)
    if getattr(p, "run_energy", 100) < cost:
        if p.location in set(TRAVEL_HUBS.values()) or _house_perk(p, "oak bed"):
            cmd_rest(p, "")             # catch your breath, then set off
        else:
            say(f"You're too winded to run that far (need {cost} energy, have "
                f"{int(p.run_energy)}). 'rest' in a city, or walk with n/s/e/w.",
                "byellow")
            return
    p.run_energy -= cost
    say(f"You set off and travel to {ROOMS[room]['name']}.  "
        + paint(f"(-{cost} energy → {int(p.run_energy)}/100)", "grey"), "bgreen")
    p.location = room
    cmd_look(p, "")
    _ambient(p)
    _maybe_ambush(p)


def cmd_rest(p, _a):
    in_bed = _house_perk(p, "oak bed")
    if p.location not in set(TRAVEL_HUBS.values()) and not in_bed:
        say("You can only rest in a major city — or your own bed at home.",
            "grey")
        return
    if getattr(p, "run_energy", 100) >= 100 and p.hp >= p.max_hp and \
            getattr(p, "spec_energy", 100) >= 100 and \
            (not in_bed or p.prayer_points >= p.prayer_max()):
        say("You're already fully rested.", "grey")
        return
    p.run_energy = 100
    p.spec_energy = 100
    p.hp = p.max_hp
    if in_bed:
        p.prayer_points = p.prayer_max()
        say("You sleep soundly in your own bed — everything restored, even "
            "your prayers.", "bgreen")
    else:
        say("You rest a while in the city — hitpoints, run and special energy "
            "fully restored.", "bgreen")


def cmd_look(p, _a):
    r = ROOMS[p.location]
    banner(r["name"], color="bcyan", line_color="teal")
    say(r["desc"], "white")
    services = []
    for flag, label in [("bank", "bank"), ("range", "cooking range"),
                        ("furnace", "furnace"), ("anvil", "anvil"),
                        ("ge", "Grand Exchange"), ("spinning_wheel", "spinning wheel"),
                        ("tanner", "tanner")]:
        if r.get(flag):
            services.append(paint(label, "bmagenta"))
    if r.get("shop"):
        services.append(paint("shop", "bmagenta"))
    if r.get("trees"):
        services.append(paint("trees: " + ", ".join(r["trees"]), "bgreen"))
    if r.get("rocks"):
        services.append(paint("rocks: " + ", ".join(r["rocks"]), "brown"))
    if r.get("fish_tools"):
        services.append(paint("fishing spot", "bblue"))
    if r.get("stalls"):
        services.append(paint("stalls to 'steal' from: "
                              + ", ".join(r["stalls"]), "purple"))
    if r.get("pick"):
        services.append(paint("'pick': " + ", ".join(r["pick"]), "lime"))
    if p.location == "your_house":
        built = getattr(p, "house", [])
        services.append(paint("furniture: " + (", ".join(built) if built
                              else "none yet — 'build'"), "brown"))
    if r.get("gwd"):
        kc = getattr(p, "gwd_kc", {})
        kcs = ", ".join(f"{g} {n}" for g, n in sorted(kc.items()) if n)
        services.append(paint("kill count: " + (kcs or "none — slay "
                              "followers (10 opens a god's door)"),
                              "bmagenta"))
    for ptype in r.get("patches", []):
        crop = getattr(p, "farm", {}).get(f"{p.location}:{ptype}")
        if crop:
            ready, left = _patch_state(p, crop)
            services.append(paint(
                f"{ptype} patch: {crop['seed'].replace(' seed', '')}"
                + (" — READY ('harvest')" if ready
                   else f" (~{left} actions to grow)"), "green"))
        else:
            services.append(paint(f"{ptype} patch: empty — 'plant <seed>'",
                                  "green"))
    mons = _room_monsters(p)
    if mons:
        services.append(paint("monsters: " + ", ".join(mons), "bred"))
    if r.get("npc"):
        services.append(paint("someone to 'talk' to", "byellow"))
    if services:
        print(paint("\n  Here: ", "grey") + "; ".join(services))
    print(paint("  Exits: ", "grey")
          + paint(", ".join(r["exits"].keys()), "bcyan"))
    _show_automap(p)


def cmd_go(p, arg):
    r = ROOMS[p.location]
    d = arg.strip().lower()
    if d not in r["exits"]:
        d = DIRECTIONS.get(d, d)            # 'go n' means 'go north'
    if d not in r["exits"]:
        # a compass direction that simply isn't an exit stays a refusal;
        # anything else may be a place: 'go bank', 'go cow field'
        if d not in DIRECTIONS.values() and cmd_goto(p, d, quiet_fail=True):
            return
        say("You can't go that way.")
        return
    dest = r["exits"][d]
    if ROOMS[dest].get("members") and not getattr(p, "members", False):
        say("A magical barrier blocks the way — that area is members-only.",
            "bmagenta")
        say("(Type 'membership' to unlock members content in this tribute game.)",
            "grey")
        return
    ql = ROOMS[dest].get("qlock")   # some places are locked behind a quest
    if ql and _q(p, ql[0]) not in ql[1]:
        say(ql[2], "byellow")
        return
    sl = ROOMS[dest].get("stat_lock")   # guild doors weigh your levels
    if sl:
        skills, need, msg = sl
        have = sum(p.lvl(s) for s in skills)
        if have < need:
            say(msg, "byellow")
            say(f"  ({' + '.join(skills)} = {have}, needs {need}.)", "grey")
            return
    gl = ROOMS[dest].get("gear_lock")   # some doors demand a disguise
    if gl:
        worn = set(filter(None, p.equipment.values()))
        # each entry may offer alternatives: "fire cape|infernal cape"
        if any(not any(alt in worn for alt in i.split("|")) for i in gl[0]):
            say(gl[1], "byellow")
            say("  (You must be wearing: "
                + ", ".join(i.replace("|", " or ") for i in gl[0]) + ".)",
                "grey")
            return
    kcl = ROOMS[dest].get("kc_lock")    # god doors drink kill count
    if kcl:
        god, need = kcl
        have = getattr(p, "gwd_kc", {}).get(god, 0)
        if have < need:
            say(f"The great door of {god.title()} is sealed. Slay {god}'s "
                f"followers in this dungeon to earn entry "
                f"({have}/{need} kill count).", "byellow")
            return
        p.gwd_kc[god] = have - need
        say(f"The door drinks your kill count (-{need}) and grinds open...",
            "bmagenta")
    key = ROOMS[dest].get("key")        # some doors need (and consume) a key
    if key and p.location != dest:
        if not p.has(key):
            say(f"The way is locked. You need a {key} to enter.", "byellow")
            return
        p.take(key)
        say(f"You unlock the door with the {key}.", "bgreen")
    fee = ROOMS[dest].get("fee")        # some doors charge admission
    if fee:
        cost, msg = fee
        if not p.has("coins", cost):
            say(msg, "byellow")
            say(f"  (Entry costs {cost} coins — you can't pay.)", "grey")
            return
        p.take("coins", cost)
        say(f"You pay the {cost} coin entry fee.", "grey")
    if p.location == "fight_caves" and getattr(p, "cave_wave", 0):
        p.cave_wave = 0             # walking out abandons the run
        say("You leave the Fight Caves — your run is abandoned.", "byellow")
    if ROOMS[p.location].get("inferno") and getattr(p, "inferno_wave", 0):
        p.inferno_wave = 0
        say("You leave the Inferno — your run is abandoned.", "byellow")
    if p.location == "plunder_pyramid" and getattr(p, "plunder_tier", 0):
        p.plunder_tier = 0          # daylight resets the pyramid's depths
    if ROOMS[p.location].get("toll") and dest == "al_kharid_square":
        if _q(p, "prince_ali") == "complete":       # Prince Ali Rescue reward
            say("The gate guards recognise the prince's rescuer and wave you "
                "through for free.", "bgreen")
        else:
            toll = ROOMS[p.location]["toll"]
            if not p.has("coins", toll):
                say(f"The gate guard demands {toll} coins. You can't afford it.")
                return
            p.take("coins", toll)
            say(f"You pay the {toll} coin toll.")
    p.location = dest
    getattr(p, "seen", set()).add(dest)
    cmd_look(p, "")
    _ambient(p)
    _maybe_ambush(p)


# --- goto: auto-walk anywhere you've already discovered --------------------
def _bfs_path(p, is_target):
    """Shortest walk from here to a target, through discovered rooms only.
    Returns a list of exit directions, or None. You can only auto-walk
    roads you've walked before — exploring stays a hands-on affair."""
    seen = (getattr(p, "seen", None) or set()) | {p.location}
    if is_target(p.location):
        return []
    came = {p.location: None}           # room -> (previous room, direction)
    queue = [p.location]
    i = 0
    while i < len(queue):
        cur = queue[i]
        i += 1
        for d, nxt in ROOMS[cur]["exits"].items():
            if nxt in came or nxt not in seen:
                continue
            came[nxt] = (cur, d)
            if is_target(nxt):
                path = []
                node = nxt
                while came[node]:
                    node, step = came[node]
                    path.append(step)
                return path[::-1]
            queue.append(nxt)
    return None


def _walk_path(p, path):
    """Follow a list of exit directions, stopping honestly at trouble."""
    crumbs = []
    for d in path:
        before = p.location
        coins0 = p.count("coins")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_go(p, d)
        if p.location == before:            # a locked/tolled door said no
            if crumbs:
                say("You walk: " + " → ".join(crumbs) + " …and stop short.",
                    "bcyan")
            print(buf.getvalue(), end="")   # replay the refusal, loudly
            return True
        crumbs.append(d)
        if getattr(p, "combat", None) is not None:      # ambushed en route!
            say("You walk: " + " → ".join(crumbs), "bcyan")
            print(buf.getvalue(), end="")   # the ambush, as you'd have seen it
            return True
        if p.count("coins") < coins0:       # a door took payment — show it
            print(buf.getvalue(), end="")
        if len(crumbs) < len(path):
            _regen_energy(p)                # each step moves the world
    say("You walk: " + " → ".join(crumbs) + ".", "bcyan")
    cmd_look(p, "")
    return True


# 'goto <service>' finds the nearest discovered room offering it
_GOTO_SERVICES = {"bank": "bank", "ge": "ge", "grand exchange": "ge",
                  "anvil": "anvil", "furnace": "furnace", "range": "range",
                  "kitchen": "range", "altar": "prayer_altar", "shop": "shop",
                  "spinning wheel": "spinning_wheel", "tanner": "tanner"}


def cmd_goto(p, arg, quiet_fail=False):
    """Auto-walk to any place you've discovered: 'goto draynor village',
    'goto bank'. Stops at locked doors and ambushes, like honest feet."""
    want = arg.strip().lower().replace("_", " ")
    if getattr(p, "combat", None) is not None:
        say("Not while something is trying to kill you!", "bred")
        return True
    if not want:
        say("Go where? 'goto <place>' walks you anywhere you've explored — "
            "try 'goto bank' or 'goto cow field'.", "grey")
        return True
    svc = _GOTO_SERVICES.get(want)
    if svc:
        path = _bfs_path(p, lambda room: ROOMS[room].get(svc))
        if path is None:
            say(f"You don't know anywhere around here with a {want}. "
                "Explore, or 'travel' to a city.", "grey")
        elif not path:
            say(f"There's a {want} right here.", "grey")
        else:
            _walk_path(p, path)
        return True
    seen = (getattr(p, "seen", None) or set()) | {p.location}

    def label(k):
        return ROOMS[k]["name"].lower()
    hits = [k for k in seen if k.replace("_", " ") == want or label(k) == want]
    if not hits:
        hits = [k for k in seen
                if want in k.replace("_", " ") or want in label(k)]
    if not hits:
        # a city you've never walked to? take the road — that's what feet
        # would do ('goto varrock' on a fresh character just travels)
        hub = want if want in TRAVEL_HUBS else \
            next((c for c in TRAVEL_HUBS if want in c), None)
        if hub:
            say(f"You don't know the streets yet — you take the road to "
                f"{hub.title()} instead.", "grey")
            cmd_travel(p, hub)
            return True
        anywhere = [k for k in ROOMS if want in k.replace("_", " ")
                    or want in label(k)]
        if quiet_fail and not anywhere:
            return False                    # let 'go' print its own refusal
        if anywhere:
            say(f"You haven't found the way to {ROOMS[anywhere[0]]['name']} "
                "yet — explore, or 'travel' to a city and walk from there.",
                "grey")
        else:
            close = difflib.get_close_matches(
                want, [label(k) for k in seen], 1, 0.6)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            say(f"You don't know a place called '{arg.strip()}'.{hint}",
                "grey")
        return True
    targets = set(hits)
    if targets == {p.location}:
        say("You're already there.", "grey")
        return True
    targets.discard(p.location)
    path = _bfs_path(p, lambda room: room in targets)
    if path is None:                        # discovered, but across the sea
        hub = next((c for c, r in TRAVEL_HUBS.items() if r in targets), None)
        if hub:
            say("No walking route that you know — you take the road.",
                "grey")
            cmd_travel(p, hub)
        else:
            say("No walking route that you know — 'travel' to a nearby "
                "city and walk from there.", "grey")
        return True
    _walk_path(p, path)
    return True


# skill -> theme colour for the stats screen
SKILL_COLOR = {
    "attack": "bred", "strength": "bred", "defence": "bred",
    "hitpoints": "bred", "ranged": "bgreen", "prayer": "bwhite",
    "magic": "bblue", "cooking": "orange", "woodcutting": "bgreen",
    "fishing": "bcyan", "firemaking": "orange", "crafting": "brown",
    "smithing": "grey", "mining": "brown", "runecrafting": "bmagenta",
    "thieving": "purple", "agility": "lime", "slayer": "teal",
    "herblore": "lime", "fletching": "bcyan", "farming": "green",
    "construction": "brown", "hunter": "orange",
}


def _resolve_skill(name):
    """Match a (possibly abbreviated) skill name; return the skill or None."""
    name = (name or "").strip().lower()
    if name in SKILLS:
        return name
    matches = [s for s in SKILLS if s.startswith(name)]
    return matches[0] if len(matches) == 1 else None


def _show_skill_detail(p, skill):
    xp = p.skills[skill]
    lvl, into, span, to_next = xp_progress(xp)
    color = SKILL_COLOR.get(skill, "white")
    banner(f"{skill.title()} — level {p.lvl(skill)}", color=color)
    print("  " + paint(f"Total XP: {xp:,}", "white")
          + (paint("   (members skill)", "bmagenta")
             if skill in MEMBERS_SKILLS else ""))
    if lvl >= 99:
        say("  Mastered — level 99!", "gold", "bold")
    else:
        print("  " + paint(f"L{lvl} ", "grey")
              + bar_meter(into, span, 24, fill_color=color)
              + paint(f" L{lvl + 1}", "grey"))
        say(f"  {to_next:,} xp to level {lvl + 1}.", "bcyan")
    boost = getattr(p, "stat_boost", {}).get(skill, 0)
    drain = getattr(p, "stat_drain", {}).get(skill, 0)
    if boost:
        say(f"  Temporarily boosted +{boost}.", "lime")
    if drain:
        say(f"  Temporarily drained -{drain}.", "bblue")


def cmd_stats(p, arg=""):
    skill = _resolve_skill(arg)
    if (arg or "").strip():
        if skill:
            return _show_skill_detail(p, skill)
        return say("No such skill. Type 'stats' for the overview, or "
                   "'stats <skill>' for detail.", "grey")
    banner(f"{p.name} — Combat level {p.combat_level()}", color="gold")
    print("  " + paint("Hitpoints ", "white")
          + bar_meter(p.hp, p.max_hp, 22)
          + paint(f"   Coins: {p.coins:,}", "gold"))
    style_str = paint(p.style, STYLE_COLOR.get(p.style, "white"), "bold")
    if p.style == "magic":
        style_str += paint(f" ({p.autocast})", "grey")
    print("  " + paint("Style: ", "white") + style_str
          + paint("    Run energy ", "white")
          + bar_meter(int(getattr(p, "run_energy", 100)), 100, 16, fill_color="lime")
          + (paint("   [member]", "bmagenta") if p.members else ""))
    say()
    total = 0
    total_xp = 0
    cols = []
    for s in SKILLS:
        total += p.lvl(s)
        total_xp += p.skills[s]
        label = paint(f"{s:12}", SKILL_COLOR.get(s, "white"))
        cols.append(f"{label}{paint(f'{p.lvl(s):2}', 'bwhite', 'bold')}")
    for i in range(0, len(cols), 3):
        print("  " + "   ".join(cols[i:i + 3]))
    print("\n  " + paint(f"Total level: {total}", "gold", "bold")
          + paint(f"    Total XP: {total_xp:,}", "white"))
    print("  " + paint("Tip: 'stats <skill>' shows xp and progress to the "
                       "next level.", "grey"))


def cmd_inventory(p, _a):
    banner("Inventory", color="bgreen")
    if not p.inventory:
        say("Empty.")
        return
    n = len(p.inventory)
    print(paint(f"  {n} item type(s)  ·  {p.coins:,} coins", "grey"))
    for item, q in sorted(p.inventory.items()):
        qty = f" x{q}" if q > 1 else ""
        worth = ITEMS.get(item, {}).get("value", 0) * q
        print("  " + paint(item, item_rarity_color(item))
              + paint(qty, "grey")
              + paint(f"   ({worth:,} gp)" if worth >= 50 else "", "grey"))


def cmd_equipment(p, _a):
    banner("Worn Equipment")
    for slot in EQUIP_SLOTS:
        say(f"  {slot:7}: {p.equipment[slot] or '(empty)'}")
    eb = p.equip_bonus
    say("")
    print("  " + paint("Attack ", "white")
          + paint(f"stab {eb('astab'):+d}  slash {eb('aslash'):+d}  "
                  f"crush {eb('acrush'):+d}  magic {eb('amagic'):+d}  "
                  f"ranged {eb('arange'):+d}", "bcyan"))
    print("  " + paint("Defence", "white")
          + paint(f" stab {eb('dstab'):+d}  slash {eb('dslash'):+d}  "
                  f"crush {eb('dcrush'):+d}  magic {eb('dmagic'):+d}  "
                  f"ranged {eb('drange'):+d}", "byellow"))
    print("  " + paint("Other  ", "white")
          + paint(f" melee-str {eb('str'):+d}  ranged-str {eb('rstr'):+d}  "
                  f"magic-dmg {eb('mdmg'):+d}%  prayer {eb('prayer'):+d}", "grey"))
    print("  " + paint(f"Melee stance: {getattr(p, 'attack_type', 'slash')}  "
                       f"(change with 'style stab|slash|crush')", "grey"))


def cmd_equip(p, arg):
    item = arg.strip().lower()
    if not item:
        say("Equip what?")
        return
    if item not in p.inventory:         # 'equip scim' finds rune scimitar
        wearable = [i for i in p.inventory if ITEMS.get(i, {}).get("equip")]
        found = _resolve_named(item, wearable)
        if found is _ASKED:
            return
        if found:
            item = found
    p.equip_item(item)


def cmd_unequip(p, arg):
    slot = arg.strip().lower()
    if slot not in EQUIP_SLOTS:
        # accept the worn item's name too: 'unequip scimitar'
        worn = {v: k for k, v in p.equipment.items() if v}
        found = _resolve_named(slot, worn)
        if found is _ASKED:
            return
        if found:
            slot = worn[found]
        else:
            say(f"Slots: {', '.join(EQUIP_SLOTS)} — or name the worn item.")
            return
    p.unequip(slot)


def cmd_style(p, arg):
    s = arg.strip().lower()
    if s in ("stab", "slash", "crush"):       # melee attack stance
        p.attack_type = s
        p.style = "melee"
        wpn = p.equipment.get("weapon")
        bonus = ITEMS.get(wpn, {}).get("equip", {}).get(AKEY[s], 0) if wpn else 0
        note = "" if bonus > 0 else paint("  (your weapon isn't suited to that — "
                                          "accuracy will suffer)", "grey")
        say(f"You switch to a {s}bing stance." if s == "stab"
            else f"You switch to a {s}ing stance.", "bcyan")
        if note:
            print(note)
        return
    if s in ("melee", "ranged", "magic"):
        p.style = s
        extra = ""
        if s == "melee":
            extra = f" (attack type: {getattr(p, 'attack_type', 'slash')})"
        say(f"Combat style set to {s}.{extra}")
        if s == "magic":
            # auto-pick the strongest spell you can cast, unless the player
            # has deliberately chosen something beyond the starter spell
            book = getattr(p, "spellbook", "standard")
            castable = [n for n, d in SPELLS.items() if d["type"] == "combat"
                        and d.get("book", "standard") == book
                        and p.lvl("magic") >= d["lvl"]]
            cur = SPELLS.get(p.autocast)
            if castable and (not cur or p.autocast == "wind strike"):
                p.autocast = max(castable, key=lambda n: SPELLS[n]["max"])
                say(f"  (Autocasting {p.autocast} — 'autocast <spell>' to "
                    "change.)", "grey")
        return
    say(f"Current style: {p.style} "
        f"(melee type: {getattr(p, 'attack_type', 'slash')}).", "bcyan")
    say("Choose a style: melee, ranged, magic — or a melee stance: "
        "stab, slash, crush.", "grey")


def cmd_autocast(p, arg):
    spell = arg.strip().lower()
    book = getattr(p, "spellbook", "standard")
    if spell not in SPELLS or SPELLS[spell]["type"] != "combat":
        combat_spells = [s for s in SPELLS if SPELLS[s]["type"] == "combat"
                         and SPELLS[s].get("book", "standard") == book]
        say(f"Combat spells ({book} book): " + ", ".join(combat_spells))
        return
    if SPELLS[spell].get("book", "standard") != book:
        say(f"{spell.title()} belongs to the "
            f"{SPELLS[spell].get('book', 'standard')} spellbook — swap "
            "books at its altar.", "byellow")
        return
    if p.lvl("magic") < SPELLS[spell]["lvl"]:
        can = [s for s in SPELLS if SPELLS[s]["type"] == "combat"
               and SPELLS[s].get("book", "standard") == book
               and p.lvl("magic") >= SPELLS[s]["lvl"]]
        say(f"You need magic level {SPELLS[spell]['lvl']} to cast {spell}."
            + (f" You can cast: {', '.join(can)}." if can else ""), "byellow")
        return
    p.autocast = spell
    p.style = "magic"
    say(f"You will autocast {spell}. Style set to magic.")


# --- gathering ------------------------------------------------------------
def cmd_chop(p, arg):
    a = arg.strip().lower()
    if a and _gem_uncut(a):             # 'cut sapphire' = gem cutting
        return cmd_cutgem(p, a)
    r = ROOMS[p.location]
    trees = r.get("trees", [])
    if not trees:
        say("No trees here.")
        return
    tree = arg.strip().lower()
    if not tree:            # bare 'chop': best tree you can actually cut here
        can = [t for t in trees if p.lvl("woodcutting") >= TREES[t][1]]
        tree = max(can, key=lambda t: TREES[t][1]) if can else trees[0]
    if tree not in trees:
        say(f"No {tree} tree here. Available: {', '.join(trees)}")
        return
    if not p.find_tool("axe"):
        say("You need an axe.")
        return
    product, req, xp = TREES[tree]
    if p.lvl("woodcutting") < req:
        say(f"You need woodcutting level {req} to chop {tree}.")
        can = [t for t in trees if p.lvl("woodcutting") >= TREES[t][1]]
        if can:
            say("  (Here you can chop: " + ", ".join(can) + ".)", "grey")
        return
    say(f"You swing your axe at the {tree}...")
    eff = p.lvl("woodcutting")
    if "dragon axe" in p.inventory or p.equipment.get("weapon") == "dragon axe":
        eff += 3                        # the dragon axe bites deeper
    if random.random() < gather_chance(eff, req):
        p.add(product)
        say(f"You get some {product}.")
        p.gain_xp("woodcutting", xp)
        if random.random() < 1 / 32:
            _birds_nest(p)
        return True
    say("You fail to get any logs this time.")
    return False


def cmd_mine(p, arg):
    r = ROOMS[p.location]
    rocks = r.get("rocks", [])
    if not rocks:
        say("No rocks here.")
        return
    rock = arg.strip().lower()
    if not rock:            # bare 'mine': best rock you can actually mine here
        can = [x for x in rocks if p.lvl("mining") >= ROCKS[x][1]]
        rock = max(can, key=lambda x: ROCKS[x][1]) if can else rocks[0]
    if rock not in rocks:
        say(f"No {rock} here. Available: {', '.join(rocks)}")
        return
    if rock != "rune essence" and not p.find_tool("pickaxe"):
        say("You need a pickaxe.")
        return
    product, req, xp = ROCKS[rock]
    if p.lvl("mining") < req:
        say(f"You need mining level {req} to mine {rock}.")
        can = [r2 for r2 in rocks if p.lvl("mining") >= ROCKS[r2][1]]
        if can:
            say("  (Here you can mine: " + ", ".join(can) + ".)", "grey")
        return
    say(f"You swing your pickaxe at the {rock} rock...")
    eff = p.lvl("mining")
    if "dragon pickaxe" in p.inventory \
            or p.equipment.get("weapon") == "dragon pickaxe":
        eff += 3                        # the dragon pickaxe bites deeper
    if random.random() < gather_chance(eff, req):
        if rock == "gem rock":              # Shilo's mine: every strike a gem
            product = random.choices(list(GEM_CUT), weights=[8, 5, 2, 1])[0]
        p.add(product)
        say(f"You manage to mine some {product}.")
        p.gain_xp("mining", xp)
        if rock != "rune essence" and random.random() < 0.025:
            gem = random.choices(list(GEM_CUT), weights=[8, 5, 2, 1])[0]
            p.add(gem)
            say(f"Your pickaxe strikes something hard — an {gem}!", "bcyan")
        return True
    say("You only chip the rock.")
    return False


def cmd_fish(p, arg):
    r = ROOMS[p.location]
    tools = r.get("fish_tools", [])
    if not tools:
        say("No fishing spot here.")
        return
    # choose a tool the player has
    tool_map = {"net": "net", "rod": "rod", "fly": "fly",
                "harpoon": "harpoon", "cage": "cage"}
    usable = [t for t in tools if p.find_tool(tool_map[t])]
    if not usable:
        needed = {"net": "small fishing net", "rod": "fishing rod",
                  "fly": "fly fishing rod", "harpoon": "harpoon",
                  "cage": "lobster pot"}
        say("You need: " + " or ".join(needed[t] for t in tools))
        return
    want = arg.strip().lower()
    tool = usable[0]
    if want:                        # 'fish harpoon' / 'fish lobster' etc.
        by_tool = next((t for t in usable if want in t), None)
        by_fish = next((t for t in usable
                        for prod, _l, _x in FISH[t] if want in prod), None)
        picked = by_tool or by_fish
        if not picked:
            say(f"You can't fish '{want}' here. Spots: "
                + ", ".join(f"{t} ({', '.join(pr.replace('raw ', '') for pr, _l, _x in FISH[t])})"
                            for t in usable), "grey")
            return
        tool = picked
    options = [o for o in FISH[tool] if p.lvl("fishing") >= o[1]]
    if not options:
        say(f"You need fishing level {FISH[tool][0][1]} to fish here.")
        return
    product, req, xp = max(options, key=lambda o: o[1])
    say("You cast out your line...")
    if random.random() < gather_chance(p.lvl("fishing"), req):
        p.add(product)
        say(f"You catch some {product}.")
        p.gain_xp("fishing", xp)
        return True
    say("You fail to catch anything.")
    return False


# --- processing -----------------------------------------------------------
def _has_fire(p):
    f = getattr(p, "fire", None)
    return bool(f and f["room"] == p.location and f["left"] > 0)


def _house_perk(p, furniture):
    """True when standing in your house with that furniture built."""
    return p.location == "your_house" and furniture in getattr(p, "house", [])


def cmd_cook(p, arg):
    r = ROOMS[p.location]
    if not (r.get("range") or r.get("fire") or _has_fire(p)
            or _house_perk(p, "kitchen range")):
        say("You need a cooking range or a fire ('light logs' with a "
            "tinderbox — or 'goto range' finds a kitchen).")
        return
    raw = arg.strip().lower()
    cookable = [i for i in p.inventory if i in RAW_TO_COOKED]
    if not raw:
        if not cookable:
            say("You have nothing to cook.")
            return
        raw = cookable[0]
    if raw not in RAW_TO_COOKED:
        say(f"You can't cook {raw}.")
        return
    if not p.has(raw):
        say(f"You have no {raw}.")
        return
    cooked, burnt, req = RAW_TO_COOKED[raw]
    p.take(raw)
    if p.lvl("cooking") < req:
        say(f"You need cooking level {req} for that.")
        p.add(raw)
        return
    burn_chance = clamp(0.55 - (p.lvl("cooking") - req) * 0.03, 0.02, 0.55)
    if random.random() > burn_chance:
        p.add(cooked)
        say(f"You cook the {raw} into {cooked}.")
        p.gain_xp("cooking", COOK_XP[raw])
        return True
    p.add(burnt)
    say(f"Oops! You burn the {raw}.")
    return False


def cmd_light(p, arg):
    if not p.find_tool("tinderbox"):
        say("You need a tinderbox.")
        return
    logs = arg.strip().lower() or "logs"
    if logs not in ITEMS or "log_fm_xp" not in ITEMS[logs]:
        say("You can't light that.")
        return
    if not p.has(logs):
        say(f"You have no {logs}.")
        return
    p.take(logs)
    p.fire = {"room": p.location, "left": 25}
    say(f"You light the {logs}. A fire crackles to life — you can 'cook' "
        "over it here while it burns.")
    p.gain_xp("firemaking", ITEMS[logs]["log_fm_xp"])
    return True


def cmd_bury(p, arg):
    bone = arg.strip().lower() or "bones"
    if bone not in ITEMS or "bury" not in ITEMS[bone]:
        # bury any bones
        bone = "big bones" if p.has("big bones") else "bones"
    if not p.has(bone):
        say("You have no bones to bury.")
        return
    p.take(bone)
    skill, xp = ITEMS[bone]["bury"]
    say(f"You dig a hole and bury the {bone}.")
    if ROOMS[p.location].get("chaos_altar"):
        xp = int(xp * 1.5)
        say("The chaos altar drinks the offering greedily. (+50% xp)",
            "purple")
    p.gain_xp(skill, xp)
    return True


def cmd_smelt(p, arg):
    r = ROOMS[p.location]
    if not r.get("furnace"):
        say("You need a furnace. ('goto furnace' knows the way.)")
        return
    bar = arg.strip().lower()
    if not bar.endswith("bar"):
        bar = bar + " bar" if bar else ""
    if bar not in SMELT:
        say("Smeltable bars: " + ", ".join(SMELT))
        return
    ores, req, xp = SMELT[bar]
    if p.lvl("smithing") < req:
        say(f"You need smithing level {req} to smelt {bar}.")
        return
    for ore, q in ores.items():
        if not p.has(ore, q):
            say(f"You need {q}x {ore}.")
            return
    for ore, q in ores.items():
        p.take(ore, q)
    # iron has a 50% chance to fail (a ring of forging never fails)
    if bar == "iron bar" and p.equipment.get("ring") != "ring of forging" \
            and random.random() < 0.5:
        say("The iron ore is too impure — the bar is ruined.")
        p.gain_xp("smithing", xp // 4)
        return False
    p.add(bar)
    say(f"You smelt a {bar}.")
    p.gain_xp("smithing", xp)
    return True


def cmd_smith(p, arg):
    r = ROOMS[p.location]
    if not (r.get("anvil") or _house_perk(p, "workbench")):
        say("You need an anvil. ('goto anvil' knows the way.)")
        return
    if not p.find_tool("hammer"):
        say("You need a hammer.")
        return
    arg = arg.strip().lower()
    if "godsword" in arg:
        return _smith_godsword(p, arg)
    parts = arg.split()
    if len(parts) < 2:
        say("Smith what? e.g. 'smith iron platebody'. Items: "
            + ", ".join(SMITH_BARS))
        return
    metal = parts[0]
    item_type = " ".join(parts[1:])
    if metal not in SMITH_METAL_LVL or item_type not in SMITH_BARS:
        say(f"Metals: {', '.join(SMITH_METAL_LVL)}. Items: {', '.join(SMITH_BARS)}")
        return
    nbars = SMITH_BARS[item_type]
    bar = f"{metal} bar"
    base_lvl = SMITH_METAL_LVL[metal]
    req = base_lvl + nbars  # rough scaling
    if p.lvl("smithing") < req:
        say(f"You need smithing level {req} to smith a {metal} {item_type}.")
        return
    if not p.has(bar, nbars):
        say(f"You need {nbars}x {bar}.")
        return
    result = f"{metal} {item_type}"
    if result not in ITEMS:
        say(f"You don't know how to smith a {result}.")
        return
    p.take(bar, nbars)
    p.add(result)
    say(f"You hammer out a {result}.")
    p.gain_xp("smithing", nbars * (12 + base_lvl // 3))


def cmd_spin(p, arg):
    r = ROOMS[p.location]
    if not r.get("spinning_wheel"):
        say("You need a spinning wheel (Lumbridge Castle, Crafting Guild).")
        return
    want = arg.strip().lower()
    # flax -> bow string (Crafting); wool -> ball of wool
    if (want in ("flax", "bow string", "bowstring")) or (not want and p.has("flax")
                                                         and not p.has("wool")):
        if not p.has("flax"):
            say("You have no flax to spin.")
            return
        p.take("flax")
        p.add("bow string")
        say("You spin the flax into a bow string.", "bcyan")
        p.gain_xp("crafting", 15)
        return True
    if not p.has("wool"):
        say("You have no wool (or flax) to spin.")
        return
    p.take("wool")
    p.add("ball of wool")
    say("You spin the wool into a ball of wool.")
    p.gain_xp("crafting", 2.5)
    return True


# hide -> (leather product, coin fee per hide). Extended by later content.
TAN_HIDES = {"cowhide": ("leather", 1)}


def cmd_tan(p, arg):
    r = ROOMS[p.location]
    if not r.get("tanner"):
        say("You need a tanner (Al Kharid, Crafting Guild).")
        return
    want = arg.strip().lower()
    hide = want if want in TAN_HIDES else next((h for h in TAN_HIDES if p.has(h)), None)
    if not hide or not p.has(hide):
        say("You have no hide to tan. Tannable: " + ", ".join(TAN_HIDES))
        return
    leather, fee = TAN_HIDES[hide]
    if not p.has("coins", fee):
        say(f"The tanner charges {fee} coin(s) per {hide}.")
        return
    p.take(hide)
    p.take("coins", fee)
    p.add(leather)
    say(f"The tanner turns your {hide} into {leather}.")
    return True


# product -> (material, qty, crafting level, xp).  Needs a needle + thread.
CRAFT_RECIPES = {
    "leather body": ("leather", 1, 1, 25),
}


def cmd_craft(p, arg):
    name = arg.strip().lower()
    name = {"body": "leather body", "leather": "leather body"}.get(name, name)
    if name == "trident of the swamp":  # magic fang + trident of the seas
        if not (p.has("magic fang") and p.has("trident of the seas")):
            say("The swamp trident takes a magic fang AND a trident of "
                "the seas.")
            return
        if p.lvl("crafting") < 59:
            say("You need crafting level 59 to set the fang.")
            return
        p.take("magic fang")
        p.take("trident of the seas")
        p.add("trident of the swamp")
        p.gain_xp("crafting", 300)
        say("You seat the magic fang in the trident's head — TRIDENT OF "
            "THE SWAMP.", "bgreen", "bold")
        return True
    if name in JEWELLERY:
        return _craft_jewellery(p, name)
    rec = CRAFT_RECIPES.get(name)
    if not rec:
        say("You can craft: " + ", ".join(CRAFT_RECIPES)
            + ". (Also 'spin' wool/flax, 'tan' hides.)")
        say("At a furnace, with a gold bar: " + ", ".join(JEWELLERY)
            + " ('cut' uncut gems with a chisel first).", "grey")
        return
    mat, qty, lvl, xp = rec
    if p.lvl("crafting") < lvl:
        say(f"You need crafting level {lvl} to make {name}.")
        return
    if not p.find_tool("needle"):
        say("You need a needle.")
        return
    if not p.has("thread"):
        say("You need thread.")
        return
    if not p.has(mat, qty):
        say(f"You need {qty}x {mat}.")
        return
    p.take(mat, qty)
    p.take("thread")
    p.add(name)
    say(f"You stitch together {name}.")
    p.gain_xp("crafting", xp)
    return True


def cmd_craftrune(p, _a):
    r = ROOMS[p.location]
    altar = r.get("altar")
    if not altar:
        say("You need a runecrafting altar.")
        return
    rune = altar + " rune"
    if rune not in RUNECRAFT:
        say("You can't craft that rune here.")
        return
    if not p.has("rune essence"):
        say("You need rune essence.")
        return
    req, xp = RUNECRAFT[rune]
    if p.lvl("runecrafting") < req:
        say(f"You need runecrafting level {req}.")
        return
    n = p.count("rune essence")
    p.take("rune essence", n)
    mult = 1 + min(2, max(0, (p.lvl("runecrafting") - req) // 11))
    p.add(rune, n * mult)
    say(f"You bind the essence into {n * mult}x {rune}."
        + (f" (Your mastery draws x{mult} runes from each essence!)"
           if mult > 1 else ""))
    p.gain_xp("runecrafting", xp * n)


# --- eating, magic utility ------------------------------------------------
def cmd_eat(p, arg):
    item = arg.strip().lower()
    foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
    if not item:
        if not foods:
            say("You have no food.")
            return
        item = foods[0]
    if "heal" not in ITEMS.get(item, {}):
        # 'eat trout' should find your cooked trout
        near = [f for f in foods if item in f]
        if near:
            item = near[0]
        else:
            say(f"You can't eat {item}.")
            return
    if p.hp >= p.max_hp:
        say("You're already at full health — save the food.", "grey")
        return
    if not p.has(item):
        say(f"You have no {item}.")
        return
    p.take(item)
    p.hp = min(p.max_hp, p.hp + ITEMS[item]["heal"])
    say(f"You eat the {item}. (HP: {p.hp}/{p.max_hp})")


def _autoeat_bite(p):
    """Reflex-eat when badly hurt in interactive combat ('autoeat' toggles)."""
    if getattr(p, "duel", None) and p.duel["rule"] == "no food":
        return
    foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
    if not foods:
        return
    food = max(foods, key=lambda f: ITEMS[f]["heal"])
    p.take(food)
    p.hp = min(p.max_hp, p.hp + ITEMS[food]["heal"])
    note = ""
    seen = getattr(p, "tips_seen", None)
    if seen is None:
        seen = p.tips_seen = []
    if "autoeat" not in seen:
        seen.append("autoeat")
        note = " 'autoeat off' to disable."
    print("  " + paint(f"(autoeat: you wolf down a {food} — "
                       f"hp {p.hp}/{p.max_hp}.{note})", "lime"))


def cmd_autoeat(p, arg):
    a = arg.strip().lower()
    if a in ("on", "off"):
        p.autoeat = (a == "on")
    elif a:
        say("'autoeat on' or 'autoeat off'.", "grey")
        return
    else:
        p.autoeat = not getattr(p, "autoeat", True)
    say("Autoeat is " + ("ON — you'll reflexively eat when badly hurt in "
                         "combat." if p.autoeat
                         else "OFF — you eat only when you say so."), "bcyan")


# --- Herblore: clean grimy herbs, brew potions, drink them -----------------
def _herblore_gate(p):
    if not getattr(p, "members", False):
        say("Herblore is members-only. Type 'membership' to unlock it.", "bmagenta")
        return False
    return True


def cmd_clean(p, arg):
    if not _herblore_gate(p):
        return
    name = arg.strip().lower()
    grimies = [g for g in HERBS if p.has(g)]
    if not name:
        if not grimies:
            say("You have no grimy herbs to clean. Buy some in Edgeville, or "
                "get them as monster drops.", "grey")
            return
        name = grimies[0]
    if name not in HERBS:                       # accept "clean guam" / "clean ranarr"
        match = [g for g in HERBS if name in g]
        if match:
            name = match[0]
    if name not in HERBS:
        say("That isn't a grimy herb.", "grey")
        return
    if not p.has(name):
        say(f"You have no {name}.", "grey")
        return
    clean, lvl, xp = HERBS[name]
    if p.lvl("herblore") < lvl:
        say(f"You need Herblore level {lvl} to clean {name}.", "byellow")
        return
    p.take(name)
    p.add(clean)
    say(f"You clean the {name} into a {clean}.", "lime")
    p.gain_xp("herblore", xp)
    return True


def cmd_brew(p, arg):
    if not _herblore_gate(p):
        return
    name = arg.strip().lower()
    if not name:
        say("Brew which potion? You know: " + ", ".join(POTIONS), "lime")
        say("Each needs a clean herb + a vial of water + a secondary ingredient.",
            "grey")
        return
    if name not in POTIONS:
        match = [pn for pn in POTIONS if pn.startswith(name)]
        if len(match) == 1:
            name = match[0]
    if name not in POTIONS:
        say("You don't know how to brew that.", "grey")
        return
    rec = POTIONS[name]
    if p.lvl("herblore") < rec["lvl"]:
        say(f"You need Herblore level {rec['lvl']} to brew {name}.", "byellow")
        return
    need = ["vial of water", rec["herb"], rec["second"]]
    missing = [i for i in need if not p.has(i)]
    if missing:
        say("You still need: " + ", ".join(missing), "byellow")
        return
    for i in need:
        p.take(i)
    p.add(name)
    p.potions_made = getattr(p, "potions_made", 0) + 1
    article = "an" if name[:1] in "aeiou" else "a"
    say(f"You mix {article} {name}.", "lime", "bold")
    p.gain_xp("herblore", rec["xp"])


def _boost_amount(p, skill, tier):
    base = p.base_lvl(skill)
    return (5 + int(base * 0.15)) if tier >= 1 else (3 + int(base * 0.10))


def cmd_drink(p, arg):
    name = arg.strip().lower()
    pots = [i for i in p.inventory if ITEMS.get(i, {}).get("potion")]
    if not name:
        if not pots:
            say("You have no potions to drink. Brew some with Herblore.", "grey")
            return
        name = pots[0]
    if name not in POTIONS:
        match = [pn for pn in pots if pn.startswith(name)]
        if len(match) == 1:
            name = match[0]
    if not ITEMS.get(name, {}).get("potion") or not p.has(name):
        say(f"You have no {name} to drink.", "grey")
        return
    kind, target, tier = POTIONS[name]["effect"]
    p.take(name)
    if kind == "boost":
        amt = _boost_amount(p, target, tier)
        p.stat_boost[target] = max(p.stat_boost.get(target, 0), amt)
        say(f"You drink the {name}. Your {target} is boosted by {amt}!",
            "lime", "bold")
    elif kind == "restore" and target == "prayer":
        amt = int(p.prayer_max() * 0.3) + 7
        p.prayer_points = min(p.prayer_max(), p.prayer_points + amt)
        say(f"You drink the {name}. Prayer points: {p.prayer_points}/{p.prayer_max()}.",
            "bwhite", "bold")
    elif kind == "restore" and target == "energy":
        p.run_energy = min(100, getattr(p, "run_energy", 100) + 40)
        say(f"You drink the {name}. Run energy: {int(p.run_energy)}/100.", "lime")
    elif kind == "cure" and target == "poison":
        p.poison = 0
        say(f"You drink the {name}. The poison is neutralised.", "bgreen")


def cmd_cast(p, arg):
    spell = arg.strip().lower()
    if spell not in SPELLS:
        say("Known spells: " + ", ".join(SPELLS))
        return
    s = SPELLS[spell]
    if p.lvl("magic") < s["lvl"]:
        say(f"You need magic level {s['lvl']} to cast {spell}.")
        return
    if s["type"] == "combat":
        cmd_autocast(p, spell)
        return
    if s["type"] == "tele":
        if not _consume_runes(p, s["runes"]):
            say("You don't have the runes.")
            return
        p.location = s["dest"]
        p.gain_xp("magic", s["xp"])
        say(f"You teleport in a flash of light.")
        cmd_look(p, "")
        return
    if s["type"] == "alch":
        # alch the most valuable non-coin, non-rune item
        candidates = [i for i in p.inventory
                      if i not in ("coins",) and "rune" not in i]
        if not candidates:
            say("You have nothing worth alching.")
            return
        target = max(candidates, key=lambda i: ITEMS.get(i, {}).get("value", 0))
        if not _consume_runes(p, s["runes"]):
            say("You don't have the runes.")
            return
        p.take(target)
        gold = int(ITEMS[target]["value"] * s["ratio"])
        p.add("coins", gold)
        say(f"You transmute the {target} into {gold} coins.")
        p.gain_xp("magic", s["xp"])


# --- banking, shops, GE ---------------------------------------------------
def cmd_bank(p, arg=""):
    if not ROOMS[p.location].get("bank"):
        say("There's no bank here. ('goto bank' knows the way.)")
        return
    total = sum(ITEMS.get(i, {}).get("value", 0) * q for i, q in p.bank.items())
    banner(f"Bank of Gielinor — {len(p.bank)} stack(s), worth ~{total:,} gp")
    if not p.bank:
        say("Your bank is empty.")
    else:
        flt = (arg or "").strip().lower()
        items = sorted(p.bank.items(),
                       key=lambda kv: -ITEMS.get(kv[0], {}).get("value", 0)
                       * kv[1])
        shown = [(i, q) for i, q in items if flt in i] if flt else items
        if flt and not shown:
            say(f"  Nothing in the bank matches '{flt}'.", "grey")
        for item, q in shown[:40]:
            worth = ITEMS.get(item, {}).get("value", 0) * q
            print("  " + paint(f"{item} x{q}", item_rarity_color(item))
                  + paint(f"   ({worth:,} gp)" if worth else "", "grey"))
        if len(shown) > 40:
            say(f"  ...and {len(shown) - 40} more — narrow it down with "
                "'bank <name>'.", "grey")
    say("\nUse: deposit <item> [n|all] | withdraw <item> [n|all] | "
        "deposit all | bank <filter>")


def cmd_deposit(p, arg):
    if not ROOMS[p.location].get("bank"):
        say("There's no bank here. ('goto bank' knows the way.)")
        return
    arg = arg.strip().lower()
    if arg in ("all", ""):
        moved = 0
        for item in list(p.inventory):
            q = p.inventory[item]
            p.bank[item] = p.bank.get(item, 0) + q
            del p.inventory[item]
            moved += 1
        say(f"You deposit everything ({moved} stacks).")
        return
    parts = arg.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].isdigit() or parts[1] == "all"):
        item, qarg = parts
    else:
        item, qarg = arg, "all"
    if not p.has(item):
        found = _resolve_named(item, p.inventory)   # 'deposit trout' works
        if found is _ASKED:
            return
        if not found:
            say(f"You have no {item}.")
            return
        item = found
    q = p.count(item) if qarg == "all" else min(int(qarg), p.count(item))
    p.take(item, q)
    p.bank[item] = p.bank.get(item, 0) + q
    say(f"Deposited {item} x{q}.")


def cmd_withdraw(p, arg):
    if not ROOMS[p.location].get("bank"):
        say("There's no bank here. ('goto bank' knows the way.)")
        return
    arg = arg.strip().lower()
    parts = arg.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].isdigit() or parts[1] == "all"):
        item, qarg = parts
    else:
        item, qarg = arg, "1"
    if p.bank.get(item, 0) <= 0:
        found = _resolve_named(item, p.bank)    # 'withdraw trout' works
        if found is _ASKED:
            return
        if not found:
            say(f"You have no {item} in the bank.")
            return
        item = found
    q = p.bank[item] if qarg == "all" else min(int(qarg), p.bank[item])
    p.bank[item] -= q
    if p.bank[item] <= 0:
        del p.bank[item]
    p.add(item, q)
    say(f"Withdrew {item} x{q}.")


def cmd_shop(p, _a):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here. ('goto shop' finds the nearest.)")
        return
    banner(f"Shop — {shop}")
    print("  " + paint(f"Your coins: {p.coins:,}", "gold")
          + paint("   (shops pay 40% of value when you sell)", "grey"))
    for item, price in SHOPS[shop].items():
        affordable = "bwhite" if p.coins >= price else "grey"
        print("  " + paint(f"{item:22}", affordable)
              + paint(f"{price:,} coins", "gold" if p.coins >= price
                      else "grey"))
    say("\nUse: buy <item> [n] | sell <item> [n]")


def _parse_item_qty(arg):
    parts = arg.strip().lower().rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return arg.strip().lower(), 1


_ASKED = object()       # sentinel: _resolve_named already asked "which one?"


def _resolve_named(name, pool):
    """Resolve a (possibly partial) item name against a pool of names, the
    way 'eat trout' finds cooked trout. Returns the resolved name, None
    (nothing close — the caller prints its own refusal), or _ASKED (it was
    ambiguous and we listed the choices, so the caller should just stop)."""
    if not name or name in pool:
        return name if name in pool else None
    near = sorted(i for i in pool if name in i)
    if len(near) == 1:
        return near[0]
    if near:
        say("Which one? " + ", ".join(near[:8])
            + (" …" if len(near) > 8 else ""), "grey")
        return _ASKED
    return None


def cmd_drop(p, arg):
    a = arg.strip().lower()
    if not a:
        say("Drop what? ('drop <item> [n|all]')")
        return
    parts = a.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].isdigit() or parts[1] == "all"):
        item, qarg = parts
    else:
        item, qarg = a, "1"
    if not p.has(item):
        found = _resolve_named(item, p.inventory)   # 'drop beef' works
        if found is _ASKED:
            return
        if not found:
            say(f"You have no {item}.")
            return
        item = found
    q = p.count(item) if qarg == "all" else min(int(qarg), p.count(item))
    p.take(item, q)
    say(f"You drop {item} x{q}." + (" A seagull swoops in to inspect it."
        if "karamja" in p.location or "sarim" in p.location else ""))


def cmd_buy(p, arg):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here. ('goto shop' finds the nearest.)")
        return
    item, qty = _parse_item_qty(arg)
    if item not in SHOPS[shop]:
        found = _resolve_named(item, SHOPS[shop])   # 'buy scim' works
        if found is _ASKED:
            return
        if not found:
            say("The shopkeeper doesn't sell that. ('shop' lists the stock.)")
            return
        item = found
    cost = SHOPS[shop][item] * qty
    if not p.has("coins", cost):
        say(f"That costs {cost:,} coins; you can't afford it. "
            f"(You have {p.coins:,}.)")
        return
    p.take("coins", cost)
    p.add(item, qty)
    say(f"You buy {item} x{qty} for {cost:,} coins.")


def cmd_sell(p, arg):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here. ('goto shop' finds the nearest.)")
        return
    item, qty = _parse_item_qty(arg)
    if item not in p.inventory:
        found = _resolve_named(item, p.inventory)   # 'sell beef' works
        if found is _ASKED:
            return
        if found:
            item = found
    if not p.has(item, qty):
        say(f"You don't have {qty}x {item}.")
        return
    price = max(1, int(ITEMS.get(item, {}).get("value", 1) * 0.4)) * qty
    p.take(item, qty)
    p.add("coins", price)
    say(f"You sell {item} x{qty} for {price:,} coins.")


def cmd_ge(p, arg):
    if not ROOMS[p.location].get("ge"):
        say("You must be at the Grand Exchange. ('goto ge' knows the way; "
            "it's north of Varrock.)")
        return
    arg = arg.strip().lower()
    if not arg:
        banner("Grand Exchange")
        say("Trade almost any item at its market value.")
        say("Use: ge buy <item> [n]  |  ge sell <item> [n]")
        say("(Prices are the item's value; sell returns full value here.)")
        return
    action, rest = (arg.split(" ", 1) + [""])[:2]
    item, qty = _parse_item_qty(rest)
    if item not in ITEMS:
        # selling matches what you carry first; buying matches the catalogue
        pool = p.inventory if action == "sell" else ITEMS
        found = _resolve_named(item, pool)
        if found is _ASKED:
            return
        if not found:
            close = difflib.get_close_matches(item, list(ITEMS), 1, 0.75)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            say(f"No such item: {item}.{hint}")
            return
        item = found
    price = ITEMS[item]["value"] * qty
    if action == "buy":
        if not p.has("coins", price):
            say(f"That costs {price:,} coins; you can't afford it. "
                f"(You have {p.coins:,}.)")
            return
        p.take("coins", price)
        p.add(item, qty)
        say(f"Bought {item} x{qty} for {price:,} coins.")
    elif action == "sell":
        if not p.has(item, qty):
            say(f"You don't have {qty}x {item}.")
            return
        p.take(item, qty)
        p.add("coins", price)
        say(f"Sold {item} x{qty} for {price:,} coins.")
    else:
        say("Use: ge buy <item> [n] | ge sell <item> [n]")


# --- combat & farm actions ------------------------------------------------
def _handle_death(p):
    if getattr(p, "god", False):        # [dev] god mode refuses death
        p.hp = p.max_hp
        say("[dev] God mode shrugs off the killing blow.", "bmagenta",
            "bold")
        return
    _clear_status(p)
    show_art(ART_DEATH, "bred")
    banner("YOU HAVE DIED", color="bred", line_color="red")
    say("You wake in Lumbridge, your wounds bound. Your items are safe.", "grey")
    if getattr(p, "cave_wave", 0):
        p.cave_wave = 0
        say("Your Fight Caves run is over.", "byellow")
    if getattr(p, "inferno_wave", 0):
        p.inferno_wave = 0
        say("Your Inferno run ends in the flames.", "byellow")
    p.hp = p.max_hp
    p.location = "lumbridge_castle"


def _start_auto(p, target, count):
    """Engage the autopilot: the game fights for you, one kill at a time.
    In the browser each kill lands on a timer; in a terminal it's paced
    with real seconds. Any command breaks it off."""
    rank = MONSTERS[target].get("rank", "medium")
    p.auto = {"target": target, "count": count, "done": 0,
              "xp": {}, "loot": {}}
    banner(f"Auto-fight: {target} \u00d7{count}", color="gold", line_color="brown")
    print("  " + paint(f"rank: {rank}", RANK_COLOR.get(rank, "white"))
          + paint("   (the game fights for you \u2014 type anything to break "
                  "off)", "grey"))
    if WEB:
        _auto_step(p)          # first kill now; the browser paces the rest
        return
    try:                       # terminal: live pacing with real seconds
        while getattr(p, "auto", None):
            _auto_step(p)
            if getattr(p, "auto", None) and sys.stdout.isatty():
                time.sleep(0.6)
    except KeyboardInterrupt:
        p.auto = None
        say("\n  You break off the auto-fight.", "byellow")


def _auto_step(p):
    """One autopilot kill. Clears p.auto when the run ends."""
    a = getattr(p, "auto", None)
    if not a:
        return
    target, count = a["target"], a["count"]
    if p.hp <= p.max_hp * 0.4:
        # eat from the pack like a real grinder; retreat only when it's empty
        ate = {}
        while p.hp < p.max_hp * 0.7:
            food = next((i for i in p.inventory
                         if "heal" in ITEMS.get(i, {})), None)
            if not food:
                break
            p.take(food)
            p.hp = min(p.max_hp, p.hp + ITEMS[food]["heal"])
            ate[food] = ate.get(food, 0) + 1
        if ate:
            menu = ", ".join(f"{n}x {f}" for f, n in ate.items())
            print("  " + paint(f"(You pause to eat {menu} — "
                               f"hp {p.hp}/{p.max_hp}.)", "lime"))
    if p.hp <= p.max_hp * 0.4 and a["done"] > 0:
        _auto_finish(p, "retreat")
        return
    before_xp = {s: p.skills[s] for s in SKILLS}
    before_inv = {i: q for i, q in p.inventory.items()}
    before_lvls = {s: p.lvl(s) for s in SKILLS}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = fight_auto(p, target)
        if res == "won":
            _quest_on_kill(p, target)
    if res == "died":
        _auto_finish(p, "died")
        return
    if res in ("noattack", "fled"):
        print(buf.getvalue().strip()[-200:] if res == "noattack" else "",
              end="")
        _auto_finish(p, "stopped")
        return
    a["done"] += 1
    n = a["done"]
    gained = {s: p.skills[s] - before_xp[s] for s in SKILLS}
    gx = int(sum(gained.values()))
    ups = [s for s in SKILLS if p.lvl(s) > before_lvls[s]]
    loot = {i: p.count(i) - before_inv.get(i, 0) for i in p.inventory
            if p.count(i) - before_inv.get(i, 0) > 0}
    for s, v in gained.items():
        if v:
            a["xp"][s] = a["xp"].get(s, 0) + v
    for i, v in loot.items():
        a["loot"][i] = a["loot"].get(i, 0) + v
    loot_str = ", ".join(f"{i} x{v}" for i, v in loot.items()) or "no loot"
    hp_col = "bgreen" if p.hp > p.max_hp * 0.5 else \
        ("byellow" if p.hp > p.max_hp * 0.3 else "bred")
    print(f"  [{n}/{count}] slew the {target}  "
          + paint(f"+{gx} xp", "bcyan") + "  " + paint(loot_str, "byellow")
          + "  " + paint(f"HP {max(p.hp,0)}/{p.max_hp}", hp_col))
    if ups:
        print("       " + paint("LEVEL UP: "
              + ", ".join(f"{s} {p.lvl(s)}" for s in ups), "byellow", "bold"))
    if n >= count:
        _auto_finish(p, "done")
    elif p.hp <= p.max_hp * 0.3:
        _auto_finish(p, "retreat")


def _auto_finish(p, outcome):
    """Close out an autopilot run with the totals."""
    a = getattr(p, "auto", None)
    p.auto = None
    if not a:
        return
    print()
    print(paint(f"  Defeated {a['done']} {a['target']}(s).", "bgreen", "bold")
          + paint(f"    HP {max(p.hp,0)}/{p.max_hp}", "white"))
    if a["xp"]:
        print("  " + paint("Total XP: ", "bcyan")
              + ", ".join(f"{s} +{int(v)}" for s, v in a["xp"].items()))
    if a["loot"]:
        print("  " + paint("Total loot: ", "byellow")
              + ", ".join(f"{i} x{v}" for i, v in sorted(a["loot"].items())))
    if outcome == "retreat":
        say("  You break off, badly wounded \u2014 rest or heal before "
            "continuing.", "byellow")
    elif outcome == "stopped":
        say("  The auto-fight stopped.", "grey")
    elif outcome == "died":
        say(f"  You were slain after {a['done']} kill(s).", "bred")
        _handle_death(p)


def cmd_fight(p, arg):
    monsters = _room_monsters(p)
    if not monsters:
        say("There's nothing to fight here.")
        return
    # parse: 'auto'/number/'all' triggers auto mode; rest is the monster name
    count = 1
    auto = False
    words = []
    for t in arg.strip().lower().split():
        if t == "auto":
            auto = True
        elif t == "all":
            auto = True
            count = 999
        elif t.isdigit():
            auto = True
            count = int(t)
        else:
            words.append(t)
    target = " ".join(words) or monsters[0]
    if target not in monsters:
        # 'fight rex' should find dagannoth rex — unique substring match
        near = [m for m in monsters if target in m]
        if len(near) == 1:
            target = near[0]
        elif len(near) > 1:
            say(f"Which one? {', '.join(near)}")
            return
        else:
            say(f"No {target} here. Monsters: {', '.join(monsters)}")
            return
    sreq = MONSTERS[target].get("slayer_req", 0)
    if sreq and p.lvl("slayer") < sreq:
        say(f"You need slayer level {sreq} to know how to harm a {target}.",
            "byellow")
        return

    rank = MONSTERS[target].get("rank", "medium")
    if MONSTERS[target].get("boss"):
        if auto:
            say(f"The {target} is a BOSS — bosses can't be auto-fought. "
                "Face it yourself!", "bmagenta")
        return _start_combat(p, target)       # bosses are always interactive

    if not auto:
        return _start_combat(p, target)       # interactive turn-based

    cap = RANK_CAP.get(rank, 20)
    if count > cap:
        say(f"Auto-fight is capped at {cap} for {rank}-rank monsters.", "grey")
    count = clamp(count, 1, cap)
    _start_auto(p, target, count)


def cmd_collect(p, _a):
    if p.location != "lumbridge_farm":
        say("There are no eggs here.")
        return
    p.add("egg")
    say("You take a fresh egg from the chicken coop.")


def cmd_milk(p, _a):
    if p.location not in ("lumbridge_farm",):
        say("There's no cow to milk here.")
        return
    if not p.has("bucket"):
        say("You need an empty bucket.")
        return
    p.take("bucket")
    p.add("bucket of milk")
    say("You milk the cow, filling your bucket.")


def cmd_pick(p, arg):
    picks = ROOMS[p.location].get("pick", [])
    if not picks:
        say("There's nothing to pick here.")
        return
    want = arg.strip().lower()
    item = next((i for i in picks if want and want in i), None if want else
                picks[0])
    if not item:
        say(f"No {want} to pick here. You can pick: {', '.join(picks)}")
        return
    p.add(item)
    say("You pick some wheat, gathering grain." if item == "grain"
        else f"You pick some {item}.")
    return True


def cmd_mill(p, _a):
    if p.location != "windmill":
        say("You need a windmill.")
        return
    if not p.has("grain"):
        say("You have no grain.")
        return
    if not p.has("pot"):
        say("You need an empty pot to catch the flour.")
        return
    p.take("grain")
    p.take("pot")
    p.add("pot of flour")
    say("You grind the grain into a pot of flour.")


def cmd_shear(p, _a):
    if p.location not in ("lumbridge_farm", "cow_field"):
        say("There are no sheep here.")
        return
    if not p.find_tool("shears"):
        say("You need shears.")
        return
    p.add("wool")
    say("You shear a sheep and collect some wool.")


