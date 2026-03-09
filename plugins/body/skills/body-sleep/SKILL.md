---
name: body-sleep
description: Provide specialist sleep evidence using Oura data when `body-data-qa` or `body-cadence-review` needs sleep-domain depth, or when the user explicitly asks for a sleep-only deep dive rather than general body Q&A.
compatibility:
  - tool: mcp__oura__get_daily_sleep
  - tool: mcp__oura__get_sleep
---

# Body - Sleep

Use this as the sleep specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants sleep-only depth.

## MCP Server

oura-mcp — pull sleep data including: score, stages (deep/rem/light/awake
durations + percentages), efficiency, HRV avg, lowest HR, avg HR, bedtime,
wake time, latency, temp delta, respiratory rate, restfulness.

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/` when available.
2. Identify the relevant body systems and targets in the OS systems/targets document.
3. Read the relevant body area guidance in `300 Areas/Body/`.
4. Then compare current data against sleep goals and flag progress or regression.

## Analysis

Produce sleep evidence that can stand on its own or feed a larger synthesis.

- Pull the requested date or latest available sleep record from `oura-mcp`.
- For direct sleep-only trend questions, pull a 7-14 day window unless the caller asks for longer.
- When invoked from `body-cadence-review`, use the exact review and comparison windows provided by the caller, such as `this week` vs `last week` or `this month` vs `last month`.
- Do not substitute a rolling 7-14 day baseline for cadence reviews unless it is explicitly labeled as supplemental context.
- Prioritize HRV, deep sleep percentage, REM balance, efficiency, and lowest heart rate over raw total-hours simplifications.
- Flag deviations greater than one standard deviation from the recent personal baseline when the data supports it.
- Use directional language such as "HRV up 8% over 14 days" or "deep sleep down 11% vs prior week".
- Personal baselines first. Do not use population averages unless the question is explicitly about a medical reference.
- If training impact matters, coordinate with `body-recovery`.

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/sleep.json`.
Present the findings in prose under this shape:

- `Current snapshot` - the key sleep metrics for the requested date or most recent night
- `Trend` - the direction over the comparison window
- `Goal alignment` - whether sleep behavior is supporting stated body goals
- `Caveats` - missing nights, inferred conclusions, low-confidence metrics, or device limitations

## Escalation Rules

Stay in `body-sleep` when the request explicitly asks for sleep-only depth or when an upstream workflow already scoped the task to sleep.

Escalate to:

- `body-recovery` when the main question is whether to train and recovery capacity is the decision point
- `body-data-qa` when the question compares sleep with another domain in an ad-hoc way
- `body-cadence-review` when the user wants a weekly, monthly, quarterly, or yearly review

## Resources

Only search `400 Resources/` when this specialist is being used directly for a sleep-only deep dive.
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

Reference `../../schemas/sleep.json` for field definitions.
