#!/usr/bin/env python3
"""Fetch archived game pages and extract original SWF references for diagnostics."""
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GAMES = [
    ("R.U.E.S.P. Quiz", "ruesp", "20130502115524", "http://www.emilystrange.com/beware/games/ruesp/index.cfm", "ruesp.swf"),
    ("Strange Invaders", "strange-invaders", "20130502103054", "http://www.emilystrange.com/beware/games/StrangeInvaders/index.cfm", "StrangeInvaders.swf"),
    ("Deathtris", "deathtris", "20130502104114", "http://www.emilystrange.com/beware/games/Deathtris/index.cfm", "Deathtris.swf"),
    ("Nine Lives Forever", "nine-lives-forever", "20130502120404", "http://www.emilystrange.com/beware/games/ninelives/index.cfm", "NineLivesForever.swf"),
    ("Homework Hexx", "homework-hexx", "20130515043628", "http://www.emilystrange.com/beware/games/hexx/index.cfm", "HomeworkHexx.swf"),
    ("Spiders and the Fly", "spiders-and-the-fly", "20130523023053", "http://www.emilystrange.com/beware/games/Spidersandthefly/index.cfm", "SpidersAndTheFly.swf"),
    ("Drop Dead Dizzy", "drop-dead-dizzy", "20130502104752", "http://www.emilystrange.com/beware/games/DropDeadDizzy/index.cfm", "DropDeadDizzy.swf"),
]
WAYBACK = "https://web.archive.org/web/"
OUT = Path("archive-html")
OUT.mkdir(exist_ok=True)

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("src", "data", "href", "value", "movie"):
            val = attrs.get(key)
            if val:
                self.values.append((tag, key, val))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

def fetch(url):
    last = None
    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 EmilyArcadeAssetAudit/1.1"})
            with urlopen(req, timeout=45) as res:
                return res.geturl(), res.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise last

def decode_ref(raw):
    return raw.replace("&amp;", "&").replace("\\/", "/").replace("\\u0026", "&").strip()

report = []
md = ["# Emily Arcade — archived SWF reference audit", ""]
for title, slug, stamp, original, expected in GAMES:
    page_url = WAYBACK + stamp + "id_/" + original
    record = {"game": title, "page": page_url, "expected_filename": expected, "fetch_error": None, "html_bytes": 0, "swf_references": [], "embed_attributes": [], "expected_name_context": []}
    try:
        final_url, body = fetch(page_url)
        text = body.decode("utf-8", "replace")
        record["html_bytes"] = len(body)
        (OUT / (slug + ".html")).write_text(text, encoding="utf-8")
        parser = AssetParser()
        parser.feed(text)
        candidates = set()
        for _, _, value in parser.values:
            value = decode_ref(value)
            if ".swf" in value.lower():
                candidates.add(value)
        for match in re.findall(r"""(?i)(?:https?:)?[^\s\"'<>]+?\.swf(?:\?[^\s\"'<>]*)?""", text):
            candidates.add(decode_ref(match).rstrip(");,"))
        record["swf_references"] = sorted(candidates)
        record["embed_attributes"] = [{"tag": t, "attribute": k, "value": v} for t, k, v in parser.values if any(ext in v.lower() for ext in (".swf", ".js", ".xml"))][:100]
        low = text.lower()
        pos = low.find(expected.lower())
        if pos >= 0:
            record["expected_name_context"] = [text[max(0, pos-500):min(len(text), pos+800)]]
        md += [f"## {title}", f"- Archived page: {page_url}", f"- HTML fetched: {len(body)} bytes"]
        if candidates:
            md += ["- SWF references found:"] + [f"  - {u}" for u in sorted(candidates)]
        else:
            md += ["- No .swf reference found in the archived page HTML."]
        if record["expected_name_context"]:
            md += ["- Expected filename context:"] + [record["expected_name_context"][0]]
    except Exception as exc:
        record["fetch_error"] = f"{type(exc).__name__}: {exc}"
        md += [f"## {title}", f"- Archived page: {page_url}", f"- Fetch failed: {record['fetch_error']}"]
    md += [""]
    report.append(record)
    print(f"{title}: {len(record['swf_references'])} SWF refs; error={record['fetch_error']}")
Path("wayback-game-inspection.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
Path("wayback-game-inspection.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
