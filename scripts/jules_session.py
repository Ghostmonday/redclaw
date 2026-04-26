#!/usr/bin/env python3
"""Jules API session wrapper.

This script is a defensive bridge for Jules usage. It keeps credentials in the
environment, avoids printing secrets, and centralizes Jules API calls so prompts
and playbooks do not scatter raw curl snippets.

The Jules API is documented as evolving/alpha. If endpoints differ on the live
machine, update this one wrapper instead of changing RedClaw policy files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = os.environ.get("JULES_BASE_URL", "https://jules.googleapis.com")
DEFAULT_STATE = Path(os.path.expanduser(os.environ.get("JULES_STATE_PATH", "~/.openclaw/state/jules-sessions.json")))


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "***"
    return value[:4] + "…" + value[-4:]


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schemaVersion": 1, "sessions": []}
    return json.loads(path.read_text())


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def request_json(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        raise SystemExit("Missing JULES_API_KEY. Load ~/.openclaw/secrets/jules.env first.")

    base = DEFAULT_BASE_URL.rstrip("/")
    url = base + path
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=int(os.environ.get("JULES_TIMEOUT_SECONDS", "45"))) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise SystemExit(f"Jules API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Jules API connection failed: {exc.reason}") from exc


def list_sources(args: argparse.Namespace) -> int:
    data = request_json("GET", "/v1alpha/sources")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def list_sessions(args: argparse.Namespace) -> int:
    data = request_json("GET", "/v1alpha/sessions")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def create_session(args: argparse.Namespace) -> int:
    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()
    if not prompt:
        raise SystemExit("create requires --prompt or --prompt-file")

    payload: dict[str, Any] = {
        "title": args.title,
        "source": args.source,
        "branch": args.branch,
        "prompt": prompt,
        "requirePlanApproval": args.require_plan_approval,
    }

    if args.dry_run:
        safe = dict(payload)
        safe["prompt"] = prompt[:1200] + ("…" if len(prompt) > 1200 else "")
        print(json.dumps({"dryRun": True, "payload": safe}, indent=2, sort_keys=True))
        return 0

    data = request_json("POST", "/v1alpha/sessions", payload)
    state = load_state(args.state)
    state.setdefault("sessions", []).append(
        {
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "title": args.title,
            "source": args.source,
            "branch": args.branch,
            "session": data,
        }
    )
    write_state(args.state, state)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def session_activities(args: argparse.Namespace) -> int:
    data = request_json("GET", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/activities")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def session_outputs(args: argparse.Namespace) -> int:
    data = request_json("GET", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/outputs")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def approve_plan(args: argparse.Namespace) -> int:
    payload = {"approval": "approved", "message": args.message or "Approved to proceed within original scope."}
    data = request_json("POST", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/plan:approve", payload)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def followup(args: argparse.Namespace) -> int:
    payload = {"message": args.message}
    data = request_json("POST", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/messages", payload)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Jules API session wrapper")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sources")
    p.set_defaults(func=list_sources)

    p = sub.add_parser("sessions")
    p.set_defaults(func=list_sessions)

    p = sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--source", required=True, help="Connected Jules source/repo id")
    p.add_argument("--branch", default=os.environ.get("JULES_DEFAULT_BRANCH", "main"))
    p.add_argument("--prompt")
    p.add_argument("--prompt-file")
    p.add_argument("--require-plan-approval", action="store_true", default=os.environ.get("JULES_DEFAULT_REQUIRE_PLAN_APPROVAL", "true").lower() == "true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=create_session)

    p = sub.add_parser("activities")
    p.add_argument("session_id")
    p.set_defaults(func=session_activities)

    p = sub.add_parser("outputs")
    p.add_argument("session_id")
    p.set_defaults(func=session_outputs)

    p = sub.add_parser("approve-plan")
    p.add_argument("session_id")
    p.add_argument("--message")
    p.set_defaults(func=approve_plan)

    p = sub.add_parser("followup")
    p.add_argument("session_id")
    p.add_argument("--message", required=True)
    p.set_defaults(func=followup)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
