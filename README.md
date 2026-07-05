# Alex Life Marketplace

Personal Claude plugin marketplace for life-area automation.

Current implementation includes active plugins (`body`, `mind`, `work`, `lifestyle`,
`relationships`), and the repository is designed to scale to additional life-area plugins
over time (for example finance, learning) without restructuring.

## Marketplace Model

- Root marketplace manifest: `.claude-plugin/marketplace.json`
- Plugin packages live under `plugins/<area>/`
- Each plugin owns:
  - `.claude-plugin/plugin.json`
  - `skills/**/SKILL.md`
  - `schemas/*.json` (optional but recommended)

## Current Plugins

- `body` — physical health workflows for ad-hoc data Q&A and structured cadence reviews
- `mind` — habit reflection (Streaks), bidirectional Notion-Obsidian project/task sync
- `work` — work management workflows for email triage and productivity automation
- `lifestyle` — digital wellbeing: screen/phone balance from unified Apple Screen Time
- `relationships` — two-lens relationship reviews: a personal lens (partner + family/close friends) from local WhatsApp/call/iMessage metadata plus the Telegram MCP, and a network lens (professional network + community) from Clay/Mesh, Calendar, and Granola

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
    ├── mind/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/
    │   │   ├── streaks-export-analysis/SKILL.md
    │   │   └── mind-notion-sync/SKILL.md
    │   └── schemas/
    │       └── notion-sync.json
    └── work/
        ├── .claude-plugin/plugin.json
        └── skills/
            ├── deep-research/SKILL.md
            ├── gtd-email-triage/SKILL.md
            └── gtd-slack-triage/
                ├── SKILL.md
                ├── channel-rules.json
                ├── message-patterns.json
                └── sub-agent-prompt.md
```

## Obsidian Local Setup (Safe Guidance)

This repository does not ship private vault prompt templates anymore.
Keep your vault-specific `CLAUDE.md` files private in your Obsidian vault and do
not commit them here.

Recommended reset flow for legacy setups:

```bash
cd "<VAULT_PATH>"
# Backup MUST succeed before anything is deleted — the && chain stops if cp fails
cp -R .claude ".claude.backup.$(date +%Y%m%d-%H%M%S)" \
  && rm -rf .claude \
  && mkdir -p .claude
```

Then in Claude plugin UI:
1. `Plugins -> Marketplaces`
2. Add this repository as marketplace
3. Open `Discover`
4. Install required plugin(s) for your use case (`body`, `work`)

## Internal Skill Routing Matrix (`mind`)

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `streaks-export-analysis` | local + Apple Shortcuts | "analyze Streaks export", "habits report", "monthly Streaks review" | Turns a Streaks `.streaks` export into a markdown habits report |
| `mind-notion-sync` | `notion` (Claude AI Notion MCP) | "sync Notion", "pull from Notion", "push to Notion", "update projects" | Bidirectional sync of Projects & Tasks between Notion and Obsidian `200 Projects/` |
| `weekly-review` | all life-area MCPs (Oura, Garmin, Calendar, Gmail, Slack, Notion, HubSpot, Clay, Fireflies, Streaks) | "weekly review", "do my weekly review", "life review", "review all life areas" | Top-level cross-area WEEKLY orchestrator — parallel data pulls across all 8 life areas, delegating to area specialists, into one weekly note |
| `monthly-review` | delegates to area cadence skills (+ Clay/Calendar/HubSpot/Notion inline) | "monthly review", "do my monthly review", "month in review", "close out the month", "[month] review" | Top-level cross-area MONTHLY orchestrator — consolidation-first: reads/generates each area's monthly review, then synthesizes into one monthly note with cross-area correlations |

## Internal Skill Routing Matrix (`relationships`)

| Internal skill | MCP servers | Typical trigger classes | Behavior |
|---|---|---|---|
| `relationships-personal-review` | local extractor (WhatsApp/calls/iMessage) + `telegram` (read-only) + `google-calendar` + `clay` (roster only) | "am I neglecting my family/partner", "who am I losing touch with", personal/family/inner-circle review | Reviews the inner circle from the channels where it actually lives; reconciles Clay's stale family recency against real local/Telegram contact |
| `relationships-network-review` | `clay` + `google-calendar` + `granola` | network review, "who owes a follow-up", "who am I letting go cold", community engagement | Reviews the professional network + community: network-target progress, overdue follow-ups, new connections, dormant-but-important contacts |

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

