"""
Unit tests for MatildaClientManager.
"""


from matilda_client.functionality.documents import ServiceUserDocumentsClient
from matilda_client.functionality.parties import PartiesClient
from matilda_client.functionality.service_users import ServiceUsersClient
from matilda_client.manager import MatildaClientManager


def test_manager_initialization():
    manager = MatildaClientManager(
        organization="test-org",
        api_key="test-key",
        timeout=45.0,
    )
    assert manager._organization == "test-org"
    assert manager.organization == "test-org"
    assert manager._api_key == "test-key"
    assert manager._config["timeout"] == 45.0

    # Ensure lazy loading
    assert manager._client is None
    assert manager._parties_client is None
    assert manager._service_users_client is None
    assert manager._documents_client is None


def test_manager_env_fallback(monkeypatch):
    monkeypatch.setenv("ORGANIZATION", "env-org")
    monkeypatch.setenv("API_KEY", "env-key")
    manager = MatildaClientManager()
    assert manager.organization == "env-org"
    assert manager._api_key == "env-key"
    assert manager.client.base_url == "https://env-org.matildaplatform.com/"
    manager.close()


def test_manager_missing_organization(monkeypatch):
    import pytest

    monkeypatch.delenv("ORGANIZATION", raising=False)
    monkeypatch.delenv("MATILDA_ORGANIZATION", raising=False)
    with pytest.raises(ValueError, match="Organization must be specified"):
        MatildaClientManager(organization="")


def test_manager_lazy_loading(manager):
    # Access parties
    p1 = manager.parties
    assert isinstance(p1, PartiesClient)
    # Re-accessing returns same instance
    p2 = manager.parties
    assert p1 is p2
    # Alias
    assert manager.parter is p1
    assert manager.party is p1

    # Access service users
    u1 = manager.service_users
    assert isinstance(u1, ServiceUsersClient)
    u2 = manager.service_users
    assert u1 is u2
    # Aliases
    assert manager.serviceusers is u1
    assert manager.service_user is u1
    assert manager.service_brugere is u1

    # Access documents
    d1 = manager.documents
    assert isinstance(d1, ServiceUserDocumentsClient)
    assert manager.service_user_documents is d1
    assert manager.dokumenter is d1


def test_manager_context_manager():
    with MatildaClientManager(organization="test", api_key="k") as mgr:
        client = mgr.client
        assert not client.client.is_closed
    assert client.client.is_closed
