---
name: body-overview
description: Full-picture health analysis combining all wearable data sources. Trigger on: "full body report", "overall health", "weekly summary", "how am I doing", "sync body", "body overview", "health dashboard", or any broad health question that spans sleep, recovery, and body composition.
---

# Body — Overview

Full-picture analysis combining data from all three wearable devices.
Use this when the question spans multiple domains or asks for a holistic view.

## MCP Servers

- oura-mcp — sleep, readiness, HRV, activity
- garmin-mcp — training load, VO2max, steps, workouts, body battery
- withings-mcp — weight, body fat %, muscle mass, BMI

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Compare all data against all goals. Flag overall progress and regressions.

## Analysis

Pull from all three MCPs and cross-correlate:

**Recovery vs training:**
- Is training load aligned with recovery capacity?
-  days happening when readiness is low?

**Sleep vs training:**
- How is training intensity affecting HRV and deep sleep trends?
- Any pattern of declining sleep quality with increased load?

**Composition vs training:**
- Is training volume supporting body recomposition goals?
- Are weight/fat/muscle trends moving in the right direction?

**Overall trajectory:**
- Are all signals aligned toward goals or are there conflicts?
- What's the single most important thing to address right now?

For trends, pull 7-14 days minimum from each source.

## Resources

Before giving recommendations, search 400 Resources/ for relevant material:
1. Use find and grep to locate files related to the current query
2. Read .md and .txt files directly
3. For PDFs, extract text and scan for relevant sections
4. For Excel files, read and parse relevant sheets
5. Prioritize newer files over older ones
6. Cite which resource informed your recommendation

Search broadly — file names may not be descriptive. Look at actual content.

##one

Quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schemas

Reference schemas from sibling skill folders for field definitions:
- body-sleep/schemas/sleep.json
- body-recovery/schemas/recovery.json
- body-composition/schemas/body-composition.json
