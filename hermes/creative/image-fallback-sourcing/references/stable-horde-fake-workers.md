# Stable Horde — Fake Worker Detection

**The 92-byte scam, observed 2026-06-08.**

## What happened

Submitted 8 jobs to `https://stablehorde.net/api/v2/generate/async` with model "Edge Of Realism".
All 8 jobs returned in ~3-4 minutes with `done: true` and `generations: [1]`.

But the resulting files were all **92 bytes of random-looking binary data** (header `86 db 69 b3 ff da db 6d ...`), not PNG files. Pexels images start with `89 50 4E 47 0D 0A 1A 0A` (PNG) or `FF D8 FF E0` (JPEG).

Worker names observed doing this:
- `Zikeri` (default first job — fastest, scammiest)
- `Roaring 3050`
- `Roaring 3050#2`
- `Roaring 3050#3`
- `Roaring_5060ti#2`

The scam: workers earn kudos for "completing" generations without doing the work. They get kudos, you get garbage. The kudos system is exploitable.

## Verification code

```python
import base64, os

def verify_real_image(path, min_size=30000):
    if not os.path.exists(path):
        return False, "no file"
    size = os.path.getsize(path)
    if size < min_size:
        return False, f"too small ({size} B)"
    with open(path, "rb") as f:
        header = f.read(8)
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True, f"PNG {size} B"
    if header.startswith(b"\xff\xd8\xff"):
        return True, f"JPEG {size} B"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return True, f"WEBP {size} B"
    return False, f"unknown header: {header[:8].hex()}"
```

## Tier-2 dispatch with verify

```python
import json, urllib.request, base64, os, time, urllib.error

MODEL = "Edge Of Realism"
def submit_and_poll(prompt, max_wait=300):
    # submit
    data = json.dumps({
        "prompt": prompt,
        "params": {"width": 512, "height": 512, "steps": 25, "sampler_name": "k_euler_a", "n": 1},
        "models": [MODEL], "r2": True
    }).encode()
    req = urllib.request.Request("https://stablehorde.net/api/v2/generate/async", data=data,
                                  headers={"Content-Type": "application/json", "apikey": "0000000000"})
    j = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
    job_id = j["id"]
    # poll
    deadline = time.time() + max_wait
    while time.time() < deadline:
        time.sleep(20)
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"https://stablehorde.net/api/v2/generate/status/{job_id}"), timeout=10).read().decode())
        if r.get("done"):
            gens = r.get("generations", [])
            if gens and gens[0].get("img"):
                path = f"/tmp/horde_{job_id[:8]}.webp"
                with open(path, "wb") as f:
                    f.write(base64.b64decode(gens[0]["img"]))
                ok, info = verify_real_image(path)
                if ok:
                    return path, gens[0].get("worker_name", ""), gens[0].get("seed")
                else:
                    os.remove(path)
                    print(f"  ✗ {job_id[:8]} fake image from {gens[0].get('worker_name','?')}: {info}")
    return None, None, None
```

## Worker blacklist (as of 2026-06)

```
Zikeri
Roaring 3050
Roaring 3050#2
Roaring 3050#3
Roaring_5060ti#2
```

Horde has a blacklist feature but it's per-API-key and not exposed in the public API we use. Just verify each result and retry on a different worker.

## Better models to try (lower scam rate)

Per the model list `GET /api/v2/status/models?type=image`:
- `DreamShaper XL` — popular, well-monitored workers
- `majicMIX realistic` — 7 workers queue=0
- `Realistic Vision` — queue 8M, may be slow
- **Avoid**: any model where `queued > 1000000` (signals the busy/scam workers grab these)

## When to abandon Tier 2

After 3 consecutive fake-image returns, skip to Tier 3. Don't burn 10 minutes on Horde.
