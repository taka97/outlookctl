"""Tests for store selection (default store / --store / --all-stores)."""

import pytest

from outlookctl.utils import select_stores

NAMES = ["hoang.ho@tsp.com.vn", "Outlook Data File"]


def test_default_store_only():
    assert select_stores(NAMES) == [0]


def test_all_stores():
    assert select_stores(NAMES, all_stores=True) == [0, 1]


def test_named_store_case_insensitive():
    assert select_stores(NAMES, store="outlook data file") == [1]


def test_named_store_wins_over_all_stores():
    assert select_stores(NAMES, store="Outlook Data File", all_stores=True) == [1]


def test_unknown_store_raises():
    with pytest.raises(LookupError):
        select_stores(NAMES, store="nope")


def test_no_stores():
    assert select_stores([]) == []
    assert select_stores([], all_stores=True) == []
