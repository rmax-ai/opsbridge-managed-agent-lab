"""Unit tests for managed-agents provisioner helpers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest

from src.opsbridge.managed_agents import (
    agents,
    dreams,
    environments,
    events,
    memories,
    outcomes,
    permissions,
    sessions,
    vaults,
)
from src.opsbridge.managed_agents import provision as provision_module
from src.opsbridge.managed_agents.client import ManagedAgentClient, ManagedAgentClientError
from src.opsbridge.managed_agents.permissions import PolicyDecision


class FakeResource:
    def __init__(self, name: str):
        self.name = name
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def create(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("create", kwargs))
        payload = {"id": f"{self.name}-created", **kwargs}
        if self.name == "agents":
            payload.setdefault("role", "role")
            payload.setdefault("instructions", "instructions")
            payload.setdefault("tools", {})
            payload.setdefault("mcp_servers", [])
        if self.name == "environments":
            payload.setdefault("allowlist", [])
            payload.setdefault("tools", [])
        if self.name == "sessions":
            payload.setdefault("vault_ids", [])
            payload.setdefault("memory_store_ids", [])
        return payload

    def retrieve(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("retrieve", kwargs))
        identifier = next(iter(kwargs.values()))
        if self.name == "agents":
            return {
                "id": identifier,
                "name": "agent",
                "role": "role",
                "instructions": "instructions",
                "tools": {},
                "mcp_servers": [],
                "skills": [],
                "permissions": {},
            }
        if self.name == "environments":
            return {
                "id": identifier,
                "name": "env",
                "python_version": "3.12",
                "allowlist": [],
                "tools": [],
                "outputs_dir": "/tmp/out",
                "self_hosted": False,
            }
        if self.name == "sessions":
            return {
                "id": identifier,
                "agent_id": "agent-1",
                "environment_id": "env-1",
                "vault_ids": [],
                "memory_store_ids": [],
                "metadata": {},
            }
        if self.name == "memory_stores":
            return {"id": identifier, "name": "store", "memory_type": "read_write"}
        if self.name == "vaults":
            return {
                "id": identifier,
                "name": "vault",
                "credential_type": "bearer",
                "server_url": "http://localhost",
                "scopes": [],
            }
        return {"id": identifier, "status": "completed"}

    def list(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("list", kwargs))
        if self.name == "agents":
            return {"data": [self.retrieve(agent_id="agent-1")]}
        if self.name == "sessions":
            return {"data": [self.retrieve(session_id="session-1")]}
        if self.name == "memory_stores":
            return {"data": [self.retrieve(store_id="store-1")]}
        return {"data": []}

    def update(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("update", kwargs))
        return {
            "id": kwargs["agent_id"],
            "name": "updated",
            "role": "role",
            "instructions": "instructions",
            "tools": {},
            "mcp_servers": [],
            "skills": [],
            "permissions": {},
        }

    def delete(self, **kwargs: Any) -> None:
        self.calls.append(("delete", kwargs))
        return None

    def send(self, **kwargs: Any) -> None:
        self.calls.append(("send", kwargs))
        return None

    async def _stream(self) -> AsyncIterator[dict[str, Any]]:
        yield {"type": "message", "text": "hello"}

    def stream_events(self, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        self.calls.append(("stream_events", kwargs))
        return self._stream()

    def list_events(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("list_events", kwargs))
        return {"data": [{"id": "evt-1", "type": "message"}]}

    def status(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("status", kwargs))
        if self.name == "outcomes":
            return {"session_id": kwargs["session_id"], "status": "running"}
        return {"id": kwargs["dream_id"], "status": "running"}

    def evaluations(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("evaluations", kwargs))
        return {"data": [{"criterion": "quality", "score": 0.9, "notes": "ok"}]}

    def result(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("result", kwargs))
        return {"dream_id": kwargs["dream_id"], "consolidated_store_id": "store-merged"}

    def list_files(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("list_files", kwargs))
        return {"data": [{"path": "/memo.txt", "content_type": "text/plain"}]}

    def get_file(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_file", kwargs))
        return {"content": "hello"}


class FakeBetaManagedAgents:
    def __init__(self):
        self.agents = FakeResource("agents")
        self.environments = FakeResource("environments")
        self.sessions = FakeResource("sessions")
        self.memory_stores = FakeResource("memory_stores")
        self.vaults = FakeResource("vaults")
        self.outcomes = FakeResource("outcomes")
        self.dreams = FakeResource("dreams")


class FakeClient:
    def __init__(self):
        self.beta = type("Beta", (), {"managed_agents": FakeBetaManagedAgents()})()


def make_client() -> ManagedAgentClient:
    return ManagedAgentClient(client=FakeClient())


def test_client_initialization_with_injected_client() -> None:
    client = make_client()
    assert client.beta.agents is not None


def test_client_raises_without_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = __import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "anthropic":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    with pytest.raises(ManagedAgentClientError):
        ManagedAgentClient()


def test_load_agent_yaml_parses_incident_commander() -> None:
    path = Path("config/agents/incident_commander.yaml")
    data = agents.load_agent_from_yaml(path)
    assert data["name"] == "incident_commander"
    assert data["permissions"]["mcp_write"] == "never"
    assert data["mcp_servers"] == [{"opshub": "read_only"}]


def test_load_environment_yaml_parses_cloud_demo() -> None:
    path = Path("config/environments/cloud_demo.yaml")
    data = environments.load_environment_from_yaml(path)
    assert data["name"] == "opsbridge-cloud-demo"
    assert data["network"]["allowlist"] == [
        "synthetic-opsmcp.anthropic-demo.com",
        "api.anthropic.com",
    ]


def test_policy_loading_and_evaluation() -> None:
    policy = permissions.load_policy_from_yaml(Path("config/policies/action_policy.yaml"))
    decision = permissions.evaluate_policy(
        "rollback_deployment",
        {"evidence": {"root_cause_summary": "x", "supporting_metrics": "y"}},
        policy,
    )
    assert isinstance(decision, PolicyDecision)
    assert decision.requires_approval is True
    assert decision.allowed is False
    assert set(decision.missing_evidence) == {"rollback_plan", "validation_plan"}


def test_agent_crud_helpers() -> None:
    client = make_client()
    created = agents.create_agent(
        client,
        name="agent",
        role="role",
        instructions="instructions",
        tools={},
        mcp_servers=[],
        skills=[],
        permissions={},
    )
    fetched = agents.get_agent(client, "agent-1")
    listed = agents.list_agents(client)
    updated = agents.update_agent(client, "agent-1", name="updated")
    agents.delete_agent(client, "agent-1")
    assert created.id == "agents-created"
    assert fetched.id == "agent-1"
    assert len(listed) == 1
    assert updated.name == "updated"


def test_environment_helpers() -> None:
    client = make_client()
    created = environments.create_environment(
        client,
        name="env",
        python_version="3.12",
        allowlist=["api.anthropic.com"],
        tools=["read"],
        outputs_dir="/tmp/out",
    )
    fetched = environments.get_environment(client, "env-1")
    environments.delete_environment(client, "env-1")
    assert created.id == "environments-created"
    assert fetched.id == "env-1"


def test_session_helpers() -> None:
    client = make_client()
    created = sessions.create_session(client, "agent-1", "env-1", ["vault-1"], ["store-1"], {})
    fetched = sessions.get_session(client, "session-1")
    listed = sessions.list_sessions(client)
    sessions.send_text(client, "session-1", "hello")
    sessions.send_message(client, "session-1", [{"type": "text", "text": "hello"}])
    sessions.delete_session(client, "session-1")
    assert created.id == "sessions-created"
    assert fetched.id == "session-1"
    assert len(listed) == 1


@pytest.mark.asyncio
async def test_event_helpers() -> None:
    client = make_client()
    streamed = [event async for event in events.stream_events(client, "session-1")]
    cached = events.get_events(client, "session-1")
    events.confirm_tool(client, "session-1", "evt-1", allow=True)
    events.send_interrupt(client, "session-1")
    assert streamed == [{"type": "message", "text": "hello"}]
    assert cached == [{"id": "evt-1", "type": "message"}]


def test_outcome_helpers(tmp_path: Path) -> None:
    client = make_client()
    rubric = tmp_path / "rubric.md"
    rubric.write_text("Rubric", encoding="utf-8")
    defined = outcomes.define_outcome(client, "session-1", "Fix it", rubric)
    status = outcomes.get_outcome_status(client, "session-1")
    evaluations = outcomes.get_outcome_evaluations(client, "session-1")
    assert defined.id == "outcomes-created"
    assert status.status == "running"
    assert evaluations[0].criterion == "quality"


def test_memory_helpers() -> None:
    client = make_client()
    created = memories.create_memory_store(client, "store")
    fetched = memories.get_memory_store(client, "store-1")
    listed = memories.list_memory_stores(client)
    files = memories.list_memory_files(client, "store-1")
    content = memories.get_memory_file(client, "store-1", "/memo.txt")
    assert created.id == "memory_stores-created"
    assert fetched.id == "store-1"
    assert len(listed) == 1
    assert files[0].path == "/memo.txt"
    assert content == "hello"


def test_dream_helpers() -> None:
    client = make_client()
    created = dreams.create_dream(client, "store-1", ["session-1"], "Summarize")
    status = dreams.get_dream_status(client, "dream-1")
    result = dreams.get_dream_result(client, "dream-1")
    assert created.id == "dreams-created"
    assert status.status == "running"
    assert result.consolidated_store_id == "store-merged"


def test_vault_helpers() -> None:
    client = make_client()
    created = vaults.create_vault(
        client,
        name="vault",
        credential_type="bearer",
        server_url="http://localhost",
        scopes=["read"],
        token="secret",
    )
    fetched = vaults.get_vault(client, "vault-1")
    vaults.delete_vault(client, "vault-1")
    assert created.id == "vaults-created"
    assert fetched.id == "vault-1"


def test_provisioner_orchestrates_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    provisioner = provision_module.ManagedAgentProvisioner(client)
    summary = provisioner.provision_all(profile="cloud")
    assert summary["environment_id"] == "environments-created"
    assert summary["vault_id"] == "vaults-created"
    assert summary["coordinator_agent_id"] == "agents-created"
    assert set(summary["memory_store_ids"]) == {
        "ops_reference_material",
        "operator_learnings",
    }

    captured: dict[str, Any] = {}

    class FakeProvisioner:
        def __init__(self, injected_client: ManagedAgentClient):
            assert injected_client is client

        def provision_all(self, profile: str = "cloud") -> dict[str, str]:
            captured["profile"] = profile
            return {"environment_id": "env-1"}

    monkeypatch.setattr(provision_module, "ManagedAgentProvisioner", FakeProvisioner)
    monkeypatch.setattr(provision_module, "ManagedAgentClient", lambda: client)
    monkeypatch.setattr("sys.argv", ["provision", "--profile", "cloud"])
    exit_code = provision_module.main()
    assert exit_code == 0
    assert captured["profile"] == "cloud"
