"""Self-hosted sandbox worker process.

Receives execution requests and runs them in a controlled local environment.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKDIR = Path("/workspace")
ALLOWED_HOSTS_PATH = WORKDIR / "policy" / "allowed_hosts.yaml"
FILESYSTEM_POLICY_PATH = WORKDIR / "policy" / "filesystem_policy.yaml"


def load_policy(path: Path) -> dict:
    """Load a YAML policy file."""
    import yaml
    with open(path) as f:
        return yaml.safe_load(f) or {}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool in the sandbox environment."""
    logger.info("Executing tool: %s with args: %s", tool_name, arguments)

    if tool_name == "bash":
        result = subprocess.run(
            arguments.get("command", ""),
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }

    if tool_name == "read_file":
        path = Path(arguments.get("path", ""))
        if not path.is_relative_to(WORKDIR):
            return {"error": "Access denied: path outside workspace"}
        return {"content": path.read_text()}

    if tool_name == "write_file":
        path = Path(arguments.get("path", ""))
        if not path.is_relative_to(WORKDIR):
            return {"error": "Access denied: path outside workspace"}
        path.write_text(arguments.get("content", ""))
        return {"status": "ok"}

    return {"error": f"Unknown tool: {tool_name}"}


def main() -> int:
    """Main worker loop reading JSON commands from stdin."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            result = execute_tool(
                request.get("tool_name", ""),
                request.get("arguments", {}),
            )
            print(json.dumps(result))
            sys.stdout.flush()
        except Exception as e:
            logger.exception("Error processing request")
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
