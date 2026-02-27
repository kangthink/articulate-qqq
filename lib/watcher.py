"""Polling-based file watcher."""

import fnmatch
import os
import signal
import sys
import time
from pathlib import Path

from . import Config, PID_FILE
from .ai import PROVIDERS
from .processor import process_file


def _write_pid():
    """Write current PID to pid file."""
    PID_FILE.write_text(str(os.getpid()))


def _remove_pid():
    """Remove pid file."""
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _collect_files(target: Path, glob_pattern: str) -> list[Path]:
    """Collect files matching glob pattern under target."""
    if target.is_file():
        if fnmatch.fnmatch(target.name, glob_pattern):
            return [target]
        return [target]  # Single file always included regardless of pattern

    files = []
    for f in target.rglob("*"):
        if f.is_file() and fnmatch.fnmatch(f.name, glob_pattern):
            # Skip hidden directories
            parts = f.relative_to(target).parts
            if any(p.startswith(".") for p in parts):
                continue
            files.append(f)
    return sorted(files)


def watch(target: Path, config: Config):
    """Poll target for file changes and process markers.

    Args:
        target: File or directory to watch.
        config: Runtime configuration.
    """
    _write_pid()

    # Track file modification times
    mtimes: dict[Path, float] = {}

    running = True

    def _handle_signal(signum, frame):
        nonlocal running
        running = False
        print("\n[aq] Stopping watcher...")

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    provider_name = PROVIDERS.get(config.model, {}).get("name", config.model)
    print(f"[aq] Watching: {target} — powered by {provider_name}")
    print(f"[aq] Pattern: {config.glob_pattern} | Poll: {config.poll_interval}s")
    print(f"[aq] Press Ctrl+C to stop")

    try:
        while running:
            files = _collect_files(target, config.glob_pattern)

            for f in files:
                try:
                    mtime = f.stat().st_mtime
                except OSError:
                    continue

                prev_mtime = mtimes.get(f)
                mtimes[f] = mtime

                if prev_mtime is None:
                    # First scan — skip to avoid processing on startup
                    continue

                if mtime > prev_mtime:
                    try:
                        process_file(f, config)
                    except Exception as e:
                        print(f"[aq] Error processing {f.name}: {e}")

            time.sleep(config.poll_interval)

    finally:
        _remove_pid()
        print("[aq] Watcher stopped.")


def stop_watcher() -> bool:
    """Stop a running watcher by sending SIGTERM to its PID.

    Returns:
        True if a process was signaled, False otherwise.
    """
    if not PID_FILE.exists():
        print("[aq] No running watcher found.")
        return False

    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        print(f"[aq] Sent stop signal to PID {pid}")
        _remove_pid()
        return True
    except ProcessLookupError:
        print("[aq] Watcher process not found (stale PID file removed).")
        _remove_pid()
        return False
    except ValueError:
        print("[aq] Invalid PID file.")
        _remove_pid()
        return False
