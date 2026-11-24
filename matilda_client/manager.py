"""
MatildaClientManager - Facade for all Matilda Platform functionality clients.

Provides a unified entry point with lazy-loaded client properties,
consistent configuration, and optional context management.
"""


import os

from matilda_client.client import MatildaClient
from matilda_client.functionality.documents import ServiceUserDocumentsClient
from matilda_client.functionality.parties import PartiesClient
from matilda_client.functionality.service_users import ServiceUsersClient


class MatildaClientManager:
    """
    Manager providing unified access to all Matilda functionality clients.

    RECOMMENDED USAGE:
        from matilda_client import MatildaClientManager

        # Zero-config (reads ORGANIZATION and API_KEY from environment):
        matilda = MatildaClientManager()

        # Or explicit config:
        matilda = MatildaClientManager(
            organization="my-org",
            api_key="...",
        )

        # Access parties:
        parties = matilda.parties.get_parties()

        # Access service users:
        service_user = matilda.service_users.get_by_cpr("0102031234")

        # Access service user documents:
        docs = matilda.documents.get_documents(service_user_id="...")
    """

    def __init__(
        self,
        organization: str | None = None,
        api_key: str | None = None,
        bearer_token: str | None = None,
        basic_auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        enable_logging: bool = True,
    ):
        """
        Initialize MatildaClientManager.

        :param organization: Matilda organization (optional if ORGANIZATION env var is set).
        :param api_key: Matilda API Key (optional if API_KEY env var is set).
        :param bearer_token: Optional Bearer token (optional if BEARER_TOKEN env var is set).
        :param basic_auth: Optional tuple (username, password) for Basic auth.
        :param timeout: Request timeout in seconds (default: 30.0).
        :param verify_ssl: Verify SSL certificates (default: True).
        :param enable_logging: Enable transaction logging (default: True).
        """
        org = organization or os.getenv("ORGANIZATION") or os.getenv("MATILDA_ORGANIZATION")
        if not org or not org.strip():
            raise ValueError(
                "Organization must be specified via argument or ORGANIZATION environment variable."
            )

        self._organization = org.strip()
        self._api_key = api_key or os.getenv("API_KEY") or os.getenv("MATILDA_API_KEY")
        self._bearer_token = bearer_token or os.getenv("BEARER_TOKEN") or os.getenv("MATILDA_BEARER_TOKEN")
        self._basic_auth = basic_auth

        self._config = {
            "timeout": timeout,
            "verify_ssl": verify_ssl,
            "enable_logging": enable_logging,
        }

        # Lazy-loaded clients
        self._client: MatildaClient | None = None
        self._parties_client: PartiesClient | None = None
        self._service_users_client: ServiceUsersClient | None = None
        self._documents_client: ServiceUserDocumentsClient | None = None

    @property
    def organization(self) -> str:
        """Get the organization identifier."""
        return self._organization

    @property
    def client(self) -> MatildaClient:
        """Get the base MatildaClient (lazy-loaded)."""
        if self._client is None:
            self._client = MatildaClient(
                organization=self._organization,
                api_key=self._api_key,
                bearer_token=self._bearer_token,
                basic_auth=self._basic_auth,
                **self._config,
            )
        return self._client

    @property
    def matilda_client(self) -> MatildaClient:
        """Alias for client."""
        return self.client

    @property
    def parties(self) -> PartiesClient:
        """Get the PartiesClient (lazy-loaded)."""
        if self._parties_client is None:
            self._parties_client = PartiesClient(self.client)
        return self._parties_client

    # Aliases for parties
    party = parties
    parter = parties

    @property
    def service_users(self) -> ServiceUsersClient:
        """Get the ServiceUsersClient (lazy-loaded)."""
        if self._service_users_client is None:
            self._service_users_client = ServiceUsersClient(self.client)
        return self._service_users_client

    # Aliases for service users
    service_user = service_users
    serviceusers = service_users
    service_brugere = service_users

    @property
    def documents(self) -> ServiceUserDocumentsClient:
        """Get the ServiceUserDocumentsClient (lazy-loaded)."""
        if self._documents_client is None:
            self._documents_client = ServiceUserDocumentsClient(self.client)
        return self._documents_client

    # Aliases for documents
    service_user_documents = documents
    dokumenter = documents

    def close(self) -> None:
        """Close underlying HTTP client if initialized."""
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> "MatildaClientManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
