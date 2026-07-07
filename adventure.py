#!/usr/bin/env python3
"""
OnlyRunes  —  A Text Adventure in Gielinor
==========================================
A terminal text adventure inspired by Old School RuneScape. Explore the cities
of Misthalin, Asgarnia and the Kharidian Desert, train your skills, fight
monsters, bank your loot, trade on the Grand Exchange, unlock members content,
and complete classic quests.

A love letter to Old School RuneScape — not every item, monster or quest, but a
broad, coherent world built to be easy to extend (see the data tables below).

Run with:  python3 adventure.py
"""

import contextlib
import difflib
import io
import json
import math
import os
import random
import sys
import textwrap
import time


# ===========================================================================
#  COLOR & TEXT-ART TOOLKIT
# ===========================================================================
# ANSI colors that gracefully disable when output isn't an interactive
# terminal (so piped/scripted runs stay clean) or when NO_COLOR is set.

def _supports_color():
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    try:
        return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"
    except Exception:
        return False


COLOR = _supports_color()
WEB = False          # set by enable_web() when running in the browser (Pyodide)
BETA = False         # set by enable_beta(); gates dev/test-only commands
XP_RATE = 2          # global XP multiplier (2x) — faster progression

# Style/colour codes
_CODES = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "italic": "\033[3m", "underline": "\033[4m",
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
    "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
    "cyan": "\033[36m", "white": "\033[37m", "grey": "\033[90m",
    "bred": "\033[91m", "bgreen": "\033[92m", "byellow": "\033[93m",
    "bblue": "\033[94m", "bmagenta": "\033[95m", "bcyan": "\033[96m",
    "bwhite": "\033[97m",
    "gold": "\033[38;5;220m", "orange": "\033[38;5;208m",
    "brown": "\033[38;5;130m", "purple": "\033[38;5;141m",
    "lime": "\033[38;5;154m", "teal": "\033[38;5;44m",
}


def paint(text, *styles):
    """Wrap text in ANSI style codes (no-op when colour is disabled)."""
    if not COLOR or not styles:
        return str(text)
    prefix = "".join(_CODES.get(s, "") for s in styles)
    return f"{prefix}{text}{_CODES['reset']}"


def strip_ansi(text):
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


def visible_len(text):
    return len(strip_ansi(text))


# ===========================================================================
#  OUTPUT HELPERS
# ===========================================================================

_QUIET = False    # batch actions silence per-swing chatter (not level-ups)


def say(text="", *styles):
    """Print word-wrapped narration, optionally tinted with ANSI styles."""
    if _QUIET:
        return
    if text == "":
        print()
        return
    wrapped = textwrap.fill(str(text), width=78)
    print(paint(wrapped, *styles) if styles else wrapped)


def banner(text, color="gold", line_color="brown"):
    """A framed, centered title bar."""
    bar = paint("=" * 78, line_color)
    title = paint(str(text).center(78), color, "bold")
    print(f"\n{bar}\n{title}\n{bar}")


def rule(color="grey"):
    print(paint("-" * 78, color))


def show_art(art, *styles, center=False):
    """Print multi-line ASCII art without word-wrapping, optionally tinted."""
    for raw in art.strip("\n").splitlines():
        line = raw.center(78) if center else raw
        print(paint(line, *styles) if styles else line)


def bar_meter(current, maximum, width=20, fill_color="bgreen", empty_color="grey"):
    """Return a colored [#####-----] style meter."""
    current = max(0, current)
    ratio = (current / maximum) if maximum else 0
    filled = int(round(ratio * width))
    if ratio > 0.5:
        fc = fill_color
    elif ratio > 0.25:
        fc = "byellow"
    else:
        fc = "bred"
    bar = paint("█" * filled, fc) + paint("░" * (width - filled), empty_color)
    return f"{bar} {current}/{maximum}"


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ===========================================================================
#  ANIMATION ENGINE
# ===========================================================================
# Plays a sequence of ASCII-art frames as a real animation:
#   * in a terminal (TTY): redraws frames in place using ANSI cursor moves.
#   * in the browser (Pyodide): emits a marked block that index.html parses
#     out and plays with JS timers + xterm cursor control.
#   * otherwise (piped/tests): prints the final frame once, no control codes.
# Frames may carry their own ANSI colour (built with paint()); centering is by
# *visible* width so embedded colour codes don't throw off the alignment.

ANIM_OPEN = "\x00\x00ONLYRUNES_ANIM\x00"     # sentinels never appear in game text
ANIM_CLOSE = "\x00ONLYRUNES_ANIM\x00\x00"


def _tint(art, *styles):
    """Paint every line of an art block (so a frame can be one solid colour)."""
    return "\n".join(paint(ln, *styles) for ln in art.strip("\n").splitlines())


def animate(frames, delay=0.14, loops=1, color=None, center=True, hold=0.0):
    """Play `frames` (list of multi-line art strings) as an animation.

    Frames are *block*-centered with one shared offset (so the art stays
    rock-steady from frame to frame, even as colour/details change)."""
    if isinstance(color, str):
        color = (color,)
    blocks = [f.strip("\n").splitlines() for f in frames if f.strip("\n")]
    if not blocks:
        return
    height = max(len(b) for b in blocks)
    indent = 0
    if center:
        maxw = max((visible_len(ln) for b in blocks for ln in b), default=0)
        indent = max(0, (78 - maxw) // 2)
    pad = " " * indent
    rendered = []                        # equal height, equal indent => no jitter
    for b in blocks:
        lines = [""] * (height - len(b)) + list(b)   # bottom-align (things sink)
        out = []
        for ln in lines:
            ln = (pad + ln) if ln else ""
            out.append(paint(ln, *color) if (color and ln) else ln)
        rendered.append("\n".join(out))
    loops = max(1, loops)

    if WEB:
        sys.stdout.write(ANIM_OPEN + json.dumps({
            "frames": rendered, "delay": int(delay * 1000),
            "loops": loops, "hold": int(hold * 1000), "height": height,
        }) + ANIM_CLOSE + "\n")
        return

    if not COLOR or not _is_tty():
        print(rendered[-1])              # static fallback (pipes / tests)
        return

    up_clear = f"\x1b[{height}A\x1b[0J"   # cursor up `height` rows, clear below
    for li in range(loops):
        for fi, frame in enumerate(rendered):
            sys.stdout.write(frame + "\n")
            sys.stdout.flush()
            if li == loops - 1 and fi == len(rendered) - 1:
                break
            time.sleep(delay)
            sys.stdout.write(up_clear)
            sys.stdout.flush()
    if hold:
        time.sleep(hold)


def _is_tty():
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


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
    return [_tint(GEN_ROAR, "grey"), _tint(GEN_ROAR, "bred", "bold"),
            _tint(GEN_ROAR, "byellow", "bold"), _tint(GEN_ROAR, "bred", "bold")]


def _generic_boss_death(name):
    return [_tint(GEN_ROAR, "bred"), _tint(GEN_ROAR, "grey", "dim")]


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


# ===========================================================================
#  XP / LEVELS  (Old School RuneScape curve)
# ===========================================================================

_XP_TABLE = [0] * 100  # _XP_TABLE[level] = xp required for that level
_pts = 0
for _lvl in range(1, 99):
    _pts += int(_lvl + 300 * (2 ** (_lvl / 7.0)))
    _XP_TABLE[_lvl + 1] = _pts // 4


def level_from_xp(xp):
    level = 1
    for lvl in range(1, 100):
        if _XP_TABLE[lvl] <= xp:
            level = lvl
        else:
            break
    return level


def xp_progress(xp):
    """Progress toward the next level for a skill's total xp.

    Returns (level, xp_into_level, xp_for_this_level, xp_to_next). At level 99
    the span/remaining are 0 (maxed)."""
    lvl = level_from_xp(xp)
    if lvl >= 99:
        return (99, 0, 0, 0)
    floor = _XP_TABLE[lvl]
    nxt = _XP_TABLE[lvl + 1]
    into = xp - floor
    span = nxt - floor
    return (lvl, into, span, nxt - xp)


SKILLS = [
    "attack", "strength", "defence", "hitpoints", "ranged", "prayer", "magic",
    "cooking", "woodcutting", "fishing", "firemaking", "crafting", "smithing",
    "mining", "runecrafting",
    # members skills
    "thieving", "agility", "slayer", "herblore", "fletching", "farming",
    "construction", "hunter",
]
MEMBERS_SKILLS = {"thieving", "agility", "slayer", "herblore", "fletching",
                  "farming", "construction", "hunter"}


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
    "grimy guam":        ("guam leaf", 3, 2),
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
    "attack potion":   {"herb": "guam leaf", "second": "eye of newt", "lvl": 3,
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


# ===========================================================================
#  SPELLS  (standard spellbook)
# ===========================================================================
# combat spells: max_hit + rune cost + magic level + xp
SPELLS = {
    "wind strike":  {"type": "combat", "max": 2, "lvl": 1,  "xp": 5.5,
                     "runes": {"air rune": 1, "mind rune": 1}},
    "water strike": {"type": "combat", "max": 4, "lvl": 5,  "xp": 7.5,
                     "runes": {"water rune": 1, "air rune": 1, "mind rune": 1}},
    "earth strike": {"type": "combat", "max": 6, "lvl": 9,  "xp": 9.5,
                     "runes": {"earth rune": 2, "air rune": 1, "mind rune": 1}},
    "fire strike":  {"type": "combat", "max": 8, "lvl": 13, "xp": 11.5,
                     "runes": {"fire rune": 3, "air rune": 2, "mind rune": 1}},
    "wind bolt":    {"type": "combat", "max": 9, "lvl": 17, "xp": 13.5,
                     "runes": {"air rune": 2, "chaos rune": 1}},
    "water bolt":   {"type": "combat", "max": 10, "lvl": 23, "xp": 16.5,
                     "runes": {"water rune": 2, "air rune": 2, "chaos rune": 1}},
    "earth bolt":   {"type": "combat", "max": 11, "lvl": 29, "xp": 19.5,
                     "runes": {"earth rune": 3, "air rune": 2, "chaos rune": 1}},
    "fire bolt":    {"type": "combat", "max": 12, "lvl": 35, "xp": 22.5,
                     "runes": {"fire rune": 4, "air rune": 3, "chaos rune": 1}},
    # utility
    "low alchemy":  {"type": "alch", "ratio": 0.4, "lvl": 21, "xp": 31,
                     "runes": {"fire rune": 3, "nature rune": 1}},
    "high alchemy": {"type": "alch", "ratio": 0.6, "lvl": 55, "xp": 65,
                     "runes": {"fire rune": 5, "nature rune": 1}},
    "lumbridge teleport": {"type": "tele", "dest": "lumbridge_castle", "lvl": 31,
                           "xp": 41, "runes": {"earth rune": 1, "air rune": 3, "law rune": 1}},
    "varrock teleport":   {"type": "tele", "dest": "varrock_square", "lvl": 25,
                           "xp": 35, "runes": {"fire rune": 1, "air rune": 3, "law rune": 1}},
    "falador teleport":   {"type": "tele", "dest": "falador_square", "lvl": 37,
                           "xp": 48, "runes": {"water rune": 1, "air rune": 3, "law rune": 1}},
}


# ===========================================================================
#  GATHERING TABLES
# ===========================================================================
# tree: (product, level, xp)
TREES = {
    "tree":   ("logs", 1, 25),
    "oak":    ("oak logs", 15, 37),
    "willow": ("willow logs", 30, 67),
}
# rock: (product, level, xp)
ROCKS = {
    "copper": ("copper ore", 1, 17), "tin": ("tin ore", 1, 17),
    "clay": ("clay", 1, 5), "iron": ("iron ore", 15, 35),
    "silver": ("silver ore", 20, 40), "coal": ("coal", 30, 50),
    "gold": ("gold ore", 40, 65), "mithril": ("mithril ore", 55, 80),
    "adamantite": ("adamantite ore", 70, 95),
    "rune essence": ("rune essence", 1, 5),
}
# fishing spot tool -> [(product, level, xp), ...]
FISH = {
    "net": [("raw shrimp", 1, 10), ("raw anchovies", 15, 40)],
    "rod": [("raw sardine", 5, 20), ("raw herring", 10, 30), ("raw pike", 25, 60)],
    "fly": [("raw trout", 20, 50), ("raw salmon", 30, 70)],
}
# smelting: bar -> ({ores}, level, xp)
SMELT = {
    "bronze bar": ({"copper ore": 1, "tin ore": 1}, 1, 6),
    "iron bar": ({"iron ore": 1}, 15, 12),
    "silver bar": ({"silver ore": 1}, 20, 14),
    "steel bar": ({"iron ore": 1, "coal": 2}, 30, 17),
    "gold bar": ({"gold ore": 1}, 40, 22),
    "mithril bar": ({"mithril ore": 1, "coal": 4}, 50, 30),
    "adamant bar": ({"adamantite ore": 1, "coal": 6}, 70, 37),
}
# smithable item -> (bar type, bar count, smithing level)
SMITH_BARS = {"dagger": 1, "sword": 1, "scimitar": 2, "full helm": 2,
              "kiteshield": 3, "platelegs": 3, "platebody": 5}
SMITH_METAL_LVL = {"bronze": 1, "iron": 15, "steel": 30, "mithril": 50, "adamant": 70}
# runecrafting: rune -> (level, xp)
RUNECRAFT = {"air rune": (1, 5), "mind rune": (2, 5.5), "water rune": (5, 6),
             "earth rune": (9, 6.5), "fire rune": (14, 7), "body rune": (20, 7.5)}

# Prayers: name -> (level, drain_per_round, {boost pct}, protect_style)
# boosts are fractional bonuses to effective combat levels while active.
PRAYERS = {
    "thick skin":          (1,  0.15, {"defence": 0.05}, None),
    "burst of strength":   (4,  0.15, {"strength": 0.05}, None),
    "clarity of thought":  (7,  0.15, {"attack": 0.05}, None),
    "rock skin":           (10, 0.30, {"defence": 0.10}, None),
    "superhuman strength": (13, 0.30, {"strength": 0.10}, None),
    "improved reflexes":   (16, 0.30, {"attack": 0.10}, None),
    "steel skin":          (28, 0.60, {"defence": 0.15}, None),
    "ultimate strength":   (31, 0.60, {"strength": 0.15}, None),
    "incredible reflexes": (34, 0.60, {"attack": 0.15}, None),
    "protect from magic":  (37, 0.60, {}, "magic"),
    "protect from missiles": (40, 0.60, {}, "ranged"),
    "protect from melee":  (43, 0.60, {}, "melee"),
}

# Thieving pickpocket targets: name -> (level, xp, max_coins, fail_damage)
PICKPOCKET = {
    "man": (1, 8, 12, 1), "woman": (1, 8, 12, 1),
    "farmer": (10, 15, 30, 2), "guard": (40, 47, 60, 3),
}
# Agility: course-name -> (level, xp, fail_damage)
AGILITY_COURSE = (1, 8, 2)  # (min level, xp per lap, fall damage)

# Monsters a Slayer Master may assign (all reachable). Slayer xp per kill = hp.
SLAYER_TARGETS = ["goblin", "cow", "giant rat", "scorpion", "skeleton",
                  "zombie", "giant spider", "minotaur", "flesh crawler",
                  "barbarian", "hobgoblin", "guard", "hill giant"]
SLAYER_POINTS = {"easy": 3, "medium": 5, "hard": 8, "elite": 12}


# ===========================================================================
#  MONSTERS
# ===========================================================================
def mob(hp, attack, defence, max_hit, drops, weak=None, members=False, boss=False):
    return {"hp": hp, "attack": attack, "defence": defence,
            "max_hit": max_hit, "drops": drops, "weak": weak,
            "members": members, "boss": boss}


# drops: list of (item, min, max, chance)
MONSTERS = {
    "chicken": mob(3, 1, 1, 1, [("bones", 1, 1, 1.0), ("feather", 5, 15, 1.0),
                                ("raw chicken", 1, 1, 1.0)]),
    "cow": mob(8, 1, 1, 1, [("bones", 1, 1, 1.0), ("cowhide", 1, 1, 1.0),
                            ("raw beef", 1, 1, 1.0)]),
    "goblin": mob(5, 1, 1, 2, [("bones", 1, 1, 1.0), ("coins", 1, 12, 0.7)]),
    "giant rat": mob(5, 1, 1, 1, [("bones", 1, 1, 1.0), ("raw beef", 1, 1, 0.5)]),
    "barbarian": mob(18, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.8),
                                   ("bronze sword", 1, 1, 0.1)]),
    "guard": mob(22, 9, 8, 3, [("bones", 1, 1, 1.0), ("coins", 10, 40, 0.9)]),
    "scorpion": mob(10, 4, 3, 2, [("bones", 1, 1, 0.0)]),
    "skeleton": mob(16, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 25, 0.6)]),
    "zombie": mob(16, 7, 5, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.6)]),
    "dark wizard": mob(14, 7, 5, 4, [("bones", 1, 1, 1.0), ("mind rune", 1, 5, 0.5),
                                     ("chaos rune", 1, 2, 0.2)]),
    "hobgoblin": mob(28, 14, 10, 4, [("bones", 1, 1, 1.0), ("coins", 10, 50, 0.8),
                                     ("iron arrow", 5, 10, 0.2)]),
    "hill giant": mob(35, 18, 14, 5, [("big bones", 1, 1, 1.0), ("coins", 20, 80, 0.9),
                                      ("steel platelegs", 1, 1, 0.05),
                                      ("limpwurt root", 1, 1, 0.12),
                                      ("grimy ranarr", 1, 1, 0.06),
                                      ("giant key", 1, 1, 0.05),
                                      ("law rune", 1, 3, 0.1)]),
    "count draynor": mob(30, 12, 8, 4, [("bones", 1, 1, 1.0)], weak="stake"),
    # --- additional monsters ---
    "giant spider": mob(16, 8, 5, 2, [("bones", 1, 1, 1.0), ("coins", 1, 15, 0.5)]),
    "dwarf": mob(14, 8, 6, 2, [("bones", 1, 1, 1.0), ("coins", 3, 25, 0.9)]),
    "minotaur": mob(18, 10, 7, 3, [("bones", 1, 1, 1.0), ("coins", 5, 30, 0.9),
                                   ("iron arrow", 5, 15, 0.4)]),
    "flesh crawler": mob(22, 11, 7, 2, [("bones", 1, 1, 1.0), ("coins", 10, 45, 0.9),
                                        ("mind rune", 2, 6, 0.3)]),
    "thug": mob(20, 12, 6, 3, [("bones", 1, 1, 1.0), ("coins", 8, 40, 0.8)]),
    "dark warrior": mob(28, 16, 12, 4, [("bones", 1, 1, 1.0), ("coins", 15, 60, 0.9)]),
    "imp": mob(6, 3, 2, 1, [("bones", 1, 1, 0.0), ("red bead", 1, 1, 0.25),
                            ("yellow bead", 1, 1, 0.25), ("black bead", 1, 1, 0.25),
                            ("white bead", 1, 1, 0.25), ("coins", 1, 8, 0.4)]),
    "man": mob(7, 1, 1, 1, [("bones", 1, 1, 1.0), ("coins", 1, 12, 0.8)]),
    "chicken farmer": mob(7, 1, 1, 1, [("bones", 1, 1, 1.0), ("coins", 1, 10, 0.7)]),
    "zombie rat": mob(6, 2, 1, 1, [("bones", 1, 1, 1.0)]),
    # --- members monsters (gated behind membership) ---
    "moss giant": mob(60, 24, 18, 6, [("big bones", 1, 1, 1.0), ("coins", 20, 120, 0.9),
                                      ("mithril sword", 1, 1, 0.06),
                                      ("grimy harralander", 1, 1, 0.12),
                                      ("grimy ranarr", 1, 1, 0.08),
                                      ("nature rune", 2, 6, 0.2)], members=True),
    "ice giant": mob(70, 28, 22, 8, [("big bones", 1, 1, 1.0), ("coins", 30, 150, 0.9),
                                     ("adamant arrow", 5, 15, 0.2)], members=True),
    "lesser demon": mob(79, 32, 24, 8, [("ashes", 1, 1, 1.0), ("coins", 30, 180, 0.9),
                                        ("rune full helm", 1, 1, 0.03),
                                        ("law rune", 2, 8, 0.2)], members=True),
    "greater demon": mob(87, 36, 26, 9, [("ashes", 1, 1, 1.0), ("coins", 40, 220, 0.9),
                                         ("rune kiteshield", 1, 1, 0.02)], members=True),
    "king black dragon": mob(240, 60, 40, 25, [("big bones", 1, 1, 1.0),
                             ("coins", 500, 3000, 1.0), ("rune platebody", 1, 1, 0.15),
                             ("dragon med helm", 1, 1, 0.05),
                             ("ranarr seed", 1, 3, 0.3)], members=True, boss=True),
    "obor": mob(120, 30, 22, 12, [("big bones", 1, 1, 1.0),
                ("coins", 200, 1200, 1.0), ("hill giant club", 1, 1, 0.10),
                ("grimy ranarr", 2, 4, 0.6), ("limpwurt root", 2, 5, 0.6),
                ("law rune", 3, 8, 0.4)], boss=True),
}

# Difficulty rank per monster (drives auto-kill caps). Bosses set below.
MONSTER_RANK = {
    # easy
    "chicken": "easy", "cow": "easy", "goblin": "easy", "giant rat": "easy",
    "man": "easy", "zombie rat": "easy", "imp": "easy",
    # medium
    "scorpion": "medium", "giant spider": "medium", "dwarf": "medium",
    "minotaur": "medium", "barbarian": "medium", "thug": "medium",
    "skeleton": "medium", "zombie": "medium", "dark wizard": "medium",
    "flesh crawler": "medium",
    # hard
    "guard": "hard", "hobgoblin": "hard", "dark warrior": "hard",
    "hill giant": "hard",
    # elite
    "moss giant": "elite", "ice giant": "elite", "lesser demon": "elite",
    "greater demon": "elite",
}
_BOSSES = {"king black dragon", "count draynor", "obor"}
for _name, _m in MONSTERS.items():
    _m["rank"] = "boss" if _name in _BOSSES else MONSTER_RANK.get(_name, "medium")
    if _name in _BOSSES:
        _m["boss"] = True

# How many of each rank you may auto-fight in one go. Bosses: none.
RANK_CAP = {"easy": 30, "medium": 20, "hard": 10, "elite": 5}
RANK_COLOR = {"easy": "bgreen", "medium": "byellow", "hard": "orange",
              "elite": "bred", "boss": "bmagenta"}


# ===========================================================================
#  WORLD MAP
# ===========================================================================
# Each room: name, desc, exits{dir:roomkey}, plus optional service flags:
#   bank, range, furnace, anvil, ge, spinning_wheel, altar(rune name)
#   trees[], rocks[], fish_tools[], monsters[], shop, npc(quest key)
ROOMS = {
    # ---- Lumbridge -------------------------------------------------------
    "lumbridge_castle": dict(
        name="Lumbridge Castle",
        desc="The home of Duke Horacio. A cooking range warms the kitchen, a "
             "bank sits upstairs, and a spinning wheel hums in the hall. The "
             "Cook frets by the ovens.",
        exits={"north": "general_store", "east": "river_lum", "south": "swamp",
               "west": "cow_field", "church": "lumbridge_church"},
        bank=True, range=True, spinning_wheel=True, npc="cooks_assistant"),
    "general_store": dict(
        name="Lumbridge General Store",
        desc="A well-stocked shop selling adventuring basics.",
        exits={"south": "lumbridge_castle", "north": "lumbridge_forest",
               "east": "lumbridge_farm"},
        shop="general"),
    "lumbridge_forest": dict(
        name="Lumbridge Forest",
        desc="Trees crowd the road north to Varrock. Goblins grunt in the brush.",
        exits={"south": "general_store", "north": "varrock_gate"},
        trees=["tree", "oak"], monsters=["goblin"]),
    "lumbridge_farm": dict(
        name="Lumbridge Farm",
        desc="Chickens, a cow, a wheat field and sheep. Farmer Fred is here.",
        exits={"west": "general_store", "north": "windmill"},
        monsters=["chicken"], npc="sheep_shearer", pickpocket=["farmer"]),
    "windmill": dict(
        name="Lumbridge Windmill",
        desc="Grain becomes flour here if you have an empty pot.",
        exits={"south": "lumbridge_farm"}),
    "river_lum": dict(
        name="River Lum",
        desc="A fishing spot teeming with shrimp. A toll bridge leads east to "
             "Al Kharid.",
        exits={"west": "lumbridge_castle", "east": "al_kharid_gate"},
        fish_tools=["net"]),
    "swamp": dict(
        name="Lumbridge Swamp",
        desc="Copper and tin rocks dot the misty ground.",
        exits={"north": "lumbridge_castle"}, rocks=["copper", "tin", "clay"]),
    "cow_field": dict(
        name="Lumbridge Cow Field",
        desc="A fenced field full of cows and sheep. Good for combat, hides, "
             "and wool.",
        exits={"east": "lumbridge_castle", "west": "draynor_path"},
        monsters=["cow"]),
    # ---- Al Kharid -------------------------------------------------------
    "al_kharid_gate": dict(
        name="Al Kharid Toll Gate",
        desc="A gate guard demands 10 coins to pass east into Al Kharid.",
        exits={"west": "river_lum", "east": "al_kharid_square"}, toll=10),
    "al_kharid_square": dict(
        name="Al Kharid",
        desc="A desert city with a bank, furnace, range, a scimitar shop and a "
             "tanner. Scorpions skitter at the edges.",
        exits={"west": "al_kharid_gate", "north": "al_kharid_mine",
               "east": "al_kharid_palace"},
        bank=True, furnace=True, range=True, tanner=True, shop="scimitar",
        monsters=["scorpion"], pickpocket=["man"]),
    "al_kharid_mine": dict(
        name="Al Kharid Mine",
        desc="A rich mine: iron, silver, coal, gold, mithril and adamantite.",
        exits={"south": "al_kharid_square"},
        rocks=["iron", "silver", "coal", "gold", "mithril", "adamantite"]),
    "al_kharid_palace": dict(
        name="Al Kharid Palace",
        desc="The palace of Emir. Guards watch the gleaming halls.",
        exits={"west": "al_kharid_square"}),
    # ---- Draynor ---------------------------------------------------------
    "draynor_path": dict(
        name="Draynor Path",
        desc="A path winding west to Draynor Village.",
        exits={"east": "cow_field", "west": "draynor_village"}),
    "draynor_village": dict(
        name="Draynor Village",
        desc="A run-down village with a bank, willow trees by the river, a "
             "wheat field, and Morgan, who looks terrified.",
        exits={"east": "draynor_path", "north": "draynor_manor",
               "south": "wizard_tower"},
        bank=True, trees=["willow"], npc=["vampyre_slayer", "witch_potion"]),
    "draynor_manor": dict(
        name="Draynor Manor",
        desc="A gloomy manor. Skeletons and zombies roam, and Count Draynor "
             "lurks within.",
        exits={"south": "draynor_village"},
        monsters=["skeleton", "zombie"], npc="ernest_chicken"),
    # ---- Varrock ---------------------------------------------------------
    "varrock_gate": dict(
        name="Varrock South Gate",
        desc="The southern entrance to Varrock, capital of Misthalin. The "
             "Champions' Guild stands to the south-west ('guild').",
        exits={"south": "lumbridge_forest", "north": "varrock_square"}),
    "varrock_square": dict(
        name="Varrock Square",
        desc="A bustling plaza with a fountain. Romeo paces, lovesick, and "
             "townsfolk mill about.",
        exits={"south": "varrock_gate", "west": "varrock_west_bank",
               "east": "varrock_east_bank", "north": "varrock_palace"},
        npc="romeo_juliet", pickpocket=["man", "woman"]),
    "varrock_west_bank": dict(
        name="West Varrock",
        desc="A bank, the sword shop, an anvil for smithing, and Aubury's rune "
             "shop with a portal to the rune essence mine.",
        exits={"east": "varrock_square", "west": "barbarian_village",
               "essence": "essence_mine"},
        bank=True, anvil=True, shop="rune"),
    "varrock_east_bank": dict(
        name="East Varrock",
        desc="A bank near the road north to the Grand Exchange.",
        exits={"west": "varrock_square", "north": "grand_exchange"}, bank=True),
    "grand_exchange": dict(
        name="Grand Exchange",
        desc="Traders from across Gielinor buy and sell here. A bank is on site.",
        exits={"south": "varrock_east_bank"}, bank=True, ge=True),
    "varrock_palace": dict(
        name="Varrock Palace",
        desc="King Roald's palace, patrolled by guards.",
        exits={"south": "varrock_square", "down": "varrock_sewers"},
        monsters=["guard"], pickpocket=["guard"]),
    "essence_mine": dict(
        name="Rune Essence Mine",
        desc="A mystical cavern of pure rune essence. A portal leads back out.",
        exits={"out": "varrock_west_bank"}, rocks=["rune essence"]),
    # ---- Barbarian Village / Edgeville / Wilderness ----------------------
    "barbarian_village": dict(
        name="Barbarian Village",
        desc="Rowdy barbarians, a mine, and a river for fly fishing trout and "
             "salmon.",
        exits={"east": "varrock_west_bank", "west": "falador_east",
               "north": "edgeville", "down": "stronghold_security",
               "agility": "agility_course"},
        rocks=["copper", "tin", "iron", "coal"], fish_tools=["fly"],
        monsters=["barbarian"]),
    "edgeville": dict(
        name="Edgeville",
        desc="A frontier town with a bank and furnace. Vannaka the Slayer "
             "Master is here, and Oziach the armourer keeps a hut by the "
             "river ('hut'). A dungeon lies below, and the Wilderness ditch "
             "is to the north.",
        exits={"south": "barbarian_village", "north": "wilderness_edge",
               "down": "edgeville_dungeon"},
        bank=True, furnace=True, npc="slayer_master", shop="herblore"),
    "edgeville_dungeon": dict(
        name="Edgeville Dungeon",
        desc="A dank dungeon. Hobgoblins and hill giants prowl the dark. A "
             "huge locked door bars the way to a giant's lair — a giant key "
             "would open it.",
        exits={"up": "edgeville", "deeper": "members_dungeon",
               "giant": "giant_lair"},
        monsters=["hobgoblin", "hill giant", "giant spider"]),
    "giant_lair": dict(
        name="Obor's Lair",
        desc="A cavernous vault littered with shattered bones. Obor, the Hill "
             "Giant boss, looms in the gloom.",
        exits={"out": "edgeville_dungeon"},
        monsters=["obor"], key="giant key"),
    "wilderness_edge": dict(
        name="Edge of the Wilderness",
        desc="Past this ditch lies the lawless Wilderness. Dark wizards and "
             "skeletons haunt the wastes. Tread carefully.",
        exits={"south": "edgeville", "deep": "kbd_lair"},
        monsters=["dark wizard", "skeleton", "dark warrior"]),
    # ---- Falador / Dwarven Mine ------------------------------------------
    "falador_east": dict(
        name="East Falador",
        desc="The eastern gate of Falador, with a bank.",
        exits={"east": "barbarian_village", "west": "falador_square"},
        bank=True),
    "falador_square": dict(
        name="Falador",
        desc="The white-walled city of Asgarnia. Doric the dwarf works nearby, "
             "and a mine lies south.",
        exits={"east": "falador_east", "west": "falador_west",
               "south": "dwarven_mine"},
        npc="dorics_quest"),
    "falador_west": dict(
        name="West Falador",
        desc="A bank and the road south toward Rimmington.",
        exits={"east": "falador_square", "south": "rimmington",
               "altar": "air_altar"}, bank=True),
    "dwarven_mine": dict(
        name="Dwarven Mine",
        desc="A deep mine of coal, iron, mithril and gold. Scorpions lurk.",
        exits={"north": "falador_square"},
        rocks=["iron", "coal", "gold", "mithril"], monsters=["scorpion", "dwarf"]),
    # ---- Rimmington / Port Sarim / Karamja -------------------------------
    "rimmington": dict(
        name="Rimmington",
        desc="A small mining village with Doric's anvil. Copper, tin, iron and "
             "clay rocks are here. To the north loom the ruins of Melzar's "
             "Maze ('maze').",
        exits={"north": "falador_west", "east": "port_sarim"},
        rocks=["copper", "tin", "iron", "clay"], anvil=True),
    "port_sarim": dict(
        name="Port Sarim",
        desc="A busy port with a fishing shop and a food shop. Boats sail south "
             "to Karamja, and Klarense tends his ship, the Lady Lumbridge, at "
             "the dock.",
        exits={"west": "rimmington", "south": "karamja_port"},
        shop="fishing"),
    "karamja_port": dict(
        name="Karamja (Musa Point)",
        desc="A tropical island port. Fishing spots line the docks; a volcano "
             "smokes in the distance.",
        exits={"north": "port_sarim"}, fish_tools=["net", "rod"]),
    # ---- New areas ---------------------------------------------------
    "lumbridge_church": dict(
        name="Lumbridge Church",
        desc="A quiet stone church with a graveyard out back. Father Aereck "
             "tends the altar, and prayers can be restored here.",
        exits={"out": "lumbridge_castle"},
        prayer_altar=True, npc="restless_ghost"),
    "varrock_sewers": dict(
        name="Varrock Sewers",
        desc="A reeking warren beneath the palace, crawling with rats, zombies "
             "and giant spiders.",
        exits={"up": "varrock_palace"},
        monsters=["giant rat", "zombie", "giant spider"]),
    "wizard_tower": dict(
        name="Wizard's Tower",
        desc="A tower of mages south of Draynor. Sedridor studies runes in the "
             "basement, and mischievous imps flit about.",
        exits={"north": "draynor_village"},
        monsters=["imp"], npc=["rune_mysteries", "imp_catcher"]),
    "stronghold_security": dict(
        name="Stronghold of Security",
        desc="A monster-filled dungeon beneath Barbarian Village. Minotaurs and "
             "flesh crawlers roam its halls — and treasure awaits the brave.",
        exits={"up": "barbarian_village"},
        monsters=["minotaur", "flesh crawler", "zombie rat"], stronghold=True),
    "air_altar": dict(
        name="Air Altar",
        desc="A mystical altar humming with air magic. Bind rune essence into "
             "air runes here.",
        exits={"out": "falador_west"}, altar="air"),
    # ---- Members areas (require membership) -------------------------------
    "members_dungeon": dict(
        name="Deep Dungeon",
        desc="A forbidding cavern far below Edgeville. Moss giants and demons "
             "lurk in the gloom. (members)",
        exits={"up": "edgeville_dungeon"},
        monsters=["moss giant", "ice giant", "lesser demon", "greater demon"],
        members=True),
    "kbd_lair": dict(
        name="Lair of the King Black Dragon",
        desc="A scorched lair deep in the Wilderness. The King Black Dragon "
             "broods over a hoard of treasure. (members)",
        exits={"out": "wilderness_edge"},
        monsters=["king black dragon"], members=True),
    "agility_course": dict(
        name="Barbarian Agility Course",
        desc="A rickety obstacle course of ropes, beams and ledges. Run laps to "
             "train agility. (members)",
        exits={"out": "barbarian_village"}, members=True, agility_course=True),
}


# ===========================================================================
#  SHOPS
# ===========================================================================
SHOPS = {
    "general": {"bread": 12, "pot": 1, "bucket": 2, "tinderbox": 1, "hammer": 1,
                "shears": 1, "chisel": 1, "needle": 1, "thread": 5},
    "scimitar": {"bronze scimitar": 32, "iron scimitar": 112, "steel scimitar": 400,
                 "mithril scimitar": 1300},
    "rune": {"air rune": 4, "water rune": 4, "earth rune": 4, "fire rune": 4,
             "mind rune": 3, "body rune": 3, "chaos rune": 90, "nature rune": 180,
             "law rune": 240},
    "fishing": {"small fishing net": 5, "fishing rod": 5, "fly fishing rod": 5,
                "harpoon": 5, "feather": 2},
    "herblore": {"vial of water": 2, "eye of newt": 3, "limpwurt root": 25,
                 "snape grass": 30, "unicorn horn dust": 20, "chocolate dust": 8,
                 "white berries": 40, "grimy guam": 8, "grimy marrentill": 10,
                 "grimy tarromin": 14},
}


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


def _player_attack(p, m):
    """Return (kind, atype, att_roll, max_hit) for one player attack, or None."""
    if p.style == "ranged":
        bow = p.equipment["weapon"]
        ammo = p.equipment["ammo"]
        if not bow or "arange" not in ITEMS[bow].get("equip", {}):
            say("You need a bow equipped to use ranged.")
            return None
        if not ammo or p.count_ammo() <= 0:
            say("You're out of arrows!")
            return None
        acc = p.equip_bonus("arange")
        rstr = p.equip_bonus("rstr")
        eff = p.lvl("ranged") + 9
        att_roll = eff * (acc + 64)
        max_hit = int(0.5 + eff * (rstr + 64) / 640)
        p.take(ammo)  # consume one arrow
        if p.count(ammo) == 0:
            p.equipment["ammo"] = None
        return ("ranged", "ranged", att_roll, max_hit)
    if p.style == "magic":
        spell = SPELLS.get(p.autocast)
        if not spell or spell["type"] != "combat":
            say("Set a combat spell with 'autocast <spell>'.")
            return None
        if p.lvl("magic") < spell["lvl"]:
            say(f"You need magic level {spell['lvl']} to cast {p.autocast}.")
            return None
        if not _consume_runes(p, spell["runes"]):
            say(f"You don't have the runes for {p.autocast}.")
            return None
        att_roll = (p.lvl("magic") + 9) * (p.equip_bonus("amagic") + 64)
        return ("magic", "magic", att_roll, spell["max"])
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
    task = getattr(p, "slayer_task", None)    # slayer helmet: on-task ferocity
    if task and task.get("remaining", 0) > 0 and m["name"] == task.get("monster") \
            and p.equipment.get("head") == "slayer helmet":
        att_roll = int(att_roll * 1.15)
        max_hit = max(1, int(max_hit * 1.15))
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
        if m["cur"] <= 0 and m.get("transform") and not m.get("phase2"):
            m["phase2"] = True
            m["cur"] = m["hp"]
            m["flying"] = True
            say("The carapace SPLITS — the Kalphite Queen sheds her shell "
                "and takes wing, reborn!", "bmagenta", "bold")
        if m["cur"] <= 0 and m.get("finisher") and not p.has(m["finisher"]):
            m["cur"] = max(1, int(m["hp"] * 0.3))
            print("  " + paint(f"The {m['name']} starts to crumble \u2014 "
                               f"then its stone knits back together! "
                               f"(finish it with a {m['finisher']})",
                               "byellow"))
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
    """Dragonfire burns through armour — unless an anti-dragon shield soaks it."""
    if p.equipment.get("shield") == "anti-dragon shield":
        print("  " + paint("Your anti-dragon shield deflects the worst of the "
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
        show_art(ART_SWORDS, "grey")
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
        show_art(ART_SWORDS, "grey")
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
                   "flee. (stats/inventory are free to check.)", "grey")
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
    if r.get("monsters"):
        services.append(paint("monsters: " + ", ".join(r["monsters"]), "bred"))
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
    cmd_look(p, "")
    _ambient(p)
    _maybe_ambush(p)


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
    p.equip_item(item)


def cmd_unequip(p, arg):
    slot = arg.strip().lower()
    if slot not in EQUIP_SLOTS:
        say(f"Slots: {', '.join(EQUIP_SLOTS)}")
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
            castable = [n for n, d in SPELLS.items() if d["type"] == "combat"
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
    if spell not in SPELLS or SPELLS[spell]["type"] != "combat":
        combat_spells = [s for s in SPELLS if SPELLS[s]["type"] == "combat"]
        say("Combat spells: " + ", ".join(combat_spells))
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
    tree = arg.strip().lower() or trees[0]
    if tree not in trees:
        say(f"No {tree} tree here. Available: {', '.join(trees)}")
        return
    if not p.find_tool("axe"):
        say("You need an axe.")
        return
    product, req, xp = TREES[tree]
    if p.lvl("woodcutting") < req:
        say(f"You need woodcutting level {req} to chop {tree}.")
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
    rock = arg.strip().lower() or rocks[0]
    if rock not in rocks:
        say(f"No {rock} here. Available: {', '.join(rocks)}")
        return
    if rock != "rune essence" and not p.find_tool("pickaxe"):
        say("You need a pickaxe.")
        return
    product, req, xp = ROCKS[rock]
    if p.lvl("mining") < req:
        say(f"You need mining level {req} to mine {rock}.")
        return
    say(f"You swing your pickaxe at the {rock} rock...")
    if random.random() < gather_chance(p.lvl("mining"), req):
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
            "tinderbox).")
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
        say("You need a furnace.")
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
        say("You need an anvil.")
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
        say("There's no bank here.")
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
        say("There's no bank here.")
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
        say(f"You have no {item}.")
        return
    q = p.count(item) if qarg == "all" else min(int(qarg), p.count(item))
    p.take(item, q)
    p.bank[item] = p.bank.get(item, 0) + q
    say(f"Deposited {item} x{q}.")


def cmd_withdraw(p, arg):
    if not ROOMS[p.location].get("bank"):
        say("There's no bank here.")
        return
    arg = arg.strip().lower()
    parts = arg.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].isdigit() or parts[1] == "all"):
        item, qarg = parts
    else:
        item, qarg = arg, "1"
    if p.bank.get(item, 0) <= 0:
        say(f"You have no {item} in the bank.")
        return
    q = p.bank[item] if qarg == "all" else min(int(qarg), p.bank[item])
    p.bank[item] -= q
    if p.bank[item] <= 0:
        del p.bank[item]
    p.add(item, q)
    say(f"Withdrew {item} x{q}.")


def cmd_shop(p, _a):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here.")
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
        say(f"You have no {item}.")
        return
    q = p.count(item) if qarg == "all" else min(int(qarg), p.count(item))
    p.take(item, q)
    say(f"You drop {item} x{q}." + (" A seagull swoops in to inspect it."
        if "karamja" in p.location or "sarim" in p.location else ""))


def cmd_buy(p, arg):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here.")
        return
    item, qty = _parse_item_qty(arg)
    if item not in SHOPS[shop]:
        say("The shopkeeper doesn't sell that.")
        return
    cost = SHOPS[shop][item] * qty
    if not p.has("coins", cost):
        say(f"That costs {cost} coins; you can't afford it.")
        return
    p.take("coins", cost)
    p.add(item, qty)
    say(f"You buy {item} x{qty} for {cost} coins.")


def cmd_sell(p, arg):
    shop = ROOMS[p.location].get("shop")
    if not shop:
        say("There's no shop here.")
        return
    item, qty = _parse_item_qty(arg)
    if not p.has(item, qty):
        say(f"You don't have {qty}x {item}.")
        return
    price = max(1, int(ITEMS.get(item, {}).get("value", 1) * 0.4)) * qty
    p.take(item, qty)
    p.add("coins", price)
    say(f"You sell {item} x{qty} for {price} coins.")


def cmd_ge(p, arg):
    if not ROOMS[p.location].get("ge"):
        say("You must be at the Grand Exchange.")
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
        say(f"No such item: {item}")
        return
    price = ITEMS[item]["value"] * qty
    if action == "buy":
        if not p.has("coins", price):
            say(f"That costs {price} coins; you can't afford it.")
            return
        p.take("coins", price)
        p.add(item, qty)
        say(f"Bought {item} x{qty} for {price} coins.")
    elif action == "sell":
        if not p.has(item, qty):
            say(f"You don't have {qty}x {item}.")
            return
        p.take(item, qty)
        p.add("coins", price)
        say(f"Sold {item} x{qty} for {price} coins.")
    else:
        say("Use: ge buy <item> [n] | ge sell <item> [n]")


# --- combat & farm actions ------------------------------------------------
def _handle_death(p):
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
    r = ROOMS[p.location]
    monsters = r.get("monsters", [])
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
            "EGG, a BUCKET OF MILK and a POT OF FLOUR. The farm is east!\"")
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
        p.quests["vampyre_slayer"] = "started"
        # add the count to the manor
        if "count draynor" not in ROOMS["draynor_manor"]["monsters"]:
            ROOMS["draynor_manor"]["monsters"].append("count draynor")
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


def _quest_on_kill(p, target):
    if target == "count draynor" and _q(p, "vampyre_slayer") == "started":
        show_art(ART_QUEST, "gold", center=True)
        banner("QUEST COMPLETE: Vampyre Slayer", color="byellow", line_color="gold")
        say("With the stake through its heart, Count Draynor crumbles to dust! "
            "4825 attack xp awarded.")
        p.gain_xp("attack", 4825)
        p.quests["vampyre_slayer"] = "complete"
        ROOMS["draynor_manor"]["monsters"].remove("count draynor")
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
        if "temple guardian" in ROOMS["paterdomus"]["monsters"]:
            ROOMS["paterdomus"]["monsters"].remove("temple guardian")
        say("The guardian collapses into grave-dust. Tell Drezel the crypt "
            "is safe!", "bgreen")
    if target == "the draugen" and _q(p, "fremennik_trials") == "hunt":
        p.quests["fremennik_trials"] = "hunted"
        if "the draugen" in ROOMS["rock_crab_coast"]["monsters"]:
            ROOMS["rock_crab_coast"]["monsters"].remove("the draugen")
        say("The Draugen unravels into cold sea-mist. Brundt will want to "
            "hear of this!", "bgreen")
    if target == "dad" and _q(p, "troll_stronghold") == "started":
        p.quests["troll_stronghold"] = "dad"
        say("DAD crashes down and the gate-hall stands open. Somewhere "
            "deeper, chains rattle — find Godric! ('talk godric')",
            "bgreen")
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


# ===========================================================================
#  ACHIEVEMENTS
# ===========================================================================
ACHIEVEMENTS = {
    "first_blood":  ("First Blood", "Defeat your first monster."),
    "apprentice":   ("Apprentice", "Reach total level 100."),
    "adventurer":   ("Adventurer", "Reach total level 500."),
    "veteran":      ("Veteran", "Reach total level 1000."),
    "skill_master": ("Skill Master", "Reach level 99 in any skill."),
    "quester":      ("Quester", "Complete 3 quests."),
    "hero":         ("Hero of Gielinor", "Complete every quest."),
    "herbalist":    ("Herbalist", "Brew your first potion."),
    "dragonslayer": ("Dragonslayer", "Defeat the King Black Dragon."),
    "giant_slayer": ("Giant Slayer", "Defeat Obor, the Hill Giant boss."),
    "crandor_saved": ("Crandor's Saviour", "Complete the Dragon Slayer quest."),
    "fire_cape": ("JalYt Champion", "Conquer the Fight Caves and earn the "
                  "fire cape."),
    "grave_robber": ("Grave Robber", "Put all six Barrows brothers to rest "
                     "and loot the chest."),
    "whack_a_mole": ("Whack-a-Mole", "Defeat the Giant Mole beneath "
                     "Falador Park."),
    "green_thumb": ("Green Thumb", "Harvest 25 crops from your patches."),
    "god_slayer": ("God Slayer", "Defeat all four generals of the God Wars "
                   "Dungeon."),
    "taskmaster": ("Taskmaster", "Reach a 10-task slayer streak."),
    "hive_slayer": ("Hive Slayer", "Defeat both bodies of the Kalphite "
                    "Queen."),
    "king_slayer": ("Kingsbane", "Defeat all three Dagannoth Kings."),
    "infernal": ("The Infernal", "Defeat TzKal-Zuk at the bottom of the "
                 "Inferno."),
    "rich":         ("Wealthy", "Hold 100,000 coins."),
}


def _earned_achievements(p):
    got = set()
    total = sum(p.base_lvl(s) for s in SKILLS)
    if getattr(p, "kills", 0) >= 1:
        got.add("first_blood")
    if total >= 100:
        got.add("apprentice")
    if total >= 500:
        got.add("adventurer")
    if total >= 1000:
        got.add("veteran")
    if any(p.base_lvl(s) >= 99 for s in SKILLS):
        got.add("skill_master")
    done = sum(1 for k in ALL_QUESTS if _q(p, k) == "complete")
    if done >= 3:
        got.add("quester")
    if done >= len(ALL_QUESTS):
        got.add("hero")
    if getattr(p, "potions_made", 0) >= 1:
        got.add("herbalist")
    bosses = getattr(p, "bosses", [])
    if "king black dragon" in bosses:
        got.add("dragonslayer")
    if "obor" in bosses:
        got.add("giant_slayer")
    if _q(p, "dragon_slayer") == "complete":
        got.add("crandor_saved")
    if "tztok-jad" in bosses:
        got.add("fire_cape")
    if getattr(p, "barrows_loots", 0) >= 1:
        got.add("grave_robber")
    if "giant mole" in bosses:
        got.add("whack_a_mole")
    if getattr(p, "crops", 0) >= 25:
        got.add("green_thumb")
    if all(g in bosses for g in ("general graardor", "kree'arra",
                                 "k'ril tsutsaroth", "commander zilyana")):
        got.add("god_slayer")
    if getattr(p, "task_streak", 0) >= 10:
        got.add("taskmaster")
    if "kalphite queen" in bosses:
        got.add("hive_slayer")
    if all(k in bosses for k in ("dagannoth rex", "dagannoth prime",
                                 "dagannoth supreme")):
        got.add("king_slayer")
    if "tzkal-zuk" in bosses:
        got.add("infernal")
    if p.coins >= 100000:
        got.add("rich")
    return got


def _check_achievements(p):
    """Unlock + announce any newly earned achievements."""
    have = getattr(p, "achievements", None)
    if have is None:
        p.achievements = have = []
    for key in _earned_achievements(p):
        if key not in have:
            have.append(key)
            title, desc = ACHIEVEMENTS[key]
            print()
            banner("ACHIEVEMENT UNLOCKED", color="gold", line_color="byellow")
            print("  " + paint("★ " + title, "byellow", "bold")
                  + paint("  —  " + desc, "grey"))


def cmd_achievements(p, _a):
    have = set(getattr(p, "achievements", []))
    banner(f"Achievements  ({len(have)}/{len(ACHIEVEMENTS)})", color="gold")
    for key, (title, desc) in ACHIEVEMENTS.items():
        if key in have:
            print("  " + paint("★ ", "byellow")
                  + paint(f"{title:18}", "byellow", "bold") + paint(desc, "grey"))
        else:
            print("  " + paint("☆ ", "grey")
                  + paint(f"{title:18}", "grey") + paint(desc, "grey"))


def cmd_task(p, _a):
    if not getattr(p, "members", False):
        say("Slayer is members-only. Type 'membership' to unlock it.", "bmagenta")
        return
    banner("Slayer", color="teal", line_color="teal")
    print("  " + paint(f"Slayer level {p.lvl('slayer')}", "teal")
          + paint(f"    Points: {p.slayer_points}", "white"))
    t = getattr(p, "slayer_task", None)
    if t and t["remaining"] > 0:
        print("  " + paint(f"Task: slay {t['remaining']}/{t['amount']} "
                           f"{t['monster']}s", "white"))
        locs = sorted({ROOMS[k]["name"] for k, r in ROOMS.items()
                       if t["monster"] in r.get("monsters", [])})
        if locs:
            print("  " + paint("Found at: " + ", ".join(locs[:4]), "grey"))
    else:
        print("  " + paint("No active task — see Vannaka, the Slayer Master in "
                           "Edgeville.", "grey"))
    print("  " + paint(f"Task streak: {getattr(p, 'task_streak', 0)} "
                       "(bonus points at every 5th and 10th)", "teal"))
    print("  " + paint("Spend points with 'slayerbuy' (helmet, gear, xp, "
                       "skips \u2014 skipping resets your streak).", "grey"))


def cmd_search(p, _a):
    loc = p.location
    if loc == "draynor_village" and _q(p, "romeo_juliet") == "started" \
            and not p.has("message"):
        p.add("message")
        say("You find Juliet here. She gives you a heartfelt message for Romeo. "
            "Take it back to Varrock Square!")
        return
    if loc == "varrock_sewers" and _q(p, "restless_ghost") == "started" \
            and not p.has("ghost's skull"):
        p.add("ghost's skull")
        say("Among the filth you spot a grinning skull — the ghost's! You pocket it.")
        return
    if loc == "draynor_manor" and _q(p, "ernest_chicken") == "started":
        for part in ["oil can", "pressure gauge", "rubber tube"]:
            if not p.has(part):
                p.add(part)
                say(f"You rummage through the manor and find a {part}.")
                return
    if _q(p, "dragon_slayer") == "maps":
        if loc == "melzars_maze" and not p.has("melzar's map piece"):
            p.add("melzar's map piece")
            say("Behind a crumbling wall you find Melzar's old strongbox — "
                "inside lies MELZAR'S MAP PIECE, one third of the route to "
                "Crandor!", "bgreen")
            return
        if loc == "draynor_manor" and not p.has("lozar's map piece"):
            p.add("lozar's map piece")
            say("In the manor's cellar a magic chest clicks open at your "
                "touch — LOZAR'S MAP PIECE is yours!", "bgreen")
            return
    if loc == "black_knights_fortress" and _q(p, "black_knights") == "infiltrate":
        if p.has("cabbage"):
            p.take("cabbage")
            p.quests["black_knights"] = "sabotaged"
            say("You creep to a listening-hole. Below, a witch stirs a vast "
                "cauldron — the invincibility potion! You drop your CABBAGE "
                "down the chimney. The brew hisses, turns pink, and curdles. "
                "Sabotage complete — report to Sir Amik Varze!", "bgreen")
        else:
            say("You find the chimney over the witch's cauldron. Something "
                "vile dropped in would ruin the potion forever... a CABBAGE, "
                "say. (The general store sells them.)", "byellow")
        return
    if loc == "draynor_jail" and _q(p, "prince_ali") == "rescue":
        p.take("blonde wig")
        p.take("bronze key")
        p.quests["prince_ali"] = "freed"
        say("You slip the bronze key into the lock while Lady Keli's back is "
            "turned. Prince Ali dons the wig and strolls out disguised — free! "
            "Return to Osman at the Al Kharid palace.", "bgreen")
        return
    if loc == "baxtorian_falls" and _q(p, "waterfall_quest") == "started":
        p.add("glarial's amulet")
        p.quests["waterfall_quest"] = "amulet"
        say("Beneath a moss-grown tombstone you find GLARIAL'S AMULET. The "
            "roar of the falls seems to open like a door — the cave behind "
            "the water will admit you now ('cave').", "bgreen")
        return
    if loc == "waterfall_cave" and _q(p, "waterfall_quest") == "amulet":
        _complete_banner("Waterfall Quest")
        say("Past the sleeping guardians you set Glarial's amulet on the "
            "altar of Baxtorian. The chalice fills with light — and with "
            "understanding. 13,750 attack AND strength xp awarded!",
            "gold", "bold")
        p.gain_xp("attack", 13750)
        p.gain_xp("strength", 13750)
        p.quests["waterfall_quest"] = "complete"
        return
    if loc == "camelot" and _q(p, "merlins_crystal") in ("excalibur",
                                                         "shatter"):
        if p.has("excalibur") or "excalibur" in p.equipment.values():
            _complete_banner("Merlin's Crystal")
            say("You climb the tower and strike the crystal with EXCALIBUR. "
                "It rings once, like a bell, and falls away in shards. "
                "Merlin steps out, brushing centuries off his robes: "
                "\"Took your time.\" King Arthur is overjoyed!",
                "gold", "bold")
            p.quests["merlins_crystal"] = "complete"
        else:
            say("The crystal atop the tower shrugs off everything you try. "
                "Only EXCALIBUR will crack it.", "byellow")
        return
    say("You find nothing of interest.")


# ===========================================================================
#  SAVE / LOAD
# ===========================================================================
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")


def serialize(p):
    """Return a plain-dict snapshot of a player (for file or browser saves)."""
    return {"name": p.name, "location": p.location, "skills": p.skills,
            "hp": p.hp, "inventory": p.inventory, "bank": p.bank,
            "equipment": p.equipment, "style": p.style,
            "train": getattr(p, "train", "shared"),
            "attack_type": getattr(p, "attack_type", "slash"), "autocast": p.autocast,
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
            "tips_seen": list(getattr(p, "tips_seen", []))}


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
    # restore quest-spawned monsters
    if p.quests.get("vampyre_slayer") == "started" and \
            "count draynor" not in ROOMS["draynor_manor"]["monsters"]:
        ROOMS["draynor_manor"]["monsters"].append("count draynor")
    if p.quests.get("priest_in_peril") == "guardian" and \
            "temple guardian" not in ROOMS["paterdomus"]["monsters"]:
        ROOMS["paterdomus"]["monsters"].append("temple guardian")
    if p.quests.get("fremennik_trials") == "hunt" and \
            "the draugen" not in ROOMS["rock_crab_coast"]["monsters"]:
        ROOMS["rock_crab_coast"]["monsters"].append("the draugen")
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


# ===========================================================================
#  HELP & DISPATCH
# ===========================================================================
def cmd_help(_p, _a):
    banner("Commands")
    groups = {
        "Move": "look (l), go <dir>, n/s/e/w, up/down, exits",
        "Info": "me (character card), stats [skill], inventory (i), "
                "equipment, quests, examine <item|creature>, bestiary",
        "Combat": "fight [monster], spec (special attack), "
                  "train <attack|strength|defence|shared>, "
                  "style <melee|ranged|magic|stab|slash|crush>, "
                  "autocast <spell>, eat [food], drink [potion]",
        "Gear": "equip <item>, unequip <slot>, drop <item> [n|all]",
        "Skilling": "chop [tree], mine [rock], fish, cook [food], light [logs], "
                    "bury [bones], smelt <bar>, smith <metal> <item>, spin, tan, "
                    "craft <item>, cut <gem>, craftrune, skillcape <skill>, "
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
        ("Move", "type a direction (n/s/e/w) — or tap the arrow buttons."),
        ("Look", "'look' shows what's here, who's around, and your exits."),
        ("Fight", "'fight chicken' (or tap a creature). Win XP and loot."),
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

def _best_gear_for_style(style):
    """Best-in-slot item per equipment slot for a combat style (ignores reqs)."""
    def defsum(eq):
        return sum(eq.get(k, 0) for k in ("dstab", "dslash", "dcrush",
                                          "dmagic", "drange"))
    def score(eq):
        if style == "ranged":
            return eq.get("arange", 0) * 2 + eq.get("rstr", 0) * 3 + defsum(eq) * 0.05
        if style == "magic":
            return eq.get("amagic", 0) * 3 + eq.get("mdmg", 0) * 2 + defsum(eq) * 0.05
        best_atk = max(eq.get("astab", 0), eq.get("aslash", 0), eq.get("acrush", 0))
        return best_atk + eq.get("str", 0) * 2 + defsum(eq) * 0.05
    best, best_score = {}, {}
    for name, info in ITEMS.items():
        eq = info.get("equip")
        slot = eq.get("slot") if eq else None
        if not slot:
            continue
        sc = score(eq)
        if sc <= 0:                       # irrelevant to this style
            continue
        if slot not in best_score or sc > best_score[slot]:
            best_score[slot], best[slot] = sc, name
    # a two-handed weapon leaves no hand for a shield
    w = best.get("weapon")
    if w and ITEMS[w].get("equip", {}).get("two_handed"):
        best.pop("shield", None)
    return best


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
        combat = [s for s, d in SPELLS.items() if d.get("type") == "combat"]
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


HANDLERS = {
    "look": cmd_look, "l": cmd_look, "exits": cmd_look,
    "go": cmd_go,
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
    "eat": cmd_eat,
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
}

# verbs kept out of the web tab-completion list (dev tools; still runnable)
_HIDDEN_VERBS = {"maxme", "devmax", "dev"}


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
             "clean", "tan", "spin"}
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
    if getattr(player, "auto", None) is not None:
        player.auto = None
        say("(You break off the auto-fight.)", "byellow")
        if raw.lower() == "stop":
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
    if not raw:
        return True
    parts = raw.split(maxsplit=1)
    verb = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    if verb in ("quit", "exit", "q"):
        say("Farewell, adventurer. May your bank be ever full.", "gold")
        return False
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
    for m in r.get("monsters", []):
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


# ===========================================================================
#  WORLD EXPANSION  (Kandarin route, Karamja, guilds, wilderness, fishing)
# ===========================================================================
# --- Catherby fishing food (lobster / tuna / swordfish) -------------------
add_item("lobster pot", 20, tool="cage")
for _raw, _cooked, _heal, _val, _cxp, _clvl in [
        ("raw tuna", "tuna", 10, 60, 100, 30),
        ("raw lobster", "lobster", 12, 80, 120, 40),
        ("raw swordfish", "swordfish", 14, 100, 140, 50)]:
    add_item(_raw, _val // 2)
    add_item(_cooked, _val, heal=_heal)
    add_item("burnt " + _cooked, 1)
    RAW_TO_COOKED[_raw] = (_cooked, "burnt " + _cooked, _clvl)
    COOK_XP[_raw] = _cxp
FISH["harpoon"] = [("raw tuna", 35, 80), ("raw swordfish", 50, 100)]
FISH["cage"] = [("raw lobster", 40, 90)]
SHOPS["fishing"]["harpoon"] = 5
SHOPS["fishing"]["lobster pot"] = 20
SHOPS["crafting"] = {"needle": 1, "thread": 5, "chisel": 1, "ball of wool": 12,
                     "leather": 20}
PICKPOCKET["monk"] = (5, 12, 20, 2)


def _add_mob(name, s, drops, members=False, rank="hard"):
    m = mob(s["hp"], s["att"], s["def"], s["maxhit"], drops, members=members)
    m["rank"] = rank
    m["level"] = s.get("cb")
    m["abonus"] = s.get("abonus", 0)
    m["atktype"] = s.get("atktype", ["crush"])
    m["weakness"] = s.get("weak", "crush")
    m["dbonus"] = {"stab": s["dstab"], "slash": s["dslash"], "crush": s["dcrush"],
                   "magic": s["dmagic"], "ranged": s["drange"]}
    MONSTERS[name] = m


_add_mob("chaos druid", {"abonus":0,"atktype":["crush"],"att":8,"cb":13,"dcrush":0,"def":12,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":20,"maxhit":2,"str":8,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 1, 28, 0.7),
    ("grimy guam", 1, 2, 0.3), ("grimy marrentill", 1, 2, 0.25),
    ("grimy tarromin", 1, 1, 0.15), ("grimy ranarr", 1, 1, 0.05),
    ("law rune", 1, 3, 0.1)], members=True, rank="medium")
_add_mob("white wolf", {"abonus":0,"atktype":["stab"],"att":20,"cb":25,"dcrush":0,"def":22,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":34,"maxhit":3,"str":16,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 1, 20, 0.5)],
    members=True, rank="hard")
_add_mob("deadly red spider", {"abonus":0,"atktype":["stab"],"att":30,"cb":34,"dcrush":7,"def":30,"dmagic":12,"drange":16,"dslash":16,"dstab":15,"hp":35,"maxhit":3,"str":25,"weak":"crush"}, [("bones", 1, 1, 1.0), ("coins", 5, 40, 0.6),
    ("grimy harralander", 1, 2, 0.2), ("steel arrow", 5, 15, 0.3)],
    members=True, rank="hard")
_add_mob("jogre", {"abonus":22,"atktype":["crush"],"att":43,"cb":53,"dcrush":0,"def":43,"dmagic":0,"drange":0,"dslash":0,"dstab":0,"hp":60,"maxhit":7,"str":43,"weak":"stab"}, [("bones", 1, 1, 1.0), ("big bones", 1, 1, 0.3),
    ("coins", 10, 60, 0.8)], members=True, rank="elite")
_add_mob("paladin", {"abonus":0,"atktype":["slash"],"att":134,"cb":49,"dcrush":40,"def":28,"dmagic":30,"drange":20,"dslash":40,"dstab":20,"hp":55,"maxhit":6,"str":48,"weak":"stab"}, [("bones", 1, 1, 1.0), ("coins", 80, 220, 1.0),
    ("law rune", 1, 4, 0.2)], members=True, rank="elite")

# --- New rooms ------------------------------------------------------------
ROOMS.update({
    "mining_guild": dict(name="Mining Guild",
        desc="A bustling guild mine rich with coal, gold, mithril and "
             "adamantite ore.",
        exits={"out": "dwarven_mine"},
        rocks=["coal", "gold", "mithril", "adamantite"]),
    "crafting_guild": dict(name="Crafting Guild",
        desc="Master crafters work here. A tannery, a spinning wheel and a "
             "supply shop serve members of the guild.",
        exits={"out": "falador_west"},
        tanner=True, spinning_wheel=True, shop="crafting"),
    "monastery": dict(name="Edgeville Monastery",
        desc="A peaceful monastery. Monks tend an altar where prayer can be "
             "restored — and their pockets jingle with coin.",
        exits={"east": "edgeville"},
        prayer_altar=True, pickpocket=["monk"]),
    "deep_wilderness": dict(name="Deep Wilderness",
        desc="The lawless wastes stretch north. Dark warriors and giants roam, "
             "and the air hums with danger.",
        exits={"south": "wilderness_edge"},
        monsters=["dark warrior", "hill giant", "hobgoblin"]),
    # ---- Kandarin (members) via Taverley -----------------------------------
    "taverley": dict(name="Taverley",
        desc="A druidic village west of Falador, gateway to Kandarin. A bank "
             "stands by the road, and a dungeon yawns below. (members)",
        exits={"east": "falador_west", "down": "taverley_dungeon",
               "west": "white_wolf_mountain"},
        bank=True, members=True),
    "taverley_dungeon": dict(name="Taverley Dungeon",
        desc="A sprawling cavern. Chaos druids gather herbs while giants stomp "
             "in the dark. (members)",
        exits={"up": "taverley"},
        monsters=["chaos druid", "hill giant", "deadly red spider"], members=True),
    "white_wolf_mountain": dict(name="White Wolf Mountain",
        desc="A snow-capped pass between Taverley and Catherby, prowled by "
             "white wolves. (members)",
        exits={"east": "taverley", "west": "catherby"},
        monsters=["white wolf"], members=True),
    "catherby": dict(name="Catherby",
        desc="A seaside town with the finest fishing in Kandarin — tuna, "
             "swordfish and lobster. A bank sits by the shore. (members)",
        exits={"east": "white_wolf_mountain", "north": "seers_village"},
        bank=True, fish_tools=["net", "harpoon", "cage"], members=True),
    "seers_village": dict(name="Seers' Village",
        desc="A quiet village beside Camelot, with a bank and roads west to "
             "Ardougne. (members)",
        exits={"south": "catherby", "west": "ardougne"},
        bank=True, members=True),
    "ardougne": dict(name="Ardougne",
        desc="A grand split city. The market square bustles with stalls and "
             "pickpocketable crowds; paladins patrol the palace. (members)",
        exits={"east": "seers_village"},
        bank=True, pickpocket=["man", "woman"], monsters=["paladin"],
        members=True),
    # ---- Karamja extension (members) ---------------------------------------
    "brimhaven": dict(name="Brimhaven",
        desc="A tropical port on eastern Karamja. Jogres lumber through the "
             "jungle and a bank serves adventurers. (members)",
        exits={"west": "karamja_port"},
        bank=True, monsters=["jogre", "scorpion"], members=True),
    "karamja_volcano": dict(name="Karamja Volcano",
        desc="A smoking caldera riddled with lava tunnels and deadly red "
             "spiders. (members)",
        exits={"out": "karamja_port"},
        monsters=["deadly red spider"], members=True),
})

# --- Wire new exits into existing rooms -----------------------------------
ROOMS["dwarven_mine"]["exits"]["guild"] = "mining_guild"
ROOMS["falador_west"]["exits"]["guild"] = "crafting_guild"
ROOMS["falador_west"]["exits"]["west"] = "taverley"
ROOMS["edgeville"]["exits"]["west"] = "monastery"
ROOMS["wilderness_edge"]["exits"]["north"] = "deep_wilderness"
ROOMS["karamja_port"]["exits"]["east"] = "brimhaven"
ROOMS["karamja_port"]["exits"]["volcano"] = "karamja_volcano"

# --- New travel destinations ----------------------------------------------
TRAVEL_HUBS.update({"taverley": "taverley", "catherby": "catherby",
                    "seers village": "seers_village", "seers": "seers_village",
                    "ardougne": "ardougne", "brimhaven": "brimhaven"})
TRAVEL_NAMES.extend(["Taverley", "Catherby", "Seers' Village", "Ardougne",
                     "Brimhaven"])

# ===========================================================================
#  COMBAT-TRIANGLE GEAR EXPANSION  (real OSRS gear for all 3 styles)
# ===========================================================================
# Obtainable at the Grand Exchange ('ge buy <item>'); top-tier also drops.
add_item('dragon scimitar', 100000, equip={'astab': 8, 'aslash': 67, 'acrush': -2, 'dslash': 1, 'str': 66, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('abyssal whip', 120001, equip={'aslash': 82, 'str': 82, 'slot': 'weapon', 'req': {'attack': 70}}, members=True)
add_item('dragon mace', 50000, equip={'astab': 40, 'aslash': -2, 'acrush': 60, 'str': 55, 'prayer': 5, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('dragon longsword', 100000, equip={'astab': 58, 'aslash': 69, 'acrush': -2, 'dslash': 3, 'dcrush': 2, 'str': 71, 'slot': 'weapon', 'req': {'attack': 60}}, members=True)
add_item('granite maul', 50000, equip={'acrush': 81, 'str': 79, 'slot': 'weapon', 'req': {'attack': 50, 'strength': 50}}, members=True)
add_item('dragon platelegs', 270000, equip={'amagic': -21, 'arange': -11, 'dstab': 68, 'dslash': 66, 'dcrush': 63, 'dmagic': -4, 'drange': 65, 'slot': 'legs', 'req': {'defence': 60}}, members=True)
add_item('dragon chainbody', 250000, equip={'amagic': -15, 'dstab': 81, 'dslash': 93, 'dcrush': 98, 'dmagic': -3, 'drange': 82, 'slot': 'body', 'req': {'defence': 60}}, members=True)
add_item('dragon kiteshield', 1600000, equip={'amagic': -8, 'arange': -3, 'dstab': 56, 'dslash': 60, 'dcrush': 58, 'dmagic': -1, 'drange': 58, 'slot': 'shield', 'req': {'defence': 60}}, members=True)
add_item('dragon boots', 20000, equip={'amagic': -3, 'arange': -1, 'dstab': 16, 'dslash': 17, 'dcrush': 18, 'str': 4, 'slot': 'boots', 'req': {'defence': 60}}, members=True)
add_item('berserker helm', 60000, equip={'amagic': -5, 'arange': -5, 'dstab': 31, 'dslash': 29, 'dcrush': 33, 'drange': 30, 'str': 3, 'slot': 'head', 'req': {'defence': 45}}, members=True)
add_item('maple shortbow', 400, equip={'arange': 29, 'slot': 'weapon', 'req': {'ranged': 30}})
add_item('magic shortbow', 1600, equip={'arange': 69, 'slot': 'weapon', 'req': {'ranged': 50}}, members=True)
add_item('rune crossbow', 16200, equip={'arange': 90, 'slot': 'weapon', 'req': {'ranged': 61}}, members=True)
add_item('runite bolts', 300, equip={'rstr': 115, 'slot': 'ammo', 'req': {'ranged': 61}}, members=True)
add_item('adamant bolts', 58, equip={'rstr': 100, 'slot': 'ammo', 'req': {'ranged': 36}}, members=True)
add_item("green d'hide body", 7800, equip={'amagic': -15, 'arange': 15, 'dstab': 18, 'dslash': 27, 'dcrush': 24, 'dmagic': 20, 'drange': 35, 'slot': 'body', 'req': {'ranged': 40, 'defence': 40}})
add_item("green d'hide chaps", 3900, equip={'amagic': -10, 'arange': 8, 'dstab': 12, 'dslash': 15, 'dcrush': 18, 'dmagic': 8, 'drange': 17, 'slot': 'legs', 'req': {'ranged': 40}})
add_item("green d'hide vambraces", 2500, equip={'amagic': -10, 'arange': 8, 'dstab': 1, 'dslash': 2, 'dcrush': 2, 'dmagic': 2, 'slot': 'gloves', 'req': {'ranged': 40}})
add_item('coif', 200, equip={'amagic': -1, 'arange': 2, 'dstab': 4, 'dslash': 6, 'dcrush': 8, 'dmagic': 4, 'drange': 4, 'slot': 'head'})
add_item('snakeskin body', 1250, equip={'amagic': -5, 'arange': 12, 'dstab': 25, 'dslash': 28, 'dcrush': 32, 'dmagic': 15, 'drange': 35, 'slot': 'body', 'req': {'ranged': 30, 'defence': 30}}, members=True)
add_item('mystic hat', 15000, equip={'amagic': 4, 'dmagic': 4, 'slot': 'head', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic robe top', 120000, equip={'amagic': 20, 'dmagic': 20, 'slot': 'body', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic robe bottom', 80000, equip={'amagic': 15, 'dmagic': 15, 'slot': 'legs', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic gloves', 10000, equip={'amagic': 3, 'dmagic': 3, 'slot': 'gloves', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('mystic boots', 10000, equip={'amagic': 3, 'dmagic': 3, 'slot': 'boots', 'req': {'magic': 40, 'defence': 20}}, members=True)
add_item('amulet of glory', 17625, equip={'astab': 10, 'aslash': 10, 'acrush': 10, 'amagic': 10, 'arange': 10, 'dstab': 3, 'dslash': 3, 'dcrush': 3, 'dmagic': 3, 'drange': 3, 'str': 6, 'prayer': 3, 'slot': 'amulet'}, members=True)

SPELLS.update({
    "wind blast":  {"type":"combat","max":13,"lvl":41,"xp":25.5,"runes":{"air rune":3,"death rune":1}},
    "water blast": {"type":"combat","max":14,"lvl":47,"xp":28.5,"runes":{"water rune":3,"air rune":3,"death rune":1}},
    "earth blast": {"type":"combat","max":15,"lvl":53,"xp":31.5,"runes":{"earth rune":4,"air rune":3,"death rune":1}},
    "fire blast":  {"type":"combat","max":16,"lvl":59,"xp":34.5,"runes":{"fire rune":5,"air rune":4,"death rune":1}},
})

MONSTERS["king black dragon"]["drops"].append(("dragon platelegs", 1, 1, 0.03))
MONSTERS["obor"]["drops"].append(("dragon mace", 1, 1, 0.06))
# (the abyssal whip is earned from abyssal demons in the Slayer Tower)



# ===========================================================================
#  MONSTER SPRITES  (art shown at the start of a fight)
# ===========================================================================
MONSTER_ART.update({
    'man': '\n       o\n      /|\\    a man\n      / \\\n',
    'chicken farmer': '\n      _o_\n      /|\\    a chicken farmer\n      / \\\n',
    'imp': "\n     ,vv,\n     (oo)   an imp\n     /''\\\n",
    'dwarf': '\n      ___\n     (o o)   a dwarf\n     )WWW(\n',
    'minotaur': '\n     \\(oo)/   a minotaur\n      /||\\\n     _/  \\_\n',
    'thug': '\n      [--]\n     ([oo])   a thug\n      /||\\\n',
    'dark warrior': '\n      .--.\n     |x  x|   a dark warrior\n     /|##|\\\n',
    'giant spider': '\n    /\\(oo)/\\   a giant spider\n    \\/_/\\_\\/\n',
    'deadly red spider': '\n    /\\(xx)/\\   a deadly red spider\n    \\/>><<\\/\n',
    'flesh crawler': '\n    (((o)))   a flesh crawler\n     >====<\n     ^^^^^^\n',
    'zombie rat': '\n     (\\_/)\n    =(x.x)=   a zombie rat\n     (")(")\n',
    'moss giant': '\n     #####\n    ( o  o )   a moss giant\n    /|####|\\\n',
    'ice giant': '\n     *****\n    ( o  o )   an ice giant\n    /|::::|\\\n',
    'lesser demon': '\n     \\(oo)/   a lesser demon\n      )##(\n      /VV\\\n',
    'greater demon': '\n    \\\\(@@)//   a GREATER demon\n      )###(\n     /|VVV|\\\n',
    'chaos druid': '\n      ,-.\n     (o o)   a chaos druid\n     )~~~(\n',
    'jogre': '\n      ____\n    ( o  o )   a jogre\n    |  ==  |\n    /|    |\\\n',
    'paladin': '\n      .+.\n     [o o]   a paladin\n     /|+|\\\n',
    'white wolf': '\n     /\\_/\\\n    ( o o )   a white wolf\n     >\\^/<\n',
})


# ===========================================================================
#  FLETCHING  (members skill: carve logs into bows, string them with flax)
# ===========================================================================
add_item("knife", 6, tool="knife")
add_item("flax", 4)
add_item("bow string", 12)
add_item("maple logs", 64, log_fm_xp=135)
add_item("longbow", 80, equip={"slot": "weapon", "arange": 8, "req": {"ranged": 1}})
add_item("oak longbow", 160, equip={"slot": "weapon", "arange": 14, "req": {"ranged": 5}})
add_item("willow longbow", 320, members=True,
         equip={"slot": "weapon", "arange": 20, "req": {"ranged": 20}})
add_item("maple longbow", 640, members=True,
         equip={"slot": "weapon", "arange": 29, "req": {"ranged": 30}})
for _u in ["shortbow (u)", "longbow (u)", "oak shortbow (u)", "oak longbow (u)",
           "willow shortbow (u)", "willow longbow (u)", "maple shortbow (u)",
           "maple longbow (u)"]:
    add_item(_u, 8)

FLETCH_CUT = {
    "logs": [("shortbow (u)", 5, 5), ("longbow (u)", 10, 10)],
    "oak logs": [("oak shortbow (u)", 20, 16), ("oak longbow (u)", 25, 25)],
    "willow logs": [("willow shortbow (u)", 35, 33), ("willow longbow (u)", 40, 42)],
    "maple logs": [("maple shortbow (u)", 50, 50), ("maple longbow (u)", 55, 58)],
}
FLETCH_STRING = {
    "shortbow (u)": ("shortbow", 5, 5), "longbow (u)": ("longbow", 10, 10),
    "oak shortbow (u)": ("oak shortbow", 20, 16), "oak longbow (u)": ("oak longbow", 25, 25),
    "willow shortbow (u)": ("willow shortbow", 35, 33),
    "willow longbow (u)": ("willow longbow", 40, 42),
    "maple shortbow (u)": ("maple shortbow", 50, 50),
    "maple longbow (u)": ("maple longbow", 55, 58),
}


def cmd_fletch(p, arg):
    if not getattr(p, "members", False):
        say("Fletching is members-only. Type 'membership' to unlock it.", "bmagenta")
        return
    name = arg.strip().lower()
    cut = {u: (log, lvl, xp) for log, opts in FLETCH_CUT.items()
           for u, lvl, xp in opts}
    if not name:
        opts = []
        if p.has("knife"):
            for u, (log, lvl, xp) in cut.items():
                if p.has(log) and p.lvl("fletching") >= lvl:
                    opts.append(u)
        for u, (bow, lvl, xp) in FLETCH_STRING.items():
            if p.has(u) and p.has("bow string") and p.lvl("fletching") >= lvl:
                opts.append(bow)
        say("Fletch what? You can make: " + (", ".join(opts) if opts else
            "(need a knife + logs, or an unstrung bow + a bow string)"), "bcyan")
        return
    for u, (bow, lvl, xp) in FLETCH_STRING.items():
        if name == bow:
            if not p.has(u):
                say(f"You need a {u} first - fletch one from logs.", "byellow")
                return
            if not p.has("bow string"):
                say("You need a bow string (spin flax on a spinning wheel).", "byellow")
                return
            if p.lvl("fletching") < lvl:
                say(f"You need Fletching level {lvl} to make a {bow}.", "byellow")
                return
            p.take(u); p.take("bow string"); p.add(bow)
            say(f"You string the {u} into a {bow}.", "bcyan")
            p.gain_xp("fletching", xp)
            return
    if name in cut:
        log, lvl, xp = cut[name]
        if not p.has("knife"):
            say("You need a knife to fletch.", "byellow")
            return
        if not p.has(log):
            say(f"You need {log} to fletch a {name}.", "byellow")
            return
        if p.lvl("fletching") < lvl:
            say(f"You need Fletching level {lvl} to fletch a {name}.", "byellow")
            return
        p.take(log); p.add(name)
        say(f"You carve the {log} into a {name}.", "bcyan")
        p.gain_xp("fletching", xp)
        return
    say("You can't fletch that. Type 'fletch' to see options.", "grey")


HANDLERS["fletch"] = cmd_fletch
HANDLERS["string"] = cmd_fletch

# Sources in Kandarin + supply shops
TREES["maple"] = ("maple logs", 45, 100)
ROOMS["seers_village"]["trees"] = ["maple"]
ROOMS["seers_village"]["spinning_wheel"] = True
ROOMS["catherby"]["trees"] = ["tree", "oak", "willow"]
SHOPS["general"]["knife"] = 6
SHOPS["crafting"]["knife"] = 6
SHOPS["crafting"]["flax"] = 4
SHOPS["crafting"]["bow string"] = 12


# ===========================================================================
#  CRANDOR & ELVARG  (dragons — a Dragon-Slayer-flavoured expansion)
# ===========================================================================
# New loot loop: green dragons & Elvarg drop dragon bones (bury -> big prayer
# xp) and green dragonhide (tan -> craft the green d'hide armour that already
# exists in the gear tables).

add_item("dragon bones", 90, bury=("prayer", 72))
add_item("green dragonhide", 1500)
add_item("green dragon leather", 1700)

TAN_HIDES["green dragonhide"] = ("green dragon leather", 20)
CRAFT_RECIPES.update({
    "green d'hide vambraces": ("green dragon leather", 1, 57, 62),
    "green d'hide chaps": ("green dragon leather", 2, 60, 124),
    "green d'hide body": ("green dragon leather", 3, 63, 186),
})

# --- Elvarg the dragon: art + a dragonfire moveset -------------------------
_ELVARG_BRAILLE = '''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⣲⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠖⠋⢀⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠜⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠊⠀⠀⡠⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠊⡰⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⠀⠀⡜⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠚⠁⡜⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⠀⠀⠀⠀⢀⣀⣀⠤⠖⠈⠀⠀⢀⡜⠀⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠓⠲⢤⣸⠒⣊⣭⠛⠉⠀⠀⠀⠀⠀⢀⣠⢿⡶⠛⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⣹⠎⠀⠀⠑⡄⠀⢀⡠⠔⢊⡥⢺⠋
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠎⠀⠀⠀⣠⠞⠁⠀⠀⠀⢀⣾⠋⠁⣠⠞⠁⠀⢸⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠃⠀⡠⠊⡜⠁⠀⠀⠀⢀⡊⠁⠁⠀⢊⡀⠀⠀⠀⣀⣉⣓⣦⡤⠤
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡤⠊⠁⠸⠀⠀⠀⡠⡖⡝⠀⠀⠀⠀⠀⠈⢉⡩⠭⠒⢋⡟⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠁⠀⠀⠀⠑⠒⠛⠒⠋⠁⠀⠀⠀⠀⠀⠀⠘⠤⣀⡀⠈⣇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠜⠁⠀⠀⠀⠀⠀⠀⢀⣀⠤⠄⠀⠀⠀⡰⠚⢧⠉⠒⠒⠮⠽⣾⣦⣀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠋⠁⡠⣖⠂⠀⠀⠀⡠⠋⠉⠀⡀⠀⠀⢀⡴⠁⠀⠸⡄⠀⠀⠀⠀⡇⠙⢌⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠘⠐⠁⣀⡠⠔⠋⣀⣀⡴⠚⠓⡶⣞⣉⣀⣀⡠⢤⠇⠀⠀⠀⢰⣃⡀⠈⢳⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣀⣠⡊⠁⡀⣠⠞⠁⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⣿⠀⠈⠑⢄⢳
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣽⢻⡏⠁⠀⠀⠀⢀⠞⠑⠦⠤⠤⠤⠄⡸⠁⠀⠀⠀⢸⠉⣆⠀⠀⠘⡾
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠀⠃⠀⠀⠀⢀⢏⠀⠀⠀⠀⠀⠀⡰⠁⠀⠀⠀⠀⢸⠀⠘⡄⠀⠀⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠑⠦⠤⠤⠄⢲⠁⠀⠀⠀⠀⠀⠘⣆⣀⣹
'''
# blank braille (U+2800) -> real space so the negative space is empty, not a
# filled block; the dot glyphs remain to draw the dragon.
ELVARG_CALM = _ELVARG_BRAILLE.replace("⠀", " ")
ELVARG_FIRE = ELVARG_CALM
ELVARG_DIE = ELVARG_CALM


def _elvarg_intro(name):
    return [_tint(ELVARG_CALM, "green"), _tint(ELVARG_CALM, "bgreen", "bold"),
            _tint(ELVARG_FIRE, "orange", "bold"), _tint(ELVARG_FIRE, "byellow", "bold"),
            _tint(ELVARG_CALM, "bgreen", "bold")]


def _elvarg_death(name):
    return [_tint(ELVARG_CALM, "bred"), _tint(ELVARG_CALM, "grey"),
            _tint(ELVARG_DIE, "grey", "dim")]


def _elvarg_fire(_=None):
    return [_tint(ELVARG_FIRE, "orange", "bold"), _tint(ELVARG_FIRE, "byellow", "bold"),
            _tint(ELVARG_FIRE, "bred", "bold")]


def _elvarg_bite(_=None):
    return [_tint(ELVARG_CALM, "bgreen", "bold"), _tint(ELVARG_FIRE, "bred", "bold")]


ELVARG_ATTACKS = [
    {"label": "a searing blast of dragonfire", "verb": "breathes",
     "color": ("orange", "bold"), "builder": _elvarg_fire, "mult": 1.5, "w": 3,
     "atype": "magic", "dragonfire": True},
    {"label": "her great fangs", "verb": "snaps with", "color": ("bgreen", "bold"),
     "builder": _elvarg_bite, "mult": 1.0, "w": 3, "atype": "stab"},
    {"label": "a lashing tail swipe", "verb": "strikes with",
     "color": ("green", "bold"), "builder": _elvarg_bite, "mult": 1.1, "w": 2,
     "atype": "crush"},
]

BOSS_INTRO["elvarg"] = _elvarg_intro
BOSS_DEATH["elvarg"] = _elvarg_death
BOSS_TURN["elvarg"] = lambda p, m: _boss_take_turn(p, m, ELVARG_ATTACKS)
MONSTER_ART["elvarg"] = ELVARG_CALM

# --- Dragons (green dragon is farmable; Elvarg is the boss) ----------------
_add_mob("green dragon",
    {"abonus": 0, "atktype": ["slash", "dragonfire"], "att": 68, "cb": 79,
     "dstab": 20, "dslash": 20, "dcrush": 20, "dmagic": -20, "drange": 10,
     "def": 68, "hp": 75, "maxhit": 8, "str": 68, "weak": "ranged"},
    [("dragon bones", 1, 1, 1.0), ("green dragonhide", 1, 1, 1.0),
     ("coins", 30, 120, 0.8)], rank="hard")

_add_mob("elvarg",
    {"abonus": 0, "atktype": ["slash", "dragonfire"], "att": 120, "cb": 83,
     "dstab": 50, "dslash": 50, "dcrush": 50, "dmagic": -15, "drange": 30,
     "def": 100, "hp": 140, "maxhit": 10, "str": 120, "weak": "stab"},
    [("dragon bones", 1, 1, 1.0), ("green dragonhide", 2, 3, 1.0),
     ("coins", 1000, 3000, 1.0), ("dragon med helm", 1, 1, 0.04)])
MONSTERS["elvarg"]["boss"] = True
MONSTERS["elvarg"]["rank"] = "boss"
_BOSSES.add("elvarg")

# --- Crandor: a volcanic dragon isle reached by sailing from Karamja -------
ROOMS.update({
    "crandor": dict(name="Crandor",
        desc="A volcanic island long shunned by sailors. Black sand, the bones "
             "of failed adventurers, and green dragons basking in the heat. A "
             "dragon's roar rolls down from the caldera.",
        exits={"sail": "karamja_port", "caldera": "elvarg_lair"},
        monsters=["skeleton", "green dragon"]),
    "elvarg_lair": dict(name="Elvarg's Lair",
        desc="The molten heart of Crandor. Elvarg, the dread green dragon, "
             "coils atop a hoard of charred bones and gold.",
        exits={"out": "crandor"},
        monsters=["elvarg"]),
})
ROOMS["karamja_port"]["exits"]["sail"] = "crandor"

TRAVEL_HUBS["crandor"] = "crandor"
TRAVEL_NAMES.append("Crandor")


# ===========================================================================
#  DRAGON SLAYER  (the capstone quest)
# ===========================================================================
# Earn 12 quest points, talk to the Guildmaster at the Champions' Guild, then
# Oziach west of Edgeville. Gather the three map pieces, buy and repair the
# Lady Lumbridge at Port Sarim, and slay Elvarg. Rewards: 18,650 strength and
# defence xp and the right to wear the rune platebody / green d'hide body.

QUEST_POINTS = {
    "cooks_assistant": 1, "sheep_shearer": 1, "dorics_quest": 1,
    "romeo_juliet": 5, "vampyre_slayer": 3, "restless_ghost": 1,
    "rune_mysteries": 1, "imp_catcher": 1, "witch_potion": 1,
    "ernest_chicken": 4, "dragon_slayer": 2,
}
GUILD_QP = 12      # quest points needed to enter the Champions' Guild


def quest_points(p):
    return sum(QUEST_POINTS.get(k, 1) for k in ALL_QUESTS
               if _q(p, k) == "complete")


ALL_QUESTS["dragon_slayer"] = "Dragon Slayer"

MAP_PIECES = ["melzar's map piece", "wormbrain's map piece", "lozar's map piece"]
for _piece in MAP_PIECES:
    add_item(_piece, 1)
add_item("anti-dragon shield", 40, equip={
    "amagic": -8, "arange": -2, "dstab": 7, "dslash": 9, "dcrush": 8,
    "dmagic": 1, "drange": 9, "slot": "shield"})

# the classic rewards are locked behind the quest
ITEMS["rune platebody"]["equip"]["quest"] = "dragon_slayer"
ITEMS["green d'hide body"]["equip"]["quest"] = "dragon_slayer"

SHOPS["oziach"] = {"anti-dragon shield": 40, "rune platebody": 65000,
                   "green d'hide body": 7800}

ROOMS.update({
    "champions_guild": dict(name="Champions' Guild",
        desc="A proud hall south-west of Varrock where only proven "
             "adventurers may enter. The Guildmaster sizes you up from his "
             "chair by the fire.",
        exits={"east": "varrock_gate"}, npc="dragon_slayer"),
    "oziach_hut": dict(name="Oziach's Hut",
        desc="A shabby hut by the river west of Edgeville. Oziach, a "
             "wild-eyed armourer, mutters about dragons as he works.",
        exits={"east": "edgeville"}, npc="oziach", shop="oziach"),
    "melzars_maze": dict(name="Melzar's Maze",
        desc="A decaying stronghold north of Rimmington, sealed since Crandor "
             "fell. The shambling dead wander halls that still reek of ash.",
        exits={"out": "rimmington"},
        monsters=["zombie", "skeleton", "giant rat"]),
})
ROOMS["varrock_gate"]["exits"]["guild"] = "champions_guild"
ROOMS["edgeville"]["exits"]["hut"] = "oziach_hut"
ROOMS["rimmington"]["exits"]["maze"] = "melzars_maze"
ROOMS["port_sarim"]["exits"]["crandor"] = "crandor"
ROOMS["port_sarim"]["npc"] = "klarense"

REGIONS.update({"champions_guild": "Varrock", "oziach_hut": "Edgeville",
                "melzars_maze": "Rimmington"})

# Crandor is unreachable until the Lady Lumbridge is seaworthy
ROOMS["crandor"]["qlock"] = (
    "dragon_slayer", ("sail", "complete"),
    "The reefs around Crandor have sunk every ship that dared approach. You "
    "need a seaworthy ship and a route through the reef. (Quest: Dragon Slayer)")


def talk_guildmaster(p):
    stage = _q(p, "dragon_slayer")
    if stage == "not_started":
        qp = quest_points(p)
        if qp < GUILD_QP:
            say("Guildmaster: \"Champions only! Prove yourself on Gielinor's "
                f"quests and return with {GUILD_QP} quest points. You have "
                f"{qp}.\"", "byellow")
            say("  (Check your progress with 'quests'.)", "grey")
            return
        banner("Quest Start: Dragon Slayer", color="purple", line_color="bmagenta")
        say("Guildmaster: \"So you seek the right to wear rune armour? Then "
            "hear this: ELVARG, the dragon of Crandor, burned that isle to "
            "cinders and has never been slain. Speak to OZIACH, the armourer "
            "in a hut west of Edgeville — only he can grant you the honour.\"")
        p.quests["dragon_slayer"] = "started"
    elif stage == "complete":
        say("Guildmaster: \"The slayer of Elvarg! Drinks are on the guild, "
            "champion.\"")
    else:
        say("Guildmaster: \"Oziach's hut is west of Edgeville ('hut'). Elvarg "
            "awaits.\"")


def talk_oziach(p):
    stage = _q(p, "dragon_slayer")
    if stage == "started":
        banner("Dragon Slayer", color="purple", line_color="bmagenta")
        say("Oziach: \"Rune armour, is it? Slay ELVARG of Crandor and you've "
            "earned it. But no ship's route to Crandor survives whole — the "
            "map was torn in three:\"")
        say("  • MELZAR'S piece — search Melzar's Maze, north of Rimmington", "bcyan")
        say("  • WORMBRAIN'S piece — a goblin of Lumbridge Forest swallowed it", "bcyan")
        say("  • LOZAR'S piece — locked in a magic chest in Draynor Manor", "bcyan")
        say("Oziach: \"Take this as well — no shield, no dragon-slaying.\"")
        p.add("anti-dragon shield")
        say("(He hands you an ANTI-DRAGON SHIELD — equip it before facing "
            "dragonfire!)", "bgreen")
        say("\"With all three pieces, buy a ship from KLARENSE at Port Sarim.\"")
        p.quests["dragon_slayer"] = "maps"
    elif stage == "maps":
        missing = [i for i in MAP_PIECES if not p.has(i)]
        if missing:
            _need_msg("Oziach", missing)
        else:
            say("Oziach: \"The whole map! Now buy that ship off KLARENSE at "
                "Port Sarim and sail.\"")
    elif stage == "sail":
        say("Oziach: \"The Lady Lumbridge is ready — sail from Port Sarim "
            "('go crandor') and end Elvarg!\"")
    elif stage == "complete":
        say("Oziach: \"Dragon Slayer! My rune platebodies are yours to buy — "
            "and at last to wear. ('shop')\"")
    else:
        say("Oziach: \"I only deal with champions. See the Guildmaster at the "
            "Champions' Guild, south-west of Varrock.\"")


def talk_klarense(p):
    stage = _q(p, "dragon_slayer")
    if stage in ("sail", "complete"):
        say("Klarense: \"She's your ship now. Fair winds to Crandor! "
            "('go crandor')\"")
        return
    if stage != "maps":
        say("Klarense: \"Fine ship, the Lady Lumbridge. Not for sale, mind... "
            "unless a dragon-slaying came into it.\"")
        return
    missing = [i for i in MAP_PIECES if not p.has(i)]
    if missing:
        _need_msg("Klarense", missing)
        return
    needs = []
    if not p.has("coins", 2000):
        needs.append("2,000 coins")
    if not p.has("steel bar", 2):
        needs.append("2 steel bars (to patch the hull)")
    if not p.has("hammer"):
        needs.append("a hammer")
    if needs:
        say("Klarense: \"The Lady Lumbridge is yours for 2,000 coins — but "
            "her hull needs work. Bring " + ", ".join(needs) + ".\"", "byellow")
        return
    p.take("coins", 2000)
    p.take("steel bar", 2)
    for i in MAP_PIECES:
        p.take(i)
    banner("The Lady Lumbridge is seaworthy!", color="bcyan", line_color="bcyan")
    say("You hammer steel plate over her hull and chart the reef from the "
        "three map pieces. Klarense signs her over. Crandor lies dead ahead — "
        "'go crandor'. Bring your anti-dragon shield!", "bgreen")
    p.quests["dragon_slayer"] = "sail"


QUEST_TALK["dragon_slayer"] = talk_guildmaster
QUEST_TALK["oziach"] = talk_oziach
QUEST_TALK["klarense"] = talk_klarense


# ===========================================================================
#  THE KNIGHT'S SWORD  &  PRINCE ALI RESCUE
# ===========================================================================
# Two more classics. The Knight's Sword: help a Falador squire replace Sir
# Vyvin's lost blade — find Thurgo the Imcando dwarf (he loves redberry pie),
# mine blurite, and reforge it for a huge slug of smithing xp. Prince Ali
# Rescue: spring the prince from Draynor jail with a disguise; the grateful
# emirate makes the Al Kharid toll gate free forever.

add_item("redberry pie", 12, heal=5)
SHOPS["general"]["redberry pie"] = 12
add_item("blurite ore", 60)
ROCKS["blurite"] = ("blurite ore", 10, 18)
add_item("knight's sword", 100, equip={
    "astab": 6, "aslash": 9, "acrush": -2, "str": 8, "slot": "weapon",
    "req": {"attack": 5}})
add_item("blonde wig", 2)
add_item("bronze key", 1)

ROOMS.update({
    "white_knights_castle": dict(name="White Knights' Castle",
        desc="The great white keep of Falador. Knights drill in the courtyard "
             "while a young squire paces, looking close to tears.",
        exits={"south": "falador_square"}, npc="knights_sword"),
    "mudskipper_point": dict(name="Mudskipper Point",
        desc="A windswept spit south of Port Sarim. Thurgo, last of the "
             "Imcando dwarves, tends a forge by his hut. An icy cave mouth "
             "yawns nearby ('cave').",
        exits={"north": "port_sarim", "cave": "icy_cavern"},
        npc="thurgo", anvil=True),
    "icy_cavern": dict(name="Icy Cavern",
        desc="A frozen cavern beneath Asgarnia. Rare blurite veins glitter "
             "blue in the walls, guarded by hulking ice giants.",
        exits={"out": "mudskipper_point"},
        rocks=["blurite"], monsters=["ice giant"]),
    "draynor_jail": dict(name="Draynor Jail",
        desc="A squat stone jail on the village edge. Lady Keli holds court "
             "over her toughs while a hooded prisoner waits in the cell.",
        exits={"out": "draynor_village"}),
})
ROOMS["falador_square"]["exits"]["castle"] = "white_knights_castle"
ROOMS["port_sarim"]["exits"]["point"] = "mudskipper_point"
ROOMS["draynor_village"]["exits"]["jail"] = "draynor_jail"
ROOMS["al_kharid_palace"]["npc"] = "prince_ali"
ROOMS["falador_square"]["desc"] += " The White Knights' Castle rises north ('castle')."
ROOMS["port_sarim"]["desc"] += " Mudskipper Point lies south ('point')."
ROOMS["draynor_village"]["desc"] += " A squat jail stands at the edge of town ('jail')."
ROOMS["al_kharid_palace"]["desc"] += " Osman, the Emir's chancellor, beckons you over."

REGIONS.update({"white_knights_castle": "Falador",
                "mudskipper_point": "PortSarim", "icy_cavern": "PortSarim",
                "draynor_jail": "Draynor"})

ALL_QUESTS.update({"knights_sword": "The Knight's Sword",
                   "prince_ali": "Prince Ali Rescue"})
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS.update({"knights_sword": 1, "prince_ali": 3})


def talk_squire(p):
    stage = _q(p, "knights_sword")
    if stage == "not_started":
        banner("Quest Start: The Knight's Sword", color="purple",
               line_color="bmagenta")
        say("Squire: \"I've lost Sir Vyvin's family sword — I'm ruined! Only "
            "an IMCANDO DWARF could reforge such a blade. THURGO, the last of "
            "them, lives at Mudskipper Point south of Port Sarim ('point'). "
            "One thing: Imcando dwarves are mad for REDBERRY PIE...\"")
        p.quests["knights_sword"] = "started"
    elif stage == "sword":
        has = p.has("knight's sword")
        if not has and p.equipment.get("weapon") == "knight's sword":
            p.equipment["weapon"] = None            # hand it over off your back
            has = True
        elif has:
            p.take("knight's sword")
        if has:
            _complete_banner("The Knight's Sword")
            say("The squire nearly faints with relief. \"Sir Vyvin will never "
                "know!\" Watching Thurgo work has taught you much: 12,725 "
                "smithing xp awarded!")
            p.gain_xp("smithing", 12725)
            p.quests["knights_sword"] = "complete"
        else:
            say("Squire: \"Where is the sword?! Thurgo was our only hope!\"")
    elif stage == "complete":
        say("Squire: \"Sir Vyvin suspects nothing. Thank you, friend.\"")
    else:
        say("Squire: \"Thurgo's at Mudskipper Point, south of Port Sarim. "
            "Take him a redberry pie!\"")


def talk_thurgo(p):
    stage = _q(p, "knights_sword")
    if stage == "started":
        if p.has("redberry pie"):
            p.take("redberry pie")
            say("Thurgo devours the pie in two bites. \"Ahh! Fine, I'll forge "
                "your sword. Bring me 2 IRON BARS and 1 BLURITE ORE — there's "
                "a vein in the icy cavern ('cave'), if you can mine it (level "
                "10) and slip past the ice giants.\"", "bcyan")
            p.quests["knights_sword"] = "forge"
        else:
            say("Thurgo: \"Can't help you. ...Unless you happened to have a "
                "REDBERRY PIE? The general store in Lumbridge bakes them.\"")
    elif stage == "forge":
        needs = []
        if not p.has("iron bar", 2):
            needs.append("2 iron bars")
        if not p.has("blurite ore"):
            needs.append("1 blurite ore")
        if needs:
            _need_msg("Thurgo", needs)
        else:
            p.take("iron bar", 2)
            p.take("blurite ore")
            p.add("knight's sword")
            banner("Thurgo forges the blade!", color="bcyan", line_color="bcyan")
            say("Sparks fly from the Imcando forge. Thurgo hands you a perfect "
                "KNIGHT'S SWORD — take it to the squire in Falador!", "bgreen")
            p.quests["knights_sword"] = "sword"
    elif stage == "sword":
        say("Thurgo: \"Get that sword to your squire before I eat it too.\"")
    elif stage == "complete":
        say("Thurgo: \"Come by any time... especially with pie.\"")
    else:
        say("Thurgo: \"Mmm. I do love a good redberry pie.\"")


def talk_osman(p):
    stage = _q(p, "prince_ali")
    if stage == "not_started":
        banner("Quest Start: Prince Ali Rescue", color="purple",
               line_color="bmagenta")
        say("Osman: \"Prince Ali is held in DRAYNOR's jail by the bandit Lady "
            "Keli! We must smuggle him out in disguise. Bring me 3 BALLS OF "
            "WOOL for a wig, 2 CLAY for a key mould, and a BRONZE BAR to "
            "forge the key.\"")
        p.quests["prince_ali"] = "started"
    elif stage == "started":
        needs = []
        if not p.has("ball of wool", 3):
            needs.append("3 balls of wool")
        if not p.has("clay", 2):
            needs.append("2 clay")
        if not p.has("bronze bar"):
            needs.append("a bronze bar")
        if needs:
            _need_msg("Osman", needs)
        else:
            p.take("ball of wool", 3)
            p.take("clay", 2)
            p.take("bronze bar")
            p.add("blonde wig")
            p.add("bronze key")
            say("Osman works quickly: a BLONDE WIG and a forged BRONZE KEY. "
                "\"Go to the jail in Draynor ('jail') and 'search' for a way "
                "to free the prince!\"", "bgreen")
            p.quests["prince_ali"] = "rescue"
    elif stage == "rescue":
        say("Osman: \"The prince still rots in Draynor's jail — go, 'search' "
            "for his cell!\"")
    elif stage == "freed":
        _complete_banner("Prince Ali Rescue")
        say("Prince Ali embraces his family. Osman presses 700 coins into "
            "your hand — and the Al Kharid gate is forever free to you.")
        p.add("coins", 700)
        p.quests["prince_ali"] = "complete"
    else:
        say("Osman: \"Al Kharid remembers its friends. The gate is always "
            "open to you.\"")


QUEST_TALK["knights_sword"] = talk_squire
QUEST_TALK["thurgo"] = talk_thurgo
QUEST_TALK["prince_ali"] = talk_osman

# journal objective hints (quest -> stage -> what to do next)
QUEST_HINTS = {
    "cooks_assistant": {"started":
        "bring the Cook an egg, a bucket of milk and a pot of flour"},
    "sheep_shearer": {"started":
        "bring Fred 6 balls of wool ('shear' sheep, then 'spin' at Lumbridge)"},
    "dorics_quest": {"started":
        "bring Doric 6 clay, 4 copper ore and 2 iron ore"},
    "romeo_juliet": {"started":
        "'search' Draynor Village for Juliet, take her message to Romeo"},
    "vampyre_slayer": {"started":
        "slay Count Draynor in Draynor Manor (keep Morgan's stake!)"},
    "restless_ghost": {"started":
        "'search' the Varrock sewers for the skull, return to Father Aereck"},
    "rune_mysteries": {"started":
        "study the air talisman, then return it to Sedridor"},
    "imp_catcher": {"started":
        "slay imps at the Wizard's Tower for red, yellow, black & white beads"},
    "witch_potion": {"started":
        "bring Aggie raw rat meat, a bucket of milk and an egg"},
    "ernest_chicken": {"started":
        "'search' Draynor Manor for the oil can, pressure gauge & rubber tube"},
    "knights_sword": {
        "started": "find Thurgo at Mudskipper Point ('point' from Port Sarim) "
                   "— bring a redberry pie (Lumbridge general store)",
        "forge": "bring Thurgo 2 iron bars + 1 blurite ore (mine it in the "
                 "icy cavern)",
        "sword": "return the knight's sword to the squire in Falador"},
    "prince_ali": {
        "started": "bring Osman 3 balls of wool, 2 clay and a bronze bar",
        "rescue": "'search' the Draynor jail ('jail' from Draynor Village)",
        "freed": "return to Osman at the Al Kharid palace"},
    "dragon_slayer": {
        "started": "speak to Oziach in his hut west of Edgeville ('hut')",
        "maps": "search Melzar's Maze, slay goblins in Lumbridge Forest, and "
                "search Draynor Manor for the three map pieces",
        "sail": "see Klarense at Port Sarim, then 'go crandor' — bring your "
                "anti-dragon shield!"},
}


# ===========================================================================
#  BLACK KNIGHTS' FORTRESS
# ===========================================================================
# The other 12-QP quest. Sir Amik Varze of the White Knights sends you to
# infiltrate the Black Knights' fortress on Ice Mountain disguised in a
# bronze med helm + iron chainbody (Wayne's Chainmail Shop, East Falador),
# and ruin their invincibility potion with a well-placed cabbage.

# chainbodies + med helms (real OSRS-ish per-type defences, bronze -> rune)
for _mname, _req, _t in METALS:
    _v = TIER_VALUE[_t]
    add_item(f"{_mname} chainbody", 75 * _v, equip={
        "dstab": 7 + _t * 5, "dslash": 11 + _t * 7, "dcrush": 13 + _t * 8,
        "dmagic": 0, "drange": 7 + _t * 5, "slot": "body",
        "req": {"defence": _req}})
    add_item(f"{_mname} med helm", 18 * _v, equip={
        "dstab": 3 + _t * 2, "dslash": 4 + _t * 2, "dcrush": 3 + _t * 2,
        "dmagic": -1, "drange": 3 + _t * 2, "slot": "head",
        "req": {"defence": _req}})

SHOPS["chainmail"] = {"bronze chainbody": 60, "iron chainbody": 210,
                      "steel chainbody": 750, "bronze med helm": 24,
                      "iron med helm": 84, "steel med helm": 300}
ROOMS["falador_east"]["shop"] = "chainmail"
ROOMS["falador_east"]["desc"] += " Wayne's Chainmail Shop stands by the gate."

add_item("cabbage", 1, heal=2)
SHOPS["general"]["cabbage"] = 1

_add_mob("black knight",
    {"abonus": 10, "atktype": ["slash"], "att": 25, "cb": 33, "dstab": 15,
     "dslash": 17, "dcrush": 10, "dmagic": 5, "drange": 15, "def": 25,
     "hp": 42, "maxhit": 5, "str": 25, "weak": "crush"},
    [("bones", 1, 1, 1.0), ("coins", 5, 60, 0.8),
     ("black dagger", 1, 1, 0.04), ("black kiteshield", 1, 1, 0.02)],
    rank="medium")

ROOMS.update({
    "black_knights_fortress": dict(name="Black Knights' Fortress",
        desc="A grim fortress atop Ice Mountain. Black Knights drill in the "
             "yard, and somewhere below, a cauldron bubbles.",
        exits={"out": "monastery"},
        monsters=["black knight"],
        gear_lock=(["bronze med helm", "iron chainbody"],
                   "The gate guard bars your way: \"No entry to outsiders!\" "
                   "You'll need to look like one of them to get inside.")),
})
ROOMS["monastery"]["exits"]["fortress"] = "black_knights_fortress"
ROOMS["monastery"]["desc"] += (" To the north, the Black Knights' Fortress "
                               "glowers atop Ice Mountain ('fortress').")
REGIONS["black_knights_fortress"] = "Edgeville"

ALL_QUESTS["black_knights"] = "Black Knights' Fortress"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["black_knights"] = 3


def talk_amik(p):
    stage = _q(p, "black_knights")
    if stage == "not_started":
        qp = quest_points(p)
        if qp < GUILD_QP:
            say("Sir Amik Varze: \"This mission needs a proven adventurer — "
                f"return when you hold {GUILD_QP} quest points. You have "
                f"{qp}.\"", "byellow")
            return
        banner("Quest Start: Black Knights' Fortress", color="purple",
               line_color="bmagenta")
        say("Sir Amik Varze: \"The Black Knights are brewing an INVINCIBILITY "
            "POTION in their fortress on Ice Mountain, near the Edgeville "
            "monastery. Infiltrate it disguised as one of them — a BRONZE MED "
            "HELM and an IRON CHAINBODY should fool the guards (Wayne sells "
            "chainmail in East Falador). Then 'search' for their cauldron and "
            "ruin the brew. They say a CABBAGE would do horrid things to it.\"")
        p.quests["black_knights"] = "infiltrate"
    elif stage == "infiltrate":
        say("Sir Amik Varze: \"The potion still brews! Wear the bronze med "
            "helm and iron chainbody, slip into the fortress ('fortress' from "
            "the monastery), and 'search' — with a cabbage to hand.\"")
    elif stage == "sabotaged":
        _complete_banner("Black Knights' Fortress")
        say("Sir Amik Varze: \"The potion, ruined by a vegetable! Magnificent "
            "work.\" He counts out 2,500 coins.")
        p.add("coins", 2500)
        p.quests["black_knights"] = "complete"
    else:
        say("Sir Amik Varze: \"Falador sleeps easier thanks to you.\"")


QUEST_TALK["black_knights"] = talk_amik
ROOMS["white_knights_castle"]["npc"] = ["knights_sword", "black_knights"]
ROOMS["white_knights_castle"]["desc"] += (" Sir Amik Varze, captain of the "
                                          "White Knights, studies a map.")

QUEST_HINTS["black_knights"] = {
    "infiltrate": "wear a bronze med helm + iron chainbody (Wayne's, East "
                  "Falador), take a cabbage, and 'search' the fortress "
                  "('fortress' from the monastery)",
    "sabotaged": "report back to Sir Amik Varze at the White Knights' Castle",
}

# where every quest begins ('quests' shows this for unstarted ones)
QUEST_STARTS = {
    "cooks_assistant": "the Cook, Lumbridge Castle",
    "sheep_shearer": "Farmer Fred, Lumbridge Farm",
    "dorics_quest": "Doric, Falador",
    "romeo_juliet": "Romeo, Varrock Square",
    "vampyre_slayer": "Morgan, Draynor Village",
    "restless_ghost": "Father Aereck, Lumbridge Church",
    "rune_mysteries": "Sedridor, Wizard's Tower",
    "imp_catcher": "Wizard Mizgog, Wizard's Tower",
    "witch_potion": "Aggie, Draynor Village",
    "ernest_chicken": "Professor Oddenstein, Draynor Manor",
    "knights_sword": "the squire, White Knights' Castle",
    "prince_ali": "Osman, Al Kharid Palace",
    "black_knights": "Sir Amik Varze, White Knights' Castle (12 qp)",
    "priest_in_peril": "King Roald, Varrock Palace",
    "dragon_slayer": "the Guildmaster, Champions' Guild (12 qp)",
}


# ===========================================================================
#  THE FIGHT CAVES  (wave minigame -> TzTok-Jad -> fire cape)
# ===========================================================================
# 'challenge' in the Fight Caves starts a run: seven waves of TzHaar-kin,
# 'next' between waves (heal up first!), leaving or dying abandons the run.
# Each TzHaar has its OSRS signature: Tz-Kih drains prayer, Tz-Kek's spikes
# recoil, Tok-Xil shoots, Yt-MejKot heals itself, Ket-Zek blasts magic. The
# final wave is TzTok-Jad, who telegraphs every attack — switch to the right
# protection prayer or be flattened. Reward: the fire cape (and tokkul).

add_item("tokkul", 1)     # the obsidian currency of the TzHaar

_add_mob("tz-kih",
    {"abonus": 0, "atktype": ["crush"], "att": 32, "cb": 22, "dstab": 0,
     "dslash": 0, "dcrush": 0, "dmagic": 0, "drange": 0, "def": 12,
     "hp": 10, "maxhit": 4, "str": 30, "weak": "crush"},
    [("tokkul", 3, 9, 1.0)], members=True, rank="easy")

_add_mob("tz-kek",
    {"abonus": 0, "atktype": ["crush"], "att": 40, "cb": 45, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 5, "drange": 5, "def": 28,
     "hp": 20, "maxhit": 7, "str": 40, "weak": "slash"},
    [("tokkul", 6, 15, 1.0)], members=True, rank="medium")
MONSTERS["tz-kek"]["recoil"] = 1        # spiked hide: melee hits bite back

_add_mob("tok-xil",
    {"abonus": 20, "atktype": ["ranged"], "att": 65, "cb": 90, "dstab": 20,
     "dslash": 20, "dcrush": 20, "dmagic": 10, "drange": 25, "def": 45,
     "hp": 40, "maxhit": 13, "str": 60, "weak": "stab"},
    [("tokkul", 15, 40, 1.0)], members=True, rank="hard")

_add_mob("yt-mejkot",
    {"abonus": 10, "atktype": ["slash"], "att": 90, "cb": 180, "dstab": 40,
     "dslash": 45, "dcrush": 40, "dmagic": 30, "drange": 40, "def": 65,
     "hp": 80, "maxhit": 20, "str": 95, "weak": "stab"},
    [("tokkul", 30, 90, 1.0)], members=True, rank="elite")

_add_mob("ket-zek",
    {"abonus": 40, "atktype": ["magic"], "att": 130, "cb": 360, "dstab": 45,
     "dslash": 60, "dcrush": 60, "dmagic": 70, "drange": 60, "def": 80,
     "hp": 160, "maxhit": 22, "str": 120, "weak": "stab"},
    [("tokkul", 90, 270, 1.0)], members=True, rank="elite")

MONSTER_ART["tz-kih"] = r'''
      /\  ~  /\
     ( o \_/ o )
      \|/ ' \|/
'''
MONSTER_ART["tz-kek"] = r'''
      /\/\/\/\/\
     <  o    o  >
     <    __    >
      \/\/\/\/\/
'''
MONSTER_ART["tok-xil"] = r'''
       |\   /|
      ( >o.o< )    }---->
       /|| ||\
'''
MONSTER_ART["yt-mejkot"] = r'''
       _/=====\_
      (  o _ o  )
      /|   W   |\
      \|_______|/
        |     |
'''
MONSTER_ART["ket-zek"] = r'''
      \ /       \ /
     --#---------#--
      ( ((o) (o)) )
       \   ___   /
       /|_______|\
      /_/       \_\
'''


def _kih_drain(p, m, dmg):
    if p.prayer_points > 0:
        drain = dmg + 2
        p.prayer_points = max(0, p.prayer_points - drain)
        print("  " + paint(f"The Tz-Kih latches on and drains {drain} prayer "
                           f"points!", "bmagenta"))


def _mejkot_heal(p, m, dmg):
    if m["cur"] < m["hp"]:
        heal = random.randint(3, 8)
        m["cur"] = min(m["hp"], m["cur"] + heal)
        print("  " + paint(f"The Yt-MejKot knits its obsidian flesh back "
                           f"together. (+{heal})", "lime"))


MONSTER_EFFECTS["tz-kih"] = _kih_drain
MONSTER_EFFECTS["yt-mejkot"] = _mejkot_heal

CAVE_WAVES = ["tz-kih", "tz-kek", "tok-xil", "yt-mejkot", "ket-zek",
              "ket-zek", "tztok-jad"]

add_item("fire cape", 50000, members=True, equip={
    "astab": 1, "aslash": 1, "acrush": 1, "amagic": 1, "arange": 1,
    "dstab": 11, "dslash": 11, "dcrush": 11, "dmagic": 11, "drange": 11,
    "str": 4, "prayer": 2, "slot": "cape"})

JAD_ART = r'''
        \ /             \ /
      ---#---------------#---
        /_\ ___________ /_\
       /   (  (o)  (o)  )   \
      |     \____ _____/     |
       \     /VVVVVVVVV\    /
        \___|           |__/
        /   \___________/   \
       /_/|  |    |    |  |\_\
          |__|    |____|__|
'''


def _jad_intro(name):
    return [_tint(JAD_ART, "brown"), _tint(JAD_ART, "orange", "bold"),
            _tint(JAD_ART, "bred", "bold"), _tint(JAD_ART, "orange", "bold")]


def _jad_death(name):
    return [_tint(JAD_ART, "orange"), _tint(JAD_ART, "grey"),
            _tint(JAD_ART, "grey", "dim")]


_add_mob("tztok-jad",
    {"abonus": 0, "atktype": ["crush", "magic", "ranged"], "att": 160,
     "cb": 702, "dstab": 0, "dslash": 0, "dcrush": 0, "dmagic": 0,
     "drange": 0, "def": 100, "hp": 250, "maxhit": 25, "str": 160,
     "weak": "ranged"},
    [("coins", 5000, 20000, 1.0), ("tokkul", 1000, 3000, 1.0)], members=True)
MONSTERS["tztok-jad"]["boss"] = True
MONSTERS["tztok-jad"]["rank"] = "boss"
_BOSSES.add("tztok-jad")
BOSS_INTRO["tztok-jad"] = _jad_intro
BOSS_DEATH["tztok-jad"] = _jad_death
MONSTER_ART["tztok-jad"] = JAD_ART

JAD_CUES = {
    "magic": "TzTok-Jad rears back, flame gathering between his horns — "
             "MAGIC is coming! (pray 'protect from magic')",
    "ranged": "TzTok-Jad slams his forelegs into the rock — a boulder "
              "barrage is coming! (pray 'protect from missiles')",
    "melee": "TzTok-Jad crouches low, jaws gaping wide — a MELEE bite is "
             "coming! (pray 'protect from melee')",
}


def _jad_take_turn(p, m):
    """Jad telegraphs each attack a turn ahead: pray right or be flattened."""
    style = m.get("jad_next")
    if style:
        animate([_tint(JAD_ART, "orange", "bold"), _tint(JAD_ART, "bred", "bold")],
                delay=0.12, center=True)
        say(f"{m['name'].title()} unleashes his {style} attack!",
            "orange", "bold")
        if p.prayer_protects(style):
            print("  " + paint("Your prayer holds — the attack breaks "
                               "harmlessly over you!", "bcyan"))
        else:
            dmg = random.randint(8, m["max_hit"])
            p.hp -= dmg
            print("  " + paint(f"It smashes into you for a devastating {dmg}!",
                               "bred") + "  " + paint("HP ", "white")
                  + bar_meter(max(p.hp, 0), p.max_hp, 18))
    else:
        say(f"{m['name'].title()} sizes you up, embers dripping from his "
            "jaws...", "orange")
    nxt = random.choice(["magic", "ranged", "melee"])
    m["jad_next"] = nxt
    print("  " + paint(JAD_CUES[nxt], "byellow"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


BOSS_TURN["tztok-jad"] = _jad_take_turn

ROOMS.update({
    "fight_caves": dict(name="The Fight Caves",
        desc="A scorched arena deep in the volcano. TzHaar-Mej-Jal guards "
             "the entrance, sizing up challengers. Seven waves await the "
             "brave — and TzTok-Jad awaits the foolish. (members)",
        exits={"out": "karamja_volcano"},
        npc="tzhaar", fight_caves=True, members=True),
})
ROOMS["karamja_volcano"]["exits"]["caves"] = "fight_caves"
ROOMS["karamja_volcano"]["desc"] += " A heat-shimmering tunnel leads to the Fight Caves ('caves')."
REGIONS["fight_caves"] = "Karamja"
NPC_NAMES["tzhaar"] = "TzHaar-Mej-Jal"


def talk_tzhaar(p):
    wave = getattr(p, "cave_wave", 0)
    if wave:
        say(f"TzHaar-Mej-Jal: \"You fight good so far, JalYt — wave {wave} of "
            f"{len(CAVE_WAVES)}. Type 'next' when ready. Leave, and you start "
            "over.\"", "orange")
        return
    if p.has("fire cape") or "tztok-jad" in getattr(p, "bosses", []):
        say("TzHaar-Mej-Jal: \"The JalYt who slew TzTok-Jad! You fight again "
            "any time — 'challenge'.\"", "orange")
        return
    say("TzHaar-Mej-Jal: \"You want good fight, JalYt? Seven waves of my "
        "kin, no mercy, no leaving. TZ-KIH drinks your prayers. TZ-KEK's "
        "spikes bite back. TOK-XIL shoots true. YT-MEJKOT mends its own "
        "flesh. KET-ZEK burns with sorcery — twice. Survive them all and "
        "face TZTOK-JAD: watch his moves and pray right, or die fast. Beat "
        "him and the FIRE CAPE is yours. Bring food, prayer potions, your "
        "best gear. Type 'challenge' to begin.\"", "orange")


QUEST_TALK["tzhaar"] = talk_tzhaar


def _cave_start_wave(p):
    mon = CAVE_WAVES[p.cave_wave - 1]
    say(f"— Wave {p.cave_wave} of {len(CAVE_WAVES)} —", "byellow", "bold")
    _start_combat(p, mon)


def cmd_challenge(p, _a):
    if ROOMS[p.location].get("inferno"):
        return _inferno_challenge(p)
    if p.location != "fight_caves":
        say("There's nothing to challenge here.", "grey")
        return
    if getattr(p, "cave_wave", 0):
        say(f"You're mid-run — wave {p.cave_wave}/{len(CAVE_WAVES)}. "
            "Type 'next' to continue.", "byellow")
        return
    banner("THE FIGHT CAVES", color="orange", line_color="red")
    say("TzHaar-Mej-Jal: \"Seven waves. No mercy. Fight good, JalYt!\"",
        "orange", "bold")
    p.cave_wave = 1
    _cave_start_wave(p)


def cmd_next(p, _a):
    if ROOMS[p.location].get("inferno") and getattr(p, "inferno_wave", 0):
        return _inferno_start_wave(p)
    if p.location != "fight_caves" or not getattr(p, "cave_wave", 0):
        say("Nothing to continue. (In the Fight Caves, 'challenge' starts "
            "a run.)", "grey")
        return
    _cave_start_wave(p)


HANDLERS["challenge"] = cmd_challenge
HANDLERS["next"] = cmd_next
HANDLERS["wave"] = cmd_next


# ===========================================================================
#  SKILLING EXPANSION  (gems & jewellery, runecrafting altars, yew/magic
#  trees + high fletching, skill capes)
# ===========================================================================

# --- Gem cutting (mining rocks can strike gems; cut them with a chisel) -----
# uncut gem -> (cut gem, crafting level, xp). Order matters: mining strike
# weights (8/5/2/1) follow this order, common -> rare.
GEM_CUT = {
    "uncut sapphire": ("sapphire", 20, 50),
    "uncut emerald": ("emerald", 27, 67),
    "uncut ruby": ("ruby", 34, 85),
    "uncut diamond": ("diamond", 43, 107),
}


def _gem_uncut(name):
    if name in GEM_CUT:
        return name
    if "uncut " + name in GEM_CUT:
        return "uncut " + name
    return None


def cmd_cutgem(p, arg):
    name = arg.strip().lower()
    uncut = _gem_uncut(name) if name else \
        next((g for g in GEM_CUT if p.has(g)), None)
    if not uncut:
        say("Cut what? You have no uncut gems. (Mining sometimes strikes "
            "them.)", "grey")
        return
    if not p.has(uncut):
        say(f"You have no {uncut}.")
        return
    if not p.find_tool("chisel"):
        say("You need a chisel (general or crafting shop).")
        return
    cut, lvl, xp = GEM_CUT[uncut]
    if p.lvl("crafting") < lvl:
        say(f"You need crafting level {lvl} to cut a {uncut}.")
        return
    p.take(uncut)
    p.add(cut)
    say(f"You carefully chisel the {uncut} into a sparkling {cut}.", "bcyan")
    p.gain_xp("crafting", xp)
    return True


# --- Jewellery (furnace + gold bar [+ gem] -> rings and amulets) ------------
# product -> (gem or None, crafting level, xp)
JEWELLERY = {
    "gold ring": (None, 5, 15),
    "sapphire ring": ("sapphire", 20, 40),
    "emerald ring": ("emerald", 27, 55),
    "ruby ring": ("ruby", 34, 70),
    "diamond ring": ("diamond", 43, 85),
    "gold amulet": (None, 8, 30),
    "sapphire amulet": ("sapphire", 24, 65),
    "emerald amulet": ("emerald", 31, 70),
    "ruby amulet": ("ruby", 50, 85),
    "diamond amulet": ("diamond", 70, 100),
}

add_item("gold ring", 315, equip={"slot": "ring"})
add_item("sapphire ring", 900, equip={"slot": "ring"})
add_item("emerald ring", 1275, equip={"slot": "ring"})
add_item("ruby ring", 2025, equip={"slot": "ring"})
add_item("diamond ring", 3525, equip={"slot": "ring"})
add_item("gold amulet", 350, equip={"slot": "amulet"})
add_item("sapphire amulet", 900, equip={
    "amagic": 2, "dmagic": 2, "slot": "amulet"})
add_item("emerald amulet", 1250, equip={
    "arange": 3, "drange": 2, "slot": "amulet"})
add_item("ruby amulet", 2000, equip={
    "astab": 4, "aslash": 4, "acrush": 4, "str": 2, "slot": "amulet"})
add_item("diamond amulet", 3500, equip={
    "astab": 6, "aslash": 6, "acrush": 6, "amagic": 3, "arange": 3,
    "str": 3, "slot": "amulet"})


def _craft_jewellery(p, name):
    gem, lvl, xp = JEWELLERY[name]
    if not ROOMS[p.location].get("furnace"):
        say("You need a furnace to work gold (Lumbridge, Falador, Al Kharid, "
            "Edgeville).")
        return
    if p.lvl("crafting") < lvl:
        say(f"You need crafting level {lvl} to make a {name}.")
        return
    if not p.has("gold bar"):
        say("You need a gold bar (smelt gold ore).")
        return
    if gem and not p.has(gem):
        say(f"You need a {gem} (cut an uncut {gem} with a chisel).")
        return
    p.take("gold bar")
    if gem:
        p.take(gem)
    p.add(name)
    say(f"You pour the gold into a mould and set it — a {name}!", "byellow")
    p.gain_xp("crafting", xp)
    return True


# --- Runecrafting altars across the realm -----------------------------------
# (the air altar has stood alone long enough; craftrune works at each)
ROOMS.update({
    "mind_altar": dict(name="Mind Altar",
        desc="A wind-scoured shrine on Ice Mountain's shoulder. Thoughts "
             "hum in the stones. ('craftrune' with rune essence)",
        exits={"out": "monastery"}, altar="mind"),
    "water_altar": dict(name="Water Altar",
        desc="A glassy pool deep in the swamp mist. The air tastes of rain. "
             "('craftrune' with rune essence)",
        exits={"out": "swamp"}, altar="water"),
    "earth_altar": dict(name="Earth Altar",
        desc="A ring of standing stones north-east of Varrock, thick with "
             "the smell of loam. ('craftrune' with rune essence)",
        exits={"out": "varrock_east_bank"}, altar="earth"),
    "fire_altar": dict(name="Fire Altar",
        desc="A scorched ruin in the dunes where the sand has turned to "
             "glass. ('craftrune' with rune essence)",
        exits={"out": "al_kharid_square"}, altar="fire"),
    "body_altar": dict(name="Body Altar",
        desc="A squat stone shrine below Ice Mountain, humming with a slow "
             "heartbeat. ('craftrune' with rune essence)",
        exits={"out": "barbarian_village"}, altar="body"),
})
ROOMS["monastery"]["exits"]["altar"] = "mind_altar"
ROOMS["swamp"]["exits"]["altar"] = "water_altar"
ROOMS["varrock_east_bank"]["exits"]["altar"] = "earth_altar"
ROOMS["al_kharid_square"]["exits"]["altar"] = "fire_altar"
ROOMS["barbarian_village"]["exits"]["altar"] = "body_altar"
ROOMS["swamp"]["desc"] += " A still pool glimmers oddly ('altar')."
ROOMS["monastery"]["desc"] += " A path climbs toward the Mind Altar ('altar')."
ROOMS["varrock_east_bank"]["desc"] += " Standing stones rise to the north-east ('altar')."
ROOMS["al_kharid_square"]["desc"] += " Scorched ruins shimmer in the dunes ('altar')."
ROOMS["barbarian_village"]["desc"] += " A humming shrine squats by the rocks ('altar')."
REGIONS.update({"mind_altar": "Edgeville", "water_altar": "Lumbridge",
                "earth_altar": "Varrock", "fire_altar": "AlKharid",
                "body_altar": "Barbarian"})

# --- Yew & magic trees + high-tier fletching ---------------------------------
add_item("yew logs", 160, log_fm_xp=202)
add_item("magic logs", 640, log_fm_xp=303)
TREES["yew"] = ("yew logs", 60, 175)
TREES["magic"] = ("magic logs", 75, 250)
ROOMS["lumbridge_church"]["trees"] = ["yew"]
ROOMS["lumbridge_church"]["desc"] += " Ancient yews shade the graveyard."
ROOMS["seers_village"]["trees"].append("yew")
ROOMS["catherby"]["trees"].append("magic")
ROOMS["catherby"]["desc"] += " A lone magic tree sparkles north of the bank."

for _u, _v in [("yew shortbow (u)", 400), ("yew longbow (u)", 480),
               ("magic shortbow (u)", 800), ("magic longbow (u)", 1050)]:
    add_item(_u, _v)
add_item("yew shortbow", 800, members=True,
         equip={"arange": 47, "slot": "weapon", "req": {"ranged": 40}})
add_item("yew longbow", 960, members=True,
         equip={"arange": 55, "slot": "weapon", "req": {"ranged": 40}})
add_item("magic longbow", 2100, members=True,
         equip={"arange": 71, "slot": "weapon", "req": {"ranged": 50}})
FLETCH_CUT["yew logs"] = [("yew shortbow (u)", 65, 67),
                          ("yew longbow (u)", 70, 75)]
FLETCH_CUT["magic logs"] = [("magic shortbow (u)", 80, 83),
                            ("magic longbow (u)", 85, 91)]
FLETCH_STRING.update({
    "yew shortbow (u)": ("yew shortbow", 65, 67),
    "yew longbow (u)": ("yew longbow", 70, 75),
    "magic shortbow (u)": ("magic shortbow", 80, 83),
    "magic longbow (u)": ("magic longbow", 85, 91),
})

# --- Skill capes (99 mastery; the Wise Old Man sells them in Draynor) --------
SKILLCAPE_PRICE = 99000
for _s in SKILLS:
    add_item(f"{_s} cape", SKILLCAPE_PRICE, equip={
        "dstab": 9, "dslash": 9, "dcrush": 9, "dmagic": 9, "drange": 9,
        "prayer": 1, "slot": "cape", "req": {_s: 99}})


def talk_wise_old_man(p):
    mastered = [s for s in SKILLS if p.base_lvl(s) >= 99]
    if not mastered:
        say("Wise Old Man: \"Master any skill — level 99 — and I'll sell you "
            "its cape of accomplishment. Off you go; greatness takes "
            "grinding.\"")
        return
    say("Wise Old Man: \"Ah, a true master! I can sell you: "
        + ", ".join(f"{s} cape" for s in mastered)
        + f" — {SKILLCAPE_PRICE:,} coins each. Type 'skillcape <skill>'.\"",
        "gold")


def cmd_skillcape(p, arg):
    if p.location != "draynor_village":
        say("The Wise Old Man sells skill capes in Draynor Village.", "grey")
        return
    skill = _resolve_skill(arg)
    if not skill:
        return talk_wise_old_man(p)
    if p.base_lvl(skill) < 99:
        say(f"Wise Old Man: \"Come back when your {skill} is level 99 — it's "
            f"{p.base_lvl(skill)} now.\"", "byellow")
        return
    if not p.has("coins", SKILLCAPE_PRICE):
        say(f"Wise Old Man: \"The cape costs {SKILLCAPE_PRICE:,} coins — "
            "mastery must be celebrated properly.\"", "byellow")
        return
    p.take("coins", SKILLCAPE_PRICE)
    p.add(f"{skill} cape")
    banner("CAPE OF ACCOMPLISHMENT", color="gold", line_color="gold")
    say(f"The Wise Old Man drapes the {skill} cape over your shoulders. "
        "Wear it with pride, master.", "gold", "bold")


QUEST_TALK["skillcape"] = talk_wise_old_man
NPC_NAMES["skillcape"] = "the Wise Old Man"
ROOMS["draynor_village"]["npc"] = ["vampyre_slayer", "witch_potion",
                                   "skillcape"]
ROOMS["draynor_village"]["desc"] += (" The Wise Old Man watches the street "
                                     "from his doorway.")
HANDLERS["skillcape"] = cmd_skillcape
BATCHABLE.add("craft")      # jewellery & leatherwork batch nicely now


# ===========================================================================
#  SKILLING SYNERGIES  (jewellery enchanting, thieving stalls)
# ===========================================================================
# Enchanting: gem rings become magic rings with real effects (cosmic runes,
# magic xp). Stalls: Varrock's tea stall and the Ardougne market give
# thieving a proper ladder beyond pickpocketing.

SHOPS["rune"]["cosmic rune"] = 120

# base ring -> (enchanted ring, magic level, xp, runes)
ENCHANT = {
    "sapphire ring": ("ring of recoil", 7, 17,
                      {"cosmic rune": 1, "water rune": 1}),
    "emerald ring": ("ring of life", 27, 37,
                     {"cosmic rune": 1, "air rune": 3}),
    "ruby ring": ("ring of forging", 49, 59,
                  {"cosmic rune": 1, "fire rune": 5}),
    "diamond ring": ("ring of wealth", 57, 67,
                     {"cosmic rune": 1, "earth rune": 10}),
}
add_item("ring of recoil", 900, equip={"slot": "ring"})
add_item("ring of life", 1200, equip={"slot": "ring"})
add_item("ring of forging", 2100, equip={"slot": "ring"})
add_item("ring of wealth", 3600, equip={"slot": "ring"})


def cmd_enchant(p, arg):
    name = arg.strip().lower()
    if not name:
        say("Enchant which ring? " + ", ".join(
            f"{base} → {e[0]} (magic {e[1]})" for base, e in ENCHANT.items()),
            "bcyan")
        say("  Each needs cosmic + elemental runes (rune shop, or craft "
            "them).", "grey")
        return
    base = name if name in ENCHANT else \
        next((b for b, e in ENCHANT.items()
              if name in b or name in e[0]), None)
    if not base:
        say("You can't enchant that. ('enchant' lists the rings.)", "grey")
        return
    enchanted, lvl, xp, runes = ENCHANT[base]
    if not p.has(base):
        say(f"You have no {base} (craft one at a furnace).", "byellow")
        return
    if p.lvl("magic") < lvl:
        say(f"You need magic level {lvl} to enchant a {base}.", "byellow")
        return
    if not _consume_runes(p, runes):
        say("You need: " + ", ".join(f"{q}x {r}" for r, q in runes.items())
            + ".", "byellow")
        return
    p.take(base)
    p.add(enchanted)
    say(f"The gem flares with power — your {base} is now a {enchanted}!",
        "bmagenta", "bold")
    p.gain_xp("magic", xp)
    return True


HANDLERS["enchant"] = cmd_enchant
BATCHABLE.add("enchant")

# ring effects live in: _player_recoil (combat), _ring_of_life (combat),
# cmd_smelt (forging), _roll_drops (wealth)

# --- Thieving stalls ---------------------------------------------------------
# stall -> (thieving level, xp, [(loot, weight), ...])
STALLS = {
    "tea stall": (5, 16, [("cup of tea", 1.0)]),
    "baker's stall": (20, 24, [("bread", 0.7), ("cake", 0.3)]),
    "silk stall": (35, 48, [("silk", 1.0)]),
    "gem stall": (75, 160, [("uncut sapphire", 0.55), ("uncut emerald", 0.30),
                            ("uncut ruby", 0.12), ("uncut diamond", 0.03)]),
}
add_item("cup of tea", 10, heal=3)
add_item("silk", 60)


def cmd_steal(p, arg):
    if not getattr(p, "members", False):
        say("Thieving is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    stalls = ROOMS[p.location].get("stalls", [])
    if not stalls:
        say("There are no stalls to steal from here.")
        return
    want = arg.strip().lower()
    stall = next((s for s in stalls if want and want in s),
                 None if want else stalls[0])
    if not stall:
        say(f"No such stall. Here: {', '.join(stalls)}")
        return
    lvl, xp, loot = STALLS[stall]
    if p.lvl("thieving") < lvl:
        say(f"You need thieving level {lvl} for the {stall}.", "byellow")
        return
    say(f"You wait for the stallkeeper to look away...")
    if random.random() < gather_chance(p.lvl("thieving"), lvl):
        item = random.choices([i for i, _ in loot],
                              weights=[w for _, w in loot])[0]
        p.add(item)
        say(f"You swipe {item} from the {stall}!", "purple")
        p.gain_xp("thieving", xp)
        return True
    dmg = min(random.randint(1, 3), max(0, p.hp - 1))   # guards won't kill you
    p.hp -= dmg
    say(f"A guard spots you and clubs you for {dmg}! You stumble away, "
        "stunned.", "bred")
    return False


HANDLERS["steal"] = cmd_steal
BATCHABLE.add("steal")
BATCHABLE.add("light")

ROOMS["varrock_square"]["stalls"] = ["tea stall"]
ROOMS["varrock_square"]["desc"] += " A tea stall steams by the fountain."
ROOMS["ardougne"]["stalls"] = ["baker's stall", "silk stall", "gem stall"]
ROOMS["ardougne"]["desc"] += (" Market stalls line the square: baked goods, "
                              "silk, and glittering gems.")


# ===========================================================================
#  MORYTANIA & THE BARROWS  (Priest in Peril -> Canifis -> the six brothers)
# ===========================================================================
# Across the River Salve lies haunted Morytania: complete Priest in Peril
# (King Roald -> Drezel -> slay the temple guardian) to cross. Canifis prowls
# with werewolves, ghasts rot your food in Mort Myre, and at the Barrows you
# can 'dig' into six burial mounds, face each wight's signature power, and
# 'loot' the crypt chest for the famous barrows gear — with set effects.

add_item("spade", 3, tool="spade")
SHOPS["general"]["spade"] = 3
add_item("rotten food", 1)

# --- Morytania monsters ------------------------------------------------------
_add_mob("werewolf",
    {"abonus": 0, "atktype": ["slash"], "att": 60, "cb": 88, "dstab": 20,
     "dslash": 20, "dcrush": 20, "dmagic": 10, "drange": 20, "def": 50,
     "hp": 70, "maxhit": 10, "str": 70, "weak": "magic"},
    [("bones", 1, 1, 1.0), ("coins", 20, 150, 0.8),
     ("grimy ranarr", 1, 1, 0.05)], members=True, rank="hard")

_add_mob("ghast",
    {"abonus": 5, "atktype": ["crush"], "att": 50, "cb": 79, "dstab": 10,
     "dslash": 10, "dcrush": 10, "dmagic": 10, "drange": 10, "def": 40,
     "hp": 45, "maxhit": 8, "str": 55, "weak": "crush"},
    [("coins", 10, 60, 0.5)], members=True, rank="hard")

_add_mob("temple guardian",
    {"abonus": 0, "atktype": ["crush"], "att": 30, "cb": 30, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 0, "drange": 5, "def": 20,
     "hp": 49, "maxhit": 6, "str": 35, "weak": "slash"},
    [("bones", 1, 1, 1.0)], members=True, rank="medium")


def _ghast_rot(p, m, dmg):
    foods = [i for i in p.inventory if "heal" in ITEMS.get(i, {})]
    if foods:
        food = random.choice(foods)
        p.take(food)
        p.add("rotten food")
        print("  " + paint(f"The ghast's touch rots your {food}!", "green"))


MONSTER_EFFECTS["ghast"] = _ghast_rot

# --- The region ----------------------------------------------------------------
ROOMS.update({
    "paterdomus": dict(name="Paterdomus",
        desc="The temple over the River Salve, last light before Morytania. "
             "Drezel the priest keeps a nervous vigil.",
        exits={"west": "varrock_east_bank", "cross": "canifis"},
        npc="drezel", prayer_altar=True, monsters=[], members=True),
    "canifis": dict(name="Canifis",
        desc="A fog-bound town where the locals smile with too many teeth. "
             "A bank and a quiet tavern serve... whatever the locals are.",
        exits={"back": "paterdomus", "south": "mort_myre"},
        bank=True, monsters=["werewolf"], pickpocket=["man"], members=True),
    "mort_myre": dict(name="Mort Myre Swamp",
        desc="A drowned forest of grasping mist. Ghasts drift between the "
             "trees, hungry for the food in your pack.",
        exits={"north": "canifis", "south": "barrows_mounds"},
        monsters=["ghast"], members=True),
    "barrows_mounds": dict(name="The Barrows",
        desc="Six ancient burial mounds rise from the marsh. The air thrums "
             "with old wrath. ('dig' a mound — bring a spade)",
        exits={"north": "mort_myre"},
        barrows=True, members=True),
})
ROOMS["varrock_east_bank"]["exits"]["east"] = "paterdomus"
ROOMS["varrock_east_bank"]["desc"] += (" The road east runs toward the River "
                                       "Salve.")
ROOMS["canifis"]["qlock"] = (
    "priest_in_peril", ("complete",),
    "The temple doors to Morytania are sealed. (Quest: Priest in Peril — "
    "speak to King Roald in Varrock Palace)")
REGIONS.update({"paterdomus": "Morytania", "canifis": "Morytania",
                "mort_myre": "Morytania", "barrows_mounds": "Morytania"})
TRAVEL_HUBS["canifis"] = "canifis"
TRAVEL_NAMES.append("Canifis")

# --- Priest in Peril (the gate quest) --------------------------------------------
ALL_QUESTS["priest_in_peril"] = "Priest in Peril"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["priest_in_peril"] = 1
NPC_NAMES["priest_in_peril"] = "King Roald"
NPC_NAMES["drezel"] = "Drezel"


def talk_roald(p):
    stage = _q(p, "priest_in_peril")
    if stage == "not_started":
        banner("Quest Start: Priest in Peril", color="purple",
               line_color="bmagenta")
        say("King Roald: \"The priest DREZEL, who keeps the temple on the "
            "River Salve east of here, has not reported in weeks. Go east "
            "from the bank and see that he still stands his watch.\"")
        p.quests["priest_in_peril"] = "started"
    elif stage == "complete":
        say("King Roald: \"Varrock sleeps safer for your work at the Salve.\"")
    else:
        say("King Roald: \"The temple lies east of the east bank. See to "
            "Drezel!\"")


def talk_drezel(p):
    stage = _q(p, "priest_in_peril")
    if stage == "started":
        say("Drezel: \"Thank the gods! Something has crawled up from the "
            "crypt — a GUARDIAN of grave-dust and bone. I cannot bless the "
            "Salve while it prowls. Slay it, please!\"", "byellow")
        p.quests["priest_in_peril"] = "guardian"
        if "temple guardian" not in ROOMS["paterdomus"]["monsters"]:
            ROOMS["paterdomus"]["monsters"].append("temple guardian")
    elif stage == "guardian":
        say("Drezel: \"The guardian still prowls the temple — 'fight temple "
            "guardian'!\"")
    elif stage == "cleansed":
        _complete_banner("Priest in Peril")
        say("Drezel blesses the river and throws open the eastern doors. "
            "\"Morytania lies beyond — tread carefully, friend.\" "
            "1406 prayer xp awarded!")
        p.gain_xp("prayer", 1406)
        p.quests["priest_in_peril"] = "complete"
    elif stage == "complete":
        say("Drezel: \"The Salve holds. May it always.\"")
    else:
        say("Drezel: \"A traveller? Speak to King Roald if you would aid "
            "Varrock.\"")


QUEST_TALK["priest_in_peril"] = talk_roald
QUEST_TALK["drezel"] = talk_drezel
ROOMS["varrock_palace"]["npc"] = "priest_in_peril"
ROOMS["varrock_palace"]["desc"] += " King Roald holds court within."
QUEST_HINTS["priest_in_peril"] = {
    "started": "find Drezel at Paterdomus — east from East Varrock's bank",
    "guardian": "slay the temple guardian at Paterdomus",
    "cleansed": "speak to Drezel to bless the Salve",
}

# --- The six brothers ---------------------------------------------------------------
# name -> (attack style key, signature note)
BROTHERS = {
    "ahrim the blighted": "magic",
    "dharok the wretched": "melee",
    "guthan the infested": "melee",
    "karil the tainted": "ranged",
    "torag the corrupted": "melee",
    "verac the defiled": "melee",
}

_BROTHER_STATS = {"abonus": 30, "att": 100, "cb": 115, "dstab": 60,
                  "dslash": 60, "dcrush": 60, "dmagic": 40, "drange": 60,
                  "def": 70, "hp": 100, "maxhit": 16, "str": 100,
                  "weak": "magic"}
for _b in BROTHERS:
    _s = dict(_BROTHER_STATS)
    _s["atktype"] = ["slash"]
    _add_mob(_b, _s, [("coins", 100, 600, 0.6)], members=True)
    MONSTERS[_b]["boss"] = True
    MONSTERS[_b]["rank"] = "boss"
    _BOSSES.add(_b)

BARROWS_ART = r'''
        _______
       /  RIP  \
      |  .-=-.  |
      | (  x  ) |
     _|__|___|__|_
'''
def _brother_intro(name):
    return [_tint(BARROWS_ART, "grey", "dim"), _tint(BARROWS_ART, "grey"),
            _tint(BARROWS_ART, "purple", "bold"),
            _tint(BARROWS_ART, "bmagenta", "bold")]


def _brother_death(name):
    return [_tint(BARROWS_ART, "purple"), _tint(BARROWS_ART, "grey"),
            _tint(BARROWS_ART, "grey", "dim")]


for _b in BROTHERS:
    MONSTER_ART[_b] = BARROWS_ART
    BOSS_INTRO[_b] = _brother_intro
    BOSS_DEATH[_b] = _brother_death


def _brother_take_turn(p, m):
    """Each wight fights with its brother's old power."""
    name = m["name"].split(" ")[0]
    style = BROTHERS[m["name"]]
    verb = {"magic": "hurls a gout of blighted fire",
            "ranged": "looses a volley of black bolts",
            "melee": "swings his weapon in a killing arc"}
    say(f"{m['name'].title()} {verb[style]}!", "purple", "bold")
    m_att_roll = (m["attack"] + 9) * (m.get("abonus", 0) + 64)
    dtype = {"magic": "magic", "ranged": "ranged"}.get(style, "crush")
    p_def_roll = _player_def_roll(p, dtype)
    max_hit = m["max_hit"]
    if name == "dharok":                # hits harder as HIS wounds deepen
        max_hit = int(max_hit * (1 + (1 - m["cur"] / m["hp"])))
    prot = {"magic": "magic", "ranged": "ranged"}.get(style, "melee")
    protected = p.prayer_protects(prot) and name != "verac"
    if random.random() < _accuracy(m_att_roll, p_def_roll):
        dmg = random.randint(0, max_hit)
        if protected:
            dmg = int(dmg * 0.5)
        p.hp -= dmg
        hpbar = "  " + paint("HP ", "white") + bar_meter(max(p.hp, 0),
                                                         p.max_hp, 18)
        if name == "verac" and dmg and p.prayer_protects("melee"):
            print("  " + paint(f"Verac's flail swings THROUGH your prayer "
                               f"for {dmg}!", "bmagenta") + hpbar)
        elif dmg == 0:
            print("  " + paint("Its blow grazes you. (0)", "grey") + hpbar)
        else:
            print("  " + paint(f"It hits you for {dmg}.", "bred") + hpbar)
        if p.hp > 0 and dmg > 0:
            _player_recoil(p, m, dmg)
            if name == "ahrim" and random.random() < 0.25:
                p.stat_drain["strength"] = p.stat_drain.get("strength", 0) + 2
                print("  " + paint("Ahrim's blight saps your strength! (-2)",
                                   "bblue"))
            elif name == "guthan" and m["cur"] < m["hp"]:
                heal = dmg // 2
                if heal:
                    m["cur"] = min(m["hp"], m["cur"] + heal)
                    print("  " + paint(f"Guthan's spear siphons your life "
                                       f"(+{heal}).", "lime"))
            elif name == "torag" and random.random() < 0.25:
                p.run_energy = max(0, getattr(p, "run_energy", 100) - 20)
                print("  " + paint("Torag's hammers crush your stamina "
                                   "(-20 energy).", "bblue"))
            elif name == "karil" and random.random() < 0.25:
                p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
                print("  " + paint("Karil's taint corrodes your defence! "
                                   "(-2)", "bblue"))
    else:
        print("  " + paint("You weather the wight's assault.", "grey"))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer points).",
                               "bmagenta"))
    return "died" if p.hp <= 0 else None


for _b in BROTHERS:
    BOSS_TURN[_b] = _brother_take_turn

# --- dig / loot ------------------------------------------------------------------------
def cmd_dig(p, arg):
    if p.location == "falador_park":
        if not p.find_tool("spade"):
            say("You need a spade (general store).", "byellow")
            return
        say("You dig into the great molehill and tumble into a dark, "
            "earth-smelling burrow...", "brown")
        p.location = "mole_lair"
        return cmd_look(p, "")
    if p.location != "barrows_mounds":
        say("There's nothing worth digging here.", "grey")
        return
    if not p.find_tool("spade"):
        say("You need a spade (general store).", "byellow")
        return
    slain = set(getattr(p, "barrows", []))
    left = [b for b in BROTHERS if b not in slain]
    if not left:
        say("All six mounds lie quiet. The tunnel below is open — 'loot' "
            "the chest!", "bgreen")
        return
    want = arg.strip().lower()
    target = next((b for b in left if want and want in b), left[0])
    say(f"You dig into the mound... and drop into a burial crypt. "
        f"({len(slain)}/6 brothers at rest)", "purple")
    _start_combat(p, target)


def cmd_loot(p, _a):
    if p.location != "barrows_mounds":
        say("There's no chest to loot here.", "grey")
        return
    slain = set(getattr(p, "barrows", []))
    left = [b for b in BROTHERS if b not in slain]
    if left:
        say(f"The tunnel is sealed while brothers still stir — {len(left)} "
            "mound(s) to go. ('dig')", "byellow")
        return
    p.barrows = []
    p.barrows_loots = getattr(p, "barrows_loots", 0) + 1
    show_art(ART_QUEST, "gold", center=True)
    banner("THE BARROWS CHEST", color="purple", line_color="bmagenta")
    coins = random.randint(4000, 20000)
    p.add("coins", coins)
    say(f"  Coins x{coins:,}", "gold")
    for rune, lo, hi in [("death rune", 8, 40), ("chaos rune", 15, 60),
                         ("nature rune", 5, 25)]:
        q = random.randint(lo, hi)
        p.add(rune, q)
        say(f"  {rune} x{q}", "byellow")
    if random.random() < 0.30:
        piece = random.choice(BARROWS_GEAR)
        p.add(piece)
        say(f"  ✦ BARROWS: {piece}!", "bmagenta", "bold")
    else:
        say("  (No barrows equipment this time — the brothers stir again.)",
            "grey")
    say("The mounds seal themselves behind you. The dead do not stay dead "
        "here.", "purple")


HANDLERS["dig"] = cmd_dig
HANDLERS["loot"] = cmd_loot


def _barrows_on_kill(p, target):
    if target not in BROTHERS or p.location != "barrows_mounds":
        return
    if target not in p.barrows:
        p.barrows.append(target)
    n = len(p.barrows)
    if n >= len(BROTHERS):
        say("The last wight crumbles. Below the mounds, a tunnel grinds "
            "open — 'loot' the chest!", "bmagenta", "bold")
    else:
        say(f"{target.title()} returns to his rest. ({n}/6 — 'dig' the next "
            "mound)", "purple")


# --- Barrows gear (weapon + body per brother; wear both for the set effect) ---
BARROWS_GEAR = [
    "dharok's greataxe", "dharok's platebody",
    "ahrim's staff", "ahrim's robetop",
    "karil's crossbow", "karil's leathertop",
    "guthan's warspear", "guthan's platebody",
    "torag's hammers", "torag's platebody",
    "verac's flail", "verac's brassard",
]
add_item("dharok's greataxe", 800000, members=True, equip={
    "aslash": 90, "acrush": 70, "str": 105, "slot": "weapon",
    "req": {"attack": 70}})
add_item("dharok's platebody", 800000, members=True, equip={
    "dstab": 90, "dslash": 88, "dcrush": 85, "dmagic": -5, "drange": 90,
    "slot": "body", "req": {"defence": 70}})
add_item("ahrim's staff", 700000, members=True, equip={
    "amagic": 25, "dmagic": 15, "mdmg": 5, "slot": "weapon",
    "req": {"magic": 70}})
add_item("ahrim's robetop", 700000, members=True, equip={
    "amagic": 22, "dmagic": 60, "dstab": 35, "dslash": 30, "dcrush": 40,
    "slot": "body", "req": {"magic": 70}})
add_item("karil's crossbow", 700000, members=True, equip={
    "arange": 94, "slot": "weapon", "req": {"ranged": 70}})
add_item("karil's leathertop", 700000, members=True, equip={
    "drange": 90, "dmagic": 45, "dstab": 45, "dslash": 40, "dcrush": 45,
    "arange": 3, "slot": "body", "req": {"ranged": 70}})
add_item("guthan's warspear", 750000, members=True, equip={
    "astab": 85, "aslash": 70, "acrush": 70, "str": 85, "slot": "weapon",
    "req": {"attack": 70}})
add_item("guthan's platebody", 750000, members=True, equip={
    "dstab": 88, "dslash": 86, "dcrush": 83, "dmagic": -5, "drange": 88,
    "slot": "body", "req": {"defence": 70}})
add_item("torag's hammers", 700000, members=True, equip={
    "acrush": 90, "str": 90, "slot": "weapon", "req": {"attack": 70}})
add_item("torag's platebody", 700000, members=True, equip={
    "dstab": 92, "dslash": 90, "dcrush": 88, "dmagic": -4, "drange": 92,
    "slot": "body", "req": {"defence": 70}})
add_item("verac's flail", 750000, members=True, equip={
    "acrush": 88, "astab": 70, "str": 84, "prayer": 3, "slot": "weapon",
    "req": {"attack": 70}})
add_item("verac's brassard", 750000, members=True, equip={
    "dstab": 85, "dslash": 83, "dcrush": 84, "dmagic": 0, "drange": 85,
    "prayer": 3, "slot": "body", "req": {"defence": 70}})


# ===========================================================================
#  REGIONAL GAP-FILL  (the world's completed regions get their missing bits)
# ===========================================================================

# --- Pickables (data-driven 'pick') ------------------------------------------
add_item("banana", 2, heal=2)
ROOMS["lumbridge_farm"]["pick"] = ["grain"]
ROOMS["draynor_village"]["pick"] = ["grain"]
ROOMS["karamja_port"]["pick"] = ["banana"]
ROOMS["karamja_port"]["desc"] += " Banana palms sway overhead."
ROOMS["seers_village"]["pick"] = ["flax"]
ROOMS["seers_village"]["desc"] += " A blue flax field ripples south of town."
ROOMS["falador_east"]["pick"] = ["cabbage"]
ROOMS["falador_east"]["desc"] += " The famous cabbage patch grows by the wall."
BATCHABLE.add("pick")

# --- Fishing spots the regions were missing -----------------------------------
ROOMS["draynor_village"]["fish_tools"] = ["net"]
ROOMS["draynor_village"]["desc"] += " Fishing spots bubble along the riverbank."
ROOMS["karamja_port"]["fish_tools"] = ["net", "rod", "cage", "harpoon"]
ROOMS["karamja_port"]["desc"] += (" The dock heaves with lobster pots and "
                                  "harpoon fishers.")

# --- Edgeville's famous yews ----------------------------------------------------
ROOMS["edgeville"]["trees"] = ["yew"]
ROOMS["edgeville"]["desc"] += " A stand of old yews grows south of the bank."

# --- The Wilderness gets its green dragons + the Chaos Temple -------------------
ROOMS["deep_wilderness"]["monsters"].append("green dragon")
ROOMS["deep_wilderness"]["desc"] += (" Green dragons wheel over the blasted "
                                     "ground.")
ROOMS.update({
    "chaos_temple": dict(name="Chaos Temple",
        desc="A ruined shrine to the god of chaos, deep in the wastes. "
             "Burying bones at its blood-stained altar honours something "
             "hungry. (bones buried here give +50% prayer xp)",
        exits={"south": "deep_wilderness"},
        prayer_altar=True, chaos_altar=True, monsters=["dark wizard"]),
})
ROOMS["deep_wilderness"]["exits"]["temple"] = "chaos_temple"
REGIONS["chaos_temple"] = "Wilderness"

# --- The Giant Mole beneath Falador Park -----------------------------------------
add_item("mole claw", 3500)
add_item("mole skin", 1500)

MOLE_ART = r'''
        ______________
       /  .-.    .-.  \
      |  ( o )  ( o )  |__
      |   `-'.--.`-'   |  \__
       \    (####)    /  \/..\
     ___\__ `~~~~' __/____\/\/
    /_/\_\/_______\/_/\_\_\/
'''


def _mole_intro(name):
    return [_tint(MOLE_ART, "brown"), _tint(MOLE_ART, "byellow"),
            _tint(MOLE_ART, "brown", "bold")]


def _mole_death(name):
    return [_tint(MOLE_ART, "brown"), _tint(MOLE_ART, "grey", "dim")]


def _mole_dirt(p, m, dmg):
    p.stat_drain["attack"] = p.stat_drain.get("attack", 0) + 2
    print("  " + paint("Dirt sprays into your eyes! (-2 attack)", "bblue"))


MOLE_ATTACKS = [
    {"label": "a raking claw swipe", "verb": "lashes out with",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(MOLE_ART, "brown", "bold")],
     "mult": 1.2, "w": 4, "atype": "slash"},
    {"label": "a spray of blinding dirt", "verb": "kicks up",
     "color": ("byellow",),
     "builder": lambda: [_tint(MOLE_ART, "byellow")],
     "mult": 0.8, "w": 2, "atype": "ranged", "effect": _mole_dirt},
    {"label": "a burrowing charge from below", "verb": "erupts in",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(MOLE_ART, "brown")],
     "mult": 1.4, "w": 2, "atype": "crush"},
]


def _mole_take_turn(p, m):
    if m["cur"] < m["hp"] and random.random() < 0.2:
        heal = random.randint(8, 15)
        m["cur"] = min(m["hp"], m["cur"] + heal)
        say("The Giant Mole burrows away in a spray of soil... and "
            f"resurfaces, refreshed. (+{heal})", "brown")
        return None
    return _boss_take_turn(p, m, MOLE_ATTACKS)


_add_mob("giant mole",
    {"abonus": 10, "atktype": ["slash", "crush"], "att": 60, "cb": 90,
     "dstab": 30, "dslash": 40, "dcrush": 40, "dmagic": 20, "drange": 40,
     "def": 60, "hp": 120, "maxhit": 12, "str": 70, "weak": "stab"},
    [("big bones", 1, 1, 1.0), ("mole claw", 1, 1, 1.0),
     ("mole skin", 1, 3, 1.0), ("coins", 200, 1500, 0.9)], rank="boss")
MONSTERS["giant mole"]["boss"] = True
_BOSSES.add("giant mole")
BOSS_INTRO["giant mole"] = _mole_intro
BOSS_DEATH["giant mole"] = _mole_death
BOSS_TURN["giant mole"] = _mole_take_turn
MONSTER_ART["giant mole"] = MOLE_ART

ROOMS.update({
    "falador_park": dict(name="Falador Park",
        desc="A tidy garden of hedges and flowerbeds — ruined by an "
             "enormous molehill in the lawn. ('dig' it, if you dare)",
        exits={"south": "falador_square"}),
    "mole_lair": dict(name="Mole Lair",
        desc="A vast earthen warren beneath the park. Something huge moves "
             "in the dark, showering soil from the ceiling.",
        exits={"up": "falador_park"},
        monsters=["giant mole"], dig_entry=True),
})
ROOMS["falador_square"]["exits"]["park"] = "falador_park"
ROOMS["falador_square"]["desc"] += " Falador Park lies north ('park')."
REGIONS.update({"falador_park": "Falador", "mole_lair": "Falador"})


# ===========================================================================
#  SKILLING EXPANSION III  (high runecrafting, wilderness agility, slayer
#  rewards)
# ===========================================================================

# --- High runecrafting altars -------------------------------------------------
RUNECRAFT.update({"chaos rune": (35, 8.5), "nature rune": (44, 9),
                  "law rune": (54, 9.5), "death rune": (65, 10)})
ROOMS["chaos_temple"]["altar"] = "chaos"     # the temple earns its name
ROOMS["chaos_temple"]["desc"] += (" The blood-stained altar also binds "
                                  "essence into chaos runes ('craftrune').")
ROOMS.update({
    "nature_altar": dict(name="Nature Altar",
        desc="A living shrine deep in the Karamja jungle, vines coiling "
             "over ancient stone. ('craftrune' with rune essence)",
        exits={"out": "brimhaven"}, altar="nature", members=True),
    "law_altar": dict(name="Law Altar",
        desc="A wind-swept holy islet off Catherby's shore, humming with "
             "order. ('craftrune' with rune essence)",
        exits={"boat": "catherby"}, altar="law", members=True),
    "death_altar": dict(name="Death Altar",
        desc="A lightless crypt beneath Paterdomus where the air itself "
             "feels thin. ('craftrune' with rune essence)",
        exits={"up": "paterdomus"}, altar="death", members=True,
        qlock=("priest_in_peril", ("complete",),
               "Drezel bars the crypt stair. (Quest: Priest in Peril)")),
})
ROOMS["brimhaven"]["exits"]["altar"] = "nature_altar"
ROOMS["brimhaven"]["desc"] += " A vine-choked shrine glows in the jungle ('altar')."
ROOMS["catherby"]["exits"]["islet"] = "law_altar"
ROOMS["catherby"]["desc"] += " A ferryman poles out to a holy islet ('islet')."
ROOMS["paterdomus"]["exits"]["crypt"] = "death_altar"
REGIONS.update({"nature_altar": "Karamja", "law_altar": "Kandarin",
                "death_altar": "Morytania"})

# --- Wilderness agility course (level 52; great xp, real teeth) ---------------
ROOMS.update({
    "wilderness_course": dict(name="Wilderness Agility Course",
        desc="A gauntlet of rope swings and log balances strung over a "
             "ravine in the wastes. Only the sure-footed survive. "
             "('agility' to run a lap)",
        exits={"south": "deep_wilderness"},
        agility_course=(52, 48, 9)),
})
ROOMS["deep_wilderness"]["exits"]["course"] = "wilderness_course"
ROOMS["deep_wilderness"]["desc"] += (" Ropes and logs of an agility course "
                                     "sway over a ravine ('course').")
REGIONS["wilderness_course"] = "Wilderness"

# --- Slayer rewards (Vannaka trades slayer points) ------------------------------
add_item("slayer helmet", 50000, members=True, equip={
    "dstab": 30, "dslash": 32, "dcrush": 27, "dmagic": -1, "drange": 30,
    "slot": "head", "req": {"defence": 10}})

SLAYER_REWARDS = {
    "slayer helmet": (60, "a snarling helmet: +15% accuracy & damage "
                          "against your slayer task"),
    "slayer tome": (25, "Vannaka's teachings: +2,500 slayer xp, instantly"),
    "task skip": (8, "abandon your current task and get a fresh one"),
}


def cmd_slayerbuy(p, arg):
    if not getattr(p, "members", False):
        say("Slayer is a members skill. Type 'membership' to unlock it.",
            "bmagenta")
        return
    if p.location != "edgeville":
        say("Vannaka trades slayer points in Edgeville.", "grey")
        return
    want = arg.strip().lower()
    if not want:
        banner("Slayer Rewards", color="teal", line_color="teal")
        print("  " + paint(f"Your points: {p.slayer_points}", "white"))
        for name, (cost, desc) in SLAYER_REWARDS.items():
            print(f"  {name:14} " + paint(f"{cost:>3} pts", "teal")
                  + "  " + paint(desc, "grey"))
        say("  Buy with 'slayerbuy <reward>'.", "grey")
        return
    name = next((n for n in SLAYER_REWARDS if want in n), None)
    if not name:
        say("Vannaka doesn't trade that. ('slayerbuy' lists rewards.)", "grey")
        return
    cost, _desc = SLAYER_REWARDS[name]
    if p.slayer_points < cost:
        say(f"You need {cost} slayer points ({p.slayer_points} held). "
            "Complete tasks to earn more.", "byellow")
        return
    if name == "task skip" and not getattr(p, "slayer_task", None):
        say("You have no task to skip — see Vannaka ('talk').", "grey")
        return
    p.slayer_points -= cost
    if name in ("earmuffs", "mirror shield", "rock hammer"):
        p.add(name)
        say(f"Vannaka hands over the {name}. Use it well.", "teal")
        return
    if name == "slayer helmet":
        p.add("slayer helmet")
        say("Vannaka hands you a snarling SLAYER HELMET. Wear it on task "
            "and strike true.", "teal", "bold")
    elif name == "slayer tome":
        say("You absorb Vannaka's hard-won knowledge.", "teal")
        p.gain_xp("slayer", 2500)
    elif name == "task skip":
        p.slayer_task = None
        p.task_streak = 0
        say("Vannaka waves the task away. 'Talk' to me for a new one.",
            "teal")


HANDLERS["slayerbuy"] = cmd_slayerbuy
HANDLERS["rewards"] = cmd_slayerbuy


# ===========================================================================
#  INTERFACE REFINEMENTS  (character dashboard + item effect notes)
# ===========================================================================
def cmd_me(p, _a):
    """One-screen character dashboard."""
    banner(f"{p.name} — Combat level {p.combat_level()}", color="gold")
    total = sum(p.lvl(s) for s in SKILLS)
    txp = sum(p.skills[s] for s in SKILLS)
    done = sum(1 for k in ALL_QUESTS if _q(p, k) == "complete")
    ach = len(getattr(p, "achievements", []))
    bosses = getattr(p, "bosses", [])
    bank_val = sum(ITEMS.get(i, {}).get("value", 0) * q
                   for i, q in p.bank.items())
    task = getattr(p, "slayer_task", None)
    task_str = (f"  ·  task: {task['remaining']}/{task['amount']} "
                f"{task['monster']}s" if task and task.get("remaining")
                else "")
    rows = [
        ("Total level", f"{total}   ({txp:,} xp)"),
        ("Quests", f"{done}/{len(ALL_QUESTS)} complete  ·  "
                   f"{quest_points(p)} quest points"),
        ("Achievements", f"{ach}/{len(ACHIEVEMENTS)} unlocked"),
        ("Combat", f"{getattr(p, 'kills', 0):,} kills  ·  "
                   f"{len(bosses)}/{len(_BOSSES)} bosses slain"),
        ("Slayer", f"level {p.lvl('slayer')}  ·  "
                   f"{p.slayer_points} points{task_str}"),
        ("Barrows", f"{getattr(p, 'barrows_loots', 0)} chest(s) looted"),
        ("Wealth", f"{p.coins:,} coins held  ·  bank worth ~{bank_val:,} gp"),
        ("Location", ROOMS[p.location]["name"]
                     + ("  ·  member" if p.members else "")),
    ]
    for k, v in rows:
        print("  " + paint(f"{k:13}", "byellow") + paint(v, "white"))
    if bosses:
        say("  Bosses: " + ", ".join(sorted(bosses)), "grey")
    print("  " + paint("Next up      ", "bcyan", "bold")
          + paint(_next_goal(p), "bcyan"))
    say("  ('stats' for skills, 'quests', 'achievements', 'bestiary')", "grey")


HANDLERS["me"] = cmd_me
HANDLERS["character"] = cmd_me
HANDLERS["profile"] = cmd_me

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


# ===========================================================================
#  GOD WARS DUNGEON  (four generals, kill count, godswords)
# ===========================================================================
# A frozen chasm in the deep Wilderness. Slay a god's followers for kill
# count (10 opens their general's door — and is consumed). Each general
# fights differently; all drop godsword shards, rarely their hilt. Smith 3
# shards into a blade (smithing 80), then 'smith <god> godsword'.

GWD_FOLLOWERS = {"spiritual warrior": "bandos", "aviansie": "armadyl",
                 "bloodveld": "zamorak", "knight of saradomin": "saradomin"}

_add_mob("spiritual warrior",
    {"abonus": 15, "atktype": ["slash"], "att": 80, "cb": 115, "dstab": 40,
     "dslash": 40, "dcrush": 35, "dmagic": 20, "drange": 40, "def": 60,
     "hp": 65, "maxhit": 11, "str": 85, "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 80, 400, 0.8)],
    members=True, rank="elite")
_add_mob("aviansie",
    {"abonus": 25, "atktype": ["ranged"], "att": 70, "cb": 92, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 30, "drange": 45, "def": 55,
     "hp": 60, "maxhit": 10, "str": 60, "weak": "ranged"},
    [("bones", 1, 1, 1.0), ("coins", 60, 350, 0.8),
     ("adamant bar", 1, 2, 0.15)], members=True, rank="elite")
MONSTERS["aviansie"]["flying"] = True
_add_mob("bloodveld",
    {"abonus": 10, "atktype": ["crush"], "att": 75, "cb": 76, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 25, "drange": 25, "def": 50,
     "hp": 70, "maxhit": 10, "str": 80, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 60, 350, 0.8)],
    members=True, rank="elite")
_add_mob("knight of saradomin",
    {"abonus": 20, "atktype": ["slash"], "att": 85, "cb": 101, "dstab": 45,
     "dslash": 45, "dcrush": 40, "dmagic": 30, "drange": 45, "def": 65,
     "hp": 65, "maxhit": 11, "str": 80, "weak": "crush"},
    [("bones", 1, 1, 1.0), ("coins", 80, 400, 0.8)],
    members=True, rank="elite")

# --- the generals -------------------------------------------------------------
_GOD_ART = r'''
        \\  ______________  //
         \\/    \    /    \//
         |  (@)  |  |  (@)  |
          \_____/ || \_____/
           /##### || #####\
          |__/  WAAAGH  \__|
'''


def _god_intro(name):
    return [_tint(_GOD_ART, "grey"), _tint(_GOD_ART, "byellow", "bold"),
            _tint(_GOD_ART, "bred", "bold")]


def _god_death(name):
    return [_tint(_GOD_ART, "bred"), _tint(_GOD_ART, "grey", "dim")]


def _stomp_drain(p, m, dmg):
    p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
    print("  " + paint("The stomp rattles your armour! (-2 defence)", "bblue"))


GRAARDOR_ATTACKS = [
    {"label": "a fist like a falling boulder", "verb": "swings",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bred", "bold")],
     "mult": 1.3, "w": 4, "atype": "crush"},
    {"label": "a squall of skull-sized gravel", "verb": "hurls",
     "color": ("byellow",),
     "builder": lambda: [_tint(_GOD_ART, "byellow")],
     "mult": 0.9, "w": 3, "atype": "ranged"},
    {"label": "a ground-splitting stomp", "verb": "delivers",
     "color": ("brown", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "brown", "bold")],
     "mult": 1.1, "w": 2, "atype": "crush", "effect": _stomp_drain},
]

KREE_ATTACKS = [
    {"label": "a shrieking blast of wind", "verb": "summons",
     "color": ("bcyan", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bcyan", "bold")],
     "mult": 1.2, "w": 3, "atype": "ranged"},
    {"label": "a spiralling tornado", "verb": "conjures",
     "color": ("bwhite",),
     "builder": lambda: [_tint(_GOD_ART, "bwhite")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]

KRIL_ATTACKS = [
    {"label": "twin blazing scimitars", "verb": "whirls",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bred", "bold")],
     "mult": 1.2, "w": 3, "atype": "slash"},
    {"label": "a gout of demonfire", "verb": "breathes",
     "color": ("orange", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "orange", "bold")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]

ZILYANA_MELEE = [
    {"label": "her crackling blade", "verb": "flickers in with",
     "color": ("bwhite", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "bwhite", "bold")],
     "mult": 1.0, "w": 1, "atype": "slash"},
]
ZILYANA_MAGIC = [
    {"label": "a bolt of searing light", "verb": "hurls",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(_GOD_ART, "byellow", "bold")],
     "mult": 1.0, "w": 1, "atype": "magic"},
]


def _kril_take_turn(p, m):
    # his scythe smashes THROUGH protection prayers a quarter of the time
    if p.prayer_protects("melee") and random.random() < 0.25:
        dmg = random.randint(10, m["max_hit"] + 6)
        p.hp -= dmg
        drain = random.randint(8, 16)
        p.prayer_points = max(0, p.prayer_points - drain)
        say("K'ril Tsutsaroth roars — his scythe tears STRAIGHT THROUGH "
            f"your prayer for {dmg}! (-{drain} prayer)", "bred", "bold")
        print("  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
        return "died" if p.hp <= 0 else None
    return _boss_take_turn(p, m, KRIL_ATTACKS)


def _zilyana_take_turn(p, m):
    if _boss_take_turn(p, m, ZILYANA_MELEE) == "died":
        return "died"
    say("She blurs with impossible speed — a second strike!", "bwhite")
    return _boss_take_turn(p, m, ZILYANA_MAGIC)


_GENERALS = {
    "general graardor": ("bandos",
        {"abonus": 40, "atktype": ["crush", "ranged"], "att": 180, "cb": 624,
         "dstab": 70, "dslash": 70, "dcrush": 60, "dmagic": 60, "drange": 70,
         "def": 90, "hp": 255, "maxhit": 26, "str": 190, "weak": "stab"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("bandos chestplate", 1, 1, 0.08), ("bandos tassets", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("bandos hilt", 1, 1, 0.05)],
        lambda p, m: _boss_take_turn(p, m, GRAARDOR_ATTACKS)),
    "kree'arra": ("armadyl",
        {"abonus": 45, "atktype": ["ranged", "magic"], "att": 160, "cb": 580,
         "dstab": 60, "dslash": 60, "dcrush": 60, "dmagic": 70, "drange": 75,
         "def": 80, "hp": 230, "maxhit": 20, "str": 150, "weak": "ranged"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("armadyl chestplate", 1, 1, 0.08),
         ("armadyl chainskirt", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("armadyl hilt", 1, 1, 0.05)],
        lambda p, m: _boss_take_turn(p, m, KREE_ATTACKS)),
    "k'ril tsutsaroth": ("zamorak",
        {"abonus": 40, "atktype": ["slash", "magic"], "att": 170, "cb": 650,
         "dstab": 65, "dslash": 65, "dcrush": 65, "dmagic": 65, "drange": 65,
         "def": 85, "hp": 255, "maxhit": 24, "str": 180, "weak": "slash"},
        [("big bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("zamorakian spear", 1, 1, 0.08),
         ("godsword shard", 1, 1, 0.25), ("zamorak hilt", 1, 1, 0.05)],
        _kril_take_turn),
    "commander zilyana": ("saradomin",
        {"abonus": 50, "atktype": ["slash", "magic"], "att": 175, "cb": 596,
         "dstab": 60, "dslash": 60, "dcrush": 55, "dmagic": 70, "drange": 60,
         "def": 80, "hp": 240, "maxhit": 16, "str": 150, "weak": "crush"},
        [("bones", 1, 1, 1.0), ("coins", 2000, 9000, 1.0),
         ("saradomin sword", 1, 1, 0.10),
         ("godsword shard", 1, 1, 0.25), ("saradomin hilt", 1, 1, 0.05)],
        _zilyana_take_turn),
}
for _g, (_god, _st, _drops, _turn) in _GENERALS.items():
    _add_mob(_g, _st, _drops, members=True)
    MONSTERS[_g]["boss"] = True
    MONSTERS[_g]["rank"] = "boss"
    _BOSSES.add(_g)
    BOSS_TURN[_g] = _turn
    BOSS_INTRO[_g] = _god_intro
    BOSS_DEATH[_g] = _god_death
MONSTERS["kree'arra"]["flying"] = True

# --- the rooms ------------------------------------------------------------------
ROOMS.update({
    "gwd_entrance": dict(name="God Wars Dungeon",
        desc="A frozen chasm where four god armies wage an endless war. "
             "Sealed doors bear each god's sigil — slay their followers for "
             "the kill count to enter (10 per door).",
        exits={"up": "deep_wilderness", "bandos": "bandos_stronghold",
               "armadyl": "armadyl_eyrie", "zamorak": "zamorak_fortress",
               "saradomin": "saradomin_encampment"},
        gwd=True, members=True),
    "bandos_stronghold": dict(name="Bandos' Stronghold",
        desc="Ogre-forged iron and the stink of war. Spiritual warriors "
             "drill for a battle that never ends.",
        exits={"out": "gwd_entrance", "door": "graardor_arena"},
        monsters=["spiritual warrior"], gwd=True, members=True),
    "graardor_arena": dict(name="Graardor's Arena",
        desc="A shattered throne room. GENERAL GRAARDOR bellows a challenge "
             "that cracks the ice.",
        exits={"out": "bandos_stronghold"},
        monsters=["general graardor"], kc_lock=("bandos", 10),
        gwd=True, members=True),
    "armadyl_eyrie": dict(name="Armadyl's Eyrie",
        desc="A wind-scoured spire open to the black sky. Aviansie wheel "
             "overhead on vast wings.",
        exits={"out": "gwd_entrance", "door": "kree_arena"},
        monsters=["aviansie"], gwd=True, members=True),
    "kree_arena": dict(name="Kree'arra's Roost",
        desc="The eyrie's summit. KREE'ARRA hangs in the howling air — "
             "blades will barely reach him up there.",
        exits={"out": "armadyl_eyrie"},
        monsters=["kree'arra"], kc_lock=("armadyl", 10),
        gwd=True, members=True),
    "zamorak_fortress": dict(name="Zamorak's Fortress",
        desc="Black iron and open flame. Bloodvelds drag their tongues "
             "across the ice.",
        exits={"out": "gwd_entrance", "door": "kril_arena"},
        monsters=["bloodveld"], gwd=True, members=True),
    "kril_arena": dict(name="K'ril's Sanctum",
        desc="A cathedral of fire. K'RIL TSUTSAROTH unfurls to his full "
             "height — prayers mean little to his scythe.",
        exits={"out": "zamorak_fortress"},
        monsters=["k'ril tsutsaroth"], kc_lock=("zamorak", 10),
        gwd=True, members=True),
    "saradomin_encampment": dict(name="Saradomin's Encampment",
        desc="White banners over cold ground. Knights of Saradomin hold "
             "their line with weary discipline.",
        exits={"out": "gwd_entrance", "door": "zilyana_arena"},
        monsters=["knight of saradomin"], gwd=True, members=True),
    "zilyana_arena": dict(name="Zilyana's Ground",
        desc="A ring of shattered ice. COMMANDER ZILYANA paces faster than "
             "the eye can follow.",
        exits={"out": "saradomin_encampment"},
        monsters=["commander zilyana"], kc_lock=("saradomin", 10),
        gwd=True, members=True),
})
ROOMS["deep_wilderness"]["exits"]["chasm"] = "gwd_entrance"
ROOMS["deep_wilderness"]["desc"] += (" A frozen chasm yawns in the north — "
                                     "the God Wars rage below ('chasm').")
for _rm in ("gwd_entrance", "bandos_stronghold", "graardor_arena",
            "armadyl_eyrie", "kree_arena", "zamorak_fortress", "kril_arena",
            "saradomin_encampment", "zilyana_arena"):
    REGIONS[_rm] = "Wilderness"

# --- god gear ----------------------------------------------------------------------
add_item("bandos chestplate", 2500000, members=True, equip={
    "dstab": 92, "dslash": 90, "dcrush": 88, "dmagic": -5, "drange": 92,
    "str": 4, "slot": "body", "req": {"defence": 65}})
add_item("bandos tassets", 2000000, members=True, equip={
    "dstab": 85, "dslash": 82, "dcrush": 80, "dmagic": -5, "drange": 85,
    "str": 2, "slot": "legs", "req": {"defence": 65}})
add_item("armadyl chestplate", 2500000, members=True, equip={
    "arange": 33, "dstab": 55, "dslash": 55, "dcrush": 55, "dmagic": 50,
    "drange": 90, "slot": "body", "req": {"ranged": 70}})
add_item("armadyl chainskirt", 2000000, members=True, equip={
    "arange": 20, "dstab": 50, "dslash": 50, "dcrush": 50, "dmagic": 45,
    "drange": 85, "slot": "legs", "req": {"ranged": 70}})
add_item("zamorakian spear", 2000000, members=True, equip={
    "astab": 85, "aslash": 65, "acrush": 65, "str": 75, "prayer": 2,
    "slot": "weapon", "req": {"attack": 70}})
add_item("saradomin sword", 1200000, members=True, equip={
    "aslash": 82, "acrush": 60, "str": 82, "prayer": 1,
    "slot": "weapon", "req": {"attack": 70}})
add_item("godsword shard", 100000, members=True)
add_item("godsword blade", 350000, members=True)
for _h in ("bandos hilt", "armadyl hilt", "zamorak hilt", "saradomin hilt"):
    add_item(_h, 500000, members=True)

_GS_EQUIP = {"aslash": 95, "acrush": 80, "str": 110, "slot": "weapon",
             "req": {"attack": 75}}
for _gs in ("bandos godsword", "armadyl godsword", "zamorak godsword",
            "saradomin godsword"):
    add_item(_gs, 3000000, members=True, equip=dict(_GS_EQUIP))


def _bgs_after(p, m):
    m["defence"] = max(1, m["defence"] - 15)
    print("  " + paint("The blow SHATTERS its defences!", "byellow"))


def _zgs_after(p, m):
    m["stunned"] = True
    print("  " + paint("Ice erupts — it is frozen solid and loses its "
                       "next turn!", "bcyan"))


def _sgs_after(p, m):
    heal = 15
    p.hp = min(p.max_hp, p.hp + heal)
    p.prayer_points = min(p.prayer_max(), p.prayer_points + 5)
    print("  " + paint(f"Holy light knits your wounds (+{heal} hp, "
                       "+5 prayer).", "bgreen"))


SPECIAL_ATTACKS.update({
    "bandos godsword": {"name": "Warstrike", "cost": 50, "hits": 1,
                        "acc": 1.2, "dmg": 1.21, "after": _bgs_after,
                        "desc": "a colossal blow that shatters the enemy's "
                                "defences"},
    "armadyl godsword": {"name": "Judgement", "cost": 50, "hits": 1,
                         "acc": 1.2, "dmg": 1.375,
                         "desc": "the heaviest single strike in the game"},
    "zamorak godsword": {"name": "Ice Cleave", "cost": 50, "hits": 1,
                         "acc": 1.1, "dmg": 1.1, "after": _zgs_after,
                         "desc": "freezes the enemy solid — it loses its "
                                 "next turn"},
    "saradomin godsword": {"name": "Healing Blade", "cost": 50, "hits": 1,
                           "acc": 1.1, "dmg": 1.1, "after": _sgs_after,
                           "desc": "restores your health and prayer as it "
                                   "strikes"},
})


def _smith_godsword(p, arg):
    """'smith godsword' (3 shards -> blade), 'smith <god> godsword'."""
    a = arg.strip().lower()
    god = next((g for g in ("bandos", "armadyl", "zamorak", "saradomin")
                if a.startswith(g)), None)
    if god:
        if not p.has("godsword blade"):
            say("You need a godsword blade (smith 3 godsword shards).",
                "byellow")
            return
        hilt = f"{god} hilt"
        if not p.has(hilt):
            say(f"You need a {hilt} — {god}'s general guards it.", "byellow")
            return
        p.take("godsword blade")
        p.take(hilt)
        sword = f"{god} godsword"
        p.add(sword)
        banner(sword.upper(), color="gold", line_color="gold")
        say(f"The hilt seats with a sound like a struck bell. The "
            f"{sword.upper()} is whole again.", "gold", "bold")
        p.gain_xp("smithing", 200)
        return
    if p.lvl("smithing") < 80:
        say("You need smithing level 80 to reforge a godsword blade.",
            "byellow")
        return
    if not p.has("godsword shard", 3):
        say(f"You need 3 godsword shards ({p.count('godsword shard')} held) "
            "— the generals drop them.", "byellow")
        return
    p.take("godsword shard", 3)
    p.add("godsword blade")
    say("You hammer the three shards into a single terrible GODSWORD BLADE. "
        "Now for a hilt... ('smith <god> godsword')", "gold", "bold")
    p.gain_xp("smithing", 400)


# items whose powers aren't visible in raw stats — shown by 'examine'
EFFECT_NOTES = {
    "ring of recoil": "when a monster hits you, it takes 1 damage back "
                      "(can't land the killing blow)",
    "ring of life": "at a tenth of your health it crumbles and teleports "
                    "you to Lumbridge, alive",
    "ring of forging": "iron bars never fail to smelt while worn",
    "ring of wealth": "+25% coins from monster drops",
    "slayer helmet": "+15% accuracy and damage against your slayer task",
    "anti-dragon shield": "soaks dragonfire — breath damage cut to a third",
    "fire cape": "proof you conquered the Fight Caves; the best cape there is",
    "spade": "digs into burial mounds and suspicious molehills",
}
_BARROWS_SET_NOTES = {
    "dharok": "SET (weapon+body): your max hit climbs as YOUR hp falls — "
              "up to double at death's door",
    "ahrim": "SET (weapon+body): magic hits may sap the monster's strength",
    "karil": "SET (weapon+body): ranged hits may corrode the monster's "
             "defence",
    "guthan": "SET (weapon+body): a quarter of your hits siphon life, "
              "healing you",
    "torag": "SET (weapon+body): hits may leave the monster reeling, "
             "losing its turn",
    "verac": "SET (weapon+body): a quarter of your misses strike true "
             "anyway",
}
for _piece in BARROWS_GEAR:
    EFFECT_NOTES[_piece] = _BARROWS_SET_NOTES[_piece.split("'")[0]]


def _barrows_set(p):
    """The brother whose weapon AND body you wear (else None)."""
    w = p.equipment.get("weapon") or ""
    b = p.equipment.get("body") or ""
    for bro in ("dharok", "ahrim", "karil", "guthan", "torag", "verac"):
        if w.startswith(bro) and b.startswith(bro):
            return bro
    return None


def _barrows_set_proc(p, m, bro, kind, dmg):
    """On-hit set effects (dharok & verac are handled in the hit roll)."""
    if bro == "guthan" and random.random() < 0.25 and p.hp < p.max_hp:
        heal = max(1, dmg // 2)
        p.hp = min(p.max_hp, p.hp + heal)
        print("  " + paint(f"Guthan's spear siphons life (+{heal} hp).",
                           "lime"))
    elif bro == "ahrim" and kind == "magic" and random.random() < 0.25:
        m["attack"] = max(1, m["attack"] - 5)
        print("  " + paint("Ahrim's blight saps its strength!", "bblue"))
    elif bro == "karil" and kind == "ranged" and random.random() < 0.25:
        m["defence"] = max(1, m["defence"] - 5)
        print("  " + paint("Karil's taint corrodes its defence!", "bblue"))
    elif bro == "torag" and random.random() < 0.15:
        m["stunned"] = True
        print("  " + paint("Torag's hammers leave it reeling!", "teal"))


def _cave_on_kill(p, target):
    """Advance the Fight Caves after each wave kill; crown the champion."""
    wave = getattr(p, "cave_wave", 0)
    if not wave or p.location != "fight_caves" \
            or target != CAVE_WAVES[wave - 1]:
        return
    if wave < len(CAVE_WAVES):
        p.cave_wave += 1
        nxt = CAVE_WAVES[p.cave_wave - 1]
        say(f"Wave {wave} cleared! Catch your breath, eat up — then 'next' "
            f"(wave {p.cave_wave}/{len(CAVE_WAVES)}: {nxt}).",
            "byellow", "bold")
    else:
        p.cave_wave = 0
        show_art(ART_QUEST, "gold", center=True)
        banner("THE FIGHT CAVES — CONQUERED", color="orange", line_color="red")
        p.add("fire cape")
        say("TzHaar-Mej-Jal: \"You defeated TzTok-Jad?! Unbelievable, JalYt! "
            "Take this — you have earned it.\"", "orange", "bold")
        say("You receive a FIRE CAPE! ('equip fire cape')", "bgreen", "bold")


# ===========================================================================
#  THE KHARIDIAN DESERT  (heat, thieves, the Duel Arena, and the Queen)
# ===========================================================================
# South through the Shantay Pass the sun becomes a monster: carry waterskins
# or burn. Pollnivneach fences stolen goods, Nardah's fountain restores the
# faithful, gamblers stake coins at the Duel Arena — and beneath the sands,
# the Kalphite Queen waits in two bodies.

add_item("waterskin", 10)
add_item("kebab", 12, heal=6)

SHOPS["shantay"] = {"waterskin": 10, "knife": 6, "bread": 12}
SHOPS["kebab"] = {"kebab": 12, "waterskin": 12}

PICKPOCKET["menaphite thug"] = (65, 137, 140, 5)

_add_mob("desert bandit",
    {"abonus": 10, "atktype": ["slash"], "att": 40, "cb": 41, "dstab": 15,
     "dslash": 15, "dcrush": 15, "dmagic": 10, "drange": 15, "def": 30,
     "hp": 40, "maxhit": 6, "str": 40, "weak": "crush"},
    [("coins", 20, 180, 0.9), ("waterskin", 1, 2, 0.3)],
    members=True, rank="medium")

_add_mob("kalphite worker",
    {"abonus": 5, "atktype": ["crush"], "att": 25, "cb": 28, "dstab": 20,
     "dslash": 20, "dcrush": 10, "dmagic": 15, "drange": 20, "def": 22,
     "hp": 32, "maxhit": 4, "str": 25, "weak": "crush"},
    [("coins", 10, 80, 0.7), ("waterskin", 1, 1, 0.1)],
    members=True, rank="medium")

_add_mob("kalphite soldier",
    {"abonus": 20, "atktype": ["crush"], "att": 75, "cb": 85, "dstab": 45,
     "dslash": 45, "dcrush": 25, "dmagic": 35, "drange": 45, "def": 60,
     "hp": 90, "maxhit": 12, "str": 80, "weak": "crush"},
    [("coins", 80, 400, 0.9), ("mithril bar", 1, 1, 0.1)],
    members=True, rank="elite")

# --- the Queen: two bodies, one grudge ------------------------------------------
KQ_ART = r"""
       \_          _/
        \ \__    __/ /
     ____\/##\==/##\/____
    <=((  \(@)==(@)/  ))=>
        \_/|/    \|\_/
      _/  /|      |\  \_
     <__ / |______| \ __>
"""


def _kq_intro(name):
    return [_tint(KQ_ART, "brown"), _tint(KQ_ART, "byellow", "bold"),
            _tint(KQ_ART, "orange", "bold")]


def _kq_death(name):
    return [_tint(KQ_ART, "orange"), _tint(KQ_ART, "grey", "dim")]


KQ_ATTACKS = [
    {"label": "her scything mandibles", "verb": "snaps with",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(KQ_ART, "byellow", "bold")],
     "mult": 1.2, "w": 3, "atype": "crush"},
    {"label": "a hail of hardened chitin", "verb": "flings",
     "color": ("brown",),
     "builder": lambda: [_tint(KQ_ART, "brown")],
     "mult": 1.0, "w": 2, "atype": "ranged"},
    {"label": "a crackling bolt of hive-magic", "verb": "spits",
     "color": ("bmagenta", "bold"),
     "builder": lambda: [_tint(KQ_ART, "bmagenta", "bold")],
     "mult": 1.1, "w": 2, "atype": "magic"},
]

_add_mob("kalphite queen",
    {"abonus": 35, "atktype": ["crush", "ranged", "magic"], "att": 150,
     "cb": 333, "dstab": 70, "dslash": 70, "dcrush": 50, "dmagic": 60,
     "drange": 70, "def": 85, "hp": 255, "maxhit": 22, "str": 150,
     "weak": "crush"},
    [("big bones", 1, 1, 1.0), ("coins", 3000, 12000, 1.0),
     ("dragon chainbody", 1, 1, 0.04), ("uncut diamond", 1, 2, 0.15),
     ("grimy ranarr", 1, 3, 0.3), ("waterskin", 2, 4, 0.5)], members=True)
MONSTERS["kalphite queen"]["boss"] = True
MONSTERS["kalphite queen"]["rank"] = "boss"
MONSTERS["kalphite queen"]["carapace"] = True
MONSTERS["kalphite queen"]["transform"] = True
_BOSSES.add("kalphite queen")
BOSS_INTRO["kalphite queen"] = _kq_intro
BOSS_DEATH["kalphite queen"] = _kq_death
BOSS_TURN["kalphite queen"] = lambda p, m: _boss_take_turn(p, m, KQ_ATTACKS)
MONSTER_ART["kalphite queen"] = KQ_ART

# --- the region -------------------------------------------------------------------
ROOMS.update({
    "shantay_pass": dict(name="Shantay Pass",
        desc="The gate to the Kharidian Desert. Shantay eyes your pack: "
             "'Waterskins, friend. The sun out there is a murderer.'",
        exits={"north": "al_kharid_square", "south": "desert_road"},
        shop="shantay", desert=True, members=True),
    "desert_road": dict(name="Kharidian Dunes",
        desc="An ocean of sand rolling south. Bandits shadow the caravan "
             "routes, and something vast has tunnelled under the western "
             "dunes ('hive').",
        exits={"north": "shantay_pass", "south": "pollnivneach",
               "hive": "kalphite_hive"},
        monsters=["desert bandit", "scorpion"], hostile=True, desert=True,
        members=True),
    "pollnivneach": dict(name="Pollnivneach",
        desc="A lawless town of thieves and kebab smoke, halfway to "
             "nowhere. Menaphite thugs swagger between the tents — light "
             "fingers could live well here.",
        exits={"north": "desert_road", "south": "nardah"},
        pickpocket=["menaphite thug", "man"], shop="kebab", desert=True,
        members=True),
    "nardah": dict(name="Nardah",
        desc="A shrine town at the desert's edge, built around a holy "
             "fountain said to wash away any weariness ('pray altar').",
        exits={"north": "pollnivneach"},
        bank=True, prayer_altar=True, desert=True, members=True),
    "kalphite_hive": dict(name="Kalphite Hive",
        desc="A honeycomb of waxy tunnels breathing hot, sweet air. "
             "Workers boil out of the dark, and a deeper shaft descends "
             "('down').",
        exits={"out": "desert_road", "down": "kq_lair"},
        monsters=["kalphite worker", "kalphite soldier"], hostile=True,
        desert=True, members=True),
    "kq_lair": dict(name="The Queen's Chamber",
        desc="The heart of the hive. THE KALPHITE QUEEN towers over her "
             "eggs, carapace glinting like wet amber.",
        exits={"up": "kalphite_hive"},
        monsters=["kalphite queen"], desert=True, members=True),
    "duel_arena": dict(name="Duel Arena",
        desc="A colosseum of hot sandstone east of Al Kharid. The "
             "Duelmaster takes stakes and the crowd takes sides. "
             "('duel <coins>' to fight under the rules of the house)",
        exits={"west": "al_kharid_square"},
        npc="duelmaster", desert=True, members=True),
})
ROOMS["al_kharid_square"]["exits"]["south"] = "shantay_pass"
ROOMS["al_kharid_square"]["exits"]["arena"] = "duel_arena"
ROOMS["al_kharid_square"]["desc"] += (" The Shantay Pass opens south, and "
                                      "the Duel Arena roars east ('arena').")
for _rm in ("shantay_pass", "desert_road", "pollnivneach", "nardah",
            "kalphite_hive", "kq_lair", "duel_arena"):
    REGIONS[_rm] = "AlKharid"
TRAVEL_HUBS["pollnivneach"] = "pollnivneach"
TRAVEL_NAMES.append("Pollnivneach")

# the Nardah fountain washes away everything
def _nardah_blessing(p):
    p.hp = p.max_hp
    p.poison = 0
    p.stat_drain = {}


# --- the Duel Arena -----------------------------------------------------------------
_add_mob("arena duelist",
    {"abonus": 15, "atktype": ["slash"], "att": 60, "cb": 70, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 25, "drange": 30, "def": 50,
     "hp": 70, "maxhit": 9, "str": 60, "weak": "crush"},
    [], members=True, rank="hard")

DUEL_RULES = ["no food", "no prayer", "no specials", "anything goes"]


def talk_duelmaster(p):
    say("Duelmaster: \"Stake your coins and fight my champions \u2014 "
        "matched to your measure, under the rules of the house. Win and "
        "I pay DOUBLE. 'duel <coins>' (minimum 100). Lose \u2014 or "
        "yield \u2014 and the stake is mine.\"", "gold")


QUEST_TALK["duelmaster"] = talk_duelmaster
NPC_NAMES["duelmaster"] = "the Duelmaster"


def cmd_duel(p, arg):
    if not getattr(p, "members", False):
        say("The Duel Arena is members-only. Type 'membership'.", "bmagenta")
        return
    if p.location != "duel_arena":
        say("The Duel Arena is east of Al Kharid.", "grey")
        return
    if getattr(p, "combat", None) is not None:
        say("You're already fighting!", "bred")
        return
    try:
        stake = int(arg.strip().split()[0])
    except (ValueError, IndexError):
        say("Stake how much? 'duel 500' (minimum 100 coins).", "bcyan")
        return
    if stake < 100:
        say("The Duelmaster sneers: \"Minimum stake is 100 coins.\"",
            "grey")
        return
    if not p.has("coins", stake):
        say(f"You don't have {stake:,} coins to stake.", "byellow")
        return
    p.take("coins", stake)
    rule = random.choice(DUEL_RULES)
    p.duel = {"stake": stake, "rule": rule}
    banner("DUEL!", color="gold", line_color="gold")
    say(f"Stake: {stake:,} coins.  House rule: {rule.upper()}.",
        "gold", "bold")
    _start_combat(p, "arena duelist")
    # the house matches champions to your measure
    m = p.combat
    cb = p.combat_level()
    m["attack"] = max(20, int(cb * 0.9))
    m["defence"] = max(15, int(cb * 0.7))
    m["max_hit"] = max(4, cb // 9)
    m["hp"] = m["cur"] = max(40, p.max_hp - 10)
    m["level"] = cb


def _duel_loss(p):
    duel = getattr(p, "duel", None)
    p.duel = None
    p.combat = None
    _clear_status(p)
    p.hp = max(p.hp, 1)
    stake = duel["stake"] if duel else 0
    say(f"The Duelmaster collects your stake of {stake:,} coins. The "
        "medics drag you out \u2014 beaten, breathing, and poorer.",
        "byellow")
    p.location = "duel_arena"
    return True


HANDLERS["duel"] = cmd_duel


# ===========================================================================
#  THE SLAYER TOWER & SLAYER OVERHAUL
# ===========================================================================
# Three floors of horrors over Canifis, each gated by slayer level, several
# demanding the right counter-gear. Masters now come in tiers: Turael
# (Taverley, gentle), Vannaka (Edgeville, standard), Duradel (Brimhaven,
# brutal). Task streaks pay bonus points at every 5th and 10th task.

# --- counter-gear -------------------------------------------------------------
add_item("earmuffs", 200, members=True, equip={
    "dstab": 1, "dslash": 1, "dcrush": 1, "slot": "head"})
add_item("mirror shield", 5000, members=True, equip={
    "dstab": 20, "dslash": 22, "dcrush": 20, "dmagic": 25, "drange": 22,
    "slot": "shield", "req": {"defence": 20}})
add_item("rock hammer", 500, members=True, tool="rock hammer")

SLAYER_REWARDS.update({
    "earmuffs": (5, "blocks a banshee's mind-splitting scream"),
    "mirror shield": (15, "turns a basilisk's gaze back on itself"),
    "rock hammer": (10, "shatters a dying gargoyle before it reforms"),
})


def _has_slayer_helm(p):
    return p.equipment.get("head") == "slayer helmet"


def _banshee_scream(p, m, dmg):
    if _has_slayer_helm(p) or p.equipment.get("head") == "earmuffs":
        return
    for s in ("attack", "strength"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 2
    print("  " + paint("The banshee's SCREAM splits your mind! (-2 attack & "
                       "strength \u2014 earmuffs would block it)", "bblue"))


def _basilisk_gaze(p, m, dmg):
    if p.equipment.get("shield") == "mirror shield":
        return
    for s in ("attack", "defence"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 3
    print("  " + paint("You meet the basilisk's gaze! (-3 attack & defence "
                       "\u2014 a mirror shield would protect you)", "bblue"))


def _spectre_stench(p, m, dmg):
    if _has_slayer_helm(p):
        return
    for s in ("attack", "strength", "defence"):
        p.stat_drain[s] = p.stat_drain.get(s, 0) + 3
    print("  " + paint("The spectre's stench sears your lungs! (-3 combat "
                       "stats \u2014 a slayer helmet would seal it out)",
                       "bblue"))


MONSTER_EFFECTS["banshee"] = _banshee_scream
MONSTER_EFFECTS["basilisk"] = _basilisk_gaze
MONSTER_EFFECTS["aberrant spectre"] = _spectre_stench

# --- the tower's residents -----------------------------------------------------
_add_mob("crawling hand",
    {"abonus": 0, "atktype": ["crush"], "att": 8, "cb": 8, "dstab": 0,
     "dslash": 0, "dcrush": 0, "dmagic": 0, "drange": 0, "def": 6,
     "hp": 16, "maxhit": 2, "str": 8, "weak": "crush"},
    [("coins", 2, 30, 0.7), ("leather gloves", 1, 1, 0.15)],
    members=True, rank="easy")
MONSTERS["crawling hand"]["slayer_req"] = 5

_add_mob("banshee",
    {"abonus": 10, "atktype": ["magic"], "att": 20, "cb": 23, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 10, "drange": 5, "def": 15,
     "hp": 22, "maxhit": 3, "str": 15, "weak": "crush"},
    [("coins", 10, 60, 0.7), ("grimy guam", 1, 2, 0.2),
     ("grimy marrentill", 1, 1, 0.12)], members=True, rank="medium")
MONSTERS["banshee"]["slayer_req"] = 15

_add_mob("basilisk",
    {"abonus": 15, "atktype": ["slash"], "att": 55, "cb": 61, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 15, "drange": 25, "def": 45,
     "hp": 75, "maxhit": 9, "str": 55, "weak": "crush"},
    [("coins", 40, 200, 0.8), ("grimy ranarr", 1, 1, 0.05),
     ("uncut sapphire", 1, 1, 0.06), ("mithril bar", 1, 1, 0.1)],
    members=True, rank="hard")
MONSTERS["basilisk"]["slayer_req"] = 40

_add_mob("aberrant spectre",
    {"abonus": 25, "atktype": ["magic"], "att": 70, "cb": 96, "dstab": 30,
     "dslash": 30, "dcrush": 30, "dmagic": 35, "drange": 30, "def": 55,
     "hp": 90, "maxhit": 11, "str": 70, "weak": "ranged"},
    [("coins", 50, 250, 0.7), ("grimy ranarr", 1, 2, 0.18),
     ("grimy tarromin", 1, 2, 0.15), ("grimy guam", 1, 3, 0.2),
     ("ranarr seed", 1, 1, 0.04)], members=True, rank="elite")
MONSTERS["aberrant spectre"]["slayer_req"] = 60

_add_mob("gargoyle",
    {"abonus": 20, "atktype": ["crush"], "att": 90, "cb": 111, "dstab": 55,
     "dslash": 55, "dcrush": 40, "dmagic": 40, "drange": 55, "def": 70,
     "hp": 105, "maxhit": 11, "str": 90, "weak": "crush"},
    [("coins", 400, 1500, 0.9), ("adamant bar", 1, 2, 0.2),
     ("gold ore", 2, 5, 0.2), ("rune full helm", 1, 1, 0.03),
     ("granite maul", 1, 1, 0.01)], members=True, rank="elite")
MONSTERS["gargoyle"]["slayer_req"] = 75
MONSTERS["gargoyle"]["finisher"] = "rock hammer"

_add_mob("abyssal demon",
    {"abonus": 45, "atktype": ["slash"], "att": 95, "cb": 124, "dstab": 45,
     "dslash": 45, "dcrush": 45, "dmagic": 45, "drange": 45, "def": 75,
     "hp": 150, "maxhit": 8, "str": 85, "weak": "slash"},
    [("coins", 200, 1200, 0.9), ("abyssal whip", 1, 1, 0.02),
     ("grimy ranarr", 1, 1, 0.08), ("chaos rune", 5, 20, 0.3)],
    members=True, rank="elite")
MONSTERS["abyssal demon"]["slayer_req"] = 85

# --- the tower ------------------------------------------------------------------
ROOMS.update({
    "slayer_tower_1": dict(name="Slayer Tower \u2014 Ground Floor",
        desc="A crumbling gothic tower over Canifis. Severed hands drag "
             "themselves across the flagstones, and something upstairs is "
             "screaming.",
        exits={"out": "canifis", "up": "slayer_tower_2"},
        monsters=["crawling hand", "banshee"], hostile=True, members=True),
    "slayer_tower_2": dict(name="Slayer Tower \u2014 First Floor",
        desc="Scaled things slither between the pillars, and the fleshy "
             "walls pulse. Don't meet anything's eye.",
        exits={"down": "slayer_tower_1", "up": "slayer_tower_3"},
        monsters=["basilisk", "bloodveld"], hostile=True, members=True),
    "slayer_tower_3": dict(name="Slayer Tower \u2014 Top Floor",
        desc="Stone sentinels perch in the rafters over a floor scarred "
             "with teleport burns. The air smells of sulphur and rot.",
        exits={"down": "slayer_tower_2"},
        monsters=["aberrant spectre", "gargoyle", "abyssal demon"],
        hostile=True, members=True),
})
ROOMS["canifis"]["exits"]["tower"] = "slayer_tower_1"
ROOMS["canifis"]["desc"] += (" The Slayer Tower looms over the town "
                             "('tower').")
REGIONS.update({"slayer_tower_1": "Morytania", "slayer_tower_2": "Morytania",
                "slayer_tower_3": "Morytania"})

# --- masters in tiers --------------------------------------------------------------
TURAEL_TARGETS = ["chicken", "cow", "goblin", "giant rat", "scorpion",
                  "giant spider", "imp", "skeleton", "zombie"]
DURADEL_TARGETS = ["bloodveld", "basilisk", "aberrant spectre", "gargoyle",
                   "abyssal demon", "green dragon", "werewolf", "ice giant",
                   "greater demon", "hill giant"]


def _assign_task(p, master, targets, lo, hi):
    task = p.slayer_task
    if task and task["remaining"] > 0:
        say(f"{master}: \"You're still on the hunt \u2014 "
            f"{task['remaining']} of {task['amount']} "
            f"{task['monster']}s to go.\"", "teal")
        return
    pool = [t for t in targets if t in MONSTERS
            and p.lvl("slayer") >= MONSTERS[t].get("slayer_req", 0)]
    if not pool:
        pool = [t for t in targets if t in MONSTERS][:1]
    mon = random.choice(pool)
    amt = random.randint(lo, hi)
    p.slayer_task = {"monster": mon, "amount": amt, "remaining": amt}
    banner("Slayer Assignment", color="teal", line_color="teal")
    say(f"{master}: \"Your task: slay {amt} {mon}s.\"", "teal")
    locs = sorted({ROOMS[k]["name"] for k, r in ROOMS.items()
                   if mon in r.get("monsters", [])})
    if locs:
        say("  Find them at: " + ", ".join(locs[:4]), "grey")
    say("  (Check progress with 'task'; spend points with 'slayerbuy'.)",
        "grey")


def talk_turael(p):
    if not getattr(p, "members", False):
        say("Turael: \"Slayer is a members art, friend.\"", "bmagenta")
        return
    _assign_task(p, "Turael", TURAEL_TARGETS, 8, 15)


def talk_duradel(p):
    if not getattr(p, "members", False):
        say("Duradel: \"Members only, and I don't repeat myself.\"",
            "bmagenta")
        return
    if p.combat_level() < 100 or p.lvl("slayer") < 50:
        say("Duradel: \"Come back at combat 100 and slayer 50. I don't "
            "waste my lists on the soft.\"", "byellow")
        return
    _assign_task(p, "Duradel", DURADEL_TARGETS, 15, 35)


QUEST_TALK["turael"] = talk_turael
QUEST_TALK["duradel"] = talk_duradel
NPC_NAMES["turael"] = "Turael"
NPC_NAMES["duradel"] = "Duradel"
ROOMS["taverley"]["npc"] = "turael"
ROOMS["taverley"]["desc"] += " Turael, the gentlest of slayer masters, trims his hedge."
ROOMS["brimhaven"]["npc"] = "duradel"
ROOMS["brimhaven"]["desc"] += " Duradel watches the docks, arms crossed."

EFFECT_NOTES.update({
    "earmuffs": "blocks a banshee's scream (a slayer helmet also works)",
    "mirror shield": "reflects a basilisk's gaze",
    "rock hammer": "shatters dying gargoyles before their stone reforms",
})
EFFECT_NOTES["slayer helmet"] = ("+15% accuracy and damage against your "
                                 "slayer task; blocks banshee screams and "
                                 "spectre stench")


# ===========================================================================
#  THE WORLD PUSHES BACK  (ambushes, training focus, nests, ambience)
# ===========================================================================

# --- melee training focus ----------------------------------------------------
def cmd_train(p, arg):
    """Aim your melee xp: attack (accurate), strength (aggressive),
    defence (defensive), or shared."""
    want = arg.strip().lower()
    names = {"attack": "attack", "accurate": "attack",
             "strength": "strength", "aggressive": "strength",
             "str": "strength",
             "defence": "defence", "defensive": "defence", "def": "defence",
             "shared": "shared", "controlled": "shared", "all": "shared"}
    if not want:
        cur = getattr(p, "train", "shared")
        say(f"Melee training focus: {cur}. "
            "('train attack|strength|defence|shared' \u2014 ranged and magic "
            "train themselves)", "bcyan")
        return
    focus = names.get(want)
    if not focus:
        say("Train what? attack (accurate), strength (aggressive), "
            "defence (defensive), or shared.", "grey")
        return
    p.train = focus
    if focus == "shared":
        say("You balance your technique \u2014 melee xp is shared across "
            "attack, strength and defence.", "bcyan")
    else:
        say(f"You focus your technique \u2014 melee kills now train {focus}.",
            "bcyan")


HANDLERS["train"] = cmd_train
HANDLERS["focus"] = cmd_train

# --- bird's nests (woodcutting's little jackpot) --------------------------------
_NEST_LOOT = [("potato seed", 18), ("onion seed", 14), ("cabbage seed", 12),
              ("guam seed", 12), ("marrentill seed", 8), ("tarromin seed", 6),
              ("sweetcorn seed", 5), ("gold ring", 10), ("sapphire ring", 6),
              ("emerald ring", 4), ("ranarr seed", 3), ("watermelon seed", 2)]


def _birds_nest(p):
    prize = random.choices([i for i, _ in _NEST_LOOT],
                           weights=[w for _, w in _NEST_LOOT])[0]
    p.add(prize)
    print("  " + paint(f"\u2726 A bird's nest tumbles from the branches "
                       f"\u2014 inside: {prize}!", "gold", "bold"))


# --- hostile territory: some places attack YOU ----------------------------------
for _rm in ("wilderness_edge", "deep_wilderness", "chaos_temple",
            "wilderness_course", "varrock_sewers", "edgeville_dungeon",
            "stronghold_security", "members_dungeon", "taverley_dungeon",
            "melzars_maze", "icy_cavern", "draynor_manor",
            "black_knights_fortress", "mort_myre", "crandor",
            "karamja_volcano", "gwd_entrance", "bandos_stronghold",
            "armadyl_eyrie", "zamorak_fortress", "saradomin_encampment"):
    if _rm in ROOMS:
        ROOMS[_rm]["hostile"] = True


def _maybe_ambush(p):
    """Entering hostile ground can start a fight on THEIR terms. Strong
    adventurers get left alone (double a monster's level and it ignores
    you), and bosses never lurk."""
    r = ROOMS[p.location]
    if not r.get("hostile") or getattr(p, "combat", None) is not None:
        return
    if getattr(p, "auto", None) is not None:
        return
    cb = p.combat_level()
    lurkers = [m for m in r.get("monsters", [])
               if not MONSTERS[m].get("boss")
               and (MONSTERS[m].get("level") or 1) * 2 >= cb
               and p.lvl("slayer") >= MONSTERS[m].get("slayer_req", 0)]
    if not lurkers or random.random() > 0.30:
        return
    m = random.choice(lurkers)
    say(f"\u26a0 Ambush! A {m} lunges at you from the shadows!",
        "bred", "bold")
    _start_combat(p, m)


# --- ambient flavour on the road --------------------------------------------------
REGION_AMBIENT = {
    "Wilderness": [
        "A cold wind drags ash across the wastes.",
        "Somewhere out in the grey, something howls.",
        "Old bones crunch underfoot.",
    ],
    "Morytania": [
        "The mist thickens, and the light gives up early here.",
        "Something watches from between the trees. It does not blink.",
        "A church bell tolls, far off and wrong.",
    ],
    "Karamja": [
        "Parrots shriek somewhere in the green.",
        "The volcano grumbles in its sleep.",
        "The air is thick enough to drink.",
    ],
    "AlKharid": [
        "Heat shimmers off the dunes.",
        "Sand hisses across the road.",
    ],
    "Kandarin": [
        "Bees drone through the long grass.",
        "A cart rattles by on the King's road.",
    ],
}


REGIONS.update({
    "giant_lair": "Edgeville", "mining_guild": "Falador",
    "crafting_guild": "Falador", "monastery": "Edgeville",
    "deep_wilderness": "Wilderness", "taverley": "Kandarin",
    "taverley_dungeon": "Kandarin", "white_wolf_mountain": "Kandarin",
    "catherby": "Kandarin", "seers_village": "Kandarin",
    "ardougne": "Kandarin", "brimhaven": "Karamja",
    "karamja_volcano": "Karamja", "crandor": "Crandor",
    "elvarg_lair": "Crandor",
})


def _ambient(p):
    lines = REGION_AMBIENT.get(REGIONS.get(p.location, ""))
    if lines and random.random() < 0.22:
        say(random.choice(lines), "grey")


# ===========================================================================
#  THE FREMENNIK PROVINCE  (the Trials, rock crabs, and the three Kings)
# ===========================================================================
# Rellekka lies north of Seers' Village. The Fremennik Trials earn you a
# Fremennik name and the sail to Waterbirth Island, where the Dagannoth
# Kings circle beneath the rock — a tribrid trio: magic fells Rex, arrows
# fell Prime, steel fells Supreme. Their rings have no equal.

# --- items -----------------------------------------------------------------
add_item("lyre", 40, members=True)
add_item("yak-hide", 60, members=True)
add_item("dagannoth bones", 110, bury=("prayer", 62), members=True)
add_item("helm of neitiznot", 55000, members=True,
         equip={"slot": "head", "dstab": 31, "dslash": 29, "dcrush": 34,
                "dmagic": 3, "drange": 30, "str": 3, "prayer": 3,
                "quest": "fremennik_trials"})
add_item("berserker ring", 45000, members=True,
         equip={"slot": "ring", "str": 4, "dstab": 4, "dslash": 4,
                "dcrush": 4})
add_item("warrior ring", 30000, members=True,
         equip={"slot": "ring", "aslash": 4, "dslash": 4})
add_item("archers ring", 42000, members=True,
         equip={"slot": "ring", "arange": 4, "drange": 4})
add_item("seers ring", 38000, members=True,
         equip={"slot": "ring", "amagic": 6, "dmagic": 6})
add_item("dragon axe", 61000, members=True, tool="axe", tier=7,
         equip={"slot": "weapon", "aslash": 38, "acrush": 32, "str": 42,
                "req": {"woodcutting": 61}})
EFFECT_NOTES["dragon axe"] = ("the finest axe in Gielinor — its edge counts "
                              "as +3 woodcutting levels while you chop")
EFFECT_NOTES["helm of neitiznot"] = ("the Jarl's gift: a berserker helm "
                                     "without the drawbacks, blessed for "
                                     "prayer")
SHOPS["neitiznot"] = {"helm of neitiznot": 55000, "harpoon": 5,
                      "lobster pot": 20}

# --- creatures ---------------------------------------------------------------
_add_mob("rock crab",
    {"abonus": 0, "atktype": ["crush"], "att": 5, "cb": 13, "dstab": 8,
     "dslash": 8, "dcrush": 8, "dmagic": 0, "drange": 8, "def": 5,
     "hp": 50, "maxhit": 1, "str": 10, "weak": "crush"},
    [("coins", 1, 12, 0.3), ("raw tuna", 1, 1, 0.1)],
    members=True, rank="easy")
_add_mob("yak",
    {"abonus": 0, "atktype": ["crush"], "att": 10, "cb": 22, "dstab": 5,
     "dslash": 5, "dcrush": 5, "dmagic": 0, "drange": 5, "def": 10,
     "hp": 50, "maxhit": 2, "str": 15, "weak": "stab"},
    [("yak-hide", 1, 1, 1.0), ("bones", 1, 1, 1.0)],
    members=True, rank="easy")
_add_mob("dagannoth",
    {"abonus": 30, "atktype": ["ranged"], "att": 80, "cb": 90, "dstab": 60,
     "dslash": 60, "dcrush": 60, "dmagic": 30, "drange": 60, "def": 70,
     "hp": 70, "maxhit": 9, "str": 80, "weak": "magic"},
    [("bones", 1, 1, 1.0), ("coins", 40, 220, 0.8),
     ("blood rune", 2, 6, 0.15), ("grimy ranarr", 1, 1, 0.05),
     ("steel arrow", 5, 20, 0.3)],
    members=True, rank="elite")
_add_mob("the draugen",
    {"abonus": 20, "atktype": ["magic"], "att": 60, "cb": 69, "dstab": 30,
     "dslash": 30, "dcrush": 20, "dmagic": 40, "drange": 30, "def": 50,
     "hp": 60, "maxhit": 7, "str": 60, "weak": "crush"},
    [("coins", 200, 500, 1.0)], members=True, rank="hard")
DURADEL_TARGETS.append("dagannoth")

# --- wave spells (magic's missing top end — Rex demands a real spellbook) ----
add_item("blood rune", 400, members=True)
SHOPS["rune"]["blood rune"] = 450
SPELLS.update({
    "wind wave":  {"type": "combat", "max": 17, "lvl": 62, "xp": 36,
                   "runes": {"air rune": 5, "blood rune": 1}},
    "water wave": {"type": "combat", "max": 18, "lvl": 65, "xp": 37.5,
                   "runes": {"water rune": 7, "air rune": 5, "blood rune": 1}},
    "earth wave": {"type": "combat", "max": 19, "lvl": 70, "xp": 40,
                   "runes": {"earth rune": 7, "air rune": 5, "blood rune": 1}},
    "fire wave":  {"type": "combat", "max": 20, "lvl": 75, "xp": 42.5,
                   "runes": {"fire rune": 7, "air rune": 5, "blood rune": 1}},
})

# --- the three Kings ----------------------------------------------------------
DK_ART = r"""
              ,--.___
         __.-'   \o  `\__
     _.-'    /\   \      `--.
   ,'   /\  /  \   \  /\     `.
  /    /  \/    \   \/  \      \
  ~^~^~/    ~^~^~\   ~^~^\~^~^~^~
"""

_DK_TINT = {"dagannoth rex": "bred", "dagannoth prime": "bcyan",
            "dagannoth supreme": "bgreen"}


def _dk_intro(name):
    c = _DK_TINT.get(name, "bcyan")
    return [_tint(DK_ART, "grey"), _tint(DK_ART, c, "bold")]


def _dk_death(name):
    c = _DK_TINT.get(name, "bcyan")
    return [_tint(DK_ART, c), _tint(DK_ART, "grey", "dim")]


# while you fight one King, the other two circle the lair
_DK_SNIPE = {
    "dagannoth rex": ("melee",
        "REX barrels through the shallows, jaws snapping at your blind side"),
    "dagannoth prime": ("magic",
        "PRIME rears from the water and spits a crackling bolt at your back"),
    "dagannoth supreme": ("ranged",
        "SUPREME wheels past and rakes you with a volley of spikes"),
}


def _dk_take_turn(p, m, attacks):
    if random.random() < 0.22:
        name = random.choice([k for k in _DK_SNIPE if k != m["name"]])
        style, flavor = _DK_SNIPE[name]
        print("  " + paint(flavor + "!", "bcyan"))
        if p.prayer_protects(style):
            print("  " + paint("Your prayer turns the ambush aside.", "teal"))
        else:
            dmg = random.randint(2, 13)
            p.hp -= dmg
            print("  " + paint(f"It strikes from nowhere for {dmg}. "
                               f"(protect from {style}!)", "bred"))
            if p.hp <= 0:
                return "died"
    return _boss_take_turn(p, m, attacks)


REX_ATTACKS = [
    {"label": "jaws like a ship's ram", "verb": "lunges with",
     "color": ("bred", "bold"),
     "builder": lambda: [_tint(DK_ART, "bred", "bold")],
     "mult": 1.2, "w": 3, "atype": "stab"},
    {"label": "a tail-sweep that shakes the cavern", "verb": "spins into",
     "color": ("orange",),
     "builder": lambda: [_tint(DK_ART, "orange")],
     "mult": 1.0, "w": 2, "atype": "crush"},
]
PRIME_ATTACKS = [
    {"label": "a bolt of deep-water lightning", "verb": "spits",
     "color": ("bcyan", "bold"),
     "builder": lambda: [_tint(DK_ART, "bcyan", "bold")],
     "mult": 1.2, "w": 3, "atype": "magic"},
    {"label": "a scalding geyser", "verb": "summons",
     "color": ("bblue",),
     "builder": lambda: [_tint(DK_ART, "bblue")],
     "mult": 1.0, "w": 2, "atype": "magic"},
]
SUPREME_ATTACKS = [
    {"label": "a storm of barbed spikes", "verb": "launches",
     "color": ("bgreen", "bold"),
     "builder": lambda: [_tint(DK_ART, "bgreen", "bold")],
     "mult": 1.2, "w": 3, "atype": "ranged"},
    {"label": "a darting peck", "verb": "snaps out",
     "color": ("green",),
     "builder": lambda: [_tint(DK_ART, "green")],
     "mult": 0.8, "w": 1, "atype": "stab"},
]

_DK_KINGS = {
    "dagannoth rex": (
        {"abonus": 45, "atktype": ["stab"], "att": 180, "cb": 303,
         "dstab": 220, "dslash": 220, "dcrush": 220, "dmagic": 0,
         "drange": 220, "def": 90, "hp": 255, "maxhit": 26, "str": 180,
         "weak": "magic"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("berserker ring", 1, 1, 0.05), ("warrior ring", 1, 1, 0.05),
         ("dragon axe", 1, 1, 0.03), ("grimy ranarr", 1, 3, 0.25)],
        REX_ATTACKS),
    "dagannoth prime": (
        {"abonus": 45, "atktype": ["magic"], "att": 180, "cb": 303,
         "dstab": 220, "dslash": 220, "dcrush": 220, "dmagic": 220,
         "drange": 0, "def": 90, "hp": 255, "maxhit": 25, "str": 180,
         "weak": "ranged"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("seers ring", 1, 1, 0.05), ("dragon axe", 1, 1, 0.03),
         ("blood rune", 5, 20, 0.5), ("nature rune", 10, 40, 0.4)],
        PRIME_ATTACKS),
    "dagannoth supreme": (
        {"abonus": 45, "atktype": ["ranged"], "att": 180, "cb": 303,
         "dstab": 10, "dslash": 10, "dcrush": 10, "dmagic": 220,
         "drange": 220, "def": 90, "hp": 255, "maxhit": 24, "str": 180,
         "weak": "slash"},
        [("dagannoth bones", 1, 1, 1.0), ("coins", 1500, 8000, 1.0),
         ("archers ring", 1, 1, 0.05), ("dragon axe", 1, 1, 0.03),
         ("raw swordfish", 2, 5, 0.5)],
        SUPREME_ATTACKS),
}
for _k, (_st, _drops, _atk) in _DK_KINGS.items():
    _add_mob(_k, _st, _drops, members=True)
    MONSTERS[_k]["boss"] = True
    MONSTERS[_k]["rank"] = "boss"
    _BOSSES.add(_k)
    BOSS_TURN[_k] = (lambda atk: (lambda p, m: _dk_take_turn(p, m, atk)))(_atk)
    BOSS_INTRO[_k] = _dk_intro
    BOSS_DEATH[_k] = _dk_death
    MONSTER_ART[_k] = DK_ART

# --- the province --------------------------------------------------------------
ROOMS.update({
    "rellekka": dict(name="Rellekka",
        desc="A palisaded seafarers' town of longhalls, woodsmoke and "
             "gull-cry. Brundt the Chieftain holds court, Olaf the Bard "
             "hums over his strings, and longships rock at the dock "
             "('sail'). Rock crabs bask along the coast ('coast'), and the "
             "Jarl's isle of Neitiznot lies over the water ('isles').",
        exits={"south": "seers_village", "coast": "rock_crab_coast",
               "sail": "waterbirth_island", "isles": "neitiznot"},
        bank=True, npc=["fremennik_trials", "olaf"], members=True),
    "rock_crab_coast": dict(name="Rock Crab Coast",
        desc="A cold grey shore where boulders sprout legs if you step too "
             "close. Warriors come from across Gielinor to batter the "
             "crabs' shells — they hit like pebbles and last like rocks.",
        exits={"west": "rellekka"},
        monsters=["rock crab"], fish_tools=["cage", "harpoon"],
        members=True),
    "neitiznot": dict(name="Neitiznot",
        desc="A tidy isle of yak-paddocks and fresh-cut timber. The Jarl's "
             "armoury sells his famous helm — to those the Fremennik call "
             "kin.",
        exits={"sail": "rellekka"},
        monsters=["yak"], shop="neitiznot", members=True),
    "waterbirth_island": dict(name="Waterbirth Island",
        desc="A storm-lashed rock where dagannoths boil out of blowholes. "
             "A sea-cave mouth yawns at the waterline ('cave').",
        exits={"sail": "rellekka", "cave": "waterbirth_dungeon"},
        monsters=["dagannoth", "rock crab"], hostile=True, members=True,
        qlock=("fremennik_trials", ("complete",),
               "Jarvald bars the gangplank: 'Waterbirth is FREMENNIK "
               "water, outerlander.' (Quest: The Fremennik Trials — speak "
               "to Brundt in Rellekka)")),
    "waterbirth_dungeon": dict(name="Waterbirth Dungeon",
        desc="Sea-cut tunnels booming with surf. Dagannoths swarm the "
             "dark, and the deepest shaft breathes like something asleep "
             "('deep').",
        exits={"up": "waterbirth_island", "deep": "dks_lair"},
        monsters=["dagannoth"], hostile=True, members=True),
    "dks_lair": dict(name="The Kings' Lair",
        desc="A drowned cathedral of rock. THREE KINGS circle in the black "
             "water: REX the crusher, PRIME the storm-caller, SUPREME the "
             "spike-thrower. Fight one and the others circle...",
        exits={"up": "waterbirth_dungeon"},
        monsters=["dagannoth rex", "dagannoth prime", "dagannoth supreme"],
        members=True),
})
ROOMS["seers_village"]["exits"]["north"] = "rellekka"
ROOMS["seers_village"]["desc"] += (" North, the road runs cold toward "
                                   "Rellekka and the Fremennik Province.")
for _rm in ("rellekka", "rock_crab_coast", "neitiznot", "waterbirth_island",
            "waterbirth_dungeon", "dks_lair"):
    REGIONS[_rm] = "Fremennik"
TRAVEL_HUBS["rellekka"] = "rellekka"
TRAVEL_NAMES.append("Rellekka")
REGION_AMBIENT["Fremennik"] = [
    "Gulls scream over the grey water.",
    "Somewhere in the longhall, a saga finds its chorus.",
    "The surf drags cold fingers up the shingle.",
    "A war-horn sounds far out across the sound, and falls silent.",
]

# --- The Fremennik Trials (3 QP) ---------------------------------------------
ALL_QUESTS["fremennik_trials"] = "The Fremennik Trials"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["fremennik_trials"] = 3
NPC_NAMES["fremennik_trials"] = "Brundt the Chieftain"
NPC_NAMES["olaf"] = "Olaf the Bard"
QUEST_STARTS["fremennik_trials"] = "Brundt the Chieftain, Rellekka"
QUEST_HINTS["fremennik_trials"] = {
    "hunt": "slay the Draugen haunting the rock crab coast east of Rellekka",
    "hunted": "report your kill to Brundt the Chieftain",
    "lyre": "bring Olaf the Bard maple logs and 2 balls of wool",
    "song": "perform in the longhall — talk to Brundt, lyre in hand",
    "feast": "bring Brundt 3 swordfish (cooked) for the longhall table",
}

_FREM_NAMES = ["Skulgrimen", "Thorvald", "Sigli", "Manni", "Swensen",
               "Peer", "Thora", "Asleif", "Borrokar", "Freygerd"]


def _frem_name(p):
    return _FREM_NAMES[sum(ord(c) for c in p.name) % len(_FREM_NAMES)]


def talk_brundt(p):
    stage = _q(p, "fremennik_trials")
    if stage == "not_started":
        banner("Quest Start: The Fremennik Trials", color="purple",
               line_color="bmagenta")
        say("Brundt the Chieftain: \"An outerlander wants to sail OUR "
            "waters? Then become one of us. Three trials: the HUNT, the "
            "SONG, and the FEAST. First — a DRAUGEN, a drowned man's "
            "spite, haunts the crab coast. Slay it.\"")
        p.quests["fremennik_trials"] = "hunt"
        if "the draugen" not in ROOMS["rock_crab_coast"]["monsters"]:
            ROOMS["rock_crab_coast"]["monsters"].append("the draugen")
    elif stage == "hunt":
        say("Brundt: \"The Draugen still walks the coast east of here. "
            "'fight the draugen'!\"")
    elif stage == "hunted":
        say("Brundt: \"The Draugen unmade! You hunt like one of us. Now "
            "the SONG — Olaf the Bard will build you a lyre, if you bring "
            "him maple logs and two balls of wool.\"", "byellow")
        p.quests["fremennik_trials"] = "lyre"
    elif stage == "lyre":
        say("Brundt: \"Speak to Olaf — maple logs and two balls of wool "
            "for your lyre.\"")
    elif stage == "song":
        if not p.has("lyre"):
            say("Brundt: \"You'd perform empty-handed? Where is your "
                "lyre?\"")
            return
        say("You strike the strings. The longhall falls quiet... then "
            "stamps and roars along until the rafters shake!", "bcyan",
            "bold")
        say("Brundt: \"HA! The song is yours. Last comes the FEAST — "
            "bring three swordfish, cooked and steaming, for the long "
            "table.\"", "byellow")
        p.quests["fremennik_trials"] = "feast"
    elif stage == "feast":
        if p.count("swordfish") < 3:
            say("Brundt: \"Three cooked swordfish for the table! Catherby "
                "and Musa Point run thick with them — bring a harpoon.\"")
            return
        p.take("swordfish", 3)
        _complete_banner("The Fremennik Trials")
        name = _frem_name(p)
        say(f"The feast is laid and the horns are drained. The longhall "
            f"rises as one and roars your Fremennik name: {name.upper()}! "
            "2,812 xp awarded across six skills — and the sail to "
            "WATERBIRTH ISLAND is yours.", "gold", "bold")
        for _s in ("attack", "strength", "defence", "hitpoints",
                   "fishing", "woodcutting"):
            p.gain_xp(_s, 2812)
        p.quests["fremennik_trials"] = "complete"
    elif stage == "complete":
        say(f"Brundt: \"{_frem_name(p)}! The Kings still circle beneath "
            "Waterbirth, if your arm itches for glory.\"")


def talk_olaf(p):
    stage = _q(p, "fremennik_trials")
    if stage == "lyre":
        if p.has("maple logs") and p.count("ball of wool") >= 2:
            p.take("maple logs", 1)
            p.take("ball of wool", 2)
            p.add("lyre")
            p.quests["fremennik_trials"] = "song"
            say("Olaf carves the maple, twists the wool to strings, and "
                "hands you a LYRE. \"Now play it for the chieftain — and "
                "don't you dare go flat.\"", "bgreen")
        else:
            say("Olaf: \"Maple logs and two balls of wool. Seers' maples "
                "stand south of here, and their spinning wheel isn't "
                "far.\"")
    elif stage == "song":
        say("Olaf: \"You have the lyre — go play the longhall, "
            "outerlander!\"")
    else:
        say("Olaf hums a saga of three Kings beneath Waterbirth: the "
            "crusher, the storm-caller, the spike-thrower — and the rings "
            "they hoard.")


QUEST_TALK["fremennik_trials"] = talk_brundt
QUEST_TALK["olaf"] = talk_olaf


# ===========================================================================
#  TROLL COUNTRY  (Burthorpe, the Warriors' Guild, and the Troll Stronghold)
# ===========================================================================
# Burthorpe sits north of Taverley. The Warriors' Guild weighs your arm at
# the door (attack + strength 130) and its cyclopes yield DEFENDERS tier by
# tier; Death Plateau climbs to the Troll Stronghold and the peak of
# Trollheim — where a crack in the mountain drops into the God Wars.

# --- defenders: off-hand weapons, earned in order ---------------------------
_DEFENDER_TIERS = [("bronze", 3, 1, 300), ("iron", 5, 2, 700),
                   ("steel", 8, 3, 1500), ("black", 11, 4, 3000),
                   ("mithril", 14, 5, 6000), ("adamant", 17, 5, 12000),
                   ("rune", 20, 6, 35000)]
DEFENDER_ORDER = [f"{n} defender" for n, _a, _s, _v in _DEFENDER_TIERS]
for _dn, _da, _ds, _dv in _DEFENDER_TIERS:
    add_item(f"{_dn} defender", _dv, members=True,
             equip={"slot": "shield", "astab": _da, "aslash": _da,
                    "acrush": _da, "dstab": _da, "dslash": _da,
                    "dcrush": _da, "str": _ds})
EFFECT_NOTES["rune defender"] = ("an off-hand blade — attack bonuses in the "
                                 "shield slot; guild cyclopes award each "
                                 "tier in order")


def _best_defender(p):
    """Index of the best defender the player owns anywhere, or -1."""
    best = -1
    for i, d in enumerate(DEFENDER_ORDER):
        if p.has(d) or d in p.equipment.values() \
                or d in getattr(p, "bank", {}):
            best = i
    return best


# --- creatures ---------------------------------------------------------------
_add_mob("cyclops",
    {"abonus": 15, "atktype": ["crush"], "att": 50, "cb": 56, "dstab": 25,
     "dslash": 25, "dcrush": 25, "dmagic": 10, "drange": 25, "def": 45,
     "hp": 60, "maxhit": 7, "str": 50, "weak": "stab"},
    [("big bones", 1, 1, 1.0), ("coins", 20, 120, 0.7)],
    members=True, rank="hard")
_add_mob("mountain troll",
    {"abonus": 20, "atktype": ["crush"], "att": 60, "cb": 69, "dstab": 40,
     "dslash": 40, "dcrush": 30, "dmagic": 20, "drange": 40, "def": 55,
     "hp": 60, "maxhit": 8, "str": 65, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 20, 150, 0.7),
     ("earth rune", 5, 20, 0.3), ("grimy ranarr", 1, 1, 0.04)],
    members=True, rank="hard")
_add_mob("thrower troll",
    {"abonus": 25, "atktype": ["ranged"], "att": 65, "cb": 76, "dstab": 40,
     "dslash": 40, "dcrush": 35, "dmagic": 25, "drange": 45, "def": 60,
     "hp": 64, "maxhit": 9, "str": 70, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 30, 180, 0.7),
     ("law rune", 1, 4, 0.15)],
    members=True, rank="hard")
_add_mob("troll general",
    {"abonus": 30, "atktype": ["crush"], "att": 90, "cb": 91, "dstab": 55,
     "dslash": 55, "dcrush": 45, "dmagic": 30, "drange": 55, "def": 75,
     "hp": 90, "maxhit": 11, "str": 90, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 100, 500, 0.9),
     ("nature rune", 5, 15, 0.3), ("grimy ranarr", 1, 2, 0.08)],
    members=True, rank="elite")

# --- DAD, the gatekeeper ------------------------------------------------------
DAD_ART = r"""
        ______
     .-'      '-.
    /  O      O  \
   |      __      |
   |  \________/  |
    \   ______   /
   .-'-.|      |.-'-.
  /     '------'     \
"""


def _dad_intro(name):
    return [_tint(DAD_ART, "grey"), _tint(DAD_ART, "byellow", "bold")]


def _dad_death(name):
    return [_tint(DAD_ART, "byellow"), _tint(DAD_ART, "grey", "dim")]


def _dad_stagger(p, m, dmg):
    p.stat_drain["defence"] = p.stat_drain.get("defence", 0) + 2
    print("  " + paint("The slam rattles your bones! (-2 defence)", "bblue"))


DAD_ATTACKS = [
    {"label": "a haymaker like a falling pine", "verb": "swings",
     "color": ("byellow", "bold"),
     "builder": lambda: [_tint(DAD_ART, "byellow", "bold")],
     "mult": 1.3, "w": 3, "atype": "crush"},
    {"label": "a boulder the size of a cartwheel", "verb": "hurls",
     "color": ("grey", "bold"),
     "builder": lambda: [_tint(DAD_ART, "grey", "bold")],
     "mult": 1.0, "w": 2, "atype": "ranged"},
    {"label": "a ground-slam", "verb": "drops into",
     "color": ("brown",),
     "builder": lambda: [_tint(DAD_ART, "brown")],
     "mult": 0.8, "w": 2, "atype": "crush", "effect": _dad_stagger},
]

_add_mob("dad",
    {"abonus": 35, "atktype": ["crush", "ranged"], "att": 100, "cb": 101,
     "dstab": 60, "dslash": 60, "dcrush": 50, "dmagic": 35, "drange": 60,
     "def": 80, "hp": 120, "maxhit": 13, "str": 100, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 300, 1200, 1.0),
     ("law rune", 2, 8, 0.4)], members=True)
MONSTERS["dad"]["boss"] = True
MONSTERS["dad"]["rank"] = "boss"
_BOSSES.add("dad")
BOSS_TURN["dad"] = lambda p, m: _boss_take_turn(p, m, DAD_ATTACKS)
BOSS_INTRO["dad"] = _dad_intro
BOSS_DEATH["dad"] = _dad_death
MONSTER_ART["dad"] = DAD_ART

# --- the region ----------------------------------------------------------------
ROOMS.update({
    "burthorpe": dict(name="Burthorpe",
        desc="A garrison town under the mountains, all drill-yards and "
             "watchfires. Denulth of the Imperial Guard frets over his "
             "maps, the Warriors' Guild stands open to proven arms "
             "('guild'), and Death Plateau looms above ('plateau').",
        exits={"south": "taverley", "guild": "warriors_guild",
               "plateau": "death_plateau"},
        bank=True, npc="troll_stronghold", members=True),
    "warriors_guild": dict(name="Warriors' Guild",
        desc="Ghommal's hall of clashing steel. In the cyclops pen, "
             "one-eyed giants guard the armoury's DEFENDERS — hold your "
             "best and slay for the next tier.",
        exits={"out": "burthorpe"},
        monsters=["cyclops"], members=True,
        stat_lock=(["attack", "strength"], 130,
                   "Ghommal bars the door: 'Da Warriors' Guild is for "
                   "WARRIORS. Come back wiv attack an' strength what add "
                   "to 130.'")),
    "death_plateau": dict(name="Death Plateau",
        desc="A wind-scoured shelf of scree where trolls squat among the "
             "boulders — some of the boulders squat back. The stronghold "
             "gate is carved into the cliff above ('up').",
        exits={"down": "burthorpe", "up": "troll_stronghold"},
        monsters=["mountain troll", "thrower troll"], hostile=True,
        members=True),
    "troll_stronghold": dict(name="Troll Stronghold",
        desc="A reeking warren of tunnels behind a gate of lashed pines. "
             "DAD fills the gate-hall, and somewhere deeper a prisoner "
             "rattles his chains.",
        exits={"out": "death_plateau", "peak": "trollheim"},
        monsters=["dad", "troll general"], hostile=True, members=True,
        npc="godric",
        qlock=("troll_stronghold",
               ("started", "dad", "freed", "complete"),
               "The stronghold gate is barred from within. (Quest: Troll "
               "Stronghold — speak to Denulth in Burthorpe)")),
    "trollheim": dict(name="Trollheim",
        desc="The roof of Troll Country. From the summit you can see half "
             "of Gielinor — and a crack in the mountainside that breathes "
             "frost, descending into the God Wars ('chasm').",
        exits={"down": "troll_stronghold", "chasm": "gwd_entrance"},
        members=True),
})
ROOMS["taverley"]["exits"]["north"] = "burthorpe"
ROOMS["taverley"]["desc"] += " Burthorpe's watchfires glow to the north."
ROOMS["gwd_entrance"]["exits"]["climb"] = "trollheim"
REGIONS.update({"burthorpe": "Asgarnia", "warriors_guild": "Asgarnia",
                "death_plateau": "Trollheim", "troll_stronghold": "Trollheim",
                "trollheim": "Trollheim"})
TRAVEL_HUBS["burthorpe"] = "burthorpe"
TRAVEL_NAMES.append("Burthorpe")
REGION_AMBIENT["Trollheim"] = [
    "Wind screams over the scree.",
    "Somewhere above, rock grinds on rock — or a troll laughs.",
    "Loose stones clatter away down the mountainside.",
]

# --- Troll Stronghold (1 QP) ---------------------------------------------------
ALL_QUESTS["troll_stronghold"] = "Troll Stronghold"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["troll_stronghold"] = 1
NPC_NAMES["troll_stronghold"] = "Denulth"
NPC_NAMES["godric"] = "Godric"
QUEST_STARTS["troll_stronghold"] = "Denulth, Burthorpe"
QUEST_HINTS["troll_stronghold"] = {
    "started": "climb Death Plateau and breach the Troll Stronghold ('up')",
    "dad": "DAD is beaten — find Godric in the stronghold and set him free",
    "freed": "return to Denulth in Burthorpe",
}


def talk_denulth(p):
    stage = _q(p, "troll_stronghold")
    if stage == "not_started":
        banner("Quest Start: Troll Stronghold", color="purple",
               line_color="bmagenta")
        say("Denulth: \"The trolls have taken GODRIC of the Imperial Guard "
            "and dragged him to their stronghold above Death Plateau. "
            "Their gatekeeper is a brute they call DAD. Beat the troll, "
            "breach the gate, bring our man home.\"")
        p.quests["troll_stronghold"] = "started"
    elif stage in ("started", "dad"):
        say("Denulth: \"The stronghold is up the plateau — beat DAD at the "
            "gate and find Godric!\"")
    elif stage == "freed":
        _complete_banner("Troll Stronghold")
        say("Godric limps into the drill-yard behind you and the garrison "
            "erupts. Denulth: \"The Guard owes you a debt.\" 8,000 "
            "agility and strength xp awarded!", "gold", "bold")
        p.gain_xp("agility", 8000)
        p.gain_xp("strength", 8000)
        p.quests["troll_stronghold"] = "complete"
    elif stage == "complete":
        say("Denulth: \"Burthorpe sleeps easier with you on the wall, "
            "friend.\"")


def talk_godric(p):
    stage = _q(p, "troll_stronghold")
    if stage == "dad":
        say("You snap the crude troll chains. Godric: \"Thought I was "
            "stew, friend. Let's get off this mountain — Denulth will "
            "want to see us both.\"", "bgreen")
        p.quests["troll_stronghold"] = "freed"
    elif stage == "started":
        say("Godric (from the shadows): \"The gatekeeper! Deal with DAD "
            "first or we'll never walk out — 'fight dad'!\"")
    elif stage in ("freed", "complete"):
        say("The empty chains rattle in the draught.")
    else:
        say("A prisoner's voice echoes somewhere deeper in the warren.")


QUEST_TALK["troll_stronghold"] = talk_denulth
QUEST_TALK["godric"] = talk_godric


# ===========================================================================
#  KANDARIN COMPLETION  (Camelot, the Waterfall, gnomes, and two guilds)
# ===========================================================================
# Camelot rises by Seers' Village; Baxtorian Falls thunders north of
# Ardougne; the Tree Gnome Stronghold and Yanille fill the west. The
# Fishing Guild (68) and Magic Guild (66) reuse the stat_lock gate, and
# sharks arrive as the endgame food.

# --- sharks: the food upgrade -------------------------------------------------
add_item("raw shark", 300, members=True)
add_item("shark", 450, heal=20, members=True)
FISH["harpoon"].append(("raw shark", 76, 110))
RAW_TO_COOKED["raw shark"] = ("shark", "burnt fish", 80)
COOK_XP["raw shark"] = 140

# --- excalibur + odds and ends ------------------------------------------------
add_item("excalibur", 20000, members=True,
         equip={"slot": "weapon", "astab": 20, "aslash": 29, "str": 25,
                "req": {"attack": 30}, "quest": "merlins_crystal"})


def _excal_guard(p, m):
    p.stat_boost["defence"] = p.stat_boost.get("defence", 0) + 8
    print("  " + paint("Excalibur flares — your guard hardens! (+8 defence "
                       "for this fight)", "bcyan"))


SPECIAL_ATTACKS["excalibur"] = {
    "name": "Sanctuary", "cost": 100, "hits": 1, "acc": 1.0, "dmg": 0.5,
    "desc": "a warding strike: +8 defence for the rest of the fight",
    "after": _excal_guard}
EFFECT_NOTES["excalibur"] = ("the Lady of the Lake's blade — its special "
                             "hardens your defence by 8 for the fight")
add_item("gnome cocktail", 30, heal=5, members=True)
add_item("glarial's amulet", 100, members=True)
SHOPS["gnome"] = {"gnome cocktail": 30, "banana": 5}
SHOPS["fishing_guild"] = {"harpoon": 5, "lobster pot": 20,
                          "small fishing net": 5}
SHOPS["magic_guild"] = {"air rune": 4, "water rune": 4, "earth rune": 4,
                        "fire rune": 4, "mind rune": 3, "chaos rune": 90,
                        "death rune": 180, "cosmic rune": 100,
                        "law rune": 240, "nature rune": 180,
                        "blood rune": 380, "mystic hat": 15000}

# --- fire giants ----------------------------------------------------------------
_add_mob("fire giant",
    {"abonus": 25, "atktype": ["slash"], "att": 70, "cb": 86, "dstab": 40,
     "dslash": 40, "dcrush": 40, "dmagic": 15, "drange": 45, "def": 65,
     "hp": 111, "maxhit": 10, "str": 80, "weak": "slash"},
    [("big bones", 1, 1, 1.0), ("coins", 30, 300, 0.8),
     ("fire rune", 10, 30, 0.6), ("blood rune", 2, 5, 0.1),
     ("grimy ranarr", 1, 1, 0.05), ("rune scimitar", 1, 1, 0.015)],
    members=True, rank="elite")

# --- the region -------------------------------------------------------------------
ROOMS.update({
    "camelot": dict(name="Camelot Castle",
        desc="White towers over blue banners. King Arthur keeps an "
             "improbable court here — and high in the tallest tower, "
             "something glitters man-shaped in a shard of crystal "
             "('search').",
        exits={"south": "seers_village"},
        npc="merlins_crystal", members=True),
    "baxtorian_falls": dict(name="Baxtorian Falls",
        desc="The river throws itself off the cliff in a standing wall of "
             "thunder. Almera's cottage clings to the bank, an old "
             "tombstone leans in the spray ('search'), and a ledge runs "
             "behind the water ('cave').",
        exits={"south": "ardougne", "cave": "waterfall_cave"},
        npc="waterfall_quest", members=True),
    "waterfall_cave": dict(name="Chambers of Baxtorian",
        desc="A drowned elven hall behind the falls. FIRE GIANTS doze "
             "against pillars that remember better kings, and an altar "
             "waits at the heart of it ('search').",
        exits={"out": "baxtorian_falls"},
        monsters=["fire giant"], hostile=True, members=True,
        qlock=("waterfall_quest", ("amulet", "complete"),
               "The wall of water hurls you back. (Quest: Waterfall Quest "
               "— Almera at the falls; Glarial's amulet opens the way)")),
    "tree_gnome_stronghold": dict(name="Tree Gnome Stronghold",
        desc="A city in the boughs of a single vast tree. Gnome gliders "
             "creak overhead, cocktail waiters weave along the walkways, "
             "and the beginners' agility course loops the roots "
             "('agility').",
        exits={"east": "ardougne"},
        shop="gnome", agility_course=(1, 10, 1), members=True),
    "fishing_guild": dict(name="Fishing Guild",
        desc="Hemenster's guild of master anglers — harpoon wharves, "
             "lobster pools, and water that practically boils with "
             "SHARKS.",
        exits={"out": "seers_village"},
        bank=True, fish_tools=["harpoon", "cage"],
        shop="fishing_guild", members=True,
        stat_lock=(["fishing"], 68,
                   "The guild master blocks the gate: 'Members catch "
                   "their own weight, friend. Fishing 68 and you're "
                   "in.'")),
    "yanille": dict(name="Yanille",
        desc="A walled frontier town at Kandarin's southern edge, all "
             "watchtowers and wizardry. The Magic Guild's spire hums "
             "behind the market ('guild').",
        exits={"north": "ardougne", "guild": "magic_guild"},
        bank=True, members=True),
    "magic_guild": dict(name="Magic Guild",
        desc="The Wizards' Guild of Yanille: floating candles, arguing "
             "portals, and a shop that sells every rune a war could "
             "want.",
        exits={"out": "yanille"},
        shop="magic_guild", members=True,
        stat_lock=(["magic"], 66,
                   "The doorman's eyes glow: 'Magic 66, or the door "
                   "stays a wall.'")),
})
ROOMS["seers_village"]["exits"]["castle"] = "camelot"
ROOMS["seers_village"]["exits"]["guild"] = "fishing_guild"
ROOMS["seers_village"]["desc"] += (" Camelot's banners fly to the "
                                   "north-east ('castle'), and the Fishing "
                                   "Guild works the water at Hemenster "
                                   "('guild').")
ROOMS["ardougne"]["exits"]["falls"] = "baxtorian_falls"
ROOMS["ardougne"]["exits"]["gnome"] = "tree_gnome_stronghold"
ROOMS["ardougne"]["exits"]["yanille"] = "yanille"
for _rm in ("camelot", "baxtorian_falls", "waterfall_cave",
            "tree_gnome_stronghold", "fishing_guild", "yanille",
            "magic_guild"):
    REGIONS[_rm] = "Kandarin"
TRAVEL_HUBS["yanille"] = "yanille"
TRAVEL_NAMES.append("Yanille")
TRAVEL_HUBS["gnome stronghold"] = "tree_gnome_stronghold"
TRAVEL_NAMES.append("Gnome Stronghold")

# --- Waterfall Quest (1 QP) -----------------------------------------------------
ALL_QUESTS["waterfall_quest"] = "Waterfall Quest"
QUEST_POINTS["waterfall_quest"] = 1
NPC_NAMES["waterfall_quest"] = "Almera"
QUEST_STARTS["waterfall_quest"] = "Almera, Baxtorian Falls (north of " \
                                  "Ardougne)"
QUEST_HINTS["waterfall_quest"] = {
    "started": "search the tombstone by the falls for Glarial's amulet",
    "amulet": "enter the cave behind the falls and 'search' the altar",
}


def talk_almera(p):
    stage = _q(p, "waterfall_quest")
    if stage == "not_started":
        banner("Quest Start: Waterfall Quest", color="purple",
               line_color="bmagenta")
        say("Almera: \"My boy Hudon's obsessed with the treasure of "
            "BAXTORIAN, the elf-king drowned under these falls. They say "
            "only Glarial's amulet opens his halls — her grave lies "
            "somewhere by the water. Mind the currents, dear.\"")
        p.quests["waterfall_quest"] = "started"
    elif stage == "started":
        say("Almera: \"Glarial's grave is close — 'search' by the "
            "falls.\"")
    elif stage == "amulet":
        say("Almera: \"The amulet! Then the way behind the water is open "
            "('cave'). Mind the giants, dear.\"")
    else:
        say("Almera: \"Hudon still hasn't done the dishes, treasure or "
            "no.\"")


QUEST_TALK["waterfall_quest"] = talk_almera

# --- Merlin's Crystal (6 QP) -----------------------------------------------------
ALL_QUESTS["merlins_crystal"] = "Merlin's Crystal"
ALL_QUESTS["dragon_slayer"] = ALL_QUESTS.pop("dragon_slayer")  # capstone last
QUEST_POINTS["merlins_crystal"] = 6
NPC_NAMES["merlins_crystal"] = "King Arthur"
NPC_NAMES["lady_lake"] = "The Lady of the Lake"
QUEST_STARTS["merlins_crystal"] = "King Arthur, Camelot (by Seers' Village)"
QUEST_HINTS["merlins_crystal"] = {
    "excalibur": "seek the Lady of the Lake in Catherby — bring bread",
    "shatter": "strike the crystal atop Camelot ('search') with Excalibur",
}


def talk_arthur(p):
    stage = _q(p, "merlins_crystal")
    if stage == "not_started":
        banner("Quest Start: Merlin's Crystal", color="purple",
               line_color="bmagenta")
        say("King Arthur: \"My wizard MERLIN out-clevered himself and is "
            "sealed in his own crystal atop the tower. Steel won't scratch "
            "it — only EXCALIBUR. The Lady of the Lake keeps it; she "
            "waits at Catherby. A warning: she tests strangers.\"")
        p.quests["merlins_crystal"] = "excalibur"
    elif stage == "excalibur":
        say("King Arthur: \"The Lady of the Lake, at Catherby. Take her "
            "test — and take bread, is my advice.\"")
    elif stage == "shatter":
        say("King Arthur: \"You bear Excalibur! The tower stair is yours "
            "— 'search' and set my wizard free.\"")
    elif stage == "complete":
        say("Merlin (mid-argument with Arthur): \"— and I MEANT to be in "
            "the crystal. Ah, my rescuer! Camelot thanks you.\"")


def talk_lady(p):
    stage = _q(p, "merlins_crystal")
    if stage == "excalibur":
        if p.has("bread"):
            p.take("bread")
            p.add("excalibur")
            p.quests["merlins_crystal"] = "shatter"
            say("A beggar woman asks you for bread. You hand it over — and "
                "she stands transformed, robed in lake-light. \"Kindness "
                "before strength. The sword is yours.\" She lays EXCALIBUR "
                "in your hands.", "bcyan", "bold")
        else:
            say("A beggar woman by the shore asks: \"Spare a loaf of "
                "bread, traveller?\" (You have none. The general store "
                "sells bread.)")
    elif stage == "shatter":
        say("The Lady of the Lake: \"The sword knows its work. To "
            "Camelot.\"")
    else:
        say("A woman watches the water at the shore's edge. Lake-light "
            "clings to her.")


QUEST_TALK["merlins_crystal"] = talk_arthur
QUEST_TALK["lady_lake"] = talk_lady
ROOMS["camelot"]["npc"] = "merlins_crystal"
ROOMS["catherby"]["npc"] = "lady_lake"
ROOMS["catherby"]["desc"] += (" A woman stands at the water's edge, "
                              "watching the lake.")


# ===========================================================================
#  KARAMJA COMPLETION  (the deep jungle, dragon dungeon, and THE INFERNO)
# ===========================================================================
# South of Brimhaven the jungle swallows the road: Tai Bwo Wannai's
# tribesmen poison their spears, Shilo Village mines nothing but gems, and
# Saniboch charges admission to a dungeon full of dragons. Inside the
# volcano, the TzHaar city Mor Ul Rek trades in tokkul — and beneath it
# the INFERNO burns: eight waves, then TzKal-Zuk, then the infernal cape.

# --- red dragonhide line (ranged tier above green) ---------------------------
add_item("red dragonhide", 160, members=True)
add_item("red dragon leather", 200, members=True)
add_item("red d'hide body", 15000, members=True,
         equip={"amagic": -15, "arange": 20, "dstab": 24, "dslash": 33,
                "dcrush": 30, "dmagic": 26, "drange": 41, "slot": "body",
                "req": {"ranged": 60, "defence": 40}})
add_item("red d'hide chaps", 7000, members=True,
         equip={"amagic": -8, "arange": 10, "dstab": 12, "dslash": 15,
                "dcrush": 14, "dmagic": 12, "drange": 20, "slot": "legs",
                "req": {"ranged": 60}})
add_item("red d'hide vambraces", 3500, members=True,
         equip={"amagic": -6, "arange": 9, "dstab": 3, "dslash": 3,
                "dcrush": 3, "slot": "gloves", "req": {"ranged": 60}})
TAN_HIDES["red dragonhide"] = ("red dragon leather", 40)
CRAFT_RECIPES.update({
    "red d'hide vambraces": ("red dragon leather", 1, 73, 156),
    "red d'hide chaps": ("red dragon leather", 2, 75, 312),
    "red d'hide body": ("red dragon leather", 3, 77, 468),
})

# --- obsidian gear (tokkul-priced in Mor Ul Rek) ------------------------------
add_item("obsidian cape", 25000, members=True,
         equip={"dstab": 9, "dslash": 9, "dcrush": 9, "dmagic": 9,
                "drange": 9, "slot": "cape"})
add_item("toktz-xil-ak", 40000, members=True,
         equip={"slot": "weapon", "astab": 47, "aslash": 40, "str": 49,
                "req": {"attack": 60}})
add_item("toktz-ket-xil", 35000, members=True,
         equip={"slot": "shield", "dstab": 40, "dslash": 42, "dcrush": 38,
                "drange": 42, "str": 5, "req": {"defence": 60}})
add_item("infernal cape", 200000, members=True,
         equip={"astab": 4, "aslash": 4, "acrush": 4, "amagic": 4,
                "arange": 4, "dstab": 12, "dslash": 12, "dcrush": 12,
                "dmagic": 12, "drange": 12, "str": 6, "prayer": 2,
                "slot": "cape"})
EFFECT_NOTES["infernal cape"] = ("the greatest cape in Gielinor, quenched "
                                 "in TzKal-Zuk's own fire")
TOKKUL_SHOP = {"obsidian cape": 9000, "toktz-ket-xil": 12000,
               "toktz-xil-ak": 15000}


def cmd_redeem(p, arg):
    if p.location != "mor_ul_rek":
        say("Only the TzHaar of Mor Ul Rek trade in tokkul.", "grey")
        return
    want = arg.strip().lower()
    if not want:
        say("The TzHaar armoury (pay in tokkul — 'redeem <item>'):",
            "orange", "bold")
        for it, cost in TOKKUL_SHOP.items():
            say(f"  {it:<16} {cost:,} tokkul", "grey")
        say(f"  (You carry {p.count('tokkul'):,} tokkul.)", "grey")
        return
    match = next((it for it in TOKKUL_SHOP if want in it), None)
    if not match:
        say("The TzHaar shrugs: no such ware. ('redeem' lists the "
            "armoury.)")
        return
    cost = TOKKUL_SHOP[match]
    if p.count("tokkul") < cost:
        say(f"TzHaar-Hur: \"{cost:,} tokkul. You carry "
            f"{p.count('tokkul'):,}. Go fight, JalYt.\"", "byellow")
        return
    p.take("tokkul", cost)
    p.add(match)
    say(f"You trade {cost:,} tokkul for the {match.upper()}.", "bgreen",
        "bold")
    return True


HANDLERS["redeem"] = cmd_redeem
HANDLERS["exchange"] = cmd_redeem

# --- jungle creatures + dragons -----------------------------------------------
def _tribes_poison(p, m, dmg):
    if dmg > 0 and not getattr(p, "poison", 0) and random.random() < 0.4:
        p.poison = 2
        print("  " + paint("The spear's coating burns — you are POISONED!",
                           "green"))


_add_mob("tribesman",
    {"abonus": 10, "atktype": ["stab"], "att": 30, "cb": 32, "dstab": 15,
     "dslash": 15, "dcrush": 15, "dmagic": 5, "drange": 15, "def": 25,
     "hp": 32, "maxhit": 4, "str": 30, "weak": "slash"},
    [("bones", 1, 1, 1.0), ("coins", 5, 60, 0.6),
     ("grimy harralander", 1, 1, 0.15)],
    members=True, rank="medium")
MONSTER_EFFECTS["tribesman"] = _tribes_poison

_DRAGON_KIN = {
    "red dragon": (
        {"abonus": 30, "atktype": ["slash"], "att": 90, "cb": 152,
         "dstab": 50, "dslash": 50, "dcrush": 50, "dmagic": 60,
         "drange": 55, "def": 90, "hp": 140, "maxhit": 13, "str": 95,
         "weak": "stab"},
        [("dragon bones", 1, 1, 1.0), ("red dragonhide", 2, 3, 1.0),
         ("coins", 100, 500, 0.8), ("fire rune", 10, 30, 0.4)]),
    "bronze dragon": (
        {"abonus": 35, "atktype": ["slash"], "att": 100, "cb": 131,
         "dstab": 70, "dslash": 70, "dcrush": 60, "dmagic": 30,
         "drange": 80, "def": 100, "hp": 122, "maxhit": 13, "str": 100,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("bronze bar", 2, 4, 1.0),
         ("coins", 200, 800, 0.8), ("adamantite ore", 1, 2, 0.2)]),
    "iron dragon": (
        {"abonus": 40, "atktype": ["slash"], "att": 120, "cb": 189,
         "dstab": 85, "dslash": 85, "dcrush": 70, "dmagic": 35,
         "drange": 95, "def": 110, "hp": 165, "maxhit": 15, "str": 120,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("iron bar", 3, 5, 1.0),
         ("coins", 300, 1200, 0.9), ("dragon med helm", 1, 1, 0.015)]),
    "steel dragon": (
        {"abonus": 45, "atktype": ["slash"], "att": 140, "cb": 246,
         "dstab": 100, "dslash": 100, "dcrush": 80, "dmagic": 40,
         "drange": 110, "def": 120, "hp": 190, "maxhit": 17, "str": 140,
         "weak": "magic"},
        [("dragon bones", 1, 1, 1.0), ("steel bar", 3, 6, 1.0),
         ("coins", 500, 2000, 1.0), ("dragon platelegs", 1, 1, 0.012),
         ("dragon dagger", 1, 1, 0.02)]),
}
for _dk, (_st, _drops) in _DRAGON_KIN.items():
    _add_mob(_dk, _st, _drops, members=True, rank="elite")
    MONSTERS[_dk]["dragonfire"] = True
DURADEL_TARGETS.extend(["fire giant", "steel dragon"])

# --- the Inferno roster ---------------------------------------------------------
_INFERNO_MOBS = {
    "jal-nib": ({"abonus": 5, "atktype": ["crush"], "att": 15, "cb": 32,
                 "dstab": 5, "dslash": 5, "dcrush": 5, "dmagic": 5,
                 "drange": 5, "def": 10, "hp": 10, "maxhit": 2, "str": 15,
                 "weak": "crush"},
                [("tokkul", 10, 30, 1.0)], "easy"),
    "jal-mejrah": ({"abonus": 20, "atktype": ["ranged"], "att": 60,
                    "cb": 85, "dstab": 30, "dslash": 30, "dcrush": 30,
                    "dmagic": 30, "drange": 30, "def": 55, "hp": 40,
                    "maxhit": 7, "str": 60, "weak": "crush"},
                   [("tokkul", 20, 60, 1.0)], "hard"),
    "jal-ak": ({"abonus": 30, "atktype": ["magic", "ranged"], "att": 90,
                "cb": 165, "dstab": 45, "dslash": 45, "dcrush": 45,
                "dmagic": 45, "drange": 45, "def": 70, "hp": 70,
                "maxhit": 10, "str": 90, "weak": "crush"},
               [("tokkul", 40, 100, 1.0)], "elite"),
    "jal-imkot": ({"abonus": 40, "atktype": ["crush"], "att": 120,
                   "cb": 240, "dstab": 60, "dslash": 60, "dcrush": 60,
                   "dmagic": 50, "drange": 60, "def": 85, "hp": 100,
                   "maxhit": 14, "str": 130, "weak": "slash"},
                  [("tokkul", 60, 140, 1.0)], "elite"),
    "jal-xil": ({"abonus": 45, "atktype": ["ranged"], "att": 140,
                 "cb": 370, "dstab": 65, "dslash": 65, "dcrush": 65,
                 "dmagic": 55, "drange": 70, "def": 90, "hp": 125,
                 "maxhit": 16, "str": 140, "weak": "crush"},
                [("tokkul", 80, 180, 1.0)], "elite"),
    "jal-zek": ({"abonus": 50, "atktype": ["magic"], "att": 160,
                 "cb": 490, "dstab": 70, "dslash": 70, "dcrush": 70,
                 "dmagic": 70, "drange": 75, "def": 95, "hp": 150,
                 "maxhit": 18, "str": 160, "weak": "crush"},
                [("tokkul", 100, 220, 1.0)], "elite"),
}
for _im, (_st, _drops, _rank) in _INFERNO_MOBS.items():
    _add_mob(_im, _st, _drops, members=True, rank=_rank)
MONSTER_EFFECTS["jal-mejrah"] = MONSTER_EFFECTS["tz-kih"]   # prayer-eater

_add_mob("jaltok-jad",
    {"abonus": 60, "atktype": ["magic", "ranged", "crush"], "att": 200,
     "cb": 900, "dstab": 65, "dslash": 65, "dcrush": 65, "dmagic": 65,
     "drange": 65, "def": 100, "hp": 250, "maxhit": 30, "str": 200,
     "weak": "crush"},
    [("tokkul", 300, 800, 1.0)], members=True)
MONSTERS["jaltok-jad"]["boss"] = True
MONSTERS["jaltok-jad"]["rank"] = "boss"
_BOSSES.add("jaltok-jad")
BOSS_TURN["jaltok-jad"] = _jad_take_turn      # telegraphs like his little kin
BOSS_INTRO["jaltok-jad"] = BOSS_INTRO.get("tztok-jad")
BOSS_DEATH["jaltok-jad"] = BOSS_DEATH.get("tztok-jad")

ZUK_ART = r"""
       \\  |  //        \\  |  //
    ====[#######]====[#######]====
      .-'  ___________________ '-.
     /    /  \   _______   /  \   \
    |    | () |  \     /  | () |   |
     \    \__/    \   /    \__/   /
      '-.          \ /         .-'
         '========= V ========='
"""


def _zuk_intro(name):
    return [_tint(ZUK_ART, "grey"), _tint(ZUK_ART, "orange", "bold"),
            _tint(ZUK_ART, "bred", "bold")]


def _zuk_death(name):
    return [_tint(ZUK_ART, "bred"), _tint(ZUK_ART, "grey", "dim")]


def _zuk_take_turn(p, m):
    """Zuk's barrage burns through prayer; every third turn the obsidian
    shield glides between you and the fire."""
    cyc = m.get("zuk_cycle", 0)
    m["zuk_cycle"] = cyc + 1
    if cyc % 3 == 2:
        say("The obsidian shield glides across — you shelter in its "
            "shadow. TzKal-Zuk's fire breaks around you!", "bcyan")
    else:
        style = "magic" if cyc % 2 else "ranged"
        say(f"TzKal-Zuk hurls a wall of burning {style}!", "bred", "bold")
        dmg = random.randint(10, m["max_hit"])
        if p.prayer_protects(style):
            dmg = int(dmg * 0.85)
            print("  " + paint("Zuk's fury burns THROUGH your prayer — it "
                               "barely softens the blow.", "bmagenta"))
        p.hp -= dmg
        print("  " + paint(f"The fire takes {dmg} from you.", "bred")
              + "  " + paint("HP ", "white")
              + bar_meter(max(p.hp, 0), p.max_hp, 18))
    if p.active_prayers:
        p.prayer_points -= p.prayer_drain()
        if p.prayer_points <= 0:
            p.prayer_points = 0
            p.active_prayers = []
            print("  " + paint("Your prayers flicker out (no prayer "
                               "points).", "bmagenta"))
    return "died" if p.hp <= 0 else None


_add_mob("tzkal-zuk",
    {"abonus": 70, "atktype": ["ranged", "magic"], "att": 260, "cb": 1400,
     "dstab": 250, "dslash": 250, "dcrush": 250, "dmagic": 60,
     "drange": 80, "def": 100, "hp": 300, "maxhit": 26, "str": 260,
     "weak": "ranged"},
    [("tokkul", 1000, 3000, 1.0), ("uncut diamond", 1, 3, 0.5)],
    members=True)
MONSTERS["tzkal-zuk"]["boss"] = True
MONSTERS["tzkal-zuk"]["rank"] = "boss"
_BOSSES.add("tzkal-zuk")
BOSS_TURN["tzkal-zuk"] = _zuk_take_turn
BOSS_INTRO["tzkal-zuk"] = _zuk_intro
BOSS_DEATH["tzkal-zuk"] = _zuk_death
MONSTER_ART["tzkal-zuk"] = ZUK_ART

# --- the Inferno machinery -------------------------------------------------------
INFERNO_WAVES = ["jal-nib", "jal-mejrah", "jal-ak", "jal-imkot", "jal-xil",
                 "jal-zek", "jaltok-jad", "tzkal-zuk"]


def _inferno_start_wave(p):
    mon = INFERNO_WAVES[p.inferno_wave - 1]
    say(f"— Inferno wave {p.inferno_wave} of {len(INFERNO_WAVES)} —",
        "bred", "bold")
    _start_combat(p, mon)


def _inferno_challenge(p):
    if getattr(p, "inferno_wave", 0):
        say(f"You're mid-run — wave {p.inferno_wave}/{len(INFERNO_WAVES)}. "
            "Type 'next' to continue.", "byellow")
        return
    banner("THE INFERNO", color="bred", line_color="red")
    say("TzHaar-Ket-Keh: \"The Fight Caves was the door, JalYt. This is "
        "the furnace. Eight waves. ZUK waits at the bottom.\"",
        "orange", "bold")
    p.inferno_wave = 1
    _inferno_start_wave(p)


def _inferno_on_kill(p, target):
    """Advance the Inferno after each wave kill; forge the champion."""
    wave = getattr(p, "inferno_wave", 0)
    if not wave or not ROOMS[p.location].get("inferno") \
            or target != INFERNO_WAVES[wave - 1]:
        return
    if wave < len(INFERNO_WAVES):
        p.inferno_wave += 1
        nxt = INFERNO_WAVES[p.inferno_wave - 1]
        say(f"Wave {wave} survived! Breathe, eat, rethink — then 'next' "
            f"(wave {p.inferno_wave}/{len(INFERNO_WAVES)}: {nxt}).",
            "byellow", "bold")
    else:
        p.inferno_wave = 0
        show_art(ART_QUEST, "gold", center=True)
        banner("THE INFERNO — EXTINGUISHED", color="bred", line_color="red")
        p.add("infernal cape")
        say("TzHaar-Ket-Keh stares into the cooling dark: \"...Zuk is "
            "beaten. Take the cape, JalYt. It is quenched in his fire.\"",
            "orange", "bold")
        say("You receive the INFERNAL CAPE! ('equip infernal cape')",
            "bgreen", "bold")


# --- the region --------------------------------------------------------------------
ROOMS.update({
    "tai_bwo_wannai": dict(name="Tai Bwo Wannai",
        desc="A machete-hacked clearing where the Wannai tribe drums "
             "against the jungle dark. The spears here weep green at the "
             "tip — mind the TRIBESMEN. Shilo's gem road runs south.",
        exits={"north": "brimhaven", "south": "shilo_village"},
        monsters=["tribesman"], shop="tai_bwo", hostile=True,
        members=True),
    "shilo_village": dict(name="Shilo Village",
        desc="A stockaded mining town on the Shilo river. The famous GEM "
             "MINE glitters even in torchlight ('mine gem rock'), and "
             "fly-fishers work the rapids.",
        exits={"north": "tai_bwo_wannai"},
        bank=True, rocks=["gem rock"], fish_tools=["fly", "rod"],
        members=True),
    "brimhaven_dungeon": dict(name="Brimhaven Dungeon",
        desc="Saniboch's damp stairwell opens into a cavern of red "
             "scales and old gold. RED DRAGONS nest here, and an iron "
             "door glows at the deep end ('deeper').",
        exits={"out": "brimhaven", "deeper": "dragon_forge"},
        monsters=["red dragon", "moss giant"], hostile=True, members=True,
        fee=(875, "Saniboch grins: 'The dungeon eats adventurers, "
                  "friend. 875 coins to feed it you.'")),
    "dragon_forge": dict(name="The Dragon Forge",
        desc="A vault of ancient dwarven fire where METAL DRAGONS pace "
             "on iron claws — bronze, iron, steel. Bring an anti-dragon "
             "shield or bring a will.",
        exits={"back": "brimhaven_dungeon"},
        monsters=["bronze dragon", "iron dragon", "steel dragon"],
        hostile=True, members=True),
    "mor_ul_rek": dict(name="Mor Ul Rek",
        desc="The obsidian city of the TzHaar, lit by lava-light. "
             "TzHaar-Hur traders take TOKKUL for obsidian ('redeem'), "
             "and a sealed crack in the floor breathes white heat "
             "('inferno').",
        exits={"out": "karamja_volcano", "inferno": "the_inferno"},
        members=True),
    "the_inferno": dict(name="The Inferno",
        desc="The bottom of the world. Everything here is fire that "
             "learned to want things. ('challenge' — eight waves, then "
             "ZUK)",
        exits={"out": "mor_ul_rek"},
        inferno=True, members=True,
        gear_lock=(["fire cape|infernal cape"],
                   "TzHaar-Ket-Keh bars the crack: 'The furnace is for "
                   "PROVEN JalYt. Wear your fire cape.'")),
})
SHOPS["tai_bwo"] = {"antipoison": 120, "machete": 40, "banana": 3}
add_item("machete", 40, members=True,
         equip={"slot": "weapon", "aslash": 7, "str": 6})
ROOMS["brimhaven"]["exits"]["south"] = "tai_bwo_wannai"
ROOMS["brimhaven"]["exits"]["dungeon"] = "brimhaven_dungeon"
ROOMS["brimhaven"]["desc"] += (" A jungle track vanishes south toward "
                               "Tai Bwo Wannai, and Saniboch loiters by "
                               "a dungeon mouth ('dungeon').")
ROOMS["karamja_volcano"]["exits"]["city"] = "mor_ul_rek"
ROOMS["karamja_volcano"]["desc"] += (" Deeper in the rock, lava-light "
                                     "marks the TzHaar city of Mor Ul Rek "
                                     "('city').")
ROCKS["gem rock"] = ("uncut sapphire", 40, 65)
for _rm in ("tai_bwo_wannai", "shilo_village", "brimhaven_dungeon",
            "dragon_forge", "mor_ul_rek", "the_inferno"):
    REGIONS[_rm] = "Karamja"
TRAVEL_HUBS["shilo"] = "shilo_village"
TRAVEL_NAMES.append("Shilo")


# ===========================================================================
#  TWO-HANDED WEAPONS  (both hands or none — no shield alongside these)
# ===========================================================================
_TWO_HANDED = [
    # every bow needs a draw arm (crossbows are one-handed, bar Karil's)
    "shortbow", "longbow", "oak shortbow", "oak longbow", "willow shortbow",
    "willow longbow", "maple shortbow", "maple longbow", "yew shortbow",
    "yew longbow", "magic shortbow", "magic longbow", "karil's crossbow",
    # great weapons
    "bandos godsword", "armadyl godsword", "zamorak godsword",
    "saradomin godsword", "dharok's greataxe", "guthan's warspear",
    "torag's hammers", "verac's flail", "zamorakian spear",
    "saradomin sword", "granite maul", "hill giant club",
]
for _n in _TWO_HANDED:
    if _n in ITEMS and ITEMS[_n].get("equip"):
        ITEMS[_n]["equip"]["two_handed"] = True


# ===========================================================================
#  DESCRIPTION POLISH  (rooms that accumulated bolted-on hints get rewritten
#  as one clean paragraph — keep every 'keyword' players need)
# ===========================================================================
for _room, _desc in {
    "draynor_village": (
        "A run-down village where willows lean over the riverbank and "
        "fishing spots bubble in the shallows. Morgan looks terrified, "
        "Aggie's cauldron reeks, the Wise Old Man watches from his doorway, "
        "and a seed stall does quiet business in the market. A squat jail "
        "stands at the edge of town ('jail'), and the manor looms north."),
    "falador_square": (
        "The white-walled heart of Asgarnia. Doric the dwarf works his "
        "forge near the square, the White Knights' Castle rises north "
        "('castle'), Falador Park lies just beyond ('park'), and a mine "
        "shaft drops away to the south."),
    "port_sarim": (
        "A busy port smelling of tar and fish. Klarense tends the Lady "
        "Lumbridge at her mooring, boats run south to Karamja, and the "
        "fishing shop serves the docks. Mudskipper Point lies along the "
        "coast ('point')."),
    "edgeville": (
        "A frontier town on the Wilderness' doorstep, with a bank, a "
        "furnace, and old yews south of the wall. Vannaka the Slayer "
        "Master takes names here, Oziach's shabby hut sits by the river "
        "('hut'), and a dungeon mouth gapes below ('down'). North, past "
        "the ditch, the law runs out."),
    "varrock_east_bank": (
        "A bank on Varrock's east side. The road north leads to the Grand "
        "Exchange, standing stones rise to the north-east ('altar'), and "
        "the long road east runs for the River Salve and Paterdomus."),
    "karamja_port": (
        "A tropical island port under swaying banana palms ('pick'). The "
        "dock heaves with lobster pots and harpoon fishers, a volcano "
        "smokes inland ('volcano'), and Brimhaven lies east along the "
        "coast."),
    "rimmington": (
        "A small mining village with Doric's spare anvil and a scatter of "
        "copper, tin, iron and clay rocks. Your house plot sits west of "
        "the village ('house'), and the sealed ruin of Melzar's Maze "
        "stands to the north ('maze')."),
    "grand_exchange": (
        "Traders from across Gielinor shout prices under the great arches. "
        "A bank is on site, and a sawmill creaks just north ('mill')."),
    "monastery": (
        "A peaceful monastery where monks tend the altar — and their "
        "pockets jingle with coin. A path climbs toward the Mind Altar "
        "('altar'), and to the north the Black Knights' Fortress glowers "
        "on Ice Mountain ('fortress')."),
    "deep_wilderness": (
        "The lawless wastes stretch to the horizon. Dark warriors, giants "
        "and green dragons roam the blasted ground, an agility course "
        "sways over a ravine ('course'), the Chaos Temple squats to the "
        "north ('temple') — and a frozen chasm yawns where the God Wars "
        "rage below ('chasm')."),
    "ardougne": (
        "A grand split city. Market stalls line the square — baked goods, "
        "silk, glittering gems — pickpockets work the crowds, and paladins "
        "patrol the palace walls. Tilled farming patches sit north of the "
        "market, and hunting grounds stretch south. Baxtorian Falls "
        "thunders upriver ('falls'), the Tree Gnome Stronghold rises west "
        "('gnome'), and walled Yanille guards the far road ('yanille'). "
        "(members)"),
    "lumbridge_church": (
        "A quiet stone church where Father Aereck tends the altar and "
        "prayers are restored. Ancient yews shade the graveyard out back."),
}.items():
    ROOMS[_room]["desc"] = _desc


if __name__ == "__main__":
    main()
