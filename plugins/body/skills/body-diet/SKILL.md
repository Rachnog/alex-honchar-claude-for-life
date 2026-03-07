---
name: body-diet
description: Provide specialist nutrition evidence from Yazio when `body-data-qa` or `body-cadence-review` needs diet-domain depth, or when the user explicitly asks for a nutrition-only deep dive.
---

# Body - Diet

Analyze nutrition data from Yazio and assess adherence to calorie, macro, and hydration goals.
Use this as the diet specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants diet-only depth.

## MCP Server

yazio-mcp — pull user goals, daily summary, consumed items, water intake, exercises, and weight entries.

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/` when available.
2. Identify the relevant body systems and targets in the OS systems/targets document.
3. Read the relevant body area guidance in `300 Areas/Body/`.
4. Then compare nutrition behavior against diet and body composition goals.

## Analysis

- Pull today or the requested date from `yazio-mcp`.
- For trends, pull the last 7-14 days, or 30 days when the question is broader.
- Calculate adherence against goals:
  - energy_kcal consumed vs target
  - protein_g, carb_g, fat_g consumed vs targets
  - water_ml consumed vs target
- Analyze meal distribution across breakfast, lunch, dinner, and snacks.
- Flag high day-to-day calorie variance and repeated macro under-target patterns.
- Track logging consistency using consumed-item presence per day.
- If an explicit streak is unavailable, derive a streak proxy from consecutive logged days.
- Mark inferred metrics with lower confidence than direct MCP fields.
- Prioritize protein and consistency adherence for recomposition-oriented goals.
- Cross-reference with `body-recovery` and `body-composition` when training or physique context is relevant.

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/diet.json`.
Present the findings in prose under this shape:

- `Current intake snapshot` - the latest daily totals against targets
- `Trend` - adherence and variance over the active window
- `Behavior pattern` - meal timing, logging consistency, or repeated misses
- `Goal alignment` - whether intake behavior supports the active body goal
- `Caveats` - inferred streaks, missing logging, or weak hydration coverage

## Escalation Rules

Stay in `body-diet` when the user explicitly wants diet-only depth or when an upstream workflow already scoped the task to nutrition behavior and adherence.

Escalate to:

- `body-composition` when the core question is physique change rather than intake behavior
- `body-recovery` when the core decision is fueling versus recovery capacity
- `body-data-qa` for ad-hoc cross-domain comparisons
- `body-cadence-review` for weekly, monthly, quarterly, or yearly reviews

## Resources

Only search `400 Resources/` when this specialist is being used directly for a nutrition-only deep dive.
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

Reference ../../schemas/diet.json for field definitions.
