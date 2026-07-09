"""Translate the engine's rich ANSI output into Discord-safe ANSI and chunk
it under Discord's 2000-char message limit.

Discord ```ansi``` code blocks understand only a small SGR subset — 0/1/4
and 30-37 / 40-47.  The game paints with bright colours (90-97) and 256-colour
codes (gold, orange, teal, ...), so every sequence is mapped down to the
nearest supported code (or dropped).  The ASCII art and HP bars render fine
inside the monospace block regardless.
"""
import re

_ESC = re.compile(r"\033\[([0-9;]*)m")

# engine SGR body -> Discord-safe body ("" drops the whole sequence)
_SIMPLE = {
    "": "0", "0": "0", "1": "1", "4": "4",
    "2": "", "3": "",                       # dim / italic: unsupported
    "30": "30", "31": "31", "32": "32", "33": "33",
    "34": "34", "35": "35", "36": "36", "37": "37",
    "90": "30",                             # grey
    "91": "31", "92": "32", "93": "33", "94": "34",
    "95": "35", "96": "36", "97": "37",     # bright -> base
}
# 256-colour (38;5;N) -> nearest Discord base foreground
_EXT = {"220": "33", "208": "33", "130": "31", "141": "35",
        "154": "32", "44": "36"}

FENCE_ANSI = "```ansi\n"
FENCE_PLAIN = "```\n"
CLOSE = "\n```"
LIMIT = 1900          # headroom under Discord's hard 2000


def _map(body):
    if body.startswith("38;5;"):
        return _EXT.get(body.split(";")[-1], "37")
    if body.startswith("48;5;"):
        return ""                          # extended background: drop
    return _SIMPLE.get(body, "")


def to_discord_ansi(text):
    def repl(m):
        mapped = _map(m.group(1))
        return f"\033[{mapped}m" if mapped != "" else ""
    return _ESC.sub(repl, text)


def strip(text):
    return _ESC.sub("", text)


def chunks(text, color=True):
    """Split rendered output into a list of fenced Discord code-block messages."""
    text = (text or "").rstrip("\n") or "(nothing happens)"
    body = to_discord_ansi(text) if color else strip(text)
    fence = FENCE_ANSI if color else FENCE_PLAIN
    budget = LIMIT - len(fence) - len(CLOSE)
    out, cur = [], ""

    def flush():
        nonlocal cur
        if cur:
            out.append(fence + cur + CLOSE)
            cur = ""

    for line in body.split("\n"):
        while len(line) > budget:            # hard-wrap a pathological line
            flush()
            out.append(fence + line[:budget] + CLOSE)
            line = line[budget:]
        if len(cur) + len(line) + 1 > budget:
            flush()
            cur = line
        else:
            cur = (cur + "\n" + line) if cur else line
    flush()
    return out
