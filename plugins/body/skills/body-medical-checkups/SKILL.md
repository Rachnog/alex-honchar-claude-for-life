---
name: body-medical-checkups
description: Track medical checkup cadence and interpret key blood marker progress (especially LDL/HDL) from local documents. Trigger on: medical checkup, bloodwork, LDL, HDL, labs, health panel, preventative care, "when should I do checkups", or any question about medical baseline tracking.
---

# Body — Medical Checkups

Track medical checkup regularity and key marker direction using local medical
documents and explicit targets.

## Data Sources

- 400 Resources/ medical documents (primary)
- optional MCP context from other body systems for trend interpretation

## Goals

Read goals from 300 Areas/Body/CLAUDE.md before every analysis.
Prioritize:
- regular checkup cadence as a core pillar
- LDL/HDL movement toward healthy reference ranges

## Analysis

- Search medical files in 400 Resources/ for recent labs/checkup reports
- Extract latest available checkup date and major lipid markers (LDL/HDL)
- Compare current markers against previously documented values when available
- Flag missing or stale checkup cadence
- Recommend next follow-up window based on recency and risk signals
- Explicitly separate:
  - data-backed observations
  - assumptions from incomplete medical documents

## Resources

Always cite which resource file(s) informed conclusions.
If no recent medical documents are found, say this explicitly and propose
the minimum next step (for example: schedule checkup, upload latest panel).

## Tone

Quant analyst reviewing a dashboard. Numbers first, brief context, no fluff.

## Schema

Reference ../../schemas/medical-checkups.json for field definitions.
