"""Quick body scan meditation for Zen Mode.

Progressive relaxation through body regions, 1-3 minutes.
Text prompts with gentle pacing and soft visuals.
"""

import random
import time

from .display import Colors, Display


SCAN_SEQUENCES = [
    # Full sequence (~2.5 min at 20s per step)
    [
        ("Crown & Forehead",
         "Bring your awareness to the top of your head.\n"
         "Notice any sensations — tingling, warmth, weight.\n"
         "Let your forehead soften completely."),
        ("Eyes & Jaw",
         "Relax the muscles around your eyes.\n"
         "Unclench your jaw. Let your tongue rest.\n"
         "There's nothing to hold here."),
        ("Neck & Shoulders",
         "Drop your shoulders away from your ears.\n"
         "Feel the weight releasing with each exhale.\n"
         "Let the tension dissolve."),
        ("Hands & Arms",
         "Notice your hands, wherever they are.\n"
         "Feel your fingers... your palms.\n"
         "Let any tension melt like ice in warm water."),
        ("Chest & Belly",
         "Place your awareness on your chest.\n"
         "Feel it rise and fall with each breath.\n"
         "Soften your belly completely. Let it be free."),
        ("Lower Back & Hips",
         "Bring attention to your lower back.\n"
         "Breathe into any tightness you find.\n"
         "Let your hips feel heavy and supported."),
        ("Legs & Feet",
         "Scan down through your legs to your feet.\n"
         "Feel your connection to the ground.\n"
         "You are supported. You are here."),
    ],
    # Short sequence (~1.5 min at 20s per step)
    [
        ("Head & Face",
         "Soften your forehead... your eyes... your jaw.\n"
         "Let everything above your neck release."),
        ("Shoulders & Arms",
         "Drop your shoulders. Relax your arms.\n"
         "Feel the weight leave your hands."),
        ("Core & Breath",
         "Notice your breath in your chest and belly.\n"
         "Let your torso soften with each exhale."),
        ("Ground & Feet",
         "Feel where your body meets the surface below.\n"
         "You are held. You are grounded. You are here."),
    ],
]


TRANSITIONS = [
    "Now gently shift your attention...",
    "Slowly move your awareness...",
    "Let your focus drift to...",
    "Bring a soft attention to...",
]


class BodyScan:
    """Guided body scan meditation with text prompts."""

    def __init__(self, display: Display):
        self.display = display

    def run(self, duration_seconds=120):
        """Run a body scan for the given duration.

        Returns True if completed, False if skipped.
        """
        # Pick sequence based on duration
        if duration_seconds <= 90:
            sequence = SCAN_SEQUENCES[1]  # Short
        else:
            sequence = SCAN_SEQUENCES[0]  # Full

        time_per_step = duration_seconds / len(sequence)
        start_time = time.time()

        # Intro
        if self._show_intro():
            return False

        for i, (region, prompt) in enumerate(sequence):
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            if remaining <= 0:
                break

            # Transition text (skip for first step)
            if i > 0:
                transition = random.choice(TRANSITIONS)
                if self._show_transition(transition):
                    return False

            # Show the scan step
            step_time = min(time_per_step, remaining)
            if self._show_step(region, prompt, step_time, remaining, duration_seconds):
                return False

        # Outro
        self._show_outro()
        return True

    def _show_intro(self):
        """Show opening instructions. Returns True if skipped."""
        self.display.clear()
        row = self.display.height // 2 - 4

        self.display.center_text("~ zen ~", row, Colors.DIM + Colors.MUTED)
        self.display.center_text("Body Scan", row + 2, Colors.BODY + Colors.BOLD)
        self.display.center_text(
            "Close your eyes if comfortable.", row + 5, Colors.SOFT_WHITE
        )
        self.display.center_text(
            "We'll move gently through your body,", row + 7, Colors.MUTED
        )
        self.display.center_text(
            "noticing and releasing tension.", row + 8, Colors.MUTED
        )
        self.display.bottom_bar(center="[q] skip")
        return self.display.sleep_check(4)

    def _show_transition(self, text):
        """Brief pause between body regions. Returns True if skipped."""
        self.display.clear()
        row = self.display.height // 2
        self.display.center_text(text, row, Colors.DIM + Colors.MUTED)
        return self.display.sleep_check(2)

    def _show_step(self, region, prompt, step_time, remaining, total):
        """Display a body scan step. Returns True if skipped."""
        self.display.clear()

        # Region header
        header_row = max(3, self.display.height // 2 - 5)
        self.display.center_text("~ zen ~", header_row, Colors.DIM + Colors.MUTED)

        spaced_region = "  ".join(region.upper())
        self.display.center_text(
            spaced_region, header_row + 3, Colors.BODY + Colors.BOLD
        )

        # Prompt text (centered, multi-line)
        prompt_row = header_row + 6
        for j, line in enumerate(prompt.split("\n")):
            self.display.center_text(line.strip(), prompt_row + j, Colors.SOFT_WHITE)

        # Progress bar
        bar_row = self.display.height - 4
        bar = self.display.progress_bar(total - remaining, total)
        time_str = self.display.format_time(remaining)
        self.display.center_text(
            f"{Colors.BODY}{bar}  {Colors.MUTED}{time_str}", bar_row
        )
        self.display.bottom_bar(center="[q] skip")

        # Hold for step duration, checking for skip
        return self.display.sleep_check(step_time)

    def _show_outro(self):
        """Completion screen."""
        self.display.clear()
        row = self.display.height // 2 - 2

        self.display.center_text("~ session complete ~", row, Colors.BODY)
        self.display.center_text(
            "Your body thanks you. Carry this awareness forward.",
            row + 3,
            Colors.SOFT_WHITE,
        )
        self.display.sleep_check(3)
