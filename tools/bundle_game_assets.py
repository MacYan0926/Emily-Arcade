#!/usr/bin/env python3
"""Recover the exact SWF files previously supplied by the project owner from Wayback captures."""
import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

GAMES = [
    {
        "id": "drop-dead-dizzy",
        "filename": "DropDeadDizzy.swf",
        "original": "http://www.emilystrange.com/AAAemily/fungames/DropDeadDizzy/DropDeadDizzy.swf",
        "preferred": "20130502104752",
        "sha256": "f62a27a14c33c9993d75ba0de50bbbbecf6da6b59576a6b2f57f1a6615adb078",
    },
    {
        "id": "strange-invaders",
        "filename": "StrangeInvaders.swf",
        "original": "http://www.emilystrange.com/AAAemily/fungames/StrangeInvaders/StrangeInvaders.swf",
        "preferred": "20130502103054",
        "sha256": "9b430516ad6a675c344692755f3ef27d9f3f3e97d5d4e84bc3e53934cb39e06d",
    },
    {
        "id": "deathtris",
        "filename": "Deathtris.swf",
        "original": "http://www.emilystrange.com/beware/games/Deathtris/Deathtris.swf",
        "preferred": "20130502104114",
        "sha256": "18ae89f0c3ddacab8cb080156a77e6135af1c9fa071a2cc0275155186b4c337d",
    },
    {
        "id": "nine-lives-forever",
        "filename": "ninelives.swf",
        "original": "http://www.emilykittycatclothing.com/aaaemily/fungames/ninelives/ninelives.swf",
        "preferred": "20130502120404",
        "sha256": "e0172c95762a29bb53f78d1ff6dd22a819104835b4e7302d322c1ebc1abf1fad",
    },
    {
        "id": "homework-hexx",
        "filename": "hexxagonFinal.swf",
        "original": "http://www.emilystrange.com/AAAemily/fungames/hexx/hexxagonFinal.swf",
        "preferred": "20130515043628",
        "sha256": "c964d59cb8c8ec9a7bdbb22ecd337566f3d6f241c0a4dab971a3a70e69e3f907",
    },
    {
        "id": "spiders-and-the-fly",
        "filename": "Spiders.swf",
        "original": "http://www.emilystrange.com/beware/games/Spidersandthefly/Spiders.swf",
        "preferred": "20130523023053",
        "sha256": "04e9d6565b0e0291bb0e02856f23a2753813af206b369d6869e82bc4a0587e03",
    },
]

def get(url, timeout=60):
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; EmilyArcadeAssetRecovery/1.0)",
        "Accept": "*/*",
        "Connection": "close",
    })
    last_error = None
    for attempt in range(7):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.geturl(), response.read()
        except HTTPError as exc:
            if exc.code not in (408, 425, 429, 500, 502, 503, 504):
                raise
            last_error = exc
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt < 6:
            delay = min(2 ** attempt, 20)
            print(f"Temporary archive connection error; retry {attempt + 1}/6 in {delay}s: {last_error}", flush=True)
            time.sleep(delay)
    raise last_error

def cdx_timestamps(original):
    endpoint = (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(original, safe="")
        + "&output=json&filter=statuscode:200&fl=timestamp,digest,length&collapse=digest&limit=100"
    )
    try:
        _, raw = get(endpoint, timeout=60)
        rows = json.loads(raw.decode("utf-8", "replace"))
        return [row[0] for row in rows[1:] if len(row) >= 3], None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"

def recover(game):
    target_hash = game["sha256"]
    timestamps = [game["preferred"]]
    more, cdx_error = cdx_timestamps(game["original"])
    timestamps.extend(t for t in more if t not in timestamps)
    tried = []
    for stamp in timestamps[:100]:
        url = f"https://web.archive.org/web/{stamp}id_/{game['original']}"
        try:
            final_url, data = get(url)
            digest = hashlib.sha256(data).hexdigest()
            signature = data[:3]
            tried.append({"timestamp": stamp, "bytes": len(data), "sha256": digest, "signature": signature.decode("ascii", "replace"), "final_url": final_url})
            if digest == target_hash and signature in (b"FWS", b"CWS", b"ZWS"):
                destination = Path("games") / game["filename"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                return {"game": game["id"], "filename": game["filename"], "bytes": len(data), "sha256": digest, "source_timestamp": stamp, "status": "matched"}
        except Exception as exc:
            tried.append({"timestamp": stamp, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.15)
    raise RuntimeError(json.dumps({
        "game": game["id"],
        "expected_sha256": target_hash,
        "cdx_error": cdx_error,
        "attempts": tried[:25],
    }, ensure_ascii=False))

def main():
    results = []
    failures = []
    for game in GAMES:
        try:
            result = recover(game)
            results.append(result)
            print(f"OK {result['filename']} ({result['bytes']} bytes; SHA-256 matched uploaded file)", flush=True)
        except Exception as exc:
            failures.append({"game": game["id"], "error": str(exc)})
            print(f"FAILED {game['id']}: {exc}", flush=True)
    if failures:
        raise RuntimeError(json.dumps({"recovered": results, "failures": failures}, ensure_ascii=False))
    Path("games/asset-manifest.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
