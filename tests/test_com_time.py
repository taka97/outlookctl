"""Tests for COM date conversion helpers."""

from datetime import date, datetime, timedelta, timezone

import pytest

from outlookctl.utils import all_day_range, to_com_time


class TestToComTime:
    def test_naive_keeps_wall_clock_and_labels_utc(self):
        result = to_com_time(datetime(2026, 11, 20, 8, 30))
        assert result == datetime(2026, 11, 20, 8, 30, tzinfo=timezone.utc)

    def test_date_becomes_midnight(self):
        assert to_com_time(date(2026, 11, 21)) == datetime(2026, 11, 21, tzinfo=timezone.utc)

    def test_aware_is_converted_to_local_first(self):
        aware = datetime(2026, 11, 20, 1, 30, tzinfo=timezone.utc)
        local = aware.astimezone().replace(tzinfo=None)
        assert to_com_time(aware) == local.replace(tzinfo=timezone.utc)

    def test_aware_with_fixed_offset(self):
        plus7 = timezone(timedelta(hours=7))
        aware = datetime(2026, 11, 20, 8, 30, tzinfo=plus7)
        expected_local = aware.astimezone().replace(tzinfo=None)
        assert to_com_time(aware).replace(tzinfo=None) == expected_local


class TestAllDayRange:
    def test_single_day(self):
        start, end = all_day_range(datetime(2026, 11, 21))
        assert start == datetime(2026, 11, 21, tzinfo=timezone.utc)
        assert end == datetime(2026, 11, 22, tzinfo=timezone.utc)

    def test_end_is_inclusive_last_day(self):
        start, end = all_day_range(datetime(2026, 11, 21, 15, 0), datetime(2026, 11, 23))
        assert start == datetime(2026, 11, 21, tzinfo=timezone.utc)
        assert end == datetime(2026, 11, 24, tzinfo=timezone.utc)

    def test_end_before_start_rejected(self):
        with pytest.raises(ValueError):
            all_day_range(date(2026, 11, 21), date(2026, 11, 20))


class TestToLocalIso:
    def test_utc_labelled_wall_clock_gets_local_offset(self):
        from outlookctl.utils import to_local_iso
        value = datetime(2026, 11, 11, 9, 0, tzinfo=timezone.utc)
        expected = datetime(2026, 11, 11, 9, 0).astimezone().isoformat()
        assert to_local_iso(value) == expected
        assert to_local_iso(value).startswith("2026-11-11T09:00:00")

    def test_naive_treated_as_local(self):
        from outlookctl.utils import to_local_iso
        value = datetime(2026, 11, 11, 9, 0)
        assert to_local_iso(value) == value.astimezone().isoformat()

    def test_round_trip_with_to_com_time(self):
        from outlookctl.utils import to_local_iso
        typed = datetime(2026, 11, 20, 8, 30)
        assert to_local_iso(to_com_time(typed)) == typed.astimezone().isoformat()

    def test_far_future_no_date_value(self):
        from outlookctl.utils import to_local_iso
        result = to_local_iso(datetime(4501, 1, 1, tzinfo=timezone.utc))
        assert result.startswith("4501-01-01T00:00:00")

    def test_plain_date(self):
        from outlookctl.utils import to_local_iso
        assert to_local_iso(date(2026, 11, 21)) == "2026-11-21"
