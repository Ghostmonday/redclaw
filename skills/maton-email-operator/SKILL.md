---
name: maton-email-operator
description: Use Maton as the canonical email control plane for both Gmail inboxes. Invoke for every email search, triage, summary, label, archive, draft, reply preparation, recurring check, and email-derived memory update.
---

# Maton Email Operator

Maton is the canonical email control plane.

Use Maton for every email operation across both managed Gmail inboxes. Direct Gmail access is not the preferred path and must not be used for mutations unless Amir explicitly overrides the boundary.

## Managed Accounts

Treat these as mandatory Maton-managed inboxes:

```yaml
accounts:
  talkfightciti:
    provider: gmail
    managed_by: maton
    purpose: FightCityTickets / ParkingBreaker / civic-ticket business
    secret_env: MATON_TALKFIGHTCITI_API_KEY
  vibezbizz:
    provider: gmail
    managed_by: maton
    purpose: business / creator / general operations
    secret_env: MATON_VIBEZBIZZ_API_KEY
```

Do not commit account API keys, OAuth tokens, refresh tokens, or raw mailbox exports. Store credentials only in the local environment, OpenClaw secret store, Maton auth store, or another approved secret manager.

## Core Rule

Email work routes through Maton.

If Maton is unavailable, disclose that plainly. Use direct Gmail only as a read-only emergency fallback when the user needs an answer immediately. Do not silently mutate email state through Gmail.

## Reliability Requirement

Every newly arrived inbox email should enter the Maton triage loop.

Preferred order:

1. Maton webhook or push notification.
2. Maton scheduled sync / poll.
3. OpenClaw cron fallback that asks Maton to scan both inboxes.
4. Heartbeat only surfaces Maton summaries; heartbeat does not replace the email pipeline.

Triage must be idempotent. The same message should not be repeatedly surfaced after it has been classified unless priority escalates.

## Scope

Maton owns:

- both Gmail inboxes
- inbox triage
- unread and priority summaries
- urgent/security detection
- label recommendations and label application
- archive workflows
- draft creation
- reply preparation
- thread summaries
- attachment awareness
- recurring email checks through cron/heartbeat
- email-derived memory distilled into Mempalace

## Standard Workflow

For any email task:

1. Route through Maton.
2. Identify account scope: `talkfightciti`, `vibezbizz`, or `both`.
3. Read the minimum necessary content.
4. Classify messages consistently.
5. Apply safe labels/archive rules only when configured or requested.
6. Draft replies when helpful; never send without explicit approval.
7. Store durable preferences/decisions in Mempalace as distilled facts.
8. Report mutations precisely.

## Triage Categories

| Category | Meaning | Default Action |
| --- | --- | --- |
| `urgent` | time-sensitive money, legal, outage, account/security | surface immediately |
| `security` | login, password, suspicious access, account alerts | surface immediately; never click links automatically |
| `action_required` | needs Amir response or decision | summarize and propose next action |
| `waiting` | someone else owes Amir a response | track without noisy reminders |
| `receipt` | order, payment, subscription, invoice | label/archive when safe or requested |
| `project` | tied to active work/repo/client/vendor | route to the relevant project context |
| `lead` | customer/client/prospect opportunity | surface with recommended next response |
| `noise` | newsletters, promos, low-value automation | summarize only if asked; label/archive only if rule exists |

## Account-Specific Bias

For `talkfightciti`:

- prioritize legal/court/city/payment/customer/ticket-related mail
- surface inbound customer leads quickly
- route ParkingBreaker/FightCityTickets vendors to project context
- never archive legal/court/account-security mail automatically

For `vibezbizz`:

- prioritize business opportunities, platform/security alerts, invoices, and collaboration messages
- surface creator/business leads quickly
- label obvious receipts/promotions when a rule exists

## Send / Delete / External Boundaries

Allowed when requested:

- search/read email through Maton
- summarize threads
- create drafts
- recommend labels
- apply labels when the instruction clearly asks for cleanup
- archive non-urgent messages after labeling when clearly requested

Requires explicit approval:

- send email
- delete email
- report spam
- unsubscribe
- forward private email
- click links
- change filters or account settings
- grant permissions or connect accounts

Never send just because a draft exists. Drafting and sending are separate actions.

## Recurring Both-Inbox Check

For recurring checks, Maton should inspect both accounts and produce one consolidated result:

```text
Email check
TalkFightCiti: <urgent/action summary or clear>
VibezBizz: <urgent/action summary or clear>
Needs Amir: <number + bullets>
Silent: <count labeled/archived/noise ignored, if any>
```

If nothing important exists, Maton should return exactly:

```text
EMAIL_OK
```

Heartbeat may convert `EMAIL_OK` to `HEARTBEAT_OK` when no other heartbeat module has action.

## Idempotency State

Maton or the local wrapper should track:

```json
{
  "schemaVersion": 1,
  "accounts": {
    "talkfightciti": {
      "lastSyncAt": null,
      "lastHistoryCursor": null,
      "lastActionHash": null
    },
    "vibezbizz": {
      "lastSyncAt": null,
      "lastHistoryCursor": null,
      "lastActionHash": null
    }
  },
  "dedupe": {
    "messageActionHashes": {},
    "cooldownSeconds": 7200
  }
}
```

## Mempalace Integration

Write only distilled email-derived memory to Mempalace:

- preferred senders
- account routing rules
- label policies
- recurring obligations
- vendor/project relationships
- explicit reply preferences

Do not store raw private email bodies unless Amir explicitly requests it.

Required email-derived memory shape:

```json
{
  "type": "email_context",
  "project": "general | redclaw | fightcitytickets | parkingbreaker | fatedfortress",
  "source": "maton",
  "account": "talkfightciti | vibezbizz",
  "confidence": "high | medium | low",
  "summary": "distilled fact without raw private body text",
  "updated_at": "ISO-8601 timestamp"
}
```

## Failure Behavior

If Maton is unavailable:

```text
Maton unavailable. I will not mutate email state. I can use read-only fallback only if needed and will say exactly what was not done.
```

If account scope is unclear, default to the least invasive Maton search across both accounts and do not mutate state.

## Validation Checklist

A valid email operation must show:

- Maton was the intended route.
- account scope was explicit: talkfightciti, vibezbizz, or both.
- send/delete/unsubscribe/forward/filter actions were not performed without explicit approval.
- durable email preferences were stored in Mempalace, not scattered notes.
- private email content was not exposed in group/public contexts.
- any direct-Gmail fallback was read-only and disclosed.
