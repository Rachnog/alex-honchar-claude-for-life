---
name: body-recovery
description: Provide specialist recovery and training-readiness evidence when `body-data-qa` or `body-cadence-review` needs recovery-domain depth, or when the user explicitly asks for a recovery-only readiness deep dive.
---

# Body - Recovery

Use this as the recovery and readiness specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants recovery-only depth.

## MCP Servers

- oura-mcp — readiness score, contributors (HRV balance, body temp,
  recovery index, resting HR, previous night, sleep balance)
- garmin-mcp — training status (Productive/Maintaining/Recovery/Unproductive),
  7d training load, recovery time hrs, body battery start/end, avg stress

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/` when available.
2. Identify the relevant body systems and targets in the OS systems/targets document.
3. Read the relevant body area guidance in `300 Areas/Body/`.
4. Then compare against training and recovery goals.

## Analysis

Pull readiness from `oura-mcp` and training context from `garmin-mcp`, then produce a defensible readiness call.

**Recommendation logic:**
- Readiness >= 85 AND recovery_time = 0 -> high intensity ok
- Readiness 70-84 OR recovery_time <= 12 -> moderate ok
- Readiness 50-69 OR recovery_time 12-24 -> light only
- Readiness < 50 OR recovery_time > 24 -> rest day
- When Oura and Garmin disagree -> default to the more conservative one

**Sleep-training impact** (cross-reference body-sleep):
- How yesterday's training affected last night's HRV and deep sleep
- Pull multiple days if needed to show the pattern

For trend questions, pull 7-14 days of data and compare the current window to the prior window when possible.

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/recovery.json`.
Present the findings in prose under this shape:

- `Current readiness call` - today's recommendation and confidence
- `Key drivers` - the few metrics that drove the call
- `Trend context` - whether readiness and load are improving, stable, or deteriorating
- `Goal alignment` - whether the current pattern supports sustainable training goals
- `Caveats` - missing device data, conflicting signals, or inferred assumptions

## Escalation Rules

Stay in `body-recovery` when the user explicitly wants recovery-only depth or when an upstream workflow already scoped the task to readiness and load management.

Escalate to:

- `body-sleep` when the user really wants a sleep-quality analysis rather than a training recommendation
- `body-data-qa` when the question compares recovery with diet, composition, or another adjacent domain
- `body-cadence-review` for ritualized weekly, monthly, quarterly, or yearly reviews

## Resources

Only search `400 Resources/` when this specialist is being used directly for a recovery-only deep dive.
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

Reference ../../schemas/recovery.json for field definitions.
