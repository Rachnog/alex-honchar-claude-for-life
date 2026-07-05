---
name: gtd-email-triage
description: Triage and classify emails across ALL connected email accounts using GTD principles. Classifies into actionable vs non-actionable, auto-archives noise via Gmail API. Trigger on: "process my email", "triage inbox", "check my emails", "email summary", "inbox zero", "GTD", "getting things done", "what needs my attention", "email review", or any question about classifying incoming communications.
compatibility:
  - tool: mcp__google-workspace__manage_email
  - tool: mcp__google-workspace__manage_accounts
  - tool: mcp__google-workspace__queue_operations
---

# Email Triage v3.0 — Token-Optimized GTD Pipeline

Triage unread inbox emails across **all connected accounts**. Classify using deterministic rules first, Haiku sub-agents for ambiguous emails only, then auto-archive noise via Gmail API.

> **TOKEN EFFICIENCY — Tool Selection:**
> - Use `mcp__google-workspace__manage_email(operation: "search")` as the PRIMARY fetch tool — returns clean metadata (sender, subject, date, snippet)
> - Use `manage_email(operation: "triage")` only for quick counts — it caps at ~20 results, not suitable for full triage
> - Reserve `manage_email(operation: "read")` for Phase 2 body reads only
> - Use `mcp__google-workspace__queue_operations` to batch archive operations (up to 10 per call)

## Rule Files

Load these from `plugins/work/skills/gtd-email-triage/` before processing:
- **`sender-rules.json`** — deterministic sender-based classification (by exact sender, domain, or display-name substring)
- **`subject-patterns.json`** — regex patterns for auto-keep (invoices, confirmations) and auto-skip (spam markers, tool noise)

## Phase 1: Fetch + Deterministic Triage (Main Agent)

1. **Load rule files** — read `sender-rules.json` and `subject-patterns.json`
2. **Discover accounts** — call `mcp__google-workspace__manage_accounts(operation: "list")` to get all connected accounts.
3. **Fetch ALL emails per account (mandatory pagination)** — for each account:
   - Call `mcp__google-workspace__manage_email(operation: "search", email: "<account>", query: "in:inbox is:unread", maxResults: 50)`
   - If the batch returns exactly 50 results, **more emails exist** — paginate:
     - Take the date of the oldest email in the batch (e.g. `Mar 28`)
     - Call again with `query: "in:inbox is:unread before:YYYY/MM/DD"` using that date
     - Repeat until a batch returns fewer than 50 results
   - Deduplicate by messageId and merge all batches
   - **Never stop at 50** — always paginate to completion
   This returns sender, subject, date, and snippet inline — **no per-message reads needed**.
   Run the first call per account in parallel; pagination calls are sequential per account.
4. **Report totals** to the user. Warn if any count is suspiciously round (100, 200).
5. **Classify each email** by applying rules in this priority order:

   **Priority 1 — Subject KEEP patterns** (from `subject-patterns.json` `keep_patterns`). These override ALL other rules. Invoices and booking confirmations are always kept regardless of sender.

   **Priority 2 — Subject OR Snippet SKIP patterns** (from `subject-patterns.json` `skip_patterns`). Apply each regex against both the subject AND the snippet returned by the search results. Spam markers like `iOJDH1` are often embedded in the body (not the subject) — a snippet match is sufficient to SKIP. Ashby job applications, Productive time reminders. If a pattern has `sender_contains`, both must match.

   **Priority 3 — Sender exact match** (`sender-rules.json` → `by_sender`)

   **Priority 4 — Sender domain match** (`sender-rules.json` → `by_domain`)

   **Priority 5 — Sender name contains** (`sender-rules.json` → `by_name_contains`). Case-insensitive substring match on the sender display name.

   **Priority 6 — General heuristics** (no rule matched):
   - Phishing: sender domain ≠ claimed service, redirect chains, bulk sender impersonating trusted service → flag to user
   - Cold sales to Neurons Lab → ARCHIVE. Add sender domain to your PRIVATE local copy of `sender-rules.json` immediately — never commit real sender data to a publicly published copy of this file.
   - Fake-Re: cold sales: subject starts with "Re:" but sender is not in contacts/NL/known domain → read snippet; if body is a product pitch or ends with "should I stop following up?" → ARCHIVE cold-sales, add domain to `sender-rules.json`
   - HubSpot/system admin notifications where the added user IS Alex himself → ARCHIVE (not a security event)
   - NL internal threads (CC'd, other NL staff present) → RELEVANT unless user is directly asked to act
   - Multi-party external client threads where an NL account manager (any known NL delivery/account staff member) is present and managing the relationship, and Alex has no direct question or request → ARCHIVE (NL staff is handling it). This applies even when Alex is in the To: field — if NL delivery/account staff are the primary actors, it's not actionable for Alex.
   - Unknown newsletters → RELEVANT (default: keep newsletters, archive software notifications)
   - Restaurants/cafes → ARCHIVE (unless booking confirmation caught by Priority 1)

   **Priority 7 — AMBIGUOUS** — needs body read. Mark for Phase 2.

6. **If zero ambiguous** — skip Phase 2, go directly to report + Phase 3.

## Phase 2: Body Read + Classify (Haiku Sub-Agents) — only if ambiguous emails exist

1. Create `/tmp/claude-email-triage/` (wipe if exists)
2. Batch ambiguous emails into groups of **30**
3. Launch parallel sub-agents using the **Agent tool** with `model: "haiku"`. Each sub-agent gets:
   - The list of message IDs with subjects and senders, plus the account email address for the batch
   - Instruction to read `plugins/work/skills/gtd-email-triage/sub-agent-prompt.md`
   - Instruction to use `mcp__google-workspace__manage_email(operation: "read", email: "<account>", messageId: "<id>")` to read each email body
   - Output file path: `/tmp/claude-email-triage/batch-N.json`
4. After all sub-agents complete, read result files and merge with Phase 1 classifications
5. **Update sender-rules.json** — append newly discovered automated/system senders (never cache human senders). If this skill lives in a git repo that is or may become public, keep the real rules in a private local overlay instead — committed sender rules leak your inbox contents over time.
6. Clean up `/tmp/claude-email-triage/`

## Phase 3: Auto-Archive via API

**Skip if no emails were classified as ARCHIVE, ARCHIVE_UNSUB, or SKIP.**

1. **Group archive targets by account** — collect all messageIds classified as ARCHIVE, ARCHIVE_UNSUB, or SKIP, grouped by their account email.
2. **Batch archive via queue_operations** — for each account, use `mcp__google-workspace__queue_operations` to batch up to 10 modify operations per call:
   ```
   mcp__google-workspace__queue_operations(operations: [
     { tool: "manage_email", args: { operation: "modify", email: "<account>", messageId: "<id1>", removeLabelIds: "INBOX,UNREAD" } },
     { tool: "manage_email", args: { operation: "modify", email: "<account>", messageId: "<id2>", removeLabelIds: "INBOX,UNREAD" } },
     ...up to 10 per call
   ], onError: "continue")
   ```
   If more than 10 emails need archiving for an account, make multiple `queue_operations` calls.
3. **For ARCHIVE_UNSUB senders** (expert networks like GLG, AlphaSights, Guidepoint, Third Bridge): archive programmatically as above, then note them in the report for manual unsubscribe.

Report archived counts per account.

## Output Format

Write the triage report to `100 Periodics/Weekly/[current week folder]/[date]-email-triage.md`:

```markdown
## Inbox Triage — [date]

### Top Priorities (≤5)
1. [sender] — [subject] — [why urgent]

### [account] — Actionable (X)
#### Urgent
- [sender] — [subject] — [why]
#### Deferred
- [sender] — [subject] — [what needs doing]

### [account] — Relevant (X)
- [sender] — [subject]

### [account] — Discovery (X)
- [sender] — [subject] — [why interesting]

### Archived (X emails)
Auto-archived via API: [account-1] (Y), [account-2] (Z)

### Unsubscribed
- [sender] — unsubscribed and archived

### Stats
Total: N | Cached: X% | Body-read: Y | Haiku sub-agents: Z | Errors: W
```

## Notion Task Creation

For actionable emails that require follow-up, apply the **GTD 2-minute rule**:

### > 2 minutes → Dedicated Notion task
For actions requiring research, document review, writing a proposal, or multi-step work, create a dedicated task in the personal Tasks database (use your own Notion Tasks data_source_id):
- **Task name:** Short imperative summary
- **Status:** `Backlog`
- **Priority:** `High` for URGENT, `Medium` for DEFERRED
- **Task type:** `Low / Operational` for approvals/reviews; `Average / Professional` for decisions/analysis
- **Content:** Source email, sender, what needs doing, relevant links

### < 2 minutes → Daily Review aggregator task
For quick approvals, brief replies, minor decisions, or awareness items (e.g., "approve time entries", "submit Ashby feedback", "check hiring pipeline"), add to the existing **"Daily Review — [YYYY-MM-DD]"** task:
1. Search the Tasks database for an existing "Daily Review — [today]" task first
2. If it exists: append the item via `notion-update-page` (update_content)
3. If it doesn't exist: create it with `Status: Backlog`, `Priority: Medium`, `Task type: Low / Operational`
4. Format each entry as: `- [Email / Source] — [one-line summary]`

**Default to Daily Review** for most email-triggered action items — standalone tasks are only for genuinely complex, multi-step work.

**After creating any Notion task (standalone or Daily Review entry), always archive the source email immediately** — remove INBOX,UNREAD labels via `manage_email(operation: "modify")`.

## Tone

Executive assistant. Crisp, organized, surface only what matters.

## Safety

- Flag phishing emails explicitly — never bury them
- Apply NL business filter: buy/invest FROM = surface, sell TO = archive
- Default to ACTIONABLE > DEFERRED when uncertain
- When explicitly instructed to reply to an email: send the reply, then immediately archive the entire thread by searching for all messages with the same subject/thread and removing INBOX,UNREAD labels — the reply itself can resurface the thread in the inbox
- During triage: never reply, forward, or send emails unprompted — only read, classify, and archive
- **GLOBAL RULE: Never send any message to any real person without explicit user confirmation.** Even when instructed to reply, always show the draft first and wait for explicit approval ("yes" / "send it" / "go ahead") before executing. No exceptions.
