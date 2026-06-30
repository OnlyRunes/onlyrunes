# Deploying OnlyRunes to the web

The game runs **entirely in the browser** (Python compiled to WebAssembly via
Pyodide + an xterm.js terminal). There is **no server to run** — you just host
the static `site/` folder. Free hosting + free HTTPS.

## Sites & domains (current setup)

Hosted on **Cloudflare Workers** (static assets), configured in `wrangler.jsonc`:

| Worker | Serves | Domain | Deploy |
|---|---|---|---|
| `onlyrunes-site` | `landing/` | `onlyrunes.net` | `npx wrangler deploy --env landing` |
| `onlyrunes-beta` | `site/` (game) | `beta.onlyrunes.net` | `npx wrangler deploy --env beta` |
| `onlyrunes` | `site/` (game) | `play.onlyrunes.net` *(later)* | `npx wrangler deploy` |

Only the **landing page** and the **beta** are advertised right now. The live
game worker (`onlyrunes`) stays on its `*.workers.dev` URL until
`play.onlyrunes.net` is wired up later.

Attach each domain to its worker in the Cloudflare dashboard: Workers &amp; Pages
→ the worker → Settings → Domains &amp; Routes → Add → Custom domain. A given
domain can only be attached to one worker at a time.

## 1. Build

```bash
./build_site.sh
```

This copies the latest `adventure.py` into `site/`. The deployable folder is
`site/` and contains exactly two files: `index.html` and `adventure.py`.

## 2. Preview locally

Pyodide needs to `fetch()` `adventure.py`, so you can't just double-click the
HTML (file:// blocks fetch). Serve it:

```bash
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

## 3. Deploy (recommended: Cloudflare Pages)

You'll create a free account and run one login command; I (Claude) can run the
deploy from your machine after that.

```bash
npm install -g wrangler         # one-time
wrangler login                  # opens browser, you approve
wrangler pages deploy site --project-name onlyrunes
```

Wrangler prints a `*.pages.dev` URL — the game is already live there.

### Attach the domain (onlyrunes.net)
- If you registered the domain **at Cloudflare**: Pages → your project → Custom
  domains → "Set up a custom domain" → `onlyrunes.net` (and `www`). DNS is
  configured automatically. HTTPS is automatic.
- If registered **elsewhere** (Porkbun/Namecheap): add the custom domain in
  Pages, then at your registrar create the DNS records Cloudflare shows you
  (a `CNAME` for `www` → `onlyrunes.pages.dev`, and Cloudflare's instructions
  for the apex). Propagation: minutes to a couple hours.

## Alternative: Netlify (drag-and-drop, no CLI)
1. Go to app.netlify.com → "Add new site" → "Deploy manually".
2. Drag the `site/` folder onto the page. You get a live `*.netlify.app` URL.
3. Site settings → Domain management → add `onlyrunes.net`, then follow the DNS
   instructions at your registrar.

## Notes
- First visit downloads ~6 MB of Pyodide (cached afterward) — a few seconds.
- Saves live in each player's browser (`localStorage`), per device.
- It's single-player per browser; there's no shared world (that would need the
  server option).
