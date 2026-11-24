"""
Service Users client for Matilda Platform.

Handles Service Users (citizens/care recipients) lifecycle, searching,
attendance tracking, and meal registrations.
Endpoints:
- POST   /v1/service-user/search
- POST   /v1/service-user
- GET    /v1/service-user/{id}
- PUT    /v1/service-user/{id}
- DELETE /v1/service-user/{id}
- POST   /v1/service-user/attendance
- POST   /v1/service-user/attendance/by-attendees
"""

from typing import Any

import httpx

from matilda_client.client import MatildaClient
from matilda_client.models import (
    AttendanceRequest,
    AttendingServiceUsersRequest,
    ServiceUserFilter,
    ServiceUserRequest,
    ServiceUserResponse,
)
from matilda_client.utils import clean_dict, sanitize_cpr, sanitize_personal_id, to_iso_datetime


class ServiceUsersClient:
    """
    Client for Service Users operations in Matilda Platform.

    IMPORTANT: Do not instantiate directly. Use MatildaClientManager:
        matilda = MatildaClientManager(...)
        users = matilda.service_users.search_service_users(...)
    """

    SEARCH_ENDPOINT = "/integrations/gateway/v1/service-user/Search"
    BASE_ENDPOINT = "/integrations/gateway/v1/service-user"
    DETAIL_ENDPOINT = "/integrations/gateway/v1/service-user/{id}"
    ATTENDANCE_ENDPOINT = "/integrations/gateway/v1/service-user/attendance"
    ATTENDEES_ENDPOINT = "/integrations/gateway/v1/service-user/attendance/by-attendees"

    def __init__(self, matilda_client: MatildaClient):
        self.client = matilda_client

    def search_service_users(
        self,
        filter_criteria: ServiceUserFilter | dict[str, Any] | None = None,
        personal_id_number: str | None = None,
        customer_external_id: str | None = None,
        external_id: str | None = None,
        service_period_start: Any | None = None,
        service_period_end: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for service users matching specified criteria.

        :param filter_criteria: Existing ServiceUserFilter or dict of filter options.
        :param personal_id_number: Filter by CPR / Personnummer.
        :param customer_external_id: Filter by customer / department external ID.
        :param external_id: Filter by service user external ID.
        :param service_period_start: Filter service periods starting from this date.
        :param service_period_end: Filter service periods ending before this date.
        :return: List of service user dictionaries matching criteria.
        """
        if filter_criteria is not None:
            if isinstance(filter_criteria, ServiceUserFilter):
                payload = filter_criteria.to_dict()
            else:
                payload = clean_dict(filter_criteria)
        else:
            cleaned_personal_id = (
                sanitize_personal_id(personal_id_number) if personal_id_number else None
            )
            payload = clean_dict(
                {
                    "personalIdNumber": cleaned_personal_id,
                    "customerExternalId": customer_external_id,
                    "externalId": external_id,
                    "servicePeriodStart": to_iso_datetime(service_period_start),
                    "servicePeriodEnd": to_iso_datetime(service_period_end),
                }
            )

        response = self.client.post(self.SEARCH_ENDPOINT, json=payload)
        return response.json()

    def search_service_users_typed(
        self,
        **kwargs,
    ) -> list[ServiceUserResponse]:
        """
        Search for service users and return strongly-typed ServiceUserResponse objects.
        """
        results = self.search_service_users(**kwargs)
        return [ServiceUserResponse.from_dict(item) for item in results]

    def get_service_user(self, service_user_id: str) -> dict[str, Any] | None:
        """
        Get a service user by Matilda internal ID.

        :param service_user_id: Internal ID (GUID / string) of the service user.
        :return: Service user dictionary or None if not found (404).
        """
        endpoint = self.DETAIL_ENDPOINT.replace("{id}", str(service_user_id))
        try:
            response = self.client.get(endpoint)
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_service_user_typed(self, service_user_id: str) -> ServiceUserResponse | None:
        """
        Get a service user by internal ID parsed as ServiceUserResponse.
        """
        data = self.get_service_user(service_user_id)
        return ServiceUserResponse.from_dict(data) if data else None

    def get_by_cpr(self, cpr: str) -> dict[str, Any] | None:
        """
        Convenience method to retrieve a single service user by CPR / personalIdNumber.

        :param cpr: CPR number (e.g. '010101-1234' or '0101011234').
        :return: First matching service user dict, or None if not found.
        """
        cleaned_cpr = sanitize_cpr(cpr, strict=False)
        results = self.search_service_users(personal_id_number=cleaned_cpr)
        return results[0] if results else None

    def get_by_external_id(self, external_id: str) -> dict[str, Any] | None:
        """
        Convenience method to retrieve a service user by externalId.

        :param external_id: The external identifier string.
        :return: First matching service user dict, or None if not found.
        """
        results = self.search_service_users(external_id=external_id)
        for user in results:
            if str(user.get("externalId")) == str(external_id):
                return user
        return results[0] if results else None

    def create_service_user(
        self,
        service_user: ServiceUserRequest | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create a new service user.

        :param service_user: ServiceUserRequest object or dictionary payload.
        :return: Created service user dictionary.
        """
        if isinstance(service_user, ServiceUserRequest):
            payload = service_user.to_dict()
        else:
            payload = clean_dict(service_user)

        response = self.client.post(self.BASE_ENDPOINT, json=payload)
        return response.json()

    def update_service_user(
        self,
        service_user_id: str,
        service_user: ServiceUserRequest | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update an existing service user by ID.

        :param service_user_id: ID of the service user to update.
        :param service_user: ServiceUserRequest object or dictionary payload.
        :return: Updated service user dictionary.
        """
        if isinstance(service_user, ServiceUserRequest):
            payload = service_user.to_dict()
        else:
            payload = clean_dict(service_user)

        endpoint = self.DETAIL_ENDPOINT.replace("{id}", str(service_user_id))
        response = self.client.put(endpoint, json=payload)
        return response.json()

    def delete_service_user(self, service_user_id: str) -> bool:
        """
        Delete a service user by ID.

        :param service_user_id: ID of the service user to delete.
        :return: True if deleted successfully, False if user did not exist (404).
        """
        endpoint = self.DETAIL_ENDPOINT.replace("{id}", str(service_user_id))
        try:
            response = self.client.delete(endpoint)
            return response.status_code in (200, 204)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise

    def register_attendance(
        self,
        attendances: list[AttendanceRequest | dict[str, Any]],
    ) -> Any:
        """
        Register attendance or absences for service users.

        Endpoint: POST /v1/organization/{organization}/service-user/attendance

        :param attendances: List of AttendanceRequest items or dicts.
        :return: Server response data (usually empty or confirmation).
        """
        payload = []
        for att in attendances:
            if isinstance(att, AttendanceRequest):
                payload.append(att.to_dict())
            else:
                payload.append(clean_dict(att))

        response = self.client.post(self.ATTENDANCE_ENDPOINT, json=payload)
        try:
            return response.json()
        except Exception:
            return response.status_code == 200

    def register_attendance_by_attendees(
        self,
        attending_requests: list[AttendingServiceUsersRequest | dict[str, Any]],
    ) -> Any:
        """
        Register attending service users for meals.

        Endpoint: POST /v1/organization/{organization}/service-user/attendance/by-attendees

        :param attending_requests: List of AttendingServiceUsersRequest items or dicts.
        :return: Server response data (usually empty or confirmation).
        """
        payload = []
        for req in attending_requests:
            if isinstance(req, AttendingServiceUsersRequest):
                payload.append(req.to_dict())
            else:
                payload.append(clean_dict(req))

        response = self.client.post(self.ATTENDEES_ENDPOINT, json=payload)
        try:
            return response.json()
        except Exception:
            return response.status_code == 200

    # Danish / Nordic aliases (matching nexus-client style)
    søg_service_brugere = search_service_users
    hent_service_bruger = get_service_user
    hent_via_cpr = get_by_cpr
    hent_via_eksternt_id = get_by_external_id
    opret_service_bruger = create_service_user
    opdater_service_bruger = update_service_user
    slet_service_bruger = delete_service_user
    registrer_fremmøde = register_attendance
    registrer_fremmøde_via_deltagere = register_attendance_by_attendees


# Class aliases
ServiceUserClient = ServiceUsersClient
ServiceBrugerClient = ServiceUsersClient
