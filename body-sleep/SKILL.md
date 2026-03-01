---
name: body-sleep
description: Analyze sleep data from Oura Ring. Trigger on: sleep, HRV, deep sleep, REM, sleep score, sleep efficiency, "how did I sleep", bedtime, wake time, sleep latency, restfulness, respiratory rate, temperature deviation, or any sleep-related question.
---

# Body — Sleep

Analyze sleep data from Oura Ring on demand.

## MCP Server

oura-mcp — pull sleep data including: score, stages (deep/rem/light/awake
durations + percentages), efficiency, HRV avg, lowest HR, avg HR, bedtime,
wake time, latency, temp delta, respiratory rate, restfulness.

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Compare current data against sleep goals and flag progress or regression.

## Analysis

- Pull today (or requested date) from oura-mcp
- For trends, pull last 7-14 days and compare
- Prioritize HRV, deep sleep %, and efficiency over total hours
- Flag deviations > 1 SD from recent personal baseline
- Directional language:V trending up 8% over 14 days"
- Personal baselines only, never population averages
- Cross-reference with body-recovery skill when training impact is relevant

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

Reference schemas/sleep.json for field definitions.
