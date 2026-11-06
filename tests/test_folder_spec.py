"""Tests for folder path parsing."""

from outlookctl.utils import split_store_prefix

STORES = ["Outlook Data File", "hoang.ho@tsp.com.vn"]


def test_store_prefix_is_split_off():
    assert split_store_prefix(["hoang.ho@tsp.com.vn", "Inbox", "Care-HRM"], STORES) == (
        "hoang.ho@tsp.com.vn",
        ["Inbox", "Care-HRM"],
    )


def test_store_prefix_case_insensitive_returns_real_name():
    assert split_store_prefix(["outlook data file", "Contacts"], STORES) == (
        "Outlook Data File",
        ["Contacts"],
    )


def test_no_store_prefix():
    assert split_store_prefix(["Inbox", "Care-HRM"], STORES) == (None, ["Inbox", "Care-HRM"])


def test_store_only():
    assert split_store_prefix(["hoang.ho@tsp.com.vn"], STORES) == ("hoang.ho@tsp.com.vn", [])


def test_empty_parts():
    assert split_store_prefix([], STORES) == (None, [])
