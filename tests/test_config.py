"""Tests for UiPathConfig."""

from __future__ import annotations

import pytest

from uipath_mcp.config import UiPathConfig


def test_defaults() -> None:
    cfg = UiPathConfig()
    assert cfg.orchestrator_url == "https://cloud.uipath.com"
    assert cfg.timeout == 30.0
    assert cfg.folder_id is None


def test_env_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UIPATH_ORGANIZATION_NAME", "acme")
    monkeypatch.setenv("UIPATH_TENANT_NAME", "prod")
    monkeypatch.setenv("UIPATH_CLIENT_ID", "cid")
    monkeypatch.setenv("UIPATH_CLIENT_SECRET", "secret")
    monkeypatch.setenv("UIPATH_FOLDER_ID", "7")
    monkeypatch.setenv("UIPATH_TIMEOUT", "15")

    cfg = UiPathConfig()
    assert cfg.organization_name == "acme"
    assert cfg.tenant_name == "prod"
    assert cfg.client_id == "cid"
    assert cfg.client_secret == "secret"
    assert cfg.folder_id == 7
    assert cfg.timeout == 15.0


def test_tenant_base_url() -> None:
    cfg = UiPathConfig(
        orchestrator_url="https://cloud.uipath.com/",
        organization_name="acme",
        tenant_name="prod",
    )
    assert cfg.tenant_base_url == "https://cloud.uipath.com/acme/prod/orchestrator_"


def test_identity_token_url() -> None:
    cfg = UiPathConfig(orchestrator_url="https://cloud.uipath.com")
    assert cfg.identity_token_url == "https://cloud.uipath.com/identity_/connect/token"
