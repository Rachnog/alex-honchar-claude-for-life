---
name: body-exercise
description: Provide specialist exercise evidence from Garmin when `body-data-qa` or `body-cadence-review` needs training-domain depth, or when the user explicitly asks for an exercise-only deep dive.
compatibility:
  - tool: mcp__garmin-connect__get_activities
  - tool: mcp__garmin-connect__get_weekly_volume
  - tool: mcp__garmin-connect__get_activity_details
  - tool: mcp__garmin-connect__get_health_metrics
---

# Body - Exercise

Analyze exercise behavior and training consistency with a focus on execution
against defined habits and systems.
Use this as the exercise specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants exercise-only depth.

## MCP Server

garmin-mcp — pull workout history, training load, training status, steps,
activity sessions, and related performance signals.

**Always call `get_activities` with `includeSummaryOnly: false`** (or omit the parameter — `false` is the schema default) whenever VO2Max or training quality matters. The summary view silently drops `training.vO2MaxValue`, `training.aerobicEffect`, `training.anaerobicEffect`, and `training.trainingEffectLabel` (values like `AEROBIC_BASE`, `RECOVERY`, `TEMPO`, `ANAEROBIC_CAPACITY`). This is the *only* place VO2Max shows up in this connector — `get_activity_details` only returns split-level pace/HR/distance, not training effect or VO2Max, and Oura does not report VO2Max at all for this account (its dedicated endpoint returns empty). `get_training_stress_balance` (CTL/ATL/TSB) has returned all-zero output in every review to date — do not treat it as evidence of low training load; use the Training Effect labels above as the working substitute for training-load-quality signal. For daily steps/resting-HR context beyond what the activity log covers, `get_health_metrics` is per-day only — pull the full window rather than a sparse sample when a different-device cross-check against Oura's activity data is warranted (Oura and Garmin do not share coverage gaps).

## Supporting Inputs

- `mind:streaks-export-analysis` - optional exercise-adjacent adherence evidence from Streaks

Use Streaks only as supporting evidence for habits Garmin may undercapture or miss entirely, such as warmups, stretching, rehab, walking goals, sauna, or showing up to train without a clean recorded workout.
Garmin remains the primary source for actual training load and workout execution.

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/`.
2. Check the numerical targets in `3 Numerical Targets 2026`.
3. Read the body area guidance in `300 Areas/Body/`: protocols (`0 Intro to body protocols`), beliefs (`Body beliefs`), and maintenance systems (`Body maintenance systems`).
4. Then prioritize alignment with:
- gym frequency habit (per the targets file)
- strength/cardio/mobility balance
- sustainable progression over intensity spikes

## Analysis

- For direct exercise-only questions, pull the current week and the last four weeks from `garmin-mcp`.
- When invoked from `body-cadence-review`, use the exact review and comparison windows provided by the caller, such as `this week` vs `last week` or `this month` vs `last month`.
- Do not let cadence-review comparisons drift into `current week vs recent baseline` unless that rolling view is explicitly labeled as supplemental context.
- Evaluate session frequency against the weekly habit target.
- For direct exercise-only questions, compare recent load versus the historical baseline to flag over-loading and under-loading.
- For cadence reviews, keep the caller-provided comparison window as the primary frame and mention historical baseline only as supplemental context when useful.
- Assess pattern consistency such as missed streaks or irregular session timing.
- If Garmin evidence is incomplete or the question depends on exercise-adjacent routines, use `mind:streaks-export-analysis` to fill the adherence gap.
- For live or recent windows such as `this week` or `last month`, prefer a fresh Streaks export unless the user explicitly wants to reuse an existing report.
- For older or clearly file-based exercise questions, an authorized saved Streaks report is acceptable.
- Distinguish real progression from isolated hard-session spikes.
- Correlate the training pattern with sleep and recovery context when relevant.
- For planning questions, recommend next 7 days intensity mix:
  - hard / moderate / light / rest distribution

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/exercise.json`.
Present the findings in prose under this shape:

- `Current execution` - recent training frequency and load
- `Trend` - how consistency and load changed over the active window
- `Habit alignment` - whether behavior matches the stated system and weekly targets
- `Interpretation` - whether the pattern suggests progress, drift, or unsustainable spikes
- `Caveats` - missing activity capture, ambiguous workout labels, weak context, or Streaks-vs-Garmin mismatch

## Escalation Rules

Stay in `body-exercise` when the user explicitly wants exercise-only depth or when an upstream workflow already scoped the task to training behavior and execution.

Escalate to:

- `body-recovery` when the real question is intensity readiness or rest-day choice
- `body-data-qa` for ad-hoc comparisons with diet, sleep, or composition
- `body-cadence-review` for structured weekly, monthly, quarterly, or yearly reviews

## Resources

Only search `400 Resources/` when this specialist is being used directly for an exercise-only deep dive.
When invoked from `body-data-qa` or `body-cadence-review`, let the upstream workflow decide whether resource-backed recommendations are needed.

If a direct deep dive needs resource support:
1. Use find and grep to locate files related to the current query
2. Read .md and .txt files directly
3. For PDFs, extract text and scan for relevant sections
4. For Excel files, read and parse relevant sheets
5. Prioritize newer files over older ones
6. Cite which resource informed your recommendation

Search broadly — file names may not be descriptive. Look at actual content.

## Tone

Quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schema

Reference ../../schemas/exercise.json for field definitions.
