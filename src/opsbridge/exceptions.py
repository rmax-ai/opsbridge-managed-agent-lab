"""Custom domain exceptions."""


class OpsBridgeError(Exception):
    """Base exception for all OpsBridge errors."""


class NotAuthorizedError(OpsBridgeError):
    """Agent or user not authorized for this action."""


class SessionNotFoundError(OpsBridgeError):
    """No Managed Agent session found for the given ID."""


class ToolExecutionError(OpsBridgeError):
    """Error during custom tool execution."""


class PolicyViolationError(OpsBridgeError):
    """Action violates defined policy."""


class MCPConnectionError(OpsBridgeError):
    """Failed to connect to MCP server."""
