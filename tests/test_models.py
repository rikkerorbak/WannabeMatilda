"""
Unit tests for Models serialization and deserialization.
"""

from matilda_client.models import (
    AttendanceRequest,
    CommonStatus,
    DayOfWeek,
    OrderType,
    PartyPaginationResponse,
    ServicePeriod,
    ServiceUserIdentifier,
    ServiceUserRequest,
    ServiceUserResponse,
)


def test_service_period_to_dict():
    sp = ServicePeriod(
        start="2026-01-01",
        end="2026-12-31",
        customerExternalId="CUST01",
        mealType="Lunch",
        enabledWeekDays=[DayOfWeek.MONDAY, DayOfWeek.FRIDAY],
        orderType=OrderType.TRAY,
    )
    d = sp.to_dict()
    assert d["start"] == "2026-01-01"
    assert d["enabledWeekDays"] == ["Monday", "Friday"]
    assert d["orderType"] == "Tray"
    assert "comment" not in d  # None stripped by clean_dict


def test_service_user_request_to_dict():
    req = ServiceUserRequest(
        externalId="SU-1",
        servicePeriods=[
            ServicePeriod(start="2026-01-01", mealType="Breakfast"),
        ],
        firstName="Test",
        lastName="User",
    )
    d = req.to_dict()
    assert d["externalId"] == "SU-1"
    assert len(d["servicePeriods"]) == 1
    assert d["servicePeriods"][0]["mealType"] == "Breakfast"
    assert d["firstName"] == "Test"


def test_service_user_response_from_dict():
    raw = {
        "id": "123",
        "externalId": "EXT-1",
        "personalIdNumber": "0101011234",
        "firstName": "John",
        "servicePeriods": [],
        "status": CommonStatus.ACTIVE.value,
    }
    resp = ServiceUserResponse.from_dict(raw)
    assert resp.id == "123"
    assert resp.externalId == "EXT-1"
    assert resp.status == "Active"


def test_party_pagination_from_dict():
    raw = {
        "startIndex": 0,
        "itemsPerPage": 10,
        "totalItemsCount": 1,
        "totalPages": 1,
        "items": [
            {
                "id": 1,
                "name": "Central Kitchen",
                "isProducer": True,
            }
        ],
    }
    res = PartyPaginationResponse.from_dict(raw)
    assert res.totalItemsCount == 1
    assert len(res.items) == 1
    assert res.items[0].id == 1
    assert res.items[0].name == "Central Kitchen"
    assert res.items[0].isProducer is True


def test_attendance_request_to_dict():
    att = AttendanceRequest(
        externalId="EVENT-1",
        numberOfAttendees=5,
        absentServiceUsers=[ServiceUserIdentifier(externalId="U1")],
    )
    d = att.to_dict()
    assert d["externalId"] == "EVENT-1"
    assert d["numberOfAttendees"] == 5
    assert d["absentServiceUsers"] == [{"externalId": "U1"}]
