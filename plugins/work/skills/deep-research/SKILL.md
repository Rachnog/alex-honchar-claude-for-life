---
name: deep-research
description: >
  Launch a deep research query across 10 AI platforms simultaneously using browser automation.
  Opens ChatGPT, Claude, Gemini, Grok, Parallel, Perplexity, Manus, DeepSeek, Mistral, and Kimi
  in separate browser tabs, enables each platform's deep/expert research mode, enters the user's
  query, and monitors progress. Use this skill whenever the user says "deep research", "research
  this across platforms", "multi-platform research", "run research everywhere", "parallel research",
  "compare AI research", or any variation of wanting to query multiple AI chatbots at once for
  in-depth research. Also triggers when the user mentions wanting to use multiple AI tools for
  research, or asks to "search all AIs", "ask all the AIs", or "get research from every platform".
compatibility:
  - tool: mcp__claude-in-chrome__tabs_context_mcp
  - tool: mcp__claude-in-chrome__tabs_create_mcp
  - tool: mcp__claude-in-chrome__navigate
  - tool: mcp__claude-in-chrome__computer
  - tool: mcp__claude-in-chrome__find
  - tool: mcp__claude-in-chrome__read_page
  - tool: mcp__claude-in-chrome__form_input
  - tool: mcp__claude-in-chrome__get_page_text
---

# Deep Research Across 10 AI Platforms

This skill automates launching a deep research query across 10 AI platforms in parallel using Claude in Chrome browser automation. The user provides a research query, and you open all platforms in separate tabs, enable their respective deep research modes, enter the query, and monitor progress.

## Prerequisites

The user must already be logged into all 10 platforms in their Chrome browser. Do not attempt to log in on their behalf.

## Platform Registry

Each platform has a URL, and a specific sequence of UI actions to enable deep research mode before entering the query. Here they are:

| # | Platform | URL | Deep Research Activation |
|---|----------|-----|--------------------------|
| 1 | ChatGPT | `https://chatgpt.com/` | Click the "+" button, then select "Deep Research" |
| 2 | Claude | `https://claude.ai/new` | Click the "+" button, then select "Research" |
| 3 | Gemini | `https://gemini.google.com/app` | Click "Tools", then select "Deep Research" |
| 4 | Grok | `https://grok.com/` | Click "Expert" to the right of the search bar |
| 5 | Parallel | `https://platform.parallel.ai/play/deep-research` | Select "Ultra8x" from the dropdown in the search bar |
| 6 | Perplexity | `https://www.perplexity.ai/` | Click the "+" button, then select "Deep Research" |
| 7 | Manus | `https://manus.im/app` | On the bottom right of the search bar, click "More", then select "Wide Research" |
| 8 | DeepSeek | `https://chat.deepseek.com/` | Click "DeepThink" and "Search" under the search bar |
| 9 | Mistral | `https://chat.mistral.ai/chat` | Click "Research" under the search bar |
| 10 | Kimi | `https://www.kimi.com/deep-research` | Verify that "Agent\|Deep Research" is already selected |

## Workflow

### Phase 1: Get the Research Query

Ask the user for their research query if they haven't already provided one.

**CRITICAL — Query Preservation Rule**: Use the user's query EXACTLY as provided. Do NOT rephrase, reword, shorten, expand, or "improve" it in any way. Copy the text character-for-character into every platform. If you feel the query is ambiguous, ask the user to clarify — do not silently modify it.

### Phase 2: Open All Tabs

1. Call `tabs_context_mcp` to get the current browser state.
2. Create 10 new tabs using `tabs_create_mcp` (one per platform). Record each tab ID.
3. Navigate each tab to its respective platform URL using `navigate`. Do this for all 10 tabs — you can issue multiple navigate calls in the same turn since they are independent.
4. Wait a few seconds for pages to load (`computer` with `action: wait`).

### Phase 3: Enable Deep Research Mode (Per Platform)

Work through each tab to enable the platform's deep research mode. Because each platform has a different UI, you need to handle them individually. Take a screenshot of each tab before interacting to understand the current state.

The general approach for each platform:

1. **Take a screenshot** to see the current UI state.
2. **Use `find` or `read_page`** to locate the relevant UI elements (buttons, dropdowns, menus).
3. **Click the activation elements** in sequence per the Platform Registry above.
4. **Verify** the mode is active by taking another screenshot or reading the page.

Tips for specific platforms:

- **ChatGPT**: The "+" button is typically near the message input area. After clicking it, a menu appears — look for "Deep Research" in the menu items.
- **Claude**: Similar to ChatGPT — "+" button near the input, then select "Research" from the menu. If the `find` tool doesn't work to locate the "Research" menuitem, use `read_page` with `filter: "interactive"` to get all interactive elements and find the one labeled "Research". **HARD GATE — Never fall back to standard chat**: If after trying both `find` and `read_page` you still cannot locate the "Research" mode option, do NOT submit the query in regular chat mode. Instead, stop, tell the user: "I cannot find the Research mode option on Claude. Please enable it manually (it may need to be turned on in your Claude settings or plan), then let me know when it's ready." Wait for the user to confirm before proceeding with Claude's tab. IMPORTANT: After submitting the research query, Claude will ask for **tool use permission** (e.g., "Allow Claude to use web search?" or similar). The user must manually accept this in their browser — remind the user to allow it when you see it, or note in your status report that Claude needs tool use approval.
- **Gemini**: "Tools" is typically a button/tab in the UI. After clicking, look for "Deep Research" option. Gemini may show a research plan — accept the default plan without modification.
- **Grok**: "Expert" appears as a mode selector near/right of the search bar. It may be a toggle or button.
- **Parallel**: There's a dropdown in the search bar area. Click it and select "Ultra8x".
- **Perplexity**: "+" button near the search input, then "Deep Research" from the resulting menu.
- **Manus**: IMPORTANT — The "More" button is NOT an icon on the search bar itself. There is a row of suggestion cards/buttons at the bottom of the chat area (e.g., "Travel Planning", "Data Analysis", "More"). The "More" button is the LAST item in this row of suggestion cards. Do NOT click the puzzle icon (that opens skills/plugins panel) or the model dropdown (that shows plan options). Click the "More" text in the suggestion cards row at the bottom. After clicking "More", a dropdown menu appears with "Wide Research" at the top — click it.
- **DeepSeek**: "DeepThink" and "Search" are separate toggles/buttons below the search bar. Enable both.
- **Mistral**: "Research" appears as a mode option under the search bar. Click to select it.
- **Kimi**: The URL already targets deep research. Just verify "Agent|Deep Research" is selected in the UI. If not, select it.

Process platforms in batches to balance speed with reliability. A good approach: handle 3-4 platforms, then move to the next batch. Take screenshots liberally — browser UIs change and you need to see what you're clicking.

### Phase 4: Enter the Query and Submit

For each platform tab:

1. Locate the text input / search bar / message box.
2. Click on it to focus.
3. Type the research query using `computer` with `action: type`.
4. Press Enter or click the submit/send button.

Move through all 10 tabs to enter and submit the query. Some platforms use a textarea, others use a contenteditable div — use `find` to locate the input element if clicking in the expected location doesn't work.

### Phase 5: Handle Follow-up Questions

Some platforms ask clarifying questions before starting the research. After submitting queries in all tabs:

1. Cycle through each tab and take a screenshot.
2. If a platform is asking a follow-up question or showing a confirmation dialog:
   - **Gemini research plan**: Accept the default plan. Click the accept/confirm button.
   - **Any other platform asking a question**: Report the question to the user in the chat. Tell them which platform is asking. Wait for the user's answer, then go back to that tab and provide the answer.
3. If a platform has already started researching (showing progress indicators, thinking animations, etc.), note it as "running" and move on.

### Phase 6: Monitor and Report

After all queries are launched:

1. Wait 30-60 seconds, then cycle through all tabs taking screenshots.
2. Report to the user which platforms are:
   - Still researching (show progress if visible)
   - Finished (have produced results)
   - Stuck or errored (need attention)
3. If any platform needs the user's input (follow-up questions that appeared after launch), surface those.
4. Continue monitoring every 60 seconds until the user tells you to stop, or all platforms have completed.

When reporting, keep it concise:
```
Research Status Update:
✅ Perplexity — Complete
✅ Gemini — Complete
🔄 ChatGPT — Still researching (~60% through)
🔄 Claude — Still researching
🔄 Grok — Still researching
❌ Manus — Needs your input (asking: "What specific aspects of X should I focus on?")
🔄 DeepSeek — Still researching
🔄 Mistral — Still researching
✅ Kimi — Complete
🔄 Parallel — Still researching
```

## Error Handling

- **Tab fails to load**: Retry navigation once. If it still fails, report to the user and continue with other platforms.
- **Platform not logged in**: If you see a login screen, tell the user which platform needs authentication and skip it. Do not attempt to log in.
- **UI element not found**: Take a screenshot, try `find` with different descriptions, and try `read_page` with interactive filter. If the element truly can't be found, report that the UI may have changed.
- **Platform timeout**: If a platform hasn't responded in 5 minutes during setup, skip it and report.

## Important Notes

- Always use `find` or `read_page` to locate elements rather than hard-coding coordinates. Platform UIs change frequently and coordinates will break.
- Take screenshots before and after major actions to verify success.
- When typing the query, be aware that some platforms may have character limits or may interpret certain characters specially. Type the query **exactly as provided by the user — character for character, including any unusual capitalisation, line breaks, bullet style, or apparent typos.** Do not normalise or improve the text.
- If a platform shows a CAPTCHA or bot detection, inform the user immediately — they'll need to handle it manually.

## Lessons from Live Testing

These tips come from actual test runs and address common pitfalls:

1. **Manus "More" button misidentification**: The Manus UI has multiple icons that look like they could be "More" — a puzzle icon (opens skills panel) and a model dropdown. The actual "More" is a text label in the suggestion cards row at the BOTTOM of the chat area, alongside cards like "Travel Planning" and "Data Analysis". Always scroll down and look for the suggestion cards row.

2. **Claude tool use permission**: After submitting a research query on Claude, it will prompt the user to allow tool use (web search, etc.). This is a browser-level permission dialog that the user must click "Allow" on manually. Remind the user to do this in your first status report, or it will sit waiting.

3. **Claude Research mode menu**: The "+" dropdown menu on Claude can be finicky — clicking by coordinates may not work reliably as the menu closes quickly. Use the `find` tool to locate the `menuitemcheckbox` for "Research" and click it via `ref` instead of coordinates.

4. **Parallel detach on long text**: Typing very long queries on Parallel may cause the browser tab to detach. If `type` fails, use `javascript_tool` to set the value directly on the `contenteditable` element: `el.innerText = "...query..."; el.dispatchEvent(new Event('input', { bubbles: true }));`

5. **Parallel START RESEARCH button**: After entering the query, Parallel requires clicking the orange "START RESEARCH →" button — pressing Enter alone does not start the research.

6. **Kimi follow-up questions**: Kimi frequently asks 5 clarifying questions before starting deep research. Surface these to the user or answer with reasonable defaults (open to all themes, any project size, open to collaboration, both Spanish and English, etc.) and instruct Kimi to proceed.

7. **Gemini auto-accept**: Gemini shows a research plan with "Edit plan" and "Start research" buttons. Per the skill instructions, always click "Start research" to accept the default plan without modification.

8. **Perplexity input element**: Perplexity uses a contenteditable `<div>` not a `<textarea>`. If `type` doesn't work, use `javascript_tool` to set `innerText` on the `[contenteditable="true"]` or `[role="textbox"]` element.

9. **Mistral "Start research" button**: After entering the query, Mistral's Research mode generates a research plan but does NOT auto-start execution. It displays "Edit" and "Start research" buttons. You MUST scroll down to find and click the "Start research" button explicitly, or Mistral will sit idle with the plan visible but no research running.

10. **Kimi quota exhaustion**: Kimi Deep Research has a usage quota that may be exhausted. When this happens, it shows "Quota used up" and "Starting Deep Research creates a new chat". There is no workaround — create a placeholder file with the conversation link and note that quota was exhausted.

11. **Chrome extension disconnects during long waits**: The Claude in Chrome extension frequently disconnects during 30-second `wait` actions. After any wait of 15+ seconds, always call `tabs_context_mcp` to reconnect before issuing further browser commands. If you get connection errors, `tabs_context_mcp` will re-establish the connection.

12. **Sibling tool call failures**: When making multiple parallel browser tool calls (e.g., `get_page_text` on 3 tabs simultaneously), if ONE call fails, ALL sibling calls in that batch also fail. Always retry failed calls individually rather than in another batch.

13. **ChatGPT canvas not extractable**: ChatGPT Deep Research produces results in a "canvas" document panel that is NOT accessible to browser automation. `get_page_text` returns only the user's query text. `read_page` shows internal links, not actual content. `javascript_tool` is blocked on chatgpt.com. Clicking expand, download, or title icons does not help. **Workaround**: Create a placeholder file with the ChatGPT conversation link and instruct the user to copy the content manually.

14. **Manus document extraction**: `get_page_text` fails on Manus with "No semantic content element found and page body is too large". The fix: at the bottom of the Manus chat, there is a document thumbnail/card showing the final report title (e.g., "Produce and deliver the final comprehensive report"). Click this card — it opens a document viewer modal. Then use `read_page` with `depth: 15` and `max_chars: 80000+` on the modal to extract the full report content from the accessibility tree.

15. **Query must be used verbatim**: Never paraphrase or rewrite the user's research query. Enter it character-for-character on every platform. Editing queries — even with good intentions — changes the research results and violates user intent.

16. **Claude Research mode is mandatory**: If the Research mode menu item cannot be found on Claude after exhausting `find` and `read_page` approaches, do NOT fall back to standard chat. Pause and ask the user to enable it manually, waiting for their confirmation before continuing.

## Phase 7: Result Extraction and Saving

After all platforms have completed (or timed out / errored), extract results and save them as individual markdown files. Each platform needs a different extraction strategy:

### Extraction Strategy Per Platform

| Platform | Method | Notes |
|----------|--------|-------|
| ChatGPT | ❌ Not extractable | Canvas content blocked. Save placeholder with link. |
| Claude | `read_page` on artifact panel | Click the artifact button to open the side panel, then `read_page` with `depth: 15` and `max_chars: 100000`. Content is in the `region "Artifact panel: ..."` subtree. |
| Gemini | `read_page` accessibility tree | Parse the accessibility tree, filtering for content nodes. May need `javascript_tool` to extract from JSON-like structures. |
| Grok | `get_page_text` | Works directly. Returns full report text. |
| Parallel | `get_page_text` | Works directly. Content may be in structured key-value format — reformat into clean markdown. |
| Perplexity | `get_page_text` | Works directly. Returns full report with citations. |
| Manus | `read_page` after clicking document | Click the document thumbnail at bottom of chat, then `read_page` with high `max_chars` on the opened viewer. |
| DeepSeek | `get_page_text` | Works directly. Returns full report text. |
| Mistral | `read_page` with high `max_chars` | `get_page_text` may exceed limits. Use `read_page` with `max_chars: 80000+`. Content includes search steps, sources, and analysis. |
| Kimi | `get_page_text` or placeholder | If completed, `get_page_text` works. If quota exhausted, save placeholder. |

### File Naming Convention

Save files as `{##}-{platform}.md` in the user-specified output directory:
```
01-chatgpt.md
02-claude.md
03-gemini.md
04-grok.md
05-parallel.md
06-perplexity.md
07-manus.md
08-deepseek.md
09-mistral.md
10-kimi.md
```

### File Format

Each file should include:
- Platform name and research mode used
- Stats (sources, time, steps) if available
- Direct link to the conversation/report
- Full extracted content formatted as clean markdown
- For placeholders: note explaining why content couldn't be extracted + conversation link

Use `Task` (Bash subagent) with heredoc to write large files, as direct `Write` tool may struggle with very long content.
