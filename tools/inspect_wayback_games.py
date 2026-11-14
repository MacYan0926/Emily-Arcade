#!/usr/bin/env python3
"""Inspect archived Emily the Strange game pages for original Flash assets."""
import json
import re
import sys
import time
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GAMES = [
    ("R.U.E.S.P. Quiz", "20130502115524", "http://www.emilystrange.com/beware/games/ruesp/index.cfm"),
    ("Strange Invaders", "20130502103054", "http://www.emilystrange.com/beware/games/StrangeInvaders/index.cfm"),
    ("Deathtris", "20130502104114", "http://www.emilystrange.com/beware/games/Deathtris/index.cfm"),
    ("Nine Lives Forever", "20130502120404", "http://www.emilystrange.com/beware/games/ninelives/index.cfm"),
    ("Homework Hexx", "20130515043628", "http://www.emilystrange.com/beware/games/hexx/index.cfm"),
    ("Spiders and the Fly", "20130523023053", "http://www.emilystrange.com/beware/games/Spidersandthefly/index.cfm"),
    ("Drop Dead Dizzy", "20130502104752", "http://www.emilystrange.com/beware/games/DropDeadDizzy/index.cfm"),
]
BASE = "https://web.archive.org/web/"

def get(url, timeout=35):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 EmilyArcadeArchiveDiagnostics/1.0"})
    with urlopen(req, timeout=timeout) as response:
        return response.geturl(), response.read()

def clean_url(raw, page_url):
    raw = raw.replace("&amp;", "&").replace("\\/", "/").strip().strip("\\\"'()")
    if not raw or raw.startswith(("javascript:", "data:", "#")):
        return None
    return urljoin(page_url, raw)

def extract_assets(html, page_url):
    text = html.decode("utf-8", "replace")
    found = set()
    patterns = [
        r"""(?:src|data|movie|value)\\s*=\\s*["']([^"']+\\.swf(?:\\?[^"']*)?)["']""",
        r"""["']([^"']+\\.swf(?:\\?[^"']*)?)["']""",
        r"""(?:src|href)\\s*=\\s*["']([^"']+\\.(?:js|xml|txt|dat)(?:\\?[^"']*)?)["']""",
    ]
    for pattern in patterns:
        for raw in re.findall(pattern, text, flags=re.I):
            resolved = clean_url(raw, page_url)
            if resolved:
                found.add(resolved)
    # Capture common Flash embedding attributes and nearby source fragments.
    snippets = []
    for match in re.finditer(r"(?is)<(?:object|embed)\\b.{0,2500}?>", text):
        snippet = re.sub(r"\\s+", " ", match.group(0))[:700]
        snippets.append(snippet)
    return sorted(found), snippets, text

def cdx_prefix(prefix):
    query = (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(prefix, safe="") +
        "&matchType=prefix&output=json&filter=statuscode:200" +
        "&fl=timestamp,original,mimetype,statuscode,length&limit=250"
    )
    try:
        _, raw = get(query, timeout=50)
        rows = json.loads(raw.decode("utf-8", "replace"))
        if not rows:
            return [], "empty CDX response"
        header = rows[0]
        return [dict(zip(header, row)) for row in rows[1:] if len(row) == len(header)], None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"

report = []
summary = ["# Emily Arcade — Wayback game asset inspection", "", "This diagnostic checks archived HTML and the Wayback CDX index. It does not redistribute or commit game files.", ""]
for name, timestamp, original in GAMES:
    page = BASE + timestamp + "id_/" + original
    row = {"game": name, "page": page, "page_fetch": None, "assets": [], "embed_snippets": [], "cdx": [], "errors": []}
    try:
        final_url, body = get(page)
        assets, snippets, html = extract_assets(body, final_url)
        row["page_fetch"] = {"final_url": final_url, "bytes": len(body), "content_type": "html"}
        row["assets"] = assets
        row["embed_snippets"] = snippets[:12]
        # Find resource paths under the same game folder, then the historical common games folder.
        folder = original.rsplit("/", 1)[0] + "/"
        rows, error = cdx_prefix(folder)
        row["cdx"] = rows[:80]
        if error:
            row["errors"].append("CDX game folder: " + error)
        # Some games were stored in a shared Flash asset directory; query common paths too.
        if not any(".swf" in x.lower() for x in assets) and not any(".swf" in str(x.get("original","")).lower() for x in rows):
            for prefix in [
                "http://www.emilystrange.com/AAEmily/fungames/",
                "http://www.emilystrange.com/beware/games/",
            ]:
                extra, extra_error = cdx_prefix(prefix)
                swfs = [x for x in extra if ".swf" in str(x.get("original","")).lower()]
                if swfs:
                    row["cdx"].extend(swfs[:80])
                if extra_error:
                    row["errors"].append("CDX shared folder " + prefix + ": " + extra_error)
    except Exception as exc:
        row["errors"].append("Page fetch: " + f"{type(exc).__name__}: {exc}")
    report.append(row)
    summary += [f"## {name}", f"- Page: {page}"]
    if row["page_fetch"]:
        summary += [f"- Fetched archived HTML: {row['page_fetch']['bytes']} bytes"]
    if row["assets"]:
        summary += ["- Referenced resources:"] + [f"  - {u}" for u in row["assets"]]
    swfs = [x for x in row["cdx"] if ".swf" in str(x.get("original","")).lower()]
    if swfs:
        summary += ["- CDX SWF captures:"] + [f"  - {x.get('timestamp')} {x.get('original')} ({x.get('length')} bytes)" for x in swfs]
    if row["embed_snippets"]:
        summary += ["- Flash embed snippets:"] + [f"  - `{x}`" for x in row["embed_snippets"][:5]]
    if row["errors"]:
        summary += ["- Errors:"] + [f"  - {e}" for e in row["errors"]]
    if not row["assets"] and not swfs:
        summary += ["- No direct SWF URL found in this pass."]
    summary += [""]
with open("wayback-game-inspection.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
with open("wayback-game-inspection.md", "w", encoding="utf-8") as f:
    f.write("\\n".join(summary) + "\\n")
print("\\n".join(summary))
