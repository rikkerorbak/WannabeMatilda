"""
Base client for Matilda Platform Gateway API communication.

Handles authentication (API Key, Bearer token, Basic auth), URL normalization,
error handling with ProblemDetails support, and structured transaction logging.
"""

import logging
import os
from typing import Any
from urllib.parse import urljoin

import httpx

from matilda_client.hooks import create_response_logging_hook


class MatildaClient:
    """
    Base HTTP client for interacting with the Matilda Platform Gateway API.

    IMPORTANT: For optimal developer experience, use MatildaClientManager
    instead of instantiating this class directly.
    """

    BASE_URL = "https://{organization}.matildaplatform.com"

    def __init__(
        self,
        organization: str | None = None,
        api_key: str | None = None,
        bearer_token: str | None = None,
        basic_auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        enable_logging: bool = True,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the MatildaClient.

        :param organization: Matilda organization / tenant (optional if ORGANIZATION env var is set).
        :param api_key: Matilda API Key (optional if API_KEY env var is set).
        :param bearer_token: Optional Bearer token (optional if BEARER_TOKEN env var is set).
        :param basic_auth: Optional tuple of (username, password) for HTTP Basic Auth.
        :param timeout: Request timeout in seconds (default: 30.0).
        :param verify_ssl: Whether to verify SSL certificates (default: True).
        :param enable_logging: Enable structured request/response logging (default: True).
        :param logger: Optional custom logger instance.
        """
        org = organization or os.getenv("ORGANIZATION") or os.getenv("MATILDA_ORGANIZATION")
        if not org or not org.strip():
            raise ValueError(
                "Organization must be specified via argument or ORGANIZATION environment variable."
            )

        self.organization = org.strip()
        self.base_url = self.BASE_URL.replace("{organization}", self.organization).rstrip("/") + "/"
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Configure logger
        self.logger = logger or logging.getLogger("matilda.client")
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        # Setup authentication headers
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "Matilda-Client-Python/0.1.0",
        }

        auth: httpx.Auth | None = None

        resolved_api_key = api_key or os.getenv("API_KEY") or os.getenv("MATILDA_API_KEY")
        resolved_bearer_token = bearer_token or os.getenv("BEARER_TOKEN") or os.getenv("MATILDA_BEARER_TOKEN")

        if resolved_api_key:
            headers["x-api-key"] = resolved_api_key.strip()
        elif resolved_bearer_token:
            headers["Authorization"] = f"Bearer {resolved_bearer_token.strip()}"
        elif basic_auth:
            username, password = basic_auth
            auth = httpx.BasicAuth(username, password)

        # Setup event hooks
        hooks: dict[str, list[Any]] = {}
        if enable_logging:
            response_hook = create_response_logging_hook(logger=self.logger)
            hooks["response"] = [response_hook]

        self.client = httpx.Client(
            headers=headers,
            auth=auth,
            timeout=timeout,
            verify=verify_ssl,
            event_hooks=hooks,
        )

    def _normalize_url(self, endpoint: str) -> str:
        """
        Normalize URL and interpolate organization placeholder.

        Handles:
        - Absolute URLs (http:// or https://)
        - Relative endpoints with '{organization}' placeholder
        - Relative endpoints starting with or without leading '/'
        """
        endpoint = endpoint.replace("{organization}", self.organization)

        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        endpoint = endpoint.lstrip("/")
        return urljoin(self.base_url, endpoint)

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """
        Inspect response and raise informative HTTPStatusError when status >= 400.
        """
        if response.is_error:
            error_message = f"HTTP {response.status_code} {response.reason_phrase} for {response.request.method} {response.request.url}"
            try:
                data = response.json()
                if isinstance(data, dict):
                    # ASP.NET Core ProblemDetails handling
                    title = data.get("title") or data.get("error")
                    detail = data.get("detail") or data.get("message")
                    errors = data.get("errors")
                    details = []
                    if title:
                        details.append(f"Title: {title}")
                    if detail:
                        details.append(f"Detail: {detail}")
                    if errors:
                        details.append(f"Validation errors: {errors}")
                    if details:
                        error_message += " - " + " | ".join(details)
            except Exception:
                pass

            response.raise_for_status()

        return response

    def get(self, endpoint: str, params: dict[str, Any] | None = None, **kwargs) -> httpx.Response:
        """
        Perform a GET request.

        :param endpoint: Target endpoint (e.g. '/v1/organization/{organization}/parties')
        :param params: Optional query parameters dictionary
        :return: httpx.Response
        """
        url = self._normalize_url(endpoint)
        response = self.client.get(url, params=params, **kwargs)
        return self._handle_response(response)

    def post(
        self,
        endpoint: str,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a POST request.

        :param endpoint: Target endpoint
        :param json: JSON body payload
        :param data: Form data payload
        :param files: File payload for multipart/form-data upload
        :param params: Optional query parameters
        :return: httpx.Response
        """
        url = self._normalize_url(endpoint)
        response = self.client.post(url, json=json, data=data, files=files, params=params, **kwargs)
        return self._handle_response(response)

    def put(
        self,
        endpoint: str,
        json: Any | None = None,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a PUT request.

        :param endpoint: Target endpoint
        :param json: JSON body payload
        :param data: Form data payload
        :param params: Optional query parameters
        :return: httpx.Response
        """
        url = self._normalize_url(endpoint)
        response = self.client.put(url, json=json, data=data, params=params, **kwargs)
        return self._handle_response(response)

    def delete(self, endpoint: str, params: dict[str, Any] | None = None, **kwargs) -> httpx.Response:
        """
        Perform a DELETE request.

        :param endpoint: Target endpoint
        :param params: Optional query parameters
        :return: httpx.Response
        """
        url = self._normalize_url(endpoint)
        response = self.client.delete(url, params=params, **kwargs)
        return self._handle_response(response)

    def close(self) -> None:
        """Close the underlying HTTP client session."""
        self.client.close()

    def __enter__(self) -> "MatildaClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
