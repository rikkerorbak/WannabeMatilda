"""
Unit tests for CPR and utility functions.
"""

from datetime import date, datetime

import pytest

from matilda_client.utils import (
    clean_dict,
    is_valid_cpr,
    sanitize_cpr,
    sanitize_personal_id,
    to_iso_datetime,
)


def test_is_valid_cpr():
    # Valid birthdates
    assert is_valid_cpr("0101011234") is True
    assert is_valid_cpr("311299-1234") is True
    assert is_valid_cpr("010101-1234") is True

    # Invalid
    assert is_valid_cpr("") is False
    assert is_valid_cpr("12345") is False
    assert is_valid_cpr("9999991234") is False  # 99th day does not exist
    assert is_valid_cpr("abcdef1234") is False


def test_sanitize_cpr():
    assert sanitize_cpr("010101-1234") == "0101011234"
    assert sanitize_cpr(" 010101 1234 ") == "0101011234"

    with pytest.raises(ValueError):
        sanitize_cpr("")

    with pytest.raises(ValueError):
        sanitize_cpr("9999991234", strict=True)


def test_sanitize_personal_id():
    assert sanitize_personal_id(" 19800101-1234 ") == "19800101-1234"
    assert sanitize_personal_id("010101-1234") == "010101-1234"
    assert sanitize_personal_id("") == ""


def test_clean_dict():
    data = {
        "a": 1,
        "b": None,
        "nested": {"c": "hello", "d": None},
        "list": [{"x": 10, "y": None}, None, 20],
    }
    cleaned = clean_dict(data)
    assert cleaned == {
        "a": 1,
        "nested": {"c": "hello"},
        "list": [{"x": 10}, 20],
    }


def test_to_iso_datetime():
    dt = datetime(2026, 5, 12, 14, 30, 0)
    assert to_iso_datetime(dt) == "2026-05-12T14:30:00"

    d = date(2026, 5, 12)
    assert to_iso_datetime(d) == "2026-05-12T00:00:00"

    assert to_iso_datetime(None) is None
    assert to_iso_datetime("2026-05-12") == "2026-05-12"
