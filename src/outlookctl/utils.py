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


def to_local_iso(value) -> str:
    """
    ISO 8601 string with the machine's real UTC offset for a COM date value.

    pywin32 returns Outlook dates (ReceivedTime, Start, End, ...) as the local
    wall-clock time labelled UTC (``09:00+00:00`` for 09:00 in UTC+7). The
    label is dropped and the local offset attached, giving ``09:00+07:00``.
    Naive datetimes are treated as local time. Dates outside the platform's
    range (e.g. Outlook's 4501-01-01 "no date") are returned without offset.
    """
    if not isinstance(value, datetime):
        return value.isoformat()
    wall_clock = value.replace(tzinfo=None)
    try:
        return wall_clock.astimezone().isoformat()
    except (OverflowError, OSError, ValueError):
        return wall_clock.isoformat()


FOLDER_ITEM_TYPES = {
    0: "mail",
    1: "calendar",
    2: "contacts",
    3: "tasks",
    4: "journal",
    5: "notes",
    6: "post",
}


def folder_item_type(default_item_type) -> str:
    """Name for an Outlook Folder.DefaultItemType value ("other" if unknown)."""
    try:
        return FOLDER_ITEM_TYPES.get(int(default_item_type), "other")
    except (TypeError, ValueError):
        return "other"


def folder_spec(store: str, path: str) -> str:
    """The `--folder` value that selects this folder, e.g. by-path:me@x.com/Inbox/Sub."""
    return f"by-path:{store}/{path}" if path else f"by-path:{store}"


def select_stores(names: list[str], store=None, all_stores: bool = False) -> list[int]:
    """
    Indexes of the stores a command works on. ``names`` is default store first.

    - ``store`` given: that store only (case-insensitive); LookupError if unknown
    - ``all_stores``: every store
    - otherwise: the default store only
    """
    if store is not None:
        found = [i for i, name in enumerate(names) if name.lower() == store.lower()]
        if not found:
            raise LookupError(store)
        return found
    if all_stores:
        return list(range(len(names)))
    return [0] if names else []
