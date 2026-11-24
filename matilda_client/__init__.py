"""
Matilda Platform Python Client

Library for interacting with the Matilda Platform Gateway API
(Party, ServiceUsers, and ServiceUserDocuments endpoints).

Recommended usage:
    from matilda_client import MatildaClientManager

    matilda = MatildaClientManager(organization="your-org", api_key="your-api-key")
    parties = matilda.parties.get_parties()
    users = matilda.service_users.search_service_users()
"""

from .client import MatildaClient
from .functionality.documents import (
    DocumentClient,
    DokumentClient,
    ServiceUserDocumentsClient,
)
from .functionality.parties import ParterClient, PartiesClient, PartyClient
from .functionality.service_users import (
    ServiceBrugerClient,
    ServiceUserClient,
    ServiceUsersClient,
)
from .hooks import create_response_logging_hook
from .manager import MatildaClientManager
from .models import (
    AttendanceRequest,
    AttendingServiceUsersRequest,
    CommonStatus,
    DayOfWeek,
    OrderType,
    Party,
    PartyPaginationResponse,
    ServicePeriod,
    ServiceUserDocumentResponse,
    ServiceUserFilter,
    ServiceUserIdentifier,
    ServiceUserRequest,
    ServiceUserResponse,
)
from .utils import is_valid_cpr, sanitize_cpr, sanitize_personal_id

__version__ = "0.1.0"

__all__ = [
    # Manager & Base Client
    "MatildaClientManager",
    "MatildaClient",
    # Functionality Clients
    "PartiesClient",
    "PartyClient",
    "ParterClient",
    "ServiceUsersClient",
    "ServiceUserClient",
    "ServiceBrugerClient",
    "ServiceUserDocumentsClient",
    "DocumentClient",
    "DokumentClient",
    # Models
    "Party",
    "PartyPaginationResponse",
    "ServicePeriod",
    "ServiceUserRequest",
    "ServiceUserResponse",
    "ServiceUserFilter",
    "ServiceUserIdentifier",
    "AttendanceRequest",
    "AttendingServiceUsersRequest",
    "ServiceUserDocumentResponse",
    "DayOfWeek",
    "CommonStatus",
    "OrderType",
    # Utilities
    "is_valid_cpr",
    "sanitize_cpr",
    "sanitize_personal_id",
    # Hooks
    "create_response_logging_hook",
]
