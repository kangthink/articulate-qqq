"""Multi-provider AI CLI wrapper. Supports Claude, Gemini, Codex."""

import os
import subprocess
import shutil
from dataclasses import dataclass

PROVIDERS = {
    "claude": {
        "name": "Claude",
        "bins": ["~/.local/bin/claude", "/usr/local/bin/claude"],
        "cmd": "claude",
        "url": "https://docs.anthropic.com/en/docs/claude-code",
    },
    "gemini": {
        "name": "Gemini",
        "bins": [],
        "cmd": "gemini",
        "url": "https://github.com/google-gemini/gemini-cli",
    },
    "codex": {
        "name": "Codex",
        "bins": [],
        "cmd": "codex",
        "url": "https://github.com/openai/codex",
    },
}

DEFAULT_PROVIDER = "claude"


def find_binary(provider: str) -> str | None:
    """Find the CLI binary for a provider."""
    info = PROVIDERS.get(provider)
    if not info:
        return None

    # Check known paths first
    for path in info["bins"]:
        expanded = os.path.expanduser(path)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return expanded

    return shutil.which(info["cmd"])


def _build_claude_call(combined: str) -> tuple[list[str], str, dict]:
    """Build Claude CLI command."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    cmd = ["claude", "-p", "--output-format", "text", "--max-turns", "1"]
    return cmd, combined, env


def _build_gemini_call(combined: str) -> tuple[list[str], str, dict]:
    """Build Gemini CLI command."""
    env = dict(os.environ)
    cmd = ["gemini", "-p", combined, "--output-format", "text"]
    return cmd, None, env  # None input = no stdin


def _build_codex_call(combined: str) -> tuple[list[str], str, dict]:
    """Build Codex CLI command."""
    env = dict(os.environ)
    cmd = ["codex", "exec", combined]
    return cmd, None, env


_BUILDERS = {
    "claude": _build_claude_call,
    "gemini": _build_gemini_call,
    "codex": _build_codex_call,
}


def call_ai(
    system_prompt: str,
    user_prompt: str,
    provider: str = DEFAULT_PROVIDER,
    timeout: int = 120,
) -> str | None:
    """Call an AI CLI and return the response text.

    Args:
        system_prompt: System-level instructions.
        user_prompt: User prompt/question.
        provider: AI provider (claude, gemini, codex).
        timeout: Timeout in seconds.

    Returns:
        Response text or None on failure.
    """
    info = PROVIDERS.get(provider)
    if not info:
        print(f"  [aq] Unknown provider: {provider}")
        print(f"  [aq] Available: {', '.join(PROVIDERS.keys())}")
        return None

    binary = find_binary(provider)
    if not binary:
        raise FileNotFoundError(
            f"{info['name']} CLI not found. Install: {info['url']}"
        )

    combined = f"[System Instructions]\n{system_prompt}\n\n[User Request]\n{user_prompt}"

    builder = _BUILDERS[provider]
    cmd, stdin_input, env = builder(combined)

    # Replace command name with full path
    cmd[0] = binary

    try:
        result = subprocess.run(
            cmd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            label = info["name"]
            print(f"  [aq] {label} error: {stderr}" if stderr else f"  [aq] {label} returned non-zero")
            return None

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        print(f"  [aq] {info['name']} timed out after {timeout}s")
        return None
    except Exception as e:
        print(f"  [aq] {info['name']} call failed: {e}")
        return None
