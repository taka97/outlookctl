"""
Pure helper functions (no COM dependency) so they can be unit tested anywhere.
"""

import html
import re
from datetime import date, datetime, time, timedelta, timezone

_ANGLE_ADDRESS = re.compile(r"<\s*([^<>\s]+@[^<>\s]+)\s*>\s*$")
_QUOTE_CHARS = ("'", '"')
_BODY_TAG = re.compile(r"<body\b[^>]*>", re.IGNORECASE)

# Default style for text inserted into an HTML mail (matches Outlook defaults).
DEFAULT_FRAGMENT_STYLE = "font-family:Calibri,sans-serif;font-size:11pt"


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


def text_to_html_fragment(text: str, style: str = DEFAULT_FRAGMENT_STYLE) -> str:
    """Convert plain text to an HTML fragment (escaped, line breaks kept)."""
    lines = html.escape(text).replace("\r\n", "\n").split("\n")
    return f'<div style="{style}">' + "<br>\n".join(lines) + "<br><br></div>"


def insert_into_html_body(document: str, fragment: str) -> str:
    """
    Insert an HTML fragment at the top of an HTML document's body.

    The fragment goes right after the opening ``<body ...>`` tag so the
    existing content (for example a quoted reply thread) keeps its formatting.
    Without a body tag the fragment is prepended.
    """
    match = _BODY_TAG.search(document or "")
    if not match:
        return fragment + (document or "")
    return document[: match.end()] + fragment + document[match.end():]


def split_store_prefix(parts: list[str], store_names: list[str]) -> tuple:
    """
    Split a folder path into (store_name, remaining_parts).

    If the first path segment equals a store display name (case-insensitive),
    it is returned as the store name and removed from the parts; otherwise the
    store name is None and the parts are returned unchanged.
    """
    if parts:
        for name in store_names:
            if parts[0].lower() == name.lower():
                return name, list(parts[1:])
    return None, list(parts)


def to_com_time(value) -> datetime:
    """
    Convert a local date/datetime into the value to assign to an Outlook COM
    date property (AppointmentItem.Start/End, ...).

    pywin32 treats a naive datetime as UTC and Outlook then shifts it by the
    machine's UTC offset, so "08:30" was stored as 01:30 on a UTC+7 machine.
    Labelling the local wall-clock time as UTC makes Outlook store exactly the
    time the user typed (verified on Outlook Classic: Start == typed time,
    StartUTC == typed time - offset).

    - date            -> midnight of that day
    - naive datetime  -> treated as local wall-clock time
    - aware datetime  -> converted to local time first
    """
    if not isinstance(value, datetime):
        value = datetime.combine(value, time.min)
    elif value.tzinfo is not None:
        value = value.astimezone().replace(tzinfo=None)
    return value.replace(tzinfo=timezone.utc)


def all_day_range(start, end=None) -> tuple[datetime, datetime]:
    """
    Start/End values for an all-day event.

    ``end`` is the last day of the event (inclusive); Outlook stores the
    exclusive end, i.e. midnight after the last day.
    """
    first_day = start.date() if isinstance(start, datetime) else start
    if end is None:
        last_day = first_day
    else:
        last_day = end.date() if isinstance(end, datetime) else end
    if last_day < first_day:
        raise ValueError("End date must not be before start date.")
    return to_com_time(first_day), to_com_time(last_day + timedelta(days=1))
