---
name: body-recovery
description: Analyze recovery and training readiness by combining Oura Ring readiness with Garmin training data. Trigger on: recovery, readiness, "should I train today", training load, training status, overtraining, rest day, body battery, stress, "am I recovered", or any question about training readiness.
---

# Body — Recovery

Combine Oura readiness with Garmin training signals to assess recovery
and recommend training intensity.

## MCP Servers

- oura-mcp — readiness score, contributors (HRV balance, body temp,
  recovery index, resting HR, previous night, sleep balance)
- garmin-mcp — training status (Productive/Maintaining/Recovery/Unproductive),
  7d training load, recovery time hrs, body battery start/end, avg stress

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Compare against training and recovery goals.

## Analysis

Pull readiness from oura-mcp and training status from garmin-mcp, then:

**Recommendation logic:**
- Readiness >= 85 AND recovery_time = 0 -> high intensity ok
- Readiness 70-84 OR recovery_time <= 12 -> moderate ok
- Readiness 50-69 OR recovery_time 12-24 -> light only
- Readiness < 50 OR recovery_time > 24 -> rest day
- When Oura and Garmin disagree -> default to the more conservative one

**Sleep-training impact** (cross-reference body-sleep):
- How yesterday's training affected last night's HRV and deep sleep
- Pull multiple days if needed to show the pattern

For trend questions, pull 7-14 days of data.

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

Reference ../../schemas/recovery.json for field definitions.
