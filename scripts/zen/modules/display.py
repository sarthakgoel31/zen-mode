"""Terminal display utilities for Zen Mode.

Handles alternate screen buffer, soft color palette, centered text,
non-blocking keypress detection, breathing circle rendering, and
progress indicators.
"""

import os
import re
import sys
import time
import select
import shutil
import signal
import tty
import termios


class Colors:
    """Soft, calming ANSI color palette."""

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    # Breathing phases
    BREATHE_IN = "\033[38;5;117m"   # Soft blue
    HOLD = "\033[38;5;183m"         # Soft purple
    BREATHE_OUT = "\033[38;5;115m"  # Soft green
    REST = "\033[38;5;223m"         # Warm sand

    # UI elements
    MUTED = "\033[38;5;245m"
    SOFT_WHITE = "\033[38;5;255m"
    ACCENT = "\033[38;5;216m"       # Soft peach
    TITLE = "\033[38;5;146m"        # Lavender
    QUOTE = "\033[38;5;180m"        # Warm gold
    BODY = "\033[38;5;152m"         # Sage

    PHASE_COLORS = {
        "in": BREATHE_IN,
        "hold_in": HOLD,
        "out": BREATHE_OUT,
        "hold_out": REST,
    }


# Pre-defined breathing circles at 6 sizes (0-5)
# Using middle dots for a delicate, airy feel
CIRCLES = [
    # Size 0
    ["  ·  "],
    # Size 1
    [
        "  · · ·  ",
        " ·     · ",
        "  · · ·  ",
    ],
    # Size 2
    [
        "   · · · ·   ",
        " ·         · ",
        "·           ·",
        " ·         · ",
        "   · · · ·   ",
    ],
    # Size 3
    [
        "    · · · · ·    ",
        "  ·           ·  ",
        " ·             · ",
        "·               ·",
        " ·             · ",
        "  ·           ·  ",
        "    · · · · ·    ",
    ],
    # Size 4
    [
        "     · · · · · ·     ",
        "   ·             ·   ",
        "  ·               ·  ",
        " ·                 · ",
        "·                   ·",
        " ·                 · ",
        "  ·               ·  ",
        "   ·             ·   ",
        "     · · · · · ·     ",
    ],
    # Size 5
    [
        "      · · · · · · ·      ",
        "    ·               ·    ",
        "  ·                   ·  ",
        "  ·                   ·  ",
        " ·                     · ",
        "·                       ·",
        " ·                     · ",
        "  ·                   ·  ",
        "  ·                   ·  ",
        "    ·               ·    ",
        "      · · · · · · ·      ",
    ],
]


class Display:
    """Terminal display manager for meditation sessions."""

    def __init__(self):
        self.width, self.height = shutil.get_terminal_size((80, 24))
        self._old_settings = None
        self._in_zen_mode = False
        self._original_sigwinch = None

    def enter_zen_mode(self):
        """Enter alternate screen buffer, hide cursor, enable cbreak mode."""
        self._in_zen_mode = True
        try:
            self._old_settings = termios.tcgetattr(sys.stdin.fileno())
        except termios.error:
            self._old_settings = None
        # Alternate screen buffer
        sys.stdout.write("\033[?1049h")
        # Hide cursor
        sys.stdout.write("\033[?25l")
        self.clear()
        sys.stdout.flush()
        # Enable cbreak for non-blocking input (no echo, char-at-a-time)
        try:
            tty.setcbreak(sys.stdin.fileno())
        except termios.error:
            pass
        # Handle terminal resize
        self._original_sigwinch = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._on_resize)

    def exit_zen_mode(self):
        """Restore terminal to original state."""
        if not self._in_zen_mode:
            return
        self._in_zen_mode = False
        # Show cursor
        sys.stdout.write("\033[?25h")
        # Exit alternate screen buffer
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()
        # Restore terminal settings
        if self._old_settings:
            try:
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings
                )
            except termios.error:
                pass
        # Restore signal handler
        if self._original_sigwinch is not None:
            signal.signal(signal.SIGWINCH, self._original_sigwinch)

    def _on_resize(self, sig, frame):
        self.width, self.height = shutil.get_terminal_size((80, 24))

    def clear(self):
        """Clear screen and move cursor to top-left."""
        sys.stdout.write("\033[2J\033[H")

    def move_to(self, row, col):
        """Move cursor to 1-based (row, col)."""
        sys.stdout.write(f"\033[{row};{col}H")

    def _strip_ansi(self, text):
        """Remove ANSI escape codes for width calculation."""
        return re.sub(r"\033\[[0-9;]*m", "", text)

    def center_text(self, text, row=None, color=""):
        """Print centered text. Returns the row after the last line."""
        lines = text.split("\n")
        if row is None:
            row = max(1, (self.height - len(lines)) // 2)
        for i, line in enumerate(lines):
            clean = self._strip_ansi(line)
            col = max(1, (self.width - len(clean)) // 2)
            self.move_to(row + i, col)
            sys.stdout.write(f"{color}{line}{Colors.RESET}")
        sys.stdout.flush()
        return row + len(lines)

    def bottom_bar(self, left="", center="", right=""):
        """Show text at the bottom of the screen."""
        row = self.height
        if left:
            self.move_to(row, 2)
            sys.stdout.write(f"{Colors.MUTED}{left}{Colors.RESET}")
        if center:
            clean = self._strip_ansi(center)
            col = max(1, (self.width - len(clean)) // 2)
            self.move_to(row, col)
            sys.stdout.write(f"{Colors.MUTED}{center}{Colors.RESET}")
        if right:
            clean = self._strip_ansi(right)
            col = max(1, self.width - len(clean) - 1)
            self.move_to(row, col)
            sys.stdout.write(f"{Colors.MUTED}{right}{Colors.RESET}")
        sys.stdout.flush()

    def progress_bar(self, current, total, width=30):
        """Render a soft progress bar string."""
        filled = int(width * min(current, total) / max(total, 1))
        return f"{'━' * filled}{'╌' * (width - filled)}"

    def breathing_circle(self, size_index, center_text="", color=""):
        """Get a breathing circle at the given size (0-5) with optional center text."""
        size_index = max(0, min(5, size_index))
        lines = [line[:] for line in CIRCLES[size_index]]

        # Insert center text in the middle line
        if center_text and lines:
            mid = len(lines) // 2
            line = lines[mid]
            text_start = max(0, (len(line) - len(center_text)) // 2)
            line_list = list(line)
            for i, ch in enumerate(center_text):
                pos = text_start + i
                if pos < len(line_list):
                    line_list[pos] = ch
            lines[mid] = "".join(line_list)

        return "\n".join(lines)

    def check_skip(self):
        """Non-blocking check for skip keys (q, Escape, space). Returns True if pressed."""
        try:
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch in ("q", "Q", "\x1b", " "):
                    return True
        except (OSError, ValueError):
            pass
        return False

    def fade_in_text(self, text, row=None, color=Colors.SOFT_WHITE, delay=0.04):
        """Reveal text character by character. Returns True if skipped."""
        if row is None:
            row = self.height // 2
        clean = self._strip_ansi(text)
        col = max(1, (self.width - len(clean)) // 2)
        self.move_to(row, col)
        for i, ch in enumerate(text):
            sys.stdout.write(f"{color}{ch}")
            sys.stdout.flush()
            time.sleep(delay)
            if self.check_skip():
                # Print remaining instantly
                sys.stdout.write(f"{color}{text[i + 1:]}")
                sys.stdout.flush()
                return True
        return False

    def sleep_check(self, seconds, interval=0.2):
        """Sleep for `seconds`, checking for skip every `interval`. Returns True if skipped."""
        elapsed = 0.0
        while elapsed < seconds:
            if self.check_skip():
                return True
            wait = min(interval, seconds - elapsed)
            time.sleep(wait)
            elapsed += wait
        return False

    def format_time(self, seconds):
        """Format seconds as M:SS."""
        m, s = divmod(max(0, int(seconds)), 60)
        return f"{m}:{s:02d}"

    def render_breathing_frame(self, phase, phase_progress, countdown,
                                total_remaining, total_duration, phase_label):
        """Render a complete breathing frame: circle + label + progress."""
        # Calculate circle size based on phase
        if phase == "in":
            size = round(phase_progress * 5)
        elif phase == "out":
            size = round((1 - phase_progress) * 5)
        elif phase == "hold_in":
            size = 5
        else:  # hold_out
            size = 0

        color = Colors.PHASE_COLORS.get(phase, Colors.SOFT_WHITE)

        self.clear()

        # Title (top area)
        title_row = max(2, self.height // 2 - 8)
        self.center_text("~ zen ~", title_row, Colors.DIM + Colors.MUTED)

        # Phase label
        label_row = title_row + 3
        spaced = "   ".join(phase_label.upper())
        self.center_text(spaced, label_row, color + Colors.BOLD)

        # Breathing circle with countdown
        circle_text = self.breathing_circle(size, str(countdown), color)
        circle_start = label_row + 2
        self.center_text(circle_text, circle_start, color)

        # Progress bar
        bar_row = self.height - 4
        bar = self.progress_bar(total_duration - total_remaining, total_duration)
        time_str = self.format_time(total_remaining)
        self.center_text(f"{color}{bar}  {Colors.MUTED}{time_str}", bar_row)

        # Bottom bar
        self.bottom_bar(center="[q] skip  ·  [space] pause")

        sys.stdout.flush()
