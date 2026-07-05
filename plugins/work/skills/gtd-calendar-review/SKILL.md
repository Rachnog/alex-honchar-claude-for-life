---
name: gtd-calendar-review
description: >
  Analyze calendar events across all Google accounts for any time range — today, this week,
  last week, next week, or custom dates. Categorizes events, calculates meeting load vs targets,
  checks Deep Work Thursday protection, identifies focus blocks, and generates actionable
  recommendations. Supports retrospective analysis, prospective planning, and full weekly review.
  Trigger on: "calendar review", "review my calendar", "time review", "what meetings do I have",
  "how did I spend my time", "meeting load", "zone of genius check", "next week prep",
  "deep work check", "calendar analysis", "check my schedule", "today's calendar",
  "tomorrow's meetings", "weekly review calendar", or any question about calendar-based
  time allocation or upcoming schedule.
compatibility:
  - tool: mcp__google__calendar_events_list_all_accounts
  - tool: mcp__google__calendar_events_list
  - tool: mcp__google__calendar_list
---

# Calendar Review v1.0 — Time Allocation Analysis + Schedule Prep

Analyze calendar events across **all connected Google accounts** for any time range. Categorize events, measure time allocation against targets, identify violations and opportunities, and generate actionable recommendations.

> **TOKEN EFFICIENCY — API Selection:**
> - Use `mcp__google__calendar_events_list_all_accounts` as PRIMARY — one call covers all 3 accounts
> - ALWAYS set tight `timeMin`/`timeMax` — API returns ~13k tokens per response without filtering
> - Never fetch more than 7 days per call — split longer ranges into multiple calls
> - Skip all-day events in calculations (they are labels, not meetings)
> - Single-day queries are cheapest (~2-3k tokens)

## Scope Argument

Parse the user's argument (or lack thereof) into `timeMin` and `timeMax` in **Europe/Madrid timezone**:

| Argument | timeMin | timeMax | Mode |
|----------|---------|---------|------|
| _(none)_ / "today" | Today 00:00 | Today 23:59 | Single-day |
| "tomorrow" | Tomorrow 00:00 | Tomorrow 23:59 | Single-day |
| "this week" | This Monday 00:00 | This Sunday 23:59 | Mixed (past days = retro, future = prospective) |
| "last week" / "past week" | Last Monday 00:00 | Last Sunday 23:59 | Retrospective |
| "next week" | Next Monday 00:00 | Next Sunday 23:59 | Prospective |
| "March 20-25" / custom | Parsed start 00:00 | Parsed end 23:59 | Auto-detect (past/future/mixed) |
| "weekly review" | Last Monday 00:00 | Next Sunday 23:59 | Full (retro + prospective) |

Default with no argument: **today**.

For "this week" and custom ranges that span past and future, split the analysis at the current time boundary — events before now get retrospective treatment, events after now get prospective treatment.

## Rule Files

Load these from `plugins/work/skills/gtd-calendar-review/` before processing:
- **`event-rules.json`** — deterministic event categorization by title patterns, attendee domains, calendar source
- **`targets.json`** — quantitative targets for time allocation comparison

## Phase 1: Fetch + Categorize

1. **Load rule files** — read `event-rules.json` and `targets.json`

2. **Parse scope** — determine `timeMin`, `timeMax`, and analysis mode from the user's argument. Convert to ISO 8601 with Europe/Madrid offset.

3. **Fetch events** — call `mcp__google__calendar_events_list_all_accounts` with computed `timeMin` and `timeMax`. If range exceeds 7 days, split into multiple calls (e.g., "weekly review" = 2 calls: last week + next week).

4. **Filter:**
   - Remove cancelled events (status = "cancelled")
   - Remove declined events (check attendee responseStatus for user's email)
   - Remove all-day events from meeting calculations (keep as context annotations if they're deadlines or holidays)
   - Deduplicate across accounts: same event appearing on multiple calendars → keep the work account version

5. **Categorize each event** by applying rules in priority order:

   **Priority 1 — Calendar source** (`event-rules.json` → `by_calendar`).
   Match the calendar name or ID. Personal/Gym calendars get direct category assignment.

   **Priority 2 — Title exact match** (`event-rules.json` → `by_title_exact`).
   Exact title match for recurring meetings with stable names.

   **Priority 3 — Title pattern match** (`event-rules.json` → `by_title_pattern`).
   Regex match against event title. Array — first match wins. Each pattern maps to a category.

   **Priority 4 — Attendee domain rules** (`event-rules.json` → `by_attendee_domain`).
   Check all attendee email domains. Use the `role` field to infer category:
   - All attendees are `internal` (neurons-lab.com) → check attendee count:
     - 2 attendees (Alex + 1 other) → `INTERNAL_1ON1`
     - 3+ attendees → `INTERNAL_SYNC`
   - Any attendee has `role: "client"` → `CLIENT_EXTERNAL`
   - Any external domain not in rules → likely `SALES_BD` or `CLIENT_EXTERNAL` (check if NL staff are present to distinguish)

   **Priority 5 — General heuristics** (no rule matched):
   - Solo event (only Alex as attendee or no attendees) on work calendar → `DEEP_WORK_BLOCK` or `OTHER` based on title
   - Event with "prep" in title → `OTHER`
   - Event on personal calendar with no NL attendees → `PERSONAL`
   - Event with >5 attendees and only NL domains → `INTERNAL_SYNC`
   - Default → `OTHER`

6. **Compute duration** for each event in hours (decimal). Handle:
   - Multi-hour events: use actual start-end difference
   - Back-to-back meetings: no overlap adjustment needed (they are separate events)
   - Overlapping events: flag to user, count only the longer one to avoid double-counting

## Phase 2: Analyze + Report

The analysis adapts to the mode determined by scope:

### Single-Day Mode (today / tomorrow)

Generate a chronological schedule view:

```markdown
# Calendar — [Day, Date]

## Schedule

| Time | Duration | Event | Category | Prep |
|------|----------|-------|----------|------|
| 09:00-10:00 | 1h | [c-suite] Weekly Sync | INTERNAL_SYNC | — |
| 10:00-11:30 | 1.5h | Acme<>Neurons Lab | CLIENT_EXTERNAL | Check #client-acme |
| 11:30-14:00 | — | **Focus gap (2.5h)** | | |
| 14:00-15:00 | 1h | 1:1 [teammate] | INTERNAL_1ON1 | Check last 1:1 notes |
| ... | | | | |

## Day Summary
- Meetings: Xh (Y events)
- Focus gaps >30min: [list with time windows]
- Deep work blocks: Xh
- Violations: [evening cutoff, overloaded]

## Prep Hints
- **[Meeting name]** (HH:MM) — [what to check: Slack channel, Notion page, Clay contact, email thread]
```

For **today**: split past (already happened) vs remaining (upcoming). Mark past events with checkmarks.

For each upcoming meeting, generate prep hints:
- `CLIENT_EXTERNAL` → "Check #client-[client] Slack channel, [client] Notion project page, recent email threads, Clay contact for [external attendees]"
- `INTERNAL_1ON1` → "Check pending feedback items, last 1:1 notes"
- `INTERVIEW` → "Review candidate profile, CV"
- `SALES_BD` → "Check Clay contact, last email thread, web search for [company/person]"
- `INTERNAL_SYNC` → "Check relevant Notion project page, Slack channel"

### Retrospective Mode (past range)

```markdown
# Calendar Review — [date range] (Retrospective)

## Time Allocation

| Category | Hours | % of [N]h | vs Target |
|----------|-------|-----------|-----------|
| Client/External | Xh | Y% | — |
| Internal Syncs | Xh | Y% | — |
| Internal 1:1s | Xh | Y% | — |
| Interviews | Xh | Y% | — |
| Sales/BD | Xh | Y% | — |
| Deep Work Blocks | Xh | Y% | Target: 50% → [delta] |
| Gym | Xh | Y% | — |
| Personal | Xh | Y% | — |
| Other | Xh | Y% | — |
| **Total Meetings** | **Xh** | **Y%** | **Warn >35%, Crit >45%** |

Denominator: [N weekdays] x 8h = [total]h standard productive capacity.

## Daily Breakdown

| Day | Meetings | DW Blocks | Personal | Total | Longest Gap | Violations |
|-----|----------|-----------|----------|-------|-------------|------------|
| Mon | Xh | Yh | Zh | Wh | Nh | — |
| Tue | Xh | Yh | Zh | Wh | Nh | — |
| ... | | | | | | |
| Thu | Xh | Yh | Zh | Wh | Nh | DW violated |

## Target Checks

| Target | Status | Detail |
|--------|--------|--------|
| ZoG >= 50% | FAIL/PASS | Actual: X% (Yh of Zh) |
| DW Thursday | FAIL/PASS | N meetings: [list] |
| Evening cutoff 21:00 | FAIL/PASS | N violations: [list] |
| Max 5h meetings/day | FAIL/PASS | [days over] |
| Weekend work-free | FAIL/PASS | [events found] |

## Top Meeting Consumers
1. [Client/Account] — Xh across Y meetings
2. [Client/Account] — Xh across Y meetings
3. ...

## Meeting Patterns
- Recurring meetings: Xh (Y% of meeting time)
- One-off meetings: Xh (Y% of meeting time)
- 1:1 ratio: Xh of Yh total (Z%)
- Average meeting density: X meetings/weekday

## Observations
1. [Key insight — what displaced ZoG this period]
2. [Pattern worth noting]
3. ...
```

### Prospective Mode (future range)

```markdown
# Calendar Preview — [date range]

## Meeting Density

| Day | Meetings | Hours | Available Focus | Status |
|-----|----------|-------|-----------------|--------|
| Mon | N | Xh | Yh | [green/yellow/red] |
| Tue | N | Xh | Yh | [green/yellow/red] |
| ... | | | | |

Status: green = <3h meetings, yellow = 3-5h, red = >5h

## Available Focus Blocks (gaps > 2h)
- **Monday:** 09:00-11:30 (2.5h), 14:00-17:00 (3h)
- **Tuesday:** [none — overloaded]
- ...

## Deep Work Thursday
Status: **PROTECTED** / **AT RISK** (N meetings) / **VIOLATED** (N meetings)
[If not protected: list events and recommend what to move/decline]

## Upcoming Meetings + Prep Hints

### [Day — Date]
| Time | Meeting | Category | Attendees | Prep |
|------|---------|----------|-----------|------|
| 10:00 | Acme Sync | CLIENT | [names] | Check #client-acme, Notion |
| ... | | | | |

### [Day — Date]
...

## Recommendations
1. [Specific actionable recommendation with quantified impact]
2. [e.g., "Move [meeting] from Thursday to [day with gap] — protects DW day"]
3. [e.g., "Add 2h focus block on Wednesday 14:00-16:00 — currently empty"]
4. ...

## Zone of Genius Forecast
- Protected deep work blocks next week: Xh (Y% of 40h)
- If recommendations applied: Zh (W%)
```

### Weekly Review Mode

Combine retrospective for last Mon-Sun + prospective for next Mon-Sun, separated by a horizontal rule. Use the full retrospective and prospective formats above.

## Output Destination

- **"weekly review" mode:** Write to `100 Periodics/Weekly/Week [N]/[YYYY-MM-DD]-calendar-review.md` where Week N is the upcoming week number. Create the folder if it doesn't exist.
- **All other modes:** Print directly in conversation. If the user asks to save, write to an appropriate file.

## Tone

Chief of Staff analyst. Data-driven, concise tables over prose. Surface violations and recommendations prominently — the user wants to know what is wrong and what to do, not a neutral summary. Use bold for violations. Keep observations to 3-5 bullet points maximum.

## Safety

- **CRITICAL: Never create, modify, update, or delete calendar events** — read-only analysis exclusively
- Never call `calendar_event_create`, `gcal_create_event`, `gcal_update_event`, or `gcal_delete_event`
- Recommendations are suggestions in text only — the user takes action manually
- Do not expose full attendee email addresses in the report — use display names or first/last name
- If calendar API returns errors for an account, continue with available data and note the gap
- All times in Europe/Madrid timezone
- This is calendar data only — note explicitly when actual screen time (Rize) or off-screen activities may differ

## Rule Iteration

After each run, if events were classified by heuristics (Priority 5) rather than deterministic rules:
1. Identify the most common uncached patterns (recurring meeting titles, new client domains)
2. Suggest additions to `event-rules.json` with the exact JSON to add
3. Present suggestions to the user — never auto-modify rules without confirmation
4. Target: >90% deterministic classification rate after 3-5 runs
