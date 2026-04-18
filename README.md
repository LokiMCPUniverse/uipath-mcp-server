# UiPath MCP Server

<div align="center">

# Uipath Mcp Server

[![GitHub stars](https://img.shields.io/github/stars/LokiMCPUniverse/uipath-mcp-server?style=social)](https://github.com/LokiMCPUniverse/uipath-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LokiMCPUniverse/uipath-mcp-server?style=social)](https://github.com/LokiMCPUniverse/uipath-mcp-server/network)
[![GitHub watchers](https://img.shields.io/github/watchers/LokiMCPUniverse/uipath-mcp-server?style=social)](https://github.com/LokiMCPUniverse/uipath-mcp-server/watchers)

[![License](https://img.shields.io/github/license/LokiMCPUniverse/uipath-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/uipath-mcp-server/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/LokiMCPUniverse/uipath-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/uipath-mcp-server/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/LokiMCPUniverse/uipath-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/uipath-mcp-server/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/LokiMCPUniverse/uipath-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/uipath-mcp-server/commits)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-DC143C?style=for-the-badge)](https://modelcontextprotocol.io)

</div>

A Model Context Protocol (MCP) server that exposes the UiPath Orchestrator
Cloud API to MCP-compatible clients such as Claude Desktop. Built on the
official `mcp` Python SDK (FastMCP) with async `httpx` and OAuth2 client
credentials authentication.

## Features

- OAuth2 client credentials flow against UiPath Cloud Identity Server with
  automatic token caching and refresh.
- Personal access token (PAT) support via the `UIPATH_ACCESS_TOKEN` env var.
- Optional Orchestrator folder scoping through `X-UIPATH-OrganizationUnitId`.
- Typed tool surface covering processes, robots, machines, jobs, queues, and
  assets.
- Single-retry on 401 with forced token refresh.

## Installation

Install from source:

```bash
git clone https://github.com/LokiMCPUniverse/uipath-mcp-server.git
cd uipath-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

All configuration is read from environment variables (prefixed with `UIPATH_`)
or an optional `.env` file in the working directory.

| Variable | Required | Description |
| --- | --- | --- |
| `UIPATH_ORCHESTRATOR_URL` | no | Base URL, defaults to `https://cloud.uipath.com`. |
| `UIPATH_ORGANIZATION_NAME` | yes | Organization (account) logical name. |
| `UIPATH_TENANT_NAME` | yes | Tenant logical name. |
| `UIPATH_CLIENT_ID` | yes* | OAuth2 client id of the external application. |
| `UIPATH_CLIENT_SECRET` | yes* | OAuth2 client secret. |
| `UIPATH_ACCESS_TOKEN` | no | Pre-issued access token or PAT (overrides client credentials). |
| `UIPATH_FOLDER_ID` | no | Folder id sent via `X-UIPATH-OrganizationUnitId`. |
| `UIPATH_TIMEOUT` | no | HTTP timeout in seconds (default 30). |

`*` Not required if `UIPATH_ACCESS_TOKEN` is provided.

## Running

```bash
uipath-mcp
```

### Claude Desktop configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "uipath": {
      "command": "uipath-mcp",
      "env": {
        "UIPATH_ORGANIZATION_NAME": "your-org",
        "UIPATH_TENANT_NAME": "your-tenant",
        "UIPATH_CLIENT_ID": "...",
        "UIPATH_CLIENT_SECRET": "...",
        "UIPATH_FOLDER_ID": "123456"
      }
    }
  }
}
```

## Tools

| Tool | Description |
| --- | --- |
| `list_processes` | List Orchestrator processes (Releases). |
| `list_robots` | List robots registered in the tenant. |
| `list_machines` | List machines registered in the tenant. |
| `start_job` | Start a process, optionally with specific robots and input arguments. |
| `list_jobs` | List jobs, optionally filtered by state. |
| `get_job` | Get a single job by id. |
| `stop_job` | Stop or kill a running job (`SoftStop` or `Kill`). |
| `list_queue_items` | List queue items, optionally filtered by queue name and status. |
| `add_queue_item` | Add a new item to a queue with arbitrary specific content. |
| `list_assets` | List assets in the current folder. |

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -x --tb=short
ruff check src tests
```

## License

MIT License - see LICENSE file for details
