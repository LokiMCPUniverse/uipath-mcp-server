"""Smoke tests for the FastMCP server wiring."""

from __future__ import annotations

import pytest

from uipath_mcp import __version__
from uipath_mcp.server import mcp


def test_server_name() -> None:
    assert mcp.name == "uipath-mcp-server"


@pytest.mark.asyncio
async def test_all_expected_tools_registered() -> None:
    tool_names = {tool.name for tool in await mcp.list_tools()}
    expected = {
        "list_processes",
        "list_robots",
        "list_machines",
        "start_job",
        "list_jobs",
        "get_job",
        "stop_job",
        "list_queue_items",
        "add_queue_item",
        "list_assets",
    }
    assert expected.issubset(tool_names)


def test_version_exposed() -> None:
    assert __version__ == "0.1.0"
