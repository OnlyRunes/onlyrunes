"""Per-user save store: Discord user id -> serialized Player JSON.

A single SQLite file (stdlib, no deps). Point ONLYRUNES_DB elsewhere to
relocate it. One character per Discord account.
"""
import os
import sqlite3

_DB = os.environ.get(
    "ONLYRUNES_DB", os.path.join(os.path.dirname(__file__), "onlyrunes.db"))


def _conn():
    c = sqlite3.connect(_DB)
    c.execute("CREATE TABLE IF NOT EXISTS players ("
              "discord_id TEXT PRIMARY KEY, data TEXT NOT NULL, "
              "updated REAL DEFAULT (strftime('%s','now')))")
    return c


def load(discord_id):
    with _conn() as c:
        row = c.execute("SELECT data FROM players WHERE discord_id=?",
                        (str(discord_id),)).fetchone()
    return row[0] if row else None


def save(discord_id, data):
    with _conn() as c:
        c.execute("INSERT INTO players (discord_id, data) VALUES (?, ?) "
                  "ON CONFLICT(discord_id) DO UPDATE SET "
                  "data=excluded.data, updated=strftime('%s','now')",
                  (str(discord_id), data))


def delete(discord_id):
    with _conn() as c:
        c.execute("DELETE FROM players WHERE discord_id=?", (str(discord_id),))


def exists(discord_id):
    return load(discord_id) is not None


def all_players():
    """Every (discord_id, data) pair — for the leaderboard."""
    with _conn() as c:
        return c.execute("SELECT discord_id, data FROM players").fetchall()
