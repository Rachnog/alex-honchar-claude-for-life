# Plugin Authoring Conventions

This document defines conventions for adding future life-area plugins to this marketplace.

## 1) Naming Conventions

- Plugin folder: `plugins/<area>/`
- Plugin name in manifest: `<area>`
- Internal skill name: `<area>-<domain>`
- Skill folder: `plugins/<area>/skills/<area>-<domain>/`
- Skill file: `plugins/<area>/skills/<area>-<domain>/SKILL.md`

Examples:
- `plugins/body/skills/body-sleep/SKILL.md`
- `plugins/finance/skills/finance-cashflow/SKILL.md`

## 2) Required Plugin Layout

Each plugin should follow:

```text
plugins/<area>/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── <area>-<domain>/
│       └── SKILL.md
└── schemas/
    └── *.json
```

Notes:
- `schemas/` is optional but recommended for structured outputs.
- Keep plugin-local schema references relative to skill files.

## 3) Manifest Expectations

### Marketplace entry (`.claude-plugin/marketplace.json`)

For each plugin entry in `plugins[]`:
- `name`
- `description`
- `version` (semver-like)
- `source` (for example `./plugins/<area>`)
- `strict` (recommended `true`)

### Plugin manifest (`plugins/<area>/.claude-plugin/plugin.json`)

Recommended fields:
- `name`
- `description`
- `version`
- `author`
- `keywords`

## 4) Skill Authoring Expectations

Each `SKILL.md` should include:
- frontmatter with `name` and `description`
- scope and trigger guidance
- required MCP server(s) for the skill
- goal-file behavior (if area uses goal docs)
- data-quality caveats when sources can be missing
- schema reference when applicable

## 5) MCP Dependency Guidance

MCP dependencies are documented in skill files and README matrices.
When adding new plugins:
- list required MCP servers in each skill clearly
- keep server names consistent across docs
- define fallback behavior for missing connectors

## 6) Versioning Guidance

- Bump plugin `version` for plugin-specific changes.
- Bump marketplace metadata version when plugin catalog changes.
- Use concise commit messages explaining why behavior changed.

## 7) Pre-Publish Validation Checklist

Before publishing/updating marketplace:

1. `plugins/<area>/.claude-plugin/plugin.json` exists.
2. At least one `skills/**/SKILL.md` exists.
3. Marketplace `plugins[]` entry points to valid `source`.
4. Referenced schema files exist.
5. README documents:
   - current plugins
   - setup flow
   - any new routing/usage behavior
6. Plugin appears in Discover after marketplace refresh.

## 8) Privacy Rule

Do not commit private vault prompt files or personal templates.
Keep vault-specific `CLAUDE.md` files in your private Obsidian vault only.
