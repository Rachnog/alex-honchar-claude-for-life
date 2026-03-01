---
name: body
description: Pull and analyze wearable health data from Oura Ring, Garmin Fenix 7, and Withings scale. Trigger on: sleep, HRV, readiness, training load, body composition, weight, body fat, recovery, Oura, Garmin, Withings, "sync body", "how did I sleep", "am I recovered", "body composition update", "should I train today", or any health/fitness query about personal data.
---

# Body Plugin

Pull health data from wearable MCPs on demand, analyze in-memory,
answer questions. Nothing is written to the vault.

## MCP Servers

| Server | Device | Data |
|--------|--------|------|
| oura-mcp | Oura Ring | sleep score, stages, HRV, readiness, activity |
| garmin-mcp | Garmin Fenix 7 | training load, VO2max, steps, workouts, body battery |
| withings-mcp | Withings scale | weight, body fat %, muscle mass, BMI |

## What To Pull

**From oura-mcp:**
- Sleep: score, stages (deep/rem/light/awake durations + %), efficiency,
  HRV avg, lowest HR, bedtime/wake, latency, temp delta
- Readiness: score, contributors (HRV balance, body temp, recovery index,
  resting HR, previous night, sleep balance)
- Activity: activity score, steps, calories

**From garmin-mcp:**
- Daily: steps, active calories, training load, VO2max, intensity minutes,
  body battery start/end, stress avg
- Workouts: name, duration, distance, avg/max HR, calories,
  training effect aerobic/anaerobic
- Status: training status (Productive/Maintaining/Recovery/Unproductive),
  7d load, recovery time hrs

**From withings-mcp:**
- Latest measurement: weight kg, body fat %, muscle mass kg, bone mass,
  water %, BMI

## Goals

Read goals from 300 Areas/Body/CLAUDE.md in the vault before every analysis.
Always compare current data against these goals and flag progress or regression.

## Correlations To Run

When analyzing data, always look for these cross-device signals:

**Recovery assessment** (Oura x Garmin):
- Combine readiness score with training status and recovery time
- Recommendation logic:
  - Readiness >= 85 AND recovery_time = 0 -> high intensity ok
  - Readiness 70-84 OR recovery_time <= 12 -> moderate ok
  - Readiness 50-69 OR recovery_time 12-24 -> light only
  - Readiness < 50 OR recovery_time > 24 -> rest day
- When Oura and Garmin disagree -> default to the more conservative one

**Sleep-training impact** (Garmin -> Oura):
- How yesterday's training intensity affected last night's HRV and deep sleep
- Pull multiple days if needed to show the pattern

**Body recomposition** (Withings + Garmin):
- Weight, fat %, muscle mass trends contextualized by training volume
- Are you gaining muscle while losing fat? Is training volume supporting the trend?

## Analysis Style

- HRV, deep sleep %, efficiency matter more than total hours
- Directional: "HRV trending up 8% over 14 days" not "HRV is 45ms"
- Personal baselines only, never population averages
- Body composition: trend line, not individual measurements
- When data seems off -> flag it, don't silently use it
- Tone: quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schemas

Reference schemas/ relative to this skill for field definitions:
- sleep.json — Oura sleep fields
- activity.json — Garmin + Oura activity fields
- body-composition.json — Withings fields
- recovery.json — Combined recovery assessment fields
