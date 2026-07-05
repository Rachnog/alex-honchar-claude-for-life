---
name: streaks-export-analysis
description: Analyze a Streaks `.streaks` export, preferably acquired through an Apple Shortcuts plus shell plus Claude Code workflow, and create a markdown habits report in the same style as the sample monthly report. Trigger on "analyze my Streaks export", "make a habits report from Streaks", "run a monthly Streaks review", "use Shortcuts with Streaks", or requests to turn a Streaks backup into a report.
---

# Mind - Streaks Export Analysis

Turn a Streaks export into a trustworthy markdown review.

This skill is Streaks-specific. It is not a generic export-analysis workflow, and it does not assume a native Streaks MCP server exists today.

## Core Principle

Do not write the report until you have:

1. confirmed the export shape
2. separated current tasks from historical tasks
3. matched scoring rules to the task cadence and task type

If those three things are not true yet, you are still in discovery.

## When To Use

Use this skill when the user asks to:

- analyze a Streaks export
- generate a monthly or weekly habits report from Streaks
- build a report from a `.streaks` file
- use Apple Shortcuts and Claude Code to automate Streaks reporting
- review habit performance from Streaks with strongest tasks, weakest tasks, and patterns

When this skill is being used to support a weekly or monthly `body-cadence-review`, its output is required before the body review can be finalized.

## Intake Paths

Support these paths in order.

Decision rule:

- If the user asks about a live or recent period such as `today`, `this week`, `last week`, `this month`, or `last month`, assume they want a fresh export and start with Path A unless they explicitly say to use an existing file.
- If the user gives a concrete `.streaks` file path or says they already exported the data, use Path B.
- Do not search the filesystem first for date-scoped requests when the user did not mention an existing export file.
- Do not silently substitute a recently found export for a fresh-period request. If the data source is not fresh or user-authorized, stop and ask.

### Path A - Shortcut-first acquisition

Prefer this path when the user wants a fresh export or wants the workflow automated.

Recommended Shortcut pipeline:

1. Streaks action: export the backup for the requested date range
2. Streaks action: get the current task list or streak counts if available
3. Shortcuts action: `Run Shell Script`
4. Save the raw export to disk
5. Run Claude Code against the saved export

This is a Shortcut plus shell workflow pattern. It is not a built-in Streaks MCP server.

For fresh-export requests, the first move is to try Apple Shortcuts automatically when the `shortcuts` CLI and a matching export shortcut are available. Do not start by searching the disk for `.streaks` files unless the user explicitly asked to reuse a saved export.

If the `shortcuts` CLI is available and there is a matching Streaks export shortcut, try running it automatically before asking the user to do it manually.
Prefer the shortcut named `Streaks Export` when present.

Use wording like:

- `I’m trying your Apple Shortcuts Streaks export automatically first. If it succeeds, I’ll use that output directly.`
- `If the automatic Shortcut run fails, run your Streaks Shortcut export and give me the resulting file or payload.`
- `If you want, I can help you set up the Shortcut plus shell flow so this becomes one command.`

For a weekly or monthly body-review flow, this ask is mandatory. Do not let the downstream review finish until the Shortcut-provided Streaks export has been supplied and analyzed.

For a request such as `get my streaks performance this week and last month`, the preferred first response is:

- `I’m trying your Apple Shortcuts Streaks export automatically first for this week and last month. If that automatic run fails, I’ll ask you for the resulting file or payload.`

Forbidden first moves for fresh-period requests:

- searching common folders for old `.streaks` files
- reading the most recent export you happen to find without user approval
- treating `most recent export on disk` as equivalent to `this week` or `last month`
- generating the final report before resolving whether the user wants fresh or existing data
- asking the user to run the Shortcut before first attempting `shortcuts run "Streaks Export"` when that automatic path is available

Example shell shape:

```bash
#!/bin/zsh

EXPORT_DIR="$HOME/Documents/Streaks"
DATE=$(date +%Y-%m-%d)
mkdir -p "$EXPORT_DIR"

# Run the Shortcut first when available and capture its output
EXPORT_PAYLOAD="$(shortcuts run "Streaks Export")"
printf '%s' "$EXPORT_PAYLOAD" > "$EXPORT_DIR/backup-$DATE.streaks"

claude -p "Analyze $EXPORT_DIR/backup-$DATE.streaks and write a markdown habits report." \
  --output-format text
```

If the user wants a more advanced automation package, you can also help with:

- a richer shell wrapper
- a `launchd` schedule
- saving reports into another local knowledge system

### Path B - Existing export file

Use this when the user already has a `.streaks` file on disk.

Required inputs:

- the export file path
- the reporting window, if not obvious from context

If the user does not specify the review window, infer the most recent full month when that is clearly what they want. Otherwise ask.

Use filesystem search only when:

- the user explicitly says the export already exists somewhere on disk and wants help locating it
- the user points to a directory and asks you to inspect it
- the Shortcut-first path already ran and saved the export locally

Do not treat "I want my Streaks performance this week" as permission to search random folders for old exports.
If you do find an existing export while helping with Path B, state its timestamp and ask whether the user wants to use it before analyzing.

## Workflow

### Step 1 - Confirm the export shape

Before deep analysis:

- confirm the file is JSON
- identify the top-level keys
- confirm `tasks` exists
- inspect a few representative task records before computing metrics

On the sample export used to design this skill, the top-level keys are:

- `app`
- `categories`
- `desc`
- `tasks`
- `timestamp`
- `type`
- `version`

### Step 2 - Split current tasks from history

Treat population splitting as mandatory.

For the sample export, these are the working rules:

- `tasks` is the main task-definition collection
- `st='N'` is the working definition for current tasks
- `st='A'` is the working definition for historical or archived tasks

Only use those rules when the evidence still supports them in the current export. The evidence should include:

- the current-task population looks plausibly sized
- the current-task population contains richer task metadata
- the current-task population contains `pg` values that partition cleanly into visible groups

If the evidence is mixed, say so explicitly and ask before treating the split as fact.

### Step 3 - Identify grouping

When the export supports it, group the current tasks by `pg`.

For the sample export:

- `pg=0` -> `Screen 1`
- `pg=1` -> `Screen 2`
- `pg=2` -> `Screen 3`
- `pg=3` -> `Screen 4`

Do not force screen labels if the active-task population does not partition cleanly by `pg`.

### Step 4 - Decode task fields carefully

Important field rules:

- task-level `t` is the task title
- log-level `t` is the outcome code
- `n=true` indicates an avoidance-style task
- `fm=0` behaves like a daily task family in the sample export
- `fm=6` behaves like a weekly task family in the sample export
- `ftpd` is the target count for count-based tasks

Useful sample-export patterns:

- positive daily binary tasks: `fm=0`, `ftpd=1`, `n=false`
- daily avoidance tasks: `fm=0`, `ftpd=1`, `n=true`
- daily count-based tasks: `fm=0`, `ftpd>1`, `n=false`
- weekly binary tasks: `fm=6`, `ftpd=1`
- weekly count-based tasks: `fm=6`, `ftpd>1`

Treat these as working interpretations, not product documentation.

Before final classification, inspect the actual outcome-code distribution for each task. If a task that looks binary by metadata emits substantial `4` or `6` logs, do not force it into the plain binary bucket. Reclassify it conservatively as a progress-coded daily task or ask the user before scoring if that changes the headline result.

### Step 5 - Score each cadence correctly

Use cadence-aware scoring. Never apply one scoring rule to every task.

#### Positive daily binary tasks

Working outcome codes from the sample export:

- `1` = success
- `5` = missed

Only use this bucket when the task's observed logs are dominated by `1` and `5`. If `4` or `6` appear in non-trivial volume, stop treating the task as a simple binary task.

Report format:

- `February: 15/28 successful days, 13/28 missed`

#### Daily progress-coded tasks with binary-looking metadata

Some tasks may look like daily binary tasks from metadata but still emit many `4` or `6` logs.

For those tasks:

1. do not silently score them as plain binary
2. inspect whether the task is effectively behaving like a partial-progress task
3. if a conservative day-level classification is possible, describe the task accordingly
4. if not, ask the user or include an explicit caveat instead of inventing certainty

Preferred wording when caveated:

- `This task uses a daily schedule but emits progress-style codes (`4` and `6`), so its February scoring is more uncertain than the other binary tasks.`

#### Daily avoidance tasks

Working outcome codes from the sample export:

- `2` = good day
- `7` = failed day
- `13` = special or unclear status

Report format:

- `February: 9/28 good days, 18/28 failed days, 1/28 special-status day`

#### Daily count-based tasks

These can have multiple log rows for the same day.

Working interpretation rules from the sample export:

- `1` = target hit
- `6` and `4` = partial progress
- `5` = no hit

Daily scoring rule:

1. group logs by day
2. if any row for the day has `t=1`, count the day as a target-hit day
3. else if the day has `t=6` or `t=4`, count the day as a partial-progress day
4. else if the day has `t=5`, count the day as a no-hit day
5. if multiple interpretations remain plausible, choose the conservative one and note it

Report format:

- `February: 4/28 target-hit days, 8/28 partial-progress days, 16/28 no-hit days`

#### Weekly binary tasks

Use `ps`, `pe`, and `pt='w'` to score by scheduled week, not by raw log-entry count.

Working outcome codes from the sample export:

- `1` = successful week
- `5` = missed week

Count weeks by unique scheduled periods inside the report window.

Report format:

- `February: 3 successful weeks, 0 partial weeks, 0 missed weeks`

#### Weekly count-based tasks

Score by scheduled week using `ps`, `pe`, and `pt='w'`.

Working interpretation rules from the sample export:

- `1` = target-hit week
- `6` = partial-progress week
- `5` = missed week

Weekly scoring rule:

1. group logs by `ps` plus `pe`
2. if the period includes `t=1`, count it as a successful week
3. else if the period includes `t=6`, count it as a partial week
4. else if the period includes `t=5`, count it as a missed week

Report format:

- `February: 2 successful weeks, 2 partial weeks, 0 missed weeks`

## Ambiguity Rules

Always separate raw facts from interpretation.

High-confidence facts:

- top-level keys present in the file
- counts of tasks and log rows
- raw field values observed
- whether multiple rows exist for the same day or week

Medium-confidence interpretations in the sample export:

- `st='N'` means current tasks
- `st='A'` means historical tasks
- `pg` maps to app screens
- `fm=0` means daily-style tasks
- `fm=6` means weekly-style tasks

Lower-confidence interpretations:

- exact meaning of every outcome code
- exact semantics of special codes like `13`
- undocumented scheduler fields outside what is needed for the report

If a low-confidence interpretation changes the headline result, stop and ask instead of guessing.

## Output Contract

Default to the sample-style markdown report unless the user explicitly asks for a different format.
The same structure can be used for monthly or weekly reviews; only the title, window labels, and metric lines should change with the cadence.

Use this structure:

```markdown
# [Period Label] Habits Report

Source: `[export filename]`

This report uses the `[N]` tasks treated as current for this export and groups them using the export field that most cleanly partitions the active set.

- If confidence is high, you may state the exact interpretation, for example: `This report uses the 23 current tasks (`st='N'`) and groups them by the export's built-in page field, pg, which maps cleanly to four app screens.`
- If confidence is only medium, keep the wording caveated, for example: `This report treats the 23 tasks with st='N' as the current set and uses pg as the best available screen-like grouping field.`

- List one bullet per discovered group.
- If `pg` confidently maps to screens in the current export, use the sample style:
  - `Screen 1` = `pg=0` = [count] tasks
  - `Screen 2` = `pg=1` = [count] tasks
  - `Screen 3` = `pg=2` = [count] tasks
  - `Screen 4` = `pg=3` = [count] tasks
- If the grouping field is weaker or uses a different partition, keep the same rhythm but rename the groups honestly:
  - `Group 1` = `[group value]` = [count] tasks
  - `Group 2` = `[group value]` = [count] tasks

Notes on decoding:

- Binary positive tasks: `1 = success`, `5 = missed`
- Avoidance tasks (`n=true`): `2 = good day`, `7 = failed day`, `13 = special/unclear status`
- Count-based tasks: `1 = target hit`, `6/4 = partial progress`, `5 = no hit`

Repeat the following section once per discovered group:

## [Group label]

1. `Task name`
   Daily, 1x target
   [Period label]: `[metric summary]`

1. `Task name`
   [Cadence label]
   [Window label]: `[metric summary]`

## Quick Read

Strongest tasks:

- `Task A`: `[metric]`

Weakest tasks:

- `Task B`: `[metric]`

Pattern:

- `[Group label]` summary
- `[Group label]` summary
```

Keep the report readable and direct. Do not switch to a heavy schema-style report unless the user asks for that explicitly.
Adjust the introductory prose to match the actual confidence level of the `st` split and the grouping field. The sample structure is fixed; the certainty of the wording is not.

Weekly examples:

- title: `Week 10 Habits Report`
- metric line: `Week 10: 4/5 successful days, 1/5 missed`
- weekly count target line: `Week 10: 1 successful week, 0 partial weeks, 0 missed weeks`

## Downstream Handoff

When another plugin needs Streaks evidence, keep `mind:streaks-export-analysis` as the source of truth for export decoding.
Do not make downstream plugins reverse-engineer raw `.streaks` files when a Streaks report or summary can be passed in instead.

After the main markdown report, optionally provide a compact handoff section for other skills under this shape:

```markdown
## Habit Evidence Summary

- Review window: `[start]` to `[end]`
- Current tasks analyzed: `[N]`
- Grouping basis: `[high-confidence grouping or caveated grouping]`
- Strongest habits: `[habit]`, `[habit]`
- Weakest habits: `[habit]`, `[habit]`
- Notable habits:
  - `[habit]` - `[brief adherence summary]`
  - `[habit]` - `[brief adherence summary]`
- Caveats:
  - `[important ambiguity or confidence note]`
```

Keep the handoff generic. Downstream plugins should decide which habits matter to their own domain rather than relying on `mind` to assign domain ownership.

## File Output Rules

If the user asks for a saved report:

- write markdown to the requested path
- otherwise save next to the export with a descriptive filename such as `2026-02-habits-report.md`

If the user wants the report saved into a `Periodics` structure, create the period subfolder first when needed.

Folder naming rules:

- monthly reports: create or use a month-name folder such as `January`, `February`, `March`
- weekly reports: create or use a week-number folder such as `Week 10`, `Week 11`
- the period folder should live inside the correct parent under `Periodics`, for example a monthly parent for month reports and a weekly parent for week reports

Use shell commands shaped like:

```bash
# Monthly report
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"

# Weekly report
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"
```

Then save the report inside that folder.

Examples:

- monthly: `$PERIODICS_ROOT/Monthly/February/2026-02-streaks-report.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 10/2026-week-10-streaks-report.md`

Only create the folder if it does not already exist. `mkdir -p` is the preferred command because it is safe when the folder already exists.

When this skill is supporting `body-cadence-review`, keep the save-path rules compatible with the body review's mandatory `Periodics` output. The body review may save its own final report separately, but this skill must not suggest skipping file creation for the weekly/monthly review flow.

If the user only asks for analysis and does not request a file:

- provide the markdown in the response
- offer to save it after

## Guardrails

- Do not treat every task in the export as current by default
- Do not treat every log row as a success row
- Do not score weekly tasks by raw event count
- Do not claim a native Streaks MCP integration unless one actually exists
- Do not hide field uncertainty behind confident wording

## Tone

Thoughtful operating review of habits. Numbers first, plain English, no fluff.
