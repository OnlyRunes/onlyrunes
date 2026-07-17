# ===========================================================================
#  SAVE / LOAD
# ===========================================================================
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")


def serialize(p):
    """Return a plain-dict snapshot of a player (for file or browser saves)."""
    return {"v": 1,     # save-format version, for future migrations
            "name": p.name, "location": p.location, "skills": p.skills,
            "hp": p.hp, "inventory": p.inventory, "bank": p.bank,
            "equipment": p.equipment, "style": p.style,
            "train": getattr(p, "train", "shared"),
            "attack_type": getattr(p, "attack_type", "slash"), "autocast": p.autocast,
            "spellbook": getattr(p, "spellbook", "standard"),
            "quests": p.quests, "members": p.members,
            "prayer_points": p.prayer_points, "equipped_prayers": p.active_prayers,
            "run_energy": p.run_energy, "spec_energy": getattr(p, "spec_energy", 100),
            "cave_wave": getattr(p, "cave_wave", 0),
            "inferno_wave": getattr(p, "inferno_wave", 0),
            "barrows": list(getattr(p, "barrows", [])),
            "barrows_loots": getattr(p, "barrows_loots", 0),
            "actions": getattr(p, "actions", 0),
            "farm": dict(getattr(p, "farm", {})),
            "crops": getattr(p, "crops", 0),
            "house": list(getattr(p, "house", [])),
            "traps": dict(getattr(p, "traps", {})),
            "gwd_kc": dict(getattr(p, "gwd_kc", {})),
            "task_streak": getattr(p, "task_streak", 0),
            "slayer_task": p.slayer_task,
            "slayer_points": p.slayer_points,
            "achievements": list(getattr(p, "achievements", [])),
            "kills": getattr(p, "kills", 0),
            "kill_log": dict(getattr(p, "kill_log", {})),
            "bosses": list(getattr(p, "bosses", [])),
            "potions_made": getattr(p, "potions_made", 0),
            "tips_seen": list(getattr(p, "tips_seen", [])),
            "seen": sorted(getattr(p, "seen", [])),
            "autoeat": getattr(p, "autoeat", True),
            "kingdom": getattr(p, "kingdom", None)}


def deserialize(data):
    """Rebuild a Player from a snapshot dict."""
    p = Player(data["name"])
    p.location = data["location"]
    p.skills = {s: data["skills"].get(s, p.skills[s]) for s in SKILLS}
    p.hp = data["hp"]
    p.inventory = data["inventory"]
    p.bank = data.get("bank", {})
    eq = {slot: None for slot in EQUIP_SLOTS}
    eq.update(data.get("equipment", {}))
    p.equipment = eq
    p.style = data.get("style", "melee")
    p.train = data.get("train", "shared")
    p.attack_type = data.get("attack_type", "slash")
    p.autocast = data.get("autocast", "wind strike")
    p.quests = data.get("quests", {})
    p.members = data.get("members", False)
    p.prayer_points = data.get("prayer_points", 1)
    p.active_prayers = data.get("equipped_prayers", [])
    p.run_energy = data.get("run_energy", 100)
    p.spec_energy = data.get("spec_energy", 100)
    p.cave_wave = data.get("cave_wave", 0)
    p.inferno_wave = data.get("inferno_wave", 0)
    p.spellbook = data.get("spellbook", "standard")
    p.barrows = data.get("barrows", [])
    p.barrows_loots = data.get("barrows_loots", 0)
    p.actions = data.get("actions", 0)
    p.farm = data.get("farm", {})
    p.crops = data.get("crops", 0)
    p.house = data.get("house", [])
    p.traps = data.get("traps", {})
    p.gwd_kc = data.get("gwd_kc", {})
    p.task_streak = data.get("task_streak", 0)
    p.slayer_task = data.get("slayer_task", None)
    p.slayer_points = data.get("slayer_points", 0)
    p.achievements = data.get("achievements", [])
    p.kills = data.get("kills", 0)
    p.kill_log = data.get("kill_log", {})
    p.bosses = data.get("bosses", [])
    p.potions_made = data.get("potions_made", 0)
    p.tips_seen = data.get("tips_seen", [])
    p.seen = set(data.get("seen") or [])
    p.seen.add(p.location)
    if not data.get("seen"):
        # older save: seed the cities 'travel' already offers — they're one
        # command away regardless, so 'goto' knowing them spoils nothing
        for room in set(TRAVEL_HUBS.values()):
            r = ROOMS[room]
            if r.get("members") and not p.members:
                continue
            ql = r.get("qlock")
            if ql and p.quests.get(ql[0]) not in ql[1]:
                continue
            p.seen.add(room)
    p.autoeat = data.get("autoeat", True)
    p.kingdom = data.get("kingdom", None)
    # (quest-story monsters need no restoring: QUEST_SPAWNS derives them
    #  from quest state whenever a room is looked at)
    return p


def cmd_save(p, _a):
    with open(SAVE_PATH, "w") as f:
        json.dump(serialize(p), f, indent=2)
    say(f"Game saved to {os.path.basename(SAVE_PATH)}.", "bgreen")


def load_game():
    if not os.path.exists(SAVE_PATH):
        return None
    with open(SAVE_PATH) as f:
        return deserialize(json.load(f))


def cmd_load(p, _a):
    say("Use 'load' from the title screen. (Loading mid-game not supported here.)")


