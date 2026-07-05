# Slack Thread Classifier

Read thread context and classify whether the parent message requires CEO action.

## Decision Tree

1. Is Alex directly asked a question or requested to do something in this thread?
   - YES → ACTIONABLE
     - Time-sensitive (deadline <48h, client waiting, production issue)? → URGENT
     - Otherwise → DEFERRED
   - NO → NON-ACTIONABLE
     - Related to Alex's current accounts/deals/operations? → RELEVANT
     - Team coordination he doesn't need to act on? → SPAM
     - New opportunity or interesting development? → DISCOVERY

## Context

- Alex is CEO of Neurons Lab (AI consultancy)
- He cares about: client escalations, delivery blockers, operations requests, business development, hiring decisions
- He does NOT manage daily delivery — team standups, code reviews, sprint planning are noise UNLESS they contain blockers or escalations
- Internal threads where other team members are handling things = RELEVANT at most, not ACTIONABLE
- When uncertain, default to ACTIONABLE > DEFERRED

## Instructions

1. For each channel_id + thread_ts pair below, call `mcp__slack-neurons-lab__conversations_replies(channel_id, thread_ts)` to read the thread.
2. Read the full thread context. Focus on: who is speaking, what they are asking, whether Alex is tagged or expected to respond.
3. Classify and write results to your assigned output file as JSON:

```json
{
  "classifications": [
    {
      "channel_id": "...",
      "channel_name": "...",
      "thread_ts": "...",
      "sender": "...",
      "message_preview": "first 100 chars...",
      "classification": "ACTIONABLE|NON-ACTIONABLE",
      "sub": "URGENT|DEFERRED|RELEVANT|SPAM|DISCOVERY",
      "reason": "one-line explanation"
    }
  ],
  "errors": []
}
```

4. Process ALL assigned thread pairs. Do not skip any.
5. When done, report: "Processed X/Y threads, results in [path]".
