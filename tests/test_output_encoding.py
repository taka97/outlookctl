"""Tests for UTF-8 output handling."""

import io
import sys

from outlookctl.cli import _force_utf8_stdio


def test_force_utf8_stdio_allows_vietnamese(monkeypatch):
    buffer = io.BytesIO()
    fake_stdout = io.TextIOWrapper(buffer, encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(io.BytesIO(), encoding="cp1252"))

    _force_utf8_stdio()
    text = "Báo cáo tuần - Team Kỹ thuật"
    print(text)
    sys.stdout.flush()

    assert buffer.getvalue().decode("utf-8").strip() == text


def test_force_utf8_stdio_ignores_streams_without_reconfigure(monkeypatch):
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    _force_utf8_stdio()  # must not raise
