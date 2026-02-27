"""Prompt templates for ??? (elaboration) and !!! (answer) markers."""

SYSTEM_EXPAND = """\
You are a thought-structuring assistant. Generate exactly 3 questions that decompose the given concept along 3 axes:
1. [Distinction] How does it differ from similar concepts?
2. [Structure] What are its internal components and stages?
3. [Relation] What are its external dependencies and connections?

Rules:
- Output exactly 3 lines
- Each line: - [Axis] Specific question
- Match the input language
- No preamble, no summary, no explanation
"""

SYSTEM_ANSWER = """\
Provide a concise, practical answer.
- 2 to 5 bullet points
- Each line starts with -
- Match the input language
- No preamble, no summary, no explanation
"""


def build_expand_prompt(
    content: str,
    context: str,
    heading_context: str = "",
    lang: str | None = None,
    custom: str | None = None,
) -> tuple[str, str]:
    """Build system + user prompts for ??? marker.

    Returns:
        (system_prompt, user_prompt)
    """
    system = SYSTEM_EXPAND
    if lang:
        system += f"\nRespond in {lang}."
    if custom:
        system += f"\n{custom}"

    parts = []
    if heading_context:
        parts.append(f"Section context:\n{heading_context}")
    if context:
        parts.append(f"Surrounding context:\n{context}")
    parts.append(f"Concept to elaborate:\n{content}")

    user = "\n\n".join(parts)
    return system, user


def build_answer_prompt(
    content: str,
    context: str,
    heading_context: str = "",
    lang: str | None = None,
    custom: str | None = None,
) -> tuple[str, str]:
    """Build system + user prompts for !!! marker.

    Returns:
        (system_prompt, user_prompt)
    """
    system = SYSTEM_ANSWER
    if lang:
        system += f"\nRespond in {lang}."
    if custom:
        system += f"\n{custom}"

    parts = []
    if heading_context:
        parts.append(f"Section context:\n{heading_context}")
    if context:
        parts.append(f"Surrounding context:\n{context}")
    parts.append(f"Question/topic to answer:\n{content}")

    user = "\n\n".join(parts)
    return system, user
