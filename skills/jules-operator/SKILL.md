---
name: jules-operator
description: Use Jules as a delegated GitHub coding agent through its dashboard/API. Invoke when creating Jules tasks, routing GitHub issues, monitoring Jules sessions, approving plans, reviewing PR outputs, or recovering blocked Jules work.
---

# Jules Operator

Jules is a delegated coding/implementation agent connected to GitHub.

Use Jules for bounded repo implementation work: bug fixes, tests, dependency bumps, scoped features, refactors, documentation updates, and isolated migration tasks.

Jules is powerful, but it is not the source of truth. RedClaw remains responsible for framing, safety, review, merge discipline, and memory capture.

## Deep Integration Model

Preferred flow:

```text
RedClaw frames task
  ↓
Jules API creates session against a connected GitHub source
  ↓
Jules VM clones repo, plans, edits, tests
  ↓
Jules produces activities and optionally a PR
  ↓
RedClaw reviews plan/diff/test output
  ↓
Human approval for risky merge/deploy/public effects
  ↓
Mempalace stores distilled decision/lesson
```

## Core Rules

- Use Jules for implementation delegation, not blind authority.
- Keep Jules tasks scoped and testable.
- Prefer requiring plan approval for risky or broad work.
- Inspect Jules diffs and test results before merge/pull.
- Never paste API keys, secrets, private email bodies, or credentials into Jules prompts.
- Stash or commit local changes before pulling Jules updates.
- Record durable lessons/decisions in Mempalace after useful Jules work.

## Best Jules Task Types

Good Jules tasks:

- add tests for a known module
- fix a specific bug with reproduction steps
- update docs for a specific feature
- implement one bounded feature behind existing patterns
- bump a dependency and fix resulting tests
- add validation around an existing script
- generate a PR for review

Bad Jules tasks:

- “improve the whole app”
- ambiguous root-identity rewrites
- live production mutation
- secret/key handling
- DNS/billing/payment changes
- public messaging or email sending
- large unbounded redesigns without acceptance criteria

## Repo Preparation

Every Jules-targeted repo should have a root `AGENTS.md` that includes:

- project purpose
- install/test commands
- coding conventions
- forbidden files/actions
- safety boundaries
- PR expectations
- where to add tests
- how to validate changes

Jules reads repo `AGENTS.md`, so keeping it current materially improves Jules output.

## API Concepts

Jules API resources:

- `Source` — connected GitHub repository.
- `Session` — a unit of work with prompt/source/branch.
- `Activity` — progress, messages, plan, completion, or follow-up inside a session.
- `Output` — result artifacts such as PRs.

Use API wrappers instead of raw curl scattered across prompts.

## Session Creation Policy

Default session settings:

- source: exact GitHub repo source
- branch: current target branch or a dedicated task branch
- title: short imperative task title
- prompt: bounded, acceptance-test driven
- require plan approval: true for risky/broad work; false only for low-risk docs/tests

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
- Do not touch secrets, credentials, billing, DNS, production deploys, or public messaging.
- Do not make broad rewrites outside the listed scope.
- Preserve existing style and patterns.

Validation:
- Run <exact test/lint/build command if known>.
- Report what passed, failed, or could not be run.
```

## Review Policy

Before accepting Jules output:

1. Inspect the plan.
2. Inspect changed files.
3. Check tests/build logs.
4. Confirm no secrets or unrelated rewrites.
5. Confirm acceptance criteria.
6. Merge only after explicit approval when the change is risky.

## Blocked / Awaiting Feedback Policy

If Jules is waiting for feedback:

- read the latest activity
- answer only the specific blocker
- keep scope bounded
- do not change task goals mid-session unless necessary
- if scope changed substantially, start a new Jules session

## Mempalace Integration

After meaningful Jules work, store distilled memory:

- task type
- repo
- files/patterns touched
- validation result
- lesson learned
- whether Jules was reliable for that task type

Do not store raw diffs or secrets.

## Failure Behavior

If Jules API/CLI is unavailable:

```text
Jules unavailable. I will not pretend a session was created. I can prepare a Jules-ready task prompt and validation checklist instead.
```

## Final Rule

Jules should multiply implementation throughput without weakening review, safety, or repo discipline.
