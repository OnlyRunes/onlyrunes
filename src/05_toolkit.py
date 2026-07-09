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
XP_RATE = 5          # global XP multiplier (5x) — faster progression

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


