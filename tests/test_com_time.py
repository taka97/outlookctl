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
