---
name: mempalace-memory
description: Use Mempalace as the canonical durable memory layer for RedClaw/OpenClaw. Invoke for durable recall, memory writes, preference updates, project facts, decisions, lessons, and memory conflict resolution.
---

# Mempalace Memory Authority

Mempalace is the canonical durable memory system.

Use local workspace files as startup hints, mirrors, caches, or fallbacks. Do not treat chat context, `MEMORY.md`, daily notes, project docs, or ad-hoc markdown as the final memory authority when Mempalace is available.

## Core Rule

For durable memory: read from Mempalace first, write to Mempalace first.

If Mempalace is unavailable, disclose the fallback and do not claim durable memory was updated.

## Use This Skill For

- recalling user preferences
- remembering new preferences
- storing project facts
- recording decisions
- storing safety boundaries
- summarizing project history
- extracting lessons from completed work
- reconciling conflicting memory
- preparing future-agent context
- storing durable email-handling preferences from Maton

## Memory Classification

Classify before writing:

| Type | Examples | Action |
| --- | --- | --- |
| `user_preference` | tone, workflow, tool preference | write to Mempalace |
| `project_fact` | repo names, infra, status | write with project tag |
| `decision` | approved architecture, rejected approach | write with timestamp and reason |
| `lesson` | what worked or failed | write only if actionable later |
| `safety_boundary` | never-send, no-secrets, approval rules | write with clear scope |
| `email_context` | sender preference, label rule, recurring obligation | write distilled fact; no raw body |
| `transient` | one-off command output, temporary logs | do not write unless it affects future behavior |
| `secret` | tokens, passwords, keys, private credentials | never write |

## Required Memory Shape

Every durable memory write should include:

```json
{
  "subject": "short stable name",
  "type": "user_preference | project_fact | decision | lesson | safety_boundary | email_context",
  "project": "redclaw | fightcitytickets | parkingbreaker | fatedfortress | general",
  "source": "conversation | repo | email | calendar | manual | maton",
  "confidence": "high | medium | low",
  "summary": "one concrete sentence",
  "evidence": "what proved it",
  "updated_at": "ISO-8601 timestamp"
}
```

## Read-Before-Act Rule

Before major work, retrieve Mempalace context for:

1. Amir/user preferences
2. target project
3. relevant tools
4. known safety boundaries
5. recent decisions that constrain the task

If Mempalace is unavailable:

```text
Mempalace unavailable. I will use local workspace context as a temporary fallback and will not claim durable memory was updated.
```

Then proceed only with the safest available local context.

## Write Policy

Write memory when the fact will likely matter later.

Good memory:

- specific
- source-backed
- scoped to a project or user preference
- useful for future decisions
- free of secrets/raw private content

Bad memory:

- vague praise
- raw logs
- full email bodies
- secrets
- temporary command output
- duplicated session transcripts

## Conflict Resolution

When memory conflicts:

1. Prefer explicit recent user instruction.
2. Prefer Mempalace over local markdown mirrors.
3. Prefer repo evidence over stale conversation memory.
4. Mark older memory as superseded; do not silently delete.
5. Ask only if the conflict changes a risky action.

## Local File Policy

These files are not the final source of truth when Mempalace is available:

- `MEMORY.md`
- `USER.md`
- `memory/YYYY-MM-DD.md`
- `memory/*.json`
- project-specific notes

Use them for bootstrapping and low-token summaries. Use Mempalace for canonical durable memory.

## Privacy Rules

- Never store secrets.
- Never store full private email bodies unless Amir explicitly requests it.
- Store email-derived facts as distilled memory.
- Keep group-chat-safe context separate from private memory.
- Do not expose Mempalace contents in shared contexts unless clearly safe and relevant.

## Validation Checklist

A memory workflow is valid only if:

- Mempalace was checked before important recall/update work.
- durable writes include type/project/source/confidence/evidence metadata.
- secrets and raw private email bodies were excluded.
- local files were treated as mirrors or fallbacks.
- any fallback was disclosed.
