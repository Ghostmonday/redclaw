# Maton Two-Inbox Triage Playbook

This playbook makes RedClaw reliable for email triage across both managed Gmail inboxes through Maton.

Managed accounts:

- `talkfightciti` — FightCityTickets / ParkingBreaker / civic-ticket business
- `vibezbizz` — business / creator / general operations

Credentials are never committed. Use environment variables from `config/maton.env.example`.

## Reliability Goal

Every newly arrived inbox email should be classified by Maton and either:

- surfaced to Amir because it needs attention, or
- safely categorized as quiet/no-action, or
- prepared as a draft/recommendation without sending.

## Pipeline

```text
Gmail inbox arrival
      ↓
Maton webhook/push if available
      ↓
Maton scheduled sync/poll fallback
      ↓
OpenClaw cron fallback for both inboxes
      ↓
Maton classification + dedupe
      ↓
Mempalace distilled memory write when durable
      ↓
Heartbeat surfaces only actionable summary
```

Heartbeat does not replace the pipeline. Heartbeat only reports Maton output.

## Local Secret Setup

Create a private local env file:

```bash
mkdir -p ~/.openclaw/secrets ~/.openclaw/state
cp config/maton.env.example ~/.openclaw/secrets/maton.env
chmod 600 ~/.openclaw/secrets/maton.env
```

Edit the copied file and insert the real Maton keys locally.

Do not commit `~/.openclaw/secrets/maton.env`.

## OpenClaw Skill Setup

Install or enable the Maton ClawHub skill in the live OpenClaw environment.

Then verify:

```bash
openclaw skills check
```

Expected:

- Maton skill is visible to the email-handling agent.
- `maton-email-operator` workspace skill is visible.
- Mempalace skill is visible for durable memory writes.

## Suggested Cron Fallback

Exact syntax depends on the installed Maton ClawHub skill command. Use this structure after confirming the live command name:

```bash
# Every 5 minutes during active hours; adjust if Maton webhook/push is reliable.
*/5 8-22 * * * . ~/.openclaw/secrets/maton.env && openclaw agent --message "Use Maton to triage new mail for both managed inboxes: talkfightciti and vibezbizz. Return EMAIL_OK if nothing important exists. Store durable email preferences in Mempalace only as distilled facts." >> ~/.openclaw/logs/maton-triage.log 2>&1
```

For lower volume, use every 10 or 15 minutes. For true inbox-arrival reliability, prefer Maton webhook/push and keep cron as a fallback.

## Triage Rules

Surface immediately:

- security/account alerts
- legal/court/city/payment issues
- customer/client leads
- urgent platform/vendor messages
- anything requiring Amir's decision today

Do not surface repeatedly:

- unchanged waiting items
- newsletters
- promos
- ordinary receipts
- already-classified non-urgent automation

Never automatically:

- send replies
- delete mail
- unsubscribe
- report spam
- forward private mail
- click links
- change filters or account settings

## Output Contract

Maton should produce:

```text
Email check
TalkFightCiti: <urgent/action summary or clear>
VibezBizz: <urgent/action summary or clear>
Needs Amir: <number + bullets>
Silent: <count labeled/archived/noise ignored, if any>
```

If nothing important exists:

```text
EMAIL_OK
```

## State / Dedupe

Track state at:

```text
~/.openclaw/state/maton-email-state.json
```

Track latest summary at:

```text
~/.openclaw/state/maton-email-latest.json
```

Dedupe by:

```text
account + message_id + category + recommended_action
```

Do not alert the same non-urgent item more than once per cooldown window.

## Mempalace Writes

Write durable email-derived memory only when it changes future handling:

- sender preference
- account routing rule
- label policy
- vendor/project relationship
- recurring obligation
- explicit reply preference

Never store raw email bodies unless Amir explicitly requests it.

## Validation

After setup:

```bash
openclaw skills check
openclaw cron list
openclaw memory status --deep --agent personal
openclaw system heartbeat last
```

Then test with a manual run:

```bash
. ~/.openclaw/secrets/maton.env
openclaw agent --message "Use Maton to triage both managed inboxes. Do not send, delete, unsubscribe, forward, or click links. Return EMAIL_OK if nothing important exists."
```

Expected:

- both accounts are checked
- no raw keys are printed
- no send/delete/unsubscribe occurs
- important items are surfaced once
- quiet result is exactly `EMAIL_OK`
- durable preferences go to Mempalace as distilled facts
