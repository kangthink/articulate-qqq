#!/bin/bash
set -euo pipefail

APP_NAME="aq"
INSTALL_DIR="$HOME/.local/bin"
TARGET="$INSTALL_DIR/$APP_NAME"
PID_FILE="/tmp/aq.pid"

echo "=== articulate-qqq ($APP_NAME) uninstaller ==="

# Stop running watcher if any
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null || true
        echo "Stopped running watcher (PID: $PID)"
    fi
    rm -f "$PID_FILE"
fi

# Remove symlink
if [[ -L "$TARGET" || -f "$TARGET" ]]; then
    rm -f "$TARGET"
    echo "Removed: $TARGET"
else
    echo "Not installed: $TARGET not found"
fi

echo ""
echo "=== Uninstall complete ==="
echo "Note: PATH entry in shell config was not removed."
echo "You may remove the 'articulate-qqq' lines from your shell config manually."
