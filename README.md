# Matilda Client (`matilda-client`)

Python client library for the **Matilda Platform Gateway API** ([Swagger documentation](https://public-ip-matildagw.matildaplatform.com/swagger/index.html)), focusing on the **Party** and **ServiceUsers** endpoints.

Architected after the [KMD Nexus Client](https://github.com/odense-rpa/nexus-client.git) pattern:
- **`MatildaClientManager` facade**: unified, lazy-loaded entry point for all functionality clients
- **Authentication**: API Key (`x-api-key`), Bearer JWT, or HTTP Basic Auth
- **Domain clients**: dedicated modules for Parties, Service Users, and Service User Documents
- **Danish & English aliases**: Full dual-naming support matching Nordic RPA conventions (`hent_service_bruger`, `opret_service_bruger`, `hent_parter`, etc.)
- **Structured models & Enums**: strongly-typed dataclasses with automatic null-pruning (`to_dict` / `from_dict`)
- **HTTPX logging hooks**: redacting sensitive keys, tokens, and binary payloads

---

## Supported Endpoints

| Swagger Tag | Endpoint | Method | Client Method |
|---|---|---|---|
| **Party** | `/v1/organization/{organization}/parties` | `GET` | `matilda.parties.get_parties(...)` / `get_all_parties(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/search` | `POST` | `matilda.service_users.search_service_users(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user` | `POST` | `matilda.service_users.create_service_user(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/{id}` | `GET` | `matilda.service_users.get_service_user(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/{id}` | `PUT` | `matilda.service_users.update_service_user(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/{id}` | `DELETE` | `matilda.service_users.delete_service_user(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/attendance` | `POST` | `matilda.service_users.register_attendance(...)` |
| **ServiceUsers** | `/v1/organization/{organization}/service-user/attendance/by-attendees` | `POST` | `matilda.service_users.register_attendance_by_attendees(...)` |
| **ServiceUserDocuments** | `/v1/organization/{organization}/service-user/{serviceUserId}/document` | `GET` | `matilda.documents.get_documents(...)` |
| **ServiceUserDocuments** | `/v1/organization/{organization}/service-user/{serviceUserId}/document` | `POST` | `matilda.documents.upload_document(...)` |
| **ServiceUserDocuments** | `/v1/organization/{organization}/service-user/{serviceUserId}/document/{documentId}` | `DELETE` | `matilda.documents.delete_document(...)` |

---

## Installation

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -e .
```

---

## Configuration

Copy `env.example` to `.env`:
```bash
cp env.example .env
```

Fill in:
```env
ORGANIZATION=your_organization_slug
API_KEY=your_api_key_here
BASE_URL=https://public-ip-matildagw.matildaplatform.com
```

---

## Quick Start

```python
from matilda_client import MatildaClientManager, ServiceUserRequest, ServicePeriod, DayOfWeek

# 1. Initialize manager (recommended pattern)
matilda = MatildaClientManager(
    organization="odense-kommune",
    api_key="your-api-key",
)

# 2. Parties (central kitchens, suppliers, units)
parties = matilda.parties.get_parties(is_active=True)
all_parties = matilda.parties.get_all_parties()

# 3. Service Users (citizens, care recipients)
# Look up by CPR or Personal ID
citizen = matilda.service_users.get_by_cpr("010101-1234")

# Search by customer/department or date range
citizens = matilda.service_users.search_service_users(customer_external_id="DEP01")

# Create a service user with service periods
new_user = matilda.service_users.create_service_user(
    ServiceUserRequest(
        externalId="SU-2026-001",
        personalIdNumber="0101011234",
        firstName="Grethe",
        lastName="Nielsen",
        servicePeriods=[
            ServicePeriod(
                start="2026-01-01",
                customerExternalId="DEP01",
                mealType="Standard Warm",
                enabledWeekDays=[DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY, DayOfWeek.FRIDAY],
            )
        ],
    )
)

# 4. Service User Documents
docs = matilda.documents.get_documents(service_user_id="usr-uuid-...")
matilda.documents.upload_document(
    service_user_id="usr-uuid-...",
    file="path/to/diet_plan.pdf",
)

# 5. Attendance registration
matilda.service_users.register_attendance([
    {
        "externalId": "EVENT-01",
        "numberOfAttendees": 15,
        "absentServiceUsers": [{"externalId": "SU-2026-001"}],
    }
])
```

---

## Danish / Nordic Aliases

Matching the style in `nexus-client`, all functionality clients provide Danish aliases:

```python
# Hent parter
parter = matilda.parter.hent_parter()
alle_parter = matilda.parter.hent_alle_parter()

# Hent og søg service-brugere
borger = matilda.service_brugere.hent_via_cpr("0101011234")
borgere = matilda.service_brugere.søg_service_brugere(customer_external_id="DEP01")

# Opret og slet
matilda.service_brugere.opret_service_bruger(data)
matilda.service_brugere.slet_service_bruger(user_id)

# Dokumenter
dokumenter = matilda.dokumenter.hent_dokumenter(user_id)
matilda.dokumenter.upload_dokument(user_id, file="notat.pdf")
```

---

## Running Tests

The test suite includes full offline mock fixtures:

```bash
uv run pytest
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
