#!/usr/bin/env python3
"""
Fetch every feed listed in feeds.json and write a compact JSON digest to
data/feed_items.json, consumed by veille.html.

Runs headless in a GitHub Action — a broken/renamed feed is logged and
skipped, it never crashes the whole run.
"""
import datetime
import hashlib
import json
import os
import sys

import feedparser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS_FILE = os.path.join(ROOT, "feeds.json")
OUTPUT_FILE = os.path.join(ROOT, "data", "feed_items.json")

MAX_ITEMS_PER_FEED = 15
MAX_TOTAL_ITEMS = 300
SUMMARY_MAX_CHARS = 400


def load_feeds():
    with open(FEEDS_FILE, encoding="utf-8") as f:
        return json.load(f)


def strip_html(raw: str) -> str:
    """Very small HTML stripper so summaries stay plain text in the UI."""
    out, in_tag = [], False
    for ch in raw:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        elif not in_tag:
            out.append(ch)
    return " ".join("".join(out).split())


def parse_entry(entry, source_name, category):
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published:
        dt = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
        iso, ts = dt.isoformat(), dt.timestamp()
    else:
        iso, ts = None, 0

    link = entry.get("link", "")
    title = strip_html(entry.get("title", "(sans titre)")).strip()
    summary = strip_html(entry.get("summary", "") or "")[:SUMMARY_MAX_CHARS]
    uid = hashlib.sha1((link + title).encode("utf-8")).hexdigest()[:12]

    return {
        "id": uid,
        "title": title,
        "link": link,
        "source": source_name,
        "category": category,
        "published": iso,
        "ts": ts,
        "summary": summary,
    }


def main():
    feeds = load_feeds()
    all_items, errors = [], []

    for feed in feeds:
        name, url = feed["name"], feed["url"]
        category = feed.get("category", "misc")
        try:
            parsed = feedparser.parse(url)
            if parsed.bozo and not parsed.entries:
                raise RuntimeError(str(parsed.bozo_exception))
            for e in parsed.entries[:MAX_ITEMS_PER_FEED]:
                all_items.append(parse_entry(e, name, category))
        except Exception as exc:  # noqa: BLE001 — one bad feed must not kill the run
            errors.append({"source": name, "url": url, "error": str(exc)})
            print(f"[WARN] {name}: {exc}", file=sys.stderr)

    all_items.sort(key=lambda x: x["ts"], reverse=True)
    all_items = all_items[:MAX_TOTAL_ITEMS]

    output = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "count": len(all_items),
        "errors": errors,
        "items": all_items,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_items)} items ({len(errors)} feed errors) -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
