# Alex Life Marketplace (Claude Plugins)

Personal Claude plugin marketplace for life areas: sleep, recovery, body composition, diet, and holistic overview.

This repository is now structured as a proper Claude plugin marketplace:
- A root marketplace manifest at `.claude-plugin/marketplace.json`
- One plugin package per life area under `plugins/<plugin-name>`
- Each plugin package includes its own `.claude-plugin/plugin.json`
- Skills live inside each plugin package under `skills/**/SKILL.md`

## Plugin Catalog

1. `body-sleep` — Oura sleep quality and trend analysis
2. `body-recovery` — Oura + Garmin readiness/training recommendations
3. `body-composition` — Withings composition trends with Garmin context
4. `body-diet` — Yazio macro, calorie, hydration, and adherence analysis
5. `body-overview` — Cross-domain synthesis across all body signals

## Correct Marketplace Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    ├── body-sleep/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/body-sleep/SKILL.md
    │   └── schemas/sleep.json
    ├── body-recovery/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/body-recovery/SKILL.md
    │   └── schemas/recovery.json
    ├── body-composition/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/body-composition/SKILL.md
    │   └── schemas/body-composition.json
    ├── body-diet/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/body-diet/SKILL.md
    │   └── schemas/diet.json
    └── body-overview/
        ├── .claude-plugin/plugin.json
        ├── skills/body-overview/SKILL.md
        └── schemas/
            ├── sleep.json
            ├── recovery.json
            ├── body-composition.json
            └── diet.json
```

## Why This Fixes Discover/Install Behavior

Previously, the repository acted like a skill folder catalog, so Claude surfaced only individual skills.

Now each life area is a real plugin package with a plugin manifest, and the root manifest is a real marketplace index. This is what plugin Discover/Install expects.

## Install Flow

1. Add this repository as a marketplace in Claude plugin settings.
2. Open the marketplace in Discover.
3. Install plugins by life area (`body-sleep`, `body-recovery`, etc.).
4. Ensure required MCP servers are connected before using each plugin.

## MCP Dependencies by Plugin

- `body-sleep`: `oura-mcp`
- `body-recovery`: `oura-mcp`, `garmin-mcp`
- `body-composition`: `withings-mcp`, `garmin-mcp`
- `body-diet`: `yazio-mcp`
- `body-overview`: `oura-mcp`, `garmin-mcp`, `withings-mcp`, `yazio-mcp`

## Add a New Plugin (Proper Way)

1. Create `plugins/<new-plugin>/`.
2. Add `.claude-plugin/plugin.json`.
3. Add at least one skill file at `skills/<skill-name>/SKILL.md`.
4. Add any schemas needed under `schemas/`.
5. Register the plugin in `.claude-plugin/marketplace.json` with:
   - `name`
   - `description`
   - `version`
   - local `source` path
   - `strict` flag
6. Validate all referenced paths exist before install.

## Legacy Format Notice

The old root `marketplace.json` (custom object-based format) has been removed to avoid ambiguity with the Claude marketplace format.

