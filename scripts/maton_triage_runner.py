#!/usr/bin/env python3
"""Maton two-inbox triage runner.

This wrapper is intentionally conservative:
- credentials are read from environment variables only
- no raw keys are printed
- no direct Gmail mutation is performed
- sending/deleting/unsubscribing/forwarding is never performed here
- if Maton's exact CLI/API is not installed, the script writes a clear degraded status

The live Maton ClawHub skill/API should be wired into call_maton_triage().
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_STATE = Path(os.path.expanduser("~/.openclaw/state/maton-email-state.json"))
DEFAULT_OUTPUT = Path(os.path.expanduser("~/.openclaw/state/maton-email-latest.json"))
POLICY_PATH = Path("config/maton-triage.policy.json")


@dataclass(frozen=True)
class Account:
    name: str
    email_env: str
    key_env: str
    purpose: str


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON at {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def load_policy(path: Path) -> dict[str, Any]:
    return load_json(path, {"accounts": {}})


def accounts_from_policy(policy: dict[str, Any]) -> list[Account]:
    accounts: list[Account] = []
    for name, cfg in policy.get("accounts", {}).items():
        accounts.append(
            Account(
                name=name,
                email_env=cfg.get("emailEnv", ""),
                key_env=cfg.get("apiKeyEnv", ""),
                purpose=cfg.get("purpose", ""),
            )
        )
    return accounts


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def call_maton_triage(account: Account, since_cursor: str | None, dry_run: bool) -> dict[str, Any]:
    """Call Maton for one account.

    This function supports a generic CLI bridge if MATON_CLI_COMMAND is configured.
    Example:
      MATON_CLI_COMMAND='maton triage --json'

    The command receives env vars for the selected account and should output JSON.
    Without a configured bridge, returns a degraded status so cron/heartbeat can surface setup work.
    """

    email = os.environ.get(account.email_env)
    api_key = os.environ.get(account.key_env)

    if not email or not api_key:
        return {
            "account": account.name,
            "status": "degraded",
            "error": "missing_credentials",
            "message": f"Missing {account.email_env} or {account.key_env}",
            "items": [],
        }

    command = os.environ.get("MATON_CLI_COMMAND")
    if not command:
        return {
            "account": account.name,
            "status": "degraded",
            "error": "maton_bridge_not_configured",
            "message": "Set MATON_CLI_COMMAND or wire the Maton ClawHub skill/API into this runner.",
            "items": [],
        }

    env = os.environ.copy()
    env["MATON_ACCOUNT_ALIAS"] = account.name
    env["MATON_ACCOUNT_EMAIL"] = email
    env["MATON_ACCOUNT_API_KEY"] = api_key
    if since_cursor:
        env["MATON_SINCE_CURSOR"] = since_cursor
    env["MATON_DRY_RUN"] = "1" if dry_run else "0"

    try:
        proc = subprocess.run(
            command,
            shell=True,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(os.environ.get("MATON_TRIAGE_TIMEOUT_SECONDS", "45")),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "account": account.name,
            "status": "degraded",
            "error": "maton_timeout",
            "items": [],
        }

    if proc.returncode != 0:
        return {
            "account": account.name,
            "status": "degraded",
            "error": "maton_command_failed",
            "stderr": proc.stderr[-500:],
            "items": [],
        }

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "account": account.name,
            "status": "degraded",
            "error": "maton_non_json_output",
            "stdout_preview": proc.stdout[:500],
            "items": [],
        }

    result.setdefault("account", account.name)
    result.setdefault("status", "ok")
    result.setdefault("items", [])
    return result


def classify_actionable(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    actionable_categories = {"urgent", "security", "action_required", "lead"}
    return [item for item in items if item.get("category") in actionable_categories]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Maton triage for both managed inboxes.")
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    policy = load_policy(args.policy)
    accounts = accounts_from_policy(policy)
    if not accounts:
      raise SystemExit(f"No accounts configured in {args.policy}")

    state = load_json(args.state, {"schemaVersion": 1, "accounts": {}, "dedupe": {"messageActionHashes": {}}})
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    results: list[dict[str, Any]] = []
    surfaced: list[dict[str, Any]] = []
    degraded: list[dict[str, Any]] = []

    hashes = state.setdefault("dedupe", {}).setdefault("messageActionHashes", {})
    cooldown = int(policy.get("triage", {}).get("dedupe", {}).get("cooldownSeconds", 7200))
    now_epoch = int(time.time())

    for account in accounts:
        account_state = state.setdefault("accounts", {}).setdefault(account.name, {})
        result = call_maton_triage(account, account_state.get("lastHistoryCursor"), dry_run=args.dry_run)
        results.append(result)

        if result.get("status") != "ok":
            degraded.append(result)

        for item in classify_actionable(result.get("items", [])):
            dedupe_key = stable_hash({
                "account": account.name,
                "message_id": item.get("message_id"),
                "category": item.get("category"),
                "recommended_action": item.get("recommended_action"),
            })
            previous = hashes.get(dedupe_key, 0)
            if item.get("priority") == "P0" or now_epoch - int(previous or 0) >= cooldown:
                surfaced.append({"account": account.name, **item})
                hashes[dedupe_key] = now_epoch

        account_state["lastSyncAt"] = now
        if result.get("nextCursor"):
            account_state["lastHistoryCursor"] = result["nextCursor"]
        account_state["lastActionHash"] = stable_hash(result.get("items", []))

    status = "action_required" if surfaced or degraded else "ok"
    quiet = status == "ok"

    output = {
        "schemaVersion": 1,
        "generatedAt": now,
        "managedBy": "maton",
        "dryRun": args.dry_run,
        "status": status,
        "quietResult": "EMAIL_OK" if quiet else None,
        "surfaced": surfaced,
        "degraded": degraded,
        "accountsChecked": [a.name for a in accounts],
        "results": results,
    }

    write_json(args.state, state)
    write_json(args.output, output)

    if quiet:
        print("EMAIL_OK")
    else:
        print(json.dumps(output, indent=2, sort_keys=True))

    return 0 if not degraded else 2


if __name__ == "__main__":
    sys.exit(main())
