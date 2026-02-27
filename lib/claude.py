"""Claude CLI wrapper for invoking claude -p."""

import os
import subprocess
import shutil


def find_claude() -> str | None:
    """Find the claude CLI binary."""
    candidates = [
        os.path.expanduser("~/.local/bin/claude"),
        "/usr/local/bin/claude",
    ]
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return shutil.which("claude")


def call_claude(
    system_prompt: str,
    user_prompt: str,
    timeout: int = 120,
) -> str | None:
    """Call Claude CLI and return the response text.

    Uses stdin to pass the user prompt, avoiding shell escaping issues.
    Strips CLAUDE* env vars to prevent nested session issues.

    Returns:
        Response text or None on failure.
    """
    claude_bin = find_claude()
    if not claude_bin:
        raise FileNotFoundError(
            "Claude CLI not found. Install it first: "
            "https://docs.anthropic.com/en/docs/claude-code"
        )

    # Clean environment: remove CLAUDE* vars to prevent nesting issues
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}

    # Combine system + user into a single prompt via stdin
    # This avoids multiline --system-prompt CLI argument issues
    combined = f"[System Instructions]\n{system_prompt}\n\n[User Request]\n{user_prompt}"

    cmd = [
        claude_bin, "-p",
        "--output-format", "text",
        "--max-turns", "1",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=combined,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            print(f"  [aq] Claude error: {stderr}" if stderr else "  [aq] Claude returned non-zero")
            return None

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        print(f"  [aq] Claude timed out after {timeout}s")
        return None
    except Exception as e:
        print(f"  [aq] Claude call failed: {e}")
        return None
