---
name: body-composition
description: Provide specialist body-composition evidence from Withings data when `body-data-qa` or `body-cadence-review` needs composition-domain depth, or when the user explicitly asks for a body-composition-only deep dive.
compatibility:
  - tool: mcp__withings__withings_get_weight
  - tool: mcp__withings__withings_get_body_composition
  - tool: mcp__garmin-connect__get_activities
---

# Body - Composition

Analyze body composition from Withings, contextualized by Garmin training data.
Use this as the composition specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants composition-only depth.

## MCP Servers

- withings-mcp — weight kg, body fat %, muscle mass kg, bone mass kg,
  water %, BMI
- garmin-mcp — training load, workout history (for context)

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/` when available.
2. Identify the relevant body systems and targets in the OS systems/targets document.
3. Read the relevant body area guidance in `300 Areas/Body/`.
4. Then compare current measurements against composition goals and flag progress.

## Analysis

- Pull the latest measurement from `withings-mcp`.
- For direct composition-only trend questions, pull 14-30 days and compare recent movement to the prior equivalent period when useful.
- When invoked from `body-cadence-review`, use the exact review and comparison windows provided by the caller, such as `this week` vs `last week` or `this month` vs `last month`.
- Do not silently convert a cadence review into a rolling 14-30 day comparison unless it is explicitly labeled as supplemental context.
- Focus on trend lines, not isolated weigh-ins. Single-day weight fluctuations are noise.
- Contextualize with Garmin training volume when it helps explain recomposition.
- Track recomposition patterns such as fat decreasing while muscle is stable or rising.
- Flag when the trend direction moves away from goals even if scale weight looks superficially positive.

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/body-composition.json`.
Present the findings in prose under this shape:

- `Current measurements` - latest body composition values
- `Trend` - the direction of weight, fat, and muscle over the active window
- `Interpretation` - whether the pattern suggests progress, stall, or regression
- `Goal alignment` - how the trend maps to stated body-composition targets
- `Caveats` - sparse weigh-ins, measurement noise, or missing training context

## Escalation Rules

Stay in `body-composition` when the user explicitly wants composition-only depth or when an upstream workflow already scoped the task to body measurements or recomposition.

Escalate to:

- `body-diet` when intake adherence is the main explanatory variable
- `body-exercise` when training execution is the main explanatory variable
- `body-data-qa` for ad-hoc cross-domain comparisons
- `body-cadence-review` for ritualized multi-period reviews

## Resources

Only search `400 Resources/` when this specialist is being used directly for a composition-only deep dive.
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

Reference ../../schemas/body-composition.json for field definitions.
