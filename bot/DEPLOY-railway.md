# Deploy the OnlyRunes bot on Railway

Railway keeps the bot online 24/7 and **auto-redeploys whenever `beta` is
pushed**, so it stays current with no work from you. ~$5/mo (usage-based;
starts with trial credit).

The repo already carries what Railway needs:
- `Procfile` → `worker: python bot/onlyrunes_bot.py` (runs it as a worker, not
  a web server — no port needed)
- root `requirements.txt` → installs `bot/requirements.txt` (discord.py)

## One-time setup (~10 min, all in the browser)

1. **Sign in** at <https://railway.app> with your **GitHub** account.

2. **New Project → Deploy from GitHub repo** → authorize Railway to see the
   repo → pick **OnlyRunes/onlyrunes**. It creates a service and starts a
   first build.

3. **Point it at the `beta` branch.** Open the service → **Settings →
   Source** → set the branch to **`beta`**. (The bot lives on `beta`.)

4. **Add your token.** Service → **Variables** → **New Variable**:
   - `ONLYRUNES_TOKEN` = your bot token (from the Discord *Bot* tab)
   - `ONLYRUNES_DB` = `/data/onlyrunes.db`  ← saves live on the volume below

5. **Add a volume so characters persist.** Service → **Settings → Volumes**
   (or right-click the canvas → **Volume**) → attach it to this service with
   **mount path `/data`**. Without this, saves reset on every redeploy.

6. **Deploy.** Railway builds and starts it. Open the **Deploy Logs** and look
   for `OnlyRunes bot online as … — slash commands synced.`

7. In your Discord server, run **`/rs start`** (slash commands can take a
   minute to register the first time).

## From then on

- I push new content/fixes to `beta` → Railway **auto-redeploys**. Nothing for
  you to do.
- Your `onlyrunes.db` on the `/data` volume survives redeploys and restarts.
- Crashes auto-restart.

## If something's off

- **Commands don't appear:** give it a minute; confirm the bot is in the
  server (invite used `bot` + `applications.commands` scopes) and the logs say
  "synced".
- **Bot offline / crash loop:** check Deploy Logs. Usually a missing/invalid
  `ONLYRUNES_TOKEN`.
- **Saves reset after a deploy:** the volume isn't mounted at `/data`, or
  `ONLYRUNES_DB` doesn't point at `/data/...`.
