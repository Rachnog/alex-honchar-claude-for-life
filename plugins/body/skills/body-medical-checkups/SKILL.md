---
name: body-medical-checkups
description: Provide specialist medical checkup and lab-tracking evidence from local documents when `body-data-qa` or `body-cadence-review` needs medical-domain depth, or when the user explicitly asks for a medical-tracking-only deep dive.
---

# Body - Medical Checkups

Track medical checkup regularity and key marker direction using local medical
documents and explicit targets.
Use this as the medical specialist inside the body system.
The default top-level entrypoint for normal questions is `body-data-qa`. This skill should mostly support the workflow skills unless the user explicitly wants medical-only depth.

## Data Sources

- 400 Resources/ medical documents (primary)
- optional MCP context from other body systems for trend interpretation

## Goals

Use the same reasoning order as the workflow skills:

1. Read the guiding principles and strategy in `000 OS/` when available.
2. Identify the relevant body systems and targets in the OS systems/targets document.
3. Read the relevant body area guidance in `300 Areas/Body/`.
4. Then prioritize:
- regular checkup cadence as a core pillar
- LDL/HDL movement toward healthy reference ranges

## Analysis

- Search medical files in `400 Resources/` for recent labs and checkup reports.
- Extract the latest available checkup date and major lipid markers such as LDL and HDL.
- Compare current markers against previously documented values when available.
- Flag stale or missing checkup cadence.
- Recommend the next follow-up window based on recency and risk signals.
- Explicitly separate:
  - data-backed observations
  - assumptions from incomplete medical documents

## Output Contract

If structured output is needed, keep the metric payload aligned with `../../schemas/medical-checkups.json`.
Present the findings in prose under this shape:

- `Current medical snapshot` - latest labs or checkup recency
- `Trend` - how key markers changed versus prior documented results
- `Follow-up urgency` - low, medium, or high with rationale
- `Goal alignment` - whether markers and cadence support the stated body targets
- `Caveats` - stale documents, missing labs, unreadable values, or incomplete history

## Escalation Rules

Stay in `body-medical-checkups` when the user explicitly wants medical-only depth or when an upstream workflow already scoped the task to checkups, labs, or follow-up planning.

Escalate to:

- `body-data-qa` when the user asks for ad-hoc cross-domain comparison involving medical data
- `body-cadence-review` when the medical picture is one part of a larger body review

## Resources

When invoked from `body-data-qa` or `body-cadence-review`, let the upstream workflow own broader recommendation synthesis.
If this specialist is being used directly for a medical-only deep dive, always cite which resource file(s) informed conclusions.
If no recent medical documents are found, say this explicitly and propose
the minimum next step (for example: schedule checkup, upload latest panel).

## Tone

Quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schema

Reference ../../schemas/medical-checkups.json for field definitions.
