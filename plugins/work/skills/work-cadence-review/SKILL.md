---
name: work-cadence-review
description: Run structured weekly, monthly, or quarterly reviews of where WORK time actually went, using Rize automatic time tracking as source of truth. Analyzes deep/creative work vs meeting load vs communication overhead, Zone of Genius work share against the 10%->50% target, Neurons-Lab vs personal side-project allocation, and focus fragmentation, then scores against principles, goals, and the 7 Work / 3 Mind area files. Trigger on work time review, time-allocation review, meeting-load audit, deep-work audit, "where did my work time go", productivity/Rize review, or compare-work-periods requests. For the attention-hygiene / digital-wellbeing / screen-time / information-diet lens, use `mind-time-review` instead.
compatibility:
  - tool: mcp__rize__get_current_user
  - tool: mcp__rize__list_my_apps_used
  - tool: mcp__rize__get_my_time_allocation
  - tool: mcp__rize__list_my_time_entries
  - tool: mcp__rize__list_labels
---

# Work - Cadence Review (Time)

Primary entrypoint for structured reviews of how work time is spent, powered by Rize.
This is a deliberate review ritual, not a one-off "how long did I spend on X" question.

Companion skill: `mind:mind-time-review` reads the SAME Rize data through an attention-hygiene lens (distraction, information diet, screen time). When the user asks for "a time review" without qualifying, offer both; they are two lenses on one dataset and are cheap to run together.

## Review Types

- weekly review
- monthly review
- quarterly review (e.g. a March-June rollup)

If cadence is unspecified, infer from context or ask.

## Comparison Rules

Explicit calendar-period comparisons by default.

- weekly = this ISO week vs last ISO week
- monthly = this calendar month vs last calendar month
- quarterly = a multi-month trend; use the earliest month in range as the baseline and read the trend across months, not just endpoints

Do not let a weekly comparison drift into a rolling "last 7 days". Use ISO week boundaries for weekly and calendar-month boundaries for monthly.

## Reasoning Order

Before drawing conclusions, follow this order whenever the private vault has the documents:

1. Read guiding principles and strategy in `000 OS/` — especially `2 Simple strategy 2026` ("Distracted, not focused -> Deep work sessions with mono-tasking"; "Too much time overall -> Time-boxing, planning for life first"; "Systematize management work of Neurons Lab and minimize time and stress there").
2. Check `000 OS/3 Numerical Targets 2026` — the **Zone of Genius work share 10% -> 50%** target (lives in `300 Areas/7 Work/2 - Orange - Entrepreneur`).
3. Read the Work area guidance in `300 Areas/7 Work/`: `0 - Red - Builder` (hands-on tech / talent — the deep creative work), `1 - Blue - Manager` (CTO @ Neurons Lab — the management load to systematize and minimize), `2 - Orange - Entrepreneur` (Zone of Genius target). Also `300 Areas/3 Mind/2 - Orange - Goals & Performance` (the LMS/productivity-systems hub).
4. Only then interpret the Rize data.

Recommendations are checked against intent, not just against metrics.

## Data Sources

- `rize` MCP (`mcp__rize__*`) — automatic desktop time tracking. **Source of truth for actual screen time.**
- Google Calendar (optional cross-check via the `work:gtd-calendar-review` skill or calendar MCP) — scheduled meeting hours, to validate Rize-measured meeting time. Rize measures *attended* meeting time (superior to scheduled blocks); use calendar only to reconcile large gaps.

## Data Reality Rules — READ BEFORE EVERY REVIEW

Rize's convenient-looking fields are partly unreliable. These rules were established empirically and are mandatory, not optional cross-checks:

- **Do NOT build the allocation from labels (`group_by: label` / `label_name`).** Label coverage is sparse and historically absent. Mar-May 2026 were **100% "Unassigned"**; even a labeled month (Jun 2026) was ~67% unassigned. `get_my_time_allocation` grouped by label will silently undercount every real category. Labels are usable only for a recent month with confirmed coverage, and only as a secondary cross-check.
- **`list_projects` / `list_clients` are empty** for this account — there is no project/client allocation. Do not attempt `group_by: project` or `client`. (If the user later sets up projects, this rule can be revisited; flag it as a setup opportunity because it would enable per-client billing analysis.)
- **`list_my_apps_used` is the backbone.** It is the only signal populated consistently across all months. It returns up to 50 apps with `category` and an `is_focus` flag; it accepts a full-month range in one call. Build the analysis from this.
- **Do NOT trust the `is_focus` flag as "deep work".** Rize marks Slack, LinkedIn, and x.com as `is_focus: true` and Google Meet as `false`. Its focus% therefore overstates real focus. **Rebuild your own buckets** from the Bucket Taxonomy below and report the divergence between Rize's `is_focus%` and your rebuilt deep-work% — this is the review's credibility anchor (same discipline as rebuilding a body metric from raw data instead of trusting the vendor score).
- **`list_my_events` (raw app-switch events) is flaky and rate-limited** (7-day cap, frequently errors with INTERNAL_ERROR). Do not depend on it. Use `entry_count` from `get_my_time_allocation` (or the length of `list_my_time_entries`) per tracked day as the **fragmentation proxy** instead.
- **Rize is desktop-only.** It does not see phone time. Any phone/mobile screen-time target cannot be answered from Rize — say so explicitly rather than implying the desktop total is total screen time.
- **`list_my_time_entries` gives the qualitative narrative** — each entry is an AI-titled ~20-40min block with `title`, `description`, `reasoning`, `ai_confidence_score`, and `source` (`ai` | `meeting` | `user` | `timer`). `source: "meeting"` entries come from calendar sync and are the reliable meeting-count signal. Sample entries to name *what* the work actually was (which clients, which interviews, which projects), not just how much.
- **The apps list is capped at 50/period.** The tail beyond 50 is truncated but each tail app is small (<0.3% of tracked); note it, don't chase it.

## Bucket Taxonomy

Rebuild time into these buckets from `list_my_apps_used` (rule: app-name overrides win over `category`):

| Bucket | Rule |
|---|---|
| Code/dev | category `Code`; apps Cursor, Terminal, Codex, Sublime Text, github.com, localhost |
| AI tools | Claude, claude.ai, chatgpt.com, perplexity.ai (AI is the work medium for an AI consultancy) |
| Writing/docs | categories `Documenting`, `Writing` (Obsidian, Notes, docs.google, Notion, Pages, Numbers, drive, Acrobat, reMarkable, Wispr Flow) |
| Design | category `Design` (canva) |
| Research/learning | categories `Learning`, `Reading`, `Research`, `User Research`, `Search`; udemy, google.com |
| Meetings | category `Video Conferencing` (meet.google, zoom, teams calls) |
| Comms | categories `Communications`, `Email`, `Messaging` (Slack, Superhuman, WhatsApp, Telegram, Teams, Loom) |
| Admin/ops/hiring | categories `Scheduling`, `Hiring`, `Customer Support`; hubspot, ashby, novatalent, company/business sites |
| **Side project (personal)** | personal-venture hosts (any personal side-project sites) that are clearly not company work — always break these out separately from company work. |
| Social media | categories `Social Media`, `Linkedin`; x.com (marked `Business` but is scrolling) |
| Entertainment | category `Entertainment` (netflix, youtube, streaming sites), steam |
| News | category `News` |
| Browser (unattributed) | bare `Brave Browser` / `Google Chrome` with no host — browser chrome, not attributable. Report as neutral; exclude from both deep-work and leak. |

Deep/creative work = Code + AI tools + Writing/docs + Design + Research/learning.
Zone of Genius share (per the vault's definition "Code & Learning + Writing") = Code + Writing/docs + Research/learning + AI tools, as a % of tracked time.

## Metrics To Compute (per period, with period-over-period delta)

1. Total tracked desktop time; average tracked hours/day; tracked-day count.
2. Bucket breakdown (hours + % of tracked) using the taxonomy above.
3. **Zone of Genius work share** vs the 50% target.
4. **Meeting load** — hours and % of tracked; name the biggest meeting types from `list_my_time_entries` (source: meeting). This is the CTO management load to minimize.
5. **Communication overhead** — Slack + email + messaging hours and %.
6. **Side-project vs Neurons Lab** — call out personal side-project hours explicitly as opportunity-cost against consultancy Zone-of-Genius work.
7. **Fragmentation** — entry_count / tracked-day (higher = more fragmented). Note that Rize blocks are ~20-40min, so a high entry count with low deep-work% signals context-switching.
8. **Rize is_focus% vs rebuilt deep-work%** — report both and explain the gap.

## Workflow

1. Determine the review window(s) and the comparison window(s). Keep both explicit if weekly + monthly are requested together.
2. Read OS strategy, targets, and the 7 Work / 3 Mind area guidance before concluding.
3. In a single parallel batch, pull from Rize:
   - `get_current_user` (timezone, confirm identity)
   - `list_my_apps_used` for the review window AND the comparison window
   - `get_my_time_allocation` (for `entry_count` / tracked totals) for both windows
   - `list_my_time_entries` (a sample across the window; filter `source: ["meeting"]` for meeting detail)
   - `list_labels` + a label allocation ONLY if the window is a recent month with confirmed coverage
4. Rebuild buckets from apps_used per the taxonomy. Compute all metrics above for each window.
5. Optionally cross-check meeting hours against Google Calendar; reconcile only large gaps.
6. Compare current vs prior equivalent period, bucket by bucket and metric by metric.
7. Score against targets (Zone of Genius 50%), principles (deep work / mono-tasking; minimize management time; time-boxing), and the Work-area intent.
8. Back-reference the prior review's priorities and grade follow-through.
9. Produce the structured review; save the file(s).

## Recommendation Rules

- One to three high-leverage priorities, not a checklist.
- Tie each recommendation to a specific pattern in the data AND a specific target, principle, or system.
- Separate data-backed observations, interpretations, and assumptions-due-to-missing-data.
- Take a position and end with concrete numbered next actions (vault voice: sentences < 25 words; numbers/names over generalities; no banned words — delve, leverage, robust, navigate, journey, ecosystem).

## Output Contract

Structure the review around:

- review scope and comparison windows (+ "Source of truth: Rize desktop time; phone time not captured")
- a scorecard delta table (bucket hours + % across periods, with a Trend column for multi-month)
- for multi-month trends, open with a one-paragraph narrative headline that reframes the raw numbers before any table
- deep/creative work, meetings, communication, admin/hiring, and side-project sections
- the Rize-is_focus%-vs-rebuilt-deep-work% reconciliation
- alignment with goals (Zone of Genius), systems (management systematization), and principles
- top 3 priorities
- risks, caveats, and missing data (label sparsity, desktop-only, no project tags)
- recommended next actions (numbered)

Numbers first, then interpretation, then recommendation. Detailed enough to feel like a real operating review.

## File Saving

Weekly and monthly reviews always create report files. Do not ask whether to save.

```bash
# Monthly / quarterly rollup
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"
# Weekly
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"
```

Example paths (mirror the body-review naming):
- monthly: `$PERIODICS_ROOT/Monthly/06 June/2026-06-work-time-review.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 11/2026-week-11-work-time-review.md`

Open the file with an H1 + a bold metadata block (Review period / Comparison period / Source / Generated / Related), matching the body reviews. Do NOT add YAML frontmatter to review outputs.

## Resources

Before final recommendations, check `400 Resources/` for productivity/deep-work material and the `300 Areas/3 Mind` information-diet references if a recommendation needs backing.

## Tone

Operating review with quant discipline. Numbers first, then interpretation, then recommendations. No fluff.

## Schema

Reference `../../schemas/time-review.json` for the structured output. Set `lens: "work-productivity"`.
