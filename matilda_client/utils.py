"""
Utility functions for Matilda Client.

Provides helpers for:
- CPR / Personal ID sanitization and validation (Danish CPR / Swedish personnummer)
- Request payload cleaning (removing None fields)
- DateTime ISO string formatting
"""

from datetime import date, datetime
from typing import Any


def is_valid_cpr(cpr: str) -> bool:
    """
    Validate a Danish CPR number.

    :param cpr: CPR number string (with or without hyphen).
    :return: True if the CPR number is structurally valid, False otherwise.
    """
    if not cpr:
        return False

    cleaned = cpr.replace("-", "").replace(" ", "").strip()
    if len(cleaned) != 10 or not cleaned.isnumeric():
        return False

    try:
        datetime.strptime(cleaned[:6], "%d%m%y")
    except ValueError:
        return False

    return True


def sanitize_cpr(cpr: str, strict: bool = False) -> str:
    """
    Sanitize a CPR number by removing spaces and dashes.

    :param cpr: CPR number to clean.
    :param strict: If True, validates against CPR date rules and raises ValueError if invalid.
    :return: Cleaned numeric CPR string.
    """
    if not cpr:
        raise ValueError("CPR number cannot be empty.")

    cleaned = cpr.replace("-", "").replace(" ", "").strip()

    if strict and not is_valid_cpr(cleaned):
        raise ValueError(f"Invalid CPR number: {cpr}")

    return cleaned


def sanitize_personal_id(personal_id: str) -> str:
    """
    Sanitize personal identity number (removes spaces, optional hyphens).

    Supports Danish CPR (10 digits) and Swedish personnummer (10 or 12 digits).
    """
    if not personal_id:
        return ""
    return personal_id.replace(" ", "").strip()


def clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively remove None values from dictionary.

    Useful for constructing clean API request payloads where nulls should be omitted.
    """
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, dict):
            cleaned_sub = clean_dict(value)
            result[key] = cleaned_sub
        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    cleaned_list.append(clean_dict(item))
                elif item is not None:
                    cleaned_list.append(item)
            result[key] = cleaned_list
        else:
            result[key] = value
    return result


def to_iso_datetime(dt: datetime | date | str | None) -> str | None:
    """
    Convert a datetime, date, or ISO string to ISO 8601 formatted string.
    """
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, date):
        return datetime(dt.year, dt.month, dt.day).isoformat()
    return str(dt)
