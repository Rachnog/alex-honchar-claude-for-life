# Email Classifier

Classify each email using this decision tree:

1. Does it require the user to DO something? (respond, sign, review, decide, schedule)
   - YES → ACTIONABLE
     - Time-sensitive (deadline <48h) or quick (<5 min)? → URGENT
     - Otherwise → DEFERRED
   - NO → NON-ACTIONABLE
     - Related to user's current work/interests? → RELEVANT
     - Junk/marketing/tool noise? → SPAM
     - Potentially interesting new opportunity? → DISCOVERY

## Context

- User is CEO of Neurons Lab (AI consultancy).
- For neurons-lab emails: someone wants to BUY from / INVEST in NL = ACTIONABLE. Someone wants to SELL to NL = SPAM.
- NL internal threads where user is CC'd (legal, contracts) = RELEVANT unless user is directly asked to act.
- Newsletters = RELEVANT. Software notifications = SPAM.
- When uncertain, default to ACTIONABLE > DEFERRED.

## Phishing

Flag separately if: sender domain does not match claimed service, redirect chains in links, bulk sender (SES/SendGrid) impersonating trusted service.

## Instructions

The calling agent will provide the `email` account address for your batch. Use it as the `email` parameter in every `manage_email` call.

1. For each message ID below, call `mcp__google-workspace__manage_email` with `operation: "read"`, the `email` parameter (provided with your batch assignment), and the `messageId`.
2. Read only the first ~500 words. Skip signatures, legal disclaimers, and quoted reply threads.
3. Classify and write results to your assigned output file as JSON:

```json
{
  "classifications": [
    {
      "message_id": "...",
      "sender": "...",
      "subject": "...",
      "classification": "ACTIONABLE|NON-ACTIONABLE",
      "sub": "URGENT|DEFERRED|RELEVANT|SPAM|DISCOVERY",
      "reason": "one-line explanation"
    }
  ],
  "errors": []
}
```

4. Process ALL assigned message IDs. Do not skip any.
5. When done, report: "Processed X/Y emails, results in [path]".
