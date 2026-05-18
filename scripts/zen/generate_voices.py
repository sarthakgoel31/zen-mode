#!/usr/bin/env python3
"""Generate natural human voice lines for Zen Mode using ElevenLabs.

Uses ElevenLabs free tier (10K chars/month, genuinely human voices).

Setup:
  1. Sign up at elevenlabs.io (free)
  2. Get API key: Profile icon → Profile + API key → Copy
  3. Run: ELEVENLABS_API_KEY=your_key python3 generate_voices.py
     Or put the key in zen/config.json under "elevenlabs_api_key"

Voice: Custom voice ID wdymxIQkYn7MJCYCQF2Q (serene, deep, calm female)
"""

import json
import os
import sys
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(SCRIPT_DIR, "voice")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

VOICE_ID = "wdymxIQkYn7MJCYCQF2Q"
MODEL_ID = "eleven_multilingual_v2"
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

PHRASES = {
    # Breathing
    "intro_breathing": "Close your eyes. Let's begin with some gentle breathing.",
    "breathe_in": "Breathe in.",
    "hold": "Hold.",
    "breathe_out": "And breathe out.",
    "rest": "Rest.",

    # Body scan
    "intro_body_scan": "Close your eyes. We'll move gently through your body.",
    "scan_head": "Bring your awareness to the top of your head. Let your forehead soften.",
    "scan_face": "Relax the muscles around your eyes. Unclench your jaw.",
    "scan_shoulders": "Drop your shoulders away from your ears. Let the weight release.",
    "scan_hands": "Notice your hands. Let any tension dissolve.",
    "scan_chest": "Feel your chest rise and fall with each breath.",
    "scan_belly": "Soften your belly completely. There's nothing to hold.",
    "scan_feet": "Feel your connection to the ground. You are supported.",

    # Quotes
    "intro_quotes": "Close your eyes, and listen.",
    "reflect": "Sit with that for a moment.",

    # Shared
    "outro": "Gently open your eyes. Well done.",
    "transition": "Now, gently shift your attention.",
}


def get_api_key():
    """Get ElevenLabs API key from env, config, or prompt."""
    # 1. Environment variable
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key

    # 2. Config file
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        key = config.get("elevenlabs_api_key")
        if key:
            return key
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 3. Prompt
    key = input("Paste your ElevenLabs API key: ").strip()
    if key:
        # Save to config for future use
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        config["elevenlabs_api_key"] = key
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        print(f"  saved key to {CONFIG_PATH}")
        return key

    return None


def generate_voice(api_key, name, text, output_path):
    """Generate a single voice line via ElevenLabs API."""
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.4,
            "use_speaker_boost": True,
        },
    }

    resp = requests.post(
        f"{API_URL}?output_format=mp3_44100_128",
        json=payload,
        headers=headers,
        timeout=30,
    )

    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return False


def main():
    api_key = get_api_key()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    os.makedirs(VOICE_DIR, exist_ok=True)

    total_chars = sum(len(t) for t in PHRASES.values())
    print(f"Generating {len(PHRASES)} voice lines ({total_chars} chars)")
    print(f"Voice: {VOICE_ID} | Model: {MODEL_ID}\n")

    success = 0
    for name, text in PHRASES.items():
        path = os.path.join(VOICE_DIR, f"{name}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"  skip  {name} (exists)")
            success += 1
            continue

        print(f"  gen   {name}...", end=" ", flush=True)
        if generate_voice(api_key, name, text, path):
            size_kb = os.path.getsize(path) / 1024
            print(f"ok ({size_kb:.0f}KB)")
            success += 1
        else:
            print("failed")

    print(f"\nDone! {success}/{len(PHRASES)} voice files in {VOICE_DIR}/")
    if success > 0:
        print("Run zen.py to hear them in the meditation page.")


if __name__ == "__main__":
    main()
