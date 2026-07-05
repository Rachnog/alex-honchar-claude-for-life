---
name: weekly-review
description: >
  Run a comprehensive weekly review across all 8 life areas following the Integrated Life Planning
  OS. Orchestrates parallel data pulls from Oura, Garmin, Withings, Yazio, Google Calendar, Gmail,
  Slack, Notion, HubSpot, Clay, Fireflies, and Streaks. Produces a structured review with
  housekeeping audit, accomplishments, per-area reflection, planning, sharing opportunities,
  and issue log. Trigger on: "weekly review", "do my weekly review", "life review", "OS review",
  "full review", "review my week", "review all life areas", or any request for a comprehensive
  cross-area weekly check-in.
compatibility:
  - tool: mcp__oura__get_daily_sleep
  - tool: mcp__oura__get_daily_readiness
  - tool: mcp__oura__get_daily_activity
  - tool: mcp__oura__get_daily_stress
  - tool: mcp__oura__get_daily_resilience
  - tool: mcp__oura__get_daily_cardiovascular_age
  - tool: mcp__garmin-connect__get_activities
  - tool: mcp__garmin-connect__get_weekly_volume
  - tool: mcp__garmin-connect__get_daily_overview
  - tool: mcp__withings__withings_get_body_composition
  - tool: mcp__yazio__get_user_daily_summary
  - tool: mcp__yazio__get_user_water_intake
  - tool: mcp__yazio__get_user_goals
  - tool: mcp__google-workspace__manage_accounts
  - tool: mcp__google-workspace__manage_email
  - tool: mcp__google-workspace__manage_calendar
  - tool: mcp__claude_ai_Google_Calendar__gcal_list_events
  - tool: mcp__claude_ai_Google_Calendar__gcal_list_calendars
  - tool: mcp__claude_ai_Gmail__gmail_search_messages
  - tool: mcp__claude_ai_Slack__slack_search_public_and_private
  - tool: mcp__claude_ai_Notion__notion-search
  - tool: mcp__claude_ai_Notion__notion-fetch
  - tool: mcp__claude_ai_HubSpot__search_crm_objects
  - tool: mcp__claude_ai_HubSpot__get_user_details
  - tool: mcp__claude_ai_Clay__get_user_information
  - tool: mcp__claude_ai_Clay__searchContacts
  - tool: mcp__claude_ai_Fireflies__fireflies_get_transcripts
---

# Weekly Review v1.0 — Cross-Area Life OS Review

Run a comprehensive weekly review across all life areas following the Integrated Life Planning OS.
This is the top-level orchestration skill — it delegates to domain specialists where they exist
and directly pulls data for areas without dedicated skills.

> **DESIGN PRINCIPLE:** This skill mirrors the user's weekly review template in Notion.
> The structure is: Housekeeping → Accomplishments →
> Reflection (per life area) → Planning → Sharing → Clean-up → Issue Log.

## Life Areas

The review covers 8 life areas (consolidated from the 10-area Integrated Life Planning Template):

| # | Area | What it covers | Primary data sources |
|---|------|---------------|---------------------|
| 1 | **Body** | Physical health, fitness, nutrition, body composition, sleep | Oura, Garmin, Withings, Yazio, Streaks |
| 2 | **Shadow** | Emotional health, mental health, journaling, coaching, stress | Oura (stress, resilience), journals (manual) |
| 3 | **Mind** | Intellectual growth, KMS, LMS, information diet, learning | Notion, Obsidian, newsletters, Streaks |
| 4 | **Spirit** | Spiritual health, meditation, contemplative practices | Manual input, Streaks |
| 5 | **Relationships** | Partner, family, friendships, network, CRM | Clay, Google Calendar, Fireflies |
| 6 | **Lifestyle** | Quality of life, travel, experiences, subscriptions, admin | Email, Calendar, Notion tasks |
| 7 | **Wealth** | Finances, investments, taxes, company financials | HubSpot, email (invoices), Notion |
| 8 | **Work** | Neurons Lab (founder/CTO/BDM), team, delivery, pipeline | HubSpot, Fireflies, Slack, Notion, Gmail, Calendar |

## Context

- **User:** Alex Honchar, Co-Founder & CTO at Neurons Lab
- **Timezone:** Europe/Madrid
- **Google accounts:** three connected accounts — personal, brand/content, and work. Discover them via `manage_accounts` rather than hardcoding addresses.
- **Body goals:** read current weight/step/water/calorie/protein targets from the vault targets file (`000 OS/3 Numerical Targets`) and Yazio goals — do not hardcode values here.

## Reasoning Order

Before pulling data, determine the review window:

1. **Default:** The current ISO week (Monday to Sunday). If today is Monday, review the prior week.
2. **Custom:** If the user specifies a date range, use that.
3. **Comparison window:** Always compare against the immediately prior ISO week.

## Phase 1: Parallel Data Pull

Execute ALL of the following in a single parallel tool-call batch. Use `ToolSearch` first to load
any deferred MCP tools needed.

### 1A. Load Deferred Tools

Before calling MCP tools, use `ToolSearch` to load tool schemas for any deferred tools:
- `select:mcp__garmin-connect__get_activities,mcp__garmin-connect__get_weekly_volume,mcp__garmin-connect__get_daily_overview`
- `select:mcp__oura__get_daily_sleep,mcp__oura__get_daily_readiness,mcp__oura__get_daily_stress,mcp__oura__get_daily_resilience,mcp__oura__get_daily_cardiovascular_age`
- `select:mcp__withings__withings_get_body_composition`
- `select:mcp__yazio__get_user_daily_summary,mcp__yazio__get_user_water_intake,mcp__yazio__get_user_goals`
- `select:mcp__claude_ai_Google_Calendar__gcal_list_events,mcp__claude_ai_Gmail__gmail_search_messages`
- `select:mcp__claude_ai_Slack__slack_search_public_and_private,mcp__claude_ai_Notion__notion-search`
- `select:mcp__claude_ai_Fireflies__fireflies_get_transcripts,mcp__claude_ai_HubSpot__search_crm_objects,mcp__claude_ai_HubSpot__get_user_details`
- `select:mcp__claude_ai_Clay__get_user_information`
- `select:mcp__google-workspace__manage_accounts,mcp__google-workspace__manage_email`

Run all ToolSearch calls in parallel in a single batch.

### 1B. Pull Data (all in parallel after tools are loaded)

**Body data:**
- `mcp__garmin-connect__get_activities` — limit 20, includeSummaryOnly true
- `mcp__garmin-connect__get_weekly_volume` — current ISO week, includeTrends true
- `mcp__garmin-connect__get_daily_overview` — one call per day of the review week
- `mcp__oura__get_daily_sleep` — startDate/endDate = review week
- `mcp__oura__get_daily_readiness` — startDate/endDate = review week
- `mcp__oura__get_daily_stress` — startDate/endDate = review week
- `mcp__oura__get_daily_resilience` — startDate/endDate = review week
- `mcp__oura__get_daily_cardiovascular_age` — startDate/endDate = review week
- `mcp__oura__get_sleep` — startDate/endDate = review week (detailed sleep architecture)
- `mcp__withings__withings_get_body_composition` — latest
- `mcp__yazio__get_user_daily_summary` — one call per day of the review week
- `mcp__yazio__get_user_water_intake` — one call per day of the review week
- `mcp__yazio__get_user_goals` — current goals

**Work data:**
- `mcp__google-workspace__manage_accounts` — operation: list (discover all accounts)
- `mcp__google-workspace__manage_email` — operation: triage, for each of 3 accounts
- `mcp__claude_ai_Google_Calendar__gcal_list_events` — review week, primary calendar, maxResults 100
- `mcp__claude_ai_Fireflies__fireflies_get_transcripts` — fromDate/toDate = review week, limit 50, format json
- `mcp__claude_ai_HubSpot__get_user_details` — current user context
- `mcp__claude_ai_HubSpot__search_crm_objects` — objectType DEAL, open deals, sorted by closedate

**Mind & Relationships data:**
- `mcp__claude_ai_Notion__notion-search` — "weekly tasks review goals projects", page_size 25
- `mcp__claude_ai_Notion__notion-search` — "week [N] tasks bizdev delivery [month] [year]", with created_date_range filter
- `mcp__claude_ai_Slack__slack_search_public_and_private` — "after:[start] before:[end+1]", sort timestamp, limit 20, concise
- `mcp__claude_ai_Clay__get_user_information` — user context

**Streaks (for Body + Mind):**
- Run `shortcuts run "Streaks Export"` via Bash in this same parallel batch.
- If shortcut fails, note it and continue (unlike body-cadence-review, the weekly review does not hard-gate on Streaks — it produces a degraded review with a warning).

### 1C. Secondary Pulls (dependent on Phase 1B results)

After the first batch completes:
- If work calendar from Google Workspace API failed, use `mcp__claude_ai_Google_Calendar__gcal_list_events` with the work account's email as `calendarId`
- Fetch any Notion task databases or pages referenced in the search results that are relevant
- If Streaks succeeded, invoke `mind:streaks-export-analysis`

## Phase 2: Analysis by Life Area

For each life area, analyze the data and produce a section. Use domain specialist skills where they exist.

### 2.1 Body

**Delegate to `body:body-cadence-review`** if available and the user wants the full body protocol.
Otherwise, produce the Body section directly using the data pulled in Phase 1.

Structure:
- **Training summary:** Activities table (day, type, duration, distance, calories, avg/max HR), weekly volume totals, vs prior week trends
- **Sleep:** Daily table (score, duration, bedtime, wake time, deep sleep contributor, HRV avg, lowest HR), average sleep score, architecture analysis
- **Readiness & Recovery:** Daily scores, trend direction, cardiovascular age trend, stress summary, resilience level
- **Body composition:** Weight vs goal vs start weight, fat %, muscle mass, hydration
- **Nutrition:** Daily table (calories, protein, fat, carbs, tracking status), averages, vs adjusted goals, weekend tracking gap analysis
- **Steps:** Daily table with bar visualization, days meeting 10k goal, NEAT analysis
- **Water:** Daily tracking compliance
- **Streaks habits adherence** (if available)

### 2.2 Shadow

- Oura stress data: daily summary, stress_high vs recovery_high balance
- Resilience contributors trend (sleep_recovery, daytime_recovery, stress management)
- Flag if no journaling/coaching data sources are connected
- Note any emotional signals from meeting notes or Slack tone

### 2.3 Mind

- Information diet: categorize newsletters and content consumed from email
- Notion activity: tasks and pages modified during the review week
- Learning/content: any courses, books, articles referenced
- KMS/LMS activity: Obsidian vault activity (if accessible)
- Streaks cognitive habits (if available)

### 2.4 Spirit

- Flag as "no data sources connected" unless Streaks includes meditation/spiritual habits
- Surface indirect signals: sauna sessions, rest days, bedtime consistency

### 2.5 Relationships

- **Network movements:** New contacts from meetings (Fireflies attendees), Clay CRM updates
- **Relationship maintenance:** Who was interacted with this week (meetings, emails, Slack DMs)
- **Upcoming social:** Events, trips, networking opportunities from calendar + Notion tasks
- **Action items:** CRM updates needed, follow-ups, testimonials, introductions

### 2.6 Lifestyle

- **Travel planning queue:** Extract from Notion tasks anything related to trips, events, travel
- **Subscriptions & admin:** Flag expiring services, pending admin tasks (taxes, renewals)
- **Calendar load vs free time:** Ratio of meetings to unstructured time

### 2.7 Wealth

- **Company financials:** Revenue, projections, cash flow (from Fireflies meeting summaries)
- **Sales pipeline:** Active HubSpot deals, new deals this week, stale deals needing cleanup
- **Personal finance signals:** Tax filing status, investment activity, subscription costs
- **Receivables/disputes:** Overdue invoices, payment issues

### 2.8 Work

- **Meetings:** Full list from Fireflies with duration, type classification (leadership/sales/delivery/hiring/ops), key action items extracted per meeting
- **Business development:** Deal movement, new pipeline, partner engagements, proposals
- **Team management:** Hiring pipeline (ATS candidates), OKR status, team coordination
- **Delivery:** Client project status, risks, upsell opportunities
- **Email inbox status:** Per-account unread counts, key threads needing attention
- **Slack activity:** Active channels, key threads, decisions made
- **Notion tasks:** Open tasks, recently modified, overdue items

## Phase 3: Planning Section

Generate forward-looking action items split into Personal and Business columns (matching the template):

### Personal Planning
- [ ] Plan leisure and free time for next week
- [ ] Specific personal tasks carried forward or newly identified
- [ ] Health/body adjustments based on review findings
- [ ] Admin/lifestyle items with deadlines

### Business Planning
- [ ] Upcoming meetings review — prep needed for key meetings
- [ ] Business development — priority lead and partner follow-ups
- [ ] Team management — tasks to assign, feedback to share, hiring actions
- [ ] Urgent action items from this week's meetings

## Phase 4: Sharing Section

Identify shareable learnings from the week:
- Content ideas from business activities, meetings, or reading
- Internal sharing opportunities (team, Slack channels)
- Public sharing opportunities (LinkedIn, newsletter/scheduler)
- Specific people to share insights with

## Phase 5: Issue Log

Identify **systematic patterns** (not one-off incidents) that recurred this week or are recurring across weeks:
- Pattern description
- Evidence from this week's data
- Impact on goals
- Suggested structural fix

## Output Contract

Structure the final review as:

```markdown
# Weekly Review — Week [N] ([date range])

## Housekeeping: GTD Inboxes
[Table: inbox, status, unread count, key items]

## Accomplishments
### Binary (done/not done)
### Compounding (building over time)

## Life Area Reviews

### 1. Body
[Full body analysis with tables]

### 2. Shadow
[Stress, resilience, emotional health]

### 3. Mind
[Information diet, learning, KMS/LMS]

### 4. Spirit
[Spiritual practices or data gap flag]

### 5. Relationships
[Network, CRM, social calendar]

### 6. Lifestyle
[Travel, admin, quality of life]

### 7. Wealth
[Financials, pipeline, investments]

### 8. Work
[Meetings, bizdev, team, delivery]

## Planning
[Personal + Business columns with checkboxes]

## Sharing
[Learnings and distribution channels]

## Issue Log
[Systematic patterns with evidence and fixes]
```

## File Saving

Always save the review to the Obsidian vault periodics folder:

```bash
# Resolve $PERIODICS_ROOT from the vault root visible in your vault's CLAUDE.md — do not hardcode
PERIODICS_ROOT="<VAULT_ROOT>/100 Periodics"
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"
```

Save as: `$PERIODICS_ROOT/Weekly/Week $ISO_WEEK/[YYYY]-week-[N]-weekly-review.md`

If the vault path does not exist, save to Desktop and inform the user.

## Delegation Rules

- **Body deep-dive requested:** Delegate to `body:body-cadence-review`
- **Calendar deep-dive requested:** Delegate to `work:gtd-calendar-review`
- **Email triage requested:** Delegate to `work:gtd-email-triage`
- **Slack triage requested:** Delegate to `work:gtd-slack-triage`
- **Streaks analysis:** Delegate to `mind:streaks-export-analysis`

The weekly review produces a comprehensive but concise overview. If the user wants to go deeper
into any area, delegate to the specialist skill.

## Token Efficiency

This review pulls from 10+ MCP servers. To manage token budget:
- Use `includeSummaryOnly: true` for Garmin activities
- Use `condenseEventDetails: true` for Google Calendar
- Use `response_format: "concise"` for Slack searches
- Use `max_highlight_length: 80` for Notion searches
- Use `format: "json"` for Fireflies (most structured)
- Limit email triage to `operation: "triage"` (top 20 per account), not full search
- For Yazio, only pull daily summaries (not individual consumed items)
- For Oura activity, skip if the response is too large (>100k chars) — use Garmin steps instead

## Comparison Windows

Every metric should be contextualized:
- **vs prior week:** Direction (up/down/flat) and magnitude
- **vs goal:** Current vs target with gap
- **vs baseline:** Personal baseline where established (resting HR, sleep score, weight)

Do not compare against population averages unless the user has no personal baseline.

## Tone

Thoughtful operating review. Numbers first, then interpretation, then recommendations.
Direct and concise — tables over prose. Surface problems prominently. Use bold for violations
and red flags. Keep each life area section to the key signals, not an exhaustive data dump.
The user is a quantitative CTO — match that sensibility.

## Safety

- **Never create, modify, or delete** calendar events, emails, Slack messages, Notion pages,
  or HubSpot records during the review — read-only analysis exclusively
- Do not expose full email addresses of external contacts in the report — use display names
- Do not fabricate data for life areas with no data sources — mark them explicitly as unavailable
- All times in Europe/Madrid timezone
- If an MCP server is unavailable or errors, continue with available data and note the gap
