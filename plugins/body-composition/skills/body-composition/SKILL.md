---
name: body-composition
description: Analyze body composition data from Withings scale in context of Garmin training data. Trigger on: weight, body fat, muscle mass, BMI, bone mass, water percentage, body composition, recomposition, "how much do I weigh", body trends, or any question about body measurements.
---

# Body — Composition

Analyze body composition from Withings, contextualized by Garmin training data.

## MCP Servers

- withings-mcp — weight kg, body fat %, muscle mass kg, bone mass kg,
  water %, BMI
- garmin-mcp — training load, workout history (for context)

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Compare current measurements against composition goals and flag progress.

## Analysis

- Pull latest measurement from withings-mcp
- For trends, pull last 14-30 days
- Focus on trend lines, not individual measurements — single-day weight fluctuations are noise
- Contextualize with Garmin training volume: is training supporting recomposition?
- Track: gaining muscle while losing fat? Weight stable but composition improving?
- Flag when trends move away from goals

## Resources

Before giving recommendations, search 400 Resources/ for relevant material:
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
