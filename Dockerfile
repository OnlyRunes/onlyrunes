# Container image for hosting the OnlyRunes Discord bot (Railway / Fly / any
# Docker host). Deterministic build — no language auto-detection.
# The game engine (adventure.py) is pure stdlib; only the bot's discord.py
# transport is installed here.
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r bot/requirements.txt

# Runs the Discord bot. Set ONLYRUNES_TOKEN (required) and, for persistent
# saves, mount a volume and set ONLYRUNES_DB=/data/onlyrunes.db.
CMD ["python", "bot/onlyrunes_bot.py"]
