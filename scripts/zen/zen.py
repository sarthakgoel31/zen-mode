#!/usr/bin/env python3
"""Zen Mode — Mindfulness meditation engine.

Browser mode (default):  Beautiful full-screen page with nature sounds,
                         canvas animations, and human voice guidance.
Visual mode:             Terminal experience with breathing animations.
Audio mode:              Voice-guided session with ambient sound (eyes-closed).

Usage:
    python3 zen.py                                 # Browser mode (default)
    python3 zen.py --type breathing --duration 120  # Specific exercise
    python3 zen.py --theme rain                     # Specific nature theme
    python3 zen.py --visual                         # Terminal mode
    python3 zen.py --audio-only                     # Audio-only mode
    python3 zen.py --auto                           # Auto-trigger (browser)
"""

import argparse
import base64
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import webbrowser  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
HTML_PATH = os.path.join(SCRIPT_DIR, "meditation.html")
VOICE_DIR = os.path.join(SCRIPT_DIR, "voice")
VIDEO_DIR = os.path.join(SCRIPT_DIR, "videos")
SOUND_DIR = os.path.join(SCRIPT_DIR, "sounds")

THEMES = ["rain", "ocean", "forest", "waterfall", "river", "night", "thunderstorm", "campfire", "spring"]
THEME_VIDEOS = {
    "rain": "rain.mp4", "ocean": "ocean.mp4", "forest": "forest.mp4",
    "waterfall": "waterfall.mp4", "river": "river.mp4", "night": "night.mp4",
    "thunderstorm": "thunderstorm.mp4", "campfire": "campfire.mp4", "spring": "spring.mp4",
}
THEME_SOUNDS = {
    "rain": "rain.mp3", "ocean": "ocean.mp3", "forest": "forest.mp3",
    "waterfall": "waterfall.mp3", "river": "river.mp3", "night": "night.mp3",
    "thunderstorm": "thunderstorm.mp3", "campfire": "campfire.mp3", "spring": "spring.mp3",
}
BG_HTML_PATH = os.path.join(SCRIPT_DIR, "background.html")
TYPES = ["breathing", "body_scan", "quotes", "gratitude", "visualization", "metta", "affirmation"]


def load_config():
    """Load configuration from config.json with fallback defaults."""
    defaults = {
        "trigger_probability": 12,
        "idle_threshold_seconds": 45,
        "cooldown_minutes": 25,
        "min_duration_seconds": 60,
        "max_duration_seconds": 180,
        "sound_enabled": True,
        "voice_enabled": True,
        "voice_name": "Samantha",
        "voice_rate": 130,
        "preferred_types": ["breathing", "body_scan", "quotes"],
    }
    try:
        with open(CONFIG_PATH) as f:
            user_config = json.load(f)
        defaults.update(user_config)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


# ---------------------------------------------------------------------------
# Browser session (default) — beautiful HTML page with nature sounds + voice
# ---------------------------------------------------------------------------

def _build_voice_data():
    """Read voice MP3 files and encode as base64 data URIs."""
    voice_data = {}
    if not os.path.isdir(VOICE_DIR):
        return voice_data

    for fname in os.listdir(VOICE_DIR):
        if not fname.endswith(".mp3"):
            continue
        name = fname[:-4]  # strip .mp3
        path = os.path.join(VOICE_DIR, fname)
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            voice_data[name] = f"data:audio/mpeg;base64,{b64}"
        except OSError:
            pass

    return voice_data


def run_browser_session(config, exercise_type=None, duration=None, theme=None):
    """Open the meditation HTML page via a local HTTP server.

    Serves from SCRIPT_DIR so Chrome can load video audio (file:// blocks JS audio).
    Voice files are embedded as base64 data URIs in the HTML.
    """
    import socket

    if theme is None:
        theme = random.choice(THEMES)
    if exercise_type is None:
        exercise_type = random.choice(config.get("preferred_types", TYPES))
    if duration is None:
        duration = random.randint(
            config.get("min_duration_seconds", 60),
            config.get("max_duration_seconds", 180),
        )

    # Build voice data from MP3 files (embedded as base64)
    voice_data = _build_voice_data()

    # Video path as relative URL (served by local HTTP server)
    video_file = THEME_VIDEOS.get(theme, "")
    video_rel = f"videos/{video_file}" if os.path.exists(os.path.join(VIDEO_DIR, video_file)) else ""

    # Generate customized HTML
    with open(HTML_PATH, "r") as f:
        html = f.read()

    if voice_data:
        html = html.replace(
            "const VOICE_DATA = {};",
            f"const VOICE_DATA = {json.dumps(voice_data)};",
        )

    if video_rel:
        html = html.replace(
            "const VIDEO_PATH = '';",
            f"const VIDEO_PATH = '{video_rel}';",
        )

    # Inject audio file path
    sound_file = THEME_SOUNDS.get(theme, "")
    if sound_file and os.path.exists(os.path.join(SOUND_DIR, sound_file)):
        html = html.replace(
            "const USE_VIDEO_AUDIO = false;",
            "const USE_VIDEO_AUDIO = true;",
        )
        html = html.replace(
            "const AUDIO_PATH = '';",
            f"const AUDIO_PATH = 'sounds/{sound_file}';",
        )

    # Write session HTML into script dir (server serves from there)
    session_path = os.path.join(SCRIPT_DIR, "_session.html")
    with open(session_path, "w") as f:
        f.write(html)

    # Find a free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    # Start local HTTP server as background process
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port),
         "--directory", SCRIPT_DIR, "--bind", "127.0.0.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Auto-kill server after session ends
    subprocess.Popen(
        ["bash", "-c",
         f"sleep {duration + 30} && kill {server_proc.pid} 2>/dev/null"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    url = f"http://127.0.0.1:{port}/_session.html?theme={theme}&duration={duration}&type={exercise_type}"

    # DND: mute alert sounds during meditation
    try:
        subprocess.run(
            ["osascript", "-e", "set volume alert volume 0"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3,
        )
    except Exception:
        pass

    # Schedule DND restore after session ends
    subprocess.Popen(
        ["bash", "-c",
         f"sleep {duration + 15} && osascript -e 'set volume alert volume 5'"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    webbrowser.open(url)


# ---------------------------------------------------------------------------
# Visual session (terminal mode)
# ---------------------------------------------------------------------------

def run_visual_session(config, exercise_type=None, duration=None):
    """Full-screen terminal meditation experience."""
    from modules.display import Display
    from modules.ambient import AmbientSound
    from modules.breathing import BreathingExercise
    from modules.body_scan import BodyScan
    from modules.quotes import ZenQuotes

    display = Display()
    ambient = None

    if exercise_type is None:
        exercise_type = random.choice(config.get("preferred_types", ["breathing"]))
    if duration is None:
        duration = random.randint(
            config.get("min_duration_seconds", 60),
            config.get("max_duration_seconds", 180),
        )

    exercises = {
        "breathing": BreathingExercise(display),
        "body_scan": BodyScan(display),
        "quotes": ZenQuotes(display),
    }
    exercise = exercises.get(exercise_type, exercises["breathing"])

    try:
        display.enter_zen_mode()
        if config.get("sound_enabled", True):
            ambient = AmbientSound()
            ambient.start(duration + 30)
        exercise.run(duration)
    except KeyboardInterrupt:
        pass
    finally:
        if ambient:
            ambient.stop()
        display.exit_zen_mode()


# ---------------------------------------------------------------------------
# Audio-only session (legacy — macOS say + ambient)
# ---------------------------------------------------------------------------

def run_audio_session(config, exercise_type=None):
    """Voice-guided meditation with macOS say + ambient sound."""
    from modules.ambient import AmbientSound

    voice = config.get("voice_name", "Samantha")
    rate = config.get("voice_rate", 130)
    duration = random.randint(
        config.get("min_duration_seconds", 60),
        config.get("max_duration_seconds", 180),
    )

    if exercise_type is None:
        exercise_type = random.choice(config.get("preferred_types", ["breathing"]))

    ambient = AmbientSound()
    if config.get("sound_enabled", True):
        ambient.start(duration + 20)

    dialog_proc = subprocess.Popen(
        [
            "osascript", "-e",
            f'display dialog "Zen session active...\\n\\n'
            f'Close your eyes and breathe.\\n'
            f'Session: ~{duration // 60} min {duration % 60}s" '
            f'buttons {{"End Session"}} default button 1 '
            f'with title "Zen Mode" giving up after {duration + 10}',
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    def say(text):
        try:
            subprocess.run(
                ["say", "-v", voice, "-r", str(rate), text],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            time.sleep(len(text) * 0.06)

    def done():
        return dialog_proc.poll() is not None

    try:
        say("Close your eyes. Let's begin with some gentle breathing.")
        cycles = max(3, duration // 22)
        for _ in range(cycles):
            if done(): break
            say("Breathe in slowly... two... three... four.")
            if done(): break
            time.sleep(1)
            say("Hold gently... two... three... four.")
            if done(): break
            time.sleep(1)
            say("And breathe out... two... three... four... five... six.")
            if done(): break
            time.sleep(2)
        if not done():
            say("Gently bring your attention back. Open your eyes when ready.")
            time.sleep(2)
            say("Well done.")
    finally:
        ambient.stop()
        if dialog_proc.poll() is None:
            dialog_proc.terminate()

    try:
        subprocess.Popen(
            ["osascript", "-e",
             'display notification "Session complete. Well done." '
             'with title "Zen Mode" sound name "Glass"'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# Background ambient session (just video + audio, no meditation UI)
# ---------------------------------------------------------------------------

def run_background_session(config, theme=None):
    """Open a fullscreen ambient video + audio tab. No meditation UI."""
    import socket

    if theme is None:
        theme = random.choice(THEMES)

    video_file = THEME_VIDEOS.get(theme, "")
    video_rel = f"videos/{video_file}" if os.path.exists(os.path.join(VIDEO_DIR, video_file)) else ""
    sound_file = THEME_SOUNDS.get(theme, "")
    audio_rel = f"sounds/{sound_file}" if sound_file and os.path.exists(os.path.join(SOUND_DIR, sound_file)) else ""

    with open(BG_HTML_PATH, "r") as f:
        html = f.read()

    if video_rel:
        html = html.replace("const VIDEO_PATH = '';", f"const VIDEO_PATH = '{video_rel}';")
    if audio_rel:
        html = html.replace("const AUDIO_PATH = '';", f"const AUDIO_PATH = '{audio_rel}';")

    session_path = os.path.join(SCRIPT_DIR, "_background.html")
    with open(session_path, "w") as f:
        f.write(html)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port),
         "--directory", SCRIPT_DIR, "--bind", "127.0.0.1"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # Keep server alive for 2 hours (background ambient)
    subprocess.Popen(
        ["bash", "-c", f"sleep 7200 && kill {server_proc.pid} 2>/dev/null"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    webbrowser.open(f"http://127.0.0.1:{port}/_background.html")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Zen Mode — mindfulness meditation")
    parser.add_argument(
        "--type", "-t",
        choices=TYPES,
        help="Exercise type (default: random)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="Session duration in seconds (default: 60-180 random)",
    )
    parser.add_argument(
        "--theme",
        choices=THEMES,
        help="Nature theme (default: random)",
    )
    parser.add_argument(
        "--background", "--bg",
        action="store_true",
        help="Background ambient mode — just video + audio, no meditation UI",
    )
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Run in terminal mode (alternate screen + ASCII animation)",
    )
    parser.add_argument(
        "--audio-only", "-a",
        action="store_true",
        help="Run audio-only session (macOS say + ambient sound)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-trigger mode (browser, for hook invocation)",
    )
    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable ambient sound",
    )

    args = parser.parse_args()
    config = load_config()

    if args.no_sound:
        config["sound_enabled"] = False

    if args.background:
        run_background_session(config, args.theme)
    elif args.visual:
        run_visual_session(config, args.type, args.duration)
    elif args.audio_only:
        run_audio_session(config, args.type)
    else:
        # Default: browser mode
        run_browser_session(config, args.type, args.duration, args.theme)


if __name__ == "__main__":
    main()
