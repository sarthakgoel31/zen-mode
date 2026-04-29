# Zen Mode

**Guided meditation for developers, right inside your terminal.**

## What It Does

Zen Mode launches a full-featured meditation player in your browser from a single Claude Code slash command. It supports 7 meditation types, 9 nature themes, and custom durations -- all backed by real ambient videos, nature sounds, and ElevenLabs-generated voice guidance. No apps to install, no accounts to create. Just type `/zen` and breathe.

## How It Works

1. You type `/zen` (optionally with a type, theme, or duration)
2. Claude parses your input and maps words to flags (e.g., "ocean body scan 3min" becomes `--theme ocean --type body_scan --duration 180`)
3. A Python engine (`zen.py`) assembles the session -- selecting the right video loop, ambient sound, and voice clips
4. An HTML meditation player opens in your default browser with timed guidance, visual prompts, and nature footage
5. If no preferences are given, everything is randomized for a fresh experience each time

There is also a background-only mode (`/zen bg campfire`) that plays ambient video and sound without the meditation UI -- useful as a focus backdrop while working.

## Key Features

- **7 meditation types:** Breathing, body scan, quotes, gratitude, visualization, metta (loving-kindness), and affirmation
- **9 nature themes:** Rain, ocean, forest, waterfall, river, night, thunderstorm, campfire, and spring -- each with its own video loop and ambient audio
- **ElevenLabs voice guidance:** Pre-generated voice clips for each meditation type, not robotic TTS
- **Background mode:** Ambient video + sound only, no meditation overlay -- a lo-fi focus backdrop
- **Custom duration:** Set any duration in seconds or natural language ("5 mins", "10min")
- **Zero configuration:** Runs locally with no API keys, no accounts, no internet dependency after initial setup
- **Randomized defaults:** Omit any parameter and the engine picks for you

## Usage

```
/zen                          # Random type, random theme, default duration
/zen spring                   # Spring theme, random type
/zen affirmation              # Affirmation meditation, random theme
/zen 5 mins                   # 5-minute session, random everything else
/zen metta ocean 3min         # Loving-kindness meditation, ocean theme, 3 minutes
/zen background river         # Ambient river video + sound, no meditation UI
/zen bg campfire              # Shorthand for background mode
```

**Trigger phrases:** "meditation", "breathe", "mindful break", "zen mode", "calm down", "body scan"

## Project Structure

```
SKILL.md                      # Skill definition (slash command config)
scripts/zen/
  zen.py                      # Main engine -- parses flags, assembles session
  meditation.html             # Meditation player template
  background.html             # Background-only ambient template
  config.json                 # Theme and type mappings
  generate_voices.py          # ElevenLabs voice clip generator
  trigger.sh                  # Shell wrapper
  modules/                    # Python modules for session assembly
  videos/                     # Nature video loops (one per theme)
  sounds/                     # Ambient audio files
  voice/                      # Pre-generated voice guidance clips
```

## Tech Stack

- **Engine:** Python 3
- **Player:** Self-contained HTML/CSS/JS (opens in browser)
- **Voice:** ElevenLabs API (pre-generated, not called at runtime)
- **Media:** MP4 video loops + MP3/WAV ambient audio, bundled locally

---

Built with [Claude Code](https://claude.ai/code) as a slash command skill.
