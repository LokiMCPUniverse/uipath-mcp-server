# UiPath MCP Server

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
