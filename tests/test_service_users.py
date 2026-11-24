"""
Unit tests for ServiceUsersClient functionality.
"""

from matilda_client.models import (
    AttendanceRequest,
    AttendingServiceUsersRequest,
    DayOfWeek,
    ServicePeriod,
    ServiceUserIdentifier,
    ServiceUserRequest,
    ServiceUserResponse,
)


def test_search_service_users(manager):
    res = manager.service_users.search_service_users(personal_id_number="010101-1234")
    assert len(res) == 1
    assert res[0]["firstName"] == "Hans"
    assert res[0]["externalId"] == "SU-1001"


def test_search_service_users_empty(manager):
    res = manager.service_users.search_service_users(personal_id_number="999999-9999")
    assert len(res) == 0


def test_search_service_users_typed(manager):
    res = manager.service_users.search_service_users_typed(external_id="SU-1001")
    assert len(res) == 1
    assert isinstance(res[0], ServiceUserResponse)
    assert res[0].firstName == "Hans"
    assert res[0].personalIdNumber == "0101011234"


def test_get_service_user_by_id(manager):
    user = manager.service_users.get_service_user("usr-uuid-1234")
    assert user is not None
    assert user["id"] == "usr-uuid-1234"
    assert user["lastName"] == "Hansen"


def test_get_service_user_not_found(manager):
    user = manager.service_users.get_service_user("usr-not-found")
    assert user is None


def test_get_by_cpr(manager):
    user = manager.service_users.get_by_cpr("010101-1234")
    assert user is not None
    assert user["firstName"] == "Hans"


def test_get_by_external_id(manager):
    user = manager.service_users.get_by_external_id("SU-1001")
    assert user is not None
    assert user["id"] == "usr-uuid-1234"


def test_create_service_user(manager):
    req = ServiceUserRequest(
        externalId="SU-NEW-01",
        personalIdNumber="0202021234",
        firstName="Grethe",
        lastName="Nielsen",
        servicePeriods=[
            ServicePeriod(
                start="2026-03-01",
                customerExternalId="DEP02",
                mealType="Diet Lunch",
                enabledWeekDays=[DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY],
            )
        ],
    )
    res = manager.service_users.create_service_user(req)
    assert res["id"] == "usr-created-999"
    assert res["firstName"] == "Grethe"


def test_update_service_user(manager):
    req = ServiceUserRequest(
        externalId="SU-1001",
        firstName="Hans Peter",
        servicePeriods=[],
    )
    res = manager.service_users.update_service_user("usr-uuid-1234", req)
    assert res["firstName"] == "Hans Peter"


def test_delete_service_user(manager):
    success = manager.service_users.delete_service_user("usr-uuid-1234")
    assert success is True


def test_register_attendance(manager):
    att = AttendanceRequest(
        externalId="MEAL-EVENT-01",
        numberOfAttendees=12,
        absentServiceUsers=[ServiceUserIdentifier(externalId="SU-1001")],
    )
    res = manager.service_users.register_attendance([att])
    assert res == {"success": True} or res is True


def test_register_attendance_by_attendees(manager):
    req = AttendingServiceUsersRequest(
        externalId="MEAL-EVENT-02",
        mealId="MEAL-10",
        attendingServiceUsers=[
            ServiceUserIdentifier(personalIdNumber="0101011234"),
        ],
    )
    res = manager.service_users.register_attendance_by_attendees([req])
    assert res == {"success": True} or res is True


def test_service_users_danish_aliases(manager):
    u = manager.service_brugere.hent_via_cpr("010101-1234")
    assert u is not None
    assert u["firstName"] == "Hans"
