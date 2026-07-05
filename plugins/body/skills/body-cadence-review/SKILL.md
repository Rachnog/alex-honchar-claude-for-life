---
name: body-cadence-review
description: Run structured weekly, monthly, quarterly, or yearly body reviews that compare time periods, cross-check multiple body data sources, and generate recommendations grounded in principles, goals, habits, systems, and local body documents. Trigger on review, recap, retrospective, compare periods, progress review, or holistic body check-in requests.
compatibility:
  - tool: mcp__plugin_body_oura__get_daily_sleep
  - tool: mcp__plugin_body_oura__get_sleep
  - tool: mcp__plugin_body_garmin-connect__get_activities
  - tool: mcp__plugin_body_garmin-connect__get_health_metrics
  - tool: mcp__plugin_body_withings__withings_get_weight
  - tool: mcp__plugin_body_withings__withings_get_measurements
  - tool: mcp__plugin_body_yazio__get_user_daily_summary
---

# Body - Cadence Review

Use this as the primary entrypoint for structured body reviews.
It is designed for deliberate review rituals rather than one-off questions.

## Review Types

- weekly review
- monthly review
- quarterly review
- yearly review

If the user does not specify the cadence, infer it from context or ask.

## Comparison Rules

Cadence reviews use explicit calendar-period comparisons by default.

- weekly review means `this week` vs `last week`
- monthly review means `this month` vs `last month`
- quarterly review means the current quarter vs the previous quarter
- yearly review means the current year vs the previous year

For weekly reviews, use ISO week boundaries.
For monthly reviews, use calendar-month boundaries.

If the user asks for both a weekly and monthly review together, compute each comparison independently.
Do not let a weekly comparison drift into "late last month" or another rolling recent baseline.

## Reasoning Order

Before using MCPs or local resources, follow this order whenever the private vault contains the relevant documents:

1. Read the guiding principles and strategy in `000 OS/`.
2. Check the numerical targets in `3 Numerical Targets 2026`.
3. Read the body area guidance in `300 Areas/Body/`: protocols (`0 Intro to body protocols`), beliefs (`Body beliefs`), and maintenance systems (`Body maintenance systems`).
4. Only then pull MCP data and local resources from `400 Resources/`.

This ordering is mandatory because recommendations must be checked against intent, not just against metrics.

## MCP Servers

- `oura-mcp` - sleep, readiness, HRV, activity
- `garmin-mcp` - workouts, training load, readiness-adjacent performance signals
- `withings-mcp` - body composition and weight trend
- `yazio-mcp` - nutrition, hydration, and logging consistency

## Data Completeness Requirements

A prior review initially understated activity and missed real findings by relying on summary-level or sparse pulls, and only caught it after the user pushed back twice. Follow these on every cadence review, not just when something looks wrong — verifying is cheaper than a correction pass later:

- **Oura sleep — pull BOTH endpoints, not one.** `get_daily_sleep` only returns 0-100 contributor scores. `get_sleep` (a separate endpoint) returns the raw night: actual duration in seconds for total/deep/light/rem/awake, `time_in_bed`, `average_hrv` (ms), `average_heart_rate`/`lowest_heart_rate` (bpm), `average_breath`, `efficiency`, `latency`, `restless_periods`, and `low_battery_alert` (bool). The score alone can imply a smoother or different trend than what the real duration/HRV numbers show — this has already produced one real reporting error (a period that looked like a smooth score decline actually had a real duration dip that was worse in one month and partly recovered the next). When sleep coverage has unexplained gaps across the review window, check `low_battery_alert` on the nights that do have data before writing "ring wasn't charged" as an explanation — if it reads `false` throughout, that theory is ruled out, not confirmed, and the real cause should be left unresolved rather than guessed at. A full-month `get_sleep` pull is large (~130KB, with per-5-minute heart_rate/hrv arrays and hypnogram strings) and will likely overflow to a file — extract just the summary scalars with `jq` rather than reading the raw arrays.
- **Garmin activities — always pull with `includeSummaryOnly: false`** (or omit the parameter — false is the schema default) whenever VO2Max or training quality matters. The summary view silently drops `training.vO2MaxValue`, `training.aerobicEffect`, `training.anaerobicEffect`, and `training.trainingEffectLabel` — this is the *only* place VO2Max appears in this connector (not `get_activity_details`, not `get_health_metrics`, and Oura does not report it at all for this account).
- **Garmin daily health metrics — pull every day of the window, not a weekly sample**, whenever Oura's sleep/activity coverage is sparse or has gaps. `get_health_metrics` steps/heart_rate are per-day only, but a full-month pull (~30 calls) is worth it: Garmin is a different device from Oura and does not share its coverage gaps, and a sparse sample has previously made an under-tracked month look worse than it was. `body_battery`, `stress`, and `hydration` metric options on this connector currently return "service unavailable" for this account — try them each review in case that changes, but do not block on them, and do not trust `get_training_stress_balance` (CTL/ATL/TSB) — it has returned all-zero output every time so far. Use Training Effect labels (from the full-detail activities pull above) as the working substitute for training-load-quality signal.
- **Withings measurements — pull a broad `measureTypes` list, not just weight/fat/muscle/bone.** Types 91 (Pulse Wave Velocity, m/s) and 155 (Vascular Age, years) are a second, independent cardiovascular-age reading, cross-checkable against Oura's `get_daily_cardiovascular_age`. Raw PWV values roughly agree between the two devices; their age-conversion formulas do not (expect a 5-7 year gap) — compare the PWV number, not either device's "age" label, when reporting agreement or disagreement. Also: don't filter measurement groups to type==1 (weight) only when parsing — same-visit PWV/vascular-age/heart-pulse readings can live in a separate group at the identical timestamp and will be silently dropped.
- **Yazio nutrition — sample at least 8-10 dates per month for a monthly review, not 4-5.** A sparse sample has previously made intermittent-but-real logging look like a complete stop. Remember `steps`/`activity_energy` in `get_user_daily_summary` sync automatically from a connected health app independent of food logging — a day with real steps can still have zero meals logged, so don't infer "day was tracked" from steps alone; check the `meals` block itself.
- **Before writing that a month or domain "collapsed" or "fully stopped," treat that as a hypothesis to actively falsify with a denser pull first** — not the default reading of a sparse or summary-only sample. If, after a denser check, the finding still holds, say so with the stronger evidence behind it.

## Supporting Inputs

- `mind:streaks-export-analysis` - required habits-adherence evidence for weekly and monthly body reviews, acquired via Apple Shortcuts

Streaks is not a replacement for biometric sources, but it is a required input for confirming routine execution, maintenance habits, and systems adherence.

## Hard Gate — Streaks for Weekly and Monthly Reviews

For weekly and monthly reviews, run `shortcuts run "Streaks Export"` via Bash in the SAME parallel batch as MCP data pulls. This is not a later step — it fires at the same time as Oura, Garmin, Withings, and Yazio calls.

If the shortcut succeeds: save the output, then invoke `mind:streaks-export-analysis` to interpret it.
If the shortcut fails (non-zero exit, empty output, shortcut not found): STOP. Ask the user to provide the export manually. Do not continue.

Do not produce any review output — no scorecard, no domain summaries, no recommendations, no files — until Streaks data is resolved.

Forbidden:
- Pulling MCP data first, then asking the user for Streaks as an afterthought
- Producing a "draft" or "partial" review without Streaks
- Mentioning missing Streaks only as a caveat in an otherwise complete review
- Skipping the `shortcuts run` attempt and going straight to a manual ask
- Treating Streaks as a "nice to have" that can come later

| Rationalization | Why it is wrong |
|---|---|
| "I'll present the biometric data first" | Streaks runs in parallel with MCP pulls. There is no "first." |
| "The user can provide Streaks later" | You must try `shortcuts run` yourself before asking. |
| "A draft review is useful even without Streaks" | The skill forbids any review output without Streaks. STOP. |
| "Streaks is supplementary" | For weekly and monthly reviews, Streaks is mandatory input, not supplementary. |

## Review Workflow

1. Determine the review period and the comparison window.
   - For `weekly`, define the current ISO week and the immediately previous ISO week.
   - For `monthly`, define the current calendar month and the immediately previous calendar month.
   - If both are requested, keep both window pairs explicit all the way through the review.
2. Read the OS numerical targets and body area guidance (protocols, beliefs, maintenance systems) before drawing conclusions.
3. Execute ALL of the following in parallel (single tool-call batch):
   a. Pull the relevant windows from each active MCP data source (Oura, Garmin, Withings, Yazio).
   b. For weekly and monthly reviews: run `shortcuts run "Streaks Export"` via Bash.
   If the shortcut fails, STOP — see the Hard Gate section above.
   For quarterly and yearly reviews, skip Streaks (not required).
4. For weekly and monthly reviews: invoke `mind:streaks-export-analysis` to interpret the Streaks export and produce habits-adherence evidence.
5. Ask each specialist domain to produce its evidence:
   - `body-sleep`
   - `body-recovery`
   - `body-composition`
   - `body-diet`
   - `body-exercise`
   - `body-medical-checkups`
6. Compare the current period to the prior equivalent calendar period.
   - Weekly means `this week` vs `last week`.
   - Monthly means `this month` vs `last month`.
   - Do not substitute rolling windows unless they are explicitly labeled as supplemental context.
7. Compare domains against each other, not just against their own history.
8. Cross-check findings against goals, habits, maintenance systems, and stated principles.
9. Use Streaks evidence to strengthen `habits_alignment` and `systems_alignment`, especially when the biometrics alone do not explain execution quality.
10. Search `400 Resources/` when recommendations need more context.
11. Produce a structured review with priorities, caveats, and next actions.

## What To Compare

Every cadence review should look for:

- period-over-period changes inside each domain
- cross-domain relationships such as sleep vs training, nutrition vs composition, recovery vs load, or stress vs adherence
- consistency against maintenance habits and recurring systems
- direct routine adherence from Streaks when the review depends on execution rather than only on passive sensing
- goal progress against numerical targets
- conflicts between what the data says and what the operating system says should matter

When specialist skills are invoked from `body-cadence-review`, they must use the exact review and comparison windows passed by the caller.
They may mention rolling-baseline context only as supplemental context, never as the primary comparison.

## Recommendation Rules

- Recommendations must be thoughtful, not generic.
- Prefer one to three high-leverage priorities instead of a long checklist.
- Tie recommendations back to a specific pattern in the data and a specific goal, habit, system, or principle.
- If external research or a local resource materially informed the advice, cite it.
- Separate:
  - data-backed observations
  - interpretations
  - assumptions due to missing data

## Escalation Rules

Stay in `body-cadence-review` when the user asks for a ritualized review or a broad progress synthesis.

Delegate or embed specialist logic when the review needs domain depth:

- `body-sleep` for sleep-stage, HRV, efficiency, and baseline analysis
- `body-recovery` for readiness and load-management calls
- `body-composition` for body recomposition and trend interpretation
- `body-diet` for calorie, macro, hydration, and logging adherence
- `body-exercise` for consistency, load, and habit execution
- `body-medical-checkups` for checkup cadence, labs, and follow-up urgency

If the user only wants a narrow answer, de-escalate to `body-data-qa`.

## Data Quality Rules

- Prefer period windows over isolated daily snapshots.
- Prefer personal baselines over generic averages.
- Explicitly mark incomplete connectors, sparse logging, stale measurements, or inferred metrics.
- Treat Streaks reports as self-tracked execution evidence, not as proof of physiological outcome.
- If Streaks and biometric sources disagree, report both rather than forcing a false reconciliation.
- If one domain has poor data quality, reduce confidence in cross-domain conclusions that depend on it.
- Never fabricate a review section for a domain with no evidence; mark it as unavailable instead.

## Output Contract

Structure the review around:

- review scope and comparison windows
- scorecard of major domains
- key changes since the prior period
- cross-domain correlations
- alignment with goals, habits, systems, and principles
- top priorities
- risks, caveats, and missing data
- recommended next actions

The response should be detailed enough to feel like a real review, but still numbers-first and decision-oriented.

When both a weekly and monthly review are requested together, treat them as two separate cadence-review outputs.
Each output should carry its own review window, comparison window, findings, and save path.
`../../schemas/cadence-review.json` describes one cadence review at a time, so do not force a combined weekly+monthly response into a single schema object.

## File Saving

Weekly and monthly body reviews must always create report files. Do not ask whether to save them.

Save rules:

- monthly reviews: save inside the correct month-name subfolder under the monthly parent in `Periodics`
- weekly reviews: save inside the correct `Week N` subfolder under the weekly parent in `Periodics`
- if both a monthly and weekly review are requested together, create both files
- create the period folder only if it does not already exist

Use commands shaped like:

```bash
# Monthly review
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"

# Weekly review
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"
```

Example output paths:

- monthly: `$PERIODICS_ROOT/Monthly/February/2026-02-body-review.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 10/2026-week-10-body-review.md`

If the review cannot be completed because Streaks data has not yet been provided, do not create the final review files yet. Create them only after the required Streaks input is available and the review can be completed.

## Resources

Before final recommendations, search `400 Resources/` for relevant protocols, medical references, training notes, or other body-supporting material. Prioritize newer material and anything linked from the active body area documents.

## Tone

Thoughtful operating review with quant discipline. Numbers first, then interpretation, then recommendations. No fluff.

## Schema

Reference `../../schemas/cadence-review.json` for the structured review output.
