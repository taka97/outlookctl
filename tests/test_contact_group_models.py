"""Tests for contact group models."""

from outlookctl.models import (
    ContactGroup,
    ContactGroupListResult,
    ContactGroupResult,
    GroupMember,
)


def _group():
    return ContactGroup(
        name="Technical Team",
        store="hoang.ho@tsp.com.vn",
        members=[GroupMember("An", "an.nguyen@tsp.com.vn"), GroupMember("Nam", "nam.tran@tsp.com.vn")],
    )


def test_contact_group_to_dict():
    d = _group().to_dict()
    assert d["name"] == "Technical Team"
    assert d["store"] == "hoang.ho@tsp.com.vn"
    assert d["member_count"] == 2
    assert d["members"][0] == {"name": "An", "email": "an.nguyen@tsp.com.vn"}


def test_list_result_counts_groups():
    d = ContactGroupListResult(groups=[_group()]).to_dict()
    assert d["count"] == 1
    assert d["groups"][0]["name"] == "Technical Team"


def test_group_result_omits_empty_fields():
    d = ContactGroupResult().to_dict()
    assert d == {"version": "1.0", "success": True}


def test_group_result_includes_changes():
    d = ContactGroupResult(group=_group(), added=["a@x"], skipped=["b@x"], message="ok").to_dict()
    assert d["added"] == ["a@x"]
    assert d["skipped"] == ["b@x"]
    assert "removed" not in d
    assert d["group"]["member_count"] == 2
    assert d["message"] == "ok"
