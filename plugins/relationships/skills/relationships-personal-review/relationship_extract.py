#!/usr/bin/env python3
"""relationship_extract.py -- metadata-only relationship interaction extractor.

Reads local macOS communication databases and emits per-contact interaction
METADATA only -- who, when, how often, and who initiated. It NEVER reads,
stores, or emits message text. Sources:

  - iMessage / SMS        ~/Library/Messages/chat.db
  - Call history          ~/Library/Application Support/CallHistoryDB/CallHistory.storedata
  - WhatsApp (Mac app)    ~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite

These are the personal channels Clay/Mesh is blind to. The extractor exists so a
relationships review can measure the inner circle (partner, family, close
friends) instead of falsely reporting them as "neglected" from professional CRM
recency.

Design mirrors the lifestyle/digital-wellbeing screentime extractor:
  * pure Python stdlib -- no dependencies, no network
  * copies each DB (+ -wal/-shm) to a temp file before opening read-only, so the
    live database is never locked
  * degrades gracefully -- a missing/locked source is reported, not fatal
Requires Full Disk Access for the host process (same grant as the screentime skill).

Usage:
  python3 relationship_extract.py --days 30
  python3 relationship_extract.py --since 2026-03-01 --until 2026-07-01 --monthly --json
  python3 relationship_extract.py --days 120 --snapshot-dir "<vault>/400 Resources/relationships"
"""

import argparse
import csv
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta

APPLE_EPOCH = 978307200  # 2001-01-01T00:00:00Z in unix seconds (Core Data / Cocoa epoch)

HOME = os.path.expanduser("~")
IMESSAGE_DB = os.path.join(HOME, "Library/Messages/chat.db")
CALL_DB = os.path.join(HOME, "Library/Application Support/CallHistoryDB/CallHistory.storedata")
WHATSAPP_DB = os.path.join(
    HOME, "Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite"
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def apple_to_unix(v):
    """Convert a Core Data / iMessage timestamp to unix seconds.

    Call history and WhatsApp store seconds-since-2001 (float). Modern iMessage
    stores nanoseconds-since-2001; very old rows store seconds. Detect by size.
    """
    if v is None:
        return None
    v = float(v)
    if v > 1e11:  # nanoseconds
        v = v / 1e9
    return v + APPLE_EPOCH


def norm_key(handle):
    """Normalize a phone / JID / email handle to a cross-channel match key.

    Phone-like -> last 9 digits (so +34 6xx / 6xx / JID 34xxx all collapse).
    Email / username -> lowercased as-is.
    """
    if not handle:
        return None
    handle = str(handle).strip()
    local = handle.split("@")[0]
    digits = re.sub(r"\D", "", local)
    if digits and len(digits) >= 7:
        return digits[-9:] if len(digits) >= 9 else digits
    return handle.lower() or None


def mask(handle):
    """Mask a raw handle for terminal display (keep last 4)."""
    if not handle:
        return "?"
    s = str(handle).split("@")[0]
    return ("*" * max(0, len(s) - 4)) + s[-4:] if len(s) > 4 else s


def month_key(unix):
    return datetime.fromtimestamp(unix).strftime("%Y-%m")


def open_ro(path):
    """Copy a sqlite DB (and its -wal/-shm sidecars) to temp, open read-only.

    Returns (connection, tempdir) or raises. Caller removes tempdir.
    """
    tmpdir = tempfile.mkdtemp(prefix="relext_")
    base = os.path.join(tmpdir, "db.sqlite")
    shutil.copy2(path, base)
    for ext in ("-wal", "-shm"):
        if os.path.exists(path + ext):
            try:
                shutil.copy2(path + ext, base + ext)
            except OSError:
                pass
    con = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    return con, tmpdir


# --------------------------------------------------------------------------- #
# accumulator
# --------------------------------------------------------------------------- #
def new_channel():
    return {
        "count": 0,
        "sent": 0,      # I initiated / outgoing
        "recv": 0,      # they initiated / incoming
        "missed": 0,    # incoming unanswered (calls only)
        "minutes": 0.0, # connected call minutes (calls only)
        "first": None,
        "last": None,
    }


class Contacts:
    def __init__(self, monthly=False):
        self.monthly = monthly
        self.data = {}  # key -> record

    def _rec(self, key):
        if key not in self.data:
            self.data[key] = {
                "labels": {},                       # name -> hits (pick most frequent)
                "handles": set(),
                "channels": defaultdict(new_channel),
                "monthly": defaultdict(lambda: defaultdict(int)),  # channel -> YYYY-MM -> count
            }
        return self.data[key]

    def add(self, key, handle, label, channel, unix, direction, minutes=0.0, missed=False):
        if key is None:
            return
        rec = self._rec(key)
        if handle:
            rec["handles"].add(str(handle))
        if label:
            rec["labels"][label] = rec["labels"].get(label, 0) + 1
        ch = rec["channels"][channel]
        ch["count"] += 1
        if direction == "sent":
            ch["sent"] += 1
        else:
            ch["recv"] += 1
        if missed:
            ch["missed"] += 1
        ch["minutes"] += minutes
        if ch["first"] is None or unix < ch["first"]:
            ch["first"] = unix
        if ch["last"] is None or unix > ch["last"]:
            ch["last"] = unix
        if self.monthly:
            rec["monthly"][channel][month_key(unix)] += 1

    def best_label(self, rec):
        if rec["labels"]:
            return max(rec["labels"].items(), key=lambda kv: kv[1])[0]
        for h in sorted(rec["handles"]):
            return mask(h)
        return "?"


# --------------------------------------------------------------------------- #
# source readers  (metadata columns ONLY -- no text/body columns are selected)
# --------------------------------------------------------------------------- #
def read_imessage(contacts, since, until, status):
    if not os.path.exists(IMESSAGE_DB):
        status["imessage"] = {"ok": False, "reason": "not found"}
        return
    con = tmpdir = None
    try:
        con, tmpdir = open_ro(IMESSAGE_DB)
        cur = con.execute(
            "SELECT h.id, m.is_from_me, m.date "
            "FROM message m JOIN handle h ON m.handle_id = h.ROWID "
            "WHERE m.item_type = 0 AND m.associated_message_type = 0 "
            "AND m.cache_roomnames IS NULL"  # 1:1 only, exclude group chats
        )
        rows = 0
        for handle, is_from_me, date in cur:
            unix = apple_to_unix(date)
            if unix is None or unix < since or unix >= until:
                continue
            contacts.add(
                norm_key(handle), handle, None, "imessage", unix,
                "sent" if is_from_me else "recv",
            )
            rows += 1
        status["imessage"] = {"ok": True, "rows": rows}
    except Exception as e:  # noqa: BLE001 -- degrade gracefully
        status["imessage"] = {"ok": False, "reason": str(e)}
    finally:
        if con:
            con.close()
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def read_calls(contacts, since, until, status):
    if not os.path.exists(CALL_DB):
        status["call"] = {"ok": False, "reason": "not found"}
        return
    con = tmpdir = None
    try:
        con, tmpdir = open_ro(CALL_DB)
        cur = con.execute(
            "SELECT ZADDRESS, ZNAME, ZORIGINATED, ZANSWERED, ZDATE, ZDURATION "
            "FROM ZCALLRECORD"
        )
        rows = 0
        for addr, name, originated, answered, zdate, dur in cur:
            unix = apple_to_unix(zdate)
            if unix is None or unix < since or unix >= until:
                continue
            direction = "sent" if originated else "recv"
            missed = (not originated) and (not answered)
            minutes = (float(dur) / 60.0) if dur else 0.0
            contacts.add(
                norm_key(addr), addr, name, "call", unix, direction,
                minutes=minutes, missed=missed,
            )
            rows += 1
        status["call"] = {"ok": True, "rows": rows}
    except Exception as e:  # noqa: BLE001
        status["call"] = {"ok": False, "reason": str(e)}
    finally:
        if con:
            con.close()
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def read_whatsapp(contacts, since, until, status, groups=None):
    if not os.path.exists(WHATSAPP_DB):
        status["whatsapp"] = {"ok": False, "reason": "not found"}
        return
    con = tmpdir = None
    try:
        con, tmpdir = open_ro(WHATSAPP_DB)
        # 1:1 sessions only (individual JIDs). Groups end in @g.us; other odd
        # JIDs (@lid, status@broadcast) are excluded.
        sessions = {}
        for pk, jid, name in con.execute(
            "SELECT Z_PK, ZCONTACTJID, ZPARTNERNAME FROM ZWACHATSESSION "
            "WHERE ZCONTACTJID LIKE '%@s.whatsapp.net'"
        ):
            sessions[pk] = (jid, name)
        rows = 0
        for sess_pk, is_from_me, zdate in con.execute(
            "SELECT ZCHATSESSION, ZISFROMME, ZMESSAGEDATE FROM ZWAMESSAGE "
            "WHERE ZMESSAGEDATE IS NOT NULL"
        ):
            sess = sessions.get(sess_pk)
            if not sess:
                continue  # group or non-1:1 session
            unix = apple_to_unix(zdate)
            if unix is None or unix < since or unix >= until:
                continue
            jid, name = sess
            contacts.add(
                norm_key(jid), jid, name, "whatsapp", unix,
                "sent" if is_from_me else "recv",
            )
            rows += 1
        # Group participation (aggregate, metadata only). The desktop DB DOES store
        # group message rows; report volume + your own share (are you present but silent?).
        if groups is not None:
            lo, hi = since - APPLE_EPOCH, until - APPLE_EPOCH
            for gname, gjid, gmsgs, gmine in con.execute(
                "SELECT s.ZPARTNERNAME, s.ZCONTACTJID, COUNT(*), "
                "COALESCE(SUM(m.ZISFROMME), 0) "
                "FROM ZWAMESSAGE m JOIN ZWACHATSESSION s ON m.ZCHATSESSION = s.Z_PK "
                "WHERE s.ZCONTACTJID LIKE '%@g.us' "
                "AND m.ZMESSAGEDATE BETWEEN ? AND ? "
                "GROUP BY s.Z_PK ORDER BY COUNT(*) DESC",
                (lo, hi),
            ):
                groups.append({
                    "name": gname or "(unnamed)", "msgs": gmsgs, "mine": gmine,
                    "pct_mine": round(100.0 * gmine / gmsgs) if gmsgs else 0,
                })
        status["whatsapp"] = {"ok": True, "rows": rows, "sessions_1to1": len(sessions)}
    except Exception as e:  # noqa: BLE001
        status["whatsapp"] = {"ok": False, "reason": str(e)}
    finally:
        if con:
            con.close()
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


# --------------------------------------------------------------------------- #
# output
# --------------------------------------------------------------------------- #
def build_records(contacts, min_count):
    out = []
    for key, rec in contacts.data.items():
        total = sum(c["count"] for c in rec["channels"].values())
        if total < min_count:
            continue
        sent = sum(c["sent"] for c in rec["channels"].values())
        recv = sum(c["recv"] for c in rec["channels"].values())
        minutes = sum(c["minutes"] for c in rec["channels"].values())
        firsts = [c["first"] for c in rec["channels"].values() if c["first"]]
        lasts = [c["last"] for c in rec["channels"].values() if c["last"]]
        channels = {}
        for name, c in rec["channels"].items():
            channels[name] = {
                "count": c["count"], "sent": c["sent"], "recv": c["recv"],
                "missed": c["missed"], "minutes": round(c["minutes"], 1),
                "first": iso(c["first"]), "last": iso(c["last"]),
            }
        item = {
            "label": contacts.best_label(rec),
            "key": key,
            "handles": sorted(rec["handles"]),
            "total": total,
            "sent": sent,
            "recv": recv,
            "reciprocity": round(sent / total, 2) if total else 0.0,
            "call_minutes": round(minutes, 1),
            "first": iso(min(firsts)) if firsts else None,
            "last": iso(max(lasts)) if lasts else None,
            "channels": channels,
        }
        if contacts.monthly:
            item["monthly"] = {
                ch: dict(sorted(m.items())) for ch, m in rec["monthly"].items()
            }
        out.append(item)
    out.sort(key=lambda r: r["total"], reverse=True)
    return out


def iso(unix):
    return datetime.fromtimestamp(unix).strftime("%Y-%m-%d") if unix else None


def print_summary(records, status, window, top, groups=None, group_totals=None):
    s, u = window
    print(f"\nRelationship interaction metadata  {iso(s)} -> {iso(u)}")
    print("(metadata only -- no message content is read)\n")
    for src in ("whatsapp", "call", "imessage"):
        st = status.get(src, {})
        if st.get("ok"):
            extra = f", {st['sessions_1to1']} 1:1 sessions" if "sessions_1to1" in st else ""
            print(f"  {src:9s} OK   {st.get('rows', 0)} rows in window{extra}")
        else:
            print(f"  {src:9s} SKIP ({st.get('reason', '?')})")
    print(f"\nTop {top} contacts by interaction volume:\n")
    print(f"  {'contact':28s} {'tot':>5} {'out':>5} {'in':>5} {'recip':>6} {'callmin':>8}  channels")
    for r in records[:top]:
        chans = ",".join(sorted(r["channels"]))
        print(
            f"  {r['label'][:28]:28s} {r['total']:5d} {r['sent']:5d} {r['recv']:5d}"
            f" {r['reciprocity']:6.2f} {r['call_minutes']:8.0f}  {chans}"
        )
    if groups:
        gt = group_totals or {}
        print(
            f"\nWhatsApp groups: {gt.get('active_groups', 0)} active, "
            f"{gt.get('msgs', 0)} msgs, {gt.get('pct_mine', 0)}% yours "
            f"(present-but-silent if low). Top groups:\n"
        )
        print(f"  {'group':34s} {'msgs':>6} {'yours':>6} {'%you':>5}")
        for g in groups[:15]:
            print(f"  {g['name'][:34]:34s} {g['msgs']:6d} {g['mine']:6d} {g['pct_mine']:5.0f}")
    print()


def write_csv(path, records):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "key", "channel", "count", "sent", "recv",
                    "missed", "call_minutes", "first", "last"])
        for r in records:
            for ch, c in r["channels"].items():
                w.writerow([r["label"], r["key"], ch, c["count"], c["sent"],
                            c["recv"], c["missed"], c["minutes"], c["first"], c["last"]])


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(description="Metadata-only relationship interaction extractor.")
    p.add_argument("--since", help="start date YYYY-MM-DD (inclusive)")
    p.add_argument("--until", help="end date YYYY-MM-DD (exclusive)")
    p.add_argument("--days", type=int, help="last N days (overrides --since/--until)")
    p.add_argument("--monthly", action="store_true", help="include per-month counts per contact")
    p.add_argument("--min-count", type=int, default=1, help="drop contacts under this total (default 1)")
    p.add_argument("--top", type=int, default=30, help="rows in text summary (default 30)")
    p.add_argument("--json", action="store_true", help="print full JSON to stdout")
    p.add_argument("--csv", help="write per-channel CSV to this path")
    p.add_argument("--snapshot-dir", help="write relationships-<date>.csv + latest.json here")
    args = p.parse_args()

    now = datetime.now()
    if args.days:
        until_dt = now
        since_dt = now - timedelta(days=args.days)
    else:
        since_dt = datetime.strptime(args.since, "%Y-%m-%d") if args.since else datetime(2000, 1, 1)
        until_dt = datetime.strptime(args.until, "%Y-%m-%d") if args.until else now + timedelta(days=1)
    since, until = since_dt.timestamp(), until_dt.timestamp()

    contacts = Contacts(monthly=args.monthly)
    status = {}
    wa_groups = []
    read_whatsapp(contacts, since, until, status, groups=wa_groups)
    read_calls(contacts, since, until, status)
    read_imessage(contacts, since, until, status)

    records = build_records(contacts, args.min_count)
    wa_groups.sort(key=lambda g: g["msgs"], reverse=True)
    group_totals = {
        "msgs": sum(g["msgs"] for g in wa_groups),
        "mine": sum(g["mine"] for g in wa_groups),
        "active_groups": len(wa_groups),
    }
    group_totals["pct_mine"] = (
        round(100.0 * group_totals["mine"] / group_totals["msgs"])
        if group_totals["msgs"] else 0
    )
    payload = {
        "generated": now.strftime("%Y-%m-%d %H:%M"),
        "window": {"since": iso(since), "until": iso(until)},
        "sources": status,
        "contact_count": len(records),
        "contacts": records,
        "whatsapp_group_totals": group_totals,
        "whatsapp_groups": wa_groups[: args.top],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_summary(records, status, (since, until), args.top, wa_groups, group_totals)

    if args.csv:
        write_csv(args.csv, records)
        print(f"wrote {args.csv}", file=sys.stderr)

    if args.snapshot_dir:
        os.makedirs(args.snapshot_dir, exist_ok=True)
        stamp = now.strftime("%Y-%m-%d")
        csv_path = os.path.join(args.snapshot_dir, f"relationships-{stamp}.csv")
        write_csv(csv_path, records)
        with open(os.path.join(args.snapshot_dir, "latest.json"), "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"snapshot -> {csv_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
