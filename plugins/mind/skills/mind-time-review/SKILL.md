---
name: mind-time-review
description: Run structured weekly, monthly, or quarterly reviews of digital ATTENTION and information diet, using Rize automatic time tracking. Measures the attention leak (social media, entertainment/streaming, doomscroll news), focus quality and fragmentation, slow long-form vs short-form dopamine consumption, and desktop screen-time load, scored against the Lifestyle screen-time target, the strategy principles ("Distracted, not focused -> deep work / mono-tasking", "Short videos -> consume slow and long-form", "Spend more time offline"), and the Mind information-diet references (Digital Minimalism, dopamine culture). Trigger on attention review, focus review, screen-time review, digital wellbeing / digital minimalism check, distraction audit, information-diet review, or "how healthy was my attention this week/month". For the work-output lens (Zone of Genius, meeting load, deep-work productivity) use `work-cadence-review` instead.
compatibility:
  - tool: mcp__rize__get_current_user
  - tool: mcp__rize__list_my_apps_used
  - tool: mcp__rize__get_my_time_allocation
  - tool: mcp__rize__list_my_time_entries
---

# Mind - Time Review (Attention)

Primary entrypoint for reviewing the health of digital attention and information diet, powered by Rize.
This is the attention-hygiene lens on time; the work-output lens lives in `work:work-cadence-review`. They read the SAME Rize data and are cheap to run together — offer both when the user asks for "a time review" unqualified.

## Review Types

- weekly review (this ISO week vs last ISO week)
- monthly review (this calendar month vs last)
- quarterly review (multi-month trend; earliest month = baseline)

Use ISO week boundaries for weekly and calendar months for monthly. No rolling "last 7 days".

## Reasoning Order

1. Read `000 OS/2 Simple strategy 2026` — the attention-relevant lines: "Distracted, not focused -> Deep work sessions with mono-tasking", "Short videos -> Consume slow and long-form content", and core principle "Spend more time offline and outside in places that give me energy".
2. Check the screen-time targets in `300 Areas/4 Lifestyle/0 - Red - Hobby & Fun` — read the current daily mobile screen-time and phone-use targets from that file rather than assuming values.
3. Read `300 Areas/3 Mind/2 - Orange - Goals & Performance` (the information-diet / LMS hub) and its linked references `[[Digital_Minimalism-_Choosing_a_Focus]]` and `[[The rise of dopamine culture]]`.
4. Only then interpret the Rize data.

## Data Sources

- `rize` MCP (`mcp__rize__*`) — automatic **desktop** time tracking. Source of truth for what happened on the laptop.
- If a phone/mobile screen-time number exists (Screen Time export, manual estimate), use it — Rize cannot supply it.

## Data Reality Rules — READ BEFORE EVERY REVIEW

- **Build from `list_my_apps_used`, not from labels.** Label coverage is sparse-to-absent historically (Mar-May 2026 were 100% "Unassigned"; Jun ~67% unassigned). Rebuild categories yourself.
- **Do NOT report Rize's `is_focus%` as your focus number.** Rize marks Slack, LinkedIn, and x.com as `is_focus: true`. That inflates "focus". Compute your own focus vs leak split from the Bucket Taxonomy and report the gap between the two — it is the review's honesty anchor.
- **`list_my_events` is flaky** (7-day cap, frequent errors). Use `entry_count` per tracked day as the fragmentation proxy.
- **Rize is desktop-only.** It cannot measure phone doomscrolling. The screen-time target is a *phone* target — state plainly that Rize does not cover it, and treat the desktop leak as a lower bound on total distraction.
- **`list_my_time_entries`** narrates what the sessions were; sample it to distinguish, e.g., long-form learning from short-form scrolling within the same "browsing" time.

## Bucket Taxonomy

From `list_my_apps_used` (app-name overrides win over `category`):

| Bucket | Rule | Attention read |
|---|---|---|
| Focused work | Code, AI tools, Writing/docs, Design, Research/learning | The good — sustained attention |
| Meetings | `Video Conferencing` | Structured but not solo-focus |
| Comms | `Communications`, `Email`, `Messaging` | Fragmentation driver |
| **Social media** | `Social Media`, `Linkedin`; x.com | Leak — dopamine / infinite scroll |
| **Entertainment** | `Entertainment` (netflix, youtube, streaming) | Split long-form (Netflix film) vs short-form (YouTube/shorts) per "consume slow, long-form" |
| **News** | `News` (news sites, current-affairs media) | Leak when doomscrolling; note news-cycle pull |
| Admin/personal | `Scheduling`, `Hiring`, shopping, personal sites | Neutral logistics |
| Browser (unattributed) | bare Brave/Chrome | Neutral |

**Attention leak = Social media + Entertainment + News.** Report it in hours and as % of tracked desktop time.

## Metrics To Compute (per period, with delta)

1. Total tracked desktop hours; average/day. (State: phone not included.)
2. **Attention leak** (social + entertainment + news) in hours and % of tracked — the headline.
3. Social-media hours, broken to platforms (threads, x, linkedin, instagram, facebook).
4. Entertainment hours, split **long-form vs short-form** (Netflix/long film vs YouTube/shorts/streaming binges) — score against "consume slow and long-form".
5. News/doomscroll hours.
6. **Focus ratio** — focused-work hours / tracked hours, YOUR rebuild, next to Rize's inflated `is_focus%`.
7. **Fragmentation** — entry_count / tracked-day; comms hours as a switching driver.
8. **Longest-standing distraction** — the single biggest leak app and its trend across periods.

## Workflow

1. Set the review + comparison windows.
2. Read the strategy attention-lines, the Lifestyle screen-time target, and the Mind information-diet references before concluding.
3. Parallel Rize pull: `get_current_user`, `list_my_apps_used` (review + comparison windows), `get_my_time_allocation` (entry_count/tracked totals), and a `list_my_time_entries` sample.
4. Rebuild buckets; compute the leak, focus ratio, long-vs-short-form split, and fragmentation for each window.
5. Compare current vs prior equivalent period.
6. Score against the screen-time target, the "mono-tasking / slow long-form / offline" principles, and the digital-minimalism references.
7. Back-reference the prior review's priorities; grade follow-through.
8. Produce the structured review; save the file(s).

## Recommendation Rules

- One to three high-leverage priorities. Prefer subtractions (block a site, cap a platform, batch comms) over vague "be more mindful".
- Tie each to a specific leak in the data and a specific principle or target.
- Separate observation / interpretation / assumption. Vault voice: sentences < 25 words; numbers over generalities; banned words — delve, leverage, robust, navigate, journey, ecosystem.

## Output Contract

- review scope + comparison windows (+ "Source: Rize desktop only; phone attention not captured — leak figures are a lower bound").
- a scorecard delta table (leak buckets + focus ratio across periods, Trend column for multi-month).
- for multi-month trends, open with a narrative headline reframing the numbers.
- attention-leak, social-media, entertainment (long vs short form), news, and fragmentation sections.
- the rebuilt-focus% vs Rize-is_focus% reconciliation.
- alignment with the screen-time target, attention principles, and information-diet references.
- top 3 priorities; risks/caveats (desktop-only lower bound, label sparsity); numbered next actions.

Numbers first, then interpretation, then recommendation.

## File Saving

Weekly and monthly reviews always create report files. Do not ask whether to save.

```bash
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"     # monthly / quarterly
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"   # weekly
```

Example paths:
- monthly: `$PERIODICS_ROOT/Monthly/06 June/2026-06-mind-time-review.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 11/2026-week-11-mind-time-review.md`

H1 + bold metadata block (Review period / Comparison period / Source / Generated / Related). No YAML frontmatter on review outputs.

## Resources

Pull the Mind information-diet references from `400 Resources/` (Digital Minimalism, dopamine culture) when a recommendation needs backing.

## Tone

Honest attention audit. Numbers first, no moralizing, end with concrete subtractions.

## Schema

Reference `../../schemas/time-review.json`. Set `lens: "mind-attention"`.
