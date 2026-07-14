"""Bridge to the OnlyRunes engine (../adventure.py).

Imports the game UNCHANGED and exposes small JSON-in/JSON-out helpers so the
Discord layer never touches game internals. Every function takes and returns
a serialized-player string, so state lives in the store between turns.

NOTE: the engine captures stdout globally while running a command, so callers
must never run two of these concurrently — the bot serialises them with a lock.
"""
import contextlib
import io
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import adventure as game   # noqa: E402  (path set above)

# Web mode: ANSI colour on. Boss animations arrive as sentinel blocks, which
# _deanimate() collapses to their final frame for Discord.
# Beta/dev cheats (spawn/god/maxme) stay locked — enable_beta() is NOT called.
game.enable_web()


def _deanimate(text):
    """Replace each animation sentinel block with just its final frame."""
    op, cl = game.ANIM_OPEN, game.ANIM_CLOSE
    out = []
    while True:
        i = text.find(op)
        if i < 0:
            out.append(text)
            break
        out.append(text[:i])
        j = text.find(cl, i)
        if j < 0:
            break
        try:
            frames = json.loads(text[i + len(op):j]).get("frames", [])
            if frames:
                out.append(frames[-1] + "\n")
        except Exception:
            pass
        text = text[j + len(cl):].lstrip("\n")
    return "".join(out)


def _result(p, text, killed=None, alive=True):
    return {
        "json": game.player_to_json(p),
        "text": _deanimate(text),
        "status": json.loads(game.web_status(p)),
        "actions": json.loads(game.web_room_actions(p)),
        "killed": killed,
        "alive": alive,
    }


def start(name):
    """Create a fresh character. Returns a turn dict."""
    p = game.Player((name or "Adventurer").strip()[:20] or "Adventurer")
    return _result(p, game.web_welcome(p))


def run(player_json, command):
    """Run one command. Returns a turn dict."""
    p = game.player_from_json(player_json)
    res = json.loads(game.web_command(p, command))
    return _result(p, res["text"], alive=res.get("alive", True))


def autokill(player_json, target):
    """Fight `target` and resolve the whole fight — one kill, hands-free.
    Uses interactive combat (which auto-eats), so it's stateless across the
    bot's save/reload (p.combat serialises; the transient p.auto does not).
    'killed' is True only if a monster actually went down."""
    p = game.player_from_json(player_json)
    opener = io.StringIO()
    with contextlib.redirect_stdout(opener):
        game.dispatch(p, f"fight {target}")
    if getattr(p, "combat", None) is None:      # refused / nothing to fight
        return _result(p, opener.getvalue(), killed=False, alive=p.hp > 0)
    if p.combat.get("boss"):                    # engine rule: no auto-bossing
        text = (opener.getvalue()
                + "\n(Bosses can't be auto-fought — face it yourself: "
                  "tap Attack.)")
        return _result(p, text, killed=False, alive=True)
    parts, guard = [], 0
    while getattr(p, "combat", None) is not None and p.hp > 0 and guard < 100:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            game.dispatch(p, "attack")
        parts.append(buf.getvalue())
        guard += 1
    killed = p.hp > 0 and getattr(p, "combat", None) is None
    return _result(p, parts[-1] if parts else opener.getvalue(),
                   killed=killed, alive=p.hp > 0)


def summary(player_json):
    """Lightweight card for leaderboards — no command run."""
    st = json.loads(game.web_status(game.player_from_json(player_json)))
    return {"name": st["name"], "total": st["total"],
            "combat": st["combat"], "location": st["location"]}


# ---- item transfer primitives (for the shared market / gifting) --------------
def item_lookup(name):
    """Resolve a (possibly partial) item name against the game's catalogue.
    Returns (canonical_name_or_None, suggestions)."""
    want = (name or "").strip().lower()
    if want in game.ITEMS:
        return want, []
    near = sorted(i for i in game.ITEMS if want and want in i)
    if len(near) == 1:
        return near[0], []
    return None, near[:6]


def tradeable(item):
    """Only real, valued items move between players (quest tokens don't)."""
    info = game.ITEMS.get(item)
    return bool(info and info.get("value", 0) > 0)


def take_items(player_json, item, qty):
    """Remove qty of item (or coins) from a player.
    Returns updated json, or None if they don't have enough."""
    p = game.player_from_json(player_json)
    if not p.has(item, qty):
        return None
    p.take(item, qty)
    return game.player_to_json(p)


def grant_items(player_json, item, qty):
    """Add qty of item to a player. Returns updated json."""
    p = game.player_from_json(player_json)
    p.add(item, qty)
    return game.player_to_json(p)


def count_item(player_json, item):
    return game.player_from_json(player_json).count(item)
