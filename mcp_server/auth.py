"""Bearer-token authentication for the synthetic OpsHub MCP server."""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def get_auth_token() -> str:
    """Return the expected bearer token from the environment."""

    return os.getenv("OPSHUB_AUTH_TOKEN", "demo-token-opsbridge-2026")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate bearer-token auth for all HTTP routes."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Reject requests without a valid bearer token."""

        auth_header = request.headers.get("Authorization", "")
        expected = f"Bearer {get_auth_token()}"
        if auth_header != expected:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "unauthorized"},
            )
        return await call_next(request)
