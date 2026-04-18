"""Shared pytest fixtures for the UiPath MCP server tests."""

from __future__ import annotations

import os
from collections.abc import Iterator

import httpx
import pytest

from uipath_mcp.client import UiPathClient
from uipath_mcp.config import UiPathConfig

_UIPATH_ENV_VARS = (
    "UIPATH_ORCHESTRATOR_URL",
    "UIPATH_ORGANIZATION_NAME",
    "UIPATH_TENANT_NAME",
    "UIPATH_CLIENT_ID",
    "UIPATH_CLIENT_SECRET",
    "UIPATH_ACCESS_TOKEN",
    "UIPATH_FOLDER_ID",
    "UIPATH_TIMEOUT",
)


@pytest.fixture(autouse=True)
def clean_uipath_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Ensure tests run with a predictable environment."""

    for name in _UIPATH_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    # Also guard against a .env file being picked up from the working dir.
    monkeypatch.chdir(os.path.dirname(__file__))
    yield


@pytest.fixture
def uipath_config() -> UiPathConfig:
    return UiPathConfig(
        orchestrator_url="https://cloud.uipath.com",
        organization_name="acme",
        tenant_name="prod",
        client_id="client-id",
        client_secret="client-secret",
        folder_id=42,
    )


@pytest.fixture
async def uipath_client(uipath_config: UiPathConfig) -> UiPathClient:
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    http = httpx.AsyncClient(transport=transport, timeout=uipath_config.timeout)
    client = UiPathClient(uipath_config, http_client=http)
    try:
        yield client
    finally:
        await http.aclose()
