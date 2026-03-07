#### Classification Decision Tree

Every email gets one top-level classification and one sub-classification. Work through the tree top-down:

1. **Does this email require the user to DO something?** (respond, sign, review, decide, schedule, follow up)
   - YES → ACTIONABLE
     - Is it time-sensitive (deadline within 48h) or quick (< 5 min)? → URGENT
     - Otherwise → DEFERRED
   - NO → NON-ACTIONABLE
     - Is it relevant to the user's current work, projects, or interests? → RELEVANT
     - Otherwise → NON-APPLICABLE
       - Is it junk, mass marketing, or tool noise? → SPAM
       - Could it be interesting as a new opportunity or trend? → DISCOVERY

```
Email
+-- ACTIONABLE -- requires the user to do something
|   +-- URGENT -- quick (< 5 min), time-sensitive, or has a near deadline
|   +-- DEFERRED -- needs thoughtful attention, can be scheduled
|
+-- NON-ACTIONABLE -- no action required from the user
    +-- RELEVANT -- applies to current work, projects, interests, or life areas
    +-- NON-APPLICABLE -- does not match current context
        +-- SPAM -- junk, unsolicited offers, mass marketing, tool noise
        +-- DISCOVERY -- potentially interesting new topic, trend, or opportunity
```

#### First-Principles Classification Guide

Think about each email along these dimensions:

**Is there a required action?**
- Documents requiring signature → ACTIONABLE
- Tasks assigned or overdue in any project management / HR / CRM tool → ACTIONABLE
- Meeting requests needing a response → ACTIONABLE (check calendar for conflicts)
- Review requests (code, documents, applications) → ACTIONABLE
- Direct questions from colleagues, clients, or partners → ACTIONABLE
- Pure notifications, confirmations, receipts → NON-ACTIONABLE

**How urgent is the action?**
- Explicit deadline within 48 hours → URGENT
- Can be completed in under 5 minutes → URGENT
- Needs research, thought, or coordination → DEFERRED
- First pass by someone else before user's turn → DEFERRED

**Is non-actionable content relevant?**
- Relates to a project the user is actively working on → RELEVANT
- From a newsletter or source the user chose to subscribe to → RELEVANT
- User is CC'd on a topic they care about → RELEVANT
- Automated noise from tools the user doesn't actively monitor → SPAM
- Unsolicited sales, marketing, promotions → SPAM
- Well-targeted outreach or emerging trends outside current focus → DISCOVERY

#### Reference Examples (non-exhaustive — use as pattern guides, not hard rules)

These are known patterns from the user's history. New tools, senders, and patterns will appear — classify them from first principles using the guide above.

ACTIONABLE > URGENT (examples):
- DocuSign signature requests (flag phishing if sender is unusual)
- Overdue tasks or direct review requests in HR/recruiting tools (e.g. Ashby)
- CRM follow-ups specifically assigned to the user (e.g. Hubspot)
- Client or lead conversations requiring response (e.g. AWS marketplace)
- Video/async tool comments needing review (e.g. Loom)

ACTIONABLE > DEFERRED (examples):
- Application reviews where others triage first (e.g. Ashby pipeline)
- Goal-setting or performance review notifications (e.g. Leapsome)
- Shared document review requests (Google Docs/Slides/Sheets)
- Conference or education event invitations needing calendar check
- Direct emails from interns, potential employees, or collaborators
- Testing/competition notifications (e.g. Kaggle)

NON-ACTIONABLE > RELEVANT (examples):
- Newsletters the user actively reads
- Health/wellness device notifications (e.g. Oura)
- Course or learning platform emails (e.g. Neural System Mastery)
- CC'd emails on topics matching user's active projects

NON-ACTIONABLE > SPAM (examples):
- Automated notifications from productivity/time-tracking tools the user doesn't actively check (e.g. Productive, Rize)
- Financial service notifications not requiring action (e.g. N26, Wise, PayPal)
- Social media notifications (e.g. Pinterest, Discord)
- Auto-assignment notifications from CRM (e.g. "You have been made the Contact owner")
- Unsolicited service offerings (translation, outsourcing, marketing, lead gen)
- Retail promotions and ads

NON-ACTIONABLE > DISCOVERY (examples):
- Service offerings that could be a genuine business match
- Emerging tech, industry trends, or opportunities outside current focus
- Cold outreach that is well-targeted and novel
