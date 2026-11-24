"""
Unit tests for MatildaClient base HTTP client.
"""

import pytest

from matilda_client.client import MatildaClient


def test_client_initialization():
    client = MatildaClient(
        organization="demo-org",
        api_key="secret-key",
        timeout=15.0,
    )
    assert client.organization == "demo-org"
    assert client.base_url == "https://demo-org.matildaplatform.com/"
    assert client.client.headers["x-api-key"] == "secret-key"
    assert "Bearer" not in client.client.headers.get("authorization", "")
    client.close()


def test_client_class_variable_base_url(monkeypatch):
    monkeypatch.setattr(MatildaClient, "BASE_URL", "https://{organization}.custom.com")
    client = MatildaClient(organization="my-org")
    assert client.base_url == "https://my-org.custom.com/"
    client.close()


def test_client_bearer_auth():
    client = MatildaClient(
        organization="demo-org",
        bearer_token="jwt-token-xyz",
    )
    assert client.client.headers["authorization"] == "Bearer jwt-token-xyz"
    client.close()


def test_client_missing_organization(monkeypatch):
    monkeypatch.delenv("ORGANIZATION", raising=False)
    monkeypatch.delenv("MATILDA_ORGANIZATION", raising=False)
    with pytest.raises(ValueError, match="Organization must be specified"):
        MatildaClient(organization="")


def test_client_env_fallback(monkeypatch):
    monkeypatch.setenv("ORGANIZATION", "env-org")
    monkeypatch.setenv("API_KEY", "env-key")
    client = MatildaClient()
    assert client.organization == "env-org"
    assert client.base_url == "https://env-org.matildaplatform.com/"
    assert client.client.headers["x-api-key"] == "env-key"
    client.close()


def test_url_normalization():
    client = MatildaClient(
        organization="my-test-org",
        api_key="k",
    )
    # Test path with placeholder
    url = client._normalize_url("/v1/organization/{organization}/parties")
    assert url == "https://my-test-org.matildaplatform.com/v1/organization/my-test-org/parties"

    # Test path without leading slash
    url2 = client._normalize_url("v1/organization/{organization}/service-user")
    assert url2 == "https://my-test-org.matildaplatform.com/v1/organization/my-test-org/service-user"

    # Test full URL untouched
    url3 = client._normalize_url("https://other.com/api/test")
    assert url3 == "https://other.com/api/test"
    client.close()


def test_client_context_manager():
    with MatildaClient(organization="org", api_key="k") as client:
        assert client.organization == "org"
    assert client.client.is_closed
