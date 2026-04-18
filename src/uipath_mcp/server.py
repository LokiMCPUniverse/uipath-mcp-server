"""FastMCP server exposing UiPath Orchestrator tools."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from .client import UiPathClient
from .config import UiPathConfig


@dataclass
class AppContext:
    client: UiPathClient
    config: UiPathConfig


@asynccontextmanager
async def lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    config = UiPathConfig()
    client = UiPathClient(config)
    try:
        yield AppContext(client=client, config=config)
    finally:
        await client.aclose()


mcp = FastMCP("uipath-mcp-server", lifespan=lifespan)


def _client(ctx: Context) -> UiPathClient:
    app: AppContext = ctx.request_context.lifespan_context
    return app.client


@mcp.tool()
async def list_processes(ctx: Context, top: int | None = None) -> Any:
    """List UiPath processes (Releases) available in the current folder.

    Args:
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_releases(top=top)


@mcp.tool()
async def list_robots(ctx: Context, top: int | None = None) -> Any:
    """List UiPath robots registered in the Orchestrator tenant.

    Args:
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_robots(top=top)


@mcp.tool()
async def list_machines(ctx: Context, top: int | None = None) -> Any:
    """List UiPath machines registered in the Orchestrator tenant.

    Args:
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_machines(top=top)


@mcp.tool()
async def start_job(
    ctx: Context,
    process_key: str,
    robot_ids: list[int] | None = None,
    input_arguments: dict[str, Any] | None = None,
) -> Any:
    """Start a job for a UiPath process.

    Args:
        process_key: The ReleaseKey of the process to start.
        robot_ids: Optional list of robot ids. If omitted, a modern dynamic allocation runs one job.
        input_arguments: Optional dict of input arguments passed to the process.
    """

    return await _client(ctx).start_jobs(
        release_key=process_key,
        robot_ids=robot_ids,
        input_arguments=input_arguments,
    )


@mcp.tool()
async def list_jobs(
    ctx: Context,
    state: str | None = None,
    top: int | None = None,
) -> Any:
    """List jobs, optionally filtered by state.

    Args:
        state: Optional UiPath job state (e.g. Pending, Running, Successful, Faulted, Stopped).
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_jobs(state=state, top=top)


@mcp.tool()
async def get_job(ctx: Context, job_id: int) -> Any:
    """Get a single job by its numeric id.

    Args:
        job_id: The Orchestrator job id.
    """

    return await _client(ctx).get_job(job_id)


@mcp.tool()
async def stop_job(ctx: Context, job_id: int, strategy: str = "SoftStop") -> Any:
    """Stop or kill a running UiPath job.

    Args:
        job_id: The Orchestrator job id.
        strategy: One of ``SoftStop`` (graceful) or ``Kill`` (immediate).
    """

    return await _client(ctx).stop_job(job_id, strategy=strategy)


@mcp.tool()
async def list_queue_items(
    ctx: Context,
    queue_name: str | None = None,
    status: str | None = None,
    top: int | None = None,
) -> Any:
    """List queue items, optionally filtered by queue name and status.

    Args:
        queue_name: Optional queue name to filter by.
        status: Optional status filter (e.g. New, InProgress, Successful, Failed).
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_queue_items(
        queue_name=queue_name, status=status, top=top
    )


@mcp.tool()
async def add_queue_item(
    ctx: Context,
    queue_name: str,
    specific_content: dict[str, Any],
) -> Any:
    """Add a new queue item to the given UiPath queue.

    Args:
        queue_name: Target queue name.
        specific_content: Dict of key/value pairs stored on the queue item.
    """

    return await _client(ctx).add_queue_item(queue_name, specific_content)


@mcp.tool()
async def list_assets(ctx: Context, top: int | None = None) -> Any:
    """List assets configured in the current Orchestrator folder.

    Args:
        top: Optional maximum number of items to return.
    """

    return await _client(ctx).list_assets(top=top)


def main() -> None:
    """Entry point used by the ``uipath-mcp`` console script."""

    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
