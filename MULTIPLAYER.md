# Multiplayer design notes (back-burner)

OnlyRunes multiplayer is parked, not abandoned. This note records the plan
and — more importantly — the engine rules that keep the door open. RuneScape
itself began as a multiplayer text game (DeviousMUD, 1998); the shape fits.

## Why the engine is already close

- The whole game is one pure-stdlib Python file. The same `adventure.py`
  that runs in the browser (Pyodide) can run on any server unchanged.
- The UI seam is four string-passing functions: `web_command(player, line)`,
  `web_status`, `web_panel`, `web_room_actions`. The browser doesn't know
  it's talking to a local engine — swapping the transport for a WebSocket to
  a server running the same functions is the whole client change.
- No handler ever blocks on `input()` — the terminal prompt lives only in
  `main()`/`run()`. The engine core is strictly request → response.
- Saves are a single `serialize(p)`/`deserialize(data)` pair (versioned via
  the `"v"` field), so server-side accounts can reuse the exact format, and
  today's `save export` codes migrate characters in.

## The tiers (from the design discussion)

1. **Shared economy + presence** — a real Grand Exchange order book and
   mailbox trading behind a tiny API (Cloudflare Worker + D1), plus
   "2 other adventurers are here" heartbeats. No engine changes. Trust-based
   (the client runs the game), so friends-and-family only.
2. **The authority flip** — run `adventure.py` server-side (one process,
   dispatch serialized per player), saves + accounts in a database, browser
   becomes a dumb terminal. Kills cheating; the Pyodide build stays as the
   offline single-player mode.
3. **Playing together** — parties, shared boss instances (everyone's
   `attack` streams into one monster dict; boss turns pick targets from the
   party on a short timer), face-to-face trade escrow, duels/PvP.

## Engine rules that keep multiplayer possible

These hold today and are enforced by `tests/test_worldstate.py`:

- **The world data (`ROOMS`, `MONSTERS`, `ITEMS`, …) is immutable at
  runtime.** Content blocks may extend it at import time; nothing mutates it
  per player afterwards. Quest-story monsters (Count Draynor, the temple
  guardian, the Draugen, the experiment, the four Desert Treasure guardians)
  are a per-player *view*: the `QUEST_SPAWNS` table derives them from quest
  state, and all monster reads go through `_room_monsters(p, room)` — never
  `ROOMS[room]["monsters"]` directly. Adding a quest monster = one table row
  (no spawn calls, no kill-hook despawns, no save/load respawn code).
- **All per-player state lives on the `Player` object** and round-trips
  through `serialize`/`deserialize`. If a feature needs state, it goes on
  the player, not in a module global.
- **`dispatch(player, line)` is the atomic unit of play.** A few module
  globals (`_QUIET`, `_LAST_SPELL`) are set and read within a single
  dispatch call; that is safe only while dispatch calls never interleave.
  A future server must process commands serially (or lock per player) —
  cheap for a text game, and it preserves this invariant for free.
- **Monster instances are copies.** Combat mutates `p.combat` (a per-fight
  dict from `_new_monster`), never the `MONSTERS` template.

## What deliberately stays single-player for now

Resource nodes (trees, rocks, fishing spots), shops, and regular monsters
are per-player views by design — OSRS worlds are instanced generously, and
contention rules can wait for Tier 3. The GE's instant fills at list price
are the placeholder the Tier-1 order book would replace.
