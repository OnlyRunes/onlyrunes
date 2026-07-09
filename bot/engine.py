"""Bridge to the OnlyRunes engine (../adventure.py).

Imports the game UNCHANGED and exposes small JSON-in/JSON-out helpers so the
Discord layer never touches game internals. Every function takes and returns
a serialized-player string, so state lives in the store between turns.

NOTE: the engine captures stdout globally while running a command, so callers
must never run two of these concurrently — the bot serialises them with a lock.
"""
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import adventure as game   # noqa: E402  (path set above)

# Emit ANSI so we can colour Discord output; keep WEB False so animations fall
# back to their final frame (and no browser sentinel blocks leak through).
game.COLOR = True
# Beta/dev cheats (spawn/god/maxme) stay locked — enable_beta() is NOT called.


def _snapshot(p):
    return (game.player_to_json(p),
            json.loads(game.web_status(p)),
            json.loads(game.web_room_actions(p)))


def start(name):
    """Create a fresh character. Returns (json, welcome_text, status, actions)."""
    p = game.Player((name or "Adventurer").strip()[:20] or "Adventurer")
    text = game.web_welcome(p)
    j, status, actions = _snapshot(p)
    return j, text, status, actions


def run(player_json, command):
    """Run one command. Returns (json, text, status, actions)."""
    p = game.player_from_json(player_json)
    res = json.loads(game.web_command(p, command))
    j, status, actions = _snapshot(p)
    return j, res["text"], status, actions
