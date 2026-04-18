"""Async HTTP client for the UiPath Orchestrator OData API."""

from __future__ import annotations

from typing import Any

import httpx

from .auth import TokenProvider
from .config import UiPathConfig
from .exceptions import APIError, AuthenticationError, NotFoundError


class UiPathClient:
    """Thin typed wrapper around the Orchestrator OData endpoints used by the MCP server."""

    def __init__(self, config: UiPathConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self._config = config
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=config.timeout)
        self._tokens = TokenProvider(config, self._http)

    # ------------------------------------------------------------------ lifecycle
    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> UiPathClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # ------------------------------------------------------------------ request core
    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        base = self._config.tenant_base_url.rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    async def _headers(self) -> dict[str, str]:
        token = await self._tokens.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if self._config.folder_id is not None:
            headers["X-UIPATH-OrganizationUnitId"] = str(self._config.folder_id)
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        url = self._build_url(path)
        headers = await self._headers()

        response = await self._http.request(
            method, url, headers=headers, params=params, json=json
        )

        if response.status_code == 401:
            # Force a token refresh and retry once.
            self._tokens.invalidate()
            headers = await self._headers()
            response = await self._http.request(
                method, url, headers=headers, params=params, json=json
            )

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Any:
        status = response.status_code

        if 200 <= status < 300:
            if status == 204 or not response.content:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text

        # error paths
        try:
            payload: Any = response.json()
        except ValueError:
            payload = response.text

        message = f"UiPath API error {status} for {response.request.method} {response.request.url}"
        if status == 401:
            raise AuthenticationError(message)
        if status == 404:
            raise NotFoundError(message, payload=payload)
        raise APIError(message, status_code=status, payload=payload)

    # ------------------------------------------------------------------ convenience wrappers
    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json: Any | None = None, params: dict[str, Any] | None = None) -> Any:
        return await self.request("POST", path, params=params, json=json)

    # ------------------------------------------------------------------ domain helpers
    async def list_releases(self, top: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/Releases", params=params or None)

    async def list_robots(self, top: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/Robots", params=params or None)

    async def list_machines(self, top: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/Machines", params=params or None)

    async def start_jobs(
        self,
        release_key: str,
        robot_ids: list[int] | None = None,
        input_arguments: dict[str, Any] | None = None,
    ) -> Any:
        start_info: dict[str, Any] = {"ReleaseKey": release_key}
        if robot_ids:
            start_info["RobotIds"] = robot_ids
            start_info["Strategy"] = "Specific"
        else:
            start_info["Strategy"] = "ModernJobsCount"
            start_info["JobsCount"] = 1
        if input_arguments is not None:
            # Orchestrator expects a JSON string for InputArguments.
            import json as _json

            start_info["InputArguments"] = _json.dumps(input_arguments)
        body = {"startInfo": start_info}
        return await self.post(
            "/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs",
            json=body,
        )

    async def list_jobs(self, state: str | None = None, top: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if state:
            params["$filter"] = f"State eq '{state}'"
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/Jobs", params=params or None)

    async def get_job(self, job_id: int) -> Any:
        return await self.get(f"/odata/Jobs({job_id})")

    async def stop_job(self, job_id: int, strategy: str = "SoftStop") -> Any:
        body = {"strategy": strategy}
        return await self.post(
            f"/odata/Jobs({job_id})/UiPath.Server.Configuration.OData.StopJob",
            json=body,
        )

    async def list_queue_items(
        self,
        queue_name: str | None = None,
        status: str | None = None,
        top: int | None = None,
    ) -> Any:
        params: dict[str, Any] = {}
        filters: list[str] = []
        if queue_name:
            filters.append(f"QueueDefinition/Name eq '{queue_name}'")
        if status:
            filters.append(f"Status eq '{status}'")
        if filters:
            params["$filter"] = " and ".join(filters)
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/QueueItems", params=params or None)

    async def add_queue_item(self, queue_name: str, specific_content: dict[str, Any]) -> Any:
        body = {
            "itemData": {
                "Name": queue_name,
                "Priority": "Normal",
                "SpecificContent": specific_content,
            }
        }
        return await self.post(
            "/odata/Queues/UiPathODataSvc.AddQueueItem",
            json=body,
        )

    async def list_assets(self, top: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        return await self.get("/odata/Assets", params=params or None)
