# MEMORY.md — RedClaw Memory Index

_Last curated: 2026-04-26._

## Canonical Memory Authority

Mempalace is the canonical durable memory layer.

- Palace path: local machine only; do not expose contents here.
- Tooling: use `mempalace__*` MCP tools when available.
- Workspace files are startup hints, mirrors, and indexes only.
- Do not treat this file as the final memory authority when Mempalace is available.

## Purpose of This File

This file is a low-token index for RedClaw startup behavior.

It should contain only durable, high-signal routing and safety facts. Raw logs, stale operational snapshots, and sensitive paths do not belong here.

## Required Memory Workflow

When recall or durable memory matters:

1. Check Mempalace health/status.
2. Search Mempalace for the user/project/tool context.
3. Use this file only as a bootstrap hint.
4. Write durable memories back to Mempalace, not to random markdown.
5. Store only distilled facts, never secrets or raw private email bodies.

If Mempalace is unavailable, say so and use local context as a temporary fallback.

## Stable Identity Facts

- User: Amir / Airest
- Timezone: America/Los_Angeles
- GitHub handles/orgs: `Ghostmonday`, `NeuralDraftLLC`
- Preferred working style: direct, high-energy, practical, honest, low-bullshit
- RedClaw role: OpenClaw workspace/configuration control plane

## Canonical Project Map

| Project | Meaning | Rule |
| --- | --- | --- |
| RedClaw / OpenClaw | Agent workspace, runtime config, skills, memory, heartbeat, cron policy | Treat as configuration/control-plane work. |
| OpenClaw custom skills | Reusable skill packages | Treat custom skills as experimental until audited. |
| FightCityTickets | App/product repo for ticket-fighting work | Do not confuse with RedClaw identity. |
| ParkingBreaker | Ticket-fighting funnel, telemetry, ad ops | Treat as routed product/ops module. |
| FatedFortress | Game/MVP project | Preserve playable loop and scope discipline. |
| Maton | Email control plane | Use for both managed Gmail inboxes. |
| Mempalace | Durable memory authority | Use for canonical memory reads/writes. |

## Durable Operating Preferences

- Inspect repo/tool state before editing.
- Prefer bounded, committed changes over giant plans.
- Report what changed, what was verified, what was not verified, and the next action.
- Avoid decorative configuration that does not change runtime behavior.
- Search/inspect before guessing.
- Do not repeatedly ask for clarification when a safe partial improvement is obvious.

## Safety Boundaries

Never store these in workspace files or Mempalace:

- API keys
- passwords
- OAuth tokens
- refresh tokens
- private keys
- raw mailbox exports
- full private email bodies
- payment credentials
- production secrets

Actions requiring explicit approval:

- send email
- delete email
- unsubscribe
- forward private email
- click email links
- change email filters/account settings
- mutate live ad spend
- change DNS, billing, payments, production credentials, or public messaging
- destructive repo or production operations

## Memory Types Worth Keeping

Write to Mempalace when the item affects future behavior:

- user preference
- project fact
- decision
- lesson
- safety boundary
- recurring obligation
- tool preference
- infrastructure fact
- distilled email context from Maton

Do not write:

- raw logs
- stale status dumps
- vague praise
- duplicated transcripts
- one-off command output
- secrets or secret locations

## Current High-Priority Tool Rules

### Mempalace

Use Mempalace first for durable recall and durable writes.

### Maton

Use Maton for both managed Gmail inboxes:

- `talkfightciti` — FightCityTickets / ParkingBreaker / civic-ticket business
- `vibezbizz` — business / creator / general operations

No direct Gmail mutation unless Amir explicitly overrides the boundary.

### Custom Skills

Custom skills are experimental until audited.

Core trusted workspace skills:

- `mempalace-memory`
- `maton-email-operator`

Use `config/skill-registry.policy.json` and `scripts/audit-skills.py` before treating any other skill as trusted.

## Validation Commands

Run on the live OpenClaw machine:

```bash
openclaw skills check
openclaw memory status --deep --agent personal
openclaw memory search "Amir prefers direct concise status reports" --agent personal
python3 scripts/audit-skills.py
python3 scripts/mempalace_memory_sync.py --task status
```

## Superseded Material

Older Omega-era raw operational snapshots, repeated alert state, and stale ParkingBreaker/Lob/SendGrid/Reddit details were intentionally removed from this index.

Those details should live only in Mempalace if still valid, with confidence/status metadata, or in the relevant project repo if they are operational state.

## Final Rule

Memory should make RedClaw sharper, not heavier. Keep this file small; keep Mempalace canonical; keep secrets out.
