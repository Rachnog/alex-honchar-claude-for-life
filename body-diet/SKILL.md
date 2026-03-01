---
name: body-diet
description: Analyze diet and nutrition data from Yazio. Trigger on: calories, macros, protein, carbs, fat, hydration, meal logs, nutrition trends, food logging consistency, "how did I eat", "diet analysis", "nutrition summary", "calorie target", or any question about diet quality and adherence.
---

# Body — Diet

Analyze nutrition data from Yazio and assess adherence to calorie, macro, and hydration goals.

## MCP Server

yazio-mcp — pull user goals, daily summary, consumed items, water intake, exercises, and weight entries.

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Compare nutrition behavior against diet and body composition goals.

## Analysis

- Pull today (or requested date) from yazio-mcp
- For trends, pull last 7-14 days (30 days when requested)
- Calculate adherence against goals:
  - energy_kcal consumed vs target
  - protein_g, carb_g, fat_g consumed vs targets
  - water_ml consumed vs target
- Analyze meal distribution across breakfast/lunch/dinner/snack
- Flag high day-to-day calorie variance and repeated macro under-target patterns
- Track logging consistency using consumed-item presence per day
- If explicit streak is unavailable, derive a streak proxy from consecutive logged days
- Mark inferred metrics with lower confidence than direct MCP fields
- Prioritize protein and consistency adherence for recomposition-oriented goals
- Cross-reference with body-recovery and body-composition when training or physique context is relevant

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

Reference schemas/diet.json for field definitions.
