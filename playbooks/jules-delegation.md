# Jules Delegation Playbook

Jules is the delegated coding agent. RedClaw uses Jules for bounded implementation, then reviews the result before merge/deploy.

## Setup

Create local secret file:

```bash
mkdir -p ~/.openclaw/secrets ~/.openclaw/state
cp config/jules.env.example ~/.openclaw/secrets/jules.env
chmod 600 ~/.openclaw/secrets/jules.env
```

Edit `~/.openclaw/secrets/jules.env` and add the real `JULES_API_KEY`.

Load before use:

```bash
. ~/.openclaw/secrets/jules.env
```

## Validate API Access

```bash
python3 scripts/jules_session.py sources
python3 scripts/jules_session.py sessions
```

If this fails, do not pretend Jules is available. Prepare a Jules-ready prompt instead.

## Deep Integration Pattern

1. Confirm the target repo is connected as a Jules source.
2. Confirm the target repo has a useful root `AGENTS.md`.
3. Create a scoped Jules task with acceptance criteria.
4. Require plan approval for broad/risky work.
5. Review activities and plan.
6. Approve only if scope is safe.
7. Inspect outputs/PRs.
8. Validate tests/build locally or in CI.
9. Store durable lesson in Mempalace if useful.

## Create a Dry Run Session Payload

```bash
python3 scripts/jules_session.py create \
  --dry-run \
  --title "Add tests for Maton triage runner" \
  --source "Ghostmonday/redclaw" \
  --branch main \
  --prompt-file /tmp/jules-task.md
```

## Create Real Session

```bash
python3 scripts/jules_session.py create \
  --title "Add tests for Maton triage runner" \
  --source "Ghostmonday/redclaw" \
  --branch main \
  --prompt-file /tmp/jules-task.md \
  --require-plan-approval
```

## Inspect Session

```bash
python3 scripts/jules_session.py activities <session_id>
python3 scripts/jules_session.py outputs <session_id>
```

## Approve Plan

```bash
python3 scripts/jules_session.py approve-plan <session_id> \
  --message "Approved. Stay within the original scope and do not touch secrets, billing, email sends, or production deploys."
```

## Send Follow-Up

```bash
python3 scripts/jules_session.py followup <session_id> \
  --message "Please add one regression test for the degraded Maton bridge path and report the exact test command you ran."
```

## Jules Prompt Template

```text
Repo: <owner/repo>
Branch: <branch>
Task: <one bounded implementation task>

Context:
- <relevant files/features>
- <known constraints>

Acceptance criteria:
- <observable result 1>
- <observable result 2>
- tests/docs updated where appropriate

Safety:
- Do not touch secrets, credentials, billing, DNS, production deploys, public messaging, email sending, or ad spend.
- Do not make broad rewrites outside the listed scope.
- Preserve existing style and patterns.

Validation:
- Run <exact test/lint/build command if known>.
- Report what passed, failed, or could not be run.
```

## When To Use Jules

Use Jules for:

- test creation
- focused bug fixes
- small refactors
- validation scripts
- dependency bumps
- narrow feature implementation
- documentation updates with code awareness

Do not use Jules for:

- secrets or credential handling
- DNS/billing/payment changes
- live production mutation
- sending email or public posts
- broad root identity rewrites
- huge redesigns without acceptance criteria

## Review Checklist

Before merging/pulling Jules work:

- plan reviewed
- changed files reviewed
- tests/build checked
- no secrets introduced
- no unrelated rewrites
- acceptance criteria met
- risky actions explicitly approved

## Mempalace Capture

After useful Jules work, write a distilled lesson:

```json
{
  "type": "lesson",
  "project": "redclaw",
  "source": "jules",
  "confidence": "medium",
  "summary": "Jules reliably handled <task type> in <repo> when given <constraints>.",
  "evidence": "PR/session/test result summary",
  "updated_at": "ISO-8601 timestamp"
}
```

Do not store raw diffs or secrets in memory.
