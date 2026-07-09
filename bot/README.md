# OnlyRunes — Discord bot

Play the OnlyRunes text adventure inside Discord. It runs the **exact same
engine** as the terminal and the browser (`../adventure.py`, imported
unchanged) — this folder is just a Discord transport over the game's existing
per-command API. Each Discord user gets one character, saved automatically.

```
Discord slash command / button
        → load that user's Player (SQLite, keyed by Discord id)
        → adventure.web_command(player, text)      # the unchanged engine
        → save the Player
        → reply (ANSI-in-a-code-block + action buttons)
```

## What works

- `/rs start [name]` — create a character (defaults to your Discord name).
- `/rs play <command>` — run any game command: `fight cow`, `chop tree`,
  `travel varrock`, `bank`, `quests`, `goal`, `gear melee`, …
- `/rs look`, `/rs help`, `/rs delete`.
- **Buttons** under every reply: the room's actions (Attack, Chop, Bank,
  Talk…) plus Look / Inventory / Stats / Map. Combat is tapping **Attack**.
- Rich colour via Discord `ansi` code blocks (the game's palette is mapped
  down to Discord's supported colours); ASCII art and HP bars render as-is.
- Boss animations degrade to their final frame automatically.

Dev/cheat commands (`spawn`, `god`, `maxme`) are **disabled** — the bot never
calls `enable_beta()`, so they're inert for public play.

## Setup

1. **Create the bot application**
   - Go to <https://discord.com/developers/applications> → *New Application*.
   - *Bot* tab → *Add Bot* → copy the **token**.
   - No privileged intents are required (this bot uses only slash commands and
     buttons). Leave Message Content Intent **off**.

2. **Invite it to your server**
   - *OAuth2 → URL Generator*: scopes `bot` + `applications.commands`;
     bot permissions: *Send Messages*, *Embed Links*, *Use Slash Commands*.
   - Open the generated URL and add it to a server.

3. **Install + run**
   ```bash
   cd bot
   pip install -r requirements.txt
   export ONLYRUNES_TOKEN="your-bot-token"      # or set it in your shell/host
   python onlyrunes_bot.py
   ```
   On first run it syncs the slash commands (can take a minute to appear).
   Try `/rs start` in any channel the bot can see.

## Hosting

The bot is a long-running process (unlike the static website). Anything that
keeps a Python process alive works: a small VPS, Fly.io, Railway, a Raspberry
Pi, etc. Point `ONLYRUNES_DB` at a persistent path to keep saves across
restarts (defaults to `bot/onlyrunes.db`).

## Notes / limits

- **One command at a time.** The engine captures stdout globally per command,
  so the bot serialises engine calls with a lock. Fine for a hobby bot; to
  scale to many concurrent players you'd run multiple worker processes.
- **Message length.** Long output (bank, help) is split into multiple messages
  under Discord's 2000-char cap.
- **Shared world / trading / group bossing** aren't here yet — this is
  single-player-per-user for now. Because the engine runs inside the bot
  process, a Discord bot is actually the most natural home for a shared world
  later (see `../MULTIPLAYER.md`).
