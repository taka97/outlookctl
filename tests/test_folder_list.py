"""Tests for the folders command helpers and models."""

from outlookctl.models import FolderEntry, FolderListResult
from outlookctl.utils import folder_item_type, folder_spec


def test_folder_item_type_known_values():
    assert folder_item_type(0) == "mail"
    assert folder_item_type(1) == "calendar"
    assert folder_item_type(2) == "contacts"


def test_folder_item_type_unknown_or_missing():
    assert folder_item_type(99) == "other"
    assert folder_item_type(None) == "other"


def test_folder_spec_includes_store():
    assert folder_spec("me@x.com", "Inbox/Care-HRM") == "by-path:me@x.com/Inbox/Care-HRM"


def test_folder_spec_store_root():
    assert folder_spec("me@x.com", "") == "by-path:me@x.com"


def test_folder_entry_to_dict():
    entry = FolderEntry(
        name="Care-HRM", path="Inbox/Care-HRM", store="me@x.com",
        item_type="mail", depth=2, item_count=10, unread_count=3, subfolder_count=1,
    )
    assert entry.to_dict() == {
        "name": "Care-HRM",
        "path": "Inbox/Care-HRM",
        "store": "me@x.com",
        "folder_spec": "by-path:me@x.com/Inbox/Care-HRM",
        "item_type": "mail",
        "depth": 2,
        "subfolder_count": 1,
        "item_count": 10,
        "unread_count": 3,
    }


def test_folder_entry_omits_unknown_counts():
    entry = FolderEntry(name="X", path="X", store="s", item_type="mail", depth=1)
    data = entry.to_dict()
    assert "item_count" not in data and "unread_count" not in data


def test_folder_list_result():
    entry = FolderEntry(name="X", path="X", store="s", item_type="mail", depth=1)
    data = FolderListResult(folders=[entry]).to_dict()
    assert data["version"] == "1.0"
    assert data["count"] == 1
    assert data["folders"][0]["name"] == "X"
