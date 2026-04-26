#!/usr/bin/env python3
"""Mempalace memory maintenance wrapper.

This wrapper makes the memory authority explicit and safe:
- does not store secrets
- does not store raw email bodies
- supports a generic CLI bridge through MEMPALACE_CLI_COMMAND
- writes degraded status if Mempalace is not wired yet
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT = Path(os.path.expanduser("~/.openclaw/state/mempalace-latest.json"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def run_mempalace(task: str, dry_run: bool) -> dict[str, Any]:
    command = os.environ.get("MEMPALACE_CLI_COMMAND")
    if not command:
        return {
            "status": "degraded",
            "error": "mempalace_bridge_not_configured",
            "message": "Set MEMPALACE_CLI_COMMAND or wire the Mempalace integration into this runner.",
        }

    env = os.environ.copy()
    env["MEMPALACE_TASK"] = task
    env["MEMPALACE_DRY_RUN"] = "1" if dry_run else "0"

    try:
        proc = subprocess.run(
            command,
            shell=True,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(os.environ.get("MEMPALACE_TIMEOUT_SECONDS", "45")),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "degraded", "error": "mempalace_timeout"}

    if proc.returncode != 0:
        return {
            "status": "degraded",
            "error": "mempalace_command_failed",
            "stderr": proc.stderr[-500:],
        }

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        result = {"status": "ok", "rawOutputPreview": proc.stdout[:500]}

    result.setdefault("status", "ok")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe Mempalace memory maintenance.")
    parser.add_argument("--task", default="status", choices=["status", "consolidate", "conflicts", "search-test"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result = run_mempalace(args.task, dry_run=args.dry_run)
    payload: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": now,
        "managedBy": "mempalace",
        "task": args.task,
        "dryRun": args.dry_run,
        "result": result,
    }

    write_json(args.output, payload)

    if result.get("status") == "ok":
        print("MEMPALACE_OK")
        return 0

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2


if __name__ == "__main__":
    sys.exit(main())
