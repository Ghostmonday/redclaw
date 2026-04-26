# OpenClaw Workspace Configuration Research Brief

## Goal

Research how to create powerful OpenClaw workspace configuration that changes real future agent behavior, not decorative documentation.

## Research Plan

- Collect official OpenClaw/RedClaw docs, changelogs, and repo examples.
- Inspect workspace bootstrap files and loading rules in code and docs.
- Analyze skills, memory, heartbeat, cron, and session precedence mechanics.
- Design prioritized config changes with concrete file examples.
- Create validation checklist, safety rules, and do-not-do section.

## Success Standard

Every recommendation must identify the exact OpenClaw mechanism that makes it affect future agent behavior.

For each recommendation, answer:

1. What file or path changes?
2. What OpenClaw mechanism makes it work?
3. What behavior improves?
4. What failure mode does it prevent?
5. How can RedClaw validate that the configuration is actually working?

## Primary Areas to Verify

### Workspace Bootstrap

Investigate how these files are loaded, when they are loaded, and whether they have session/privacy/size constraints:

- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `IDENTITY.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `MEMORY.md`
- `memory/YYYY-MM-DD.md`

### Skills

Investigate:

- workspace skills path
- skill precedence order
- when to create a skill instead of adding instructions to `AGENTS.md`
- how workspace skills interact with managed or bundled skills
- security implications of third-party or mutable skills

### Memory

Investigate:

- what memory is safe to load in main sessions
- what must not leak into group/shared sessions
- how daily memory should differ from long-term memory
- what belongs in machine-readable memory files vs prose files

### Heartbeat and Cron

Investigate:

- how `HEARTBEAT.md` is invoked
- how to keep heartbeat low-token and delta-first
- when heartbeat should return exactly `HEARTBEAT_OK`
- when recurring checks should be cron instead of heartbeat
- how to deduplicate alerts with state files

### Session Precedence and Routing

Investigate:

- how main sessions differ from channel/group sessions
- how project-specific routing can prevent repo confusion
- whether machine-readable project maps are useful
- how to encode aliases, canonical repos, safety boundaries, and default actions

## Expected Deliverables

1. Top 10 highest-leverage OpenClaw workspace configuration changes.
2. Recommended RedClaw workspace file tree.
3. Concrete snippets for each recommended file.
4. Safety policy for secrets, public actions, billing, DNS, credentials, and group chats.
5. Do-not-do list for weak/decorative configuration.
6. Validation checklist proving the setup changes actual behavior.

## Anti-Corpse-Feeding Rule

Reject recommendations that only sound impressive but do not alter runtime behavior, future agent decisions, project routing, safety, heartbeat quality, memory quality, or execution reliability.
