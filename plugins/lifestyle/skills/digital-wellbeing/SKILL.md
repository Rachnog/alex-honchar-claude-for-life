---
name: digital-wellbeing
description: Digital-wellbeing lens on Apple Screen Time — how much you live on screens and your phone, so you don't end up chronically online. Use for "screen time", "phone usage", "am I on my phone too much", "digital detox", "screen balance", "too much time online", "phone addiction", "device time", "presence", "touch grass". Lifestyle-area analysis of volume and balance; for the QUALITY of what you consume use the mind `info-diet` skill instead.
---

# Digital wellbeing (lifestyle lens)

Measures **how much of your life happens on a screen** — total device time, phone
dominance, and whether you're living chronically online — using unified Apple Screen
Time (Mac + iPhone). The question is *volume and balance*, NOT content quality (that's
the mind `info-diet` skill). Same underlying data, different question.

## Get the data
Run the bundled extractor (self-contained — Python stdlib + vendored `ccl_segb`; needs
**Full Disk Access**), or read the latest vault snapshot if fresh:
```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/digital-wellbeing/screentime_extract.py" --days 7 \
        --snapshot-dir "<vault>/400 Resources/screentime"
```
- Source: `~/Library/Biome/streams/restricted/App.InFocus/` — `local/` = this Mac,
  `remote/<uuid>/` = each iCloud-synced device (Screen Time → Share Across Devices ON).
- `(idle/system)` = lock/StandBy/Universal Control — count it as "device on, not used",
  and keep it separate from real usage. Only source of true **iPhone** time.

## The lens: volume & balance
- **Total device time/day** (Mac + iPhone summed) and the trend — is it climbing?
- **Phone dominance**: iPhone hours ÷ total. A high phone share is the chronic-online
  signal, since the phone follows you everywhere.
- **Biggest time-sinks** by raw hours (the apps eating your day), phone first.
- **Idle/StandBy share**: high `(idle/system)` on iPhone often = phone constantly in
  hand/on the dock — a presence red flag even when not "using" an app.
- Compare **online vs. offline**: waking hours minus device time ≈ life off the screen.

## Report
- Lead with a blunt number: "You spent ~Xh/day on screens, Yh of it on your phone."
- Name the top phone sink and quantify it. Flag if total or phone share is trending up.
- Recommend for **lifestyle/presence**, not the brain: phone-free windows (meals, first
  hour, bedroom), leaving the phone in another room, a daily cap. Ground in `300 Areas/4
  Lifestyle` protocols. Voice guide applies (concrete, take a position, end with a rec).
- If the user asks about *what* they consume (feeds vs reading), hand off to the mind
  `info-diet` skill.

## Provenance
`ccl_segb/` is CCL Forensics' MIT-licensed SEGB parser (github.com/cclgroupltd/ccl-segb).
`reference_schema.proto` documents the App.InFocus protobuf. The extractor hand-rolls a
3-field protobuf decoder — no runtime dependencies beyond the Python stdlib.
