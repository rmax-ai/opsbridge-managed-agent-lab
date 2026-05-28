"""Permission policy helpers."""

from __future__ import annotations

from typing import Any

from fnmatch import fnmatch
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
import yaml


class PolicyDecision(BaseModel):
    """Result of evaluating an action against policy."""

    model_config = ConfigDict(extra="allow")

    action_name: str
    group: str | None = None
    policy: str
    allowed: bool
    requires_approval: bool
    default_deny: bool = False
    matched_pattern: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    rationale: str


def load_policy_from_yaml(path: Path) -> dict[str, Any]:
    """Load the action policy YAML."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Policy config at {path} must be a mapping")
    return data


def evaluate_policy(
    action_name: str, action_args: dict[str, object], policy_config: dict[str, object]
) -> PolicyDecision:
    """Evaluate an action against the configured policy rules."""
    rules = policy_config.get("tools", [])
    if not isinstance(rules, list):
        raise ValueError("Policy config 'tools' must be a list")

    evidence = action_args.get("evidence", {})
    evidence_map = evidence if isinstance(evidence, dict) else {}

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        pattern = str(rule.get("pattern", ""))
        if not fnmatch(action_name, pattern):
            continue

        required_evidence = [
            str(item) for item in rule.get("required_evidence", []) if isinstance(item, str)
        ]
        missing_evidence = [item for item in required_evidence if not bool(evidence_map.get(item))]
        policy = str(rule.get("policy", "always_ask"))
        default_deny = bool(rule.get("default_deny", False))
        requires_approval = policy == "always_ask"
        allowed = policy == "always_allow" or (requires_approval and not default_deny)
        if missing_evidence and requires_approval:
            allowed = False

        return PolicyDecision(
            action_name=action_name,
            group=str(rule.get("group")) if rule.get("group") is not None else None,
            policy=policy,
            allowed=allowed,
            requires_approval=requires_approval,
            default_deny=default_deny,
            matched_pattern=pattern,
            missing_evidence=missing_evidence,
            rationale=(f"Matched policy pattern {pattern!r} in group {rule.get('group')!r}"),
        )

    return PolicyDecision(
        action_name=action_name,
        group=None,
        policy="deny",
        allowed=False,
        requires_approval=False,
        default_deny=True,
        matched_pattern=None,
        missing_evidence=[],
        rationale="No matching policy rule found",
    )
