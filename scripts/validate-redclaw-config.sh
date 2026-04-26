#!/usr/bin/env bash
set -Eeuo pipefail

# Validate RedClaw/OpenClaw configuration from the live machine.
# This script intentionally does not mutate runtime config.

section() {
  printf '\n== %s ==\n' "$1"
}

run_optional() {
  local label="$1"
  shift
  section "$label"
  if command -v "$1" >/dev/null 2>&1; then
    "$@"
  else
    echo "SKIP: command not found: $1"
    return 0
  fi
}

run_openclaw() {
  local label="$1"
  shift
  section "$label"
  if ! command -v openclaw >/dev/null 2>&1; then
    echo "FAIL: openclaw CLI not found on PATH"
    return 1
  fi
  openclaw "$@"
}

section "RedClaw config validation"
date -u +"%Y-%m-%dT%H:%M:%SZ"

run_openclaw "OpenClaw doctor" doctor || true
run_openclaw "Config schema" config schema
run_openclaw "Session dmScope" config get session.dmScope || true
run_openclaw "Bootstrap contextInjection" config get agents.defaults.contextInjection || true
run_openclaw "Bootstrap max chars" config get agents.defaults.bootstrapMaxChars || true
run_openclaw "Bootstrap total max chars" config get agents.defaults.bootstrapTotalMaxChars || true
run_openclaw "Sessions" sessions --all-agents --json || true
run_openclaw "Skills" skills check
run_openclaw "Memory status" memory status --deep --agent personal || true
run_openclaw "Heartbeat last" system heartbeat last || true
run_openclaw "Cron list" cron list || true

section "Local RedClaw repo checks"
if [ -f "AGENTS.md" ]; then echo "OK: AGENTS.md present"; else echo "WARN: AGENTS.md missing"; fi
if [ -f "SOUL.md" ]; then echo "OK: SOUL.md present"; else echo "WARN: SOUL.md missing"; fi
if [ -f "USER.md" ]; then echo "OK: USER.md present"; else echo "WARN: USER.md missing"; fi
if [ -f "HEARTBEAT.md" ]; then echo "OK: HEARTBEAT.md present"; else echo "WARN: HEARTBEAT.md missing"; fi
if [ -f "config/openclaw.recommended.json5" ]; then echo "OK: runtime config skeleton present"; else echo "WARN: config/openclaw.recommended.json5 missing"; fi
if [ -f "config/maton-triage.policy.json" ]; then echo "OK: Maton triage policy present"; else echo "WARN: Maton triage policy missing"; fi

section "Secret hygiene"
if grep -RInE '(api[_-]?key|token|secret|password)\s*[:=]\s*[A-Za-z0-9_\-]{24,}' \
  --exclude-dir=.git \
  --exclude='*.example' \
  --exclude='*.md' \
  .; then
  echo "WARN: possible committed secret-like strings found above. Review manually."
else
  echo "OK: no obvious committed secret-like strings outside examples/docs"
fi

section "Done"
echo "Validation completed. Some checks may be SKIP/WARN if run outside the live OpenClaw machine."
