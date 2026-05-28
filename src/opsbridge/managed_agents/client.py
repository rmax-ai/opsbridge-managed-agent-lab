"""Anthropic Managed Agents client wrapper."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from ..config import settings
from ..exceptions import OpsBridgeError

if TYPE_CHECKING:
    from anthropic import Anthropic


LOGGER = logging.getLogger(__name__)


class ManagedAgentClientError(OpsBridgeError):
    """Raised when Anthropic Managed Agents operations fail."""


class ManagedAgentClient:
    """Thin wrapper around the Anthropic Managed Agents beta client."""

    client: Any

    def __init__(self, api_key: str | None = None, client: object | None = None):
        """Initialize the Anthropic SDK client with configured beta headers."""
        self._api_key = api_key or settings.anthropic_api_key
        if client is not None:
            self.client = client
        else:
            try:
                from anthropic import Anthropic
            except ImportError as exc:
                raise ManagedAgentClientError(
                    "anthropic SDK is required to use ManagedAgentClient"
                ) from exc

            self.client = Anthropic(
                api_key=self._api_key,
                base_url=settings.managed_agents_api_url,
                default_headers={
                    "anthropic-beta": (f"{settings.managed_agents_beta},{settings.dreaming_beta}")
                },
            )

        try:
            self.beta = self.client.beta.managed_agents
        except AttributeError as exc:
            raise ManagedAgentClientError(
                "Anthropic client does not expose beta.managed_agents"
            ) from exc

        LOGGER.debug(
            "Initialized ManagedAgentClient",
            extra={
                "base_url": settings.managed_agents_api_url,
                "managed_agents_beta": settings.managed_agents_beta,
                "dreaming_beta": settings.dreaming_beta,
            },
        )

    def resource(self, name: str) -> object:
        """Return a named managed-agents resource namespace."""
        try:
            return getattr(self.beta, name)
        except AttributeError as exc:
            raise ManagedAgentClientError(
                f"Managed Agents resource {name!r} is not available"
            ) from exc

    def call(self, resource_name: str, method_name: str, **kwargs: object) -> Any:
        """Call a method on a managed-agents resource with logging."""
        resource = self.resource(resource_name)
        try:
            method = getattr(resource, method_name)
        except AttributeError as exc:
            raise ManagedAgentClientError(
                f"Managed Agents resource {resource_name!r} has no method {method_name!r}"
            ) from exc

        LOGGER.info(
            "Calling managed-agents API",
            extra={
                "resource": resource_name,
                "method": method_name,
                "kwargs_keys": sorted(kwargs.keys()),
            },
        )
        try:
            return method(**kwargs)
        except Exception as exc:  # pragma: no cover - SDK-specific surface
            LOGGER.exception(
                "Managed-agents API call failed",
                extra={"resource": resource_name, "method": method_name},
            )
            raise ManagedAgentClientError(
                f"Managed Agents API call failed: {resource_name}.{method_name}"
            ) from exc

    def extract_list(self, result: object) -> list[Any]:
        """Normalize list responses from SDK resources."""
        if result is None:
            return []
        if isinstance(result, list):
            return result
        if isinstance(result, tuple):
            return list(result)
        if isinstance(result, Mapping):
            for key in ("data", "items", "results"):
                value = result.get(key)
                if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                    return list(value)
            return [dict(result)]
        for key in ("data", "items", "results"):
            value = getattr(result, key, None)
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                return list(value)
        if isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
            return list(result)
        return [result]
