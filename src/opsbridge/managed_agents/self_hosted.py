"""Self-hosted sandbox helpers."""

from __future__ import annotations


def create_sandbox_config(
    name: str,
    worker_image: str,
    workdir: str,
    network_policy: dict[str, object],
    filesystem_policy: dict[str, object],
) -> dict[str, object]:
    """Create self-hosted sandbox configuration."""
    return {
        "name": name,
        "worker_image": worker_image,
        "workdir": workdir,
        "network_policy": network_policy,
        "filesystem_policy": filesystem_policy,
    }
