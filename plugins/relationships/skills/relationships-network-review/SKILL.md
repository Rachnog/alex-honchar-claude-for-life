---
name: relationships-network-review
description: Run structured weekly, monthly, or quarterly reviews of the PROFESSIONAL network and community — target-network activation, follow-ups owed, new connections, and dormant-but-important contacts — using Clay/Mesh (relationship CRM), Google Calendar, and Granola (BD conversation capture). Scores against the Relationships "Network" target (non-work activities with the target network) and the "build relationships / include more people" strategy principle, and lightly covers the "Community" stage. Trigger on network review, networking review, "who owes a follow-up", "who am I letting go cold", relationship CRM review, BD/pipeline relationship check, or community engagement review. For the partner + family lens (inner circle, personal channels) use `relationships-personal-review` instead.
compatibility:
  - tool: mcp__claude_ai_Clay__searchContacts
  - tool: mcp__claude_ai_Clay__getGroups
  - tool: mcp__claude_ai_Clay__getContact
  - tool: mcp__claude_ai_Clay__getRecentReminders
  - tool: mcp__claude_ai_Clay__getUpcomingReminders
---

# Relationships - Network Review (Network & Community)

Primary entrypoint for reviewing the **professional network and community**: the Relationships stages
"Network" (Orange — grow the target network) and "Community" (Green — outward contribution). This is the
outward lens; the partner + family lens lives in `relationships:relationships-personal-review`. Offer both
when the user asks for "a relationships review" unqualified.

Clay/Mesh is the right source here and its strong suit: it richly ingests LinkedIn, email, calendar,
Facebook, and Instagram, tracks per-contact recency, and holds the follow-up reminders. (Its blind spot —
WhatsApp/calls/Telegram for the inner circle — is the *other* skill's problem, not this one's.)

## Review Types

- weekly review (this ISO week vs last ISO week)
- monthly review (this calendar month vs last)
- quarterly review (multi-month trend; earliest month = baseline)

Use ISO week boundaries for weekly, calendar months for monthly. No rolling "last 7 days".

## Reasoning Order

1. Read `000 OS/2 Simple strategy 2026` — the core relationship-building principle; note any
   self-identified derailers listed there.
2. Check the Network target in `000 OS/3 Numerical Targets 2026`: **"Non-work activities with target
   network"** — read the current baseline and target values from that file. This is the one hard number for the whole Relationships area.
3. Read `300 Areas/5 Relationships/2 - Orange - Network` (Beyond Connections practice; the weekly
   network-activation session) and `3 - Green - Community` (contribution lens).
4. Only then interpret the Clay/Calendar/Granola data.

## Data Sources

- **Clay/Mesh** (`mcp__claude_ai_Clay__*`) — the network CRM. `searchContacts` with date-window filters
  (`last_interaction_date`, `first_interaction_date` for new contacts), `group_ids` for segments;
  `getGroups`; `getRecentReminders` / `getUpcomingReminders` (follow-ups); `getContact` for detail.
- **Google Calendar** (`mcp__claude_ai_Google_Calendar__*`) — network-activation sessions, coffees,
  events, dinners with target-network people (the "non-work activities" that count toward the target).
- **Granola** (`mcp__claude_ai_Granola__*`) — BD / networking conversation capture; count and skim
  meetings with network contacts.
- **WhatsApp group participation** (from the personal review's bundled extractor, metadata only) — the
  community signal. Which local/professional group chats you belong to, and your share of the messages —
  are you present but silent in the communities you want to be part of?

## Data Reality Rules — READ BEFORE EVERY REVIEW

- **Clay interaction COUNTS are lifetime totals, not windowable.** To measure a period, filter by
  `last_interaction_date` / `first_interaction_date` gte/lte — do NOT read the count fields as
  period activity.
- **Clay is professional-biased.** It over-weights LinkedIn/email/calendar contacts and under-weights
  anyone you only reach on WhatsApp/Telegram. Good for the network; do not use it to judge closeness.
- **A calendar "meeting" is not automatically a real connection** — a group webinar ≠ a 1:1 coffee. Weigh
  non-work, small-group activities (the target metric) above bulk meetings.
- **Overdue reminders are the cleanest "dropped relationship" signal** — a follow-up whose date has passed
  with no interaction since = a slipping relationship. Rank these.
- **New connection ≠ relationship.** A first meeting this month is a lead, not yet a maintained tie; track
  first-touch and whether it got a second touch.

## Bucket Taxonomy

Use Clay groups + interaction recency to segment:

| Bucket | Rule | Read |
|---|---|---|
| **Target network — active** | Key groups (e.g. industry peers, target-accounts list, partnerships) with interaction in window | The network you are actually maintaining |
| **Target network — dormant** | Same key groups, no interaction in window (> N days) | The at-risk list — re-warm before they go cold |
| **New connections** | `first_interaction_date` inside the window | Leads; did any get a second touch? |
| **Follow-ups owed** | Reminders past-due with no interaction since | Explicit dropped balls — highest priority |
| **Community** | Community events / speaking / content (meetups, talks) | Green stage — outward contribution, lighter |

## Metrics To Compute (per period, with delta)

1. **Non-work activities with target network** — count coffees/dinners/events/1:1s with target-network
   people from Calendar + Granola; report progress toward the **25** target and the run-rate to hit it.
2. **Network breadth touched** — distinct network contacts with `last_interaction_date` in the window.
3. **Follow-ups owed** — overdue reminders (`getRecentReminders` past-due), named and ranked.
4. **New connections** — count via `first_interaction_date` in window; how many got a second touch.
5. **Dormant-but-important** — contacts in key groups with no interaction in > N days (the re-warm list).
6. **Community activity** — events attended, talks/content shipped, PLUS **WhatsApp community-group
   participation** (your message share in local/interest groups). A community group you sit in at ~0% is
   access without presence — a higher-leverage fix than re-earning a cold CRM group.

## Workflow

1. Set the review + comparison windows.
2. Read the connection principle, the network target, and the Network/Community practice files before concluding.
3. Parallel pull: Clay `getGroups`; `searchContacts` with `last_interaction_date` in window (and in the
   comparison window) and with `first_interaction_date` in window (new contacts); `getRecentReminders`
   (overdue) and `getUpcomingReminders`; Calendar events in window; Granola meetings in window.
4. Segment via groups + recency; compute the metrics and deltas.
5. Score against the network-target run-rate, the connection principle, and the Network/Community cadences.
   Back-reference the prior review's priorities; grade follow-through.
6. Produce the structured review; save the file(s).

## Recommendation Rules

- One to three high-leverage priorities. Prefer named actions ("re-message the 4 overdue FSI follow-ups")
  over vague "network more".
- Tie each to a specific contact/gap and the network target or the connection principle.
- Separate observation / interpretation / assumption. Vault voice: sentences < 25 words; numbers over
  generalities; banned words — delve, leverage, robust, navigate, journey, ecosystem.

## Output Contract

- review scope + comparison windows (+ "Source: Clay CRM + Calendar + Granola; professional network only —
  inner circle is in the personal review").
- a scorecard delta table (network buckets + network-target progress across periods, Trend column for
  multi-month).
- for multi-month trends, open with a narrative headline.
- sections: network-target progress, follow-ups owed (named), new connections, dormant-but-important, community.
- alignment with the network target, the connection principle, and the Network/Community
  cadences.
- top 3 priorities; risks/caveats (Clay counts non-windowable, meeting≠connection); numbered next actions.

Numbers first, then interpretation, then recommendation.

## File Saving

Weekly and monthly reviews always create report files. Do not ask whether to save.

```bash
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"     # monthly / quarterly
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"   # weekly
```

Example paths:
- monthly: `$PERIODICS_ROOT/Monthly/06 June/2026-06-relationships-network-review.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 11/2026-week-11-relationships-network-review.md`

H1 + bold metadata block (Review period / Comparison period / Source / Generated / Related). No YAML
frontmatter on review outputs.

## Resources

Pull the Network practice references from `400 Resources/` (Beyond Connections, Superconnector, Give and
Take) when a recommendation needs backing.

## Tone

Operating review of the network. Numbers first, name the dropped balls, end with concrete re-touches.

## Schema

Reference `../../schemas/relationships-review.json`. Set `lens: "network"`.
