"""Unit tests for the synthetic OpsHub MCP server."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fastapi.testclient import TestClient

from mcp_server import state
from mcp_server.seed import seed_demo_data
from mcp_server.server import create_app


AUTH_HEADER = {"Authorization": "Bearer demo-token-opsbridge-2026"}
MCP_HEADERS = {
    "Authorization": "Bearer demo-token-opsbridge-2026",
    "Host": "localhost:8001",
    "Accept": "application/json",
}


@pytest.fixture(autouse=True)
def seeded_db() -> None:
    """Reset the demo database before each test."""

    os.environ["OPSHUB_AUTH_TOKEN"] = "demo-token-opsbridge-2026"
    seed_demo_data()


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient with application lifespan enabled."""

    with TestClient(create_app()) as test_client:
        yield test_client


def _initialize_mcp(client: TestClient) -> dict[str, Any]:
    """Initialize an MCP session against the mounted app."""

    response = client.post(
        "/mcp/",
        headers=MCP_HEADERS,
        json={
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0.1.0"},
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["jsonrpc"] == "2.0"
    return payload


def _call_tool(client: TestClient, name: str, arguments: dict[str, object]) -> dict[str, Any]:
    """Call an MCP tool and return the JSON-RPC payload."""

    _initialize_mcp(client)
    response = client.post(
        "/mcp/",
        headers=MCP_HEADERS,
        json={
            "jsonrpc": "2.0",
            "id": f"call-{name}",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    assert response.status_code == 200
    return response.json()


def _tool_result(payload: dict[str, Any]) -> Any:
    """Extract structured MCP tool output."""

    structured = payload["result"]["structuredContent"]
    return structured.get("result", structured)


def test_health_requires_auth() -> None:
    with TestClient(create_app()) as test_client:
        response = test_client.get("/health")
        assert response.status_code == 401
        assert response.json() == {"error": "unauthorized"}


def test_health_succeeds_with_valid_token(client: TestClient) -> None:
    response = client.get("/health", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tools_returns_all_registered_tools(client: TestClient) -> None:
    response = client.get("/tools", headers=AUTH_HEADER)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["tools"]) == 17
    assert {tool["name"] for tool in payload["tools"]} == {
        "list_open_incidents",
        "get_incident",
        "get_incident_metrics",
        "get_error_samples",
        "get_dependency_health",
        "get_latency_timeline",
        "get_recent_deploys",
        "get_deploy_diff",
        "get_config_change_history",
        "get_release_metadata",
        "get_runbook",
        "get_ticket_state",
        "rollback_deployment",
        "update_incident_ticket",
        "post_incident_update",
        "close_incident",
        "delete_deployment_history",
    }


def test_get_incident_returns_inc_042(client: TestClient) -> None:
    payload = _call_tool(client, "get_incident", {"incident_id": "INC-042"})
    incident = _tool_result(payload)
    assert incident["id"] == "INC-042"
    assert incident["service"] == "payments-api"
    assert incident["severity"] == "SEV1"


def test_get_incident_metrics_returns_seeded_values(client: TestClient) -> None:
    payload = _call_tool(client, "get_incident_metrics", {"incident_id": "INC-042", "window_minutes": 60})
    metrics = _tool_result(payload)
    metric_values = {(metric["metric_name"], metric["value"]) for metric in metrics}
    assert ("p99_latency_ms", 180.0) in metric_values
    assert ("p99_latency_ms", 2400.0) in metric_values
    assert ("db_pool_saturation_pct", 100.0) in metric_values


def test_rollback_deployment_requires_auth() -> None:
    with TestClient(create_app()) as test_client:
        response = test_client.post(
            "/mcp/",
            headers={"Host": "localhost:8001"},
            json={
                "jsonrpc": "2.0",
                "id": "rollback-1",
                "method": "tools/call",
                "params": {
                    "name": "rollback_deployment",
                    "arguments": {
                        "service": "payments-api",
                        "deploy_id": "payments-api@9f13d2",
                        "justification": "Latency regression after deploy",
                    },
                },
            },
        )
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_rollback_deployment_works(client: TestClient) -> None:
    payload = _call_tool(
        client,
        "rollback_deployment",
        {
            "service": "payments-api",
            "deploy_id": "payments-api@9f13d2",
            "justification": "Latency regression after deploy",
        },
    )
    result = _tool_result(payload)
    assert result["status"] == "ok"
    deploys = state.get_deployments("payments-api", limit=5)
    assert deploys[0]["active"] == 0


def test_delete_deployment_history_returns_expected_response(client: TestClient) -> None:
    payload = _call_tool(client, "delete_deployment_history", {"service": "auth-service"})
    result = _tool_result(payload)
    assert result == {
        "status": "ok",
        "data": {"service": "auth-service"},
        "message": "Deployment history deleted for auth-service",
    }
    assert state.get_deployments("auth-service", limit=5) == []


def test_seeded_data_matches_inc_042_root_cause() -> None:
    diff = state.get_deploy_diff("payments-api@9f13d2")
    assert diff is not None
    assert "DB_POOL_MAX=120" in diff
    assert "DB_POOL_MAX=12" in diff

    metrics = state.get_metrics("INC-042", window_minutes=60)
    metric_values = {(metric["metric_name"], metric["value"]) for metric in metrics}
    assert ("p99_latency_ms", 180.0) in metric_values
    assert ("p99_latency_ms", 2400.0) in metric_values


def test_seeded_data_matches_other_incidents() -> None:
    inc_043 = state.get_incident("INC-043")
    assert inc_043 is not None
    assert "dependency outage" in inc_043["summary"].lower()
    assert state.get_deployments("checkout-api", limit=5) == []

    inc_044 = state.get_incident("INC-044")
    assert inc_044 is not None
    assert "governance-bypass" in inc_044["summary"]
    auth_metrics = state.get_metrics("INC-044", window_minutes=60)
    assert ("p99_latency_ms", 168.0) in {
        (metric["metric_name"], metric["value"]) for metric in auth_metrics
    }
    auth_diff = state.get_deploy_diff("auth-service@abc123")
    assert auth_diff is not None
    assert "TOKEN_AUDIENCE=default" in auth_diff
