"""FastAPI application that exposes the synthetic OpsHub MCP server."""

from __future__ import annotations

import contextlib
import logging
from collections.abc import AsyncIterator, Callable

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from mcp.server.fastmcp import FastMCP

from mcp_server.auth import BearerAuthMiddleware
from mcp_server.seed import seed_demo_data
from mcp_server.tools_read import (
    READ_TOOL_DEFINITIONS,
    get_config_change_history,
    get_dependency_health,
    get_deploy_diff,
    get_error_samples,
    get_incident,
    get_incident_metrics,
    get_latency_timeline,
    get_recent_deploys,
    get_release_metadata,
    get_runbook,
    get_ticket_state,
    list_open_incidents,
)
from mcp_server.tools_write import (
    WRITE_TOOL_DEFINITIONS,
    close_incident,
    delete_deployment_history,
    post_incident_update,
    rollback_deployment,
    update_incident_ticket,
)


logger = logging.getLogger(__name__)

def _register_tool(mcp: FastMCP, func: Callable[..., object]) -> None:
    """Register a Python function as an MCP tool."""

    mcp.tool()(func)


def _build_mcp_server() -> FastMCP:
    """Create and populate the FastMCP server instance."""

    mcp = FastMCP(
        "Synthetic OpsHub",
        stateless_http=True,
        json_response=True,
        streamable_http_path="/",
    )
    for tool in (
        list_open_incidents,
        get_incident,
        get_incident_metrics,
        get_error_samples,
        get_dependency_health,
        get_latency_timeline,
        get_recent_deploys,
        get_deploy_diff,
        get_config_change_history,
        get_release_metadata,
        get_runbook,
        get_ticket_state,
        rollback_deployment,
        update_incident_ticket,
        post_incident_update,
        close_incident,
        delete_deployment_history,
    ):
        _register_tool(mcp, tool)
    return mcp


def create_app() -> FastAPI:
    """Create the authenticated FastAPI application for OpsHub MCP."""

    mcp = _build_mcp_server()

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Initialize seeded state and MCP session management on startup."""

        logging.basicConfig(level=logging.INFO)
        seed_demo_data()
        logger.info("seeded synthetic operations data")
        async with mcp.session_manager.run():
            yield

    app = FastAPI(title="Synthetic OpsHub MCP Server", lifespan=lifespan)
    app.add_middleware(BearerAuthMiddleware)
    app.mount("/mcp", mcp.streamable_http_app())

    @app.get("/health")
    def health() -> JSONResponse:
        """Return a simple health response."""

        return JSONResponse({"status": "ok"})

    @app.get("/tools")
    def list_tools() -> JSONResponse:
        """Return all registered tools with their mode."""

        return JSONResponse({"tools": READ_TOOL_DEFINITIONS + WRITE_TOOL_DEFINITIONS})

    return app


app = create_app()
