#!/usr/bin/env python3
"""Jules session wrapper.

Primary path: authenticated local Jules CLI bridge.
Fallback path: direct OAuth/cookie API calls if explicitly enabled.

Live validation on Amir's machine confirmed:
- `jules login` works
- `jules_session.py sessions` lists sessions via CLI bridge
- `jules_session.py sources` lists connected repos via CLI bridge

API-key auth failed with ACCESS_TOKEN_TYPE_UNSUPPORTED / API_KEY_SERVICE_BLOCKED.
Do not use API keys for Jules unless future official docs prove otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = os.environ.get("JULES_BASE_URL", "https://jules.googleapis.com")
DEFAULT_STATE = Path(os.path.expanduser(os.environ.get("JULES_STATE_PATH", "~/.openclaw/state/jules-sessions.json")))
DEFAULT_INTEGRATION_MODE = os.environ.get("JULES_INTEGRATION_MODE", "cli").lower()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schemaVersion": 1, "sessions": []}
    return json.loads(path.read_text())


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def run_cli(jules_args: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    binary = os.environ.get("JULES_CLI", "jules")
    if not shutil.which(binary):
        raise SystemExit(f"Jules CLI not found: {binary}. Run on the live machine with Jules installed.")

    return subprocess.run(
        [binary, *jules_args],
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def run_cli_passthrough(jules_args: list[str]) -> int:
    return run_cli(jules_args, capture=False).returncode


def cli_or_api(cli_args: list[str], api_func, capture: bool = False):
    mode = DEFAULT_INTEGRATION_MODE
    if mode == "cli":
        return run_cli(cli_args, capture=capture)
    if mode == "api":
        return api_func()
    raise SystemExit(f"Unsupported JULES_INTEGRATION_MODE={mode!r}; use cli or api")


def auth_headers() -> dict[str, str]:
    mode = os.environ.get("JULES_AUTH_MODE", "oauth").lower()
    token = os.environ.get("JULES_OAUTH_ACCESS_TOKEN")
    cookie = os.environ.get("JULES_AUTH_COOKIE")
    api_key = os.environ.get("JULES_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if mode in {"oauth", "access_token", "bearer"}:
        if not token:
            raise SystemExit(
                "Missing JULES_OAUTH_ACCESS_TOKEN. Prefer `jules login` with JULES_INTEGRATION_MODE=cli."
            )
        headers["Authorization"] = f"Bearer {token}"
        return headers

    if mode in {"cookie", "browser_cookie"}:
        if not cookie:
            raise SystemExit("Missing JULES_AUTH_COOKIE for cookie auth mode.")
        headers["Cookie"] = cookie
        return headers

    if mode in {"api_key", "apikey"}:
        if not api_key:
            raise SystemExit("Missing JULES_API_KEY, but API-key auth is deprecated/blocked for the observed Jules path.")
        headers["Authorization"] = f"Bearer {api_key}"
        return headers

    raise SystemExit(f"Unsupported JULES_AUTH_MODE={mode!r}")


def request_json(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    base = DEFAULT_BASE_URL.rstrip("/")
    url = base + path
    data = None
    headers = auth_headers()

    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=int(os.environ.get("JULES_TIMEOUT_SECONDS", "45"))) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        if "API_KEY_SERVICE_BLOCKED" in detail or "ACCESS_TOKEN_TYPE_UNSUPPORTED" in detail:
            detail += "\nHint: Jules rejected API-key style auth. Use the authenticated CLI bridge with `jules login`."
        raise SystemExit(f"Jules API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Jules API connection failed: {exc.reason}") from exc


def api_sources() -> dict[str, Any]:
    return request_json("GET", "/v1alpha/sources")


def api_sessions() -> dict[str, Any]:
    return request_json("GET", "/v1alpha/sessions")


def list_sources(args: argparse.Namespace) -> int:
    if DEFAULT_INTEGRATION_MODE == "cli":
        # Live machine confirmed this subcommand works via authenticated Jules CLI.
        proc = run_cli(["sources"], capture=False)
        return proc.returncode
    print(json.dumps(api_sources(), indent=2, sort_keys=True))
    return 0


def list_sessions(args: argparse.Namespace) -> int:
    if DEFAULT_INTEGRATION_MODE == "cli":
        # Live machine confirmed this subcommand works via authenticated Jules CLI.
        proc = run_cli(["sessions"], capture=False)
        return proc.returncode
    print(json.dumps(api_sessions(), indent=2, sort_keys=True))
    return 0


def create_session(args: argparse.Namespace) -> int:
    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()
    if not prompt:
        raise SystemExit("create requires --prompt or --prompt-file")

    if args.dry_run:
        payload = {
            "title": args.title,
            "source": args.source,
            "branch": args.branch,
            "prompt": prompt[:1200] + ("…" if len(prompt) > 1200 else ""),
            "requirePlanApproval": args.require_plan_approval,
            "integrationMode": DEFAULT_INTEGRATION_MODE,
        }
        print(json.dumps({"dryRun": True, "payload": payload}, indent=2, sort_keys=True))
        return 0

    if DEFAULT_INTEGRATION_MODE == "cli":
        # Conservative generic CLI mapping. If the local Jules CLI syntax changes,
        # use `scripts/jules_session.py cli -- <args>` or update only this section.
        cli_args = [
            "create",
            "--title", args.title,
            "--source", args.source,
            "--branch", args.branch,
        ]
        if args.require_plan_approval:
            cli_args.append("--require-plan-approval")
        if args.prompt_file:
            cli_args.extend(["--prompt-file", args.prompt_file])
        else:
            cli_args.extend(["--prompt", prompt])
        return run_cli(cli_args, capture=False).returncode

    payload: dict[str, Any] = {
        "title": args.title,
        "source": args.source,
        "branch": args.branch,
        "prompt": prompt,
        "requirePlanApproval": args.require_plan_approval,
    }
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
    if DEFAULT_INTEGRATION_MODE == "cli":
        return run_cli(["activities", args.session_id], capture=False).returncode
    data = request_json("GET", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/activities")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def session_outputs(args: argparse.Namespace) -> int:
    if DEFAULT_INTEGRATION_MODE == "cli":
        return run_cli(["outputs", args.session_id], capture=False).returncode
    data = request_json("GET", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/outputs")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def approve_plan(args: argparse.Namespace) -> int:
    if DEFAULT_INTEGRATION_MODE == "cli":
        cli_args = ["approve-plan", args.session_id]
        if args.message:
            cli_args.extend(["--message", args.message])
        return run_cli(cli_args, capture=False).returncode
    payload = {"approval": "approved", "message": args.message or "Approved to proceed within original scope."}
    data = request_json("POST", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/plan:approve", payload)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def followup(args: argparse.Namespace) -> int:
    if DEFAULT_INTEGRATION_MODE == "cli":
        return run_cli(["followup", args.session_id, "--message", args.message], capture=False).returncode
    payload = {"message": args.message}
    data = request_json("POST", f"/v1alpha/sessions/{urllib.parse.quote(args.session_id)}/messages", payload)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Jules CLI/API session wrapper")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("login", help="Run local Jules CLI login flow")
    p.set_defaults(func=lambda args: run_cli_passthrough(["login"]))

    p = sub.add_parser("cli", help="Pass arguments through to local Jules CLI")
    p.add_argument("jules_args", nargs=argparse.REMAINDER)
    p.set_defaults(func=lambda args: run_cli_passthrough(args.jules_args[1:] if args.jules_args[:1] == ["--"] else args.jules_args))

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
