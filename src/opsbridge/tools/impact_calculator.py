"""Incident impact calculation tool."""

from __future__ import annotations

from pydantic import BaseModel


class ImpactEstimate(BaseModel):
    """Deterministic estimate of incident impact."""

    total_requests_affected: int
    total_failures: int
    estimated_loss: float
    severity: str


def calculate_incident_cost(
    affected_requests: int,
    failed_authorizations: int,
    estimated_loss_per_failure: float,
) -> ImpactEstimate:
    """Compute a deterministic impact estimate."""
    total_failures = max(failed_authorizations, 0)
    total_requests_affected = max(affected_requests, 0)
    estimated_loss = float(total_failures) * max(estimated_loss_per_failure, 0.0)

    if estimated_loss >= 100_000 or total_failures >= 1_000:
        severity = "critical"
    elif estimated_loss >= 10_000 or total_failures >= 100:
        severity = "high"
    elif estimated_loss >= 1_000 or total_failures >= 10 or total_requests_affected >= 1_000:
        severity = "medium"
    else:
        severity = "low"

    return ImpactEstimate(
        total_requests_affected=total_requests_affected,
        total_failures=total_failures,
        estimated_loss=estimated_loss,
        severity=severity,
    )
