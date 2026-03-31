"""Mindfulness quotes with reflection pauses for Zen Mode.

Curated quotes from meditation teachers, philosophers, and poets.
Displayed with fade-in animation and gentle pacing.
"""

import random
import time

from .display import Colors, Display


QUOTES = [
    (
        "Between stimulus and response there is a space.\n"
        "In that space is our freedom.",
        "Viktor Frankl",
    ),
    (
        "The present moment is the only moment\n"
        "available to us, and it is the door to all moments.",
        "Thich Nhat Hanh",
    ),
    (
        "Feelings come and go like clouds in a windy sky.\n"
        "Conscious breathing is my anchor.",
        "Thich Nhat Hanh",
    ),
    (
        "Almost everything will work again\n"
        "if you unplug it for a few minutes.\n"
        "Including you.",
        "Anne Lamott",
    ),
    (
        "Breath is the bridge which connects\n"
        "life to consciousness.",
        "Thich Nhat Hanh",
    ),
    (
        "Nature does not hurry,\n"
        "yet everything is accomplished.",
        "Lao Tzu",
    ),
    (
        "You are the sky.\n"
        "Everything else is just the weather.",
        "Pema Chodron",
    ),
    (
        "The quieter you become,\n"
        "the more you can hear.",
        "Ram Dass",
    ),
    (
        "Within you there is a stillness\n"
        "and a sanctuary to which you can retreat\n"
        "at any time and be yourself.",
        "Hermann Hesse",
    ),
    (
        "Smile, breathe, and go slowly.",
        "Thich Nhat Hanh",
    ),
    (
        "When you realize nothing is lacking,\n"
        "the whole world belongs to you.",
        "Lao Tzu",
    ),
    (
        "The greatest weapon against stress\n"
        "is our ability to choose\n"
        "one thought over another.",
        "William James",
    ),
    (
        "In the midst of movement and chaos,\n"
        "keep stillness inside of you.",
        "Deepak Chopra",
    ),
    (
        "Respond; don't react.\n"
        "Listen; don't talk.\n"
        "Think; don't assume.",
        "Raji Lukkoor",
    ),
    (
        "The only way to live is by accepting\n"
        "each minute as an unrepeatable miracle.",
        "Tara Brach",
    ),
    (
        "Do not dwell in the past,\n"
        "do not dream of the future,\n"
        "concentrate the mind on the present moment.",
        "Buddha",
    ),
    (
        "Surrender to what is.\n"
        "Let go of what was.\n"
        "Have faith in what will be.",
        "Sonia Ricotti",
    ),
    (
        "Life is available only in the present moment.",
        "Thich Nhat Hanh",
    ),
    (
        "Be where you are,\n"
        "not where you think you should be.",
        "Anonymous",
    ),
    (
        "The mind is everything.\n"
        "What you think, you become.",
        "Buddha",
    ),
]

REFLECTIONS = [
    "Sit with this for a moment.",
    "Let that settle.",
    "Breathe this in.",
    "Notice what arises.",
    "Let the words echo gently.",
]


class ZenQuotes:
    """Quote-based meditation with reflection pauses."""

    def __init__(self, display: Display):
        self.display = display

    def run(self, duration_seconds=120):
        """Show 2-4 quotes with reflection pauses.

        Returns True if completed, False if skipped.
        """
        # Pick random quotes (no repeats)
        num_quotes = max(2, min(4, duration_seconds // 40))
        selected = random.sample(QUOTES, num_quotes)
        time_per_quote = duration_seconds / num_quotes

        start_time = time.time()

        # Intro
        if self._show_intro():
            return False

        for i, (quote, author) in enumerate(selected):
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            if remaining <= 5:
                break

            if self._show_quote(quote, author, time_per_quote, remaining, duration_seconds):
                return False

        # Outro
        self._show_outro()
        return True

    def _show_intro(self):
        """Opening screen. Returns True if skipped."""
        self.display.clear()
        row = self.display.height // 2 - 2

        self.display.center_text("~ zen ~", row, Colors.DIM + Colors.MUTED)
        self.display.center_text(
            "A moment of reflection", row + 2, Colors.QUOTE + Colors.BOLD
        )
        self.display.center_text(
            "Listen with your whole self.", row + 5, Colors.MUTED
        )
        self.display.bottom_bar(center="[q] skip")
        return self.display.sleep_check(3)

    def _show_quote(self, quote, author, display_time, remaining, total):
        """Display a quote with reflection pause. Returns True if skipped."""
        self.display.clear()

        # Quote text
        lines = quote.split("\n")
        quote_start = max(3, self.display.height // 2 - len(lines) - 1)

        # Fade in each line
        for j, line in enumerate(lines):
            skipped = self.display.fade_in_text(
                line.strip(), quote_start + j * 2, Colors.QUOTE
            )
            if skipped:
                # Show remaining lines instantly
                for k in range(j + 1, len(lines)):
                    self.display.center_text(
                        lines[k].strip(), quote_start + k * 2, Colors.QUOTE
                    )
                break
            time.sleep(0.3)

        # Author
        author_row = quote_start + len(lines) * 2 + 1
        self.display.center_text(
            f"— {author}", author_row, Colors.DIM + Colors.MUTED
        )

        # Reflection prompt
        reflection = random.choice(REFLECTIONS)
        self.display.center_text(
            reflection, author_row + 3, Colors.DIM + Colors.SOFT_WHITE
        )

        # Progress bar
        bar_row = self.display.height - 4
        bar = self.display.progress_bar(total - remaining, total)
        time_str = self.display.format_time(remaining)
        self.display.center_text(
            f"{Colors.QUOTE}{bar}  {Colors.MUTED}{time_str}", bar_row
        )
        self.display.bottom_bar(center="[q] skip")

        # Hold for reflection
        return self.display.sleep_check(display_time - 2)

    def _show_outro(self):
        """Completion screen."""
        self.display.clear()
        row = self.display.height // 2 - 2

        self.display.center_text("~ session complete ~", row, Colors.QUOTE)
        self.display.center_text(
            "Carry a word or feeling with you.",
            row + 3,
            Colors.SOFT_WHITE,
        )
        self.display.sleep_check(3)
