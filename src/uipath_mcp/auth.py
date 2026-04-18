"""OAuth2 authentication helpers for UiPath Cloud Identity Server."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from .config import UiPathConfig
from .exceptions import AuthenticationError

DEFAULT_SCOPE = (
    "OR.Execution OR.Jobs OR.Robots OR.Machines OR.Queues OR.Assets OR.Folders"
)

# Refresh the token this many seconds before the reported expiry.
_REFRESH_SKEW_SECONDS = 60.0


@dataclass
class TokenInfo:
    access_token: str
    expires_at: float  # unix timestamp

    def is_expired(self, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        return current >= (self.expires_at - _REFRESH_SKEW_SECONDS)


class TokenProvider:
    """Fetches and caches OAuth2 bearer tokens for UiPath Orchestrator."""

    def __init__(
        self,
        config: UiPathConfig,
        http_client: httpx.AsyncClient,
        scope: str = DEFAULT_SCOPE,
    ) -> None:
        self._config = config
        self._client = http_client
        self._scope = scope
        self._cached: TokenInfo | None = None

    async def get_token(self, force_refresh: bool = False) -> str:
        """Return a valid bearer token, refreshing when needed.

        If ``access_token`` is set on the config, it is used verbatim (e.g. a
        personal access token) and no network call is made.
        """

        if self._config.access_token:
            return self._config.access_token

        if not force_refresh and self._cached and not self._cached.is_expired():
            return self._cached.access_token

        if not self._config.client_id or not self._config.client_secret:
            raise AuthenticationError(
                "UiPath client_id and client_secret must be configured for OAuth2."
            )

        data = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
            "scope": self._scope,
        }
        try:
            response = await self._client.post(
                self._config.identity_token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as exc:
            raise AuthenticationError(f"Failed to contact UiPath Identity: {exc}") from exc

        if response.status_code >= 400:
            raise AuthenticationError(
                f"UiPath Identity returned {response.status_code}: {response.text}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise AuthenticationError("Non-JSON response from UiPath Identity.") from exc

        token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)
        if not token:
            raise AuthenticationError("UiPath Identity response missing access_token.")

        self._cached = TokenInfo(
            access_token=token,
            expires_at=time.time() + float(expires_in),
        )
        return token

    def invalidate(self) -> None:
        """Drop any cached token so the next call forces a refresh."""

        self._cached = None
