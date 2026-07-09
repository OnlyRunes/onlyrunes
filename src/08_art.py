# ===========================================================================
#  TEXT ART
# ===========================================================================

LOGO = r"""
   ____                  _____
  |  _ \ _   _ _ __   ___/ ____|  ___ __ _ _ __   ___
  | |_) | | | | '_ \ / _ \____ \ / __/ _` | '_ \ / _ \
  |  _ <| |_| | | | |  __/____) | (_| (_| | |_) |  __/
  |_| \_\\__,_|_| |_|\___|_____/ \___\__,_| .__/ \___|
        T E X T   A D V E N T U R E       |_|
"""

ART_SWORDS = r"""
        ,                       ,
       /|          _____        |\
      | |        .'     '.      | |
      |/        / Battle! \      \|
   >==[]========(  vs  )========[]==<
              \         /
               '._____.'
"""

ART_LEVELUP = r"""
       .    *        .   ___   .       *      .
   *      .     LEVEL UP!  / _ \    .      *
       .------------------| | | |------------------.
        '*.   .  *    .    \_\_/    *   .   .*'
"""

ART_VICTORY = r"""
   __      ___ ___ _____ ___  _____   __
   \ \    / /_ _/ __|_   _/ _ \| _ \ \ / /
    \ \/\/ / | | (__  | || (_) |   /\ V /
     \_/\_/ |___\___| |_| \___/|_|_\ |_|
"""

ART_DEATH = r"""
        _____
      .'     '.        Oh dear, you are dead!
     /  x   x  \
    |    ___    |      You wake up in Lumbridge...
     \  \___/  /
      '._____.'
"""

ART_QUEST = r"""
    .-----------------------------------------.
   ( ~ ~ ~  Q U E S T   C O M P L E T E  ~ ~ ~ )
    '-----------------------------------------'
"""

# ---- Boss animation frames -----------------------------------------------
# The KBD's varied attacks (faithful to OSRS): melee + four dragonfire breaths,
# each with its own short animation played on the dragon's turn. (The dragon
# itself is the braille KBD_ART further down.)
KBD_BR_FIRE1 = r"""
               (vv) (vv) (vv)
                }    |    {
                ( ~≈≈≈≈~ )
"""
KBD_BR_FIRE2 = r"""
               (VV) (VV) (VV)
              }}}  \|/  {{{
           (  ~≈≈≈ FIRE ≈≈≈~  )
            ~~≈≈≈≈≈≈≈≈≈≈≈≈≈~~
"""
KBD_BR_BITE1 = r"""
               (oo) (oo) (oo)
               /VV\ /VV\ /VV\
              >=== CHOMP ===<
"""
KBD_BR_BITE2 = r"""
               (><) (><) (><)
               \WW/ \WW/ \WW/
             >>=== CRUNCH ===<<
"""
KBD_BR_SHOCK1 = r"""
               (oo) (oo) (oo)
                \z/  \z/  \z/
               z ~=ZAP=~ z
"""
KBD_BR_SHOCK2 = r"""
               (@@) (@@) (@@)
              \_z_\ /_z_/ z
             z~=*= SHOCK =*=~z
"""
KBD_BR_ICE1 = r"""
               (oo) (oo) (oo)
                *.   .*   *.
               *.* . . *.*
"""
KBD_BR_ICE2 = r"""
               (oo) (oo) (oo)
              .*+. *+* .+*.
             *+* FREEZE! +*+
              .  *  .  *  .
"""
KBD_BR_POISON1 = r"""
               (oo) (oo) (oo)
                o O  o O  O o
               ( ~ o ~ o ~ )
"""
KBD_BR_POISON2 = r"""
               (oo) (oo) (oo)
              O o O  o  O o O
            ( ~o~ POISON ~o~ )
             ~ . ~ . ~ . ~ .
"""

# Count Draynor: a giant vampyre that flares its wings and bares its fangs.
BAT_CALM = r"""
       /\                 /\
      /  \    _     _    /  \
     /    \__/ \   / \__/    \
     \    (  o  ) (  o  )    /
      \    \___/   \___/    /
       \______\_____/______/
"""
BAT_FANG = r"""
     \/\                 /\/
      \ \    _     _    / /
       \ \__/ \   / \__/ /
        (  O  ) ^ (  O  )
         \VVV/  |  \VVV/
          \____\|/____/
"""
BAT_DIE1 = r"""
       /\                 /\
      /  \    _     _    /  \
     /    \__/ \   / \__/    \
     \    (  x  ) (  x  )    /
      \    \___/   \___/    /
       \______\_____/______/
"""
BAT_DIE2 = r"""
      ^v^       ^v^      ^v^
          ^v^       ^v^
       a shrieking cloud of bats
"""

# Fallback for any boss without bespoke art.
GEN_ROAR = r"""
       \  |  /        R O A R !
     --=[ >< ]=--
       /  |  \
"""


# King Black Dragon: a three-headed braille dragon (fine dots via JuliaMono).
KBD_ART = '''
                                 ⣠⠴⠋⠁⢀⡼ ⢀⡴⠞⠉⠁  ⢀⡤⠊
                               ⣰⢿⠁  ⢠⢾⣤⠞⠉   ⢀⣠⠞⠋
                             ⣠⡾⠵⠎⠉⣉⡷⠿⣏⠁ ⢸⠃⢀⡴⠛⠳⢤⡀
                         ⣰⣶⠖⠋⣠⢶⠏⣀⣼⡥  ⠈⠳⢤⣟⣠⡟⠁  ⢀⣩⡷⠔
                        ⡼⠁⠁⣠⠞⠁⠘⠋⢁⡟  ⣠   ⣠⡴⣷⠖⠒⠋⠉
                       ⣴⠟⢠⠞⠁ ⢀⣀⣴⠏  ⢰⡷ ⠳⡏⠁⢠⡇     ⣠⠔
                      ⢀⡇ ⣾ ⢀⣾⣟⣿⡽    ⣷  ⢹  ⢣⡀⣀⡤⠖⠋⠁
                    ⣀⢠⠞⠁ ⠉⠠⠟⢛⡿⠋⢀⡤⢶⣶⡞⠁  ⡿⠴⣄ ⣿⠁⠙⣆
                  ⢀⣼⢹⡯    ⣀ ⡞ ⢀⡼⣟⣆⡟   ⢠⣇⡴⠛⠛⢧⡀ ⠈⢧⡀
                  ⡏⠘⠋⣡⡔ ⣠⣞⣭⣤⠤⠤⠶⢿⣆⣷⠃   ⢠⢣⠃   ⠹⡆  ⢸⡂
                  ⣧⡀ ⠃⢀⣠⣾⣿⡺⣳⠖⠚⠉⠉⠈⡏    ⣨⠟⠚⠋⠉⠉⠓⠓   ⢣
                   ⠙⣿⣿⣿⣿⢮⣧⣾⠁ ⣠⠤⠭⠭⡇  ⢠⠞⠑⢦⡀        ⠈
                         ⠈⠹⡄⢀⣿⡆ ⣾⡇ ⣴⠋   ⠙⣦⡀
               ⣠⠴⠋⠁⢀⡼ ⣀⣴⢾⣟⣻⠵⠋⣹⡧⢪⣯⡇⢰⠃⠈⠢⣄  ⢸⣿⡙⠶⣄ ⠸⣄ ⠉⠳⢤⡀
             ⣰⢿⠁  ⢠⢾⣤⣾⠟⠋⣩⣵⢃⣠⣿⣿⣿⣺⡿⢀⡏   ⠈⠛⢦⣸⡇⢳⡀⠈⠙⢦⣼⢦   ⢹⢷⡀
           ⣠⡾⠵⠎⠉⣉⡷⠿⣏⠙⠻⢽⠿⢿⡿⠛⠳⢼⣿⣛⣋⣁⡼     ⣠⠴⡿⠳⣄⢷⢻  ⢉⡿⠷⣏⡉⠉⠶⠽⣦⡀
       ⣰⣶⠖⠋⣠⢶⠏⣀⣼⡥  ⠈⠳⢤⣟⣠⡟⠁  ⢀⣩⡷⠔    ⠐⠴⣯⣁⠚⠁ ⠙⣿⣘⣧⠴⠋  ⠠⣽⣄⡈⢷⢦⡈⠓⢶⣶⡀
      ⡼⠁⠁⣠⠞⠁⠘⠋⢁⡟  ⣠   ⣠⡴⣷⠖⠒⠋⠉          ⠈⠉⠓⠒⢶⡷⣤⡀  ⢠⡀ ⠘⣇⠉⠛ ⠙⢦⡀⠁⠹⡄
     ⣴⠟⢠⠞⠁ ⢀⣀⣴⠏  ⢰⡷ ⠳⡏⠁⢠⡇     ⣠⠔    ⠐⢤⡀     ⣧ ⠉⡷⠃⠰⣷  ⠈⢷⣄⣀  ⠙⢦⠘⢷⡄
    ⢀⡇ ⣾ ⢀⣾⣟⣿⡽    ⣷  ⢹  ⢣⡀⣀⡤⠖⠋⠁       ⠉⠓⠦⣄⡀⣠⠃ ⢸⠁ ⢰⡇   ⠸⣽⣟⣿⣆ ⢸⡆ ⣇
  ⣀⢠⠞⠁ ⠉⠠⠟⢛⡿⠋⢀⡤⢶⣶⡞⠁  ⡿⠴⣄ ⣿⠁⠙⣆          ⢀⡞⠁⢹⡇⢀⡴⠼⡇  ⠙⣶⣶⠦⣄⠈⠻⣟⠛⠧⠈⠁ ⠙⢦⢀⡀
⢀⣼⢹⡯    ⣀ ⡞ ⢀⡼⣟⣆⡟   ⢠⣇⡴⠛⠛⢧⡀ ⠈⢧⡀       ⣠⠏  ⣠⠟⠛⠳⣄⣧   ⠘⣇⣞⡿⣄ ⠘⡆⢀⡀   ⠨⣿⢹⣄
⡏⠘⠋⣡⡔ ⣠⣞⣭⣤⠤⠤⠶⢿⣆⣷⠃   ⢠⢣⠃   ⠹⡆  ⢸⡂     ⣺   ⡾⠁   ⢣⢣    ⢳⣇⣾⠷⠦⠤⢤⣬⣝⣦⡀⠐⣤⡉⠛⠈⡇
⣧⡀ ⠃⢀⣠⣾⣿⡺⣳⠖⠚⠉⠉⠈⡏    ⣨⠟⠚⠋⠉⠉⠓⠓   ⢣    ⢠⠃  ⠐⠓⠋⠉⠉⠛⠚⢯⡀   ⠈⡏⠈⠉⠙⠒⢶⡻⣺⣿⣦⣀ ⠃ ⣠⡇
 ⠙⣿⣿⣿⣿⢮⣧⣾⠁ ⣠⠤⠭⠭⡇  ⢠⠞⠑⢦⡀        ⠈    ⠈         ⣠⠖⠙⢦   ⡯⠭⠥⢤⡀ ⢹⣦⣯⢾⣿⣿⣿⡟⠁
       ⠈⠹⡄⢀⣿⡆ ⣾⡇ ⣴⠋   ⠙⣦⡀                   ⣠⡞⠁  ⠈⢳⡄ ⣿⡆ ⣾⣇ ⡼⠉
    ⣀⣠⢴⣖⣺⠵⠋⣹⡇⢠⣯⡇⢰⠃     ⢸⣷⡀                 ⣰⣿      ⢳ ⣯⣧ ⣿⡉⠳⢽⣒⣶⢤⣀⡀
  ⢠⣾⠟⠋⣩⣵⠃ ⣿⣿⣿⣺⡿⢀⡏      ⢸⡇⢳⡀               ⣰⠃⣿      ⠈⣇⠸⣿⣺⣿⣿⡇ ⢳⣭⡉⠛⢿⣦
  ⠘⠻⠭⠽⠿⠛⠁ ⠸⢿⣛⣋⣁⡼       ⡼  ⢷              ⢰⠇ ⠸⡄      ⠸⣄⣉⣛⣻⠿  ⠙⠻⠿⠭⠽⠛
                      ⠚⠁  ⠘              ⠘   ⠙⠂
'''


def _kbd_intro(name):
    return [_tint(KBD_ART, "grey"), _tint(KBD_ART, "bred"),
            _tint(KBD_ART, "bred", "bold"), _tint(KBD_ART, "grey"),
            _tint(KBD_ART, "bred", "bold")]


def _kbd_death(name):
    return [_tint(KBD_ART, "bred"), _tint(KBD_ART, "grey"),
            _tint(KBD_ART, "grey", "dim")]


def _kbd_br_fire(_=None):
    return [_tint(KBD_BR_FIRE1, "orange", "bold"),
            _tint(KBD_BR_FIRE2, "byellow", "bold"),
            _tint(KBD_BR_FIRE2, "bred", "bold")]


def _kbd_br_bite(_=None):
    return [_tint(KBD_BR_BITE1, "grey"), _tint(KBD_BR_BITE2, "bred", "bold")]


def _kbd_br_shock(_=None):
    return [_tint(KBD_BR_SHOCK1, "bblue", "bold"),
            _tint(KBD_BR_SHOCK2, "bcyan", "bold"),
            _tint(KBD_BR_SHOCK2, "bwhite", "bold")]


def _kbd_br_ice(_=None):
    return [_tint(KBD_BR_ICE1, "bcyan"), _tint(KBD_BR_ICE2, "bwhite", "bold"),
            _tint(KBD_BR_ICE1, "bcyan", "bold")]


def _kbd_br_poison(_=None):
    return [_tint(KBD_BR_POISON1, "green"), _tint(KBD_BR_POISON2, "bgreen", "bold"),
            _tint(KBD_BR_POISON1, "green", "bold")]


# Each KBD turn picks one of these (weighted). Mults scale its base max hit;
# normal dragonfire hits hardest, the elemental breaths trade damage for an
# effect (faithful to OSRS: shock drains stats, ice freezes, poison poisons).
KBD_ATTACKS = [
    {"key": "fire",   "label": "a torrent of dragonfire", "verb": "unleashes",
     "color": ("orange", "bold"),  "builder": _kbd_br_fire,   "mult": 1.4, "w": 3},
    {"key": "melee",  "label": "its three fanged maws",   "verb": "snaps with",
     "color": ("bred", "bold"),    "builder": _kbd_br_bite,   "mult": 1.0, "w": 3},
    {"key": "shock",  "label": "a crackling shock breath", "verb": "breathes",
     "color": ("bblue", "bold"),   "builder": _kbd_br_shock,  "mult": 0.85, "w": 2},
    {"key": "ice",    "label": "a freezing ice breath",    "verb": "breathes",
     "color": ("bcyan", "bold"),   "builder": _kbd_br_ice,    "mult": 0.8, "w": 2},
    {"key": "poison", "label": "a cloud of poison breath", "verb": "breathes",
     "color": ("bgreen", "bold"),  "builder": _kbd_br_poison, "mult": 0.8, "w": 2},
]


def _count_intro(name):
    return [_tint(BAT_CALM, "grey"), _tint(BAT_FANG, "bred", "bold"),
            _tint(BAT_CALM, "bmagenta"), _tint(BAT_FANG, "bred", "bold"),
            _tint(BAT_CALM, "bmagenta", "bold")]


def _count_death(name):
    return [_tint(BAT_DIE1, "bred"), _tint(BAT_DIE1, "grey"),
            _tint(BAT_DIE2, "bmagenta", "dim")]


def _generic_boss_intro(name):
    # a boss with a portrait gets its own art flashed; GEN_ROAR otherwise
    art = MONSTER_ART.get(name, GEN_ROAR)
    return [_tint(art, "grey"), _tint(art, "bred", "bold"),
            _tint(art, "byellow", "bold"), _tint(art, "bred", "bold")]


def _generic_boss_death(name):
    art = MONSTER_ART.get(name, GEN_ROAR)
    return [_tint(art, "bred"), _tint(art, "grey", "dim")]


# Obor, the Hill Giant boss — a braille hill giant (image->braille via JuliaMono).
OBOR_ART = '''
            ⢀⡶⠲⢦⡀
            ⣾⣀⣀⣀⣳
            ⡿⠘⠰⠘⣸⡆
         ⣠⡴⠋⠁ ⢀⡾⠁⠳⣤⡀
     ⣤⠶⠚⠋⠁    ⠈    ⠙⠶⣄
     ⡇               ⠈⠳⢤⡀
     ⡇                  ⠙⢦
     ⢻                   ⢸
     ⠸⣇                  ⢻⡀
      ⠈⠳⢤⣀       ⢀⣀⣀⡀    ⢸⣇
       ⢀⣾⣿        ⢹⣿⡗⣆   ⢸⣿
       ⢹⠉⠉        ⣾⡟ ⠹⡄   ⣿
       ⢸⡆        ⢠⣿⠁  ⠹⡄ ⢀⡇
        ⢧⣠⡄⢀⣀⣀⣀⣠⣤⣤⣼⣇   ⡟  ⣇
 ⣴⣤⣤⣤⣄ ⢀⡟⠈⠍⡿⣿⣿⣿⣿⣿⣿⡟⠛⣧ ⢸⡇  ⢸⡆
⠘⣿⣿⣿⣿⣿⣧⣼⣁⢌⣾⣿⣿⡿⣿⣿⣿⣿⡇ ⣿ ⠘⡇  ⡾
 ⠈⠙⠛⠿⠿⠿⡿⣳⣿⣿⠿⢃⣼⣿⣿⣿⣿⡇ ⣿  ⢷ ⣸⠃
       ⢹⣿⢿⣉⢠⣾⣿⡿⢋⡍⠙⠃ ⢹ ⣠⠞ ⡇
       ⢸⡇⠈⣶⣿⢿⡟ ⣞    ⠘⠘⢁⣀ ⢿
       ⢸⡇ ⠛⠁⣼⠁ ⢹⡄   ⢀⣠⠏⣸ ⠘⣇
       ⢨⡇  ⠸⡇   ⣇   ⢸⡀⢴⣃⣠⠶⠛
       ⡾    ⣧   ⢿⡀  ⠈⢳⡀⠈⠁
       ⢷⠄ ⣀⣠⣿⡇  ⢈⡇   ⣸⣿⡄
       ⠸⡦⣾⣿⣿⡟   ⠘⣷⣄⠙⢸⣿⡿
        ⢷⡙⣿⡿     ⠸⣿⣇⣮⣿⠇
        ⢸⠷⣸⠁      ⠹⣼⣿⣿
       ⣠⡞⢰⣾⡄       ⢻⡉⠙⣦
   ⣠⣴⣾⣿⣿⣟⣼⡿⠟       ⣼⣅⣀⢸⣧
   ⠘⠶⠽⠿⠟⠉        ⢀⣼⣿⣿⣿⣿⠛⠁
                ⠐⠚⠶⠤⠶⠶⠇
'''


def _obor_intro(name):
    return [_tint(OBOR_ART, "byellow"), _tint(OBOR_ART, "gold", "bold"),
            _tint(OBOR_ART, "byellow", "bold"), _tint(OBOR_ART, "gold", "bold"),
            _tint(OBOR_ART, "byellow", "bold")]


def _obor_death(name):
    return [_tint(OBOR_ART, "gold"), _tint(OBOR_ART, "brown"),
            _tint(OBOR_ART, "grey", "dim")]


def _obor_smash(_=None):
    return [_tint(OBOR_ART, "gold", "bold"), _tint(OBOR_ART, "byellow", "bold")]


def _obor_slam_fx(_=None):
    return [_tint(OBOR_ART, "byellow", "bold"), _tint(OBOR_ART, "gold", "bold")]


def _obor_rock_fx(_=None):
    return [_tint(OBOR_ART, "gold", "bold"), _tint(OBOR_ART, "orange", "bold")]


def _count_claw(_=None):
    return [_tint(BAT_CALM, "bmagenta"), _tint(BAT_FANG, "bred", "bold")]


def _count_bite(_=None):
    return [_tint(BAT_FANG, "bmagenta", "bold"), _tint(BAT_FANG, "bred", "bold")]


def _count_swarm(_=None):
    return [_tint(BAT_DIE2, "bmagenta", "bold"), _tint(BAT_DIE2, "bred", "bold")]


# Boss-attack effects (called with the player, monster, and damage dealt).
def _obor_stagger(p, m, dmg):
    sd = getattr(p, "stat_drain", None)
    if sd is None:
        sd = p.stat_drain = {}
    sd["defence"] = sd.get("defence", 0) + 3
    print("  " + paint("The impact rattles your guard! (-3 defence)", "orange"))


def _count_lifesteal(p, m, dmg):
    heal = max(1, dmg // 2)
    m["cur"] = min(m["hp"], m["cur"] + heal)
    print("  " + paint(f"The Count drinks your blood and heals {heal}!", "bmagenta")
          + "  " + bar_meter(max(m["cur"], 0), m["hp"], 18, fill_color="bred"))


def _count_disorient(p, m, dmg):
    sd = getattr(p, "stat_drain", None)
    if sd is None:
        sd = p.stat_drain = {}
    sd["attack"] = sd.get("attack", 0) + 2
    print("  " + paint("The swarm claws and screeches — you're disoriented! "
                       "(-2 attack)", "bmagenta"))


# Movesets: each turn picks one (weighted). mult scales the boss's max hit;
# atype is the damage type (vs your defence + prayer); effect fires on a hit.
OBOR_ATTACKS = [
    {"label": "his giant club", "verb": "smashes down with",
     "color": ("brown", "bold"), "builder": _obor_smash, "mult": 1.4, "w": 3,
     "atype": "crush"},
    {"label": "the ground in a thunderous stomp", "verb": "slams",
     "color": ("orange", "bold"), "builder": _obor_slam_fx, "mult": 1.0, "w": 2,
     "atype": "crush", "effect": _obor_stagger},
    {"label": "a massive boulder", "verb": "hurls", "color": ("byellow", "bold"),
     "builder": _obor_rock_fx, "mult": 1.1, "w": 2, "atype": "ranged"},
]
COUNT_ATTACKS = [
    {"label": "his raking claws", "verb": "slashes with",
     "color": ("bred", "bold"), "builder": _count_claw, "mult": 1.0, "w": 3,
     "atype": "slash"},
    {"label": "his fangs, drinking deep", "verb": "bites with",
     "color": ("bmagenta", "bold"), "builder": _count_bite, "mult": 0.9, "w": 2,
     "atype": "stab", "effect": _count_lifesteal},
    {"label": "a shrieking swarm of bats", "verb": "summons",
     "color": ("bmagenta", "bold"), "builder": _count_swarm, "mult": 0.8, "w": 2,
     "atype": "crush", "effect": _count_disorient},
]


BOSS_INTRO = {"king black dragon": _kbd_intro, "count draynor": _count_intro,
              "obor": _obor_intro}
BOSS_DEATH = {"king black dragon": _kbd_death, "count draynor": _count_death,
              "obor": _obor_death}


def play_boss_intro(name):
    """Dramatic entrance animation when a boss fight begins."""
    say("The ground shudders — something ancient stirs.", "grey", "italic")
    builder = BOSS_INTRO.get(name, _generic_boss_intro)
    animate(builder(name), delay=0.16, center=True)


def play_boss_death(name):
    """Death throes animation, finishing on a golden VICTORY."""
    builder = BOSS_DEATH.get(name, _generic_boss_death)
    animate(builder(name), delay=0.18, center=True)
    show_art(ART_VICTORY, "gold", center=True)


# Small per-monster art shown at the start of a fight.
MONSTER_ART = {
    "goblin": r"""
     ,---.
    ( o o )   a goblin!
     ) ^ (
    /_/ \_\
""",
    "chicken": r"""
      __
     <o )   a chicken
      ( )>
       ""
""",
    "cow": r"""
      ^__^
      (oo)\_______   a cow
      (__)\       )
          ||----w |
""",
    "giant rat": r"""
      (\_/)
     =(o.o)=~   a giant rat
      (")_(")
""",
    "skeleton": r"""
       .-.
      (o.o)   a skeleton
       |=|
      /| |\
""",
    "zombie": r"""
      [o_o]
      /|H|\   a zombie
      _/ \_
""",
    "barbarian": r"""
      \o/
       |  >==O   a barbarian
      / \
""",
    "guard": r"""
      .--.
     |[]|]   a guard
      |  |==|
""",
    "scorpion": r"""
     /\,,/\
    ( o.o )><  a scorpion
     >   <
""",
    "hobgoblin": r"""
     ,-^-.
    ( >.< )   a hobgoblin
     )___(
    /_/ \_\
""",
    "hill giant": r"""
      _____
     ( O O )    a HILL GIANT
     /|   |\
      || ||
""",
    "dark wizard": r"""
       /\
      (oo)    a dark wizard
     <(  )>~*
      /  \
""",
    "count draynor": r"""
      /\_/\
     ( ^_^ )   COUNT DRAYNOR
     (  V  )    ~ a vampyre ~
      """ + '"""' + r"""
""",
}

# The late-game rogues' gallery: superbosses, warlords and quest guardians.
# The generic boss intro/death animations flash whichever of these exists,
# so a new boss only ever needs one piece of art here.
MONSTER_ART.update({
    "kraken": r"""
          .-''''-.
         ( o    o )
          \  __  /        THE KRAKEN rises
       _/\/|/||\|\/\_      from the lightless deep!
      / /\ | || | /\ \
     ~~ ~~ ~ ~~ ~ ~~ ~~
""",
    "cerberus": r"""
      ,_      ,_      ,_
     (o,o)   (o,o)   (o,o)
      )v(     )v(     )v(     CERBERUS —
       \ \____ | ____/ /       three heads, one hunger.
        \____ \|/ ____/
         //   |||   \\
""",
    "thermonuclear smoke devil": r"""
         (  ~~~~  )
       (  ~~~~~~~~  )
      ( ~~ (o)(o) ~~ )     the THERMONUCLEAR SMOKE
       (  ~~~~~~~~  )       DEVIL billows upward!
         \  ~~~~  /
          '------'
""",
    "abyssal sire": r"""
         .-''''''-.
        /  -    -  \
       |  (o)  (o)  |      the ABYSSAL SIRE heaves
        \    __    /        out of the miasma...
      _/|\__/||\__/|\_
     / \|/   ||   \|/ \
""",
    "grotesque guardians": r"""
      /\ /\        /\ /\
     ( o o )      ( o o )
     /| ^ |\      /| ^ |\     DUSK and DAWN —
      |___|        |___|       stone takes wing!
     _|   |_      _|   |_
""",
    "corporeal beast": r"""
        __,--------.__
       /   \      /   \
      | (o) |    | (o) |     the CORPOREAL BEAST —
       \____|____|____/       flesh of pure spirit.
       /|   |||||   |\
      ^^    |||||    ^^
""",
    "chaos elemental": r"""
        .  ~  @  ~  .
       ~  @  \|/  @  ~
      @  ~ --(?)-- ~  @     the CHAOS ELEMENTAL
       ~  @  /|\  @  ~       crackles into being!
        '  ~  @  ~  '
""",
    "scorpia": r"""
       /\_________/\    ,-,
      ( _\       /_ )  ( x )
       / |(o) (o)| \    )-(     SCORPIA — her tail
         |__ v __|     //        arcs overhead!
        //|     |\\ __//
       '' |_|_|_| '''
""",
    "callisto": r"""
        ,--._____,--.
       /    '   '    \
      |  (o)     (o)  |     CALLISTO the great bear
       \     ___     /       rears to full height!
       /|   '---'   |\
      (_|           |_)
""",
    "venenatis": r"""
      \\   //   \\   //
       \\ ((     )) //
        (( \ .. / ))        VENENATIS descends
       //   (oo)   \\        on a dripping strand...
      //   //  \\   \\
           ''    ''
""",
    "vet'ion": r"""
         .-------.
        |  [x x]  |
        |   ___   |       VET'ION, twice-risen
       /|__|   |__|\       champion of the dead!
      | ||       || |
        ||_______||
        /_/     \_\
""",
    "kolodion": r"""
         _/\_       ,
        ( o o )    /|
        /|   |\  *  |      KOLODION raises
       / |___| \    |       his god staff!
         |   |     /
        _|___|_  *
""",
    "dessous": r"""
       /\_______/\
       \  (o o)  /
       /|  ^v^  |\        DESSOUS, vampyre lord,
      / |_______| \        unfolds from his tomb.
     /__|       |__\
""",
    "kamil": r"""
        *   /\   .
         __|  |__
        | [o  o] |  *      KAMIL strides out
      * |________|          of the blizzard!
        /| /\/\ |\   .
       * |/    \| *
""",
    "fareed": r"""
       (  (    )  )
        ) _)__(_ (
       ( | (oo) | )       FAREED — the tomb
        )|      |(         burns around him!
       ( |______| )
          /    \
""",
    "damis": r"""
        .    .    .
         ________
       .| o    o |.       DAMIS coalesces
        |    _   |         from the shadows...
       .|________|.
         /   .   \
""",
})

# Family art: any monster without its own portrait gets its family's
# silhouette (a dragon reads as a dragon), keyword-matched in order.
_FAMILY_ART = [
    (("dragon",), r"""
         /\____/\
        ( o vv o )___
        /|  ^^  |/  /\      a DRAGON — beware
       ( |______|  /  )      its fiery breath!
        \|_|__|_|_/ /
          w      w '
"""),
    (("demon", "devil", "imp"), r"""
        \        /
        (\------/)
        ( o    o )        a DEMON of the
        /|  \/  |\         lower planes!
       ( |______| )
         ^      ^
"""),
    (("spectre", "banshee", "ghast", "ghost", "shade", "draugen",
      "wraith"), r"""
        .-''''''-.
       /  o    o  \
       |     _    |       something COLD
       \    '-'   /        drifts through you...
        '~~~~~~~~'
          ~  ~  ~
"""),
    (("giant", "troll", "ogre", "cyclops", "obor"), r"""
          _______
         /       \
        | [o] [o] |       a hulking BRUTE
        /|   _   |\        blocks the way!
       d |__|_|__| b
         |   |   |
        _|   |   |_
"""),
    (("hound", "wolf", "werewolf", "dog", "jackal"), r"""
         /\      /\
        /  \____/  \
       |  -      -  |     a snarling BEAST —
        \    /\    /       all fangs and hunger!
         \   \/  _/
          '----''
"""),
    (("crab",), r"""
       ,--.       ,--.
      ( () )     ( () )
       \  \_______/  /      a CRAB scuttles
        |   o   o   |        sideways at you!
       /|___________|\
      '-'   '   '   '-'
"""),
    (("kalphite", "scarab", "locust"), r"""
        ______________
       / .----------. \
      | ( (o)    (o) ) |     a KALPHITE clicks
       \ '----++----' /       its mandibles!
       /\/\  |  |  /\/\
         \/  '--'  \/
"""),
    (("horror", "basilisk", "bloodveld", "crawling hand", "experiment",
      "jelly", "turoth", "kurask", "cockatrice"), r"""
        _.-''''''-._
       /  o   o  o  \
      |   o  __  o   |     a nameless HORROR
       \    (__)    /       writhes toward you!
        \|/|\--/|\|/
         '  '  '  '
"""),
    (("jal-", "tz-", "tzhaar"), r"""
         (   )   (
        )  _)_(_  (
       (  / (  ) \  )      a creature of LIVING
        || ( () ) ||        FLAME crackles forth!
        ((________))
           /    \
"""),
    (("dagannoth", "wallasalki", "lobster"), r"""
         /\______/\
        (  o    o  )___
        /|  ^^^^  |   /\     a DAGANNOTH slithers
         ||||||||||  ~~       from the surf!
        ~~~~~~~~~~~~~~
"""),
    (("gargoyle", "guardian", "golem", "statue"), r"""
        /\  _____  /\
       //  ( o o )  \\
       \\  \ ^^^ /  //      STONE grinds
        \ \|-----|/ /        into motion!
         \ | | | | /
        '  '-'-'-'  '
"""),
    (("yak", "bull", "bison"), r"""
       (__)      (__)
        \  '.__.'  /
         (  o  o  )        a shaggy HORNED
         |   ==   |         beast snorts!
        /|________|\
          ||    ||
"""),
    (("knight", "warrior", "duelist", "pirate", "bandit", "tribesman",
      "brigand", "rogue", "aviansie"), r"""
          ____        ,
         / __ \      /|
        | [oo] |    / |     an armed FOE
        /|____|\   /  |      draws steel!
       / |    | \ /
         |____|__X
         _|__|_
"""),
]


def _fallback_art(name):
    """Family silhouette for a monster with no portrait of its own."""
    for keys, art in _FAMILY_ART:
        if any(k in name for k in keys):
            return art
    return None


# ===========================================================================
#  BOSS SPECTACLE — multi-frame entrances, signature attacks, death throes
#  (the KBD treatment, rolled out to the whole endgame rogues' gallery)
# ===========================================================================
# --- intro stage frames ----------------------------------------------------
KRAKEN_SEA = r"""
     ~   ~    ~     ~    ~     ~
   ~    ~   ~    ~     ~   ~
      ~     .   ~   .    ~    ~
   ~    ~     ~    ~    ~   ~
"""
KRAKEN_BREACH = r"""
        (        )       (
     ~  )\  ~  ( \  ~  ~/ (  ~
   ~   / /  ~ ~ \ \  ~ / /   ~
      ~     ~    ~    ~    ~
"""
CERB_DARK = r"""
      ,_      ,_      ,_
     (--)    (--)    (--)
      ..      ..      ..
       \ \____ | ____/ /
        \____ \|/ ____/
         //   |||   \\
"""
CERB_EMBER = r"""
      ,_      ,_      ,_
     (*,*)   (--)    (*,*)
      ..      ..      ..
       \ \____ | ____/ /
        \____ \|/ ____/
         //   |||   \\
"""
THERMY_WISP = r"""

           ~  ~
          ~ ~~ ~
           ~  ~
"""
THERMY_GATHER = r"""
          ( ~~~~ )
        ( ~~~~~~~~ )
         ( ~~~~~~ )
           \ ~~ /
"""
SIRE_FOG = r"""
    . ~ .  ~  . ~ .  ~  . ~ .
   ~  .  ~  .  ~  .  ~  .  ~
    . ~ . ~  . ~ .  ~ . ~ .
"""
SIRE_LOOM = r"""
      . ~ .-''''''-. ~ .
     ~   /  ~    ~  \   ~
    . ~ |   ~    ~   | ~ .
   ~  . ~\  ~ __ ~  /~ .  ~
    .~ _/|\_/ || \_/|\_ ~.
"""
GROT_STILL = r"""
      /\ /\        /\ /\
     ( - - )      ( - - )
     /| _ |\      /| _ |\
      |___|        |___|
     _|   |_      _|   |_
"""
GROT_CRACK = r"""
      /\ /\   ,    /\ /\
     ( o - ) /    ( - o )
     /| _ |\/     /| _ |\
      |__/|   ,    |\__|
     _|   |_ /    _|   |_
"""
CORP_MIST = r"""
     .  .  .    .   .  .  .
    .    .   .    .   .   .
      .    .    .    .   .
    .   .    .     .    .
"""
CORP_EYES = r"""
     .  .  .    .   .  .  .
    .   (o)  .    . (o)  .
      .    .    .    .   .
    .   .    .     .    .
"""
CALL_PROWL = r"""

        ,--.________,--.
       /  '            \
      |  (o)    ______(o)|
       \___\___/      \__|
        ||  ||     ||  ||
"""
VEN_STRAND = r"""
              |
              |
             (o)
            //''\\
"""
VET_GRAVE = r"""

         ______________
        |  R  I  P     |
     ___|______________|___
       \/  \_/  \/  \_/  \,
          '--,  \_ __/
"""
VET_HALF = r"""
         .-------.
        |  [x x]  |
        |   ___   |
     ___|__|   |__|___
       \/  \_/  \/  \_/
"""
CHAOS_SPARK = r"""

          ~  @  ~
           \ | /
          --(?)--
           / | \
"""
SCORP_MOUND = r"""

       .  ,  .  ,  .  ,
     .  , //''\\  ,  .
    , .  ((    )) . , .
"""
# --- death frames -----------------------------------------------------------
CERB_SLUMP = r"""
      ,_      ,_      ,_
     (x,x)   (x,x)   (x,x)
      ..      ..      ..
       \ \____ | ____/ /
        \______|______/
"""
THERMY_SCATTER = r"""
     ~~     ~   ~~     ~~
   ~    ~~    (o)   ~    ~
      ~~    ~   ~~    ~~
   ~     ~~   ~    ~~    ~
"""
SIRE_SLUMP = r"""
       _____________
      /  x       x  \
      \____  __ ____/
    _/|\_ \_/||\_/ _/|\_
   / \|/    ||    \|/ \
"""
GROT_RUBBLE = r"""

      ,  /\  .    .  /\  ,
     . _|  |_  ..  _|  |_ .
    ,_|      |_,,_|      |_,
"""
VET_BONES = r"""

          _  [x x]  _
       \_/ \__ _ __/ \_/
      , \_/  \|_|/ \_/ ,
"""
VEN_CURL = r"""
         \\  //
        _ ((oo)) _
       \ \/,,,,\/ /
        \/      \/
"""
SCORP_CURL = r"""
        ______________
       ( _\        /_ )
        \ |(x)  (x)| /
          |___,____|--,
                   (x_)
"""
# --- signature attack fx ------------------------------------------------------
FX_PILLAR1 = r"""
         ) ) (
        ( ( ) )
        | | | |
        | | | |
       ~~~~~~~~~
"""
FX_PILLAR2 = r"""
        (  )  (
        ) (( ) )
       || || || |
       || || || |
      ~~~~~~~~~~~
"""
FX_TENTACLE1 = r"""

        __/\__
     __/      \__,-,
    /             \_)
"""
FX_TENTACLE2 = r"""
       ,-,__/\____
      (_/         \__
                     \
"""
FX_JAWS1 = r"""
     \/\/    \/\/    \/\/
     /\/\    /\/\    /\/\
"""
FX_JAWS2 = r"""
     \/v\/  \/v\/  \/v\/
     /\^/\  /\^/\  /\^/\
"""
FX_SOULS = r"""
      }>---   )+---   *~---
       sword    bow    staff
"""
FX_BILLOW1 = r"""
        (  ~~~  )
       ( ~~~~~~~ )
        ( ~~~~~ )
"""
FX_BILLOW2 = r"""
      ( ~~~~~~~~~ )
     ( ~~~~~~~~~~~ )
      ( ~~~~~~~~~ )
"""
FX_BOLT1 = r"""
         \
          \/\
            \
"""
FX_BOLT2 = r"""
         \\
          \\/\
           /\\
             \\
"""
FX_WEB = r"""
       \ | | | /
      --+--+--+--
       / | | | \
      --+--+--+--
"""
FX_SMASH1 = r"""

         \ | /
        -- * --
         / | \
"""
FX_SMASH2 = r"""
        \  |  /
       \ \ | / /
      --- (*) ---
       / / | \ \
        /  |  \
"""
FX_CHARGE1 = r"""
    - -  ,--.____,--.
   - -  /  '        \>>
    - - \____________/
"""
FX_CHARGE2 = r"""
   - - -  ,--.____,--.
  - - -  /  '        \>>>
   - - - \____________/
"""
FX_ROAR1 = r"""
        (  RRAAA  )
       ((         ))
"""
FX_ROAR2 = r"""
      ((  RRAAAAA  ))
     (((           )))
"""
FX_TAIL1 = r"""
              ,-,
             ( x )
              )-(
            __//
         __//
"""
FX_TAIL2 = r"""
      ,-,
     ( x )==<
      )-(
       \\__
          \\__
"""


def _fx(*pairs):
    """Build an animation from (art, styles...) tuples."""
    return [_tint(art, *styles) for art, *styles in pairs]


# intro/death builders: stage frames climax on the boss's own portrait
def _kraken_intro(name):
    return _fx((KRAKEN_SEA, "bblue", "dim"), (KRAKEN_BREACH, "bblue"),
               (MONSTER_ART["kraken"], "teal", "bold"),
               (MONSTER_ART["kraken"], "bcyan", "bold"))


def _kraken_death(name):
    return _fx((MONSTER_ART["kraken"], "bred"),
               (KRAKEN_BREACH, "bblue", "dim"), (KRAKEN_SEA, "grey", "dim"))


def _cerb_intro(name):
    return _fx((CERB_DARK, "grey", "dim"), (CERB_EMBER, "red"),
               (MONSTER_ART["cerberus"], "bred", "bold"),
               (MONSTER_ART["cerberus"], "orange", "bold"))


def _cerb_death(name):
    return _fx((MONSTER_ART["cerberus"], "bred"), (CERB_SLUMP, "grey"),
               (CERB_SLUMP, "grey", "dim"))


def _thermy_intro(name):
    return _fx((THERMY_WISP, "grey", "dim"), (THERMY_GATHER, "grey"),
               (MONSTER_ART["thermonuclear smoke devil"], "bwhite", "bold"),
               (MONSTER_ART["thermonuclear smoke devil"], "bmagenta", "bold"))


def _thermy_death(name):
    return _fx((MONSTER_ART["thermonuclear smoke devil"], "bred"),
               (THERMY_SCATTER, "grey"), (THERMY_WISP, "grey", "dim"))


def _sire_intro(name):
    return _fx((SIRE_FOG, "green", "dim"), (SIRE_LOOM, "green"),
               (MONSTER_ART["abyssal sire"], "purple", "bold"),
               (MONSTER_ART["abyssal sire"], "bmagenta", "bold"))


def _sire_death(name):
    return _fx((MONSTER_ART["abyssal sire"], "bred"), (SIRE_SLUMP, "green"),
               (SIRE_FOG, "grey", "dim"))


def _grot_intro(name):
    return _fx((GROT_STILL, "grey", "dim"), (GROT_CRACK, "grey"),
               (MONSTER_ART["grotesque guardians"], "byellow", "bold"),
               (MONSTER_ART["grotesque guardians"], "bwhite", "bold"))


def _grot_death(name):
    return _fx((MONSTER_ART["grotesque guardians"], "bred"),
               (GROT_RUBBLE, "grey"), (GROT_RUBBLE, "grey", "dim"))


def _corp_intro(name):
    return _fx((CORP_MIST, "grey", "dim"), (CORP_EYES, "bred"),
               (MONSTER_ART["corporeal beast"], "grey", "bold"),
               (MONSTER_ART["corporeal beast"], "bred", "bold"))


def _corp_death(name):
    return _fx((MONSTER_ART["corporeal beast"], "bred"),
               (CORP_EYES, "grey"), (CORP_MIST, "grey", "dim"))


def _callisto_intro(name):
    return _fx((CALL_PROWL, "grey"), (MONSTER_ART["callisto"], "brown", "bold"),
               (MONSTER_ART["callisto"], "bred", "bold"))


def _callisto_death(name):
    return _fx((MONSTER_ART["callisto"], "bred"), (CALL_PROWL, "grey"),
               (CALL_PROWL, "grey", "dim"))


def _venenatis_intro(name):
    return _fx((VEN_STRAND, "grey"), (MONSTER_ART["venenatis"], "purple", "bold"),
               (MONSTER_ART["venenatis"], "bmagenta", "bold"))


def _venenatis_death(name):
    return _fx((MONSTER_ART["venenatis"], "bred"), (VEN_CURL, "grey"),
               (VEN_CURL, "grey", "dim"))


def _vetion_intro(name):
    return _fx((VET_GRAVE, "grey", "dim"), (VET_HALF, "purple"),
               (MONSTER_ART["vet'ion"], "bmagenta", "bold"),
               (MONSTER_ART["vet'ion"], "bwhite", "bold"))


def _vetion_death(name):
    return _fx((MONSTER_ART["vet'ion"], "bred"), (VET_BONES, "grey"),
               (VET_BONES, "grey", "dim"))


def _chaosele_intro(name):
    return _fx((CHAOS_SPARK, "bmagenta", "dim"), (CHAOS_SPARK, "bmagenta"),
               (MONSTER_ART["chaos elemental"], "bmagenta", "bold"),
               (MONSTER_ART["chaos elemental"], "bcyan", "bold"))


def _chaosele_death(name):
    return _fx((MONSTER_ART["chaos elemental"], "bred"),
               (CHAOS_SPARK, "bmagenta"), (CHAOS_SPARK, "grey", "dim"))


def _scorpia_intro(name):
    return _fx((SCORP_MOUND, "brown", "dim"), (SCORP_MOUND, "brown"),
               (MONSTER_ART["scorpia"], "green", "bold"),
               (MONSTER_ART["scorpia"], "bgreen", "bold"))


def _scorpia_death(name):
    return _fx((MONSTER_ART["scorpia"], "bred"), (SCORP_CURL, "green"),
               (SCORP_CURL, "grey", "dim"))


BOSS_INTRO.update({
    "kraken": _kraken_intro, "cerberus": _cerb_intro,
    "thermonuclear smoke devil": _thermy_intro, "abyssal sire": _sire_intro,
    "grotesque guardians": _grot_intro, "corporeal beast": _corp_intro,
    "callisto": _callisto_intro, "venenatis": _venenatis_intro,
    "vet'ion": _vetion_intro, "chaos elemental": _chaosele_intro,
    "scorpia": _scorpia_intro,
})
BOSS_DEATH.update({
    "kraken": _kraken_death, "cerberus": _cerb_death,
    "thermonuclear smoke devil": _thermy_death, "abyssal sire": _sire_death,
    "grotesque guardians": _grot_death, "corporeal beast": _corp_death,
    "callisto": _callisto_death, "venenatis": _venenatis_death,
    "vet'ion": _vetion_death, "chaos elemental": _chaosele_death,
    "scorpia": _scorpia_death,
})


# attack-fx builders (wired into the boss attack tables)
def _fx_pillar():
    return _fx((FX_PILLAR1, "bblue"), (FX_PILLAR2, "bcyan", "bold"))


def _fx_tentacle():
    return _fx((FX_TENTACLE1, "teal"), (FX_TENTACLE2, "teal", "bold"))


def _fx_jaws():
    return _fx((FX_JAWS1, "bred"), (FX_JAWS2, "bred", "bold"))


def _fx_hellfire():
    return _fx((FX_BILLOW1, "orange"), (FX_BILLOW2, "bred", "bold"))


def _fx_souls():
    return _fx((FX_SOULS, "grey"), (FX_SOULS, "bcyan", "bold"))


def _fx_smoke():
    return _fx((FX_BILLOW1, "grey"), (FX_BILLOW2, "grey", "bold"))


def _fx_lash():
    return _fx((FX_TENTACLE1, "purple"), (FX_TENTACLE2, "bmagenta", "bold"))


def _fx_miasma():
    return _fx((FX_BILLOW1, "green"), (FX_BILLOW2, "bgreen", "bold"))


def _fx_darkness():
    return _fx((FX_BILLOW1, "purple"), (FX_BILLOW2, "bmagenta", "bold"))


def _fx_smash():
    return _fx((FX_SMASH1, "grey"), (FX_SMASH2, "byellow", "bold"))


def _fx_slag():
    return _fx((FX_SMASH1, "orange"), (FX_SMASH2, "bred", "bold"))


def _fx_bolt():
    return _fx((FX_BOLT1, "bmagenta"), (FX_BOLT2, "bmagenta", "bold"))


def _fx_bolt_blue():
    return _fx((FX_BOLT1, "bblue"), (FX_BOLT2, "bcyan", "bold"))


def _fx_web():
    return _fx((FX_WEB, "grey"), (FX_WEB, "bwhite", "bold"))


def _fx_charge():
    return _fx((FX_CHARGE1, "brown"), (FX_CHARGE2, "bred", "bold"))


def _fx_roar():
    return _fx((FX_ROAR1, "orange"), (FX_ROAR2, "bred", "bold"))


def _fx_tail():
    return _fx((FX_TAIL1, "green"), (FX_TAIL2, "bgreen", "bold"))


def item_rarity_color(name):
    """Colour an item by its market value (loot-rarity flavour)."""
    v = ITEMS.get(name, {}).get("value", 0)
    if name == "coins":
        return "gold"
    if v >= 8000:
        return "gold"
    if v >= 1500:
        return "bmagenta"
    if v >= 300:
        return "bblue"
    if v >= 50:
        return "bgreen"
    return "white"


