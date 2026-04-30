# Zen Mode

Guided meditation for developers — 7 types, 9 themes, real ambient videos, ElevenLabs voice generation.

## Why

Developers don't take breaks until they burn out. Zen Mode makes mindfulness zero-friction: type `/zen` in the terminal, a full-screen meditation player opens with nature video, ambient sound, and human-quality voice guidance. No app to open, no subscription, no signup. Auto-triggers on idle with probability gating.

## How

```
/zen                          # Random type, random theme, default duration
/zen spring                   # Spring theme, random type
/zen affirmation              # Affirmation meditation, random theme
/zen 5 mins                   # 5-minute session, random everything else
/zen metta ocean 3min         # Loving-kindness, ocean theme, 3 minutes
/zen bg campfire              # Background ambient — focus backdrop
```

1. Type `/zen` (optionally with type, theme, or duration)
2. Python engine assembles the session — selects video loop, ambient sound, voice clips
3. Full-screen HTML meditation player opens in browser with timed guidance
4. Session ends with gentle fade — back to work

## Features

| Feature | Description |
|---|---|
| 7 Meditation Types | Breathing, body scan, quotes, gratitude, visualization, metta (loving-kindness), affirmation |
| 9 Nature Themes | Rain, ocean, forest, waterfall, river, night, thunderstorm, campfire, spring |
| ElevenLabs Voice | Pre-generated human-quality voice clips for each meditation type |
| Background Mode | Ambient video + sound only — lo-fi focus backdrop while working |
| Custom Duration | Any duration in seconds or natural language ("5 mins", "10min") |
| Auto-Trigger | Fires on idle (45s threshold, 12% probability, 25min cooldown) |
| Breathing Patterns | Box (4-4-4-4), Relaxing (4-7-8), Coherent (6-6) |
| Apple Watch | Heart rate monitoring to detect stress and trigger sessions |
| Zero Config | Runs locally, no API keys at runtime, no internet after setup |

## Tech

| Component | Technology |
|---|---|
| Engine | Python 3 |
| Player | Self-contained HTML/CSS/JS (opens in browser) |
| Voice | ElevenLabs TTS API (pre-generated, not called at runtime) |
| Media | MP4 video loops + MP3/WAV ambient audio, bundled locally |
| Config | JSON (trigger probability, breathing patterns, cooldown) |
| Integration | Claude Code skill (`/zen`), hook-triggered |

## Architecture

```
zen/
  zen.py                  # Main engine — parses flags, assembles session
  meditation.html         # Full-screen meditation player template
  background.html         # Background-only ambient template
  config.json             # Theme mappings, breathing patterns, trigger config
  generate_voices.py      # ElevenLabs voice clip generator
  trigger.sh              # Shell wrapper for auto-trigger
  modules/                # Python modules for session assembly
  videos/                 # Nature video loops (one per theme)
  sounds/                 # Ambient audio files
  voice/                  # Pre-generated voice guidance clips
```

## Status

| Item | Status |
|---|---|
| Browser meditation player | Complete |
| Terminal mode | Complete |
| Audio-only mode | Complete |
| Background mode | Complete |
| 9 nature themes | Complete |
| 7 meditation types | Complete |
| ElevenLabs voice | Complete |
| Auto-trigger (idle) | Complete |
| Apple Watch biometrics | Complete |
| Breathing patterns | Box, 4-7-8, Coherent |

---

Built with [Claude Code](https://claude.ai/code).
