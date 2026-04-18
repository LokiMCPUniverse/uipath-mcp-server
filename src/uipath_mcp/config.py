"""Configuration for the UiPath MCP server."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UiPathConfig(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Environment variables are prefixed with ``UIPATH_``. Example:
    ``UIPATH_CLIENT_ID``, ``UIPATH_CLIENT_SECRET``, ``UIPATH_ORGANIZATION_NAME``.
    """

    model_config = SettingsConfigDict(
        env_prefix="UIPATH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    orchestrator_url: str = Field(
        default="https://cloud.uipath.com",
        description="Base URL of the UiPath Orchestrator cloud instance.",
    )
    organization_name: str = Field(
        default="",
        description="UiPath organization (account logical name) in the URL path.",
    )
    tenant_name: str = Field(
        default="",
        description="UiPath tenant logical name.",
    )
    client_id: str = Field(
        default="",
        description="OAuth2 client id for the external application (client credentials flow).",
    )
    client_secret: str = Field(
        default="",
        description="OAuth2 client secret for the external application.",
    )
    access_token: str | None = Field(
        default=None,
        description="Optional pre-issued PAT or access token. Overrides client credentials when set.",
    )
    folder_id: int | None = Field(
        default=None,
        description="Optional Orchestrator folder id sent as X-UIPATH-OrganizationUnitId.",
    )
    timeout: float = Field(default=30.0, description="HTTP request timeout in seconds.")

    @property
    def tenant_base_url(self) -> str:
        """Return the Orchestrator base URL for the configured org/tenant."""

        base = self.orchestrator_url.rstrip("/")
        return f"{base}/{self.organization_name}/{self.tenant_name}/orchestrator_"

    @property
    def identity_token_url(self) -> str:
        """Return the cloud Identity Server token endpoint URL."""

        base = self.orchestrator_url.rstrip("/")
        return f"{base}/identity_/connect/token"
