#!/bin/bash
# Zen Mode — PostToolUse hook trigger
#
# Checks: macOS idle time + random probability + cooldown
# If all pass: shows a native dialog; user chooses to meditate or skip.
# Non-blocking — launches everything in background and exits immediately.

set -e

ZEN_DIR="$(cd "$(dirname "$0")" && pwd)"
STAMP_FILE="$ZEN_DIR/.last_trigger"
CONFIG="$ZEN_DIR/config.json"

# ── Quick-exit checks ──────────────────────────────────────────────

# 1. macOS idle time (seconds since last keyboard/mouse/trackpad activity)
IDLE=$(ioreg -c IOHIDSystem 2>/dev/null | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}')
[ -z "$IDLE" ] && exit 0
[ "$IDLE" -lt 45 ] && exit 0

# 2. Random roll (12% chance)
[ $((RANDOM % 100)) -ge 12 ] && exit 0

# 3. Cooldown — at least 25 minutes between triggers
if [ -f "$STAMP_FILE" ]; then
    LAST=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    ELAPSED_MIN=$(( (NOW - LAST) / 60 ))
    [ "$ELAPSED_MIN" -lt 25 ] && exit 0
fi

# ── All checks passed — record timestamp and launch ────────────────

date +%s > "$STAMP_FILE"

# Launch dialog + meditation in background (non-blocking for the hook)
(
    RESPONSE=$(osascript 2>/dev/null <<'APPLESCRIPT'
try
    set r to display dialog "Time for a mindful break?" & return & return & "1-3 minutes of guided calm." & return & "Close your eyes and breathe." buttons {"Skip", "Let's Go"} default button 2 with title "Zen Mode" with icon note giving up after 30
    return button returned of r
on error
    return "Skip"
end try
APPLESCRIPT
    )

    if [ "$RESPONSE" = "Let's Go" ]; then
        # Open beautiful browser meditation page
        python3 "$ZEN_DIR/zen.py" --auto &>/dev/null
    fi
) &>/dev/null &
disown

exit 0
