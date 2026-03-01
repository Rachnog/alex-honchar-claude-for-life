# Alex Life Marketplace (Single `body` Plugin)

This repository provides one installable Claude plugin named `body`.
Inside this single plugin are multiple specialized skills for body-domain analysis.

## Plugin Model

- Marketplace manifest: `.claude-plugin/marketplace.json`
- Single plugin package: `plugins/body/`
- Plugin manifest: `plugins/body/.claude-plugin/plugin.json`
- Multiple skills inside one plugin: `plugins/body/skills/**/SKILL.md`
- Shared schemas: `plugins/body/schemas/*.json`

## Internal Skills in `body`

1. `body-sleep`
2. `body-recovery`
3. `body-composition`
4. `body-diet`
5. `body-overview`
6. `body-exercise`
7. `body-medical-checkups`

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

## Obsidian Local Agent Setup (Separate Vault)

### Step 0: Clean reset legacy `.claude` state

Run in your vault root (replace `<VAULT_PATH>`):

```bash
cd "<VAULT_PATH>"

# Backup old local agent state
cp -R .claude ".claude.backup.$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true

# Remove old state to avoid legacy skill discovery conflicts
rm -rf .claude

# Optional baseline folder (tools may recreate this automatically)
mkdir -p .claude
```

### Step 1: Add marketplace

In Claude plugin UI:
1. Open `Plugins` -> `Marketplaces`
2. Add this repository as a marketplace
3. Open `Discover`

### Step 2: Install single plugin

Install only:
- `body`

### Step 3: Apply vault prompts

Copy full templates from:
- `templates/obsidian/CLAUDE.md`
- `templates/obsidian/300 Areas/Body/CLAUDE.md`

### Step 4: Verify MCP connectivity

Before analysis, confirm:
- `oura`
- `garmin`
- `withings`
- `yazio`

## Internal Skill Routing Matrix

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
2. Confirm `body` plugin is installed and enabled.
3. Confirm MCP connectors are online.
4. Route question to proper internal skill (or `body-overview` for cross-domain).
5. If a source is missing, continue with lower confidence and explicit caveats.
6. Cite relevant files from `400 Resources/` when used.

## Vault Prompt Templates

- `templates/obsidian/CLAUDE.md`
- `templates/obsidian/300 Areas/Body/CLAUDE.md`

## Why this works

Discover now shows one installable plugin (`body`) instead of multiple per-area plugins.
That plugin then exposes multiple specialized internal skills, matching the intended architecture.

