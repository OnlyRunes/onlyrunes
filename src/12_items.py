# ===========================================================================
#  ITEM DATABASE
# ===========================================================================
# Each item: {"value": int, optional "equip", "heal", "tool", "tier", "bury",
#             "raw"/"cooked", ...}.  Alchemy values derive from "value".

ITEMS = {}


def add_item(name, value=1, **kw):
    ITEMS[name] = {"value": value, **kw}


# --- Currency, bones, hides, raw materials --------------------------------
add_item("coins", 1)
add_item("bones", 1, bury=("prayer", 5))
add_item("big bones", 3, bury=("prayer", 15))
add_item("cowhide", 12)
add_item("leather", 20)
add_item("wool", 8)
add_item("ball of wool", 12)
add_item("feather", 2)
add_item("rune essence", 4)

# --- Logs (firemaking / woodcutting) --------------------------------------
add_item("logs", 10, log_fm_xp=40)
add_item("oak logs", 30, log_fm_xp=60)
add_item("willow logs", 40, log_fm_xp=90)

# --- Ores, bars, gems -----------------------------------------------------
for ore, val in [("copper ore", 20), ("tin ore", 20), ("iron ore", 60),
                 ("silver ore", 80), ("coal", 50), ("gold ore", 150),
                 ("mithril ore", 160), ("adamantite ore", 240), ("clay", 25)]:
    add_item(ore, val)
for bar, val in [("bronze bar", 40), ("iron bar", 70), ("steel bar", 130),
                 ("silver bar", 90), ("gold bar", 170), ("mithril bar", 330),
                 ("adamant bar", 600)]:
    add_item(bar, val)

# --- Runes ----------------------------------------------------------------
for rune, val in [("air rune", 4), ("water rune", 4), ("earth rune", 4),
                  ("fire rune", 4), ("mind rune", 3), ("body rune", 3),
                  ("chaos rune", 90), ("nature rune", 180), ("law rune", 240),
                  ("cosmic rune", 120), ("death rune", 220)]:
    add_item(rune, val)

# --- Food (heal hitpoints) -----------------------------------------------
for food, heal, val in [("bread", 5, 12), ("cooked shrimp", 3, 5),
                        ("cooked anchovies", 1, 6), ("cooked sardine", 4, 8),
                        ("cooked herring", 5, 12), ("cooked trout", 7, 20),
                        ("cooked salmon", 9, 30), ("cooked pike", 8, 25),
                        ("cooked chicken", 3, 8), ("cooked meat", 3, 8),
                        ("cake", 4, 30)]:
    add_item(food, val, heal=heal)
for burnt in ["burnt shrimp", "burnt fish", "burnt chicken", "burnt meat"]:
    add_item(burnt, 1)

# --- Herblore: herbs, secondaries, vials & potions ------------------------
add_item("vial of water", 2)
# grimy herb -> (clean herb, herblore level to clean, clean xp)
HERBS = {
    "grimy guam":        ("guam leaf", 1, 2),
    "grimy marrentill":  ("marrentill", 5, 4),
    "grimy tarromin":    ("tarromin", 11, 5),
    "grimy harralander": ("harralander", 20, 6),
    "grimy ranarr":      ("ranarr weed", 25, 8),
    "grimy irit":        ("irit leaf", 40, 9),
    "grimy kwuarm":      ("kwuarm", 54, 11),
    "grimy cadantine":   ("cadantine", 66, 13),
}
for _grimy, (_clean, _lvl, _xp) in HERBS.items():
    add_item(_grimy, 5)
    add_item(_clean, 15)
for _sec, _val in [("eye of newt", 3), ("limpwurt root", 25), ("snape grass", 30),
                   ("unicorn horn dust", 20), ("chocolate dust", 8),
                   ("white berries", 40)]:
    add_item(_sec, _val)
# potion -> {herb, secondary, level, xp, effect}.  effect = (kind, arg, tier)
#   ("boost", skill, tier)  temporary +level boost for the current fight
#   ("restore","prayer"/"energy")   ("cure","poison")
POTIONS = {
    "attack potion":   {"herb": "guam leaf", "second": "eye of newt", "lvl": 1,
                        "xp": 25, "effect": ("boost", "attack", 0), "value": 40},
    "antipoison":      {"herb": "marrentill", "second": "unicorn horn dust",
                        "lvl": 5, "xp": 38, "effect": ("cure", "poison", 0),
                        "value": 50},
    "strength potion": {"herb": "tarromin", "second": "limpwurt root", "lvl": 12,
                        "xp": 50, "effect": ("boost", "strength", 0), "value": 60},
    "energy potion":   {"herb": "harralander", "second": "chocolate dust",
                        "lvl": 26, "xp": 67, "effect": ("restore", "energy", 0),
                        "value": 80},
    "defence potion":  {"herb": "ranarr weed", "second": "white berries",
                        "lvl": 30, "xp": 75, "effect": ("boost", "defence", 0),
                        "value": 90},
    "prayer potion":   {"herb": "ranarr weed", "second": "snape grass", "lvl": 38,
                        "xp": 88, "effect": ("restore", "prayer", 0), "value": 150},
    "super attack":    {"herb": "irit leaf", "second": "eye of newt", "lvl": 45,
                        "xp": 100, "effect": ("boost", "attack", 1), "value": 180},
    "super strength":  {"herb": "kwuarm", "second": "limpwurt root", "lvl": 55,
                        "xp": 125, "effect": ("boost", "strength", 1), "value": 220},
    "super defence":   {"herb": "cadantine", "second": "white berries", "lvl": 66,
                        "xp": 150, "effect": ("boost", "defence", 1), "value": 260},
}
for _pot, _d in POTIONS.items():
    add_item(_pot, _d["value"], potion=True)

# --- Obor (Hill Giant boss) unlock + drop ---------------------------------
add_item("giant key", 1)
add_item("hill giant club", 45000,
         equip={"slot": "weapon", "att": 30, "str": 36, "req": {"attack": 40}})

# Raw food -> cooked mapping
RAW_TO_COOKED = {
    "raw shrimp": ("cooked shrimp", "burnt shrimp", 1),
    "raw anchovies": ("cooked anchovies", "burnt shrimp", 1),
    "raw sardine": ("cooked sardine", "burnt fish", 5),
    "raw herring": ("cooked herring", "burnt fish", 5),
    "raw trout": ("cooked trout", "burnt fish", 15),
    "raw salmon": ("cooked salmon", "burnt fish", 25),
    "raw pike": ("cooked pike", "burnt fish", 20),
    "raw chicken": ("cooked chicken", "burnt chicken", 1),
    "raw beef": ("cooked meat", "burnt meat", 1),
}
COOK_XP = {"raw shrimp": 30, "raw anchovies": 30, "raw sardine": 40,
           "raw herring": 50, "raw trout": 70, "raw salmon": 90,
           "raw pike": 80, "raw chicken": 30, "raw beef": 30}
for raw in RAW_TO_COOKED:
    add_item(raw, max(1, ITEMS[RAW_TO_COOKED[raw][0]]["value"] // 2))
add_item("egg", 4)
add_item("pot", 1)
add_item("pot of flour", 10)
add_item("grain", 4)
add_item("bucket", 2)
add_item("bucket of milk", 6)
add_item("garlic", 3)

# --- Tools ----------------------------------------------------------------
add_item("tinderbox", 1, tool="tinderbox")
add_item("hammer", 1, tool="hammer")
add_item("needle", 1, tool="needle")
add_item("thread", 1)
add_item("chisel", 1, tool="chisel")
add_item("shears", 1, tool="shears")
add_item("small fishing net", 5, tool="net")
add_item("fishing rod", 5, tool="rod")
add_item("fly fishing rod", 5, tool="fly")
add_item("harpoon", 5, tool="harpoon")
add_item("stake", 1)
add_item("chef's hat", 1, equip={"slot": "head"})

# --- Metal equipment (bronze -> rune) -------------------------------------
# (name, level requirement, tier index)
METALS = [("bronze", 1, 0), ("iron", 1, 1), ("steel", 5, 2), ("black", 10, 3),
          ("mithril", 20, 4), ("adamant", 30, 5), ("rune", 40, 6)]
TIER_VALUE = [1, 2, 4, 7, 12, 25, 60]

for mname, req, t in METALS:
    v = TIER_VALUE[t]
    add_item(f"{mname} sword", 30 * v,
             equip={"slot": "weapon", "att": 4 + t * 4, "str": 3 + t * 3,
                    "req": {"attack": req}})
    add_item(f"{mname} scimitar", 40 * v,
             equip={"slot": "weapon", "att": 5 + t * 5, "str": 5 + t * 4,
                    "req": {"attack": req}})
    add_item(f"{mname} platebody", 100 * v,
             equip={"slot": "body", "def": 10 + t * 6, "req": {"defence": req}})
    add_item(f"{mname} platelegs", 70 * v,
             equip={"slot": "legs", "def": 6 + t * 4, "req": {"defence": req}})
    add_item(f"{mname} kiteshield", 60 * v,
             equip={"slot": "shield", "def": 5 + t * 4, "req": {"defence": req}})
    add_item(f"{mname} full helm", 35 * v,
             equip={"slot": "head", "def": 3 + t * 2, "req": {"defence": req}})
    # tools share the metal tiers (no black tools, as in OSRS)
    if mname != "black":
        add_item(f"{mname} pickaxe", 20 * v,
                 tool="pickaxe", tier=t, equip={"slot": "weapon", "att": 2 + t,
                 "str": 2 + t, "req": {"attack": req}})
        add_item(f"{mname} axe", 16 * v, tool="axe", tier=t)

# --- Daggers (stab weapons; real OSRS per-type bonuses) -------------------
# Smith menu lists "dagger"; these make it real and give an early stab option.
_DAGGER_STATS = {"bronze": (4, 2, 3), "iron": (5, 3, 4), "steel": (8, 4, 7),
                 "black": (10, 5, 7), "mithril": (11, 5, 10),
                 "adamant": (15, 8, 14), "rune": (25, 12, 24)}
for mname, req, t in METALS:
    astab, aslash, strb = _DAGGER_STATS[mname]
    add_item(f"{mname} dagger", 10 * TIER_VALUE[t],
             equip={"slot": "weapon", "astab": astab, "aslash": aslash,
                    "acrush": -4, "str": strb, "req": {"attack": req}})

# --- Ranged gear ----------------------------------------------------------
add_item("shortbow", 20, equip={"slot": "weapon", "ranged": 8, "req": {"ranged": 1}})
add_item("oak shortbow", 40, equip={"slot": "weapon", "ranged": 14, "req": {"ranged": 5}})
add_item("willow shortbow", 70, equip={"slot": "weapon", "ranged": 20, "req": {"ranged": 20}})
for arrow, t in [("bronze arrow", 0), ("iron arrow", 1), ("steel arrow", 2),
                 ("mithril arrow", 4), ("adamant arrow", 5), ("rune arrow", 6)]:
    add_item(arrow, 2 + t * 3, equip={"slot": "ammo", "ranged": 7 + t * 4})
add_item("leather body", 30, equip={"slot": "body", "def": 8, "ranged": 8,
         "req": {"defence": 1}})

# --- Magic gear -----------------------------------------------------------
for st in ["air", "water", "earth", "fire"]:
    add_item(f"staff of {st}", 1500, provides=f"{st} rune",
             equip={"slot": "weapon", "magic": 10, "att": 5, "str": 5,
                    "req": {"attack": 1}})
add_item("wizard hat", 20, equip={"slot": "head", "magic": 2})
add_item("wizard robe", 20, equip={"slot": "body", "magic": 3})

# --- Amulets, capes, gloves, boots, rings (extra equipment slots) ---------
add_item("amulet of accuracy", 500, equip={"slot": "amulet", "att": 4})
add_item("amulet of defence", 600, equip={"slot": "amulet", "def": 4})
add_item("amulet of magic", 1000, equip={"slot": "amulet", "magic": 10})
add_item("amulet of power", 1500, equip={"slot": "amulet", "att": 6, "str": 6,
         "def": 6, "ranged": 6})
add_item("amulet of strength", 1800, equip={"slot": "amulet", "str": 10})
add_item("holy symbol", 800, equip={"slot": "amulet", "prayer": 8})
for col in ["blue", "black", "red", "green", "yellow", "purple"]:
    add_item(f"{col} cape", 20, equip={"slot": "cape", "def": 1})
add_item("team cape", 50, equip={"slot": "cape", "def": 2})
add_item("cape of legends", 1200, members=True,
         equip={"slot": "cape", "def": 4, "str": 1})
add_item("leather gloves", 12, equip={"slot": "gloves", "def": 1})
add_item("hardleather gloves", 30, equip={"slot": "gloves", "def": 2})
add_item("leather boots", 12, equip={"slot": "boots", "def": 1})
add_item("climbing boots", 120, members=True,
         equip={"slot": "boots", "def": 2, "str": 2})
add_item("gold ring", 350, equip={"slot": "ring"})
add_item("ring of recoil", 500, members=True, equip={"slot": "ring", "def": 1})

# --- Uncut gems (crafting / drops) ----------------------------------------
for gem, val in [("uncut sapphire", 100), ("uncut emerald", 200),
                 ("uncut ruby", 600), ("uncut diamond", 1200),
                 ("sapphire", 250), ("emerald", 400), ("ruby", 1000),
                 ("diamond", 2000)]:
    add_item(gem, val)

# --- Misc / quest / drop items --------------------------------------------
add_item("raw rat meat", 1)
add_item("cooked rat meat", 3, heal=3)
add_item("ashes", 1)
add_item("red bead", 2)
add_item("yellow bead", 2)
add_item("black bead", 2)
add_item("white bead", 2)
add_item("ranarr seed", 1500, members=True)
add_item("ghost's skull", 1)
add_item("air talisman", 50)
add_item("oil can", 1)
add_item("pressure gauge", 1)
add_item("rubber tube", 1)
add_item("dragon med helm", 60000, members=True,
         equip={"slot": "head", "def": 30, "req": {"defence": 60}})
add_item("dragon dagger", 30000, members=True,
         equip={"slot": "weapon", "att": 40, "str": 40, "req": {"attack": 60}})
RAW_TO_COOKED["raw rat meat"] = ("cooked rat meat", "burnt meat", 1)
COOK_XP["raw rat meat"] = 30


