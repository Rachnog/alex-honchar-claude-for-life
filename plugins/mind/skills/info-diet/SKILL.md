---
name: info-diet
description: Information-diet lens on Apple Screen Time — what you feed your brain, not how long you're on a device. Use for "info diet", "information diet", "what am I consuming", "reading vs feeds", "am I doomscrolling", "attention quality", "is my content junk or nutrition", "social feed time", "news vs deep reading". Mind-area analysis; for total screen/phone volume use the lifestyle `digital-wellbeing` skill instead.
---

# Information diet (mind lens)

Judges the **quality of what your brain consumes**, using unified Apple Screen Time
(Mac + iPhone). The question is *nutrition vs. junk* — intentional/deep intake vs.
passive algorithmic feeds — NOT total hours (that's the lifestyle `digital-wellbeing`
skill). Same underlying data, different question.

## Get the data
Run the bundled extractor (self-contained — Python stdlib + vendored `ccl_segb`; needs
**Full Disk Access**), or read the latest vault snapshot if fresh:
```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/info-diet/screentime_extract.py" --days 30 \
        --snapshot-dir "<vault>/400 Resources/screentime"
```
The extractor is identical to the lifestyle `digital-wellbeing` copy (App.InFocus SEGB →
per-app/device/day); see that skill's provenance notes for internals.

## The lens: categorize by information TYPE
Bucket app time into:
- **Algorithmic feeds** (junk risk — passive, engineered-for-engagement): Instagram
  `com.burbn.instagram`, X/Twitter, TikTok `com.zhiliaoapp.musically`, Reddit, Facebook,
  YouTube feed `com.google.ios.youtube`, LinkedIn feed `com.linkedin.LinkedIn`.
- **News/current**: news apps, browser news reading.
- **Deep / learning / creation** (nutrition): Obsidian `md.obsidian`, Claude
  `com.anthropic.claude*`, Books/Kindle, Readwise, long-form reading, courses.
- **Messaging** (communication, not diet): WhatsApp, Telegram `ph.telegra.Telegraph`,
  Slack `com.tinyspeck.chatlyio`, Messages.
- **Video/entertainment**: Netflix, YouTube (lean-back).

## Report
- Lead with the **feed-junk : deep-intake ratio** and the single biggest algorithmic
  sink (usually a social feed on iPhone). Trend it across snapshots if history exists.
- Separate **iPhone** (where feeds dominate) from Mac (where deep work lives).
- Ignore the `(idle/system)` bucket — it's not consumption.
- Take a position and recommend for the **brain**: e.g. "Instagram is 60% of your feed
  intake at Xh/wk — cap it, replace with the reading queue." Ground in the `300 Areas/3
  Mind` protocols. Voice guide applies (concrete, <25-word sentences, end with a rec).
