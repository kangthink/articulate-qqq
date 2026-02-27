#!/bin/bash
set -euo pipefail

APP_NAME="aq"
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== articulate-qqq ($APP_NAME) installer ==="

# 1. macOS check
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Warning: This tool is designed for macOS. Proceeding anyway..."
fi

# 2. Python 3 check
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found. Please install Python 3.12+."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $PY_VERSION"

# 3. Claude CLI check
if ! command -v claude &>/dev/null; then
    echo ""
    echo "Warning: Claude CLI not found."
    echo "Install it from: https://docs.anthropic.com/en/docs/claude-code"
    echo "aq requires Claude CLI to function."
    echo ""
fi

# 4. Create install directory
mkdir -p "$INSTALL_DIR"

# 5. Create symlink
SOURCE="$SCRIPT_DIR/bin/$APP_NAME"
TARGET="$INSTALL_DIR/$APP_NAME"

if [[ -L "$TARGET" || -f "$TARGET" ]]; then
    rm -f "$TARGET"
fi

chmod +x "$SOURCE"
ln -sf "$SOURCE" "$TARGET"
echo "Linked: $TARGET -> $SOURCE"

# 6. Ensure PATH includes ~/.local/bin
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    SHELL_RC=""
    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -n "${BASH_VERSION:-}" ]] || [[ "$SHELL" == */bash ]]; then
        SHELL_RC="$HOME/.bashrc"
    fi

    if [[ -n "$SHELL_RC" ]]; then
        echo "" >> "$SHELL_RC"
        echo "# articulate-qqq" >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "Added ~/.local/bin to PATH in $SHELL_RC"
        echo "Run: source $SHELL_RC"
    else
        echo "Add to your shell config: export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
fi

echo ""
echo "=== Installation complete ==="
echo "Usage:"
echo "  $APP_NAME run <file>        # Process markers once"
echo "  $APP_NAME watch <file|dir>  # Watch for changes"
echo "  $APP_NAME stop              # Stop watcher"
