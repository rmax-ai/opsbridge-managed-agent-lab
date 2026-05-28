"""Operational policy evaluation tools."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


REPO_ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = REPO_ROOT / "config" / "policies" / "action_policy.yaml"


class PolicyResult(BaseModel):
    """Result of evaluating an action against policy."""

    decision: str
    policy_id: str
    reasons: list[str] = Field(default_factory=list)


def evaluate_action_policy(
    actor_id: str,
    action_type: str,
    target_resource: str,
    evidence_ids: list[str],
) -> PolicyResult:
    """Evaluate an action against config/policies/action_policy.yaml."""
    policy_config = _load_policy_config(POLICY_PATH)
    rules = policy_config.get("tools", [])
    if not isinstance(rules, list):
        raise ValueError("Policy config 'tools' must be a list")

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        pattern = str(rule.get("pattern", ""))
        if not _matches_rule(pattern, action_type, target_resource):
            continue

        policy = str(rule.get("policy", "always_ask"))
        default_deny = bool(rule.get("default_deny", False))
        required_evidence = [
            str(item) for item in rule.get("required_evidence", []) if isinstance(item, str)
        ]
        missing_evidence = [
            evidence_key for evidence_key in required_evidence if evidence_key not in evidence_ids
        ]
        reasons = [
            f"actor={actor_id}",
            f"matched pattern {pattern!r}",
            f"group={rule.get('group', 'unknown')}",
        ]
        if missing_evidence:
            reasons.append(f"missing evidence: {', '.join(sorted(missing_evidence))}")
        if default_deny:
            reasons.append("default deny is enabled")

        if policy == "always_allow":
            return PolicyResult(
                decision="always_allow",
                policy_id=_policy_id(rule),
                reasons=reasons,
            )
        if default_deny or missing_evidence:
            return PolicyResult(
                decision="prohibited",
                policy_id=_policy_id(rule),
                reasons=reasons,
            )
        return PolicyResult(
            decision="approval_required",
            policy_id=_policy_id(rule),
            reasons=reasons,
        )

    return PolicyResult(
        decision="prohibited",
        policy_id="default:no-match",
        reasons=[f"actor={actor_id}", "no matching policy rule found"],
    )


def retrieve_operational_policy(policy_id: str) -> dict[str, object]:
    """Retrieve policy document text."""
    policy_config = _load_policy_config(POLICY_PATH)
    rules = policy_config.get("tools", [])
    if not isinstance(rules, list):
        raise ValueError("Policy config 'tools' must be a list")

    for rule in rules:
        if isinstance(rule, dict) and _policy_id(rule) == policy_id:
            return {str(key): value for key, value in rule.items()}
    raise KeyError(f"Policy {policy_id!r} not found")


def _load_policy_config(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Policy config at {path} must be a mapping")
    return {str(key): value for key, value in payload.items()}


def _matches_rule(pattern: str, action_type: str, target_resource: str) -> bool:
    return fnmatch(action_type, pattern) or fnmatch(target_resource, pattern)


def _policy_id(rule: dict[object, object]) -> str:
    group = str(rule.get("group", "ungrouped"))
    pattern = str(rule.get("pattern", "*"))
    return f"{group}:{pattern}"
