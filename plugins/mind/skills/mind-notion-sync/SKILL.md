---
name: mind-notion-sync
description: Bidirectional sync between Notion Projects & Tasks databases and Obsidian 200 Projects/ vault structure. Use for "sync Notion", "update projects from Notion", "push to Notion", "sync tasks", "pull from Notion", or any Notion-Obsidian project/task synchronization request.
compatibility:
  - tool: mcp__claude_ai_Notion__notion-fetch
  - tool: mcp__claude_ai_Notion__notion-search
  - tool: mcp__claude_ai_Notion__notion-update-page
  - tool: mcp__claude_ai_Notion__notion-create-pages
---

# Mind - Notion Sync

Bidirectional synchronization between Notion Projects & Tasks databases and the Obsidian `200 Projects/` vault structure.

## Core Principle

Every piece of data written to a file must come from an actual Notion API response or an actual Obsidian file read. Never invent, summarize, or fabricate content. If a fetch fails, skip the record and log it.

## When To Use

Use this skill when the user asks to:

- sync projects or tasks between Notion and Obsidian
- pull latest from Notion into Obsidian
- push Obsidian changes to Notion
- update projects from Notion
- check what changed in Notion since last sync
- create a new project/task in both systems

This skill is NOT for:

- querying Notion data without writing files (use Notion MCP directly)
- managing the Neurons Lab workspace (this skill targets the personal workspace only)

## Reasoning Order

Before syncing, load context in this order:

1. `000 OS/` — principles and strategy
2. `3 Numerical Targets 2026` — current year targets
3. `300 Areas/3 Mind/` — mind area guidance (LMS/KMS context)
4. Notion MCP — fetch live database state
5. `200 Projects/` — current vault state

## Workspace Safety

**CRITICAL**: Two Notion workspaces are connected — personal and Neurons Lab. This skill operates ONLY on the personal workspace. Before any sync operation:

1. Use `notion-search` to verify you are querying the personal workspace
2. The Projects database lives at `collection://<YOUR-PROJECTS-COLLECTION-ID>` (discover once via notion-search, then reuse)
3. The Tasks database lives at `collection://<YOUR-TASKS-COLLECTION-ID>`
4. If results include work-workspace data, filter it out

## Notion Database Schema

### Projects Database

| Notion Property | Type | Obsidian Property | YAML Type |
|-----------------|------|-------------------|-----------|
| Project name | Title | `title` + filename | text |
| Area | Select | `area` | text |
| Status | Status | `status` | text |
| Priority | Select | `priority` | text |
| Owner | Person | `owner` | text |
| Deadline | Date | `deadline` | date |
| Completion | Rollup | SKIP | — |
| Tasks | Relation | SKIP (Dataview) | — |

**Area options**: Work, Lifestyle, Society, Mind
**Status options**: Backlog, Paused, Ongoing, In Progress, On Others, Done
**Priority options**: Low, Medium, High

### Tasks Database

| Notion Property | Type | Obsidian Property | YAML Type |
|-----------------|------|-------------------|-----------|
| Task name | Title | `title` + filename | text |
| Status | Status | `status` | text |
| Priority | Select | `priority` | text |
| Task type | Select | `task-type` | text |
| Assignee | Person | `assignee` | text |
| Due | Date | `due` | date |
| Project | Relation | `project` | wikilink |
| Sub-tasks | Relation | `sub-tasks` | wikilink list |
| Parent-task | Relation | `parent-task` | wikilink |
| Project Status | Rollup | SKIP | — |

**Status options**: Backlog, Planned, In Progress, On Others, Done, Archived
**Task type options**: Low/Operational, Average/Professional, Creative/Technical, Leverage/Systems

### Status Semantics

Both "Done" and "Archived" count as completed. All Dataview queries must use:
- Active filter: `status != "Done" AND status != "Archived"`
- Completed filter: `(status = "Done" OR status = "Archived")`
- Progress count: `t.status === "Done" || t.status === "Archived"`

## Obsidian Vault Structure

```text
200 Projects/
├── _Templates/
│   ├── project-template.md
│   └── task-template.md
├── _Bases/
│   ├── Projects.base
│   └── Tasks.base
├── _Dashboard.md
├── _migration/
│   └── notion-export-raw.json
├── {Project Name}/
│   ├── {Project Name}.md
│   └── tasks/
│       └── {Task}.md
├── _Unassigned Tasks/
│   └── {Orphan Task}.md
└── Old projects notes/          ← NEVER TOUCH
```

## Workflow A — Notion → Obsidian (Pull)

Use when the user says "sync from Notion", "pull from Notion", "update from Notion".

### Step 1: Fetch all projects

Search the Projects data source for all pages:

```
mcp__claude_ai_Notion__notion-search(
  query: "projects",
  data_source_url: "collection://<YOUR-PROJECTS-COLLECTION-ID>",
  page_size: 25
)
```

Do multiple searches with different queries to ensure completeness. Then fetch each project page individually with `notion-fetch` to get full properties and body content.

### Step 2: Fetch all tasks

Same approach for the Tasks data source (`collection://<YOUR-TASKS-COLLECTION-ID>`). Additionally, collect task IDs from each project's `Tasks` relation property — this is the authoritative source for project-task associations.

Fetch EVERY task page individually with `notion-fetch`. Never skip a fetch.

### Step 3: Build lookup and resolve relations

Create a map: `{notion_page_id → title}` for all projects and tasks. Replace every relation URL/ID with the corresponding `"[[Title]]"` wikilink.

### Step 4: Determine sync actions

For each Notion record:
- If a file with matching `notion-id` exists in the vault → UPDATE the file
- If no matching file exists → CREATE a new file
- If a vault file has a `notion-id` that no longer exists in Notion → LOG as potentially deleted (do not auto-delete)

### Step 5: Write/update project files

For each project, ensure the folder exists at `200 Projects/{SanitizedName}/` with a `tasks/` subfolder. Write or update the project `.md` file with:

```markdown
---
title: "{project name}"
type: project
area: "{area}"
status: "{status}"
priority: "{priority}"
owner: "{owner}"
deadline: {YYYY-MM-DD or empty}
source: "Notion"
created: "{original created date or today}"
notion-id: "{uuid-with-dashes}"
tags:
  - project
---

# {Project Title}

{Converted Notion body content — VERBATIM, not summarized}

## Tasks

```dataview
TABLE status AS "Status", priority AS "Priority", due AS "Due", assignee AS "Assignee"
FROM "200 Projects"
WHERE type = "task" AND contains(project, this.file.link) AND status != "Done" AND status != "Archived"
SORT due ASC
```

## Completed Tasks

```dataview
TABLE due AS "Completed"
FROM "200 Projects"
WHERE type = "task" AND contains(project, this.file.link) AND (status = "Done" OR status = "Archived")
SORT due DESC
```

## Progress

```dataviewjs
let tasks = dv.pages('"200 Projects"')
  .where(t => t.type === "task" && t.project && dv.equal(t.project, dv.current().file.link));
let done = tasks.where(t => t.status === "Done" || t.status === "Archived").length;
let total = tasks.length;
let pct = total > 0 ? Math.round((done/total)*100) : 0;
dv.paragraph(`**${done}/${total} tasks complete (${pct}%)**`);
dv.paragraph(`<progress value="${done}" max="${total}" style="width:100%"></progress>`);
```
```

### Step 6: Write/update task files

For each task:
- With project → `200 Projects/{ProjectFolder}/tasks/{SanitizedTaskName}.md`
- Without project → `200 Projects/_Unassigned Tasks/{SanitizedTaskName}.md`

```markdown
---
title: "{task name}"
type: task
status: "{status}"
priority: "{priority}"
task-type: "{task type}"
assignee: "{assignee}"
due: {YYYY-MM-DD or empty}
project: "[[{Project Name}]]"
parent-task: "{wikilink or empty}"
sub-tasks: [{wikilink list}]
source: "Notion"
created: "{date}"
notion-id: "{uuid-with-dashes}"
tags:
  - task
---

# {Task Title}

**Project:** `= this.project`

{Converted Notion body content — VERBATIM}
```

### Step 7: Print sync summary

```
=== SYNC SUMMARY (Notion → Obsidian) ===
Projects: X synced (Y new, Z updated)
Tasks: A synced (B new, C updated)
Orphan tasks: D (in _Unassigned Tasks/)
Skipped/failed: [list]
```

## Workflow B — Obsidian → Notion (Push)

Use when the user says "push to Notion", "update Notion", "sync to Notion".

### Step 1: Scan vault

Read all `.md` files in `200 Projects/` with `type: project` or `type: task` in frontmatter. Skip `Old projects notes/`, `_Templates/`, `_Dashboard.md`.

### Step 2: Classify changes

For each file:
- Has `notion-id` → potential UPDATE to existing Notion page
- No `notion-id` → potential CREATE in Notion

### Step 3: Push updates

For files with `notion-id`, fetch the current Notion page and compare properties. If the Obsidian frontmatter differs, update the Notion page:

```
mcp__claude_ai_Notion__notion-update-page(
  page_id: "{notion-id}",
  properties: { mapped property changes }
)
```

Map Obsidian properties back to Notion format:
- `status` → Status property
- `priority` → Select property
- `area` → Select property
- `deadline`/`due` → Date property
- `title` → Title property

### Step 4: Push new records

For files without `notion-id`, create a new Notion page in the appropriate database:

- `type: project` → create in Projects database
- `type: task` → create in Tasks database, set Project relation if `project` wikilink exists

After creation, update the Obsidian file's `notion-id` with the new page ID.

### Step 5: Print push summary

```
=== SYNC SUMMARY (Obsidian → Notion) ===
Projects pushed: X (Y new, Z updated)
Tasks pushed: A (B new, C updated)
Skipped: [list with reasons]
```

## Content Conversion Rules

When converting Notion enhanced markdown to Obsidian markdown:

| Notion Markup | Obsidian Equivalent |
|---------------|---------------------|
| `<empty-block/>` | Remove |
| `<database ...>Tasks</database>` | Remove (replaced by Dataview) |
| `<details><summary>T</summary>C</details>` | `> [!info]- T` + `> C` (callout) |
| `<columns><column>...</column></columns>` | Sequential content with `---` |
| `<table>` with `<tr>/<td>` | Markdown table |
| `<span color="...">text</span>` | Plain text |
| `~~text~~` | Keep (strikethrough) |
| `- [x]` / `- [ ]` | Keep (checkboxes) |
| `![](notion-cdn-url)` | Keep as `![](url)` |
| `<mention-page url="..."/>` | Remove or `[[Note Name]]` if mappable |
| Other XML/HTML tags | Remove |

## Filename Sanitization

- Replace `/\:*?"<>|` with `-`
- Collapse multiple spaces or dashes to single
- Trim leading/trailing whitespace and dots
- Maximum 200 characters
- Empty title → `Untitled-{first 8 chars of notion-id}`
- Collision → append ` (2)`, ` (3)` etc.

## YAML Safety Rules

- kebab-case property names: `task-type`, `parent-task`, `sub-tasks`, `notion-id`
- Quote strings containing `: # [ ] { } , & * ! | > ' " % @`
- Wikilinks must be quoted: `project: "[[Name]]"`
- Empty strings: `""`
- Empty lists: `[]`
- Dates: bare ISO format `YYYY-MM-DD`

## Output Contract

After any sync operation, report:

1. **Direction** — Pull (Notion→Obsidian) or Push (Obsidian→Notion)
2. **Records processed** — projects and tasks with counts
3. **Actions taken** — created, updated, skipped
4. **Conflicts** — records that differ in both systems
5. **Errors** — failed fetches or writes with IDs
6. **Caveats** — expired image URLs, missing relations, etc.

## Data Quality Rules

- **Confidence**: High when all records fetched individually. Medium when using cached/search data. Low when records were skipped.
- **Image URLs**: Notion CDN URLs are temporary (signed S3). Include them but note they may expire.
- **Relations**: If a relation target page doesn't exist in the extracted data, log it as an orphan reference.
- **Body content**: Always fetch each page individually with `notion-fetch` to get the full body. Never rely on search result snippets.

## Escalation Rules

- If the user asks about project metrics or status summaries without requesting a sync → use Notion MCP directly, don't run the full sync
- If the user asks about habits or streaks → delegate to `mind:streaks-export-analysis`
- If the user asks about body/health data → delegate to `body:body-data-qa`

## Tone

Operational and precise. Report counts and actions taken. Flag conflicts clearly. Do not editorialize about project priorities or task importance — just sync the data faithfully.
