---
name: body-exercise
description: Analyze exercise consistency, training progression, and workload management from Garmin. Trigger on: exercise, workout plan, gym consistency, training volume, training frequency, cardio, strength progress, mobility, "am I training enough", or any question about training habits and execution.
---

# Body — Exercise

Analyze exercise behavior and training consistency with a focus on execution
against defined habits and systems.

## MCP Server

garmin-mcp — pull workout history, training load, training status, steps,
activity sessions, and related performance signals.

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Prioritize alignment with:
- gym 4x+ per week habit
- strength/cardio/mobility balance
- sustainable progression over intensity spikes

## Analysis

- Pull current week and last 4 weeks from garmin-mcp
- Evaluate session frequency against weekly habit target
- Compare recent load vs historical baseline to flag over/under-loading
- Assess pattern consistency (missed streaks, irregular session timing)
- Distinguish volume progress from random single hard sessions
- Correlate training pattern with sleep/recovery context when relevant
- For planning questions, recommend next 7 days intensity mix:
  - hard / moderate / light / rest distribution

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

Reference ../../schemas/exercise.json for field definitions.
