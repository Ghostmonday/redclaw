---
name: mempalace
description: Canonical long-term memory through MemPalace MCP. Use mempalace__* for durable recall, filing, duplicate checks, and knowledge graph operations before relying on workspace MEMORY.md or embedding search alone.
version: "1.2.0"
triggers:
  - "what did we talk about"
  - "what did we decide"
  - "last week"
  - "last month"
  - "remember that"
  - "have we discussed"
  - "recall"
  - "search memory"
  - "long-term memory"
  - "mempalace"
user-invocable: true
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["python3"]
---

# MemPalace — Canonical Long-Term Memory

MemPalace is the durable memory authority for RedClaw.

Use it before answering from guesswork when the user asks about history, decisions, preferences, past project state, or anything that should persist across sessions.

## Memory Layers

| Layer | Role |
| --- | --- |
| MemPalace | Canonical durable memory: decisions, preferences, safety boundaries, project facts, distilled email context, lessons, knowledge graph. |
| Workspace `MEMORY.md` | Low-token startup index and routing hint only. Not the final authority. |
| `memory/` daily logs | Raw/working notes that may be mined or distilled. Not canonical until curated. |
| OpenClaw `memorySearch` | Optional fuzzy recall over indexed text. Helpful, but not a substitute for MemPalace. |

## Default Workflow

For durable recall:

1. Call `mempalace__mempalace_status`.
2. Call `mempalace__mempalace_search` with a specific query.
3. Use workspace `MEMORY.md` only as an index/hint.
4. Cite or summarize the retrieved durable facts.
5. State uncertainty if the palace is unavailable or results conflict.

For durable writes:

1. Classify the memory.
2. Check duplicates first when possible.
3. File only if the memory will matter later.
4. Store distilled facts, not raw logs.
5. Never file secrets or raw private email bodies.

## Core Tools

### `mempalace__mempalace_status`

Use to verify palace health before important recall/write work.

### `mempalace__mempalace_search`

Use for past decisions, history, preferences, or exact phrasing across time/channels.

Arguments:

- `query` — required
- `limit` — optional, default 5
- `wing` / `room` — optional filters

### `mempalace__mempalace_check_duplicate`

Use before filing likely duplicate durable memory.

### `mempalace__mempalace_add_drawer`

Use for durable decisions, policies, lessons, preferences, and source-backed facts.

Recommended content shape:

```json
{
  "subject": "short stable name",
  "type": "user_preference | project_fact | decision | lesson | safety_boundary | email_context | recurring_obligation | tool_preference | infrastructure_fact",
  "project": "general | redclaw | openclaw-custom-skills | fightcitytickets | parkingbreaker | fatedfortress | maton | mempalace",
  "source": "conversation | repo | email | calendar | manual | maton | github",
  "confidence": "high | medium | low",
  "summary": "one concrete sentence",
  "evidence": "what proved it",
  "sensitivity": "public | internal | private",
  "updated_at": "ISO-8601 timestamp"
}
```

## Taxonomy Guidance

Prefer:

- `wing` = project or domain
- `room` = topic or subsystem

Examples:

| Memory | Wing | Room |
| --- | --- | --- |
| Amir's working style | `general` | `user-preferences` |
| Maton inbox policy | `maton` | `email-triage` |
| ParkingBreaker ad-spend rule | `parkingbreaker` | `ad-ops` |
| RedClaw skill audit policy | `redclaw` | `skills` |
| Mempalace curation policy | `mempalace` | `curation` |

## Knowledge Graph Tools

Use when relationships matter:

- `mempalace__mempalace_kg_query`
- `mempalace__mempalace_kg_add`
- `mempalace__mempalace_kg_invalidate`
- `mempalace__mempalace_kg_timeline`
- `mempalace__mempalace_kg_stats`

## Diary Tools

Use sparingly for agent diary entries, not raw transcripts:

- `mempalace__mempalace_diary_write`
- `mempalace__mempalace_diary_read`

## Never Store

- API keys
- passwords
- OAuth or refresh tokens
- private keys
- payment credentials
- raw mailbox exports
- full private email bodies
- unredacted secret locations
- full command logs unless they are specifically needed and sanitized

## Conflict Rules

When memories conflict:

1. Recent explicit user instruction wins.
2. Repo evidence wins for repo facts.
3. Higher confidence wins when evidence is comparable.
4. Mark stale/superseded facts rather than silently deleting.
5. Human review is required for conflicts involving secrets, money, production, public messaging, or email sending.

## When Not To Use MemPalace

Do not file:

- ephemeral chit-chat
- one-off command output
- raw logs
- vague impressions
- secrets
- data that belongs only in a project repo or secret manager

## Final Rule

MemPalace should make future recall sharper and safer. File less, curate more, and keep every durable memory specific, source-backed, and useful.
