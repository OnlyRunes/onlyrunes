"""OnlyRunes — a Discord bot front-end for the text adventure.

Plays the exact same engine as the terminal and the browser (../adventure.py),
one command at a time, per Discord user. Slash commands drive it; the room's
actions render as buttons, 'auto' fights loop hands-free — and every player
lives in ONE shared world: a player Grand Exchange (/rs ge), gifting
(/rs send), and presence ("also here") connect them.

Setup + run: see bot/README.md.  Needs a token in ONLYRUNES_TOKEN.
No privileged intents required (slash commands + buttons only).
"""
import asyncio
import os
import re
import sys

try:
    import discord
    from discord import app_commands
except ImportError:
    sys.exit("discord.py is not installed — run: pip install -r "
             "bot/requirements.txt")

import engine
import ops
import render
import store

TOKEN = os.environ.get("ONLYRUNES_TOKEN")

# The engine captures stdout globally per command, and the shared market
# moves items between saves — so every load→engine→save is one atomic unit
# under this lock (run in a worker thread to keep the event loop responsive).
_LOCK = asyncio.Lock()
_auto_active = set()          # user ids with an autofight loop running

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def _locked(fn, *args):
    async with _LOCK:
        return await asyncio.to_thread(fn, *args)


# ---- presentation -----------------------------------------------------------
def _hp_color(st):
    ratio = st["hp"] / st["max_hp"] if st.get("max_hp") else 1.0
    if ratio <= 0.34:
        return 0xff6a6a           # red
    if ratio <= 0.67:
        return 0xffe24a           # yellow
    return 0x6ee36e               # green


def _status_embed(st, also=None):
    e = discord.Embed(color=_hp_color(st))
    e.set_author(name=f"{st['name']}  —  {st['location']}")
    e.add_field(name="❤️ Hitpoints", value=f"{st['hp']}/{st['max_hp']}")
    if st.get("prayer_max"):
        e.add_field(name="🙏 Prayer", value=f"{st['prayer']}/{st['prayer_max']}")
    e.add_field(name="⚔️ Combat", value=str(st["combat"]))
    e.add_field(name="📊 Total", value=str(st["total"]))
    e.add_field(name="🪙 Coins", value=f"{st['coins']:,}")
    e.add_field(name="🏃 Run", value=f"{st['energy']}%")
    if st.get("in_combat") and st.get("enemy"):
        en = st["enemy"]
        e.add_field(name=f"🩸 {en['name']}",
                    value=f"{en['hp']}/{en['max']} hp", inline=False)
    if also:
        e.add_field(name="🧭 Also here", value=", ".join(also), inline=False)
    flags = []
    if st.get("poison"):
        flags.append(f"☣ poison {st['poison']}")
    if st.get("frozen"):
        flags.append("❄ frozen")
    if st.get("drain"):
        flags.append(f"▼ -{st['drain']} stats")
    if flags:
        e.set_footer(text="  ·  ".join(flags))
    return e


def _make_view(owner_id, actions):
    """Buttons for the current room's actions + a utility row."""
    view = discord.ui.View(timeout=900)
    seen = set()
    for group in actions or []:
        for act in group.get("actions", []):
            cmd = act.get("cmd")
            if not cmd or cmd in seen or len(view.children) >= 20:
                continue
            seen.add(cmd)
            btn = discord.ui.Button(label=act["label"][:80],
                                    style=discord.ButtonStyle.secondary)
            btn.callback = _button_cb(owner_id, cmd)
            view.add_item(btn)
    for label, cmd in (("Look", "look"), ("Inventory", "inventory"),
                       ("Stats", "stats"), ("Map", "map")):
        if len(view.children) >= 24:
            break
        btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
        btn.callback = _button_cb(owner_id, cmd)
        view.add_item(btn)
    return view


def _button_cb(owner_id, cmd):
    async def cb(interaction):
        if interaction.user.id != owner_id:
            await interaction.response.send_message(
                "That's not your adventure — **/rs start** your own!",
                ephemeral=True)
            return
        await _turn(interaction, cmd, edit=True)
    return cb


# ---- turns ------------------------------------------------------------------
async def _reply(interaction, r, edit):
    msgs = render.chunks(r["text"])
    embed = _status_embed(r["status"], r.get("also"))
    view = _make_view(interaction.user.id, r["actions"])
    if edit:
        await interaction.response.edit_message(content=msgs[0], embed=embed,
                                                view=view)
    else:
        await interaction.response.send_message(content=msgs[0], embed=embed,
                                                view=view)
    for extra in msgs[1:4]:
        await interaction.followup.send(extra)


# 'fight cow 5' / 'fight giant rat all' → a hands-free autofight loop
_AUTO_RE = re.compile(r"^fight\s+(.+?)\s+(\d+|all)$", re.IGNORECASE)
_AUTO_CAP = 40


async def _turn(interaction, command, edit):
    uid = interaction.user.id
    m = _AUTO_RE.match(command.strip())
    if m:                                       # route to the autofight loop
        count = _AUTO_CAP if m.group(2).lower() == "all" else int(m.group(2))
        await _autofight(interaction, m.group(1).strip(),
                         min(count, _AUTO_CAP), edit)
        return
    r = await _locked(ops.turn, uid, command)
    if r is None:
        await interaction.response.send_message(
            "You have no character yet — **/rs start**.", ephemeral=True)
        return
    await _reply(interaction, r, edit)


async def _autofight(interaction, target, count, edit):
    """One kill now as the reply, then loop the rest in the background,
    editing the message per kill — paced under Discord's rate limits."""
    uid = interaction.user.id
    r = await _locked(ops.autokill, uid, target)
    if r is None:
        await interaction.response.send_message(
            "You have no character yet — **/rs start**.", ephemeral=True)
        return
    await _reply(interaction, r, edit)
    if r["killed"] and r["alive"] and count > 1:
        asyncio.create_task(_auto_loop(interaction, target, count - 1))


async def _auto_loop(interaction, target, remaining):
    uid = interaction.user.id
    if uid in _auto_active:
        return
    _auto_active.add(uid)
    try:
        for _ in range(remaining):
            await asyncio.sleep(1.7)
            r = await _locked(ops.autokill, uid, target)
            if r is None:
                break
            try:
                await interaction.edit_original_response(
                    content=render.chunks(r["text"])[0],
                    embed=_status_embed(r["status"], r.get("also")),
                    view=_make_view(uid, r["actions"]))
            except discord.HTTPException:
                break
            if not (r["killed"] and r["alive"]):
                break
    finally:
        _auto_active.discard(uid)


# ---- slash commands ---------------------------------------------------------
rs = app_commands.Group(name="rs", description="Play OnlyRunes, a RuneScape-"
                                               "inspired text adventure")


@rs.command(name="start", description="Begin a new adventure in Gielinor")
@app_commands.describe(name="your character's name (defaults to your Discord "
                            "name)")
async def rs_start(interaction: discord.Interaction, name: str = None):
    if store.exists(interaction.user.id):
        await interaction.response.send_message(
            "You already walk Gielinor — **/rs look** to continue, or "
            "**/rs delete** to start over.", ephemeral=True)
        return
    r = await _locked(ops.start, interaction.user.id,
                      name or interaction.user.display_name)
    await _reply(interaction, r, edit=False)


@rs.command(name="play", description="Do something — 'fight cow', 'chop tree', "
                                     "'travel varrock', 'bank'...")
@app_commands.describe(command="the command to run")
async def rs_play(interaction: discord.Interaction, command: str):
    await _turn(interaction, command, edit=False)


@rs.command(name="look", description="Look around where you are")
async def rs_look(interaction: discord.Interaction):
    await _turn(interaction, "look", edit=False)


@rs.command(name="autofight", description="Auto-fight a monster here, "
                                          "hands-free, until it's done")
@app_commands.describe(monster="what to fight, e.g. cow",
                       count="how many (capped by the monster's rank)")
async def rs_autofight(interaction: discord.Interaction, monster: str,
                       count: int = 5):
    await _turn(interaction, f"fight {monster} {max(1, count)}", edit=False)


@rs.command(name="send", description="Gift items to another player")
@app_commands.describe(user="who to send to", item="what to send",
                       qty="how many (default 1)")
async def rs_send(interaction: discord.Interaction, user: discord.User,
                  item: str, qty: int = 1):
    qty = max(1, min(qty, ops.MAX_QTY))
    canon, near = engine.item_lookup(item)
    if not canon:
        hint = f" Did you mean: {', '.join(near)}?" if near else ""
        await interaction.response.send_message(
            f"No item called '{item}'.{hint}", ephemeral=True)
        return
    if not engine.tradeable(canon):
        await interaction.response.send_message(
            f"{canon} can't be traded.", ephemeral=True)
        return
    code, extra = await _locked(ops.send, interaction.user.id, user.id,
                                canon, qty)
    msg = {
        "self": "Sending things to yourself is just inventory management.",
        "no_target": f"{user.display_name} has no character yet — they need "
                     "**/rs start**.",
        "no_char": "You have no character yet — **/rs start**.",
        "missing": f"You don't have {qty}x {canon} (you hold {extra}).",
        "ok": f"🎁 Sent **{qty}x {canon}** to **{user.display_name}**!",
    }[code]
    await interaction.response.send_message(msg, ephemeral=code != "ok")


ge = app_commands.Group(name="ge", parent=rs,
                        description="The player Grand Exchange — trade with "
                                    "everyone, across every server")


@ge.command(name="sell", description="List items on the player market "
                                     "(escrowed until sold or cancelled)")
@app_commands.describe(item="what to sell", qty="how many",
                       price="asking price per item, in coins")
async def ge_sell(interaction: discord.Interaction, item: str, qty: int,
                  price: int):
    qty = max(1, min(qty, ops.MAX_QTY))
    price = max(1, min(price, ops.MAX_PRICE))
    canon, near = engine.item_lookup(item)
    if not canon:
        hint = f" Did you mean: {', '.join(near)}?" if near else ""
        await interaction.response.send_message(
            f"No item called '{item}'.{hint}", ephemeral=True)
        return
    if not engine.tradeable(canon):
        await interaction.response.send_message(
            f"{canon} can't be traded.", ephemeral=True)
        return
    code, extra = await _locked(ops.ge_sell, interaction.user.id, canon, qty,
                                price)
    if code == "ok":
        await interaction.response.send_message(
            f"📋 Listed **{qty}x {canon}** at **{price:,}** coins each "
            f"(listing **#{extra}**). Buyers: `/rs ge buy listing:{extra}`")
    else:
        msg = {"no_char": "You have no character yet — **/rs start**.",
               "max_orders": f"You already have {extra} open listings — "
                             "cancel one first (`/rs ge cancel`).",
               "missing": f"You don't have {qty}x {canon} "
                          f"(you hold {extra})."}[code]
        await interaction.response.send_message(msg, ephemeral=True)


@ge.command(name="market", description="Browse the player market")
@app_commands.describe(item="filter to one item (optional)")
async def ge_market(interaction: discord.Interaction, item: str = None):
    canon = None
    if item:
        canon, near = engine.item_lookup(item)
        if not canon:
            hint = f" Did you mean: {', '.join(near)}?" if near else ""
            await interaction.response.send_message(
                f"No item called '{item}'.{hint}", ephemeral=True)
            return
    rows = await _locked(store.open_orders, canon)
    lines = [f"**#{oid}** — {it} ×{q} @ **{pr:,}** ea"
             + (f"  ·  {name}" if name else "")
             for oid, it, q, pr, name in rows]
    e = discord.Embed(title="🏪 Player Grand Exchange",
                      color=0xffce42,
                      description="\n".join(lines)
                      or "No listings yet — `/rs ge sell` something!")
    e.set_footer(text="Buy with /rs ge buy listing:<id> — one shared market "
                      "across all servers")
    await interaction.response.send_message(embed=e)


@ge.command(name="buy", description="Buy from a market listing")
@app_commands.describe(listing="the listing # from /rs ge market",
                       qty="how many (default: all of it)")
async def ge_buy(interaction: discord.Interaction, listing: int,
                 qty: int = None):
    code, extra = await _locked(ops.ge_buy, interaction.user.id, listing, qty)
    if code == "ok":
        await interaction.response.send_message(
            f"🤝 Bought **{extra['qty']}x {extra['item']}** for "
            f"**{extra['cost']:,}** coins ({extra['each']:,} ea). "
            "The seller has been paid.")
    else:
        msg = {"gone": "That listing is gone — check `/rs ge market`.",
               "own": "That's your own listing — `/rs ge cancel` it instead.",
               "no_char": "You have no character yet — **/rs start**.",
               "poor": f"That costs {extra:,} coins — you can't afford it."
               }[code]
        await interaction.response.send_message(msg, ephemeral=True)


@ge.command(name="cancel", description="Cancel your listing and take the "
                                       "items back")
@app_commands.describe(listing="the listing # to cancel")
async def ge_cancel(interaction: discord.Interaction, listing: int):
    code, o = await _locked(ops.ge_cancel, interaction.user.id, listing)
    if code == "ok":
        await interaction.response.send_message(
            f"↩️ Cancelled listing #{o['id']} — **{o['qty']}x {o['item']}** "
            "returned to your pack.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "That's not one of your listings — `/rs ge market` shows ids, "
            "and you can only cancel your own.", ephemeral=True)


@rs.command(name="top", description="Leaderboard, by total level")
async def rs_top(interaction: discord.Interaction):
    rows = await _locked(store.top, 10)
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (name, cb, total) in enumerate(rows):
        rank = medals[i] if i < 3 else f"**{i + 1}.**"
        lines.append(f"{rank}  {name} — total **{total}**, cb {cb}")
    e = discord.Embed(title="🏆 OnlyRunes — Top Adventurers", color=0xffce42,
                      description="\n".join(lines)
                      or "No adventurers yet — **/rs start**!")
    await interaction.response.send_message(embed=e)


@rs.command(name="help", description="How to play OnlyRunes on Discord")
async def rs_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**OnlyRunes** — a text adventure inspired by Old School RuneScape.\n"
        "• **/rs start** to make your character.\n"
        "• **/rs play <command>** — e.g. `fight cow`, `chop tree`, "
        "`travel varrock`, `bank`, `quests`, `goal`, `gear melee`.\n"
        "• Tap the **buttons** under each reply for common actions.\n"
        "• **/rs autofight <monster>** grinds hands-free.\n"
        "• **/rs ge market / sell / buy** — the player Grand Exchange, one "
        "market shared by every player.\n"
        "• **/rs send @friend <item>** — gift items.\n"
        "• **/rs top** — the leaderboard.\n"
        "• Progress saves automatically, one character per account. "
        "**/rs delete** starts over.",
        ephemeral=True)


@rs.command(name="delete", description="Delete your character and start over")
async def rs_delete(interaction: discord.Interaction):
    await _locked(store.delete, interaction.user.id)
    await interaction.response.send_message(
        "Your character has been laid to rest (open listings cleared). "
        "**/rs start** to begin anew.", ephemeral=True)


tree.add_command(rs)


@client.event
async def on_ready():
    await _locked(ops.backfill_meta)
    await tree.sync()
    print(f"OnlyRunes bot online as {client.user} — slash commands synced.")


def main():
    if not TOKEN:
        sys.exit("Set ONLYRUNES_TOKEN to your bot token "
                 "(see bot/README.md).")
    client.run(TOKEN)


if __name__ == "__main__":
    main()
