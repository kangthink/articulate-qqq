"""Hierarchical context extraction from file content."""


def extract_context(lines: list[str], marker_line_idx: int, window: int = 10) -> str:
    """Extract context around a marker line.

    Gathers surrounding lines to provide context for the AI prompt.
    Uses a window of lines above and below the marker.

    Args:
        lines: All lines of the file.
        marker_line_idx: 0-based index of the marker line.
        window: Number of context lines above/below.

    Returns:
        Context string with the marker line highlighted.
    """
    start = max(0, marker_line_idx - window)
    end = min(len(lines), marker_line_idx + window + 1)

    context_parts = []

    # Lines above
    above = lines[start:marker_line_idx]
    if above:
        context_parts.append("\n".join(above))

    # The marker line itself (highlighted)
    context_parts.append(f">>> {lines[marker_line_idx].rstrip()} <<<")

    # Lines below
    below = lines[marker_line_idx + 1:end]
    if below:
        context_parts.append("\n".join(below))

    return "\n".join(context_parts)


def extract_heading_context(lines: list[str], marker_line_idx: int) -> str:
    """Extract parent headings (markdown) for hierarchical context.

    Walks upward from the marker to find enclosing headings,
    providing structural context.
    """
    headings = []
    for i in range(marker_line_idx - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith("#"):
            headings.append(stripped)
            # Stop at top-level heading
            if stripped.startswith("# ") and not stripped.startswith("## "):
                break

    headings.reverse()
    return "\n".join(headings) if headings else ""
