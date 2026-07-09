# OnlyRunes

A text adventure inspired by Old School RuneScape, playable in the terminal
**or** the browser. Live at **https://onlyrunes.net**.

Explore the cities of Misthalin, Asgarnia and the Kharidian Desert, train your
skills, fight monsters, bank loot, trade on the Grand Exchange, unlock members
content, and complete classic quests.

## Play in the terminal

```bash
python3 adventure.py
```

No dependencies — pure Python 3. Type `help` for commands.

## Play in the browser (locally)

The web version runs the same `adventure.py` client-side via Pyodide
(Python→WebAssembly) with an xterm.js terminal.

```bash
./build_site.sh                       # builds adventure.py from src/, copies to site/
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

(You can't just open the file — Pyodide needs to `fetch()` `adventure.py`, so
serve it over http.)

## Source layout — edit `src/`, not `adventure.py`

The game ships and runs as a single module, but the source lives in ordered
fragments under **`src/`** (named by system: `30_combat.py`, `50_quests.py`,
`60_content_*` … the 2-digit prefix is the load order). `build.py`
concatenates them into `adventure.py`:

```bash
python3 build.py        # src/*.py -> adventure.py   (build_site.sh runs this too)
```

`adventure.py` is generated — don't hand-edit it (a test enforces it stays in
sync with `src/`). To add a new region, add a new `src/9N_content_*.py`.

## Project layout

| Path | What it is |
|------|------------|
| `src/*.py` | The game source, split into ordered fragments (edit here) |
| `build.py` | Concatenates `src/` → `adventure.py` |
| `adventure.py` | Generated single-file game (CLI + web API); runnable, tracked |
| `site/index.html` | Browser front-end (Pyodide + xterm.js) |
| `site/adventure.py` | Generated copy for deploy (tracked; rebuilt by `build_site.sh`) |
| `build_site.sh` | Builds `adventure.py` from `src/`, copies it → `site/` |
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

## Environments: beta vs live

| | Branch | Worker | URL |
|---|---|---|---|
| **live** | `main` | `onlyrunes` | https://onlyrunes.net |
| **beta** | `beta` | `onlyrunes-beta` | https://beta.onlyrunes.net |

The beta site shows a `BETA` badge and uses a separate save slot.

Typical flow:

```bash
git switch beta
# ...make changes, commit...
git push                 # -> auto-deploys to beta.onlyrunes.net

# happy with it? promote to live:
git switch main
git merge beta
git push                 # -> auto-deploys to onlyrunes.net
```

Manual deploys: `./deploy.sh` (live) or `./deploy.sh beta`.

## Saves

Browser progress auto-saves to `localStorage`. Use `save export` to download a
save file and `save import` to restore it on another device.

## Contributing

Issues and pull requests are welcome — bug reports, balance feedback, new
content (areas, monsters, quests, gear), and fixes. The whole game lives in
`adventure.py`; run `python3 adventure.py` to play it in the terminal.

## License

Released under the [MIT License](LICENSE) — free to use, modify, and share.

---

OnlyRunes is a fan-made tribute and parody. It is **not** affiliated with,
endorsed by, or connected to Jagex Ltd. or RuneScape. "RuneScape" is a
trademark of Jagex. All original code and world here are our own.
