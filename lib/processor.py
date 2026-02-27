"""Core processing pipeline: scan markers, invoke Claude, insert results."""

import re
from dataclasses import dataclass
from pathlib import Path

from . import MARKER_EXPAND, MARKER_ANSWER, Config
from .context import extract_context, extract_heading_context
from .prompts import build_expand_prompt, build_answer_prompt
from .claude import call_claude
from .formatter import detect_indent, detect_indent_unit, indent_block

# Pattern: optional indent, optional content, then ??? or !!!
MARKER_RE = re.compile(r'^([ \t]*)(.*?)\s*(\?\?\?|!!!)\s*$')


@dataclass
class MarkerHit:
    """A detected marker in a file."""
    line_idx: int
    indent: str
    content: str
    marker_type: str  # "???" or "!!!"


def scan_markers(lines: list[str]) -> list[MarkerHit]:
    """Scan all lines for ??? and !!! markers.

    Returns hits sorted by line index (ascending).
    """
    hits = []
    for i, line in enumerate(lines):
        m = MARKER_RE.match(line)
        if m:
            hits.append(MarkerHit(
                line_idx=i,
                indent=m.group(1),
                content=m.group(2).strip(),
                marker_type=m.group(3),
            ))
    return hits


def process_marker(
    lines: list[str],
    hit: MarkerHit,
    config: Config,
) -> str | None:
    """Process a single marker: build prompt, call Claude, return result.

    Returns the Claude response text, or None on failure.
    """
    context = extract_context(lines, hit.line_idx)
    heading_ctx = extract_heading_context(lines, hit.line_idx)

    if hit.marker_type == MARKER_EXPAND:
        system, user = build_expand_prompt(
            content=hit.content,
            context=context,
            heading_context=heading_ctx,
            lang=config.lang,
            custom=config.custom_prompt,
            structure=config.structure,
        )
    else:
        system, user = build_answer_prompt(
            content=hit.content,
            context=context,
            heading_context=heading_ctx,
            lang=config.lang,
            custom=config.custom_prompt,
        )

    if config.dry_run:
        marker_label = "EXPAND" if hit.marker_type == MARKER_EXPAND else "ANSWER"
        print(f"  [dry-run] L{hit.line_idx + 1}: {marker_label} '{hit.content}'")
        print(f"  [dry-run] System: {system[:80]}...")
        print(f"  [dry-run] User: {user[:80]}...")
        return None

    return call_claude(system, user, timeout=config.timeout)


def process_file(filepath: Path, config: Config) -> int:
    """Process all markers in a file.

    Scans for markers, processes bottom-to-top to preserve line numbers,
    removes consumed markers, and inserts results.

    Args:
        filepath: Path to the file to process.
        config: Runtime configuration.

    Returns:
        Number of markers successfully processed.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    hits = scan_markers(lines)
    if not hits:
        return 0

    marker_label = lambda h: "???" if h.marker_type == MARKER_EXPAND else "!!!"
    print(f"[aq] {filepath.name}: {len(hits)} marker(s) found — powered by Claude AI")

    indent_unit = detect_indent_unit(lines)
    processed = 0

    # Process bottom-to-top to preserve line numbers
    for hit in reversed(hits):
        label = marker_label(hit)
        print(f"  [{label}] L{hit.line_idx + 1}: {hit.content or '(no content)'}")

        result = process_marker(lines, hit, config)

        if result is None and not config.dry_run:
            print(f"  [{label}] Failed — marker preserved for retry")
            continue

        if config.dry_run:
            processed += 1
            continue

        # Build indented result block
        formatted = indent_block(result, hit.indent, indent_unit)
        result_lines = formatted.splitlines()

        # Replace marker line with: content line (without marker) + result
        if hit.content:
            # Keep the content, remove the marker
            new_lines = [hit.indent + hit.content] + result_lines
        else:
            # Marker-only line: replace entirely with result
            new_lines = result_lines

        lines[hit.line_idx:hit.line_idx + 1] = new_lines
        processed += 1

    if processed > 0 and not config.dry_run:
        # Write back with trailing newline
        filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[aq] {filepath.name}: {processed} marker(s) processed")

    return processed
