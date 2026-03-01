# Alex Life Marketplace

Personal Claude plugin marketplace for life-area automation.

Current implementation includes one plugin (`body`), and the repository is designed
to scale to additional life-area plugins over time (for example work, finance,
relationships, learning) without restructuring.

## Marketplace Model

- Root marketplace manifest: `.claude-plugin/marketplace.json`
- Plugin packages live under `plugins/<area>/`
- Each plugin owns:
  - `.claude-plugin/plugin.json`
  - `skills/**/SKILL.md`
  - `schemas/*.json` (optional but recommended)

## Current Plugins

- `body` (implemented now)

## Future Plugin Model

When you add more life areas, each should be an independent plugin package:

- `plugins/work/`
- `plugins/finance/`
- `plugins/relationships/`
- `plugins/learning/`

No new plugin is created automatically; this README defines the convention only.

## Current Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── body/
        ├── .claude-plugin/plugin.json
        ├── skills/
        │   ├── body-sleep/SKILL.md
        │   ├── body-recovery/SKILL.md
        │   ├── body-composition/SKILL.md
        │   ├── body-diet/SKILL.md
        │   ├── body-overview/SKILL.md
        │   ├── body-exercise/SKILL.md
        │   └── body-medical-checkups/SKILL.md
        └── schemas/
            ├── sleep.json
            ├── recovery.json
            ├── body-composition.json
            ├── diet.json
            ├── exercise.json
            └── medical-checkups.json
```

## Obsidian Local Setup (Safe Guidance)

This repository does not ship private vault prompt templates anymore.
Keep your vault-specific `CLAUDE.md` files private in your Obsidian vault and do
not commit them here.

Recommended reset flow for legacy setups:

```bash
cd "<VAULT_PATH>"
cp -R .claude ".claude.backup.$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
rm -rf .claude
mkdir -p .claude
```

Then in Claude plugin UI:
1. `Plugins -> Marketplaces`
2. Add this repository as marketplace
3. Open `Discover`
4. Install required plugin(s) (currently `body`)

## Internal Skill Routing Matrix (`body`)

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `body-sleep` | `oura-mcp` | sleep quality, HRV, deep/REM, sleep efficiency | Uses personal baselines and 7-14 day trend context |
| `body-recovery` | `oura-mcp`, `garmin-mcp` | readiness, train/rest today, load management | Applies recommendation rules and resolves conflicts conservatively |
| `body-composition` | `withings-mcp`, `garmin-mcp` | weight/fat/muscle trends | Emphasizes 14-30 day trends over day-level noise |
| `body-diet` | `yazio-mcp` | calories/macros/protein/hydration adherence | Computes adherence, consistency, risk flags |
| `body-overview` | all body MCPs | holistic summary, overall status | Cross-correlates all domains and highlights top priority |
| `body-exercise` | `garmin-mcp` | training consistency, volume progression, habit execution | Evaluates frequency/load consistency against habits |
| `body-medical-checkups` | resources-first (+ optional MCP context) | checkup cadence, LDL/HDL tracking, lab follow-ups | Tracks recency and key markers from medical documents |

## Daily Operator Checklist

1. Confirm legacy `.claude/skills` clone mode is absent.
2. Confirm required marketplace plugin(s) are installed and enabled.
3. Confirm MCP connectors are online for the question scope.
4. Route question to correct internal skill (or overview skill for cross-domain).
5. If a source is missing, continue with lower confidence and explicit caveats.
6. Cite relevant files from your local `400 Resources/` when used.

## Add a New Life-Area Plugin

1. Create `plugins/<area>/`.
2. Add `plugins/<area>/.claude-plugin/plugin.json`.
3. Add at least one skill file in `plugins/<area>/skills/<area>-<domain>/SKILL.md`.
4. Add schemas under `plugins/<area>/schemas/` as needed.
5. Register plugin in `.claude-plugin/marketplace.json` under `plugins[]`.
6. Validate:
   - plugin manifest path exists
   - skill paths resolve
   - schema references are valid
   - marketplace entry points to the right `source`
   - plugin appears in Discover after marketplace refresh

## Additional Authoring Guide

See `docs/plugin-authoring.md` for conventions and pre-publish checks.

