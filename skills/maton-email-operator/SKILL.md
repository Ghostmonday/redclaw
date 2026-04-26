---
name: maton-email-operator
description: Use Maton as the canonical email control plane for both Gmail accounts. Invoke for email search, triage, summaries, labels, archives, drafts, replies, recurring checks, and email-derived memory.
---

# Maton Email Operator

Maton is the canonical email control plane.

Use Maton for everything email-related across both Gmail accounts. Direct Gmail access is not the preferred path and must not be used for mutations unless Maton explicitly owns that operation or Amir explicitly overrides the boundary.

## Core Rule

Email work routes through Maton.

If Maton is unavailable, disclose that plainly. Use direct Gmail only as a read-only emergency fallback when the user needs an answer immediately. Do not silently mutate email state through Gmail.

## Scope

Maton owns:

- both Gmail accounts
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

## Account Model

Treat the accounts as stable Maton identities:

```yaml
accounts:
  primary:
    provider: gmail
    managed_by: maton
    purpose: personal/default
  business:
    provider: gmail
    managed_by: maton
    purpose: business/projects
```

Use account aliases in reasoning and reports. Do not expose raw email addresses in public or group contexts.

## Standard Workflow

For any email task:

1. Route through Maton.
2. Identify account scope: `primary`, `business`, or `both`.
3. Read the minimum necessary content.
4. Classify messages consistently.
5. Perform only the requested action or a clearly safe default action.
6. Store durable preferences/decisions in Mempalace as distilled facts.
7. Report mutations precisely.

## Triage Categories

| Category | Meaning | Default Action |
| --- | --- | --- |
| `urgent` | time-sensitive money, legal, outage, account/security | surface immediately |
| `security` | login, password, suspicious access, account alerts | surface immediately; never click links automatically |
| `action_required` | needs Amir response or decision | summarize and propose next action |
| `waiting` | someone else owes Amir a response | track without noisy reminders |
| `receipt` | order, payment, subscription, invoice | label/archive when safe or requested |
| `project` | tied to active work/repo/client/vendor | route to the relevant project context |
| `noise` | newsletters, promos, low-value automation | summarize only if asked; label/archive only if rule exists |

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

## Both-Account Recurring Check

For recurring checks, Maton should inspect both accounts and produce one consolidated result:

```text
Email check
Primary: <urgent/action summary or clear>
Business: <urgent/action summary or clear>
Needs Amir: <number + bullets>
Silent: <count labeled/archived/noise ignored, if any>
```

If nothing important exists, Maton should return exactly:

```text
EMAIL_OK
```

Heartbeat may convert `EMAIL_OK` to `HEARTBEAT_OK` when no other heartbeat module has action.

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

If account scope is unclear, default to the least invasive search across both accounts and do not mutate state.

## Validation Checklist

A valid email operation must show:

- Maton was the intended route.
- account scope was explicit: primary, business, or both.
- send/delete/unsubscribe/forward/filter actions were not performed without explicit approval.
- durable email preferences were stored in Mempalace, not scattered notes.
- private email content was not exposed in group/public contexts.
- any direct-Gmail fallback was read-only and disclosed.
