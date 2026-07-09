# ===========================================================================
#  FARMING  (the 21st skill — crops grow on the action clock while you play)
# ===========================================================================
# 'plant <seed>' at a patch, adventure elsewhere, come back and 'harvest'.
# 'farm' shows every patch you own, anywhere in the world.

# seed -> (patch type, level, actions to grow, product, min, max, xp/harvest)
SEEDS = {
    "potato seed": ("allotment", 1, 30, "potato", 3, 6, 9),
    "onion seed": ("allotment", 5, 35, "onion", 3, 6, 11),
    "cabbage seed": ("allotment", 7, 40, "cabbage", 3, 6, 12),
    "sweetcorn seed": ("allotment", 20, 50, "sweetcorn", 3, 6, 19),
    "watermelon seed": ("allotment", 47, 70, "watermelon", 3, 5, 49),
    "guam seed": ("herb", 9, 45, "grimy guam", 3, 5, 13),
    "marrentill seed": ("herb", 14, 50, "grimy marrentill", 3, 5, 15),
    "tarromin seed": ("herb", 19, 55, "grimy tarromin", 3, 5, 18),
    "ranarr seed": ("herb", 32, 65, "grimy ranarr", 3, 5, 31),
}
for _s in SEEDS:
    add_item(_s, 40 if "ranarr" in _s else 4)
add_item("potato", 3, heal=2)
add_item("onion", 3, heal=1)
add_item("sweetcorn", 10, heal=3)
add_item("watermelon", 30, heal=5)

SHOPS["farming"] = {"potato seed": 4, "onion seed": 6, "cabbage seed": 8,
                    "sweetcorn seed": 25, "guam seed": 10,
                    "marrentill seed": 16, "tarromin seed": 24}

ROOMS["falador_park"]["patches"] = ["allotment", "herb"]
ROOMS["falador_park"]["shop"] = "farming"
ROOMS["falador_park"]["desc"] += (" A gardener tends tilled farming patches "
                                  "and sells seeds.")
ROOMS["lumbridge_farm"]["patches"] = ["allotment"]
ROOMS["lumbridge_farm"]["desc"] += " A tilled allotment patch waits for seeds."
ROOMS["catherby"]["patches"] = ["allotment", "herb"]
ROOMS["catherby"]["desc"] += " Farming patches line the shore road."
ROOMS["ardougne"]["patches"] = ["allotment", "herb"]
ROOMS["ardougne"]["desc"] += " Tilled patches sit north of the market."
ROOMS["canifis"]["patches"] = ["herb"]
ROOMS["canifis"]["desc"] += " A dark-soiled herb patch grows strangely well."

# the Draynor seed stall feeds thieving into farming
STALLS["seed stall"] = (27, 10, [("potato seed", 0.25), ("onion seed", 0.2),
                                 ("cabbage seed", 0.15),
                                 ("guam seed", 0.15),
                                 ("marrentill seed", 0.1),
                                 ("tarromin seed", 0.08),
                                 ("sweetcorn seed", 0.04),
                                 ("ranarr seed", 0.02),
                                 ("watermelon seed", 0.01)])
ROOMS["draynor_village"]["stalls"] = ["seed stall"]
ROOMS["draynor_village"]["desc"] += " A seed stall stands in the market."


def _patch_state(p, crop):
    """(ready?, actions left) for a planted crop."""
    grow = SEEDS[crop["seed"]][2]
    elapsed = getattr(p, "actions", 0) - crop["at"]
    return elapsed >= grow, max(0, grow - elapsed)


def _farm_gate(p):
    if not getattr(p, "members", False):
        say("Farming is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return False
    return True


def cmd_plant(p, arg):
    if not _farm_gate(p):
        return
    patches = ROOMS[p.location].get("patches", [])
    if not patches:
        say("There's no farming patch here. (Lumbridge farm, Falador Park, "
            "Catherby, Ardougne, Canifis)", "grey")
        return
    want = arg.strip().lower()
    if want and not want.endswith(" seed"):
        want += " seed"
    seed = want if want in SEEDS else \
        next((s for s in SEEDS if want and want in s), None) if want else \
        next((s for s in SEEDS if p.has(s)
              and SEEDS[s][0] in patches), None)
    if not seed:
        have = [s for s in SEEDS if p.has(s)]
        say("Plant what? You have: " + (", ".join(have) if have else
            "no seeds (seed stall in Draynor, farming shop in Falador Park, "
            "or monster drops)."), "bcyan")
        return
    ptype, lvl, grow, product, lo, hi, xp = SEEDS[seed]
    if ptype not in patches:
        say(f"No {ptype} patch here for {seed}.", "byellow")
        return
    pid = f"{p.location}:{ptype}"
    crop = getattr(p, "farm", {}).get(pid)
    if crop:
        ready, left = _patch_state(p, crop)
        say(f"The {ptype} patch already grows {crop['seed'].replace(' seed', '')}"
            + (" — it's READY ('harvest')." if ready
               else f" (~{left} actions to go)."), "byellow")
        return
    if p.lvl("farming") < lvl:
        say(f"You need farming level {lvl} to plant {seed}.", "byellow")
        return
    if not p.has(seed):
        say(f"You have no {seed}.", "byellow")
        return
    p.take(seed)
    p.farm[pid] = {"seed": seed, "at": getattr(p, "actions", 0)}
    say(f"You sow the {seed} into the {ptype} patch. It will be ready in "
        f"about {grow} actions — go adventure and come back!", "green")
    p.gain_xp("farming", max(4, xp // 2))
    return True


def cmd_harvest(p, arg):
    if not _farm_gate(p):
        return
    patches = ROOMS[p.location].get("patches", [])
    if not patches:
        say("There's no farming patch here.", "grey")
        return
    want = arg.strip().lower()
    grown = [(t, getattr(p, "farm", {}).get(f"{p.location}:{t}"))
             for t in patches]
    grown = [(t, c) for t, c in grown if c and (not want or want in t)]
    if not grown:
        say("Nothing is planted here." if not want else
            f"Nothing growing in a '{want}' patch here.", "grey")
        return
    harvested = False
    for ptype, crop in grown:
        ready, left = _patch_state(p, crop)
        name = crop["seed"].replace(" seed", "")
        if not ready:
            say(f"The {name} isn't ready — about {left} actions to go.",
                "byellow")
            continue
        _t, _l, _g, product, lo, hi, xp = SEEDS[crop["seed"]]
        qty = random.randint(lo, hi)
        p.add(product, qty)
        del p.farm[f"{p.location}:{ptype}"]
        p.crops = getattr(p, "crops", 0) + qty
        say(f"You harvest {qty}x {product} from the {ptype} patch!", "bgreen")
        p.gain_xp("farming", xp * qty)
        harvested = True
    return True if harvested else None


def cmd_farm(p, _a):
    if not _farm_gate(p):
        return
    banner("Your Patches", color="green", line_color="green")
    farm = getattr(p, "farm", {})
    if not farm:
        say("  Nothing planted anywhere. Patches: Lumbridge farm, Falador "
            "Park, Catherby, Ardougne, Canifis. Get seeds from the Draynor "
            "seed stall, the Falador Park shop, or drops.", "grey")
        return
    for pid, crop in sorted(farm.items()):
        room, ptype = pid.split(":")
        ready, left = _patch_state(p, crop)
        name = crop["seed"].replace(" seed", "")
        state = paint("READY — go 'harvest'!", "bgreen", "bold") if ready \
            else paint(f"~{left} actions to go", "byellow")
        print("  " + paint(f"{ROOMS[room]['name']:22}", "white")
              + paint(f"{ptype:10}", "grey")
              + paint(f"{name:12}", "green") + state)
    say(f"  Lifetime crops harvested: {getattr(p, 'crops', 0)}", "grey")


HANDLERS["plant"] = cmd_plant
HANDLERS["sow"] = cmd_plant
HANDLERS["harvest"] = cmd_harvest
HANDLERS["farm"] = cmd_farm
HANDLERS["patches"] = cmd_farm

# a few growers drop seeds now
for _mob, _seed, _ch in [("goblin", "potato seed", 0.15),
                         ("goblin", "cabbage seed", 0.08),
                         ("barbarian", "guam seed", 0.10),
                         ("hobgoblin", "marrentill seed", 0.10),
                         ("guard", "tarromin seed", 0.08),
                         ("moss giant", "ranarr seed", 0.05),
                         ("chaos druid", "ranarr seed", 0.06),
                         ("hill giant", "guam seed", 0.10),
                         ("ice giant", "watermelon seed", 0.05)]:
    if _mob in MONSTERS:
        MONSTERS[_mob]["drops"].append((_seed, 1, 2, _ch))


# ===========================================================================
#  CONSTRUCTION  (the 22nd skill — a house of your own outside Rimmington)
# ===========================================================================
# Saw logs into planks at the Varrock sawmill, claim your house ('go house'
# from Rimmington), and 'build' furniture with real perks — up to a portal
# chamber that teleports you home from anywhere.

add_item("plank", 30)
add_item("oak plank", 120)

# furniture -> (construction level, {materials}, xp, perk blurb)
FURNITURE = {
    "crude chair": (1, {"plank": 2}, 58,
                    "somewhere to sit. It's a start."),
    "oak bed": (10, {"oak plank": 3}, 90,
                "'rest' at home restores EVERYTHING — prayers included"),
    "workbench": (20, {"oak plank": 4}, 120,
                  "works as an anvil — 'smith' at home"),
    "kitchen range": (25, {"plank": 4, "steel bar": 1}, 140,
                      "'cook' at home"),
    "chapel altar": (45, {"oak plank": 6, "gold bar": 1}, 240,
                     "'pray altar' at home restores prayer points"),
    "portal chamber": (65, {"oak plank": 8, "law rune": 20}, 400,
                       "'home' teleports you here from anywhere"),
}

ROOMS.update({
    "sawmill": dict(name="Varrock Sawmill",
        desc="A creaking mill north of the Grand Exchange. The operator "
             "saws logs into planks for a fee. ('saw logs [n]' — plain 25gp, "
             "oak 60gp)",
        exits={"south": "grand_exchange"}),
    "your_house": dict(name="Your House",
        desc="Your own plot on the edge of Rimmington. What it becomes is "
             "up to you. ('build' to see what you can add)",
        exits={"out": "rimmington"}),
})
ROOMS["grand_exchange"]["exits"]["mill"] = "sawmill"
ROOMS["grand_exchange"]["desc"] += " A sawmill creaks to the north ('mill')."
ROOMS["rimmington"]["exits"]["house"] = "your_house"
ROOMS["rimmington"]["desc"] += " Your house plot sits west of the village ('house')."
REGIONS.update({"sawmill": "Varrock", "your_house": "Rimmington"})

_SAW = {"logs": ("plank", 25), "oak logs": ("oak plank", 60)}


def cmd_saw(p, arg):
    if p.location != "sawmill":
        say("You need the sawmill, north of the Grand Exchange.", "grey")
        return
    want = arg.strip().lower() or next((l for l in _SAW if p.has(l)), "logs")
    logs = want if want in _SAW else want + " logs" \
        if want + " logs" in _SAW else None
    if not logs:
        say("The sawmill takes: " + ", ".join(_SAW), "grey")
        return
    plank, fee = _SAW[logs]
    if not p.has(logs):
        say(f"You have no {logs}.", "byellow")
        return
    if not p.has("coins", fee):
        say(f"The operator charges {fee} coins per {plank}.", "byellow")
        return
    p.take(logs)
    p.take("coins", fee)
    p.add(plank)
    say(f"The saw screams through the {logs} — one {plank}. (-{fee} coins)")
    return True


def cmd_build(p, arg):
    if not getattr(p, "members", False):
        say("Construction is a members skill. Type 'membership' to unlock "
            "it.", "bmagenta")
        return
    if p.location != "your_house":
        say("You can only build in your own house ('go house' from "
            "Rimmington).", "grey")
        return
    want = arg.strip().lower()
    if not want:
        banner("Your House — Construction", color="brown", line_color="brown")
        for name, (lvl, mats, xp, perk) in FURNITURE.items():
            built = name in p.house
            mark = paint("✓ built", "bgreen") if built else \
                paint(f"lvl {lvl}: " + ", ".join(f"{q}x {m}"
                      for m, q in mats.items()), "grey")
            print("  " + paint(f"{name:16}", "bwhite" if not built else "grey")
                  + mark + "  " + paint(perk, "bcyan"))
        say("  'build <furniture>' — you'll need a hammer. Planks come from "
            "the Varrock sawmill.", "grey")
        return
    name = next((f for f in FURNITURE if want in f), None)
    if not name:
        say("You can't build that. ('build' lists your options.)", "grey")
        return
    if name in p.house:
        say(f"Your {name} is already built.", "grey")
        return
    lvl, mats, xp, perk = FURNITURE[name]
    if p.lvl("construction") < lvl:
        say(f"You need construction level {lvl} for a {name}.", "byellow")
        return
    if not p.find_tool("hammer"):
        say("You need a hammer.", "byellow")
        return
    missing = [f"{q}x {m}" for m, q in mats.items() if not p.has(m, q)]
    if missing:
        say("You still need: " + ", ".join(missing) + ".", "byellow")
        return
    for m, q in mats.items():
        p.take(m, q)
    p.house.append(name)
    banner(f"Built: {name}", color="brown", line_color="brown")
    say(f"You hammer the {name} together. ({perk})", "bgreen")
    p.gain_xp("construction", xp)
    return True


def cmd_home(p, _a):
    if "portal chamber" not in getattr(p, "house", []):
        say("You have no portal chamber. (Build one in your house — "
            "construction 65.)", "grey")
        return
    if p.location == "your_house":
        say("You're already home.", "grey")
        return
    say("The portal hums and folds the world around you — you step out "
        "into your own house.", "bmagenta")
    p.location = "your_house"
    cmd_look(p, "")


HANDLERS["saw"] = cmd_saw
HANDLERS["build"] = cmd_build
HANDLERS["home"] = cmd_home
BATCHABLE.add("saw")

# ===========================================================================
#  HUNTER  (the 23rd skill — traps spring on the action clock)
# ===========================================================================
# Buy traps at the Feldip Hunting Grounds south of Ardougne, 'settrap' for a
# creature, adventure a while, and 'check' your traps. More levels = more
# simultaneous traps.

# creature -> (trap item, level, actions to spring, catch xp, {loot: qty})
HUNT = {
    "crimson swift": ("bird snare", 1, 12, 34,
                      {"raw bird meat": 1, "feather": 8}),
    "copper longtail": ("bird snare", 9, 12, 61,
                        {"raw bird meat": 1, "feather": 12}),
    "barb-tailed kebbit": ("box trap", 33, 16, 168, {"kebbit spike": 2}),
    "grey chinchompa": ("box trap", 53, 18, 198, {"chinchompa": 1}),
    "red chinchompa": ("box trap", 63, 20, 265, {"red chinchompa": 1}),
}
add_item("bird snare", 6)
add_item("box trap", 38)
add_item("raw bird meat", 4)
RAW_TO_COOKED["raw bird meat"] = ("cooked bird meat", "burnt chicken", 1)
COOK_XP["raw bird meat"] = 30
add_item("cooked bird meat", 8, heal=4)
add_item("kebbit spike", 250)
add_item("chinchompa", 700)
add_item("red chinchompa", 1500)

SHOPS["hunter"] = {"bird snare": 6, "box trap": 38}

ROOMS.update({
    "feldip_hills": dict(name="Feldip Hunting Grounds",
        desc="Rolling scrubland south of Ardougne, alive with darting birds "
             "and chinchompas. A grizzled tracker sells traps. "
             "('settrap <creature>', then 'check' later)",
        exits={"north": "ardougne"}, shop="hunter", members=True),
})
ROOMS["ardougne"]["exits"]["south"] = "feldip_hills"
ROOMS["ardougne"]["desc"] += " Hunting grounds stretch to the south."
REGIONS["feldip_hills"] = "Kandarin"


def _trap_slots(p):
    return 1 + p.lvl("hunter") // 20      # 1 at lvl 1 -> 5 at 80+


def _hunter_gate(p):
    if not getattr(p, "members", False):
        say("Hunter is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return False
    return True


def cmd_settrap(p, arg):
    if not _hunter_gate(p):
        return
    if p.location != "feldip_hills":
        say("The hunting grounds are south of Ardougne.", "grey")
        return
    want = arg.strip().lower()
    creature = next((c for c in HUNT if want and want in c), None)
    if not creature:
        say("Trap what? " + "; ".join(
            f"{c} (lvl {v[1]}, {v[0]})" for c, v in HUNT.items()), "bcyan")
        return
    trap, lvl, spring, xp, loot = HUNT[creature]
    if p.lvl("hunter") < lvl:
        say(f"You need hunter level {lvl} for {creature}s.", "byellow")
        return
    if not p.has(trap):
        say(f"You need a {trap} (sold here).", "byellow")
        return
    traps = getattr(p, "traps", {})
    if len(traps) >= _trap_slots(p):
        say(f"You can only manage {_trap_slots(p)} trap(s) at your level — "
            "'check' the ones you have.", "byellow")
        return
    p.take(trap)
    slot = str(max([int(k) for k in traps] + [0]) + 1)
    traps[slot] = {"creature": creature, "at": getattr(p, "actions", 0)}
    p.traps = traps
    say(f"You set the {trap} for a {creature}. Give it ~{spring} actions, "
        "then 'check'.", "orange")
    p.gain_xp("hunter", max(3, xp // 8))
    return True


def cmd_checktraps(p, _a):
    if not _hunter_gate(p):
        return
    traps = getattr(p, "traps", {})
    if not traps:
        say("You have no traps set. ('settrap' at the Feldip Hunting "
            "Grounds)", "grey")
        return
    if p.location != "feldip_hills":
        say(f"Your {len(traps)} trap(s) are at the Feldip Hunting Grounds — "
            "go there to 'check' them.", "grey")
        return
    for slot in sorted(traps, key=int):
        info = traps[slot]
        creature = info["creature"]
        trap, lvl, spring, xp, loot = HUNT[creature]
        elapsed = getattr(p, "actions", 0) - info["at"]
        if elapsed < spring:
            say(f"  The {trap} for the {creature} hasn't sprung yet "
                f"(~{spring - elapsed} actions).", "byellow")
            continue
        del traps[slot]
        chance = clamp(0.45 + (p.lvl("hunter") - lvl) * 0.015, 0.45, 0.95)
        if random.random() < chance:
            got = ", ".join(f"{q}x {i}" for i, q in loot.items())
            for i, q in loot.items():
                p.add(i, q)
            p.add(trap)                       # trap recovered
            say(f"  Caught a {creature}! ({got})", "bgreen")
            p.gain_xp("hunter", xp)
        else:
            p.add(trap)
            say(f"  The {creature} sprang the trap and escaped. You reset "
                "the pieces.", "grey")
    return True


HANDLERS["settrap"] = cmd_settrap
HANDLERS["trap"] = cmd_settrap
HANDLERS["check"] = cmd_checktraps
HANDLERS["checktraps"] = cmd_checktraps
HANDLERS["traps"] = cmd_checktraps


