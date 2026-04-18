"""Exceptions raised by the UiPath MCP server."""

from __future__ import annotations


class UiPathError(Exception):
    """Base exception for all UiPath MCP errors."""


class AuthenticationError(UiPathError):
    """Raised when authentication with UiPath Identity Server fails."""


class APIError(UiPathError):
    """Raised when the Orchestrator API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None, payload: object | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class NotFoundError(APIError):
    """Raised when a requested resource is not found (HTTP 404)."""

    def __init__(self, message: str, payload: object | None = None) -> None:
        super().__init__(message, status_code=404, payload=payload)
