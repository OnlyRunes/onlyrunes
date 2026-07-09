"""OnlyRunes — a Discord bot front-end for the text adventure.

Plays the exact same engine as the terminal and the browser (../adventure.py),
one command at a time, per Discord user. Slash commands drive it; the room's
actions render as buttons so most play is tapping (combat = tap Attack).

Setup + run: see bot/README.md.  Needs a token in ONLYRUNES_TOKEN.
No privileged intents required (slash commands + buttons only).
"""
import asyncio
import os
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

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def _engine(fn, *args):
    async with _LOCK:
        return await asyncio.to_thread(fn, *args)


def _status_line(st):
    bits = [f"❤️ {st['hp']}/{st['max_hp']}"]
    if st.get("prayer_max"):
        bits.append(f"🙏 {st['prayer']}/{st['prayer_max']}")
    bits.append(f"🏃 {st['energy']}")
    bits.append(f"📍 {st['location']}")
    bits.append(f"⚔️ {st['combat']}")
    if st.get("in_combat") and st.get("enemy"):
        e = st["enemy"]
        bits.append(f"🩸 {e['name']} {e['hp']}/{e['max']}")
    return "  ·  ".join(bits)


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


async def _turn(interaction, command, edit):
    pj = store.load(interaction.user.id)
    if pj is None:
        await interaction.response.send_message(
            "You have no character yet — **/rs start**.", ephemeral=True)
        return
    new_json, text, status, actions = await _engine(engine.run, pj, command)
    store.save(interaction.user.id, new_json)
    await _reply(interaction, text, status, actions, edit)


async def _reply(interaction, text, status, actions, edit):
    msgs = render.chunks(text)
    view = _make_view(interaction.user.id, actions)
    content = _status_line(status) + "\n" + msgs[0]
    if len(content) > 2000:                       # status pushed it over: drop it
        content = msgs[0]
    if edit:
        await interaction.response.edit_message(content=content, view=view)
    else:
        await interaction.response.send_message(content=content, view=view)
    for extra in msgs[1:4]:                        # cap trailing pages
        await interaction.followup.send(extra)


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
    nm = name or interaction.user.display_name
    new_json, text, status, actions = await _engine(engine.start, nm)
    store.save(interaction.user.id, new_json)
    await _reply(interaction, text, status, actions, edit=False)


@rs.command(name="play", description="Do something — 'fight cow', 'chop tree', "
                                     "'travel varrock', 'bank'...")
@app_commands.describe(command="the command to run")
async def rs_play(interaction: discord.Interaction, command: str):
    await _turn(interaction, command, edit=False)


@rs.command(name="look", description="Look around where you are")
async def rs_look(interaction: discord.Interaction):
    await _turn(interaction, "look", edit=False)


@rs.command(name="help", description="How to play OnlyRunes on Discord")
async def rs_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**OnlyRunes** — a text adventure inspired by Old School RuneScape.\n"
        "• **/rs start** to make your character.\n"
        "• **/rs play <command>** to act — e.g. `fight cow`, `chop tree`, "
        "`travel varrock`, `bank`, `quests`, `goal`.\n"
        "• Tap the **buttons** under each reply for the common actions "
        "(combat is just tapping **Attack**).\n"
        "• Your progress saves automatically, one character per account.\n"
        "• **/rs delete** wipes your character to start fresh.",
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
