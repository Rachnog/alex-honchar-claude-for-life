# Alex's AI Plugin Marketplace (Claude Code)

Personal plugin marketplace for a personal-life AI agent system focused on Claude Code workflows.

This repository currently packages health-focused skills that combine wearable data from multiple MCP servers and apply consistent analysis logic (sleep, recovery, composition, and cross-domain overview).

## Why This Exists

- Keep personal AI capabilities modular instead of writing one large prompt.
- Reuse structured skills across sessions in Claude Code.
- Define explicit MCP dependencies per plugin.
- Standardize output quality with consistent tone, analysis steps, and schema references.

## Current Version

- Marketplace: `0.2.0`
- Plugins: `4` (`0.1.0` each)

Source of truth: `marketplace.json`

## Plugin Catalog

### 1) `body-sleep`
- Focus: Oura sleep analysis (sleep quality, HRV, stages, efficiency)
- MCP dependencies: `oura-mcp`
- Schema: `body-sleep/schemas/sleep.json`
- Typical prompts:
  - "How did I sleep?"
  - "Analyze my HRV trend"
  - "Why is my deep sleep down?"

### 2) `body-recovery`
- Focus: Training readiness using Oura + Garmin
- MCP dependencies: `oura-mcp`, `garmin-mcp`
- Schema: `body-recovery/schemas/recovery.json`
- Typical prompts:
  - "Should I train today?"
  - "Am I recovered?"
  - "Is my training load too high?"

### 3) `body-composition`
- Focus: Weight/body composition trends, contextualized by training
- MCP dependencies: `withings-mcp`, `garmin-mcp`
- Schema: `body-composition/schemas/body-composition.json`
- Typical prompts:
  - "How is my body fat trending?"
  - "Am I recomposing or just losing weight?"
  - "Show 30-day composition trend"

### 4) `body-overview`
- Focus: Holistic cross-domain analysis (sleep + recovery + composition)
- MCP dependencies: `oura-mcp`, `garmin-mcp`, `withings-mcp`
- Schema references:
  - `body-sleep/schemas/sleep.json`
  - `body-recovery/schemas/recovery.json`
  - `body-composition/schemas/body-composition.json`
- Typical prompts:
  - "Full body report"
  - "Overall health weekly summary"
  - "How am I doing overall?"

## How Plugins Are Designed

Each plugin uses a consistent internal structure:

- `SKILL.md` defines:
  - Trigger intents and scope
  - Required MCP server(s)
  - Analysis logic and decision rules
  - Goal alignment behavior
  - Tone ("numbers first, brief context, no fluff")
  - Schema linkage
- `schemas/*.json` provides expected field contracts for outputs/analysis inputs.

This makes each plugin easier to maintain, test, and evolve independently.

## Repository Structure

```text
.
├── marketplace.json
├── body-sleep/
│   ├── SKILL.md
│   └── schemas/
│       └── sleep.json
├── body-recovery/
│   ├── SKILL.md
│   └── schemas/
│       └── recovery.json
├── body-composition/
│   ├── SKILL.md
│   └── schemas/
│       └── body-composition.json
└── body-overview/
    ├── SKILL.md
    └── schemas/
        └── .gitkeep
```

## Runtime Dependencies

Declared per plugin in `marketplace.json` via `mcp_deps`.

Expected MCP integrations:
- `oura-mcp`
- `garmin-mcp`
- `withings-mcp`

Before using a plugin, make sure required MCP servers are enabled and reachable in your Claude Code environment.

## Notes from the Current Analysis

- Marketplace metadata is clear and minimal; plugin definitions are clean.
- Skill prompts are practical and specialized around real use-cases.
- Cross-plugin composition is intentional:
  - `body-recovery` references sleep impact logic.
  - `body-overview` unifies all three domains.
- `body-overview/schemas/` currently has no dedicated schema file (only `.gitkeep`), which is acceptable because it references sibling schemas, but adding an explicit overview schema would make downstream validation easier.

## Add a New Plugin

1. Create a new folder (for example, `body-nutrition/`).
2. Add `SKILL.md` with:
   - clear trigger phrases
   - MCP server dependencies
   - goals section
   - analysis rules
   - tone and output expectations
3. Add `schemas/<plugin>.json` with expected fields.
4. Register the plugin in `marketplace.json` under `plugins`:
   - version
   - `mcp_deps`
5. Validate naming consistency between folder, marketplace key, and schema references.

## Near-Term Improvements

- Add an explicit `body-overview` schema for holistic outputs.
- Add lightweight validation scripts to check:
  - every plugin has `SKILL.md`
  - every referenced schema path exists
  - every marketplace plugin folder exists
- Add example prompt/response fixtures for regression testing quality.

## License

No license file is currently present. Add one if you plan to share this marketplace publicly.

