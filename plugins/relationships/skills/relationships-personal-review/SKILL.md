---
name: relationships-personal-review
description: Run structured weekly, monthly, or quarterly reviews of PERSONAL relationships — your partner and your family/close friends (the inner circle) — using local communication metadata (WhatsApp, phone calls, iMessage/SMS) plus the Telegram MCP and Google Calendar. Measures connection cadence, reciprocity (who reaches out), and who is going dormant, scored against the Relationships area's "Woman" and "Family" practice stages and the strategy principle "Include more people in more of my life activities". Trigger on relationships review, "am I neglecting my family / partner", "who am I losing touch with", personal connection review, family review, or inner-circle check-in. For the professional network lens (target-network activation, follow-ups, new connections) use `relationships-network-review` instead.
compatibility:
  - tool: mcp__claude_ai_Clay__searchContacts
  - tool: mcp__claude_ai_Clay__getGroups
  - tool: mcp__claude_ai_Clay__getContact
---

# Relationships - Personal Review (Partner & Family)

Primary entrypoint for reviewing the health of the **inner circle**: the partner and
family + close friends. This is the personal lens; the
professional-network lens lives in `relationships:relationships-network-review`. They are cheap to
run together — offer both when the user asks for "a relationships review" unqualified.

The whole reason this skill exists: **the CRM (Clay/Mesh) is blind to the inner circle.** Family and
partner contact happens on WhatsApp, phone calls, and Telegram — none of which Clay ingests here — so
Clay's "last interaction" for family is stale by years. This review measures the channels where the
personal relationships actually live.

## Review Types

- weekly review (this ISO week vs last ISO week)
- monthly review (this calendar month vs last)
- quarterly review (multi-month trend; earliest month = baseline)

Use ISO week boundaries for weekly, calendar months for monthly. No rolling "last 7 days".

## Reasoning Order

1. Read `000 OS/2 Simple strategy 2026` — the connection-relevant lines: the core relationship-building
   principle, the stress-remedies that involve people and the partner, and any self-identified
   derailers listed there. Use what the file says — do not assume or quote values here.
2. Read the personal practice files in `300 Areas/5 Relationships/` (partner and family practices).
   These define the cadence commitments to score against.
3. Only then interpret the interaction data.

## Data Sources

- **Local extractor** `relationship_extract.py` (bundled next to this skill) — metadata only from
  `~/Library/Messages/chat.db` (iMessage/SMS), `CallHistoryDB/CallHistory.storedata` (calls),
  WhatsApp `ChatStorage.sqlite`. Per-contact counts, sent/received split, first/last date, call minutes.
  Run with `--monthly` for the per-month trend. Also reports **WhatsApp group participation** (your share
  of messages per group) — surfaces social/hobby groups where you are present but silent.
- **Telegram MCP** (`mcp__telegram__*`, read-only) — the other channel parts of the inner circle use.
  Use `get_last_interaction`, `list_chats`/`get_chats` (dialog recency), and
  per-chat `get_history`/`get_messages` message counts. Telegram has no local DB (encrypted), so it MUST
  come via the MCP. If the Telegram MCP is not loaded, say so and treat Telegram contact as unmeasured.
- **Google Calendar** (`mcp__claude_ai_Google_Calendar__*`) — date nights with the partner and family
  time; the best signal for a partner whose contact happens mostly offline.
- **Clay** (`mcp__claude_ai_Clay__*`) — used ONLY to resolve handles→people and to define the roster:
  the "❤️ Family" group and "Starred" contacts, plus their phone numbers for matching. NOT used for
  personal recency (it is wrong for the inner circle — see Data Reality Rules).

## Data Reality Rules — READ BEFORE EVERY REVIEW

- **Clay is blind to the inner circle. Never report a family member or the partner as "neglected" from
  Clay recency.** Clay's family last-interaction dates are years stale because family contact is on
  WhatsApp/calls/Telegram, which Clay does not ingest. Use Clay for names/roster/phone numbers only.
- **The extractor is metadata only** — counts, direction, dates, call minutes. It never reads message
  text. Keep it that way; the review is about cadence, not content.
- **A partner seen daily is mostly OFF the wire.** Low WhatsApp/call volume with the partner can be
  expected — much of that relationship may be in person. Use Calendar date-nights as the primary partner
  signal, and read messaging only for gaps/absences, never as a closeness score.
- **Separate 1:1 from group chats.** The extractor already excludes WhatsApp/iMessage group threads;
  keep group-chat noise out of per-person cadence.
- **Reciprocity = sent / (sent+received).** ~0.5 is balanced; persistently low means they carry the
  relationship (you mostly reply); persistently high means you chase. Flag both.
- **Local DBs hold only what synced to this Mac**, but they keep years — so a true multi-month trend IS
  possible (unlike the 30-day Screen Time cap). iMessage is often near-empty here (messaging is WhatsApp).
- **Copy each DB before reading** (the extractor does this) so the live app is never locked.

## Bucket Taxonomy

Resolve every contact to a person (WhatsApp `ZPARTNERNAME` / call `ZNAME` / Telegram name, else Clay
phone match), then bucket:

| Bucket | Rule | Read |
|---|---|---|
| **Partner** | The partner | Score on date cadence + gaps, NOT message volume |
| **Family — near** | Immediate family (parents, siblings) in Clay "❤️ Family" | The core maintenance duty; dormancy here is the headline risk |
| **Family — extended** | Grandparents, in-laws, cousins in "❤️ Family" | Lighter cadence; watch for total silence |
| **Close friends** | Starred / high-volume non-work personal contacts | The "more people on purpose" principle |
| Work-on-personal-channels | Colleagues who message on WhatsApp/Telegram | Exclude from the inner-circle verdict; note the bleed |

## Metrics To Compute (per period, with delta)

1. **Inner-circle breadth** — how many distinct family + close-friend people you exchanged with.
2. **Dormant inner circle** — family/close-friends with zero contact in the window, and the
   longest-dormant person (days since last). This is the review's headline.
3. **Partner cadence** — date-nights on Calendar vs the weekly commitment; longest no-date gap. Messaging
   only as a gap check.
4. **Per-family-member recency & frequency** across all channels (WhatsApp + calls + Telegram + iMessage),
   with call minutes for parents/grandparents (a call outweighs many texts).
5. **Reciprocity** per key person — are you initiating or only responding?
6. **Channel mix** — where the inner circle actually lives (expect WhatsApp + Telegram dominant, iMessage
   negligible), so future reviews query the right places. Note the split: Telegram often carries one
   country/community, WhatsApp another — say which is which.
7. **Social-group presence** — WhatsApp group participation rate (your share of each group's messages).
   Flag hobby/social groups where you are present but silent; that is the loner pattern, structurally.

## Workflow

1. Set the review + comparison windows.
2. Read the strategy connection-lines and the Woman/Family practice files before concluding.
3. Pull the roster from Clay: `getGroups` (find "❤️ Family"), `searchContacts` group_ids=[family] with
   `include_fields:["phone_numbers"]`, and Starred. Build a phone→person and person→bucket map.
4. Run the extractor for the review window and the comparison window (`--monthly` for quarterly), and
   pull Telegram recency/counts via the Telegram MCP for the same people.
5. Match extractor/Telegram handles to people via the phone map; bucket them; compute the metrics.
6. **Clay-vs-local reconciliation** (the honesty anchor): for 2–3 inner-circle people, show Clay's
   last-interaction date next to the real last-contact from local/Telegram, and state plainly that the
   local number is the truth for personal relationships.
7. Score against the partner date cadence, the family "time attention care" cadence, and the
   connection principle. Back-reference the prior review's priorities; grade follow-through.
8. Produce the structured review; save the file(s).

## Recommendation Rules

- One to three high-leverage priorities. Prefer concrete re-connections ("call your grandmother — 47 days
  silent") over vague "be more present".
- Tie each to a specific person/gap in the data and a specific cadence or the connection principle.
- Separate observation / interpretation / assumption. Vault voice: sentences < 25 words; numbers over
  generalities; banned words — delve, leverage, robust, navigate, journey, ecosystem.
- Privacy: name people by first name only; never quote message content (there is none to quote).

## Output Contract

- review scope + comparison windows (+ "Source: WhatsApp + calls + Telegram + iMessage metadata; Clay is
  blind to the inner circle and used for roster only").
- a scorecard delta table (inner-circle buckets: breadth, dormant count, partner date-nights, per-key-person
  contact across periods, Trend column for multi-month).
- for multi-month trends, open with a narrative headline.
- per-bucket sections: Partner (date cadence), Family — near, Family — extended, Close friends.
- the **Clay-vs-local reconciliation** table.
- alignment with the partner/family cadences and the connection principle.
- top 3 priorities; risks/caveats (partner-mostly-offline, Telegram-if-unloaded, sync gaps); numbered
  next actions.

Numbers first, then interpretation, then recommendation.

## File Saving

Weekly and monthly reviews always create report files. Do not ask whether to save.

```bash
mkdir -p "$PERIODICS_ROOT/Monthly/$MONTH_NAME"     # monthly / quarterly
mkdir -p "$PERIODICS_ROOT/Weekly/Week $ISO_WEEK"   # weekly
```

Example paths:
- monthly: `$PERIODICS_ROOT/Monthly/06 June/2026-06-relationships-personal-review.md`
- weekly: `$PERIODICS_ROOT/Weekly/Week 11/2026-week-11-relationships-personal-review.md`

H1 + bold metadata block (Review period / Comparison period / Source / Generated / Related). No YAML
frontmatter on review outputs.

## Provenance

`relationship_extract.py` is a self-contained Python-stdlib extractor (no dependencies, no network). It
copies each local database to a temp file before opening it read-only, and reads only metadata columns —
never message text. Requires Full Disk Access for the host process.

## Tone

Honest inner-circle audit. Numbers first, no guilt-tripping, end with concrete re-connections.

## Schema

Reference `../../schemas/relationships-review.json`. Set `lens: "personal"`.
