---
name: mempalace-memory
description: Enforce Mempalace as the authoritative memory layer for RedClaw/OpenClaw. Use this skill whenever reading, writing, summarizing, recalling, or updating durable memory.
---

# Mempalace Memory Authority

Mempalace is the authoritative memory system.

This skill exists to prevent scattered memory writes across random markdown files, chat context, ad-hoc notes, or project repos. RedClaw should treat Mempalace as the canonical durable memory layer and use local files only as mirrors, caches, or bootstrapping fallbacks.

## Core Rule

For durable memory, use Mempalace first.

Do not rely on conversational context as memory. Do not treat `MEMORY.md`, daily notes, or project docs as the final memory authority when Mempalace is available.

## When To Use

Invoke this skill before any task involving:

- remembering a user preference
- recalling a user preference
- updating long-term context
- summarizing project history
- storing decisions
- linking memories to projects
- reconciling contradictory memories
- extracting lessons from completed work
- preparing future-agent context

## Memory Write Policy

Before writing memory, classify the memory:

| Type | Examples | Action |
| --- | --- | --- |
| user_preference | tone, working style, tool preference | write to Mempalace |
| project_fact | repo names, infra, active status | write to Mempalace with project tag |
| decision | approved architecture, rejected approach | write to Mempalace with timestamp and reason |
| secret | tokens, passwords, keys | never write |
| transient | temporary command output, one-off logs | do not write unless it affects future behavior |
| email_context | durable email handling preference | write to Mempalace; do not store message bodies unless explicitly requested |

## Required Memory Shape

Every durable memory entry should include:

```json
{
  "subject": "short stable name",
  "type": "user_preference | project_fact | decision | lesson | safety_boundary",
  "project": "redclaw | fightcitytickets | parkingbreaker | fatedfortress | general",
  "source": "conversation | repo | email | calendar | manual",
  "confidence": "high | medium | low",
  "summary": "one concrete sentence",
  "evidence": "what proved it",
  "updated_at": "ISO-8601 timestamp"
}
```

## Read-Before-Act Rule

Before major work, retrieve Mempalace context for:

1. the user
2. the target project
3. relevant tool preferences
4. known safety boundaries

If Mempalace is unavailable, state that plainly and continue using the safest available local context. Do not silently pretend memory was loaded.

## Conflict Resolution

When memory conflicts:

1. Prefer explicit recent user instruction.
2. Prefer Mempalace over local markdown mirrors.
3. Prefer repo evidence over stale conversation memory.
4. Mark the older memory as superseded rather than deleting it silently.

## Local Files Are Mirrors, Not Authority

These files can exist, but they are not the final source of truth when Mempalace is available:

- `MEMORY.md`
- `USER.md`
- `memory/YYYY-MM-DD.md`
- `memory/*.json`
- project-specific notes

Use them for bootstrapping, summaries, and low-token startup hints. Use Mempalace for canonical durable memory.

## Privacy Rules

- Never store secrets.
- Never store full private email bodies unless Amir explicitly requests it.
- Store email-derived facts as distilled memory, not raw messages.
- Keep group-chat-safe context separate from private/main-session memory.

## Failure Behavior

If Mempalace is unavailable:

```text
Mempalace unavailable. I will use local workspace context as a temporary fallback and will not claim durable memory was updated.
```

Then proceed with local files only for the current task.

## Validation Checklist

A memory workflow is valid only if:

- Mempalace was checked before important recall/update work.
- durable memory writes have project/type/source/confidence metadata.
- secrets and raw private email bodies were excluded.
- local files were treated as mirrors or fallbacks.
- any fallback was disclosed.
