"""Breathing exercises for Zen Mode.

Supports box breathing, 4-7-8 relaxing breath, and coherent breathing.
Renders an animated breathing circle with phase labels and countdown.
"""

import random
import time

from .display import Colors, Display


PATTERNS = {
    "box": {
        "name": "Box Breathing",
        "desc": "Equal inhale, hold, exhale, hold — calming and centering",
        "phases": [
            ("in", "Breathe In", 4),
            ("hold_in", "Hold", 4),
            ("out", "Breathe Out", 4),
            ("hold_out", "Rest", 4),
        ],
    },
    "relaxing": {
        "name": "4-7-8 Breath",
        "desc": "Deep relaxation — slows the heart rate",
        "phases": [
            ("in", "Breathe In", 4),
            ("hold_in", "Hold", 7),
            ("out", "Breathe Out", 8),
        ],
    },
    "coherent": {
        "name": "Coherent Breathing",
        "desc": "5.5 breaths per minute — optimal for heart rate variability",
        "phases": [
            ("in", "Breathe In", 6),
            ("out", "Breathe Out", 6),
        ],
    },
}


class BreathingExercise:
    """Animated breathing exercise with circle visualization."""

    def __init__(self, display: Display):
        self.display = display

    def run(self, duration_seconds=120, pattern_name=None):
        """Run a breathing exercise for the given duration.

        Returns True if completed, False if skipped.
        """
        if pattern_name is None:
            pattern_name = random.choice(list(PATTERNS.keys()))

        pattern = PATTERNS[pattern_name]
        phases = pattern["phases"]

        # Show intro
        self._show_intro(pattern)

        # Calculate total cycle time
        cycle_time = sum(p[2] for p in phases)
        start_time = time.time()
        elapsed = 0

        while elapsed < duration_seconds:
            # Determine which phase we're in within the current cycle
            cycle_pos = elapsed % cycle_time
            phase_offset = 0

            for phase_id, phase_label, phase_duration in phases:
                if cycle_pos < phase_offset + phase_duration:
                    # We're in this phase
                    time_in_phase = cycle_pos - phase_offset
                    phase_progress = time_in_phase / phase_duration
                    countdown = max(1, int(phase_duration - time_in_phase))
                    remaining = duration_seconds - elapsed

                    self.display.render_breathing_frame(
                        phase=phase_id,
                        phase_progress=phase_progress,
                        countdown=countdown,
                        total_remaining=remaining,
                        total_duration=duration_seconds,
                        phase_label=phase_label,
                    )
                    break

                phase_offset += phase_duration

            # Sleep and check for skip
            time.sleep(0.4)
            if self.display.check_skip():
                return False

            elapsed = time.time() - start_time

        # Completion
        self._show_outro()
        return True

    def _show_intro(self, pattern):
        """Show exercise name and brief instruction."""
        self.display.clear()
        row = self.display.height // 2 - 3

        self.display.center_text("~ zen ~", row, Colors.DIM + Colors.MUTED)
        self.display.center_text(
            pattern["name"], row + 2, Colors.TITLE + Colors.BOLD
        )
        self.display.center_text(pattern["desc"], row + 4, Colors.MUTED)
        self.display.center_text(
            "Starting in a moment...", row + 7, Colors.DIM + Colors.MUTED
        )
        self.display.bottom_bar(center="[q] skip")
        self.display.sleep_check(3)

    def _show_outro(self):
        """Show completion message."""
        self.display.clear()
        row = self.display.height // 2 - 2

        self.display.center_text("~ session complete ~", row, Colors.TITLE)
        self.display.center_text(
            "Well done. Carry this calm with you.",
            row + 3,
            Colors.SOFT_WHITE,
        )
        self.display.sleep_check(3)
