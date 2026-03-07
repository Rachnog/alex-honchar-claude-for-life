---
name: body-data-qa
description: Default top-level entrypoint for ad-hoc body questions. Use for direct questions about current status, recent trends, metric interpretation, or targeted cross-checks across sleep, recovery, exercise, diet, body composition, and medical data when a structured cadence review is not requested.
---

# Body - Data Q&A

Use this as the primary entrypoint for ad-hoc body questions.
It should answer a concrete question quickly, with numbers first, and only expand into broader synthesis when the question genuinely spans multiple domains.

## Reasoning Order

Before using MCPs or local resources, follow this order whenever the private vault contains the relevant documents:

1. Read the guiding principles and strategy in `000 OS/`.
2. Identify the relevant body system or target in the OS systems/targets document (for example `3 Systems and Targets 2026`).
3. Read the relevant area guidance in `300 Areas/Body/` and linked body documents.
4. Only then pull MCP data and local resources from `400 Resources/`.

If one of these layers is missing, continue with explicit caveats instead of blocking.

## MCP Servers

- `oura-mcp` - sleep, readiness, HRV, activity
- `garmin-mcp` - training load, workouts, VO2max, steps, body battery
- `withings-mcp` - weight and body composition
- `yazio-mcp` - calories, macros, hydration, food logging

## Supporting Inputs

- `mind:streaks-export-analysis` - optional habits-adherence evidence when the question is about routine execution, consistency, or behavior drift

Use Streaks selectively. It is most useful for questions like:

- whether a routine was actually executed
- whether adherence dropped before the biometric trend changed
- whether a maintenance system was followed consistently

Do not pull Streaks into every body question by default.

## When To Use

Use `body-data-qa` by default when the user asks things like:

- "How did I sleep?"
- "Should I train today?"
- "What happened to my calories this week?"
- "Is my body fat trend moving the right way?"
- "Compare protein intake and gym consistency"
- "What changed between last week and this week?" when the scope is still a targeted question rather than a full ritual review

Do not use this as the primary skill for weekly, monthly, quarterly, or yearly reviews. Escalate those to `body-cadence-review`.

## Workflow

1. Identify whether the question is single-domain or cross-domain.
2. Pull only the minimum data needed to answer the question well.
3. If the question is materially about adherence, routine execution, or habit consistency, use `mind:streaks-export-analysis`.
   - For live or recent windows such as `today`, `this week`, `last week`, `this month`, or `last month`, prefer a fresh Streaks export unless the user explicitly wants to reuse an existing report.
   - For older or clearly file-based questions, an authorized saved Streaks report is acceptable.
4. Use the matching specialist skill for the domain logic:
   - `body-sleep`
   - `body-recovery`
   - `body-composition`
   - `body-diet`
   - `body-exercise`
   - `body-medical-checkups`
5. If the question spans multiple domains, synthesize the specialist evidence into one concise answer.
6. If the question turns into a recurring-review style request, escalate to `body-cadence-review`.

## Output Contract

Ad-hoc answers should usually have these parts:

- `Answer` - direct answer to the question in one or two lines
- `Evidence` - the key numbers, trend deltas, and date window used
- `Interpretation` - what the numbers likely mean relative to goals or habits
- `Caveats` - what is missing, inferred, stale, or low-confidence
- `Next action` - only if there is an obvious action

Keep the answer compact. Prefer direct metric deltas over generic wellness language.

## Escalation Rules

Stay in `body-data-qa` when:

- the user asks one targeted question
- the comparison window is small and tightly scoped
- the output can be answered cleanly without a full ritual review
- any Streaks evidence needed is narrow and directly relevant to the question

Escalate to `body-cadence-review` when:

- the user asks for a weekly, monthly, quarterly, or yearly review
- the user wants comparisons across time periods and domains
- the answer requires checking principles, goals, habits, systems, and resources together
- the user wants recommendations prioritized across the full body area

## Data Quality Rules

- Use personal baselines over population norms unless the question is explicitly medical.
- Prefer trend windows over single-day noise.
- Mark inferred values and derived streaks as lower confidence than direct MCP fields.
- Treat Streaks as self-tracked adherence evidence, not as a replacement for sensor data.
- If a connector is missing, continue with the available evidence and say exactly what is unavailable.
- If recommendations depend on local documents in `400 Resources/`, cite the file that informed them.

## Resources

When the question needs local context, search `400 Resources/` and prioritize:

1. recent body protocols and checklists
2. medical documents and lab history
3. training or nutrition notes
4. any file directly linked from the area document

Search content, not just filenames.

## Tone

Quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schemas

There is no single required schema for cross-domain ad-hoc Q&A.
Use the prose output contract above for synthesized answers.

Use a domain schema only when the answer is returning structured domain evidence for one specialist area:

- `../../schemas/sleep.json`
- `../../schemas/recovery.json`
- `../../schemas/body-composition.json`
- `../../schemas/diet.json`
- `../../schemas/exercise.json`
- `../../schemas/medical-checkups.json`
