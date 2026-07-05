---
name: gtd-apple-notes-triage
description: >
  Triage Apple Notes inbox using GTD principles — auto-save link-only notes to
  Obsidian Clippings, extract and analyze screenshots, create Notion tasks from
  actionable items, archive reference material to Obsidian vault.
  Trigger on: "process my apple notes", "triage apple notes", "check apple notes",
  "apple notes inbox zero", "clean up apple notes", "what's in my apple notes",
  "apple notes review", "notes triage", or any question about processing
  incoming Apple Notes captures.
compatibility:
  - tool: mcp__apple-notes__list_notes
  - tool: mcp__apple-notes__get_note
  - tool: mcp__apple-notes__delete_note
  - tool: mcp__apple-notes__search_notes
  - tool: mcp__claude_ai_Notion__notion-create-pages
  - tool: mcp__claude_ai_Notion__notion-fetch
---

# Apple Notes Triage v1.0 — GTD Pipeline for Quick Captures

Triage all active (non-deleted) Apple Notes. Classify each note by content type using deterministic rules, auto-save link-only notes to Obsidian Clippings, extract screenshots for user review, and present text notes for manual disposition (Notion task, Obsidian save, or delete).

> **CRITICAL: MCP LIMITATIONS — osascript Required**
> Apple Notes MCP `list_notes` returns `title: null` and `snippet: ""` for untitled "New Note" entries.
> `get_note` and `delete_note` require exact title match — fail on complex titles with newlines/quotes.
> **Phase 0 MUST use osascript via Bash tool** to scan all notes and read HTML bodies.
> MCP tools are used only as fallback for simple titled notes.

> **TOKEN EFFICIENCY:**
> Phase 0 osascript scan returns HTML bodies inline — one Bash call gets all data.
> Phase 1 (links) is fully automated with zero user interaction.
> Sub-agents only needed for Phase 2 (screenshots) — typically 0-5 per run.
> Design target: process 80%+ of notes in Phases 0-1 with zero sub-agent calls.

## Rule Files

Load these from `plugins/work/skills/gtd-apple-notes-triage/` before processing:
- **`note-rules.json`** — deterministic classification by URL domain, title pattern, and content thresholds

## Phase 0: osascript Scan + Classify (Main Agent)

1. **Load rule file** — read `note-rules.json`

2. **Scan all non-deleted notes** — run osascript via Bash:

   > **CRITICAL: NEVER use `repeat with n in notes` at the top level** — this pattern iterates over ALL notes including the "Recently Deleted" folder and will process deleted notes as if they are active.
   >
   > **ALWAYS iterate by folder and explicitly skip "Recently Deleted":**

   ```applescript
   tell application "Notes"
     repeat with f in folders
       if name of f is not "Recently Deleted" then
         repeat with n in notes of f
           -- extract name, folder, body (first 2000 chars)
         end repeat
       end if
     end repeat
   end tell
   ```
   Use Python wrapper to parse output and avoid osascript string limits.

3. **Classify each note** by analyzing HTML body structure:

   **LINK_ONLY** — body contains `<a href=` tags and stripped text is < `link_only_max_text_chars` (100 chars).
   Links may be to Instagram, X/Twitter, YouTube, LinkedIn, ChatGPT, arXiv, Substack, GitHub, etc.
   Multiple links in one note = still LINK_ONLY (common for "New Note" quick-shares).

   **SCREENSHOT** — body contains `<img src="data:image/` and stripped text is < `screenshot_max_text_chars` (50 chars).
   These are base64-encoded images captured via iPhone share sheet.

   **TEXT_RICH** — stripped text is > `text_rich_min_text_chars` (200 chars). May contain some links but the text IS the value.
   These are research notes, meeting notes, course material, drafted posts.

   **TITLE_ONLY** — has a title but body is empty, whitespace, or just `<br>` tags.
   These are quick idea captures, reminders, or topic bookmarks.

   **MIXED_LINKS** — multiple URLs from different domains + minimal text. Treated same as LINK_ONLY.

4. **Report totals** to the user:
   ```
   Apple Notes Scan: 47 notes found
   - 32 link-only (28 Instagram, 2 X/Twitter, 2 other)
   - 5 screenshots
   - 6 text-rich
   - 4 title-only
   Processing Phase 1 (links) automatically...
   ```

5. **If zero notes found** — report "Apple Notes inbox is clean" and exit.

## Phase 1: Auto-Process LINK_ONLY Notes (Fully Automated)

For each LINK_ONLY note, extract all URLs from `<a href=...>` tags and apply `by_url_domain` rules:

**Instagram / TikTok (bulk append):**
- If the note title is "New Note" (untitled): append URL(s) to the existing bulk file (e.g., `Instagram Reels - Unsorted.md`)
- If the note has a real title (not "New Note"): create individual file (e.g., `Creator Name on Instagram.md`)
- Bulk file format: read existing file, append new URLs at end of the link list

**X/Twitter (individual files):**
- Extract @handle from URL path (e.g., `/examplehandle/status/123` → `@examplehandle`)
- Create `Thread by @[handle].md` in Clippings
- If file already exists, append ` 1`, ` 2` suffix

**Other platforms (individual files):**
- Use note title if available, else domain + path fragment
- Create individual file in Clippings

**Clippings frontmatter format (simplified):**
```yaml
---
source: [primary URL]
author: "[name or @handle]"
saved: [YYYY-MM-DD]
tags: [clipping, platform]
---

# [Title]

## Links
- [url1]
- [url2]
```

**Delete processed notes:**
- Try MCP `delete_note(title)` first for simple titled notes
- Fallback to osascript: `first note whose name starts with "[prefix]"` for complex titles
- Fallback to osascript: `first note whose body contains "[unique URL fragment]"` for untitled notes
- For bulk untitled Instagram notes, use osascript loop: delete all notes whose body contains `instagram.com` and name is "New Note"

**Report:**
```
Phase 1 complete: 32 link-only notes processed
- 28 Instagram URLs → appended to Instagram Reels - Unsorted.md
- 2 X/Twitter → Thread by @handle1.md, Thread by @handle2.md
- 2 other → [filename1].md, [filename2].md
All 32 notes deleted from Apple Notes.
```

## Phase 2: Screenshots (Semi-Automated — User Decides)

**Skip if zero SCREENSHOT notes.**

1. Create `/tmp/apple-notes-screenshots/` (wipe if exists)

2. **Extract images** — for each screenshot note, use Python via Bash:
   ```python
   # osascript to get full HTML body
   # regex to extract base64: re.search(r'src="data:image/png;base64,([^"]+)"', html)
   # base64.b64decode() → save to /tmp/apple-notes-screenshots/[name].png
   ```

3. **Launch Haiku sub-agents** — one per screenshot (max 10, batch if more). Each sub-agent:
   - Reads `plugins/work/skills/gtd-apple-notes-triage/sub-agent-prompt.md`
   - Uses `Read` tool to analyze the PNG image
   - Writes JSON result to `/tmp/apple-notes-screenshots/[name].json`

4. **Present results table** to user:
   ```
   | # | Note | Content | Suggested Action |
   |---|------|---------|-----------------|
   | 1 | Screenshot Mar 28 11:29 | WhatsApp: Acme tender, budget discussion | Notion task: "Follow up Acme tender" (High) |
   | 2 | Screenshot Mar 26 20:30 | Telegram: AI talks, Anthropic report link | Notion task: "Review AI talks discussion" (Medium) |
   ```
   Include: number, note identifier, content summary, suggested action with suggested title/priority.

5. **Wait for user confirmation** — user can:
   - Accept suggestion as-is
   - Modify (change title, priority, destination)
   - Skip (leave in Apple Notes)
   - Delete (remove without saving)

6. **Execute confirmed actions:**
   - Notion task: use `mcp__claude_ai_Notion__notion-create-pages` with personal database
   - Obsidian save: write markdown file to specified vault path
   - Delete: remove from Apple Notes via osascript

7. Clean up `/tmp/apple-notes-screenshots/`

## Phase 3: Text & Title Notes (Interactive)

**Skip if zero TEXT_RICH and TITLE_ONLY notes.**

1. **Present remaining notes** in a summary table:
   ```
   | # | Title | Type | Snippet | Links | Suggested Action |
   |---|-------|------|---------|-------|-----------------|
   | 1 | Who runs Anthropic's Ambassador... | TEXT_RICH | Three people publicly manage... | 5 links | Notion task (High) |
   | 2 | Founders community | TITLE_ONLY | — | — | Notion task (Medium) |
   | 3 | Anthropic Course Notes | TEXT_RICH | Coding trends report... | 2 links | Obsidian: 500 Archive/8 Work/ |
   ```

2. **Apply title pattern rules** from `note-rules.json` → `by_title_pattern` to suggest actions.
   Default suggestion: TITLE_ONLY → Notion task; TEXT_RICH → present for user decision.

3. **Wait for user to decide each note** — for each:
   - **Notion task**: user provides task name (or accepts suggestion), priority, task type
   - **Obsidian save**: user specifies destination folder
   - **Skip**: leave in Apple Notes
   - **Delete**: remove without saving

4. **Execute confirmed actions:**
   - Notion tasks: `mcp__claude_ai_Notion__notion-create-pages` with:
     - `data_source_id`: your Tasks database data source ID (see `note-rules.json` → `notion_defaults.data_source_id`)
     - `Status`: `"Backlog"` (API rejects "Planned" despite UI showing it)
     - Content: full note text converted from HTML to markdown
   - Obsidian saves: convert HTML body to markdown, write to specified vault path
   - Deletes: remove via MCP or osascript

## Phase 4: Report

Write the triage report to `100 Periodics/Weekly/[current week folder]/[date]-apple-notes-triage.md`:

```markdown
## Apple Notes Triage — [date]

### Link-Only Notes (X → Clippings)
- Instagram: N URLs → Instagram Reels - Unsorted.md
- X/Twitter: N → [list individual files]
- Other: N → [list individual files]

### Screenshots (Y)
| Note | Content | Action Taken |
|------|---------|-------------|
| [name] | [summary] | [Notion task / Obsidian / Deleted / Skipped] |

### Text & Title Notes (Z)
| Note | Action Taken |
|------|-------------|
| [title] | [Notion task: "name" / Obsidian: path / Deleted / Skipped] |

### Notion Tasks Created (N)
- [task name] — [priority] — [status]

### Stats
Total: N | Auto-clipped: X | Screenshots: Y (Z acted on) | Text/Title: W (V acted on) | Deleted: D | Skipped: S | Sub-agents: A | Errors: E
```

## Tone

Executive assistant processing an inbox. Crisp, organized. Auto-process what's unambiguous (links), surface what needs judgment (screenshots, text).
Don't ask about every Instagram reel — batch them silently. Only interrupt for decisions on screenshots and text notes.

## Safety

- **Never delete a note without first saving its content elsewhere** — Clippings, Notion, or Obsidian
- **Never modify Apple Notes content** — only read and delete
- **Default to keeping** when classification is uncertain — mark as TEXT_RICH and present to user
- **Always use the personal Notion workspace** — never a work/company Notion workspace
- **Only process non-deleted notes** — ALWAYS iterate notes via folder loop with `if name of f is not "Recently Deleted"` guard. NEVER use top-level `repeat with n in notes` (includes deleted notes).
- **Link-only rule**: only notes with JUST URLs go to Clippings. Long text notes with embedded links are TEXT_RICH.
- **Screenshot privacy**: extracted images go to `/tmp/` and are cleaned up after processing — never saved to permanent storage unless user explicitly requests
- If osascript returns an error for a specific note, skip it and report — never retry destructively

## Error Handling

- **osascript timeout**: if scan takes >30 seconds, likely too many notes. Paginate by folder.
- **MCP delete fails**: fallback to osascript deletion. If both fail, report and skip.
- **Base64 decode fails**: skip screenshot, report as "could not extract image"
- **Notion API rejects status**: use "Backlog" (known issue: "Planned" exists in UI but API rejects it)
- **Duplicate Clippings filename**: append numeric suffix (` 1`, ` 2`)
- **Bulk file doesn't exist**: create it with proper frontmatter instead of appending

## Rule Iteration

After each triage run:
1. If notes were classified by heuristics rather than rules, identify common patterns
2. Suggest additions to `note-rules.json` — new URL domains, title patterns
3. Present suggestions to user — never auto-modify rules
4. Target: >90% of link-only notes classified by domain rule after 2-3 runs
