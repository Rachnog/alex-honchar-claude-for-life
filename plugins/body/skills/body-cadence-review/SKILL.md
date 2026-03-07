---
name: body-cadence-review
description: Run structured weekly, monthly, quarterly, or yearly body reviews that compare time periods, cross-check multiple body data sources, and generate recommendations grounded in principles, goals, habits, systems, and local body documents. Trigger on review, recap, retrospective, compare periods, progress review, or holistic body check-in requests.
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
2. Identify the relevant body systems, targets, and habits in the OS systems/targets document (for example `3 Systems and Targets 2026`).
3. Read the relevant body area guidance in `300 Areas/Body/` and linked documents such as protocols, pillars, or routines.
4. Only then pull MCP data and local resources from `400 Resources/`.

This ordering is mandatory because recommendations must be checked against intent, not just against metrics.

## MCP Servers

- `oura-mcp` - sleep, readiness, HRV, activity
- `garmin-mcp` - workouts, training load, readiness-adjacent performance signals
- `withings-mcp` - body composition and weight trend
- `yazio-mcp` - nutrition, hydration, and logging consistency

## Supporting Inputs

- `mind:streaks-export-analysis` - required habits-adherence evidence for weekly and monthly body reviews, acquired via Apple Shortcuts

For weekly and monthly body reviews, Streaks is mandatory. Use Apple Shortcuts to get the export. Do not search the filesystem for old `.streaks` files and do not continue without Streaks data.
Streaks is not a replacement for biometric sources, but it is a required input for confirming routine execution, maintenance habits, and systems adherence.

## Review Workflow

1. Determine the review period and the comparison window.
   - For `weekly`, define the current ISO week and the immediately previous ISO week.
   - For `monthly`, define the current calendar month and the immediately previous calendar month.
   - If both are requested, keep both window pairs explicit all the way through the review.
2. Read the OS, systems/targets, and area guidance before drawing conclusions.
3. Pull the relevant windows from each active data source.
4. For weekly and monthly reviews, get Streaks data through Apple Shortcuts before continuing.
   - If Streaks data is not already provided, first try to run the Shortcut automatically via the `shortcuts` CLI.
   - Prefer the shortcut named `Streaks Export` when it exists.
   - Example command: `shortcuts run "Streaks Export"`
   - If the automatic Shortcut run fails, the shortcut is missing, or the output is unusable, then ask the user to run the Shortcut manually and stop there.
   - Do not continue with only Oura, Garmin, Withings, and Yazio.
   - Do not silently use an old file on disk.
   - Do not finish the review and mention missing Streaks only in caveats.
   - Preferred fallback wording: `I tried to run your Apple Shortcuts Streaks export automatically, but I still need the resulting file or payload to complete this weekly/monthly body review.`
5. Use `mind:streaks-export-analysis` to interpret the Streaks export and provide habits-adherence evidence.
6. Ask each specialist domain to produce its evidence:
   - `body-sleep`
   - `body-recovery`
   - `body-composition`
   - `body-diet`
   - `body-exercise`
   - `body-medical-checkups`
7. Compare the current period to the prior equivalent calendar period.
   - Weekly means `this week` vs `last week`.
   - Monthly means `this month` vs `last month`.
   - Do not substitute rolling windows unless they are explicitly labeled as supplemental context.
8. Compare domains against each other, not just against their own history.
9. Cross-check findings against goals, habits, maintenance systems, and stated principles.
10. Use Streaks evidence to strengthen `habits_alignment` and `systems_alignment`, especially when the biometrics alone do not explain execution quality.
11. Search `400 Resources/` when recommendations need more context.
12. Produce a structured review with priorities, caveats, and next actions.

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
