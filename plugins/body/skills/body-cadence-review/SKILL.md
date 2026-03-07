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

- `mind:streaks-export-analysis` - optional habits-adherence evidence from a Streaks export or a recent Streaks report

Use Streaks evidence when the review needs direct proof of routine execution, maintenance habits, or behavior that sensors do not capture well, such as supplements, stretching, journaling, rehab, or wind-down routines.
Do not treat Streaks as a replacement for biometric sources; it is supporting behavior evidence.

## Review Workflow

1. Determine the review period and the comparison window.
2. Read the OS, systems/targets, and area guidance before drawing conclusions.
3. Pull the relevant windows from each active data source.
4. If the review is substantially about habits, systems, or routine adherence, use `mind:streaks-export-analysis`.
   - For live or recent windows such as `this week`, `last week`, `this month`, or `last month`, prefer a fresh Streaks export unless the user explicitly wants to reuse an existing report.
   - For older or clearly file-based reviews, a recent saved Streaks report is acceptable when the user authorizes it.
5. Ask each specialist domain to produce its evidence:
   - `body-sleep`
   - `body-recovery`
   - `body-composition`
   - `body-diet`
   - `body-exercise`
   - `body-medical-checkups`
6. Compare the current period to the prior equivalent period when possible.
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

## Resources

Before final recommendations, search `400 Resources/` for relevant protocols, medical references, training notes, or other body-supporting material. Prioritize newer material and anything linked from the active body area documents.

## Tone

Thoughtful operating review with quant discipline. Numbers first, then interpretation, then recommendations. No fluff.

## Schema

Reference `../../schemas/cadence-review.json` for the structured review output.
