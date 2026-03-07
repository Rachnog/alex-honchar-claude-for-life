---
name: gtd-email-triage
description: Triage and classify emails across ALL connected email accounts using GTD principles. Read-only — classifies into actionable vs non-actionable and presents a structured summary. Trigger on: "process my email", "triage inbox", "check my emails", "email summary", "inbox zero", "GTD", "getting things done", "what needs my attention", "email review", or any question about classifying incoming communications.
---

# Work — General Management / Getting Things Done

Read and classify inbox emails across **all connected email accounts** (work and personal). This skill is **triage only** — it reads, classifies, and presents a structured summary. It does NOT archive, reply, forward, or take any other action. Actionable items feed into a task manager; non-actionable items feed into a knowledge management system. Separate skills handle those downstream steps.

## MCP Servers

- Google MCP — read/search/list emails across all connected accounts
- Google Calendar — read calendar to check scheduling context (conflicts, availability)

## Core Workflow — 3-Phase Pipeline with Metadata-First Triage

This skill uses a token-efficient pipeline: most emails are classified from subject+sender metadata alone (no body read). Only ambiguous emails get their full body read by sub-agents. The classification framework is written to a temp file once, not duplicated in every sub-agent prompt.

> **CRITICAL — Email Fetching:**
> - Make exactly ONE call: **`gmail_messages_list_all_accounts`** with `query: "in:inbox"` and `max_results: 10000`
> - This single call returns results for every connected account — no need to list accounts first
> - You MUST pass `max_results: 10000` — the default is only 100 per account, which silently truncates results

### Phase 1: Discovery + Metadata Triage (Main Agent)

1. **Fetch ALL inbox emails across every account in a single call:**
   ```
   gmail_messages_list_all_accounts(query: "in:inbox", max_results: 10000)
   ```
   This returns all accounts and all their inbox emails (read and unread). The `max_results: 10000` overrides the default of 100.
   If an account returns an error or times out, report it and continue with others.
2. **Report totals** to the user (e.g. "Found 47 emails in account-1, 12 in account-2")
   - **Truncation check:** If any account's count is a suspiciously round number (100, 200, 500), warn the user that results may be truncated and ask if they want to retry with a date filter (e.g. `in:inbox after:YYYY/MM/DD`) to get remaining emails
3. **Create temp directory** at `/tmp/claude-email-triage/` (wipe it clean if it exists from a prior run)
4. **Load sender cache** — read `plugins/work/skills/gtd-email-triage/sender-cache.json` if it exists. Format:
   ```json
   { "noreply@productive.io": {"classification": "NON-ACTIONABLE", "sub": "NON-APPLICABLE"}, ... }
   ```
   Emails from cached senders get instant classification (no reasoning needed) — apply the cached classification directly. Still list them in metadata-results.json with reason "sender cache".
5. **Metadata-only triage** — for non-cached emails, classify obvious ones from subject + sender WITHOUT reading the body:

   Scan every email's subject and sender. Classify immediately if the signal is clear:

   **Classify as NON-ACTIONABLE > SPAM:**
   - Unsolicited sales, mass marketing, cold outreach from unknown senders
   - Retail promotions and ads from unknown/unsubscribed sources

   **Classify as NON-ACTIONABLE > NON-APPLICABLE (not SPAM — these are tools the user uses):**
   - Productivity/time-tracking tool notifications (e.g. Productive, Rize)
   - Financial service notifications not requiring action (e.g. N26, Wise, PayPal)
   - Social media notifications (e.g. Pinterest, Discord)
   - Auto-assignment CRM notifications (e.g. "You have been made the Contact owner")
   - Receipts, shipping confirmations, order confirmations
   - Automated system alerts, build notifications, uptime monitors

   **Classify as NON-ACTIONABLE > RELEVANT:**
   - Known newsletters the user subscribes to
   - Health/wellness device notifications (e.g. Oura)
   - Course or learning platform emails (e.g. Neural System Mastery)

   **Leave as AMBIGUOUS (needs body read) — do NOT classify from metadata:**
   - Emails from actual people (not automated systems)
   - Unknown senders with non-promotional subjects
   - Subjects suggesting a request, question, or action needed
   - Anything where the classification isn't obvious from subject+sender alone
   - When in doubt, mark as ambiguous — it's better to read the body than to misclassify

6. **Write metadata classification results** to `/tmp/claude-email-triage/metadata-results.json`:
   ```json
   {
     "classified": [
       {
         "account": "user@example.com",
         "message_id": "id1",
         "sender": "noreply@productive.io",
         "subject": "Weekly time report",
         "classification": "NON-ACTIONABLE",
         "sub_classification": "NON-APPLICABLE",
         "reason": "Productive automated notification"
       }
     ],
     "ambiguous": [
       {
         "account": "user@example.com",
         "message_id": "id5",
         "sender": "jane@company.com",
         "subject": "Quick question about the proposal"
       }
     ]
   }
   ```
7. **Copy the classification framework** to the temp directory:
   ```
   cp plugins/work/skills/gtd-email-triage/classification-framework.md /tmp/claude-email-triage/classification-framework.md
   ```
   This is read by each sub-agent, avoiding duplication in the main agent's context.
8. **Report to user:** "Classified X/Y emails from metadata (Z from sender cache). Reading full bodies for W ambiguous emails."
9. **Decide sub-agent splits** for ambiguous emails only:
   - Split ambiguous emails into batches of ~60 per sub-agent
   - Group by account where possible to minimize context switching
   - Record the split plan before launching

### Phase 2: Read + Classify Ambiguous Emails (Sub-Agents, launched in parallel)

**Skip this phase entirely if there are no ambiguous emails.**

Launch sub-agents using the **Agent tool**. Launch all sub-agents in parallel (multiple Agent tool calls in one response).

Each sub-agent receives a **self-contained prompt** (sub-agents do NOT inherit parent context). The prompt MUST include:

1. **The account email address** to use with `gmail_message_get`
2. **The exact list of ambiguous message IDs** to process (with their subjects and senders for context)
3. **Instruction to read the classification framework** from `/tmp/claude-email-triage/classification-framework.md`
4. **The output file path** (e.g. `/tmp/claude-email-triage/batch-1-results.json`)
5. **These explicit instructions for the sub-agent:**

```
You are an email classification agent. Your job:

1. FIRST, read the classification framework from `/tmp/claude-email-triage/classification-framework.md`
2. For each message ID below, call `gmail_message_get` to read the email body, then classify it

When reading emails, focus on the first ~500 words of the email body for classification. Skip long signatures, legal disclaimers, and quoted reply threads — they rarely affect classification.

IMPORTANT: Use first-principles thinking:
- Read the actual email content carefully
- Determine what the email is asking the user to DO (or not do)
- Consider urgency, sender relationship, and context
- The reference examples are patterns, not exhaustive rules — new senders and tools will appear that aren't listed

Write your results to the output file in this JSON format, updating the file every 5-10 emails to avoid data loss:

{
  "total_assigned": <N>,
  "classifications": [
    {
      "account": "<account email>",
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

### Phase 3: Compile + Present (Main Agent)

After all sub-agents complete (or immediately after Phase 1 if no ambiguous emails):

1. **Read all results files** from `/tmp/claude-email-triage/`:
   - `metadata-results.json` — emails classified from metadata in Phase 1
   - `batch-*-results.json` — emails classified by sub-agents in Phase 2
2. **Merge results** — combine the `classified` array from metadata-results.json with all sub-agent classification arrays into a single unified list
3. **Cross-reference against the ambiguous list** — verify every ambiguous message ID appears in sub-agent results; flag any gaps
4. **Aggregate and render the final markdown report** using the Output Format below, grouped by account and classification
5. **Report processing stats** — e.g. "Total: 175/175 processed (100%) — 110 from metadata, 65 from body read" or include error counts if any
6. **Update sender cache** — append any newly classified senders to `plugins/work/skills/gtd-email-triage/sender-cache.json`. Only cache senders that are clearly automated/system senders (not real people). If the user corrects a classification, update the cache entry for that sender.
7. **Clean up** — delete `/tmp/claude-email-triage/` directory and all contents

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
Top examples: (up to 5 listed)
- [sender] — [subject]
(Y more not shown)

#### NON-ACTIONABLE — Non-Applicable (X emails)
Top examples: (up to 5 listed)
- [sender] — [subject]
(Y more not shown)

#### NON-ACTIONABLE — Discovery (X emails)
- [sender] — [subject] — [why it might be interesting]

### [account-2@email.com]
...

### Processing Stats
Total: N/N processed (X%) — M from metadata, K from body read — Y errors (if any)

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
