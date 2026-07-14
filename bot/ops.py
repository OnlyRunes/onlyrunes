"""Atomic game operations for the bot: every function is one complete
load → engine → save unit. The Discord layer runs each of these inside a
single lock, so cross-player moves (market buys, gifts) can never race a
concurrent turn's read-modify-write.

No discord imports here — this module is plain store+engine logic, which
also makes the whole shared-world flow testable headlessly.
"""
import engine
import store

MAX_QTY, MAX_PRICE = 10_000, 100_000_000


def _meta(st):
    return (st["name"], st["location"], st["combat"], st["total"])


def start(uid, name):
    r = engine.start(name)
    store.save(uid, r["json"], _meta(r["status"]))
    r["also"] = store.players_at(r["status"]["location"], uid)
    return r


def turn(uid, command):
    pj = store.load(uid)
    if pj is None:
        return None
    r = engine.run(pj, command)
    store.save(uid, r["json"], _meta(r["status"]))
    r["also"] = store.players_at(r["status"]["location"], uid)
    return r


def autokill(uid, target):
    pj = store.load(uid)
    if pj is None:
        return None
    r = engine.autokill(pj, target)
    store.save(uid, r["json"], _meta(r["status"]))
    r["also"] = store.players_at(r["status"]["location"], uid)
    return r


def ge_sell(uid, item, qty, price):
    pj = store.load(uid)
    if pj is None:
        return "no_char", None
    if len(store.orders_by(uid)) >= store.MAX_ORDERS_PER_SELLER:
        return "max_orders", store.MAX_ORDERS_PER_SELLER
    taken = engine.take_items(pj, item, qty)
    if taken is None:
        return "missing", engine.count_item(pj, item)
    store.save(uid, taken)                     # items now escrowed
    oid = store.add_order(uid, item, qty, price)
    return "ok", oid


def ge_buy(uid, order_id, qty):
    o = store.get_order(order_id)
    if not o:
        return "gone", None
    if str(o["seller_id"]) == str(uid):
        return "own", None
    qty = max(1, min(qty or o["qty"], o["qty"]))
    cost = qty * o["price"]
    pj = store.load(uid)
    if pj is None:
        return "no_char", None
    paid = engine.take_items(pj, "coins", cost)
    if paid is None:
        return "poor", cost
    store.save(uid, engine.grant_items(paid, o["item"], qty))
    store.take_from_order(order_id, qty)
    seller = store.load(o["seller_id"])
    if seller is not None:                     # seller may have deleted
        store.save(o["seller_id"], engine.grant_items(seller, "coins", cost))
    return "ok", {"item": o["item"], "qty": qty, "cost": cost,
                  "each": o["price"]}


def ge_cancel(uid, order_id):
    o = store.get_order(order_id)
    if not o or str(o["seller_id"]) != str(uid):
        return "not_yours", None
    store.take_from_order(order_id, o["qty"])
    pj = store.load(uid)
    if pj is not None:
        store.save(uid, engine.grant_items(pj, o["item"], o["qty"]))
    return "ok", o


def send(uid, target_id, item, qty):
    if str(uid) == str(target_id):
        return "self", None
    tgt = store.load(target_id)
    if tgt is None:
        return "no_target", None
    pj = store.load(uid)
    if pj is None:
        return "no_char", None
    taken = engine.take_items(pj, item, qty)
    if taken is None:
        return "missing", engine.count_item(pj, item)
    store.save(uid, taken)
    store.save(target_id, engine.grant_items(tgt, item, qty))
    return "ok", None


def backfill_meta():
    for did, data in store.missing_meta():
        try:
            s = engine.summary(data)
            store.save(did, data, (s["name"], s["location"], s["combat"],
                                   s["total"]))
        except Exception:
            continue
