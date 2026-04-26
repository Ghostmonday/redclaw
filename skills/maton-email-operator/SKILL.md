---
name: maton-email-operator
description: Enforce Maton as the canonical email management interface for both Gmail accounts. Use this skill whenever reading, triaging, drafting, labeling, archiving, replying to, or summarizing email.
---

# Maton Email Operator

Maton is the email control plane.

RedClaw should manage Amir's email through Maton for everything: both Gmail accounts, triage, labels, drafts, replies, summaries, and recurring checks.

## Core Rule

Use Maton for email operations.

Direct Gmail tool usage is not the preferred path. Direct Gmail may only be used as an emergency read-only fallback when Maton is unavailable and the user explicitly needs an answer now.

## Scope

Maton should manage:

- both Gmail accounts
- inbox triage
- unread summaries
- important/urgent detection
- labels and archive rules
- draft creation
- reply preparation
- thread summaries
- attachment awareness
- recurring email checks through heartbeat/cron
- email-derived memory distilled into Mempalace

## Account Model

Configure both Gmail accounts as separate Maton identities.

Use stable aliases rather than raw account names in agent reasoning:

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

Do not expose email addresses in public/group contexts.

## Email Workflow

For any email task:

1. Route through Maton.
2. Identify account scope: `primary`, `business`, or `both`.
3. Search/read the minimum necessary email content.
4. Classify messages.
5. Take only the requested action or a safe default action.
6. Store durable preferences or decisions in Mempalace, not raw email bodies.

## Triage Categories

Use these categories consistently:

| Category | Meaning | Default Action |
| --- | --- | --- |
| urgent | time-sensitive, money, legal, outage, account/security | surface immediately |
| action_required | needs Amir response/decision | summarize and propose next action |
| waiting | someone else owes Amir response | track, do not nag too often |
| receipt | order/payment/subscription records | label/archive when safe |
| noise | newsletters, promos, automated low-value mail | summarize only if asked; label/archive if rule exists |
| security | login, password, suspicious access | surface immediately; never click links automatically |

## Write/Send Boundary

Maton may create drafts freely when asked.

Maton must not send emails unless Amir explicitly says to send.

Maton must not unsubscribe, click links, change account settings, or modify filters unless explicitly instructed.

## Labeling and Archive Defaults

Safe without extra confirmation when clearly requested:

- create labels
- apply labels
- archive non-urgent messages after labeling
- mark obvious low-risk notifications as read if the instruction includes cleanup

Not safe without explicit instruction:

- delete emails
- report spam
- unsubscribe
- send replies
- forward private email
- change filters globally

## Both-Account Checks

For recurring checks, Maton should inspect both accounts and produce one consolidated report:

```text
Email check
Primary: <urgent/action summary or clear>
Business: <urgent/action summary or clear>
Needs Amir: <number + bullets>
Silent: <count archived/labeled/noise if any>
```

If nothing important exists, return exactly:

```text
EMAIL_OK
```

Heartbeat may translate `EMAIL_OK` into `HEARTBEAT_OK` when no other heartbeat modules need attention.

## Mempalace Integration

Use Mempalace for durable email-derived memory:

- preferred senders
- recurring obligations
- account routing rules
- project/vendor relationships
- label policy decisions

Never store raw email bodies in Mempalace unless explicitly requested.

## Failure Behavior

If Maton is unavailable:

```text
Maton unavailable. I will not mutate email state. I can use read-only fallback only if needed and will say exactly what was not done.
```

Do not silently fall back to direct Gmail mutation.

## Validation Checklist

A valid email operation must show:

- Maton was the intended route.
- account scope was explicit: primary, business, or both.
- send/delete/unsubscribe actions were not performed without explicit approval.
- durable email preferences were stored in Mempalace, not scattered notes.
- private email content was not exposed in group/public contexts.
