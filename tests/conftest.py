"""
Pytest configuration and shared fixtures for Matilda Client tests.
"""

import json
from typing import Any

import httpx
import pytest

from matilda_client.client import MatildaClient
from matilda_client.manager import MatildaClientManager


@pytest.fixture
def sample_parties_response() -> dict[str, Any]:
    return {
        "startIndex": 0,
        "itemsPerPage": 10,
        "totalItemsCount": 2,
        "totalPages": 1,
        "items": [
            {
                "id": 101,
                "name": "Central Kitchen A",
                "shortName": "CKA",
                "streetAddress": "Main Street 1",
                "postalCode": "5000",
                "postalAddress": "Odense",
                "externalId": "EXT-CK-01",
                "gln": "5790000111222",
                "glnBy": "GLN-ORG",
                "invoiceSystemId": 1,
                "isProducer": True,
                "isRecipeOwner": True,
                "isSupplier": True,
                "isGroceriesOwner": False,
                "isExternal": False,
                "isManager": True,
                "lastModified": "2026-01-15T10:00:00Z",
            },
            {
                "id": 102,
                "name": "Supplier B",
                "shortName": "SUPB",
                "streetAddress": "Harbour Road 5",
                "postalCode": "5000",
                "postalAddress": "Odense",
                "externalId": "EXT-SUP-02",
                "gln": "5790000333444",
                "glnBy": "GLN-ORG",
                "invoiceSystemId": 2,
                "isProducer": False,
                "isRecipeOwner": False,
                "isSupplier": True,
                "isGroceriesOwner": True,
                "isExternal": True,
                "isManager": False,
                "lastModified": "2026-02-01T12:00:00Z",
            },
        ],
    }


@pytest.fixture
def sample_service_user() -> dict[str, Any]:
    return {
        "id": "usr-uuid-1234",
        "externalId": "SU-1001",
        "personalIdNumber": "0101011234",
        "firstName": "Hans",
        "lastName": "Hansen",
        "phone": "+4512345678",
        "email": "hans@example.com",
        "streetAddress": "Vestergade 10",
        "careOf": None,
        "zipCode": "5000",
        "city": "Odense C",
        "servicePeriods": [
            {
                "start": "2026-01-01T00:00:00",
                "end": "2026-12-31T23:59:59",
                "customerExternalId": "DEP01",
                "customerName": "Plejehjemmet Solbakken",
                "externalId": "SP-01",
                "mealType": "Standard Lunch",
                "portionSize": "Normal",
                "allergens": ["Gluten", "Lactose"],
                "enabledWeekDays": ["Monday", "Wednesday", "Friday"],
            }
        ],
        "mealType": "Standard Lunch",
        "comment": "Allergic to nuts as well",
        "portionSize": "Normal",
        "status": "Active",
        "isPausedOrder": False,
        "isFinishedUser": False,
    }


@pytest.fixture
def sample_documents() -> list[dict[str, Any]]:
    return [
        {
            "documentId": "doc-001",
            "name": "DietaryRequirements.pdf",
            "date": "2026-01-10T09:00:00Z",
        },
        {
            "documentId": "doc-002",
            "name": "CarePlan.pdf",
            "date": "2026-02-05T14:30:00Z",
        },
    ]


@pytest.fixture
def mock_matilda_client(sample_parties_response, sample_service_user, sample_documents):
    """
    Returns a MatildaClient equipped with an HTTPX MockTransport handler.
    No live network connection is required.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        method = request.method

        # 1. Party endpoints
        if "/parties" in url_path and method == "GET":
            # Check for specific externalId filter
            if "ExternalId=EXT-CK-01" in str(request.url.query):
                single = {
                    "startIndex": 0,
                    "itemsPerPage": 10,
                    "totalItemsCount": 1,
                    "totalPages": 1,
                    "items": [sample_parties_response["items"][0]],
                }
                return httpx.Response(200, json=single)
            return httpx.Response(200, json=sample_parties_response)

        # 2. Service User Search
        if "/service-user/search" in url_path and method == "POST":
            body = json.loads(request.content.decode("utf-8")) if request.content else {}
            pid = body.get("personalIdNumber", "").replace("-", "").replace(" ", "")
            if pid == "0101011234" or body.get("externalId") == "SU-1001":
                return httpx.Response(200, json=[sample_service_user])
            if pid == "9999999999":
                return httpx.Response(200, json=[])
            return httpx.Response(200, json=[sample_service_user])

        # 3. Attendance endpoints
        if "/service-user/attendance/by-attendees" in url_path and method == "POST":
            return httpx.Response(200, json={"success": True})
        if "/service-user/attendance" in url_path and method == "POST":
            return httpx.Response(200, json={"success": True})

        # 4. Document endpoints
        if "/document" in url_path:
            if method == "GET":
                return httpx.Response(200, json=sample_documents)
            if method == "POST":
                return httpx.Response(201, json="doc-new-123")
            if method == "DELETE":
                if "doc-not-found" in url_path:
                    return httpx.Response(404, json={"title": "Document not found"})
                return httpx.Response(204)

        # 5. Service user single item
        if "/service-user/" in url_path and not url_path.endswith("/service-user"):
            user_id = url_path.split("/")[-1]
            if user_id == "usr-not-found":
                return httpx.Response(404, json={"title": "Not Found", "detail": "User not found"})
            if method == "GET":
                return httpx.Response(200, json=sample_service_user)
            if method == "PUT":
                body = json.loads(request.content.decode("utf-8")) if request.content else {}
                updated = dict(sample_service_user)
                updated.update(body)
                return httpx.Response(200, json=updated)
            if method == "DELETE":
                return httpx.Response(204)

        # 6. Service user create
        if url_path.endswith("/service-user") and method == "POST":
            body = json.loads(request.content.decode("utf-8")) if request.content else {}
            created = dict(sample_service_user)
            created.update(body)
            created["id"] = "usr-created-999"
            return httpx.Response(201, json=created)

        return httpx.Response(404, json={"title": "Endpoint not found"})

    transport = httpx.MockTransport(handler)
    client = MatildaClient(
        organization="test-org",
        api_key="test-api-key",
        enable_logging=False,
    )
    # Inject mock transport into client
    client.client = httpx.Client(
        transport=transport,
        headers={"x-api-key": "test-api-key"},
        base_url=client.base_url,
    )
    return client


@pytest.fixture
def manager(mock_matilda_client):
    """
    Returns a configured MatildaClientManager using the mocked HTTP transport.
    """
    mgr = MatildaClientManager(
        organization="test-org",
        api_key="test-api-key",
        enable_logging=False,
    )
    # Pre-populate lazy _client with mock client
    mgr._client = mock_matilda_client
    return mgr
