# Alex Life Marketplace

Personal Claude plugin marketplace for life-area automation.

Current implementation includes two active plugins (`body`, `work`), and the
repository is designed to scale to additional life-area plugins over time (for
example work, finance, relationships, learning) without restructuring.

## Marketplace Model

- Root marketplace manifest: `.claude-plugin/marketplace.json`
- Plugin packages live under `plugins/<area>/`
- Each plugin owns:
  - `.claude-plugin/plugin.json`
  - `skills/**/SKILL.md`
  - `schemas/*.json` (optional but recommended)

## Current Plugins

- `body` — physical health workflows for ad-hoc data Q&A and structured cadence reviews
- `work` — work management workflows for email triage and productivity automation

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
    ├── body/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/
    │   │   ├── body-cadence-review/SKILL.md
    │   │   ├── body-composition/SKILL.md
    │   │   ├── body-data-qa/SKILL.md
    │   │   ├── body-diet/SKILL.md
    │   │   ├── body-overview/SKILL.md
    │   │   ├── body-exercise/SKILL.md
    │   │   ├── body-recovery/SKILL.md
    │   │   ├── body-sleep/SKILL.md
    │   │   └── body-medical-checkups/SKILL.md
    │   └── schemas/
    │       ├── cadence-review.json
    │       ├── sleep.json
    │       ├── recovery.json
    │       ├── body-composition.json
    │       ├── diet.json
    │       ├── exercise.json
    │       └── medical-checkups.json
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
4. Install required plugin(s) for your use case (`body`, `work`)

If you previously installed `shadow-and-soul`, remove or disable the stale local install after refreshing the marketplace, since it is no longer published here.

## Internal Skill Routing Matrix (`body`)

### Primary workflow skills

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `body-data-qa` | body MCPs as needed | direct questions, metric interpretation, targeted cross-checks, current status | Answers ad-hoc body questions with the minimum relevant data and specialist domain logic |
| `body-cadence-review` | all body MCPs + local resources as needed | weekly review, monthly review, quarterly review, yearly review, compare periods | Runs structured body reviews, compares periods and domains, and ties recommendations back to goals, habits, systems, and principles |

### Compatibility wrapper

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `body-overview` | delegated to workflow skills | legacy broad-body wording such as "body overview" or "full body report" | Thin compatibility wrapper that routes to `body-data-qa` or `body-cadence-review` |

### Specialist support skills

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `body-sleep` | `oura-mcp` | sleep quality, HRV, deep/REM, sleep efficiency | Produces specialist sleep evidence using personal baselines and 7-14 day context |
| `body-recovery` | `oura-mcp`, `garmin-mcp` | readiness, train/rest today, load management | Produces specialist readiness evidence and applies conservative recovery rules |
| `body-composition` | `withings-mcp`, `garmin-mcp` | weight/fat/muscle trends | Produces body-composition evidence and emphasizes 14-30 day trends over noise |
| `body-diet` | `yazio-mcp` | calories/macros/protein/hydration adherence | Produces adherence and nutrition-pattern evidence with logging-quality caveats |
| `body-exercise` | `garmin-mcp` | training consistency, volume progression, habit execution | Produces training execution evidence against stated habits and sustainable progression |
| `body-medical-checkups` | resources-first (+ optional MCP context) | checkup cadence, LDL/HDL tracking, lab follow-ups | Produces medical cadence and lab-trend evidence from local medical documents |

## Daily Operator Checklist

1. Confirm legacy `.claude/skills` clone mode is absent.
2. Confirm required marketplace plugin(s) are installed and enabled.
3. Confirm MCP connectors are online for the question scope.
4. Route first to the correct workflow skill (`body-data-qa` or `body-cadence-review`), then rely on specialist skills as needed.
5. If a source is missing, continue with lower confidence and explicit caveats.
6. Cite relevant files from your local `400 Resources/` when used.

## Add a New Life-Area Plugin

1. Create `plugins/<area>/`.
2. Add `plugins/<area>/.claude-plugin/plugin.json`.
3. Add at least one skill file in `plugins/<area>/skills/<area>-<specialty>/SKILL.md`.
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

