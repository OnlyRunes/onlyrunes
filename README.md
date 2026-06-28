# OnlyRunes

A free-to-play text adventure inspired by Old School RuneScape, playable in the
terminal **or** the browser. Live at **https://onlyrunes.net**.

Explore the cities of Misthalin, Asgarnia and the Kharidian Desert, train all
15 F2P skills, fight monsters, bank loot, trade on the Grand Exchange, and
complete classic quests.

## Play in the terminal

```bash
python3 adventure.py
```

No dependencies — pure Python 3. Type `help` for commands.

## Play in the browser (locally)

The web version runs the same `adventure.py` client-side via Pyodide
(Python→WebAssembly) with an xterm.js terminal.

```bash
./build_site.sh                       # copies adventure.py into site/
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

(You can't just open the file — Pyodide needs to `fetch()` `adventure.py`, so
serve it over http.)

## Project layout

| Path | What it is |
|------|------------|
| `adventure.py` | The whole game (source of truth) — CLI + a web API |
| `site/index.html` | Browser front-end (Pyodide + xterm.js) |
| `site/adventure.py` | Generated copy for deploy (git-ignored) |
| `build_site.sh` | Copies `adventure.py` → `site/` |
| `deploy.sh` | Build + deploy to Cloudflare |
| `wrangler.jsonc` | Cloudflare Worker config (static assets) |
| `DEPLOY.md` | Hosting / domain guide |

## Deploy

Manual:

```bash
npx --yes wrangler login   # one time
./deploy.sh
```

Or connect this repo to Cloudflare for automatic deploys on `git push`.

## Saves

Browser progress auto-saves to `localStorage`. Use `save export` to download a
save file and `save import` to restore it on another device.

---

OnlyRunes is a fan-made tribute and parody. It is **not** affiliated with,
endorsed by, or connected to Jagex Ltd. or RuneScape. "RuneScape" is a
trademark of Jagex. All original code and world here are our own.
