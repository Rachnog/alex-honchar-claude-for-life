---
name: monthly-review
description: >
  Run a comprehensive MONTHLY review across all 8 life areas — the monthly twin of `weekly-review`,
  following the Integrated Life Planning OS. Consolidation-first: it makes sure each area's monthly
  cadence review exists (reading it, or generating it via the area's own skill), then synthesizes them
  into ONE monthly note with a headline, per-area reflections, cross-area correlations, rolled-up
  monthly actions, planning against the numerical targets, housekeeping, and an issue log. Trigger on:
  "monthly review", "do my monthly review", "month in review", "consolidate the month", "review my
  month", "close out the month", "full monthly review", or "[month] review" (e.g. "June review").
  For a single week use `weekly-review`; for one area's deep monthly dive, use that area's cadence skill.
compatibility:
  - tool: mcp__claude_ai_Clay__searchContacts
  - tool: mcp__claude_ai_Google_Calendar__list_events
  - tool: mcp__claude_ai_HubSpot__search_crm_objects
  - tool: mcp__claude_ai_Notion__notion-search
---

# Monthly Review v1.0 — Cross-Area Life OS Review (monthly)

The top-level MONTHLY orchestrator, and the counterpart to `mind:weekly-review`. **It is
consolidation-first.** Unlike the weekly review (which pulls a week of raw data across 10+ MCP servers),
each life area already owns a monthly cadence-review skill that writes a detailed
`2026-MM-<area>-review.md` into `100 Periodics/Monthly/<month>/`. This skill's job is to ensure those
exist, read them, and synthesize the month — not to re-pull a month of raw data.

> **DESIGN PRINCIPLE:** mirrors `Templates/Monthly review template.md`
> (Areas reflections → Monthly specific actions → Monthly planning → Housekeeping), enriched with the
> proven `weekly-review` scaffold (headline, cross-area correlations, issue log). Weekly and monthly are
> co-equal cadences in `000 OS/0 How My LMS Works.md`.

## Life Areas & Delegation Map

The review covers the 8 life areas. Each maps to the monthly cadence skill that produces its section, and
the file that skill writes. Areas without a dedicated skill get a brief inline reflection.

| # | Area | Monthly skill to (read or) invoke | Expected file in `Monthly/<month>/` |
|---|------|-----------------------------------|--------------------------------------|
| 1 | **Body** | `body:body-cadence-review` (monthly) | `2026-MM-body-review.md` |
| 2 | **Shadow** | — inline (Oura stress/resilience, journaling gaps) | — |
| 3 | **Mind** | `mind:mind-time-review` + `mind:info-diet` | `2026-MM-mind-time-review.md`, `2026-MM-info-diet-review.md` |
| 4 | **Spirit** | — inline (Streaks meditation/rest, contemplative habits) | — |
| 5 | **Relationships** | `relationships:relationships-personal-review` + `relationships:relationships-network-review` | `2026-MM-relationships-personal-review.md`, `2026-MM-relationships-network-review.md` (+ any consolidated `2026-MM-relationships-review.md`) |
| 6 | **Lifestyle** | `lifestyle:digital-wellbeing` | `2026-MM-digital-wellbeing-review.md` |
| 7 | **Wealth** | the vault-local `finances` skill | its finance report |
| 8 | **Work** | `work:work-cadence-review` (+ `work:gtd-calendar-review`) | `2026-MM-work-time-review.md` |

## Context

- **User:** Alex Honchar, Co-Founder & CTO at Neurons Lab. Timezone: Europe/Madrid.
- The Orange OKR dashboard lives in `000 OS/3 Numerical Targets 2026`; principles in
  `000 OS/1 Principles and values 2026`; per-area practice files under `300 Areas/`.

## Reasoning Order

1. **Determine the month.** Default: the just-completed calendar month. If run mid-month, review the
   current month-to-date and say so explicitly. `$MONTH_NAME` = the `NN Month` folder (e.g. `06 June`).
2. **Comparison window:** the immediately prior calendar month.
3. Read the OS principles, the numerical targets (Orange OKRs), and area practice files as needed —
   THEN synthesize. Numbers first, then interpretation, then recommendation.

## Phase 1: Ensure each area's monthly review exists

For each area in the delegation map, check for its file in
`$PERIODICS_ROOT/Monthly/$MONTH_NAME/2026-MM-<area>-review.md`:

- **Present and for this month** → read it. (Do not regenerate — trust the area specialist's output.)
- **Missing or stale** → invoke that area's monthly cadence skill to generate it (it saves to the same
  folder), then read the result.
- **Shadow / Spirit** (no dedicated skill) → produce a short inline reflection from whatever signals
  exist (Oura stress/resilience for Shadow; Streaks meditation/rest for Spirit). Mark as light if no data.

Run the "already present?" checks in one batch (a single `ls`/globbing pass over the month folder). Only
invoke the skills whose files are missing — this is what makes the monthly review cheap.

## Phase 2: Per-area reflections (the "Areas reflections" section)

For each area, distill from its review file (do NOT re-derive from raw data):
- **Status** (on-track / at-risk / off-track) and the area review's **headline finding**.
- **Top metric vs target** (pull the one number that matters, with its goal).
- **Top priority** carried up from that review.
- A **wikilink** to the area file so the reader can drill in.

Keep each area to its key signals — this is a synthesis, not a re-run.

## Phase 3: Cross-area correlations

The synthesis value-add — patterns that span two or more areas, which no single-area review can see.
Numbered, each with evidence. Examples of the *kind* of link to look for:
- A derailer showing up in multiple areas (e.g. under-initiation in Relationships + solo attention in Mind).
- A resource in one area constraining another (e.g. always-on screens in Lifestyle vs deep-work in Work).
- Body recovery trend vs Work meeting load; Wealth pipeline stress vs Shadow stress.

## Phase 4: Monthly specific actions (rolled-up priorities)

Merge the per-area top priorities into a single **ranked top 3–5** for the coming month. Prefer the
highest-leverage cross-area moves. Each action ties to a specific finding and a goal/target.

## Phase 5: Monthly planning

Forward-looking, per area, plus explicit progress on the `3 Numerical Targets 2026` OKRs (which targets
moved, which are at-risk, run-rate to year-end). Split Personal vs Business where useful (checkbox lists).

## Phase 6: Housekeeping

- GTD inbox/system audit (delegate to `work:gtd-*` skills only if the user asks; otherwise a light status).
- **Review-completeness check:** a table of the 8 areas × whether the monthly review existed / was
  generated / is missing, so gaps are visible.

## Phase 7: Issue log

Systematic patterns (not one-off incidents) recurring this month or across months: pattern, evidence,
impact on goals, suggested structural fix.

## Output Contract

No YAML frontmatter. Structure:

```markdown
# Monthly Review — [Month YYYY]

**Review period:** [Month YYYY]
**Comparison:** vs [prior month]
**Source:** per-area monthly reviews (+ live pulls for areas without a skill)
**Generated:** YYYY-MM-DD
**Related:** [[2026-MM-body-review]] · [[2026-MM-work-time-review]] · [[2026-MM-mind-time-review]] · [[2026-MM-info-diet-review]] · [[2026-MM-digital-wellbeing-review]] · [[2026-MM-relationships-personal-review]] · [[2026-MM-relationships-network-review]]

## Headline
[One paragraph: the month across all areas.]

## Areas reflections
### 1. Body … ### 2. Shadow … ### 3. Mind … ### 4. Spirit … ### 5. Relationships … ### 6. Lifestyle … ### 7. Wealth … ### 8. Work
[each: status, headline finding, top metric vs target, top priority, link to the area file]

## Cross-area correlations
[numbered, with evidence]

## Monthly specific actions
[ranked top 3–5 cross-area priorities]

## Monthly planning
[per-area next-month focus + numerical-target/OKR progress]

## Housekeeping
[GTD/system status + review-completeness table]

## Issue log
[systematic patterns with evidence and structural fix]
```

## File Saving

Always save; do not ask.

```bash
# Resolve $PERIODICS_ROOT from the vault root visible in your vault's CLAUDE.md — do not hardcode
PERIODICS_ROOT="<VAULT_ROOT>/100 Periodics"
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"
```

Save as: `$PERIODICS_ROOT/Monthly/$MONTH_NAME/[YYYY]-[MM]-monthly-review.md` (e.g. `2026-06-monthly-review.md`).
If the vault path does not exist, save to Desktop and inform the user.

## Delegation Rules

- Missing area monthly review → invoke that area's cadence skill (see the map), then read its file.
- Deep-dive into one area requested → hand off to that area's skill; the monthly review stays a synthesis.
- GTD inbox clearing requested → `work:gtd-daily-triage` / `gtd-email-triage` / `gtd-slack-triage`.

## Tone

Thoughtful monthly operating review. Numbers first, then interpretation, then recommendations. Tables
over prose; surface problems prominently; bold the violations. The user is a quantitative CTO — match it.
Keep each area to key signals, not a re-dump of the area review.

## Safety

- **Read-only** re: all external systems — never create/modify/delete calendar, email, Slack, Notion, or
  HubSpot records during the review.
- Use display names, not full email addresses, for external contacts.
- Do not fabricate data for areas with no sources — mark them explicitly as unavailable.
- All times Europe/Madrid. If a source or sub-skill errors, continue with available data and note the gap.
