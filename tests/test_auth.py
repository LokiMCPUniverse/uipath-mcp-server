"""Tests for the OAuth2 TokenProvider."""

from __future__ import annotations

import httpx
import pytest

from uipath_mcp.auth import TokenProvider
from uipath_mcp.config import UiPathConfig
from uipath_mcp.exceptions import AuthenticationError


def _token_transport(
    payload: dict[str, object],
    *,
    status_code: int = 200,
    call_log: list[httpx.Request] | None = None,
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if call_log is not None:
            call_log.append(request)
        return httpx.Response(status_code, json=payload)

    return httpx.MockTransport(handler)


async def test_uses_static_access_token_without_http_call() -> None:
    cfg = UiPathConfig(access_token="pat-token")
    transport = httpx.MockTransport(
        lambda request: pytest.fail(f"unexpected call: {request.url}")
    )
    async with httpx.AsyncClient(transport=transport) as http:
        provider = TokenProvider(cfg, http)
        assert await provider.get_token() == "pat-token"


async def test_fetches_and_caches_token() -> None:
    cfg = UiPathConfig(client_id="cid", client_secret="secret")
    call_log: list[httpx.Request] = []
    transport = _token_transport(
        {"access_token": "abc", "expires_in": 3600},
        call_log=call_log,
    )
    async with httpx.AsyncClient(transport=transport) as http:
        provider = TokenProvider(cfg, http)
        token1 = await provider.get_token()
        token2 = await provider.get_token()

    assert token1 == "abc"
    assert token2 == "abc"
    # Second call should reuse the cached value and not hit the network again.
    assert len(call_log) == 1
    sent = call_log[0]
    assert sent.method == "POST"
    assert sent.url == httpx.URL("https://cloud.uipath.com/identity_/connect/token")
    body = sent.content.decode()
    assert "grant_type=client_credentials" in body
    assert "client_id=cid" in body
    assert "client_secret=secret" in body
    assert "OR.Jobs" in body


async def test_force_refresh_re_fetches_token() -> None:
    cfg = UiPathConfig(client_id="cid", client_secret="secret")
    call_log: list[httpx.Request] = []
    transport = _token_transport(
        {"access_token": "abc", "expires_in": 3600},
        call_log=call_log,
    )
    async with httpx.AsyncClient(transport=transport) as http:
        provider = TokenProvider(cfg, http)
        await provider.get_token()
        await provider.get_token(force_refresh=True)

    assert len(call_log) == 2


async def test_missing_credentials_raises() -> None:
    cfg = UiPathConfig()
    async with httpx.AsyncClient() as http:
        provider = TokenProvider(cfg, http)
        with pytest.raises(AuthenticationError):
            await provider.get_token()


async def test_identity_server_error_raises() -> None:
    cfg = UiPathConfig(client_id="cid", client_secret="secret")
    transport = _token_transport({"error": "invalid_client"}, status_code=400)
    async with httpx.AsyncClient(transport=transport) as http:
        provider = TokenProvider(cfg, http)
        with pytest.raises(AuthenticationError):
            await provider.get_token()
