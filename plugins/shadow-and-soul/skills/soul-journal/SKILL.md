---
name: soul-journal
description: Transcribe and analyze handwritten journal entries from reMarkable tablet. Trigger on: journal, diary, "what did I write", "journal entries for", mood log, reflection, "transcribe my journal", "read my notes", sentiment, self-reflection, or any question about journal content.
---

## MCP Server

`remarkable` — browse, search, image tools. This is the only MCP required for this skill.

## Goals

Read `300 Areas/Shadow and Soul/CLAUDE.md` before analysis.

## Analysis

Follow these steps in order:

1. **Locate journals**: `remarkable_browse('/Journals/Daily journals')` → identify notebook by month name.

2. **Get page count**: `remarkable_read(document)` returns `total_pages` even when content is empty.

3. **Extract as images**: Loop `remarkable_image(document, page=N)` for each page. Critical rules:
   - NEVER use `remarkable_read()` for content — handwritten notebooks return empty.
   - NEVER rely on `include_ocr=true` — Russian cursive is not recognized by OCR.
   - Read the returned image visually and transcribe directly.

4. **Transcribe**: Language is Russian cursive. Each page has circled DD.MM date at top. Produce:
   - Date (convert to YYYY-MM-DD using notebook month)
   - Russian transcription (best effort, mark unclear words with `[?]`)
   - English summary (1-2 sentences)

5. **Tag sentiment**: 5-point scale: 1=very negative, 2=negative, 3=mixed, 4=neutral, 5=positive.

6. **Tag themes**: From taxonomy: `stress`, `health`, `sleep`, `exercise`, `identity`, `relationships`, `work`, `travel`, `overeating`, `pain`, `anxiety`, `productivity`, `spirituality`, `anger`, `jealousy`, `gratitude`.

7. **Output**: Table with date | summary | sentiment | themes.

## Known Limitations

- Cloud may not list all notebooks. If a month is missing from `remarkable_browse`, note it explicitly.
- Local desktop cache at `~/Library/Containers/com.remarkable.desktop/Data/Library/Application Support/remarkable/desktop/` has thumbnails (.png) and .rm binaries — thumbnails are low-res but readable as fallback.
- Local .rm binaries cannot be rendered (rmscene v0.7 fails on v6 format).
- Journal absence >2 weeks is itself a data point — flag as potential overwhelm signal.

## Resources

Search `400 Resources/` for mental health, journaling, or self-reflection material.

## Tone

Quant analyst with empathy. Numbers first. When crisis signals appear (sentiment 1, crisis themes), note them clearly but without alarm. Recommend professional follow-up for persistent negative patterns.

## Schema

Reference `../../schemas/journal-entry.json`
