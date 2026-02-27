"""articulate-qqq: AI thought expansion via ??? and !!! markers."""

from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.1.0"
APP_NAME = "aq"

# Marker constants
MARKER_EXPAND = "???"
MARKER_ANSWER = "!!!"

# Defaults
DEFAULT_POLL_INTERVAL = 1.0
DEFAULT_TIMEOUT = 120
DEFAULT_GLOB = "*.md"
PID_FILE = Path("/tmp/aq.pid")


@dataclass
class Config:
    """Runtime configuration."""
    dry_run: bool = False
    lang: str | None = None
    custom_prompt: str | None = None
    poll_interval: float = DEFAULT_POLL_INTERVAL
    glob_pattern: str = DEFAULT_GLOB
    timeout: int = DEFAULT_TIMEOUT
    structure: bool = False
