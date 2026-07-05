---
name: gtd-slack-triage
description: >
  Triage unread Slack messages across all channel types using GTD principles.
  Classifies into actionable vs non-actionable, auto-marks noise as read.
  Trigger on: "process my Slack", "triage Slack", "check Slack", "Slack summary",
  "Slack inbox zero", "what needs my attention on Slack", "Slack review",
  "unread Slack messages", "check unread messages in slack", "slack triage",
  or any question about classifying incoming Slack communications.
compatibility:
  - tool: mcp__slack-neurons-lab__conversations_unreads
  - tool: mcp__slack-neurons-lab__conversations_replies
  - tool: mcp__slack-neurons-lab__conversations_mark
  - tool: mcp__slack-neurons-lab__conversations_history
  - tool: mcp__slack-neurons-lab__channels_list
  - tool: mcp__slack-neurons-lab__users_search
---

# Slack Triage v1.0 — Token-Optimized GTD Pipeline

Triage unread Slack messages across **all channel types** (DMs, group DMs, partner channels, internal channels). Classify using deterministic rules first, Haiku sub-agents for thread context only when needed, then auto-mark noise as read via API.

> **TOKEN EFFICIENCY — Key Advantage Over Email:**
> `conversations_unreads` returns message text inline — no separate metadata/body fetch needed.
> The main token cost is thread reads (`conversations_replies`) for ambiguous messages.
> Design target: classify 80%+ of messages deterministically in Phase 1 with zero sub-agent calls.

## Rule Files

Load these from `plugins/work/skills/gtd-slack-triage/` before processing:
- **`channel-rules.json`** — deterministic channel-based, bot-based, and user-based classification rules
- **`message-patterns.json`** — regex patterns for auto-keep (escalations, blockers) and auto-skip (bot noise, standup prompts)

## Phase 1: Fetch + Deterministic Triage (Main Agent)

1. **Load rule files** — read `channel-rules.json` and `message-patterns.json`

2. **Fetch unreads by priority tier** — call `conversations_unreads` four times in parallel:
   ```
   conversations_unreads(channel_types: "dm", include_messages: true, max_channels: 50, max_messages_per_channel: 20)
   conversations_unreads(channel_types: "group_dm", include_messages: true, max_channels: 50, max_messages_per_channel: 10)
   conversations_unreads(channel_types: "partner", include_messages: true, max_channels: 50, max_messages_per_channel: 10)
   conversations_unreads(channel_types: "internal", include_messages: true, max_channels: 50, max_messages_per_channel: 10)
   ```
   Note: `include_muted: false` is the default — muted channels are automatically excluded.

3. **Report totals** to the user: X DMs, Y group DMs, Z partner channels, W internal channels.

4. **Classify each message** by applying rules in this priority order:

   **Priority 1 — Message KEEP patterns** (from `message-patterns.json` `keep_patterns`).
   These override ALL other rules. Escalation keywords, blocker mentions, direct requests to Alex. If a pattern has `channel_prefix` or `bot_name`, all conditions must match.

   **Priority 2 — Message SKIP patterns** (from `message-patterns.json` `skip_patterns`).
   Bot noise patterns, standup prompts, automated reminders. If a pattern has `bot_name` or `channel_prefix`, all conditions must match.

   **Priority 3 — Channel-type priority** (inherent in fetch order):
   - DMs from humans → default ACTIONABLE_DEFERRED (someone reached out personally)
   - @mentions in any channel → default ACTIONABLE_DEFERRED (explicitly called out)
   - Group DMs → default ACTIONABLE_DEFERRED (Alex was included for a reason)
   - **Active thread participant:** if Alex sent a message in a group DM/thread AND there are unread replies after Alex's last message, classify as ACTIONABLE_DEFERRED — BUT first check whether the reply is just agreement/sign-off (e.g., "I agree", "yes", "sounds good", "+1", "agreed") with no follow-up question or new ask. If so, treat as SPAM (mark as read, no task) — the thread is resolved. Only create a Notion task if the reply contains an open question, new information requiring action, or disagreement.

   **Priority 4 — Channel prefix rules** (`channel-rules.json` → `by_channel_prefix`).
   Match channel name against prefix patterns. Each prefix has a `default_action` for regular messages and an `escalation_action` triggered when the message also matches a keep_pattern. Example: a routine update in `#client-acme` → RELEVANT, but a message in `#client-acme` containing "client is unhappy" → ACTIONABLE_URGENT.

   **Priority 5 — Channel exact rules** (`channel-rules.json` → `by_channel_exact`).
   Exact channel name match (without `#`). Single `action`.

   **Priority 6 — Bot name rules** (`channel-rules.json` → `by_bot`).
   Exact bot display name match. Check the `BotName` field from the unreads CSV output.

   **Priority 7 — User rules** (`channel-rules.json` → `by_user`).
   Specific users whose messages always need priority treatment. Starts empty — populated iteratively based on triage feedback.

   **Priority 8 — General heuristics** (no rule matched):
   - Thread where Alex is tagged by name or user ID → ACTIONABLE_DEFERRED
   - Client-facing channel (`client-*`, `partner-*`) + message from external person → RELEVANT
   - Internal channel FYI update with no @mention → RELEVANT
   - Bot message in non-critical channel → SPAM
   - Channel with no prefix match and no @mention → RELEVANT (conservative default)
   - NL business filter: someone asking NL to do work / client request = ACTIONABLE, internal team coordination where others are handling it = RELEVANT

   **Priority 9 — AMBIGUOUS** — needs thread context. Mark for Phase 2.
   Trigger: standalone message that might be part of an ongoing conversation requiring Alex's input, or a terse message in a critical channel where context is needed to determine if Alex needs to act.

5. **If zero ambiguous** — skip Phase 2, go directly to report + Phase 3.

## Phase 2: Thread Context Read + Classify (Haiku Sub-Agents) — only if ambiguous messages exist

1. Create `/tmp/claude-slack-triage/` (wipe if exists)
2. Batch ambiguous messages into groups of **20** (smaller than email batches — thread reads return more tokens per thread)
3. Launch parallel sub-agents using the **Agent tool** with `model: "haiku"`. Each sub-agent gets:
   - The list of channel_id + thread_ts pairs with the standalone message text and channel name
   - Instruction to read `plugins/work/skills/gtd-slack-triage/sub-agent-prompt.md`
   - Instruction to use `mcp__slack-neurons-lab__conversations_replies(channel_id, thread_ts)` to read thread context
   - Output file path: `/tmp/claude-slack-triage/batch-N.json`
4. After all sub-agents complete, read result files and merge with Phase 1 classifications
5. **Update channel-rules.json** — append newly discovered bots or automated message sources (never cache human users without explicit instruction). Present suggested additions to the user before writing. If this skill lives in a git repo that is or may become public, write real bot/channel names only to a private local overlay — committed rules leak your workspace structure over time.
6. Clean up `/tmp/claude-slack-triage/`

## Phase 3: Mark as Read via API

**Skip if no messages were classified as SPAM.**

For each channel that has ALL messages classified as SPAM:
1. Call `mcp__slack-neurons-lab__conversations_mark(channel_id: "...", ts: "[latest_message_ts]")` to mark the channel as read up to the latest message.

For channels with a MIX of SPAM and non-SPAM messages:
- Do NOT mark as read — the user needs to see the non-SPAM messages in Slack's native UI.
- Note these in the report as "partially triaged."

**Safety rules:**
- **Never mark DMs as read automatically** — even if classified as noise, DMs carry social expectation of acknowledgment. **Exception:** pure acknowledgment DMs (reason contains "dm-acknowledgment") MAY be auto-marked as read — these are standalone thank-you messages with no question or request. Do not surface them in the RELEVANT section; place them in a "No Action DMs" subsection or omit entirely.
- Never mark channels with ANY actionable message as read
- Only mark channels where 100% of unread messages are SPAM
- On first invocations, list which channels WOULD be marked as read and ask for confirmation before executing. Once the user confirms the pattern is correct, proceed automatically in future runs.

Report marked-as-read counts by channel type.

## Notion Task Creation

Apply the **GTD 2-minute rule** to every message that contains a **direct @Alex mention with any question or request** — regardless of whether the channel classification is ACTIONABLE or RELEVANT. An @Alex + "?" or "would you mind" or "could you" in ANY channel always triggers task/Daily Review creation, even if the channel default is RELEVANT or SPAM:

### > 2 minutes → Dedicated Notion task
If completing the action would take more than ~2 minutes (e.g., testing a demo, reviewing a document, writing a proposal, doing research), create a dedicated task in the personal Tasks database (use your own Notion Tasks data_source_id):

- **Task name:** Short imperative summary + channel context (e.g., "Review demo — test 5-10 min (Acme)")
- **Status:** `Backlog`
- **Priority:** `High` for URGENT, `Medium` for DEFERRED
- **Task type:** `Low / Operational` for review/test tasks; `Average / Professional` for decisions/analysis
- **Content:** Source channel, who sent it, what they asked, all relevant links/URLs

### < 2 minutes → Daily Review aggregator task
If the action is a quick decision, a minor approval, a brief reply, or awareness input (e.g., "did X say Y?", "are you ok with Z?", "heads up on..."), add it to a single **"Daily Review — [YYYY-MM-DD]"** Notion task for the day:

1. Search the Tasks database for an existing "Daily Review — [today]" task first
2. If it exists: append the item to its content via `notion-update-page`
3. If it doesn't exist: create it with `Status: Backlog`, `Priority: Medium`, `Task type: Low / Operational`
4. Format each entry inside the Daily Review as: `- [Channel/DM] @Person — [one-line summary] — [link if any]`

Do NOT create tasks for:
- Messages where Alex is only CC'd with no direct request
- Bot messages or automated notifications
- Messages already handled by another workflow (e.g., calendar invites)
- Pure acknowledgment messages (handled by dm-acknowledgment pattern)

**Always include a Slack message link** in every Notion task and every Daily Review entry. Construct the permalink from the data returned by `conversations_unreads`:
- Each message has a `channel_id` and a `ts` (e.g. `1743350400.123456`)
- Permalink format: `https://{your-workspace}.slack.com/archives/{channel_id}/p{ts_without_dot}`
  - Example: channel `C08ABC123`, ts `1743350400.123456` → `https://{your-workspace}.slack.com/archives/C08ABC123/p1743350400123456`
- For thread replies, use the thread's root `ts`, not the reply `ts`
- Include it as a clickable link in the Notion content: `[Open in Slack](https://{your-workspace}.slack.com/archives/...)`

After creating/updating the Notion task, **immediately mark the source channel/DM as read** via `mcp__slack-neurons-lab__conversations_mark` — the item is captured in Notion, notification is no longer needed.

Report in the triage: `[Notion task created: "Task name" → marked as read]` or `[Added to Daily Review → marked as read]`

## Output Format

Write the triage report to `100 Periodics/Weekly/[current week folder]/[date]-slack-triage.md`:

```markdown
## Slack Triage — [date]

### Top Priorities (up to 5)
1. [DM/Channel] [person] — [summary] — [why urgent]

### DMs — Actionable (X)
#### Urgent
- @[person] — [summary] — [why]
#### Deferred
- @[person] — [summary] — [what needs doing]

### Group DMs — Actionable (X)
#### Urgent
- [group name] — [person] — [summary]
#### Deferred
- [group name] — [person] — [summary]

### Channels — Actionable (X)
#### Urgent
- #[channel] — @[person] — [summary] — [why]
#### Deferred
- #[channel] — @[person] — [summary] — [what needs doing]

### Relevant (X)
- #[channel] — [person] — [summary]

### Discovery (X)
- #[channel] — [person] — [summary] — [why interesting]

### Marked as Read (X messages across Y channels)
Auto-marked via API: #channel-1 (N), #channel-2 (M)

### Partially Triaged
- #[channel] — Z noise messages, but K non-noise messages remain unread

### Stats
Total: N | DMs: X | Group DMs: Y | Channels: Z | Deterministic: A% | Thread-read: B | Sub-agents: C | Errors: D
```

## Tone

Executive assistant. Crisp, organized, surface only what the CEO needs to act on.
Group messages by urgency, not by channel — Alex wants to know what to DO, not audit every channel.

## Safety

- Flag any message about security incidents (credential leaks, production outages, data breaches) as URGENT regardless of channel
- Apply CEO business filter: client escalations and delivery blockers always surface, internal team coordination only if Alex is directly needed
- **Someone acting for Alex** (scheduling/booking a call, preparing materials, arranging logistics) with no question or request → SPAM (mark as read, no task). This includes candidate briefings shared ahead of a scheduled call (location, salary, experience bullets, cert status) — they are FYI context, not action items. Exception: if the briefing contains a blocker or explicit question for Alex, treat as ACTIONABLE_DEFERRED.
- Default to ACTIONABLE > DEFERRED when uncertain — better to surface something Alex ignores than miss something important
- **Never send messages, reply to threads, or modify channel membership** — only read, classify, and mark-as-read
- **GLOBAL RULE: Never send any message to any real person without explicit user confirmation.** Even when the user has instructed a reply, always show the draft first and wait for explicit approval ("yes" / "send it" / "go ahead") before calling any send tool. No exceptions.
- DMs from humans are never auto-classified as SPAM — minimum classification is RELEVANT
- @mentions of Alex are always at minimum ACTIONABLE_DEFERRED
- A new/unknown bot defaults to RELEVANT until explicitly added to channel-rules.json as SPAM

## Rule Iteration

After each triage run, if any messages were classified by heuristics (Priority 8) rather than deterministic rules:
1. Identify the most common uncached patterns
2. Suggest additions to `channel-rules.json` or `message-patterns.json`
3. Present suggestions to the user — never auto-modify rules without confirmation
4. Target: >80% deterministic classification rate after 3-5 triage runs
