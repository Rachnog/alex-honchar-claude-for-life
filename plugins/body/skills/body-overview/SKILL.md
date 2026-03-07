---
name: body-overview
description: Legacy compatibility entrypoint only for explicit old wording such as "body overview", "full body report", or "health dashboard". Route those requests to `body-data-qa` for ad-hoc synthesis or `body-cadence-review` for structured weekly, monthly, quarterly, or yearly reviews.
---

# Body - Overview

This skill exists for compatibility with the older domain-first routing model.
It should not be the main long-term workflow surface.
Do not use it for ordinary broad body questions unless the user explicitly uses this older wording.

Use it to route broad requests:

- ad-hoc broad question -> `body-data-qa`
- ritualized weekly/monthly/quarterly/yearly review -> `body-cadence-review`

Do not duplicate synthesis logic here. Route first, then let the downstream workflow pull data, read goals, and search resources.

## Downstream Workflows

- `body-data-qa` for default ad-hoc body questions
- `body-cadence-review` for structured reviews and period comparisons

## Routing Logic

Choose the target workflow before doing heavy analysis.

Route to `body-data-qa` when:

- the user asks a broad but still targeted question
- the user wants a current snapshot or a quick comparison
- the request does not require a formal cadence review

Route to `body-cadence-review` when:

- the user asks for a weekly, monthly, quarterly, or yearly review
- the request explicitly compares periods
- the answer requires checking systems, habits, goals, principles, and resources together

## Specialist Inputs

Both workflows should rely on specialist domain evidence from:

- `body-sleep`
- `body-recovery`
- `body-composition`
- `body-diet`
- `body-exercise`
- `body-medical-checkups`

This skill should avoid duplicating specialist logic.

## Tone

Routing layer only. Be brief and decisive.

## Schemas

Compatibility wrapper only. Prefer the downstream workflow schema rules:
- `body-data-qa` -> no single schema for synthesized ad-hoc answers; use a domain schema only when returning structured domain evidence
- `body-cadence-review` -> `../../schemas/cadence-review.json`
