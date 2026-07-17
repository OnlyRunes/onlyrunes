# ===========================================================================
#  COMBAT
# ===========================================================================
def _accuracy(att_roll, def_roll):
    # clamp rolls so heavy off-style gear (very negative bonuses) can't push the
    # probability below 0 / above 1 — keeps the result a sane [0,1] chance.
    att_roll = max(0, att_roll)
    def_roll = max(0, def_roll)
    if att_roll > def_roll:
        return 1 - (def_roll + 2) / (2 * (att_roll + 1))
    return att_roll / (2 * (def_roll + 1))


def _style_atk_bonus(p):
    """The player's offensive accuracy bonus for their current combat style."""
    if p.style == "ranged":
        return p.equip_bonus("arange")
    if p.style == "magic":
        return p.equip_bonus("amagic")
    atype = getattr(p, "attack_type", "slash")
    return p.equip_bonus(AKEY.get(atype, "aslash"))


def _best_attack_type(item):
    """The melee attack type (stab/slash/crush) a weapon hits best with."""
    eq = ITEMS.get(item, {}).get("equip", {})
    vals = {t: eq.get(AKEY[t], 0) for t in ("stab", "slash", "crush")}
    return max(vals, key=vals.get) if any(v > 0 for v in vals.values()) else "slash"


_LAST_SPELL = [None]        # spell cast this attack (for on-hit effects)


def _player_attack(p, m):
    """Return (kind, atype, att_roll, max_hit) for one player attack, or None."""
    if p.style == "ranged":
        bow = p.equipment["weapon"]
        ammo = p.equipment["ammo"]
        if not bow or "arange" not in ITEMS[bow].get("equip", {}):
            say("You need a bow equipped to use ranged.")
            return None
        self_ammo = ITEMS[bow].get("equip", {}).get("self_ammo")
        if not self_ammo and (not ammo or p.count_ammo() <= 0):
            say("You're out of arrows!")
            return None
        acc = p.equip_bonus("arange")
        rstr = p.equip_bonus("rstr")
        eff = p.lvl("ranged") + 9
        att_roll = eff * (acc + 64)
        max_hit = int(0.5 + eff * (rstr + 64) / 640)
        if not self_ammo:               # the blowpipe feeds itself
            p.take(ammo)  # consume one arrow
            if p.count(ammo) == 0:
                p.equipment["ammo"] = None
        return ("ranged", "ranged", att_roll, max_hit)
    if p.style == "magic":
        wpn = p.equipment.get("weapon")
        powered = ITEMS.get(wpn, {}).get("equip", {}).get("powered") \
            if wpn else None
        if powered:                     # trident-class: casts its own magic
            att_roll = (p.lvl("magic") + 9) * (p.equip_bonus("amagic") + 64)
            max_hit = int(powered * (1 + p.equip_bonus("mdmg") / 100))
            return ("magic", "magic", att_roll, max_hit)
        spell = SPELLS.get(p.autocast)
        if not spell or spell["type"] != "combat":
            say("Set a combat spell with 'autocast <spell>'.")
            return None
        if spell.get("book", "standard") != getattr(p, "spellbook",
                                                    "standard"):
            say(f"{p.autocast.title()} belongs to the "
                f"{spell.get('book', 'standard')} spellbook — swap books "
                "at its altar.")
            return None
        if p.lvl("magic") < spell["lvl"]:
            say(f"You need magic level {spell['lvl']} to cast {p.autocast}.")
            return None
        if not _consume_runes(p, spell["runes"]):
            say(f"You don't have the runes for {p.autocast}.")
            return None
        p.gain_xp("magic", max(1, spell["xp"] // 2))   # xp per cast, OSRS-style
        _LAST_SPELL[0] = p.autocast
        att_roll = (p.lvl("magic") + 9) * (p.equip_bonus("amagic") + 64)
        # magic-damage gear (ahrim's, nightmare staff) raises the spell cap
        max_hit = int(spell["max"] * (1 + p.equip_bonus("mdmg") / 100))
        return ("magic", "magic", att_roll, max_hit)
    # melee: accuracy uses the chosen attack type; damage uses strength bonus
    atype = getattr(p, "attack_type", "slash")
    if atype not in ("stab", "slash", "crush"):
        atype = "slash"
    atk_bonus = p.equip_bonus(AKEY[atype])
    str_bonus = p.equip_bonus("str")
    att_lvl = int(p.lvl("attack") * p.prayer_mult("attack"))
    str_lvl = int(p.lvl("strength") * p.prayer_mult("strength"))
    att_roll = (att_lvl + 9) * (atk_bonus + 64)
    max_hit = int(0.5 + (str_lvl + 9) * (str_bonus + 64) / 640)
    return ("melee", atype, att_roll, max_hit)


STYLE_COLOR = {"melee": "bred", "ranged": "bgreen", "magic": "bblue"}


def _new_monster(mname):
    m = dict(MONSTERS[mname])
    m["cur"] = m["hp"]
    m["name"] = mname
    return m


VERB = {"stab": "stab", "slash": "slash", "crush": "crush",
        "ranged": "shoot", "magic": "blast"}


def _resolve_player_hit(p, m, acc_mult=1.0, dmg_mult=1.0):
    """One player swing at m. Prints. Returns 'won', 'noattack', or None.
    acc_mult/dmg_mult let special attacks boost the roll (default: normal)."""
    atk = _player_attack(p, m)
    if atk is None:
        return "noattack"
    kind, atype, att_roll, max_hit = atk
    if acc_mult != 1.0:
        att_roll = int(att_roll * acc_mult)
    if dmg_mult != 1.0:
        max_hit = max(1, int(max_hit * dmg_mult))
    barrows = _barrows_set(p)
    if barrows == "dharok" and p.max_hp:      # the lower your hp, the harder you hit
        max_hit = int(max_hit * (1 + (1 - p.hp / p.max_hp)))
    task = getattr(p, "slayer_task", None)    # slayer helm/black mask ferocity
    if task and task.get("remaining", 0) > 0 and m["name"] == task.get("monster") \
            and p.equipment.get("head") in ("slayer helmet", "black mask"):
        att_roll = int(att_roll * 1.15)
        max_hit = max(1, int(max_hit * 1.15))
    wpn = p.equipment.get("weapon")            # dragon-hunter gear vs dragons
    if m.get("dragon") and ITEMS.get(wpn, {}).get("equip", {}).get("dragon_bane"):
        att_roll = int(att_roll * 1.2)
        max_hit = max(1, int(max_hit * 1.25))
    if m.get("flying") and kind == "melee":   # airborne foes shrug off melee
        max_hit = max(1, max_hit // 2)
    def_bonus = m.get("dbonus", {}).get(atype, 0)     # monster's defence vs this type
    def_roll = (m["defence"] + 9) * (def_bonus + 64)
    hit = random.random() < _accuracy(att_roll, def_roll)
    if not hit and barrows == "verac" and random.random() < 0.25:
        hit = True
        print("  " + paint("Verac's aura pierces its guard!", "bmagenta"))
    if hit:
        dmg = random.randint(0, max_hit)
        m["cur"] -= dmg
        if m.get("carapace") and not m.get("phase2") and atype != "crush" \
                and dmg > 1:
            dmg = max(1, dmg // 2)
            m["cur"] += dmg              # give back the halved portion
            print("  " + paint("Her carapace turns the blow — only CRUSH "
                               "bites deep!", "byellow"))
        if m.get("corporeal") and dmg > 1 \
                and "spear" not in (p.equipment.get("weapon") or ""):
            m["cur"] += dmg - max(1, dmg // 2)
            dmg = max(1, dmg // 2)
            print("  " + paint("Its hide swallows the blow — only SPEARS "
                               "pierce the Corporeal Beast!", "byellow"))
        if m.get("pick_only") and dmg > 1 and not p.find_tool("pickaxe"):
            m["cur"] += dmg - max(1, dmg // 2)
            dmg = max(1, dmg // 2)
            print("  " + paint("Stone shrugs off steel — bring a PICKAXE "
                               "to crack Zalcano!", "byellow"))
        if m.get("mage_only") and kind != "magic" and dmg > 0:
            m["cur"] += dmg
            dmg = 0
            print("  " + paint("Kolodion swats it aside: \"MAGIC, in MY "
                               "arena!\"", "bmagenta"))
        if m["cur"] <= 0 and m.get("transform") and not m.get("phase2"):
            m["phase2"] = True
            m["cur"] = m["hp"]
            if m.get("transform_flies"):
                m["flying"] = True
            say(m.get("transform_msg",
                      "The carapace SPLITS — the Kalphite Queen sheds her "
                      "shell and takes wing, reborn!"), "bmagenta", "bold")
        if m["cur"] <= 0 and m.get("finisher") and not p.has(m["finisher"]):
            m["cur"] = max(1, int(m["hp"] * 0.3))
            print("  " + paint(f"The {m['name']} starts to crumble \u2014 "
                               f"then its stone knits back together! "
                               f"(finish it with a {m['finisher']})",
                               "byellow"))
        if dmg > 0 and kind == "magic" and m["cur"] > 0 and _LAST_SPELL[0]:
            _sp = SPELLS.get(_LAST_SPELL[0])
            if _sp and _sp.get("effect"):
                _sp["effect"](p, m, dmg)   # ancient magicks bite twice
        if dmg > 0 and barrows and m["cur"] > 0:
            _barrows_set_proc(p, m, barrows, kind, dmg)
        bar = bar_meter(max(m["cur"], 0), m["hp"], 18, fill_color="bred")
        if dmg == 0:
            print("  " + paint(f"Your {VERB[atype]} glances off the "
                               f"{m['name']}. (0)", "grey") + "  " + bar)
        elif max_hit and dmg == max_hit:
            print("  " + paint(f"★ MAX HIT! You {VERB[atype]} the {m['name']} "
                               f"for {dmg}!", "byellow", "bold") + "  " + bar)
        else:
            print("  " + paint(f"You {VERB[atype]} the {m['name']} for {dmg}!",
                               "bgreen") + "  " + bar)
        if dmg > 0 and m.get("recoil"):        # spiky hide bites back (never lethal)
            hurt = min(m["recoil"], p.hp - 1)
            if hurt > 0:
                p.hp -= hurt
                print("  " + paint(f"Its spiked hide recoils — you take {hurt}!",
                                   "orange"))
    else:
        miss = "splash on" if kind == "magic" else "fail to hit"
        print("  " + paint(f"You {miss} the {m['name']}.", "grey"))
    return "won" if m["cur"] <= 0 else None


# --- Weapon special attacks (OSRS-style) -----------------------------------
# weapon -> its special: energy cost (%), number of hits, accuracy/damage
# multipliers, and an optional extra effect.
SPECIAL_ATTACKS = {
    "dragon dagger": {"name": "Puncture", "cost": 25, "hits": 2,
                      "acc": 1.15, "dmg": 1.15,
                      "desc": "two lightning-fast stabs, +15% accuracy & damage"},
    "dragon mace": {"name": "Shatter", "cost": 25, "hits": 1,
                    "acc": 1.25, "dmg": 1.5,
                    "desc": "a colossal blow, +25% accuracy, +50% max hit"},
    "dragon longsword": {"name": "Cleave", "cost": 25, "hits": 1,
                         "acc": 1.0, "dmg": 1.25,
                         "desc": "a mighty cleave, +25% max hit"},
    "dragon scimitar": {"name": "Sever", "cost": 55, "hits": 1,
                        "acc": 1.25, "dmg": 1.1,
                        "desc": "a vicious slice, +25% accuracy, +10% max hit"},
    "granite maul": {"name": "Quick Smash", "cost": 50, "hits": 2,
                     "acc": 1.0, "dmg": 1.0,
                     "desc": "an instant second smash — two full hits"},
    "abyssal whip": {"name": "Energy Drain", "cost": 50, "hits": 1,
                     "acc": 1.25, "dmg": 1.0, "energy": 25,
                     "desc": "an accurate lash that restores 25 run energy"},
    "magic shortbow": {"name": "Snapshot", "cost": 55, "hits": 2,
                       "acc": 0.9, "dmg": 1.0,
                       "desc": "two arrows loosed at once, -10% accuracy"},
    "hill giant club": {"name": "Bone Crunch", "cost": 50, "hits": 1,
                        "acc": 1.1, "dmg": 1.4,
                        "desc": "a skull-rattling crunch, +10% accuracy, "
                                "+40% max hit"},
}


def cmd_spec(p, _a):
    """Show your weapon's special attack + energy (use 'spec' in combat)."""
    w = p.equipment.get("weapon")
    sp = SPECIAL_ATTACKS.get(w)
    e = int(getattr(p, "spec_energy", 100))
    print("  " + paint("Special energy: ", "white")
          + bar_meter(e, 100, 20, fill_color="teal") + paint(f" {e}%", "teal"))
    if sp:
        say(f"  {w} — {sp['name']} ({sp['cost']}%): {sp['desc']}", "bcyan")
        say("  Use 'spec' during combat to unleash it.", "grey")
    elif w:
        say(f"  Your {w} has no special attack.", "grey")
    else:
        say("  You have no weapon equipped.", "grey")
        say("  Weapons with specials: " + ", ".join(sorted(SPECIAL_ATTACKS)),
            "grey")


def _do_special(p, m):
    """Unleash the equipped weapon's special attack. Returns like an attack:
    'won', 'noattack' (turn not spent), or None."""
    w = p.equipment.get("weapon")
    sp = SPECIAL_ATTACKS.get(w)
    if not sp:
        say("Your weapon has no special attack. ('spec' lists them.)", "grey")
        return "noattack"
    if getattr(p, "spec_energy", 100) < sp["cost"]:
        say(f"Not enough special energy ({int(p.spec_energy)}%, need "
            f"{sp['cost']}%). It recharges out of combat.", "byellow")
        return "noattack"
    p.spec_energy -= sp["cost"]
    say(f"⚡ SPECIAL — {sp['name'].upper()}! "
        + paint(f"(-{sp['cost']}% energy)", "grey"), "teal", "bold")
    result = None
    for _ in range(sp["hits"]):
        r = _resolve_player_hit(p, m, sp.get("acc", 1.0), sp.get("dmg", 1.0))
        if r == "noattack":               # e.g. out of ammo: refund, no turn
            p.spec_energy += sp["cost"]
            return "noattack"
        if r == "won":
            result = "won"
            break
    if sp.get("energy") and getattr(p, "run_energy", 100) < 100:
        gain = min(100 - p.run_energy, sp["energy"])
        p.run_energy += gain
        print("  " + paint(f"You feel invigorated! (+{int(gain)} run energy)",
                           "lime"))
    if result != "won" and sp.get("after"):     # godsword-style side effects
        sp["after"](p, m)
    return result


def _clear_status(p):
    """Drop transient combat status effects (when a fight ends)."""
    p.poison = 0
    p.frozen = False
    p.stat_drain = {}
    p.stat_boost = {}


def _tick_poison(p):
    """Apply one tick of poison at the start of the player's turn."""
    if getattr(p, "poison", 0) <= 0:
        return
    if p.equipment.get("head") == "serpentine helm":
        p.poison = 0
        print("  " + paint("Your serpentine helm drinks the venom "
                           "harmlessly.", "green"))
        return
    dmg = 3
    p.poison -= 1
    p.hp -= dmg
    print("  " + paint(f"Poison courses through you for {dmg}.", "bgreen")
          + "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0), p.max_hp, 18))


def _apply_kbd_effect(p, key):
    """The lingering effect of a KBD breath that lands on you."""
    if key == "poison":
        p.poison = 4
        print("  " + paint("The poison takes hold — it will sear you each turn!",
                           "bgreen"))
    elif key == "ice":
        p.frozen = True
        print("  " + paint("You are frozen solid — your next strike will fail!",
                           "bcyan"))
    elif key == "shock":
        for s in ("attack", "strength", "defence", "ranged", "magic"):
            p.stat_drain[s] = p.stat_drain.get(s, 0) + 2
        print("  " + paint("Crackling energy saps your stats! (-2 combat levels)",
                           "bblue"))


def _dragonfire_adjust(p, dmg):
    """Dragonfire burns through armour — unless a dragon shield soaks it."""
    shield = p.equipment.get("shield")
    if shield in ("anti-dragon shield", "dragonfire ward"):
        print("  " + paint(f"Your {shield} deflects the worst of the "
                           "flames!", "bcyan"))
        return dmg // 3
    print("  " + paint("The dragonfire sears you — an anti-dragon shield "
                       "would protect you!", "orange"))
    return int(dmg * 1.5)


def _kbd_take_turn(p, m):
    """The King Black Dragon's turn: pick one of its varied attacks."""
    atk = random.choices(KBD_ATTACKS, weights=[a["w"] for a in KBD_ATTACKS])[0]
    animate(atk["builder"](), delay=0.1, center=True)
    say(f"The King Black Dragon {atk['verb']} {atk['label']}!", *atk["color"])
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    dtype = "crush" if atk["key"] == "melee" else "magic"   # breaths are magical
    p_def_roll = _player_def_roll(p, dtype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, max(1, int(m["max_hit"] * atk["mult"])))
        if atk["key"] != "melee":                     # every breath is dragonfire
            dmg = _dragonfire_adjust(p, dmg)
        prot = "melee" if atk["key"] == "melee" else "magic"  # prayer mitigates
        if p.prayer_protects(prot):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        print("  " + paint(f"It strikes you for {dmg}.", "bred")
              + "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0), p.max_hp, 18))
        if p.hp > 0:
            _apply_kbd_effect(p, atk["key"])
    else:
        print("  " + paint("You weather the assault.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


def _boss_take_turn(p, m, attacks):
    """Generic varied-moveset turn: pick a weighted attack, animate, hit, apply
    its effect. Used by bosses other than the KBD (which has bespoke logic)."""
    atk = random.choices(attacks, weights=[a["w"] for a in attacks])[0]
    animate(atk["builder"](), delay=0.12, center=True)
    say(f"{m['name'].title()} {atk['verb']} {atk['label']}!", *atk["color"])
    atype = atk.get("atype", "crush")
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    p_def_roll = _player_def_roll(p, atype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, max(1, int(m["max_hit"] * atk["mult"])))
        if atk.get("dragonfire"):
            dmg = _dragonfire_adjust(p, dmg)
        prot = "magic" if atype == "magic" else \
            ("ranged" if atype == "ranged" else "melee")
        if p.prayer_protects(prot):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        hpbar = "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0), p.max_hp, 18)
        if dmg == 0:
            print("  " + paint("Its blow grazes you. (0)", "grey") + hpbar)
        else:
            print("  " + paint(f"It hits you for {dmg}.", "bred") + hpbar)
            if p.hp > 0:
                _player_recoil(p, m, dmg)
                if getattr(p, "venge", False) and m["cur"] > 0:
                    p.venge = False          # Vengeance works on bosses too
                    vd = max(1, int(dmg * 0.75))
                    m["cur"] -= vd
                    print("  " + paint(f"\"Taste vengeance!\" — {vd} damage "
                                       "rebounds!", "bmagenta", "bold"))
                if atk.get("effect"):
                    atk["effect"](p, m, dmg)
    else:
        print("  " + paint("You weather the blow.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


def _obor_take_turn(p, m):
    return _boss_take_turn(p, m, OBOR_ATTACKS)


def _count_take_turn(p, m):
    return _boss_take_turn(p, m, COUNT_ATTACKS)


# Bosses with bespoke, varied turns (else the generic swing below is used).
BOSS_TURN = {"king black dragon": _kbd_take_turn,
             "obor": _obor_take_turn,
             "count draynor": _count_take_turn}


def _monster_atk_type(m):
    """The damage type a monster attacks with (stab/slash/crush/magic/ranged)."""
    for t in (m.get("atktype") or []):
        if t in DKEY:
            return t
    return "crush"                       # 'melee'/'dragonfire'/unknown -> crush


def _player_def_roll(p, atype):
    """Player's defence roll against an incoming attack of the given type."""
    def_lvl = int(p.lvl("defence") * p.prayer_mult("defence"))
    return (def_lvl + 9) * (p.equip_bonus(DKEY[atype]) + 64)


# monsters with a signature move register it here: name -> fn(p, m, dmg),
# fired after the monster lands a successful hit (dmg may be 0)
MONSTER_EFFECTS = {}


def _player_recoil(p, m, dmg):
    """Ring of recoil: bite back 1 damage when you take a hit (can't kill)."""
    if dmg > 0 and p.equipment.get("ring") == "ring of recoil" and m["cur"] > 1:
        m["cur"] -= 1
        print("  " + paint("Your ring of recoil bites back for 1.", "teal"))


def _ring_of_life(p):
    """At a tenth of your health, a ring of life whisks you to safety."""
    if p.equipment.get("ring") != "ring of life":
        return False
    if p.hp <= 0 or p.hp > max(1, p.max_hp // 10):
        return False
    p.equipment["ring"] = None
    p.combat = None
    _clear_status(p)
    banner("RING OF LIFE", color="bgreen", line_color="green")
    say("The ring flares, crumbles to dust — and whisks you to Lumbridge, "
        "alive.", "bgreen", "bold")
    p.location = "lumbridge_castle"
    return True


def _resolve_monster_hit(p, m):
    """Monster swings at the player. Prints, drains prayer. Returns 'died' or None."""
    if m.pop("stunned", None):           # dazed by Torag's hammers etc.
        print("  " + paint(f"The {m['name']} reels, dazed — it misses its "
                           "turn!", "teal"))
        return None
    if m.get("boss"):
        handler = BOSS_TURN.get(m["name"])
        if handler:
            return handler(p, m)        # varied boss attacks (e.g. KBD breaths)
    if m.get("dragonfire") and random.random() < 0.30:
        say(f"The {m['name']} rears back and BREATHES FIRE!", "orange", "bold")
        dmg = _dragonfire_adjust(p, random.randint(5, 18))
        p.hp -= dmg
        print("  " + paint(f"The flames wash over you for {dmg}.", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        return "died" if p.hp <= 0 else None
    atype = _monster_atk_type(m)
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    p_def_roll = _player_def_roll(p, atype)
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, m["max_hit"])
        prot = "magic" if atype == "magic" else \
            ("ranged" if atype == "ranged" else "melee")
        if p.prayer_protects(prot):
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        hpbar = "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0), p.max_hp, 18)
        if dmg == 0:
            print("  " + paint(f"The {m['name']}'s blow grazes you. (0)", "grey")
                  + hpbar)
        else:
            print("  " + paint(f"The {m['name']} hits you for {dmg}.", "bred")
                  + hpbar)
        if p.hp > 0:
            _player_recoil(p, m, dmg)
            if dmg > 0 and getattr(p, "venge", False) and m["cur"] > 0:
                p.venge = False              # Vengeance: one rebound per cast
                vd = max(1, int(dmg * 0.75))
                m["cur"] -= vd
                print("  " + paint(f"\"Taste vengeance!\" — {vd} damage "
                                   "rebounds!", "bmagenta", "bold"))
            eff = MONSTER_EFFECTS.get(m["name"])
            if eff:
                eff(p, m, dmg)
    else:
        print("  " + paint(f"You block the {m['name']}.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


def _victory(p, m):
    if m.get("boss"):
        play_boss_death(m["name"])
    else:
        show_art(ART_VICTORY, "gold", center=True)
    say(f"You have defeated the {m['name']}!", "bgreen", "bold")
    p.kills = getattr(p, "kills", 0) + 1
    log = getattr(p, "kill_log", None)
    if log is None:
        log = p.kill_log = {}
    log[m["name"]] = log.get(m["name"], 0) + 1
    if log[m["name"]] in (10, 50, 100, 500, 1000):
        say(f"  Bestiary: {log[m['name']]} {m['name']} kills!", "bcyan")
    if m.get("boss"):
        bs = getattr(p, "bosses", [])
        if m["name"] not in bs:
            bs.append(m["name"])
        p.bosses = bs
    _award_combat_xp(p, m["hp"])
    _roll_drops(p, m)
    if p.hp < p.max_hp:          # a kill restores some HP (scales with level)
        heal = max(1, p.max_hp // 12)
        p.hp = min(p.max_hp, p.hp + heal)
        print("  " + paint(f"You recover {heal} HP from the victory.", "grey"))


def fight_auto(p, mname):
    """Auto-resolve a whole fight (no eating / prayer switching mid-fight).

    Returns 'won', 'died', or 'noattack'."""
    m = _new_monster(mname)
    if mname in MONSTER_ART:
        show_art(MONSTER_ART[mname], "bred")
    else:
        fam = _fallback_art(mname)
        show_art(fam or ART_SWORDS, "bred" if fam else "grey")
    lvl = m.get("level")
    lbl = f"{mname.upper()}" + (f"  (lvl {lvl})" if lvl else "") + "  (auto)"
    banner(lbl, color="bred", line_color="red")
    print("  " + paint(f"{mname}: ", "white")
          + bar_meter(m["cur"], m["hp"], 18, fill_color="bred"))
    sp = SPECIAL_ATTACKS.get(p.equipment.get("weapon"))
    if sp and getattr(p, "spec_energy", 100) >= sp["cost"]:
        r = _do_special(p, m)               # open with your special, like a pro
        if r == "won":
            _victory(p, m)
            return "won"
    while m["cur"] > 0 and p.hp > 0:
        r = _resolve_player_hit(p, m)
        if r == "noattack":
            return "noattack"
        if r == "won":
            break
        if _resolve_monster_hit(p, m) == "died":
            return "died"
        if _ring_of_life(p):
            return "fled"
    if p.hp <= 0:
        return "died"
    _victory(p, m)
    return "won"


# ---- interactive (turn-based) combat -------------------------------------
def _combat_prompt(p):
    m = p.combat
    print()
    print("  " + paint(f"{m['name']}: ", "white")
          + bar_meter(max(m["cur"], 0), m["hp"], 18, fill_color="bred")
          + paint("    You: ", "white") + bar_meter(max(p.hp, 0), p.max_hp, 14)
          + paint(f"  Pray {int(p.prayer_points)}/{int(p.prayer_max())}",
                  "bmagenta"))
    status = []
    if getattr(p, "poison", 0) > 0:
        status.append(paint(f"poisoned ({p.poison})", "bgreen"))
    if getattr(p, "frozen", False):
        status.append(paint("frozen", "bcyan"))
    if getattr(p, "stat_drain", None):
        status.append(paint(f"-{max(p.stat_drain.values())} stats", "bblue"))
    if getattr(p, "stat_boost", None):
        status.append(paint(f"+{max(p.stat_boost.values())} boost", "lime"))
    if status:
        print("  " + paint("Status: ", "grey") + ", ".join(status))
    foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
    pots = [i for i in p.inventory if ITEMS.get(i, {}).get("potion")]
    if p.max_hp and p.hp / p.max_hp <= 0.30 and p.hp > 0:
        warn = "⚠ Low HP! "
        warn += "Eat to heal, or flee!" if foods else "No food left — flee!"
        print("  " + paint(warn, "bred", "bold"))
    food_hint = f" ({foods[0]})" if foods else ""
    drink_hint = f" ({pots[0]})" if pots else ""
    pray_hint = f" [{', '.join(p.active_prayers)}]" if p.active_prayers else ""
    sp = SPECIAL_ATTACKS.get(p.equipment.get("weapon"))
    spec_hint = ""
    if sp:
        e = int(getattr(p, "spec_energy", 100))
        spec_hint = f" · spec {sp['name']} ({e}%/{sp['cost']}%)"
    print("  " + paint("Your move: ", "bcyan")
          + paint(f"attack{spec_hint} · eat{food_hint} · drink{drink_hint}"
                  f" · pray{pray_hint} · flee", "grey"))


def _start_combat(p, mname):
    p.combat = _new_monster(mname)
    if p.combat.get("boss"):
        play_boss_intro(mname)
    elif mname in MONSTER_ART:
        show_art(MONSTER_ART[mname], "bred")
    else:
        fam = _fallback_art(mname)      # family silhouette beats bare swords
        show_art(fam or ART_SWORDS, "bred" if fam else "grey")
    lvl = p.combat.get("level")
    title = f"{mname.upper()}" + (f"  (lvl {lvl})" if lvl else "")
    banner(title, color="bred", line_color="red")
    weak = p.combat.get("weakness")
    if weak:
        hint = "" if p.style != "melee" else \
            paint(f"  (try 'style {weak}')" if weak in ("stab", "slash", "crush")
                  else "", "grey")
        print("  " + paint(f"Weakness: {weak}", "byellow") + hint)
    print("  " + paint("Style: ", "grey")
          + paint(p.style, STYLE_COLOR.get(p.style, "white"), "bold")
          + paint(f" / {getattr(p, 'attack_type', 'slash')}", "grey")
          + paint("   ('auto' fights with 'fight <foe> auto')", "grey"))
    if _style_atk_bonus(p) < 0:        # off-style gear sabotages accuracy
        print("  " + paint(f"⚠ Your gear has poor {p.style} attack — expect "
                           f"misses. Wear {p.style} gear (see 'equipment').",
                           "byellow"))
    _combat_prompt(p)


def _end_combat_victory(p):
    m = p.combat
    p.combat = None
    _clear_status(p)
    _victory(p, m)
    _quest_on_kill(p, m["name"])


def combat_action(p, raw):
    """Handle one command while the player is in interactive combat."""
    m = p.combat
    parts = raw.strip().split(maxsplit=1)
    verb = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    verb = {"1": "attack", "2": "eat", "3": "pray", "4": "flee",
            "5": "spec",
            "a": "attack", "hit": "attack", "run": "flee", "escape": "flee",
            "special": "spec", "": "attack"}.get(verb, verb)

    # free, no-cost actions while fighting
    if verb == "style":                 # switching stance is free, as in OSRS
        return cmd_style(p, arg)
    if verb == "autocast":
        return cmd_autocast(p, arg)
    if verb in ("gear", "loadout", "outfit"):   # the OSRS mid-fight swap
        return cmd_gear(p, arg)
    if verb == "autoeat":
        return cmd_autoeat(p, arg)
    if verb == "quests":
        return cmd_quests(p, "")
    if verb in ("goal", "goals"):
        return cmd_goal(p, "")
    if verb == "task":
        return cmd_task(p, "")
    if verb in ("stats", "skills"):
        return cmd_stats(p, "")
    if verb in ("inventory", "inv", "i"):
        return cmd_inventory(p, "")
    if verb in ("equipment", "worn"):
        return cmd_equipment(p, "")
    if verb == "examine":
        return cmd_examine(p, arg)
    if verb in ("look", "l"):
        return _combat_prompt(p)
    if verb in ("help", "?", "commands"):
        return say("In combat: attack · spec · eat [food] · pray [name] · "
                   "flee. (style/gear/stats/inventory are free to check "
                   "or switch.)", "grey")
    if verb == "pray" and not arg:
        return cmd_pray(p, "")          # checking prayers is free

    # status effects tick at the start of a turn-consuming action
    if verb in ("attack", "spec", "eat", "pray", "flee") and getattr(p, "poison", 0) > 0:
        _tick_poison(p)
        if p.hp <= 0:
            p.combat = None
            _clear_status(p)
            return _handle_death(p)

    # actions that take your turn (monster then retaliates)
    if verb == "attack":
        if getattr(p, "frozen", False):
            p.frozen = False            # one wasted attack, then you thaw
            say("You are frozen solid — your strike fails! You shatter the ice.",
                "bcyan")
        else:
            r = _resolve_player_hit(p, m)
            if r == "noattack":
                return                  # couldn't attack (no ammo/runes)
            if r == "won":
                return _end_combat_victory(p)
    elif verb == "spec":
        if getattr(p, "duel", None) and p.duel["rule"] == "no specials":
            return say("Duel rules: NO SPECIALS. Win with plain steel.",
                       "bred")
        if getattr(p, "frozen", False):
            p.frozen = False            # one wasted attack, then you thaw
            say("You are frozen solid — your special fails! You shatter the "
                "ice.", "bcyan")
        else:
            r = _do_special(p, m)
            if r == "noattack":
                return                  # no spec / no energy: turn not spent
            if r == "won":
                return _end_combat_victory(p)
    elif verb == "eat":
        if getattr(p, "duel", None) and p.duel["rule"] == "no food":
            return say("Duel rules: NO FOOD. The crowd would riot.", "bred")
        foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
        food = arg or (foods[0] if foods else "")
        if food and not p.has(food):
            near = [f for f in foods if food in f]   # 'eat trout' finds cooked trout
            food = near[0] if near else food
        if not food or not p.has(food):
            return say("You have no food to eat!", "grey")
        if p.hp >= p.max_hp:
            return say("You're already at full health — save the food.",
                       "grey")
        cmd_eat(p, food)
    elif verb == "drink":
        pots = [i for i in p.inventory if ITEMS.get(i, {}).get("potion")]
        if not (arg or pots):
            return say("You have no potions to drink!", "grey")
        cmd_drink(p, arg)
    elif verb == "pray":
        if getattr(p, "duel", None) and p.duel["rule"] == "no prayer":
            return say("Duel rules: NO PRAYER. The gods are not invited.",
                       "bred")
        before = list(p.active_prayers)
        cmd_pray(p, arg)
        if list(p.active_prayers) == before and arg not in PRAYERS:
            return                      # invalid prayer name: no turn lost
    elif verb == "flee":
        if getattr(p, "frozen", False):
            say("You can't flee — you're frozen solid!", "bcyan")
        elif random.random() < 0.55:
            p.combat = None
            _clear_status(p)
            if getattr(p, "duel", None):
                say("You yield the duel!", "byellow")
                return _duel_loss(p)
            return say("You break off and flee the battle!", "byellow")
        else:
            say("You fail to escape!", "grey")
    else:
        return say("You're locked in combat! Use: attack, spec, eat, pray, "
                   "or flee.", "bred")

    # monster's turn
    if _resolve_monster_hit(p, m) == "died":
        p.combat = None
        if getattr(p, "duel", None):
            return _duel_loss(p)
        return _handle_death(p)
    if getattr(p, "autoeat", True) and p.hp <= p.max_hp * 0.4:
        _autoeat_bite(p)                  # reflexes kick in when badly hurt
    if _ring_of_life(p):                  # emergency escape at low hp
        return
    _combat_prompt(p)


def _award_combat_xp(p, mhp):
    cxp = mhp * 4
    if p.style == "melee":
        focus = getattr(p, "train", "shared")
        if focus in ("attack", "strength", "defence"):
            p.gain_xp(focus, cxp)          # aimed training
        else:
            for s in ("attack", "strength", "defence"):
                p.gain_xp(s, cxp / 3)
    elif p.style == "ranged":
        p.gain_xp("ranged", cxp)
    elif p.style == "magic":
        spell = SPELLS.get(p.autocast)
        if spell:
            p.gain_xp("magic", spell["xp"] * 2)
    p.gain_xp("hitpoints", cxp / 3)


def _roll_drops(p, m):
    got = False
    total = 0
    for item, lo, hi, chance in m["drops"]:
        if random.random() < chance:
            qty = random.randint(lo, hi)
            if item == "coins" and p.equipment.get("ring") == "ring of wealth":
                qty = int(qty * 1.25)     # the rich get richer
            if qty > 0:
                p.add(item, qty)
                value = ITEMS.get(item, {}).get("value", 0) * qty
                total += value
                if item != "coins" and value >= 5000:   # rare/valuable highlight
                    print("  " + paint(f"✦ Valuable drop: {item} x{qty}!",
                                       "gold", "bold"))
                else:
                    tint = "gold" if item == "coins" else "byellow"
                    print("  " + paint(f"Loot: {item} x{qty}", tint))
                got = True
    if not got:
        say("  No loot this time.", "grey")
    elif total > 0:
        print("  " + paint(f"Loot value: {total:,} gp", "grey"))


def _consume_runes(p, runes):
    # staves provide unlimited runes of their element
    provided = set()
    for slot, item in p.equipment.items():
        if item and "provides" in ITEMS.get(item, {}):
            provided.add(ITEMS[item]["provides"])
    needed = {r: q for r, q in runes.items() if r not in provided}
    for r, q in needed.items():
        if not p.has(r, q):
            return False
    for r, q in needed.items():
        p.take(r, q)
    return True


# helper bound to Player (ammo count)
def _count_ammo(self):
    a = self.equipment["ammo"]
    return self.count(a) if a else 0


Player.count_ammo = _count_ammo


