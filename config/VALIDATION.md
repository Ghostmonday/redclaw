# RedClaw Configuration Validation

Use this checklist after editing RedClaw/OpenClaw runtime configuration, workspace bootstrap files, skills, heartbeat, cron, Maton, or Mempalace integrations.

## Principle

A config change is not complete until it is visible to the running OpenClaw environment.

Bootstrap files can be cached by session key, so validate in a fresh/reset session. Restart the gateway when immediate propagation matters.

## Preflight

```bash
openclaw config schema
openclaw doctor
```

Confirm:

- schema command succeeds
- no risky DM/channel policy warnings are ignored
- no secrets are stored in workspace files

## Runtime Config

```bash
openclaw config get session.dmScope
openclaw config get agents.defaults.contextInjection
openclaw config get agents.defaults.bootstrapMaxChars
openclaw config get agents.defaults.bootstrapTotalMaxChars
```

Expected:

- `session.dmScope` is explicit
- bootstrap budgets are explicit
- truncation warnings are enabled

## Sessions

```bash
openclaw sessions --all-agents --json
```

Expected:

- sessions are separated according to configured `dmScope`
- stale legacy shared-main sessions are understood before relying on routing
- group/shared contexts do not receive private memory unnecessarily

## Skills

```bash
openclaw skills check
```

Expected:

- `mempalace-memory` is visible where durable memory is needed
- `maton-email-operator` is visible where email tasks are handled
- unrelated/risky skills are not visible to agents that do not need them
- workspace skills win over lower-precedence skills with the same name

## Memory / Mempalace

```bash
openclaw memory status --deep --agent personal
openclaw memory search "Amir prefers direct concise status reports" --agent personal
```

Expected:

- memory provider is healthy
- relevant preferences can be retrieved semantically
- workspace files are mirrors/fallbacks, not the only memory source
- raw emails and secrets are absent from durable memory

## Email / Maton

Validate through Maton, not direct Gmail mutation.

Expected:

- both Gmail accounts are represented as stable Maton identities
- recurring check can return `EMAIL_OK`
- drafts can be created without sending
- send/delete/unsubscribe/forward/filter changes require explicit approval
- email-derived preferences are written to Mempalace as distilled facts

## Heartbeat

```bash
openclaw system heartbeat last
```

Expected:

- quiet cycles produce `HEARTBEAT_OK`
- no stale ParkingBreaker delta is re-alerted
- Maton `EMAIL_OK` converts to silence when no other module needs action
- Mempalace failures surface only when memory is required
- heartbeat does not run live spend or email mutations

## Cron

```bash
openclaw cron list
```

Expected:

- exact-time jobs are in cron, not `HEARTBEAT.md`
- Maton email checks are cron-capable
- ParkingBreaker telemetry pipeline is cron-capable
- Mempalace maintenance is cron-capable
- isolated jobs use the intended session/model

## Fresh Session Test

After changing `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `HEARTBEAT.md`, `MEMORY.md`, or skills:

1. Start a fresh/reset session.
2. Ask for a concise status of active project routing.
3. Confirm RedClaw distinguishes RedClaw/OpenClaw, FightCityTickets, ParkingBreaker, Maton, and Mempalace.
4. Confirm it does not claim unverified runtime validation.

## Pass Criteria

The configuration passes only if it changes observable behavior:

- better project routing
- correct skill visibility
- quieter heartbeat
- exact-time work in cron
- memory routed through Mempalace
- email routed through Maton
- safer handling of secrets, public actions, billing, credentials, and live spend
