#!/usr/bin/env bash
set -Eeuo pipefail

# Validate workspace skills in this repo.
# Uses the bundled skill-creator validator when available and falls back to simple checks.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VALIDATOR="skills/skill-creator/scripts/quick_validate.py"

if [ -f "$VALIDATOR" ]; then
  echo "== Running skill-creator quick validator =="
  python3 "$VALIDATOR" skills
else
  echo "== Fallback skill checks =="
  failed=0
  while IFS= read -r skill; do
    if [ ! -f "$skill/SKILL.md" ]; then
      echo "FAIL: missing SKILL.md in $skill"
      failed=1
      continue
    fi
    if ! grep -q '^---$' "$skill/SKILL.md"; then
      echo "WARN: no frontmatter delimiter in $skill/SKILL.md"
    fi
    if ! grep -q '^name:' "$skill/SKILL.md"; then
      echo "FAIL: missing name frontmatter in $skill/SKILL.md"
      failed=1
    fi
    if ! grep -q '^description:' "$skill/SKILL.md"; then
      echo "FAIL: missing description frontmatter in $skill/SKILL.md"
      failed=1
    fi
  done < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
  exit "$failed"
fi
