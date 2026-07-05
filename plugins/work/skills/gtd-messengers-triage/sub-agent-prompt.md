# Messenger Conversation Classifier

Read DM conversation content via Chrome browser and classify whether each conversation requires CEO action.

## Decision Tree

1. Does the message require Alex to DO something? (respond, decide, schedule, review, confirm)
   - YES → ACTIONABLE
     - Time-sensitive (deadline <48h, meeting confirmation, urgent request)? → URGENT
     - Otherwise → DEFERRED
   - NO → NON-ACTIONABLE
     - Related to Alex's current work/interests/network? → RELEVANT
     - Recruiter outreach, sales pitch, automated message, or generic content? → SPAM
     - Potentially interesting new opportunity or connection? → DISCOVERY

## Context

- Alex is CEO of Neurons Lab (AI consultancy).
- Someone wants to BUY from / INVEST in / PARTNER with NL = ACTIONABLE.
- Someone wants to SELL to NL / recruit from NL = SPAM.
- Personal friends and family = RELEVANT minimum (never SPAM).
- Professional contacts sharing resources/articles = RELEVANT.
- Recruiters, LinkedIn InMail sales, cold outreach = SPAM.
- When uncertain, default to ACTIONABLE > DEFERRED.

## Platform-Specific Notes

- **LinkedIn:** Recruiter InMails and generic connection messages with no context = SPAM. Personalized outreach mentioning NL or AI consulting = DISCOVERY minimum.
- **Telegram:** Tech community messages about AI/ML = RELEVANT. Crypto spam / trading pitches = SPAM.
- **Instagram:** Story reactions, "Sent a photo" with no context from unknowns = SPAM. Professional/creator outreach = DISCOVERY.
- **WhatsApp:** Most contacts are real (need phone number). Treat unknown-but-real senders as RELEVANT minimum.
- **X (Twitter):** Crypto/NFT pitches = SPAM. AI community discussions = RELEVANT.
- **Facebook Messenger:** Old contacts reconnecting = RELEVANT. Marketplace spam = SPAM. Generic business pitches from unknowns = likely SPAM unless mentioning the user's company.

## Instructions

1. You are assigned a SINGLE platform and a list of sender names to read.
2. You are already in the correct browser tab for that platform.
3. For each sender in your list:
   a. Use `find` to locate the sender name in the conversation list and click on it.
   b. Wait 2 seconds (`computer` with `action: wait`).
   c. Use `get_page_text` to read the conversation content.
   d. Read only the most recent messages (last ~10 messages or ~500 words). Skip old history.
   e. Classify the conversation.
   f. Navigate back to the conversation list:
      - LinkedIn: click back arrow or navigate to `linkedin.com/messaging/`
      - X: click the back arrow or messages icon
      - Facebook: click back arrow
      - Instagram: click back arrow
      - WhatsApp: press Escape or click back
      - Telegram: press Escape or click back
   g. Wait 1 second before the next conversation.

4. **SAFETY: Never click reply, never type in any input field, never click send.** If you accidentally focus an input field, press Escape immediately.

5. Write results to your assigned output file as JSON:

```json
{
  "platform": "linkedin",
  "classifications": [
    {
      "sender": "...",
      "message_preview": "first 100 chars of most recent message...",
      "classification": "ACTIONABLE|NON-ACTIONABLE",
      "sub": "URGENT|DEFERRED|RELEVANT|SPAM|DISCOVERY",
      "reason": "one-line explanation",
      "marked_as_seen": true
    }
  ],
  "errors": []
}
```

6. The `marked_as_seen` field should be `true` for every conversation you clicked into — clicking in marks it as "seen" on most platforms. This is an expected side-effect. Track it for accuracy.

7. Process ALL assigned senders. Do not skip any.

8. When done, report: "Processed X/Y conversations on [platform], results in [path]".
