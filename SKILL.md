---
name: zen
description: Launch a mindfulness meditation session or ambient background — 7 types, 9 themes, custom duration
user-invocable: true
---

# Zen Mode

Launch immediately. Don't ask questions — just run it.

## Default

```bash
python3 ~/Claude/.claude/scripts/zen/zen.py
```

## Parse user input

Map words to flags. Combine freely.

**Types** (`--type`):
breathing, body_scan, quotes, gratitude, visualization, metta, affirmation

**Themes** (`--theme`):
rain, ocean, forest, waterfall, river, night, thunderstorm, campfire, spring

**Duration** (`--duration`): Convert to seconds. Examples:
- `1min` → `--duration 60`
- `2min` → `--duration 120`
- `3min` → `--duration 180`
- `5min` → `--duration 300`
- `5 mins` → `--duration 300`
- `10min` → `--duration 600`

**Background** (`--background`): ambient video + sound only, no meditation UI.

**Examples:**
- `/zen` → random everything
- `/zen spring` → `--theme spring`
- `/zen affirmation` → `--type affirmation`
- `/zen 5 mins` → `--duration 300`
- `/zen spring affirmation` → `--theme spring --type affirmation`
- `/zen metta ocean 3min` → `--type metta --theme ocean --duration 180`
- `/zen background river` → `--background --theme river`
- `/zen bg campfire` → `--background --theme campfire`

## After running

Say something brief like "Session launched — check your browser."
