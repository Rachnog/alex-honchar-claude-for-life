#!/usr/bin/env python3
"""
Apple Screen Time extractor — unified Mac + iPhone/iPad app usage.

Reads the Biome App.InFocus streams (SEGB v2), pairs focus gain/loss events into
foreground sessions per device, and aggregates seconds per (device, app, day).

Self-contained: stdlib + vendored ccl_segb (CCL Forensics, MIT). No network, no
protobuf runtime — a tiny hand-rolled decoder reads the 3 fields we need.

Data source: ~/Library/Biome/streams/restricted/App.InFocus/{local,remote/<uuid>}/
Device names:  ~/Library/Biome/sync/sync.db  (DevicePeer)
Requires: Full Disk Access for the running process.

Usage:
  python3 screentime_extract.py [--days N] [--csv OUT.csv] [--json OUT.json]
"""
import os, sys, struct, glob, sqlite3, datetime, collections, csv, json, shutil, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ccl_segb.ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState

HOME = os.path.expanduser("~")
AIF = os.path.join(HOME, "Library/Biome/streams/restricted/App.InFocus")
SYNC_DB = os.path.join(HOME, "Library/Biome/sync/sync.db")
CF_OFFSET = 978307200          # CFAbsoluteTime (2001) -> unix epoch
MAX_SESSION = 3 * 3600         # cap a single foreground session (device-idle guard)

# ---- minimal protobuf wire decoder (AppInFocusEvent: f3=in_foreground varint,
#      f4=cf_absolute_time double, f6=bundle_id string) --------------------------
def _varint(b, i):
    shift = val = 0
    while True:
        x = b[i]; i += 1
        val |= (x & 0x7f) << shift
        if not (x & 0x80): return val, i
        shift += 7

def parse_appinfocus(data):
    i, n, fg, t, bundle = 0, len(data), None, None, None
    try:
        while i < n:
            tag, i = _varint(data, i); fnum, wt = tag >> 3, tag & 7
            if wt == 0:
                v, i = _varint(data, i)
                if fnum == 3: fg = v
            elif wt == 1:
                if fnum == 4: t = struct.unpack("<d", data[i:i+8])[0]
                i += 8
            elif wt == 2:
                ln, i = _varint(data, i)
                if fnum == 6: bundle = data[i:i+ln].decode("utf-8", "replace")
                i += ln
            elif wt == 5:
                i += 4
            else:
                break
    except (IndexError, struct.error):
        pass
    return fg, t, bundle

# ---- idle / non-app pseudo-bundles: real foreground but not "app use" ---------
IDLE_EXACT = {"com.apple.loginwindow", "com.apple.universalcontrol",
              "com.apple.ScreenTimeAgent", "com.apple.SpringBoard"}
IDLE_PREFIXES = ("com.apple.springboard",)   # stand-by, lock-screen, home-screen, today-view
def norm_bundle(b):
    if b in IDLE_EXACT or b.startswith(IDLE_PREFIXES):
        return "(idle/system)"
    return b

# ---- device identity ---------------------------------------------------------
PLATFORM = {2: "iOS", 3: "macOS", 4: "macOS", 6: "iPadOS"}
def device_labels():
    out = {}
    try:
        tmp = SYNC_DB + ".probe"; shutil.copy2(SYNC_DB, tmp)
        con = sqlite3.connect(tmp); con.row_factory = sqlite3.Row
        for r in con.execute("SELECT device_identifier,me,name,model,platform FROM DevicePeer"):
            out[r["device_identifier"]] = {
                "me": bool(r["me"]),
                "platform": PLATFORM.get(r["platform"], f"plat{r['platform']}"),
                "model": (r["model"] or "").strip(),
                "name": (r["name"] or "").strip(),
            }
        con.close(); os.remove(tmp)
    except Exception:
        pass
    return out

def label_for(uuid, me_is_mac, labels):
    if uuid == "local":
        return "Mac (this device)"
    d = labels.get(uuid)
    if not d:
        return f"unknown·{uuid[:8]}"
    nm = d["name"] or d["model"] or uuid[:8]
    return f"{d['platform']}·{nm}"

# ---- read + pair -------------------------------------------------------------
def iter_device_dirs():
    loc = os.path.join(AIF, "local")
    if os.path.isdir(loc): yield ("local", loc)
    rem = os.path.join(AIF, "remote")
    if os.path.isdir(rem):
        for d in sorted(os.listdir(rem)):
            p = os.path.join(rem, d)
            if os.path.isdir(p): yield (d, p)

def collect_events(device_dir):
    evs = []
    for f in glob.glob(os.path.join(device_dir, "*")):
        if os.path.isdir(f) or os.path.basename(f) == "lock":
            continue
        try:
            for e in read_segb_file(f):
                if e.state != EntryState.Written:
                    continue
                fg, t, b = parse_appinfocus(e.data)
                if t is None or b is None:
                    continue
                evs.append((t, 1 if fg else 0, b))
        except Exception:
            continue
    return sorted(set(evs))

def sessions(evs):
    """An app is foreground from its focus-gain until the next focus event."""
    cur = start = None
    for t, fg, b in evs:
        if cur is not None and t > start:
            dur = min(t - start, MAX_SESSION)
            if dur > 0:
                yield (start, dur, cur)
            cur = start = None
        if fg == 1:
            cur, start = b, t
    # trailing open session is left unclosed (no end event) — intentionally dropped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None, help="only include the last N days")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--snapshot-dir", default=None,
                    help="write a dated CSV + latest.json here (for building history)")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    if not os.path.isdir(AIF):
        print("App.InFocus stream not found — is this a Mac with Screen Time sync?", file=sys.stderr)
        sys.exit(2)

    cutoff = None
    if args.days:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=args.days)).timestamp()

    labels = device_labels()
    # agg[(device_label, date, bundle)] = seconds
    agg = collections.defaultdict(float)
    dev_totals = collections.defaultdict(float)
    dev_daterange = {}

    for uuid, ddir in iter_device_dirs():
        lbl = label_for(uuid, True, labels)
        evs = collect_events(ddir)
        if not evs:
            continue
        for start_cf, dur, bundle in sessions(evs):
            unix = start_cf + CF_OFFSET
            if cutoff and unix < cutoff:
                continue
            dt = datetime.datetime.fromtimestamp(unix)
            day = dt.strftime("%Y-%m-%d")
            agg[(lbl, day, norm_bundle(bundle))] += dur
            dev_totals[lbl] += dur
            lo, hi = dev_daterange.get(lbl, (day, day))
            dev_daterange[lbl] = (min(lo, day), max(hi, day))

    # ---- report ----
    rows = [{"device": d, "date": day, "bundle_id": b,
             "seconds": round(s), "hours": round(s/3600, 3)}
            for (d, day, b), s in agg.items()]
    rows.sort(key=lambda r: (r["device"], r["date"], -r["seconds"]))

    print(f"\n=== Screen Time (App.InFocus) — {len(rows)} device-day-app rows ===")
    for dev in sorted(dev_totals, key=lambda d: -dev_totals[d]):
        lo, hi = dev_daterange[dev]
        print(f"\n▶ {dev}   {dev_totals[dev]/3600:.1f}h total   [{lo} … {hi}]")
        by_app = collections.defaultdict(float)
        for (d, day, b), s in agg.items():
            if d == dev: by_app[b] += s
        for b, s in sorted(by_app.items(), key=lambda x: -x[1])[:args.top]:
            print(f"    {s/3600:6.2f}h  {b}")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["device", "date", "bundle_id", "seconds", "hours"])
            w.writeheader(); w.writerows(rows)
        print(f"\ncsv -> {args.csv} ({len(rows)} rows)")
    if args.json:
        json.dump({"generated_unix": None, "rows": rows,
                   "device_totals_hours": {d: round(s/3600, 2) for d, s in dev_totals.items()}},
                  open(args.json, "w"), indent=2)
        print(f"json -> {args.json}")

    if args.snapshot_dir:
        os.makedirs(args.snapshot_dir, exist_ok=True)
        maxday = max((r["date"] for r in rows), default=datetime.date.today().isoformat())
        snap = os.path.join(args.snapshot_dir, f"screentime-{maxday}.csv")
        with open(snap, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["device", "date", "bundle_id", "seconds", "hours"])
            w.writeheader(); w.writerows(rows)
        summary = {"through": maxday, "window_days": args.days,
                   "device_totals_hours": {d: round(s/3600, 2) for d, s in dev_totals.items()}}
        json.dump(summary, open(os.path.join(args.snapshot_dir, "latest.json"), "w"), indent=2)
        print(f"snapshot -> {snap}  (+ latest.json)")

if __name__ == "__main__":
    main()
