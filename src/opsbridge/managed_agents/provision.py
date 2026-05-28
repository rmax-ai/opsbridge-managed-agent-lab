"""Managed Agent provisioning orchestration."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from ..config import settings
from .agents import create_agent, load_agent_from_yaml
from .client import ManagedAgentClient
from .environments import create_environment_from_config, load_environment_from_yaml
from .memories import create_memory_store
from .sessions import create_session
from .vaults import create_vault


LOGGER = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_CONFIG_DIR = REPO_ROOT / "config" / "agents"
ENV_CONFIG_DIR = REPO_ROOT / "config" / "environments"


class ManagedAgentProvisioner:
    """Provision Managed Agent resources for a demo profile."""

    def __init__(self, client: ManagedAgentClient):
        self.client = client

    def create_environment(self, profile: str) -> str:
        """Create a demo environment for the requested profile."""
        filename = "cloud_demo.yaml" if profile == "cloud" else "self_hosted_demo.yaml"
        config = load_environment_from_yaml(ENV_CONFIG_DIR / filename)
        environment = create_environment_from_config(self.client, config)
        return str(environment.id)

    def create_memory_stores(self) -> dict[str, str]:
        """Create the demo memory stores."""
        stores = {
            "ops_reference_material": create_memory_store(
                self.client, "ops_reference_material", memory_type="read_only"
            ),
            "operator_learnings": create_memory_store(
                self.client, "operator_learnings", memory_type="read_write"
            ),
        }
        return {name: str(store.id) for name, store in stores.items()}

    def create_vault(self) -> str:
        """Create the OpsHub credential vault."""
        vault = create_vault(
            self.client,
            name="opshub-demo-credential",
            credential_type="bearer",
            server_url=settings.opshub_mcp_url,
            scopes=["read", "write"],
            token=settings.opshub_auth_token,
        )
        return str(vault.id)

    def create_specialist_agents(self) -> dict[str, str]:
        """Create the specialist agents used by the coordinator."""
        filenames = [
            "metrics_investigator.yaml",
            "deployment_investigator.yaml",
            "policy_reviewer.yaml",
            "remediation_executor.yaml",
        ]
        specialists: dict[str, str] = {}
        for filename in filenames:
            config = load_agent_from_yaml(AGENT_CONFIG_DIR / filename)
            agent = create_agent(
                self.client,
                name=str(config["name"]),
                role=str(config["role"]),
                instructions=str(config["instructions"]),
                tools={
                    str(key): [str(item) for item in value]
                    for key, value in config.get("tools", {}).items()
                },
                mcp_servers=[
                    {str(key): str(value) for key, value in entry.items()}
                    for entry in config.get("mcp_servers", [])
                ],
                skills=[str(item) for item in config.get("skills", [])],
                permissions={
                    str(key): str(value) for key, value in config.get("permissions", {}).items()
                },
            )
            specialists[str(config["name"])] = str(agent.id)
        return specialists

    def create_coordinator(self, specialist_ids: dict[str, str]) -> str:
        """Create the incident commander coordinator."""
        config = load_agent_from_yaml(AGENT_CONFIG_DIR / "incident_commander.yaml")
        instructions = (
            f"{config['instructions']}\n\n"
            f"Specialist agent IDs: {json.dumps(specialist_ids, sort_keys=True)}"
        )
        coordinator = create_agent(
            self.client,
            name=str(config["name"]),
            role=str(config["role"]),
            instructions=instructions,
            tools={
                str(key): [str(item) for item in value]
                for key, value in config.get("tools", {}).items()
            },
            mcp_servers=[
                {str(key): str(value) for key, value in entry.items()}
                for entry in config.get("mcp_servers", [])
            ],
            skills=[str(item) for item in config.get("skills", [])],
            permissions={
                str(key): str(value) for key, value in config.get("permissions", {}).items()
            },
        )
        return str(coordinator.id)

    def create_session(
        self,
        agent_id: str,
        environment_id: str,
        vault_ids: list[str],
        memory_store_ids: list[str],
    ) -> str:
        """Create the initial coordinator session."""
        session = create_session(
            self.client,
            agent_id=agent_id,
            environment_id=environment_id,
            vault_ids=vault_ids,
            memory_store_ids=memory_store_ids,
            metadata={"profile": "opsbridge-demo"},
        )
        return str(session.id)

    def provision_all(self, profile: str = "cloud") -> dict[str, object]:
        """Provision the full managed-agent demo stack."""
        environment_id = self.create_environment(profile)
        memory_stores = self.create_memory_stores()
        vault_id = self.create_vault()
        specialist_ids = self.create_specialist_agents()
        coordinator_id = self.create_coordinator(specialist_ids)
        session_id = self.create_session(
            agent_id=coordinator_id,
            environment_id=environment_id,
            vault_ids=[vault_id],
            memory_store_ids=list(memory_stores.values()),
        )
        return {
            "profile": profile,
            "environment_id": environment_id,
            "memory_store_ids": memory_stores,
            "vault_id": vault_id,
            "specialist_agent_ids": specialist_ids,
            "coordinator_agent_id": coordinator_id,
            "session_id": session_id,
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Provision OpsBridge Managed Agent resources")
    parser.add_argument("--profile", choices=("cloud", "self-hosted"), default="cloud")
    return parser


def main() -> int:
    """CLI entrypoint for managed-agent provisioning."""
    logging.basicConfig(level=logging.INFO)
    args = _build_parser().parse_args()
    profile = "self-hosted" if args.profile == "self-hosted" else "cloud"
    provisioner = ManagedAgentProvisioner(ManagedAgentClient())
    summary = provisioner.provision_all(profile=profile)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
