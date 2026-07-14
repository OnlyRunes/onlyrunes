"""Per-user saves + the shared player market, in one SQLite file.

players: Discord user id -> serialized Player JSON, plus cheap metadata
columns (name/location/combat/total) refreshed on every save so presence
and the leaderboard never have to parse save blobs.

orders: the player-to-player Grand Exchange. Items are ESCROWED — removed
from the seller's save when listed, returned on cancel, delivered on buy.

Point ONLYRUNES_DB elsewhere to relocate the database.
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
    for col, typ in (("name", "TEXT"), ("location", "TEXT"),
                     ("combat", "INTEGER"), ("total", "INTEGER")):
        try:
            c.execute(f"ALTER TABLE players ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass                                    # column already exists
    c.execute("CREATE TABLE IF NOT EXISTS orders ("
              "id INTEGER PRIMARY KEY AUTOINCREMENT, "
              "seller_id TEXT NOT NULL, item TEXT NOT NULL, "
              "qty INTEGER NOT NULL, price INTEGER NOT NULL, "
              "created REAL DEFAULT (strftime('%s','now')))")
    return c


# ---- players ----------------------------------------------------------------
def load(discord_id):
    with _conn() as c:
        row = c.execute("SELECT data FROM players WHERE discord_id=?",
                        (str(discord_id),)).fetchone()
    return row[0] if row else None


def save(discord_id, data, meta=None):
    """meta = (name, location, combat, total) — pass it whenever you have a
    status dict handy so presence/leaderboard stay cheap."""
    with _conn() as c:
        c.execute("INSERT INTO players (discord_id, data) VALUES (?, ?) "
                  "ON CONFLICT(discord_id) DO UPDATE SET "
                  "data=excluded.data, updated=strftime('%s','now')",
                  (str(discord_id), data))
        if meta:
            c.execute("UPDATE players SET name=?, location=?, combat=?, "
                      "total=? WHERE discord_id=?",
                      (*meta, str(discord_id)))


def delete(discord_id):
    with _conn() as c:
        c.execute("DELETE FROM players WHERE discord_id=?", (str(discord_id),))
        c.execute("DELETE FROM orders WHERE seller_id=?", (str(discord_id),))


def exists(discord_id):
    return load(discord_id) is not None


def all_players():
    """Every (discord_id, data) pair — for meta backfills."""
    with _conn() as c:
        return c.execute("SELECT discord_id, data FROM players").fetchall()


def top(n=10):
    """Leaderboard rows (name, combat, total) from the meta columns."""
    with _conn() as c:
        return c.execute(
            "SELECT name, combat, total FROM players "
            "WHERE name IS NOT NULL ORDER BY total DESC LIMIT ?",
            (n,)).fetchall()


def players_at(location, exclude_id=None):
    """Character names standing in `location` (display name), minus you."""
    with _conn() as c:
        rows = c.execute(
            "SELECT name FROM players WHERE location=? AND name IS NOT NULL "
            "AND discord_id != ? ORDER BY updated DESC LIMIT 6",
            (location, str(exclude_id or ""))).fetchall()
    return [r[0] for r in rows]


def missing_meta():
    with _conn() as c:
        return c.execute("SELECT discord_id, data FROM players "
                         "WHERE name IS NULL").fetchall()


# ---- the player market --------------------------------------------------------
MAX_ORDERS_PER_SELLER = 8


def add_order(seller_id, item, qty, price):
    with _conn() as c:
        cur = c.execute("INSERT INTO orders (seller_id, item, qty, price) "
                        "VALUES (?, ?, ?, ?)",
                        (str(seller_id), item, qty, price))
        return cur.lastrowid


def get_order(order_id):
    with _conn() as c:
        row = c.execute("SELECT id, seller_id, item, qty, price FROM orders "
                        "WHERE id=?", (order_id,)).fetchone()
    return row and {"id": row[0], "seller_id": row[1], "item": row[2],
                    "qty": row[3], "price": row[4]}


def take_from_order(order_id, qty):
    """Remove qty from a listing (delete it when emptied)."""
    with _conn() as c:
        c.execute("UPDATE orders SET qty = qty - ? WHERE id=?",
                  (qty, order_id))
        c.execute("DELETE FROM orders WHERE id=? AND qty <= 0", (order_id,))


def open_orders(item=None, limit=12):
    q = ("SELECT o.id, o.item, o.qty, o.price, p.name FROM orders o "
         "LEFT JOIN players p ON p.discord_id = o.seller_id ")
    args = []
    if item:
        q += "WHERE o.item = ? "
        args.append(item)
    q += "ORDER BY o.price ASC, o.created ASC LIMIT ?"
    args.append(limit)
    with _conn() as c:
        return c.execute(q, args).fetchall()


def orders_by(seller_id):
    with _conn() as c:
        return c.execute("SELECT id, item, qty, price FROM orders "
                         "WHERE seller_id=? ORDER BY created",
                         (str(seller_id),)).fetchall()
