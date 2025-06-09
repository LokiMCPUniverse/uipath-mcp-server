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

[![Commit Activity](https://img.shields.io/github/commit-activity/m/LokiMCPUniverse/uipath-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/uipath-mcp-server/pulse)
[![Code Size](https://img.shields.io/github/languages/code-size/LokiMCPUniverse/uipath-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/uipath-mcp-server)
[![Contributors](https://img.shields.io/github/contributors/LokiMCPUniverse/uipath-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/uipath-mcp-server/graphs/contributors)

</div>

A Model Context Protocol (MCP) server for integrating UiPath with GenAI applications.

## Overview

Robotic Process Automation (RPA) platform

## Features

- Comprehensive UiPath API coverage
- Multiple authentication methods
- Enterprise-ready with rate limiting
- Full error handling and retry logic
- Async support for better performance

## Installation

```bash
pip install uipath-mcp-server
```

Or install from source:

```bash
git clone https://github.com/asklokesh/uipath-mcp-server.git
cd uipath-mcp-server
pip install -e .
```

## Configuration

Create a `.env` file or set environment variables according to UiPath API requirements.

## Quick Start

```python
from uipath_mcp import UipathMCPServer

# Initialize the server
server = UipathMCPServer()

# Start the server
server.start()
```

## License

MIT License - see LICENSE file for details
