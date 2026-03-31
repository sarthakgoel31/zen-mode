"""Ambient sound generator for Zen Mode.

Generates calming sine-wave tones using Python stdlib (wave + struct).
Plays via macOS `afplay` in the background. No external dependencies.
"""

import math
import os
import signal
import struct
import subprocess
import tempfile
import wave


SAMPLE_RATE = 44100


def _generate_samples(duration_seconds):
    """Generate calming ambient audio samples.

    Mix of healing frequencies with slow amplitude modulation
    to create a breathing-like swell effect.
    """
    n_samples = int(SAMPLE_RATE * duration_seconds)
    two_pi = 2 * math.pi
    samples = bytearray()

    for i in range(n_samples):
        t = i / SAMPLE_RATE

        # Slow amplitude envelope — mimics breathing rhythm
        envelope = 0.35 + 0.15 * math.sin(two_pi * 0.08 * t)

        # Layered tones (solfeggio-inspired, detuned for warmth)
        tone = (
            0.35 * math.sin(two_pi * 174.0 * t)       # Foundation
            + 0.25 * math.sin(two_pi * 285.0 * t)     # Healing
            + 0.15 * math.sin(two_pi * 396.0 * t)     # Liberation
            + 0.10 * math.sin(two_pi * 87.0 * t)      # Sub-bass
            + 0.08 * math.sin(two_pi * 528.0 * t)     # Transformation (subtle)
        )

        # Apply envelope and master volume (quiet — background level)
        val = envelope * tone * 0.12

        # Clamp and pack as signed 16-bit
        sample = max(-32767, min(32767, int(val * 32767)))
        samples.extend(struct.pack("<h", sample))

    return bytes(samples)


class AmbientSound:
    """Background ambient sound player."""

    def __init__(self):
        self._process = None
        self._wav_path = None

    def generate(self, duration_seconds=180):
        """Generate a WAV file with ambient tones."""
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="zen_ambient_")
        os.close(fd)

        samples = _generate_samples(duration_seconds)

        with wave.open(path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(samples)

        self._wav_path = path
        return path

    def start(self, duration_seconds=180):
        """Generate and start playing ambient sound in background."""
        path = self.generate(duration_seconds + 10)
        try:
            self._process = subprocess.Popen(
                ["afplay", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            # afplay not available (non-macOS)
            self._process = None

    def stop(self):
        """Stop playback and clean up temp file."""
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    self._process.kill()
                except ProcessLookupError:
                    pass
        self._process = None

        if self._wav_path and os.path.exists(self._wav_path):
            try:
                os.unlink(self._wav_path)
            except OSError:
                pass
            self._wav_path = None

    def __del__(self):
        self.stop()
