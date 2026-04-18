"""UiPath MCP Server - Model Context Protocol server for UiPath Orchestrator."""

from __future__ import annotations

from .server import main, mcp

__version__ = "0.1.0"
__all__ = ["main", "mcp", "__version__"]
