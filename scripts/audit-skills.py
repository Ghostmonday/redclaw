#!/usr/bin/env python3
"""Audit RedClaw workspace skills.

This does not prove a skill works. It classifies obvious structural risk so
experimental skills are not accidentally treated as trusted runtime behavior.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
POLICY_PATH = ROOT / "config" / "skill-registry.policy.json"

SENSITIVE_WORDS = {
    "email", "gmail", "send", "delete", "unsubscribe", "forward",
    "billing", "payment", "stripe", "dns", "godaddy", "credential",
    "secret", "token", "password", "api key", "production", "deploy",
    "budget", "reddit", "ad spend", "public post", "tweet", "x.com"
}


def load_policy() -> dict[str, Any]:
    if not POLICY_PATH.exists():
        return {"coreSkills": [], "verifiedSkills": []}
    return json.loads(POLICY_PATH.read_text())


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    body = text[4:end]
    data: dict[str, str] = {}
    for line in body.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def audit_skill(skill_dir: Path, policy: dict[str, Any]) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    result: dict[str, Any] = {
        "skill": skill_dir.name,
        "path": str(skill_dir.relative_to(ROOT)),
        "trust": "experimental",
        "issues": [],
        "warnings": [],
        "sensitiveHints": [],
    }

    if not skill_md.exists():
        result["trust"] = "quarantined"
        result["issues"].append("missing SKILL.md")
        return result

    text = skill_md.read_text(errors="replace")
    fm = parse_frontmatter(text)
    if not fm.get("name"):
        result["issues"].append("missing frontmatter name")
    if not fm.get("description"):
        result["issues"].append("missing frontmatter description")

    lower = text.lower()
    for word in sorted(SENSITIVE_WORDS):
        if word in lower:
            result["sensitiveHints"].append(word)

    if len(text) > 20000:
        result["warnings"].append("large SKILL.md may consume excessive prompt budget")

    if skill_dir.name in policy.get("coreSkills", []):
        result["trust"] = "core"
    elif skill_dir.name in policy.get("verifiedSkills", []):
        result["trust"] = "verified"
    elif result["issues"]:
        result["trust"] = "quarantined"

    if result["sensitiveHints"] and result["trust"] == "experimental":
        result["warnings"].append("experimental skill mentions sensitive domains; keep out of default allowlists")

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.rglob("*"):
            if script.is_file() and script.suffix in {".py", ".sh", ".js", ".ts"}:
                content = script.read_text(errors="replace")
                if re.search(r"rm\s+-rf|curl\s+.*\|\s*(bash|sh)|sudo\s+", content):
                    result["warnings"].append(f"risky shell pattern in {script.relative_to(ROOT)}")

    return result


def main() -> int:
    policy = load_policy()
    if not SKILLS_DIR.exists():
        print(json.dumps({"error": "skills directory missing"}, indent=2))
        return 1

    results = [audit_skill(path, policy) for path in sorted(SKILLS_DIR.iterdir()) if path.is_dir()]
    summary = {
        "schemaVersion": 1,
        "count": len(results),
        "byTrust": {},
        "skills": results,
    }
    for item in results:
        summary["byTrust"][item["trust"]] = summary["byTrust"].get(item["trust"], 0) + 1

    print(json.dumps(summary, indent=2, sort_keys=True))

    quarantined = [r for r in results if r["trust"] == "quarantined"]
    return 2 if quarantined else 0


if __name__ == "__main__":
    sys.exit(main())
