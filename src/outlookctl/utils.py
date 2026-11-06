"""
Pure helper functions (no COM dependency) so they can be unit tested anywhere.
"""

import re

_ANGLE_ADDRESS = re.compile(r"<\s*([^<>\s]+@[^<>\s]+)\s*>\s*$")
_QUOTE_CHARS = ("'", '"')


def normalize_recipient(value: str) -> str:
    """
    Clean a single recipient string.

    - Strips surrounding whitespace.
    - ``Name <user@example.com>`` becomes ``user@example.com``.
    - Removes matching single/double quotes wrapped around the value, e.g.
      ``'user@example.com'`` (Outlook keeps such quotes as part of the address,
      which produces an invalid recipient).
    - Values that are not e-mail addresses (contact group or display names such
      as ``Technical Team``) are kept as-is apart from the cleanup above.
    """
    cleaned = value.strip()
    match = _ANGLE_ADDRESS.search(cleaned)
    if match:
        cleaned = match.group(1)
    while (
        len(cleaned) >= 2
        and cleaned[0] == cleaned[-1]
        and cleaned[0] in _QUOTE_CHARS
    ):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def normalize_recipients(values: list[str]) -> list[str]:
    """Normalize recipients, drop empty entries and case-insensitive duplicates (order kept)."""
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = normalize_recipient(value)
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result
