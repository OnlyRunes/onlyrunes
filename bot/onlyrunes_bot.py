"""OnlyRunes — a Discord bot front-end for the text adventure.

Plays the exact same engine as the terminal and the browser (../adventure.py),
one command at a time, per Discord user. Slash commands drive it; the room's
actions render as buttons so most play is tapping (combat = tap Attack), and
'auto' fights loop hands-free.

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
import render
import store

TOKEN = os.environ.get("ONLYRUNES_TOKEN")

# The engine captures stdout globally per command, so only one may run at a
# time. This lock + to_thread keeps the event loop responsive and safe.
_LOCK = asyncio.Lock()
_auto_active = set()          # user ids with an autofight loop running

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def _engine(fn, *args):
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


def _status_embed(st):
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
    embed = _status_embed(r["status"])
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
    pj = store.load(uid)
    if pj is None:
        await interaction.response.send_message(
            "You have no character yet — **/rs start**.", ephemeral=True)
        return
    m = _AUTO_RE.match(command.strip())
    if m:                                           # route to the autofight loop
        count = _AUTO_CAP if m.group(2).lower() == "all" else int(m.group(2))
        await _autofight(interaction, m.group(1).strip(),
                         min(count, _AUTO_CAP), edit)
        return
    r = await _engine(engine.run, pj, command)
    store.save(uid, r["json"])
    await _reply(interaction, r, edit)


async def _autofight(interaction, target, count, edit):
    """One kill now as the reply, then loop the rest in the background,
    editing the message per kill — paced under Discord's rate limits."""
    uid = interaction.user.id
    r = await _engine(engine.autokill, store.load(uid), target)
    store.save(uid, r["json"])
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
            r = await _engine(engine.autokill, store.load(uid), target)
            store.save(uid, r["json"])
            try:
                await interaction.edit_original_response(
                    content=render.chunks(r["text"])[0],
                    embed=_status_embed(r["status"]),
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
    r = await _engine(engine.start, name or interaction.user.display_name)
    store.save(interaction.user.id, r["json"])
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


@rs.command(name="top", description="Server leaderboard, by total level")
async def rs_top(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    rows = []
    for _did, data in store.all_players():
        try:
            s = await _engine(engine.summary, data)
            rows.append((s["total"], s["combat"], s["name"]))
        except Exception:
            continue
    rows.sort(reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (total, cb, name) in enumerate(rows[:10]):
        rank = medals[i] if i < 3 else f"**{i + 1}.**"
        lines.append(f"{rank}  {name} — total **{total}**, cb {cb}")
    e = discord.Embed(title="🏆 OnlyRunes — Top Adventurers", color=0xffce42,
                      description="\n".join(lines)
                      or "No adventurers yet — **/rs start**!")
    await interaction.followup.send(embed=e)


@rs.command(name="help", description="How to play OnlyRunes on Discord")
async def rs_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**OnlyRunes** — a text adventure inspired by Old School RuneScape.\n"
        "• **/rs start** to make your character.\n"
        "• **/rs play <command>** — e.g. `fight cow`, `chop tree`, "
        "`travel varrock`, `bank`, `quests`, `goal`, `gear melee`.\n"
        "• Tap the **buttons** under each reply for common actions "
        "(combat is just tapping **Attack**).\n"
        "• **/rs autofight <monster>** grinds hands-free.\n"
        "• **/rs top** shows the server leaderboard.\n"
        "• Progress saves automatically, one character per account. "
        "**/rs delete** starts over.",
        ephemeral=True)


@rs.command(name="delete", description="Delete your character and start over")
async def rs_delete(interaction: discord.Interaction):
    store.delete(interaction.user.id)
    await interaction.response.send_message(
        "Your character has been laid to rest. **/rs start** to begin anew.",
        ephemeral=True)


tree.add_command(rs)


@client.event
async def on_ready():
    await tree.sync()
    print(f"OnlyRunes bot online as {client.user} — slash commands synced.")


def main():
    if not TOKEN:
        sys.exit("Set ONLYRUNES_TOKEN to your bot token "
                 "(see bot/README.md).")
    client.run(TOKEN)


if __name__ == "__main__":
    main()
