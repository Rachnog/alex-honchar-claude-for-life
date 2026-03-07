---
name: gtd-email-triage
description: Triage and classify emails across ALL connected email accounts using GTD principles. Read-only — classifies into actionable vs non-actionable and presents a structured summary. Trigger on: "process my email", "triage inbox", "check my emails", "email summary", "inbox zero", "GTD", "getting things done", "what needs my attention", "email review", or any question about classifying incoming communications.
---

# Work — General Management / Getting Things Done

Read and classify inbox emails across **all connected email accounts** (work and personal). This skill is **triage only** — it reads, classifies, and presents a structured summary. It does NOT archive, reply, create events, or take any other action. Actionable items feed into a task manager; non-actionable items feed into a knowledge management system. Separate skills handle those downstream steps.

## MCP Servers

- Google MCP — read/search/list emails across all connected accounts
- Google Calendar — read calendar to check scheduling context (conflicts, availability)

## Core Workflow — 3-Phase Sub-Agent Pipeline

This skill uses a 3-phase pipeline to read full email bodies without hitting context limits. Sub-agents each get their own context window, read and classify a batch of emails, and write structured results to temp files that the main agent compiles.

> **CRITICAL — Email Fetching:**
> - Make exactly ONE call: **`gmail_messages_list_all_accounts`** with `query: "in:inbox"` and `max_results: 10000`
> - This single call returns results for every connected account — no need to list accounts first
> - You MUST pass `max_results: 10000` — the default is only 100 per account, which silently truncates results

### Phase 1: Discovery (Main Agent)

1. **Fetch ALL inbox emails across every account in a single call:**
   ```
   gmail_messages_list_all_accounts(query: "in:inbox", max_results: 10000)
   ```
   This returns all accounts and all their inbox emails (read and unread). The `max_results: 10000` overrides the default of 100.
   If an account returns an error or times out, report it and continue with others.
2. **Report totals** to the user (e.g. "Found 47 emails in account-1, 12 in account-2")
   - **Truncation check:** If any account's count is a suspiciously round number (100, 200, 500), warn the user that results may be truncated and ask if they want to retry with a date filter (e.g. `in:inbox after:YYYY/MM/DD`) to get remaining emails
3. **Create temp directory** at `/tmp/claude-email-triage/` (wipe it clean if it exists from a prior run)
4. **Write manifest** to `/tmp/claude-email-triage/manifest.json`:
   ```json
   {
     "accounts": [
       {
         "email": "user@example.com",
         "message_ids": ["id1", "id2", ...],
         "subjects": {"id1": "Subject line", ...},
         "senders": {"id1": "sender@example.com", ...}
       }
     ],
     "total_emails": 59,
     "created_at": "2026-03-07T10:00:00Z"
   }
   ```
5. **Decide sub-agent splits:**
   - 1 sub-agent per account by default
   - If any account has >50 emails, split that account into sub-agents of ~40 emails each
   - Record the split plan before launching

### Phase 2: Read + Classify (Sub-Agents, launched in parallel)

Launch sub-agents using the **Agent tool**. Launch all sub-agents in parallel (multiple Agent tool calls in one response).

Each sub-agent receives a **self-contained prompt** (sub-agents do NOT inherit parent context). The prompt MUST include:

1. **The account email address** to use with `gmail_message_get`
2. **The exact list of message IDs** to process
3. **The full classification framework** (copied verbatim from the "Classification Framework" section below — everything between the `---BEGIN CLASSIFICATION CONTEXT---` and `---END CLASSIFICATION CONTEXT---` markers)
4. **The output file path** (e.g. `/tmp/claude-email-triage/user@example.com-results.json`)
5. **These explicit instructions for the sub-agent:**

```
You are an email classification agent. For each message ID below, call `gmail_message_get` to read the full email body, then classify it using the classification framework provided.

IMPORTANT: The framework below gives you a decision tree and reference examples. Use first-principles thinking:
- Read the actual email content carefully
- Determine what the email is asking the user to DO (or not do)
- Consider urgency, sender relationship, and context
- The reference examples are patterns, not exhaustive rules — new senders and tools will appear that aren't listed

Write your results to the output file in this JSON format, updating the file every 5-10 emails to avoid data loss:

{
  "account": "<account email>",
  "total_assigned": <N>,
  "classifications": [
    {
      "message_id": "<id>",
      "sender": "<from address>",
      "subject": "<subject line>",
      "classification": "ACTIONABLE|NON-ACTIONABLE",
      "sub_classification": "URGENT|DEFERRED|RELEVANT|SPAM|DISCOVERY",
      "reason": "<one-line explanation>"
    }
  ],
  "errors": [
    { "message_id": "<id>", "error": "<what went wrong>" }
  ]
}

If a body fetch fails, classify from the subject/sender metadata you were given and include the message in "errors" too.

Process ALL assigned message IDs. Do not skip any. When done, report: "Processed X/Y emails, results in <path>".
```

**Sub-agent prompt template** — the main agent MUST paste the following classification framework into each sub-agent's prompt:

---BEGIN CLASSIFICATION CONTEXT---

#### Classification Decision Tree

Every email gets one top-level classification and one sub-classification. Work through the tree top-down:

1. **Does this email require the user to DO something?** (respond, sign, review, decide, schedule, follow up)
   - YES → ACTIONABLE
     - Is it time-sensitive (deadline within 48h) or quick (< 5 min)? → URGENT
     - Otherwise → DEFERRED
   - NO → NON-ACTIONABLE
     - Is it relevant to the user's current work, projects, or interests? → RELEVANT
     - Otherwise → NON-APPLICABLE
       - Is it junk, mass marketing, or tool noise? → SPAM
       - Could it be interesting as a new opportunity or trend? → DISCOVERY

```
Email
+-- ACTIONABLE -- requires the user to do something
|   +-- URGENT -- quick (< 5 min), time-sensitive, or has a near deadline
|   +-- DEFERRED -- needs thoughtful attention, can be scheduled
|
+-- NON-ACTIONABLE -- no action required from the user
    +-- RELEVANT -- applies to current work, projects, interests, or life areas
    +-- NON-APPLICABLE -- does not match current context
        +-- SPAM -- junk, unsolicited offers, mass marketing, tool noise
        +-- DISCOVERY -- potentially interesting new topic, trend, or opportunity
```

#### First-Principles Classification Guide

Think about each email along these dimensions:

**Is there a required action?**
- Documents requiring signature → ACTIONABLE
- Tasks assigned or overdue in any project management / HR / CRM tool → ACTIONABLE
- Meeting requests needing a response → ACTIONABLE (check calendar for conflicts)
- Review requests (code, documents, applications) → ACTIONABLE
- Direct questions from colleagues, clients, or partners → ACTIONABLE
- Pure notifications, confirmations, receipts → NON-ACTIONABLE

**How urgent is the action?**
- Explicit deadline within 48 hours → URGENT
- Can be completed in under 5 minutes → URGENT
- Needs research, thought, or coordination → DEFERRED
- First pass by someone else before user's turn → DEFERRED

**Is non-actionable content relevant?**
- Relates to a project the user is actively working on → RELEVANT
- From a newsletter or source the user chose to subscribe to → RELEVANT
- User is CC'd on a topic they care about → RELEVANT
- Automated noise from tools the user doesn't actively monitor → SPAM
- Unsolicited sales, marketing, promotions → SPAM
- Well-targeted outreach or emerging trends outside current focus → DISCOVERY

#### Reference Examples (non-exhaustive — use as pattern guides, not hard rules)

These are known patterns from the user's history. New tools, senders, and patterns will appear — classify them from first principles using the guide above.

ACTIONABLE > URGENT (examples):
- DocuSign signature requests (flag phishing if sender is unusual)
- Overdue tasks or direct review requests in HR/recruiting tools (e.g. Ashby)
- CRM follow-ups specifically assigned to the user (e.g. Hubspot)
- Client or lead conversations requiring response (e.g. AWS marketplace)
- Video/async tool comments needing review (e.g. Loom)

ACTIONABLE > DEFERRED (examples):
- Application reviews where others triage first (e.g. Ashby pipeline)
- Goal-setting or performance review notifications (e.g. Leapsome)
- Shared document review requests (Google Docs/Slides/Sheets)
- Conference or education event invitations needing calendar check
- Direct emails from interns, potential employees, or collaborators
- Testing/competition notifications (e.g. Kaggle)

NON-ACTIONABLE > RELEVANT (examples):
- Newsletters the user actively reads
- Health/wellness device notifications (e.g. Oura)
- Course or learning platform emails (e.g. Neural System Mastery)
- CC'd emails on topics matching user's active projects

NON-ACTIONABLE > SPAM (examples):
- Automated notifications from productivity/time-tracking tools the user doesn't actively check (e.g. Productive, Rize)
- Financial service notifications not requiring action (e.g. N26, Wise, PayPal)
- Social media notifications (e.g. Pinterest, Discord)
- Auto-assignment notifications from CRM (e.g. "You have been made the Contact owner")
- Unsolicited service offerings (translation, outsourcing, marketing, lead gen)
- Retail promotions and ads

NON-ACTIONABLE > DISCOVERY (examples):
- Service offerings that could be a genuine business match
- Emerging tech, industry trends, or opportunities outside current focus
- Cold outreach that is well-targeted and novel

---END CLASSIFICATION CONTEXT---

### Phase 3: Compile + Present (Main Agent)

After all sub-agents complete:

1. **Read all results files** from `/tmp/claude-email-triage/`
2. **Cross-reference against manifest** — verify every message ID from the manifest appears in results; flag any gaps
3. **Aggregate and render the final markdown report** using the Output Format below, grouped by account and classification
4. **Report processing stats** — e.g. "Total: 59/59 processed (100%)" or "Total: 57/59 processed (97%) — 2 errors"
5. **Clean up** — delete `/tmp/claude-email-triage/` directory and all contents

## Generalization Principles

The reference examples above are a starting point, not a complete ruleset. When encountering an email that doesn't match known patterns:

1. **Apply the decision tree top-down**: Does it require action? Is it urgent or deferrable? If no action needed, is it relevant?
2. **Infer intent** from sender, subject, body content, and which account received it
3. **Reason about the sender's relationship to the user** — colleague, client, vendor, stranger, automated system
4. **Consider the email's actual ask** — what would the user need to do, if anything?
5. **Ask on first encounter** of a genuinely new pattern — "I saw X type of email for the first time, how should I classify these going forward?"
6. **Remember the answer** — update classification heuristics for future runs
7. **Default to ACTIONABLE > DEFERRED** when uncertain — it's safer to surface something than to miss it

## Output Format

Present results grouped by account and classification:

```
## Inbox Triage — [date]

### [account-1@email.com]

#### ACTIONABLE — Urgent (X emails)
- [sender] — [subject] — [why urgent]

#### ACTIONABLE — Deferred (X emails)
- [sender] — [subject] — [what needs to be done]

#### NON-ACTIONABLE — Relevant (X emails)
- [sender] — [subject] — [which project/interest it relates to]

#### NON-ACTIONABLE — Spam (X emails)
- [sender] — [subject] — [rule applied]

#### NON-ACTIONABLE — Discovery (X emails)
- [sender] — [subject] — [why it might be interesting]

### [account-2@email.com]
...

### Processing Stats
Total: N/N processed (X%) — Y errors (if any)

### New Patterns (X emails)
- [account] — [sender] — [subject] — [suggested classification, awaiting confirmation]
```

## Tone

Executive assistant who knows the boss's preferences. Crisp, organized, no unnecessary detail. Surface only what matters.

## Safety

- This skill is READ-ONLY — never archive, reply, forward, or modify any email
- Never create, update, or delete calendar events
- Flag any email that looks like phishing, especially signature requests from unusual senders
- When in doubt, classify as ACTIONABLE > DEFERRED rather than NON-ACTIONABLE
