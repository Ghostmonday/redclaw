# Research-Backed OpenClaw Configuration Findings

This file distills the uploaded OpenClaw workspace configuration research into implementation-ready RedClaw guidance.

## Core Finding

OpenClaw should be configured as a layered durable control plane:

- `AGENTS.md` and `SOUL.md` for always-loaded operating policy and persona
- `MEMORY.md` and memory tooling for curated durable memory
- `HEARTBEAT.md` for lightweight periodic intent
- cron for exact-time automation
- `~/.openclaw/openclaw.json` for explicit per-agent runtime policy, prompt budgets, session boundaries, heartbeat behavior, and skill allowlists

The research specifically warns that configuration should affect runtime behavior through known OpenClaw mechanisms: workspace bootstrap loading, system prompt assembly, per-agent override merging, visible-skill filtering, and session-key construction.

## Safety Finding

Docs and runtime behavior may diverge. Critical limits and privacy boundaries should be set explicitly in `~/.openclaw/openclaw.json` instead of relying on defaults.

Important implications:

- Do not assume `MEMORY.md` is always main-session-only in every context.
- Do not store secrets or highly sensitive data in workspace files.
- Validate bootstrap changes in a fresh or reset session.
- Restart the gateway when immediate propagation matters.
- Treat the live config schema as stronger than prose docs when there is disagreement.

## High-Leverage Configuration Priorities

1. Explicit session isolation using `session.dmScope`, `identityLinks`, and per-agent workspaces.
2. Explicit bootstrap prompt budgets and truncation warnings.
3. Deterministic skill visibility through per-agent allowlists.
4. Workspace `/skills` for highest-precedence behavior overrides.
5. Lean `HEARTBEAT.md` plus cron for exact-time tasks.
6. Semantic memory/search configuration instead of overloading `MEMORY.md`.
7. Explicit heartbeat config: light context, isolated session, active hours, ack handling.
8. Validation commands after every config change.
9. Separate RedClaw/OpenClaw configuration from ParkingBreaker/FightCityTickets ops.
10. Treat local workspace files as private but never as a secrets store.

## Mempalace Requirement

Mempalace should be the canonical durable memory layer. Local files can bootstrap or summarize, but should not be treated as final authority when Mempalace is available.

Durable memory writes should include:

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

## Maton Requirement

Maton should be the canonical interface for both Gmail accounts.

Email rules:

- Maton for reading, triage, labels, drafts, replies, summaries, and recurring checks.
- No send/delete/unsubscribe/forward/filter changes without explicit approval.
- Email-derived durable preferences go to Mempalace.
- Raw private email bodies should not be stored as durable memory unless explicitly requested.

## Recommended `openclaw.json` Skeleton

Verify all fields against the live schema before applying.

```json5
{
  session: {
    dmScope: "per-channel-peer",
    reset: { mode: "daily", atHour: 4 },
    resetByType: {
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
      thread: { mode: "daily", atHour: 4 }
    }
  },
  agents: {
    defaults: {
      contextInjection: "continuation-skip",
      bootstrapMaxChars: 12000,
      bootstrapTotalMaxChars: 60000,
      bootstrapPromptTruncationWarning: "always",
      heartbeat: {
        every: "30m",
        includeReasoning: false,
        includeSystemPromptSection: true,
        lightContext: true,
        isolatedSession: true,
        target: "last",
        directPolicy: "allow",
        ackMaxChars: 300,
        timeoutSeconds: 45,
        activeHours: {
          start: "08:00",
          end: "22:00",
          timezone: "America/Los_Angeles"
        }
      },
      memorySearch: {
        enabled: true,
        sync: {
          onSessionStart: true,
          onSearch: true,
          watch: true,
          watchDebounceMs: 1500
        },
        query: {
          maxResults: 8,
          minScore: 0.35,
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4
          }
        }
      },
      skills: [
        "mempalace-memory",
        "maton-email-operator",
        "github"
      ]
    }
  },
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250
    },
    limits: {
      maxSkillsPromptChars: 18000
    }
  }
}
```

## Cron Direction

Use cron for exact-time automation. Keep heartbeat for soft periodic checks.

Recommended cron categories:

- Maton both-account email triage
- Mempalace memory consolidation/checks
- ParkingBreaker telemetry pipeline
- daily brief
- standup carry-forward

Avoid putting exact schedules inside `HEARTBEAT.md`.

## Validation Checklist

Run these after implementation on the real machine:

```bash
openclaw config schema
openclaw config get session.dmScope
openclaw sessions --all-agents --json
openclaw skills check
openclaw memory status --deep --agent personal
openclaw memory search "concise status reports" --agent personal
openclaw system heartbeat last
openclaw cron list
```

Expected behavior:

- fresh sessions reflect edited workspace/config
- skill allowlists show only intended skills
- Mempalace/memory search works before important recall/update tasks
- heartbeat stays quiet with `HEARTBEAT_OK` when no action exists
- exact-time work lives in cron, not heartbeat bloat

## Do Not Do

- Do not store secrets in workspace files.
- Do not rely on undocumented defaults for critical prompt budgets or privacy behavior.
- Do not use heartbeat for exact-time jobs.
- Do not assume bootstrap edits affect an existing session immediately.
- Do not let root identity files become huge operational dumping grounds.
- Do not bypass Maton for email mutations.
- Do not bypass Mempalace for durable memory.
