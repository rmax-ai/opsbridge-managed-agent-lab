"""Unit tests for the FastAPI backend."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.opsbridge.api.main import create_app


def test_sessions_endpoints_and_sse_stream() -> None:
    client = TestClient(create_app())

    create_response = client.post(
        "/api/sessions",
        json={"incident_id": "inc_042", "metadata": {"owner": "operator-1"}},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    list_response = client.get("/api/sessions")
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["id"] == session_id

    get_response = client.get(f"/api/sessions/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json()["metadata"]["owner"] == "operator-1"

    stream_response = client.get(f"/api/sessions/{session_id}/stream")
    assert stream_response.status_code == 200
    assert "text/event-stream" in stream_response.headers["content-type"]
    assert "session.created" in stream_response.text


def test_approval_routes_update_session_status() -> None:
    client = TestClient(create_app())
    session_id = client.post("/api/sessions", json={"incident_id": "inc_043"}).json()["id"]

    interrupt_response = client.post(
        f"/api/sessions/{session_id}/interrupt",
        json={"reason": "Need operator review"},
    )
    assert interrupt_response.status_code == 200
    assert interrupt_response.json()["status"] == "idle"

    resume_response = client.post(
        f"/api/sessions/{session_id}/resume",
        json={"reason": "Approval received"},
    )
    assert resume_response.status_code == 202
    assert resume_response.json()["status"] == "running"


def test_memory_routes_return_seeded_stores_and_create_dream() -> None:
    client = TestClient(create_app())
    session_id = client.post("/api/sessions", json={"incident_id": "inc_044"}).json()["id"]

    stores_response = client.get("/api/memory/stores")
    assert stores_response.status_code == 200
    assert {store["id"] for store in stores_response.json()["stores"]} == {
        "ops_reference_material",
        "operator_learnings",
    }

    dream_response = client.post(
        "/api/memory/dreams",
        json={
            "memory_store_id": "operator_learnings",
            "session_ids": [session_id],
            "instructions": "Summarize key learnings.",
        },
    )
    assert dream_response.status_code == 201
    assert dream_response.json()["memory_store_id"] == "operator_learnings"


def test_webhooks_and_scenarios_routes() -> None:
    client = TestClient(create_app())

    scenarios_response = client.get("/api/scenarios")
    assert scenarios_response.status_code == 200
    assert len(scenarios_response.json()["scenarios"]) == 3

    start_response = client.post("/api/scenarios/inc_042/start")
    assert start_response.status_code == 201
    session_id = start_response.json()["session_id"]

    webhook_response = client.post(
        "/webhooks/anthropic",
        json={"type": "session.status_terminated", "session_id": session_id, "data": {}},
    )
    assert webhook_response.status_code == 200
    assert webhook_response.json()["status"] == "terminated"

    session_response = client.get(f"/api/sessions/{session_id}")
    assert session_response.status_code == 200
    assert session_response.json()["status"] == "terminated"


def test_cors_allows_streamlit_origin() -> None:
    client = TestClient(create_app())

    response = client.options(
        "/api/sessions",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8501"
