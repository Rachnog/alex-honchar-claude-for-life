---
name: soul-correlation
description: Cross-correlate journal sentiment with body device data (Oura sleep/readiness/stress, Garmin activity). Trigger on: "mood vs sleep", "journal correlation", "does sleep affect mood", "sentiment trends", "stress correlation", "journal vs device", "subjective vs objective", or any question linking inner state to biometric data.
---

## MCP Servers

- `remarkable` — journal images (via soul-journal process)
- `oura-mcp` — sleep score, readiness score, daily stress, activity score
- `garmin-mcp` — activities list, training load (for exercise correlation)

## Goals

Read both `300 Areas/Shadow and Soul/CLAUDE.md` and `300 Areas/Body/CLAUDE.md`.

## Analysis

1. **Collect journal data**: Use soul-journal process to get dated, sentiment-tagged entries for the requested period.

2. **Pull device data for same period**:
   - Oura: `get_daily_sleep`, `get_daily_readiness`, `get_daily_stress`, `get_daily_activity`
   - Garmin: `get_activities` (optional, for exercise-mood link)

3. **Build correlation table**: Date | Sentiment | Sleep Score | Readiness | Stress Class | Activity Score.

4. **Analyze patterns** (known patterns from Q4 2025 analysis to look for):
   - **Sleep→mood**: Sleep <60 strongly predicts negative mood. Check if this holds.
   - **Stress lag**: Oura stress classification lags journal-reported stress by ~1 day. Check `stress_high` seconds on day+1 after negative entries.
   - **Activity curve**: Neither high nor low activity alone predicts mood. Check if chosen vs forced inactivity matters.
   - **Objective-subjective gap**: Flag any case where readiness >80 but sentiment ≤2 — this indicates psychological distress that devices miss entirely.
   - **Journal absence**: Weeks with no entries but high Oura stress_high = potential overwhelm.

5. **Output**:
   - Correlation table
   - Pattern findings with specific data points as evidence
   - What devices catch vs what they miss
   - Actionable insights
   - Confidence level based on data coverage (entries/total days ratio)

## Cross-Reference with Body Plugin

Note when body-sleep, body-recovery, or body-exercise findings are relevant, but do not duplicate their analysis. Point the user to those skills for deeper body-specific dives.

## Tone

Quant analyst with empathy. Numbers first. When crisis signals appear (sentiment 1, crisis themes), note them clearly but without alarm. Recommend professional follow-up for persistent negative patterns.

## Schema

Reference `../../schemas/sentiment-correlation.json`
