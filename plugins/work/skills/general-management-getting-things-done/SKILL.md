---
name: general-management-getting-things-done
description: Triage and classify emails across ALL connected email accounts using GTD principles. Read-only — classifies into actionable vs non-actionable and presents a structured summary. Trigger on: "process my email", "triage inbox", "check my emails", "email summary", "inbox zero", "GTD", "getting things done", "what needs my attention", "email review", or any question about classifying incoming communications.
---

# Work — General Management / Getting Things Done

Read and classify emails across **all connected email accounts** (work and personal). This skill is **triage only** — it reads, classifies, and presents a structured summary. It does NOT archive, reply, create events, or take any other action. Actionable items feed into a task manager; non-actionable items feed into a knowledge management system. Separate skills handle those downstream steps.

## MCP Servers

- Google MCP — list accounts, read/search/list emails across all connected accounts
- Google Calendar — read calendar to check scheduling context (conflicts, availability)

## Core Workflow

When the user asks to process emails:

1. **List all connected accounts** using the Google MCP accounts list
2. **Fetch ALL unread emails from every account — exhaustively**
   - Use the Gmail list endpoint for each account with query `is:unread` (or `in:inbox is:unread` depending on user preference)
   - **Do NOT stop at the first page of results.** If the API returns a next page token, keep fetching until all pages are consumed
   - For each account, continue paginating until there are zero remaining pages
   - Report the total count fetched per account before classifying (e.g. "Found 47 unread emails in account-1, 12 in account-2")
   - If an account returns an error or times out, report it and continue with the other accounts
3. **Classify every single email** into the decision tree below — do not skip, sample, or summarize in bulk
4. **Present a complete summary** grouped by classification, with account labels
5. **Stop** — do not execute any actions

## Classification Decision Tree

Every email gets one top-level classification and one sub-classification.

```
Email
├── ACTIONABLE — requires the user to do something
│   ├── URGENT — can/should be done quickly (< 5 min) or is time-sensitive
│   └── DEFERRED — needs thoughtful attention, can be scheduled
│
└── NON-ACTIONABLE — no action required from the user
    ├── RELEVANT — applies to current work projects, interests, or life areas
    └── NON-APPLICABLE — does not match current projects or interests
        ├── SPAM — junk, unsolicited offers, mass marketing
        └── DISCOVERY — potentially interesting as a new topic, trend, or opportunity
```

## Classification Heuristics

### ACTIONABLE > URGENT

- **DocuSign** documents requiring signature (flag phishing risk if sender is unusual)
- **Ashby**: overdue tasks, review requests directed at user
- **Hubspot**: user specifically tagged or assigned a follow-up task
- **AWS conversations** about clients or new leads
- **Meeting requests** that need a timely response (check calendar for conflicts)
- **Loom**: comments requiring user's review
- Any email with a clear deadline within 48 hours

### ACTIONABLE > DEFERRED

- **Ashby**: application reviews (initial apps go to Lika & Putri first; user reviews later)
- **Leapsome**: new goals or goal progress updates
- **Shared Google Docs/Slides/Sheets**: review when convenient
- **Conference invitations** worth considering
- **Education events** (e.g. Beyond Connections) — need calendar alignment with NL calendar
- **Meeting requests via personal email** — need cross-check with Neurons Lab calendar
- **Interns / potential employees** emailing directly
- **Tech software testing** notifications (Kaggle, Eintelligence, similar)

### NON-ACTIONABLE > RELEVANT

- **Newsletters** the user actively reads (maintain a known-newsletters list; ask to confirm new ones)
- **Oura** notifications
- **Neural System Mastery** emails
- Content related to user's current work projects, life areas, or stated interests
- Emails where the user is CC'd for awareness on a relevant topic

### NON-ACTIONABLE > NON-APPLICABLE > SPAM

- **Corporate tool noise**: Productive, Rize, Clay notifications, N26, Wise, PayPal, Pinterest, Discord, Crypto.com, Holstee, Aweber, n8n, Cloudflare, Numerai (round summaries/reminders), Spencer Shubert, Academia, Archive, Sailwiz, Boggi Milano, LV and similar retail
- **Hubspot**: "You have been made the Contact owner" auto-notifications
- **Unsolicited service offerings**: translation, outsourcing, talent hiring, marketing, lead generation
- **Ads / promotional newsletters** in work inbox
- **CC'd emails** with no relevance to user's work or interests

### NON-ACTIONABLE > NON-APPLICABLE > DISCOVERY

- Service offerings that could be a **potential business match**
- Emerging tech, industry trends, or opportunities outside current focus but potentially worth tracking
- Cold outreach that is actually well-targeted and novel

## Generalization Principles

The heuristics above are a starting point. When encountering an email that doesn't match existing rules:

1. **Apply the decision tree top-down**: Is it actionable? If yes, urgent or deferred? If no, relevant or non-applicable?
2. **Infer intent** from sender, subject, content, and which account received it
3. **Ask on first encounter** of a new pattern — "I saw X type of email for the first time, how should I classify these going forward?"
4. **Remember the answer** — update classification heuristics for future runs
5. **Default to ACTIONABLE > DEFERRED** when uncertain — it's safer to surface something than to miss it

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

### New Patterns (X emails)
- [account] — [sender] — [subject] — [suggested classification, awaiting confirmation]
```

## Tone

Executive assistant who knows the boss's preferences. Crisp, organized, no unnecessary detail. Surface only what matters.

## Safety

- This skill is READ-ONLY — never archive, reply, forward, or modify any email
- Never create, update, or delete calendar events
- Flag any email that looks like phishing, especially DocuSign requests from unusual senders
- When in doubt, classify as ACTIONABLE > DEFERRED rather than NON-ACTIONABLE
