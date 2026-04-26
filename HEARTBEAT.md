# HEARTBEAT.md — RedClaw Heartbeat Router

Heartbeat is for soft periodic awareness. Cron owns exact-time jobs and heavyweight pipeline runs.

On a quiet cycle, reply exactly:

```text
HEARTBEAT_OK
```

Do not narrate unchanged state.

## Run Order

1. Check ParkingBreaker ad-ops delta only if the delta file exists.
2. Check Maton email summary only if the Maton cron/state indicates new actionable mail.
3. Check Mempalace memory maintenance only if scheduled/due.
4. Run at most one rotated sanity check.
5. If nothing is new or actionable, return `HEARTBEAT_OK`.

## ParkingBreaker Delta Check

Read the machine-generated delta before raw telemetry:

```text
~/h/code/FIGHTCITYTICKETS-1/memory/ad-ops/latest.delta.json
```

If that path is unavailable, try the canonical app path configured for FightCityTickets. Do not scan raw telemetry unless the delta is missing or explicitly says `needs_investigation: true`.

Use workspace state:

```text
memory/heartbeat-state.json
```

Rules:

1. Compare `delta.snapshot_hash` to `state.adOps.lastSnapshotHash`.
2. If unchanged, no `actions_pending`, and no `needs_investigation`, return `HEARTBEAT_OK` unless another module has action.
3. For each `actions_pending` row:
   - Respect `adOps.cooldownsSeconds.perCityAction`.
   - Key dedupe by `city_id:recommendation`.
   - Bypass cooldown only when `notify_priority == "P0"`.
   - If `blocked_reason` exists, surface the blocker and do not propose spend changes.
   - If `approval_required` and no blocker exists, surface the approval request without executing it.
4. Update heartbeat state only after a real alert or acknowledged new snapshot.

## Budget Dry Run

Budget dry-run is allowed only when:

- the delta requests review, or
- `state.adOps.lastBudgetDryRunAt` is older than `adOps.cooldownsSeconds.budgetDryRun`.

Command:

```bash
python3 ~/.openclaw/skills/parkingbreaker-ops/scripts/budget_executor.py
```

Never use `--execute` from heartbeat. Live spend mutation requires explicit human approval outside heartbeat.

## Maton Email Check

Maton owns both Gmail accounts.

Heartbeat may surface a Maton-produced summary, but it must not directly mutate Gmail state.

Expected quiet result from Maton:

```text
EMAIL_OK
```

If Maton returns `EMAIL_OK` and no other module has action, reply `HEARTBEAT_OK`.

Surface only:

- urgent/security mail
- action-required mail
- time-sensitive account/billing/legal/project mail
- failed Maton sync or auth errors

Do not surface newsletters, promos, receipts, or unchanged waiting items unless specifically requested.

## Mempalace Memory Check

Mempalace owns durable memory.

Heartbeat may trigger or report memory maintenance only when scheduled/due. Do not rewrite `MEMORY.md` from heartbeat unless the configured Mempalace workflow explicitly calls for a local mirror update.

Surface only:

- Mempalace unavailable when memory is required
- failed sync/consolidation
- conflicting durable memory that needs Amir's decision

## Rotated Sanity Checks

Increment `rotation.runCounter` in `memory/heartbeat-state.json` after each heartbeat attempt.

Run at most one secondary check per cycle:

- `runCounter % 3 == 0` → Railway health:

  ```bash
  curl -s https://fightcitytickets-production.up.railway.app/health
  ```

  Record result in `lastChecks.railway`.

- `runCounter % 6 == 0` → pytest only if the FightCityTickets repo is dirty or `HEAD` changed since `rotation.lastPytestSha`:

  ```bash
  python3 -m pytest backend/tests/ -q --tb=short
  ```

  Run from the canonical FightCityTickets app path.

Otherwise skip secondary checks.

## Escalation Rules

Notify immediately for:

- ParkingBreaker `notify_priority == "P0"`
- Railway health failure
- Maton auth/sync failure
- urgent/security email
- Mempalace unavailable when durable memory is required
- repeated pipeline failure

Do not re-alert the same non-P0 item inside its cooldown window.

## State Contract

Use this state shape:

```json
{
  "schemaVersion": 1,
  "lastChecks": {
    "railway": null,
    "git": null,
    "parkingbreaker": null,
    "pytest": null,
    "maton": null,
    "mempalace": null
  },
  "rotation": {
    "runCounter": 0,
    "lastPytestSha": null
  },
  "adOps": {
    "lastSnapshotHash": null,
    "lastDeltaSeenAt": null,
    "lastBudgetDryRunAt": null,
    "lastAlertedCityAction": {},
    "cooldownsSeconds": {
      "perCityAction": 7200,
      "escalationP0": 0,
      "budgetDryRun": 14400
    }
  },
  "email": {
    "lastMatonCheckAt": null,
    "lastActionHash": null
  },
  "memory": {
    "lastMempalaceCheckAt": null,
    "lastConflictHash": null
  }
}
```

## Final Rule

Heartbeat should make RedClaw quietly useful. If there is no new action, no alert, and no failure, say only `HEARTBEAT_OK`.
