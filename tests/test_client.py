"""Tests for the UiPathClient."""

from __future__ import annotations

import json

import httpx
import pytest

from uipath_mcp.client import UiPathClient
from uipath_mcp.config import UiPathConfig
from uipath_mcp.exceptions import APIError, AuthenticationError, NotFoundError


def _make_client(
    handler,
    *,
    access_token: str = "pat-token",
    folder_id: int | None = 42,
) -> tuple[UiPathClient, httpx.AsyncClient]:
    cfg = UiPathConfig(
        orchestrator_url="https://cloud.uipath.com",
        organization_name="acme",
        tenant_name="prod",
        access_token=access_token,
        folder_id=folder_id,
    )
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=cfg.timeout)
    return UiPathClient(cfg, http_client=http), http


async def test_list_releases_sets_headers_and_returns_json() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": [{"Id": 1, "Name": "Process"}]})

    client, http = _make_client(handler)
    try:
        result = await client.list_releases(top=5)
    finally:
        await http.aclose()

    assert result == {"value": [{"Id": 1, "Name": "Process"}]}
    assert len(seen) == 1
    req = seen[0]
    assert req.method == "GET"
    assert req.url.path == "/acme/prod/orchestrator_/odata/Releases"
    assert req.url.params["$top"] == "5"
    assert req.headers["Authorization"] == "Bearer pat-token"
    assert req.headers["X-UIPATH-OrganizationUnitId"] == "42"


async def test_list_jobs_builds_odata_filter() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": []})

    client, http = _make_client(handler)
    try:
        await client.list_jobs(state="Running", top=3)
    finally:
        await http.aclose()

    req = seen[0]
    assert req.url.params["$filter"] == "State eq 'Running'"
    assert req.url.params["$top"] == "3"


async def test_start_jobs_serialises_input_arguments() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": [{"Id": 99}]})

    client, http = _make_client(handler)
    try:
        await client.start_jobs(
            "release-key",
            robot_ids=[1, 2],
            input_arguments={"foo": "bar"},
        )
    finally:
        await http.aclose()

    req = seen[0]
    body = json.loads(req.content.decode())
    start_info = body["startInfo"]
    assert start_info["ReleaseKey"] == "release-key"
    assert start_info["RobotIds"] == [1, 2]
    assert start_info["Strategy"] == "Specific"
    assert json.loads(start_info["InputArguments"]) == {"foo": "bar"}


async def test_start_jobs_defaults_to_modern_strategy() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": []})

    client, http = _make_client(handler)
    try:
        await client.start_jobs("release-key")
    finally:
        await http.aclose()

    body = json.loads(seen[0].content.decode())
    assert body["startInfo"]["Strategy"] == "ModernJobsCount"
    assert body["startInfo"]["JobsCount"] == 1
    assert "InputArguments" not in body["startInfo"]


async def test_stop_job_posts_strategy() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(204)

    client, http = _make_client(handler)
    try:
        result = await client.stop_job(123, strategy="Kill")
    finally:
        await http.aclose()

    assert result is None
    req = seen[0]
    assert req.method == "POST"
    assert req.url.path.endswith("/odata/Jobs(123)/UiPath.Server.Configuration.OData.StopJob")
    assert json.loads(req.content.decode()) == {"strategy": "Kill"}


async def test_add_queue_item_shape() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(201, json={"Id": 7})

    client, http = _make_client(handler)
    try:
        await client.add_queue_item("MyQueue", {"key": "value"})
    finally:
        await http.aclose()

    body = json.loads(seen[0].content.decode())
    assert body["itemData"]["Name"] == "MyQueue"
    assert body["itemData"]["SpecificContent"] == {"key": "value"}


async def test_list_queue_items_filter_composition() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": []})

    client, http = _make_client(handler)
    try:
        await client.list_queue_items(queue_name="Invoices", status="New")
    finally:
        await http.aclose()

    assert (
        seen[0].url.params["$filter"]
        == "QueueDefinition/Name eq 'Invoices' and Status eq 'New'"
    )


async def test_401_triggers_token_refresh_and_retry() -> None:
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        # Only the orchestrator endpoint is called because access_token skips identity.
        call_count["n"] += 1
        if call_count["n"] == 1:
            return httpx.Response(401, json={"error": "unauthorized"})
        return httpx.Response(200, json={"value": []})

    client, http = _make_client(handler)
    try:
        result = await client.list_robots()
    finally:
        await http.aclose()

    assert result == {"value": []}
    assert call_count["n"] == 2


async def test_not_found_raises_typed_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "gone"})

    client, http = _make_client(handler)
    try:
        with pytest.raises(NotFoundError):
            await client.get_job(999)
    finally:
        await http.aclose()


async def test_generic_api_error_raised() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client, http = _make_client(handler)
    try:
        with pytest.raises(APIError) as excinfo:
            await client.list_robots()
    finally:
        await http.aclose()

    assert excinfo.value.status_code == 500


async def test_401_persists_when_refresh_does_not_help() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    client, http = _make_client(handler)
    try:
        with pytest.raises(AuthenticationError):
            await client.list_robots()
    finally:
        await http.aclose()


async def test_no_folder_header_when_folder_unset() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"value": []})

    client, http = _make_client(handler, folder_id=None)
    try:
        await client.list_assets()
    finally:
        await http.aclose()

    assert "X-UIPATH-OrganizationUnitId" not in seen[0].headers
