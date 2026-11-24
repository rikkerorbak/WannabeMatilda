"""
HTTPX Event Hooks for Matilda Platform Client.

This module provides hook factory functions that can be used with HTTPX's
event hook system to add structured logging with security sanitization.
"""

import json
import logging
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

# Sensitive headers that should be redacted from logs
SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "x-api-key",
    "proxy-authorization",
    "x-auth-token",
    "x-csrf-token",
    "api-secret",
    "session-token",
}

# Sensitive query parameters that should be redacted from logs
SENSITIVE_QUERY_PARAMS = {"token", "session_id", "access_key", "api_key", "secret", "password"}


def create_response_logging_hook(
    logger: logging.Logger,
    non_logging_endpoints: list[str] | None = None,
) -> Callable[[httpx.Response], None]:
    """
    Create response logging hook for Matilda API that captures HTTP transactions.

    Args:
        logger: Logger instance to use
        non_logging_endpoints: Optional list of endpoint suffixes to skip logging

    Returns:
        Response hook function for HTTPX
    """
    skip_endpoints = non_logging_endpoints or ["/document"]  # Avoid logging raw binary file uploads

    def log_response(response: httpx.Response) -> None:
        """Log complete HTTP transaction from response."""
        request = response.request

        # Skip logging for binary/large endpoints if matching
        url_str = str(request.url)
        if any(endpoint in url_str for endpoint in skip_endpoints if endpoint.endswith("document") and request.method == "POST"):
            logger.debug(f"{request.method} {url_str} -> {response.status_code} [Binary/Document upload skipped from detailed payload logging]")
            return

        method = request.method
        url = _sanitize_url(str(request.url))
        status = response.status_code

        # Extract request JSON if available
        request_json = None
        try:
            if hasattr(request, "content") and request.content:
                request_json = _parse_json_content(request.content)
        except Exception:
            request_json = None

        # Extract response JSON if available
        response_json = None
        try:
            if not hasattr(response, "_content"):
                response.read()
            response_json = _parse_json_content(response.text)
        except Exception:
            response_json = None

        # Extract and sanitize headers
        request_headers = _sanitize_headers(request.headers) if hasattr(request, "headers") else {}
        response_headers = _sanitize_headers(response.headers) if hasattr(response, "headers") else {}

        # Calculate duration in milliseconds
        duration_ms = (
            int(response.elapsed.total_seconds() * 1000)
            if hasattr(response, "elapsed") and response.elapsed
            else 0
        )

        extra = {
            "http": {
                "method": method,
                "url": url,
                "status_code": status,
                "duration_ms": duration_ms,
                "request": {
                    "headers": request_headers,
                    "body": request_json,
                },
                "response": {
                    "headers": response_headers,
                    "body": response_json,
                },
            }
        }

        # Choose appropriate log level
        if status >= 500:
            logger.error(f"HTTP {method} {url} returned {status} ({duration_ms}ms)", extra=extra)
        elif status >= 400:
            logger.warning(f"HTTP {method} {url} returned {status} ({duration_ms}ms)", extra=extra)
        else:
            logger.info(f"HTTP {method} {url} returned {status} ({duration_ms}ms)", extra=extra)

    return log_response


def _sanitize_url(url: str) -> str:
    """Sanitize sensitive parameters from URL query string."""
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return url

        query_params = parse_qs(parsed.query, keep_blank_values=True)
        sanitized_params = {}

        for key, values in query_params.items():
            if key.lower() in SENSITIVE_QUERY_PARAMS:
                sanitized_params[key] = ["REDACTED"]
            else:
                sanitized_params[key] = values

        new_query = urlencode(sanitized_params, doseq=True)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )
    except Exception:
        return url


def _sanitize_headers(headers: httpx.Headers | dict[str, str]) -> dict[str, str]:
    """Sanitize sensitive headers."""
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            sanitized[key] = "REDACTED"
        else:
            sanitized[key] = value
    return sanitized


def _parse_json_content(content: bytes | str) -> Any | None:
    """Parse JSON content safely."""
    try:
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        return json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return None
