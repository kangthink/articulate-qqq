"""Indentation detection and output formatting."""

import re


def detect_indent(line: str) -> str:
    """Extract leading whitespace from a line."""
    match = re.match(r'^([ \t]*)', line)
    return match.group(1) if match else ""


def detect_indent_unit(lines: list[str]) -> str:
    """Detect the indentation unit used in the file (e.g., 2 spaces, 4 spaces, tab)."""
    for line in lines:
        stripped = line.lstrip()
        if not stripped:
            continue
        indent = line[:len(line) - len(stripped)]
        if indent:
            # Return the smallest non-empty indent as the unit
            return indent
    return "  "  # default: 2 spaces


def indent_block(text: str, base_indent: str, indent_unit: str = "  ") -> str:
    """Indent a block of text one level deeper than base_indent.

    Each non-empty line gets base_indent + indent_unit prepended.
    Empty lines are preserved as-is.
    """
    child_indent = base_indent + indent_unit
    result_lines = []
    for line in text.splitlines():
        if line.strip():
            result_lines.append(child_indent + line)
        else:
            result_lines.append("")
    return "\n".join(result_lines)
