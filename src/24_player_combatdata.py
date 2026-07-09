# ===========================================================================
#  PLAYER
# ===========================================================================
EQUIP_SLOTS = ["weapon", "shield", "head", "body", "legs", "ammo",
               "cape", "amulet", "gloves", "boots", "ring"]


# ===========================================================================
#  OSRS-ACCURATE COMBAT DATA  (per-type attack / defence)
# ===========================================================================
# Real OSRS equipment bonuses (from gear_osrs_full.csv) and monster stats
# (from the OSRS monster data), applied to the ITEMS / MONSTERS tables so
# combat uses stab / slash / crush / magic / ranged like the real game.
# Attack keys: astab aslash acrush amagic arange | str rstr mdmg | prayer
# Defence keys: dstab dslash dcrush dmagic drange

ATK_TYPES = ["stab", "slash", "crush", "magic", "ranged"]
AKEY = {"stab": "astab", "slash": "aslash", "crush": "acrush",
        "magic": "amagic", "ranged": "arange"}
DKEY = {"stab": "dstab", "slash": "dslash", "crush": "dcrush",
        "magic": "dmagic", "ranged": "drange"}

GEAR_BONUSES = {
    'adamant arrow': {"rstr":31},
    'adamant full helm': {"amagic":-6,"arange":-3,"dcrush":16,"dmagic":-1,"drange":19,"dslash":21,"dstab":19},
    'adamant kiteshield': {"amagic":-8,"arange":-3,"dcrush":29,"dmagic":-1,"drange":29,"dslash":31,"dstab":27},
    'adamant pickaxe': {"acrush":15,"aslash":-2,"astab":17,"dslash":1,"speed":5,"str":19},
    'adamant platebody': {"amagic":-30,"arange":-15,"dcrush":55,"dmagic":-6,"drange":63,"dslash":63,"dstab":65},
    'adamant platelegs': {"amagic":-21,"arange":-11,"dcrush":29,"dmagic":-4,"drange":31,"dslash":31,"dstab":33},
    'adamant scimitar': {"acrush":-2,"aslash":29,"astab":6,"dslash":1,"speed":4,"str":28},
    'adamant sword': {"acrush":-2,"aslash":18,"astab":23,"dcrush":1,"dslash":2,"speed":4,"str":24},
    'amulet of accuracy': {"acrush":4,"amagic":4,"arange":4,"aslash":4,"astab":4},
    'amulet of defence': {"dcrush":7,"dmagic":7,"drange":7,"dslash":7,"dstab":7},
    'amulet of magic': {"amagic":10},
    'amulet of power': {"acrush":6,"amagic":6,"arange":6,"aslash":6,"astab":6,"dcrush":6,"dmagic":6,"drange":6,"dslash":6,"dstab":6,"prayer":1,"str":6},
    'amulet of strength': {"str":10},
    'black cape': {"dcrush":1,"drange":2,"dslash":1},
    'black full helm': {"amagic":-6,"arange":-3,"dcrush":10,"dmagic":-1,"drange":12,"dslash":13,"dstab":12},
    'black kiteshield': {"amagic":-8,"arange":-3,"dcrush":18,"dmagic":-1,"drange":18,"dslash":19,"dstab":17},
    'black platebody': {"amagic":-30,"arange":-15,"dcrush":30,"dmagic":-6,"drange":40,"dslash":40,"dstab":41},
    'black platelegs': {"amagic":-21,"arange":-11,"dcrush":19,"dmagic":-4,"drange":20,"dslash":20,"dstab":21},
    'black scimitar': {"acrush":-2,"aslash":19,"astab":4,"dslash":1,"speed":4,"str":14},
    'black sword': {"acrush":-2,"aslash":10,"astab":14,"dcrush":1,"dslash":2,"speed":4,"str":12},
    'blue cape': {"dcrush":1,"drange":2,"dslash":1},
    'bronze arrow': {"rstr":7},
    'bronze full helm': {"amagic":-6,"arange":-3,"dcrush":3,"dmagic":-1,"drange":4,"dslash":5,"dstab":4},
    'bronze kiteshield': {"amagic":-8,"arange":-3,"dcrush":6,"dmagic":-1,"drange":6,"dslash":7,"dstab":5},
    'bronze pickaxe': {"acrush":2,"aslash":-2,"astab":4,"dslash":1,"speed":5,"str":5},
    'bronze platebody': {"amagic":-30,"arange":-15,"dcrush":9,"dmagic":-6,"drange":14,"dslash":14,"dstab":15},
    'bronze platelegs': {"amagic":-21,"arange":-11,"dcrush":6,"dmagic":-4,"drange":7,"dslash":7,"dstab":8},
    'bronze scimitar': {"acrush":-2,"aslash":7,"astab":1,"dslash":1,"speed":4,"str":6},
    'bronze sword': {"acrush":-2,"aslash":3,"astab":4,"dcrush":1,"dslash":2,"speed":4,"str":5},
    'cape of legends': {"dcrush":7,"dmagic":7,"drange":7,"dslash":7,"dstab":7},
    "chef's hat": {},
    'climbing boots': {"dcrush":2,"dslash":2,"str":2},
    'dragon dagger': {"acrush":-4,"amagic":1,"aslash":25,"astab":40,"dmagic":1,"speed":4,"str":40},
    'dragon med helm': {"amagic":-3,"dcrush":32,"dmagic":-1,"drange":34,"dslash":35,"dstab":33},
    'gold ring': {},
    'green cape': {"dcrush":1,"drange":2,"dslash":1},
    'hardleather gloves': {"acrush":1,"amagic":1,"arange":1,"aslash":1,"astab":1,"dcrush":1,"dmagic":1,"drange":1,"dslash":1,"dstab":1,"str":1},
    'hill giant club': {"acrush":65,"amagic":-4,"aslash":50,"astab":-4,"drange":-1,"speed":7,"str":70},
    'holy symbol': {"dcrush":2,"dmagic":2,"drange":2,"dslash":2,"dstab":2,"prayer":8},
    'iron arrow': {"rstr":10},
    'iron full helm': {"amagic":-6,"arange":-3,"dcrush":5,"dmagic":-1,"drange":6,"dslash":7,"dstab":6},
    'iron kiteshield': {"amagic":-8,"arange":-3,"dcrush":9,"dmagic":-1,"drange":9,"dslash":10,"dstab":8},
    'iron pickaxe': {"acrush":3,"aslash":-2,"astab":5,"dslash":1,"speed":5,"str":7},
    'iron platebody': {"amagic":-30,"arange":-15,"dcrush":12,"dmagic":-6,"drange":20,"dslash":20,"dstab":21},
    'iron platelegs': {"amagic":-21,"arange":-11,"dcrush":10,"dmagic":-4,"drange":10,"dslash":10,"dstab":11},
    'iron scimitar': {"acrush":-2,"aslash":10,"astab":2,"dslash":1,"speed":4,"str":9},
    'iron sword': {"acrush":-2,"aslash":4,"astab":6,"dcrush":1,"dslash":2,"speed":4,"str":7},
    'leather body': {"amagic":-2,"arange":2,"dcrush":10,"dmagic":4,"drange":9,"dslash":9,"dstab":8},
    'leather boots': {"dcrush":1,"dslash":1},
    'leather gloves': {"dcrush":2,"dslash":1},
    'mithril arrow': {"rstr":22},
    'mithril full helm': {"amagic":-6,"arange":-3,"dcrush":11,"dmagic":-1,"drange":13,"dslash":14,"dstab":13},
    'mithril kiteshield': {"amagic":-8,"arange":-3,"dcrush":20,"dmagic":-1,"drange":20,"dslash":22,"dstab":18},
    'mithril pickaxe': {"acrush":10,"aslash":-2,"astab":12,"dslash":1,"speed":5,"str":13},
    'mithril platebody': {"amagic":-30,"arange":-15,"dcrush":38,"dmagic":-6,"drange":44,"dslash":44,"dstab":46},
    'mithril platelegs': {"amagic":-21,"arange":-11,"dcrush":20,"dmagic":-4,"drange":22,"dslash":22,"dstab":24},
    'mithril scimitar': {"acrush":-2,"aslash":21,"astab":5,"dslash":1,"speed":4,"str":20},
    'mithril sword': {"acrush":-2,"aslash":11,"astab":16,"dcrush":1,"dslash":2,"speed":4,"str":17},
    'oak shortbow': {"arange":14,"speed":4},
    'purple cape': {"dcrush":1,"drange":2,"dslash":1},
    'red cape': {"dcrush":1,"drange":2,"dslash":1},
    'ring of recoil': {},
    'rune arrow': {"rstr":49},
    'rune full helm': {"amagic":-6,"arange":-3,"dcrush":27,"dmagic":-1,"drange":30,"dslash":32,"dstab":30},
    'rune kiteshield': {"amagic":-8,"arange":-3,"dcrush":46,"dmagic":-1,"drange":46,"dslash":48,"dstab":44},
    'rune pickaxe': {"acrush":24,"aslash":-2,"astab":26,"dslash":1,"speed":5,"str":29},
    'rune platebody': {"amagic":-30,"arange":-15,"dcrush":72,"dmagic":-6,"drange":80,"dslash":80,"dstab":82},
    'rune platelegs': {"amagic":-21,"arange":-11,"dcrush":47,"dmagic":-4,"drange":49,"dslash":49,"dstab":51},
    'rune scimitar': {"acrush":-2,"aslash":45,"astab":7,"dslash":1,"speed":4,"str":44},
    'rune sword': {"acrush":-2,"aslash":26,"astab":38,"dcrush":1,"dslash":2,"speed":4,"str":39},
    'shortbow': {"arange":8,"speed":4},
    'staff of air': {"acrush":7,"amagic":10,"aslash":-1,"dcrush":1,"dmagic":10,"dslash":3,"dstab":2,"speed":5,"str":3},
    'staff of earth': {"acrush":9,"amagic":10,"aslash":-1,"astab":1,"dcrush":1,"dmagic":10,"dslash":3,"dstab":2,"speed":5,"str":5},
    'staff of fire': {"acrush":9,"amagic":10,"aslash":-1,"astab":3,"dcrush":1,"dmagic":10,"dslash":3,"dstab":2,"speed":5,"str":6},
    'staff of water': {"acrush":7,"amagic":10,"aslash":-1,"dcrush":1,"dmagic":10,"dslash":3,"dstab":2,"speed":5,"str":3},
    'steel arrow': {"rstr":16},
    'steel full helm': {"amagic":-6,"arange":-3,"dcrush":7,"dmagic":-1,"drange":9,"dslash":10,"dstab":9},
    'steel kiteshield': {"amagic":-8,"arange":-3,"dcrush":14,"dmagic":-1,"drange":14,"dslash":15,"dstab":13},
    'steel pickaxe': {"acrush":6,"aslash":-2,"astab":8,"dslash":1,"speed":5,"str":9},
    'steel platebody': {"amagic":-30,"arange":-15,"dcrush":24,"dmagic":-6,"drange":31,"dslash":31,"dstab":32},
    'steel platelegs': {"amagic":-21,"arange":-11,"dcrush":15,"dmagic":-4,"drange":16,"dslash":16,"dstab":17},
    'steel scimitar': {"acrush":-2,"aslash":15,"astab":3,"dslash":1,"speed":4,"str":14},
    'steel sword': {"acrush":-2,"aslash":8,"astab":11,"dcrush":1,"dslash":2,"speed":4,"str":12},
    'team cape': {},
    'willow shortbow': {"arange":20,"speed":4},
    'wizard hat': {"amagic":2,"dmagic":2},
    'wizard robe': {"amagic":3,"dmagic":3},
    'yellow cape': {"dcrush":1,"drange":2,"dslash":1},
}

MONSTER_STATS = {
    'barbarian': {"abonus":8,"atktype":["stab"],"att":6,"cb":8,"dcrush":0,"def":5,"dmagic":0,"drange":0,"dslash":1,"dstab":1,"hp":14,"mage":1,"maxhit":2,"range":1,"sbonus":10,"str":5,"weak":"crush"},
    'chicken': {"abonus":-47,"atktype":["stab"],"att":1,"cb":1,"dcrush":-42,"def":1,"dmagic":-42,"drange":-42,"dslash":-42,"dstab":-42,"hp":3,"mage":1,"maxhit":0,"range":1,"sbonus":-42,"str":1,"weak":"stab"},
    'chicken farmer': {"abonus":0,"atktype":["crush"],"att":1,"cb":2,"dcrush":0,"def":1,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":7,"mage":1,"maxhit":1,"range":1,"sbonus":0,"str":1,"weak":"slash"},
    'count draynor': {"abonus":0,"atktype":["crush"],"att":30,"cb":34,"dcrush":3,"def":30,"dmagic":0,"drange":0,"dslash":1,"dstab":2,"hp":35,"mage":1,"maxhit":3,"range":1,"sbonus":0,"str":25,"weak":"magic"},
    'cow': {"abonus":-15,"atktype":["crush"],"att":1,"cb":2,"dcrush":-21,"def":1,"dmagic":-21,"drange":-21,"dslash":-21,"dstab":-21,"hp":8,"mage":1,"maxhit":1,"range":1,"sbonus":-15,"str":1,"weak":"stab"},
    'dark warrior': {"abonus":20,"atktype":["slash"],"att":5,"cb":8,"dcrush":59,"def":5,"dmagic":0,"drange":0,"dslash":79,"dstab":96,"hp":17,"mage":1,"maxhit":2,"range":1,"sbonus":16,"str":5,"weak":"magic"},
    'dark wizard': {"abonus":0,"atktype":["magic"],"att":5,"cb":7,"dcrush":0,"def":5,"dmagic":3,"drange":0,"dslash":0,"dstab":0,"hp":12,"mage":6,"maxhit":6,"range":1,"sbonus":0,"str":2,"weak":"stab"},
    'dwarf': {"abonus":5,"atktype":["crush"],"att":6,"cb":7,"dcrush":0,"def":6,"dmagic":5,"drange":10,"dslash":0,"dstab":0,"hp":10,"mage":1,"maxhit":2,"range":1,"sbonus":7,"str":6,"weak":"stab"},
    'flesh crawler': {"abonus":0,"atktype":["slash"],"att":60,"cb":28,"dcrush":15,"def":10,"dmagic":15,"drange":15,"dslash":15,"dstab":15,"hp":25,"mage":1,"maxhit":1,"range":1,"sbonus":0,"str":2,"weak":"stab"},
    'giant rat': {"abonus":0,"atktype":["stab"],"att":1,"cb":3,"dcrush":-100,"def":1,"dmagic":0,"drange":-100,"dslash":-100,"dstab":-100,"hp":3,"mage":1,"maxhit":1,"range":1,"sbonus":0,"str":1,"weak":"stab"},
    'giant spider': {"abonus":-10,"atktype":["stab"],"att":1,"cb":2,"dcrush":-10,"def":1,"dmagic":-10,"drange":-10,"dslash":-10,"dstab":-10,"hp":5,"mage":1,"maxhit":1,"range":1,"sbonus":-10,"str":1,"weak":"stab"},
    'goblin': {"abonus":-21,"atktype":["crush"],"att":1,"cb":2,"dcrush":-15,"def":1,"dmagic":-15,"drange":-15,"dslash":-15,"dstab":-15,"hp":5,"mage":1,"maxhit":1,"range":1,"sbonus":-15,"str":1,"weak":"stab"},
    'greater demon': {"abonus":0,"atktype":["slash"],"att":76,"cb":92,"dcrush":0,"def":81,"dmagic":-10,"drange":0,"dslash":0,"dstab":0,"hp":87,"mage":1,"maxhit":9,"range":1,"sbonus":0,"str":78,"weak":"magic"},
    'guard': {"abonus":5,"atktype":["stab"],"att":8,"cb":10,"dcrush":4,"def":9,"dmagic":2,"drange":3,"dslash":4,"dstab":3,"hp":16,"mage":1,"maxhit":2,"range":1,"sbonus":7,"str":6,"weak":"magic"},
    'hill giant': {"abonus":18,"atktype":["crush"],"att":18,"cb":28,"dcrush":0,"def":26,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":35,"mage":1,"maxhit":4,"range":1,"sbonus":16,"str":22,"weak":"stab"},
    'hobgoblin': {"abonus":0,"atktype":["crush"],"att":22,"cb":28,"dcrush":0,"def":24,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":29,"mage":1,"maxhit":3,"range":1,"sbonus":0,"str":24,"weak":"stab"},
    'ice giant': {"abonus":29,"atktype":["slash"],"att":40,"cb":53,"dcrush":2,"def":40,"dmagic":0,"drange":0,"dslash":3,"dstab":0,"hp":70,"mage":1,"maxhit":7,"range":1,"sbonus":31,"str":40,"weak":"stab"},
    'imp': {"abonus":-42,"atktype":["stab"],"att":1,"cb":2,"dcrush":-42,"def":1,"dmagic":-42,"drange":-42,"dslash":-42,"dstab":-42,"hp":8,"mage":1,"maxhit":0,"range":1,"sbonus":-37,"str":1,"weak":"stab"},
    'king black dragon': {"abonus":0,"atktype":["stab","dragonfire"],"att":240,"cb":276,"dcrush":90,"def":240,"dmagic":80,"drange":70,"dslash":90,"dstab":70,"hp":240,"mage":240,"maxhit":25,"range":1,"sbonus":0,"str":240,"weak":"stab"},
    'lesser demon': {"abonus":0,"atktype":["slash"],"att":68,"cb":82,"dcrush":0,"def":71,"dmagic":-10,"drange":0,"dslash":0,"dstab":0,"hp":79,"mage":1,"maxhit":8,"range":1,"sbonus":0,"str":70,"weak":"magic"},
    'man': {"abonus":0,"atktype":["crush"],"att":1,"cb":2,"dcrush":-21,"def":1,"dmagic":-21,"drange":-21,"dslash":-21,"dstab":-21,"hp":7,"mage":1,"maxhit":1,"range":1,"sbonus":0,"str":1,"weak":"stab"},
    'minotaur': {"abonus":0,"atktype":["crush"],"att":12,"cb":12,"dcrush":-21,"def":10,"dmagic":-21,"drange":-21,"dslash":-21,"dstab":-21,"hp":10,"mage":1,"maxhit":2,"range":1,"sbonus":0,"str":10,"weak":"stab"},
    'moss giant': {"abonus":33,"atktype":["crush"],"att":30,"cb":42,"dcrush":0,"def":30,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":60,"mage":1,"maxhit":6,"range":1,"sbonus":31,"str":30,"weak":"stab"},
    'obor': {"abonus":100,"atktype":["crush","ranged"],"att":90,"cb":106,"dcrush":45,"def":60,"dmagic":20,"drange":20,"dslash":40,"dstab":35,"hp":120,"mage":1,"maxhit":22,"range":120,"sbonus":68,"str":100,"weak":"magic"},
    'scorpion': {"abonus":0,"atktype":["stab"],"att":11,"cb":14,"dcrush":15,"def":11,"dmagic":0,"drange":5,"dslash":15,"dstab":5,"hp":17,"mage":1,"maxhit":2,"range":1,"sbonus":0,"str":12,"weak":"magic"},
    'skeleton': {"abonus":0,"atktype":["melee","crush"],"att":10,"cb":13,"dcrush":-5,"def":7,"dmagic":0,"drange":5,"dslash":5,"dstab":5,"hp":18,"mage":0,"maxhit":2,"range":0,"sbonus":0,"str":11,"weak":"crush"},
    'thug': {"abonus":5,"atktype":["stab"],"att":7,"cb":10,"dcrush":3,"def":9,"dmagic":0,"drange":0,"dslash":3,"dstab":2,"hp":18,"mage":1,"maxhit":2,"range":1,"sbonus":5,"str":5,"weak":"magic"},
    'zombie': {"abonus":5,"atktype":["slash"],"att":8,"cb":13,"dcrush":0,"def":10,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":22,"mage":1,"maxhit":2,"range":1,"sbonus":0,"str":9,"weak":"stab"},
    'zombie rat': {"abonus":0,"atktype":["stab"],"att":2,"cb":3,"dcrush":0,"def":2,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":5,"mage":1,"maxhit":1,"range":1,"sbonus":0,"str":3,"weak":"stab"},
}


def _apply_osrs_gear():
    """Replace simplified item bonuses with real OSRS per-type bonuses."""
    for name, b in GEAR_BONUSES.items():
        it = ITEMS.get(name)
        if not it or not it.get("equip"):
            continue
        eq = it["equip"]
        for old in ("att", "def", "ranged", "magic"):
            eq.pop(old, None)
        eq.update(b)


def _apply_osrs_monsters():
    """Give monsters real OSRS levels, max hits and per-type defences."""
    for name, s in MONSTER_STATS.items():
        m = MONSTERS.get(name)
        if not m:
            continue
        m["hp"] = s["hp"]
        m["attack"] = s["att"]
        m["defence"] = s["def"]
        m["max_hit"] = s["maxhit"]
        m["level"] = s.get("cb")
        m["abonus"] = s.get("abonus", 0)
        m["atktype"] = s.get("atktype") or ["crush"]
        m["weakness"] = s.get("weak", "crush")
        m["dbonus"] = {"stab": s["dstab"], "slash": s["dslash"],
                       "crush": s["dcrush"], "magic": s["dmagic"],
                       "ranged": s["drange"]}


_apply_osrs_gear()
_apply_osrs_monsters()


class Player:
    def __init__(self, name="Guest"):
        self.name = name
        self.location = "lumbridge_castle"
        self.skills = {s: 0 for s in SKILLS}
        self.skills["hitpoints"] = _XP_TABLE[10]  # HP starts at level 10
        self.hp = 10
        self.inventory = {}
        self.bank = {}
        self.equipment = {slot: None for slot in EQUIP_SLOTS}
        self.style = "melee"      # melee / ranged / magic
        self.spellbook = "standard"   # standard / ancient (Desert Treasure)
        self.train = "shared"     # melee xp focus: attack/strength/defence/shared
        self.attack_type = "slash"  # melee sub-type: stab / slash / crush
        self.autocast = "wind strike"
        self.quests = {}          # quest_key -> stage string
        self.automap = "compass"  # off / compass / full — mini-map on each move
        self.members = False      # unlocks members areas / skills
        self.prayer_points = 1    # current prayer points (max = prayer level)
        self.active_prayers = []  # names of currently-active prayers
        self.combat = None        # interactive-combat state (None = not fighting)
        self.run_energy = 100     # 0-100; spent travelling, regained by acting
        self.spec_energy = 100    # 0-100; spent on special attacks
        self.cave_wave = 0        # Fight Caves progress (0 = no active run)
        self.inferno_wave = 0     # Inferno progress (0 = no active run)
        self.barrows = []         # brothers slain this Barrows run
        self.barrows_loots = 0    # chests looted lifetime
        self.actions = 0          # lifetime action clock (crops grow on it)
        self.farm = {}            # patch id -> {"seed": name, "at": actions}
        self.crops = 0            # crops harvested lifetime
        self.house = []           # furniture built in your player-owned house
        self.traps = {}           # hunter traps: slot -> {"creature", "at"}
        self.gwd_kc = {}          # God Wars kill count per god
        self.task_streak = 0      # consecutive slayer tasks completed
        self.slayer_task = None   # {"monster","amount","remaining"} or None
        self.slayer_points = 0
        self.poison = 0           # remaining poison ticks (transient combat fx)
        self.frozen = False       # next attack fails (ice breath)
        self.stat_drain = {}      # skill -> levels drained (shock breath)
        self.stat_boost = {}      # skill -> levels boosted (potions; transient)
        self.achievements = []    # unlocked achievement keys
        self.kills = 0            # total monsters defeated
        self.kill_log = {}        # monster name -> kill count (bestiary)
        self.bosses = []          # boss names defeated
        self.potions_made = 0     # potions brewed (for the Herbalist achievement)
        self.tips_seen = []       # one-time tips already shown (e.g. backup nudge)
        self.seen = {self.location}   # rooms discovered ('goto' walks these)
        self.autoeat = True       # reflex-eat when badly hurt in combat
        self.last_cmd = ""        # empty Enter repeats this (not saved)
        # starter kit — now includes basic armour so new adventurers aren't
        # one-shot fodder (combat felt punishing with just a sword + 10 HP).
        for it, q in [("bronze sword", 1), ("bronze full helm", 1),
                      ("bronze platebody", 1), ("bronze platelegs", 1),
                      ("bronze kiteshield", 1), ("leather gloves", 1),
                      ("leather boots", 1), ("bronze pickaxe", 1),
                      ("bronze axe", 1), ("small fishing net", 1),
                      ("tinderbox", 1), ("hammer", 1), ("shears", 1),
                      ("bread", 3), ("coins", 25)]:
            self.add(it, q)
        for it in ("bronze sword", "bronze full helm", "bronze platebody",
                   "bronze platelegs", "bronze kiteshield", "leather gloves",
                   "leather boots"):
            self.equip_item(it, silent=True)

    # --- skills ---------------------------------------------------------
    def lvl(self, skill):
        base = level_from_xp(self.skills[skill])
        base -= getattr(self, "stat_drain", {}).get(skill, 0)
        base += getattr(self, "stat_boost", {}).get(skill, 0)
        return max(1, base)

    def base_lvl(self, skill):
        """Unboosted/undrained level (for requirements that ignore potions)."""
        return level_from_xp(self.skills[skill])

    @property
    def max_hp(self):
        return self.lvl("hitpoints")

    def combat_level(self):
        base = 0.25 * (self.lvl("defence") + self.lvl("hitpoints")
                       + self.lvl("prayer") // 2)
        melee = 0.325 * (self.lvl("attack") + self.lvl("strength"))
        rng = 0.325 * (self.lvl("ranged") * 3 // 2)
        mag = 0.325 * (self.lvl("magic") * 3 // 2)
        return int(base + max(melee, rng, mag))

    # --- prayer ---------------------------------------------------------
    def prayer_max(self):
        return self.lvl("prayer")

    def prayer_mult(self, kind):
        """Effective-level multiplier for attack/strength/defence from prayers."""
        boost = 0.0
        for name in self.active_prayers:
            boost += PRAYERS.get(name, (0, 0, {}, None))[2].get(kind, 0.0)
        return 1.0 + boost

    def prayer_protects(self, style):
        for name in self.active_prayers:
            if PRAYERS.get(name, (0, 0, {}, None))[3] == style:
                return True
        return False

    def prayer_drain(self):
        base = sum(PRAYERS.get(n, (0, 0, {}, None))[1] for n in self.active_prayers)
        # prayer bonus from gear (e.g. holy symbol) slows the drain
        return base / (1 + self.equip_bonus("prayer") / 30)

    def gain_xp(self, skill, amount):
        amount = int(amount * XP_RATE)        # global XP rate (2x)
        before = self.lvl(skill)
        self.skills[skill] += amount
        if not _QUIET:                        # batches summarise xp at the end
            print(paint(f"  +{amount} {skill} xp", "bcyan"))
        after = self.lvl(skill)
        if after > before:
            animate([_tint(ART_LEVELUP, "byellow"), _tint(ART_LEVELUP, "bwhite"),
                     _tint(ART_LEVELUP, "gold"),
                     _tint(ART_LEVELUP, "byellow", "bold")],
                    delay=0.11, center=True)
            banner(f"LEVEL UP!  Your {skill} is now level {after}.",
                   color="byellow", line_color="gold")
            _, _, _, to_next = xp_progress(self.skills[skill])
            if after >= 99:
                say(f"  You have mastered {skill} — level 99!", "gold", "bold")
            else:
                say(f"  {to_next:,} xp to level {after + 1}.", "grey")
            if skill == "hitpoints":
                self.hp = self.max_hp

    # --- inventory ------------------------------------------------------
    def add(self, item, qty=1):
        self.inventory[item] = self.inventory.get(item, 0) + qty

    def take(self, item, qty=1):
        if self.inventory.get(item, 0) < qty:
            return False
        self.inventory[item] -= qty
        if self.inventory[item] <= 0:
            del self.inventory[item]
        return True

    def has(self, item, qty=1):
        return self.inventory.get(item, 0) >= qty

    def count(self, item):
        return self.inventory.get(item, 0)

    @property
    def coins(self):
        return self.inventory.get("coins", 0)

    def find_tool(self, kind):
        """Return an equipped/inventory tool name of the given kind, or None."""
        # check inventory and equipped weapon
        for item in list(self.inventory):
            if ITEMS.get(item, {}).get("tool") == kind:
                return item
        w = self.equipment["weapon"]
        if w and ITEMS.get(w, {}).get("tool") == kind:
            return w
        return None

    # --- equipment ------------------------------------------------------
    def equip_bonus(self, field):
        total = 0
        for slot, item in self.equipment.items():
            if item:
                total += ITEMS[item].get("equip", {}).get(field, 0)
        return total

    def equip_item(self, item, silent=False):
        info = ITEMS.get(item, {})
        eq = info.get("equip")
        if not eq:
            if not silent:
                say(f"You can't equip {item}.")
            return False
        if info.get("members") and not getattr(self, "members", False):
            say(f"{item} is members-only. Type 'membership' to unlock it.")
            return False
        for skill, req in eq.get("req", {}).items():
            if self.lvl(skill) < req:
                say(f"You need {skill} level {req} to wield {item}.")
                return False
        qreq = eq.get("quest")
        if qreq and self.quests.get(qreq) != "complete":
            say(f"Only those who complete '{ALL_QUESTS.get(qreq, qreq)}' may "
                f"wear the {item}.", "byellow")
            return False
        if not self.has(item):
            say(f"You don't have {item}.")
            return False
        slot = eq["slot"]
        # two-handed weapons need both hands; shields evict them right back
        if slot == "weapon" and eq.get("two_handed") and self.equipment.get("shield"):
            shield = self.equipment["shield"]
            self.add(shield)
            self.equipment["shield"] = None
            if not silent:
                say(f"You sling the {shield} on your back — the {item} "
                    "needs both hands.", "grey")
        if slot == "shield":
            w = self.equipment.get("weapon")
            if w and ITEMS.get(w, {}).get("equip", {}).get("two_handed"):
                self.add(w)
                self.equipment["weapon"] = None
                if not silent:
                    say(f"You put away the {w} to raise a shield.", "grey")
        if self.equipment[slot]:
            self.add(self.equipment[slot])
        self.take(item)
        self.equipment[slot] = item
        if slot == "weapon":            # default to the weapon's best melee type
            self.attack_type = _best_attack_type(item)
        if not silent:
            say(f"You equip the {item}.")
        return True

    def unequip(self, slot):
        if self.equipment.get(slot):
            self.add(self.equipment[slot])
            say(f"You unequip the {self.equipment[slot]}.")
            self.equipment[slot] = None
        else:
            say(f"Nothing equipped in {slot}.")


