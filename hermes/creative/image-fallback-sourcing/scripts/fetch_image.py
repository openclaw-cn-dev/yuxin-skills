#!/usr/bin/env python3
"""
Image fallback fetcher — 6-tier chain.
Usage:
  python fetch_image.py "boiled red shrimp" 03.jpg
  python fetch_image.py "rustic seafood plate" 04_sauce.jpg
"""
import sys, os, json, time, base64, subprocess, urllib.request, urllib.error

if len(sys.argv) < 3:
    print("usage: fetch_image.py <prompt> <output_path>")
    sys.exit(1)

PROMPT = sys.argv[1]
OUT = sys.argv[2]
OUT_DIR = os.path.dirname(OUT) or "."
os.makedirs(OUT_DIR, exist_ok=True)

def verify_real_image(path, min_size=30000):
    if not os.path.exists(path): return False, "no file"
    size = os.path.getsize(path)
    if size < min_size: return False, f"too small ({size} B)"
    with open(path, "rb") as f: h = f.read(8)
    if h.startswith(b"\x89PNG\r\n\x1a\n"): return True, f"PNG {size//1024}KB"
    if h.startswith(b"\xff\xd8\xff"): return True, f"JPEG {size//1024}KB"
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP": return True, f"WEBP {size//1024}KB"
    return False, f"bad header: {h[:8].hex()}"

# === TIER 1: Polinations ===
def try_pollinations():
    import urllib.parse
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(PROMPT)}?width=1024&height=1024&seed=42&nologo=true"
    tmp = OUT + ".tier1.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if len(data) < 1000: return None, f"too small {len(data)}"
        with open(tmp, "wb") as f: f.write(data)
        ok, info = verify_real_image(tmp)
        if ok: return tmp, f"pollinations {info}"
        os.remove(tmp); return None, f"pollinations fake: {info}"
    except Exception as e: return None, f"pollinations: {e}"

# === TIER 2: Stable Horde ===
def try_horde():
    data = json.dumps({
        "prompt": PROMPT,
        "params": {"width":512,"height":512,"steps":25,"sampler_name":"k_euler_a","n":1},
        "models": ["Edge Of Realism", "majicMIX realistic", "Realistic Vision"],
        "r2": True
    }).encode()
    try:
        req = urllib.request.Request("https://stablehorde.net/api/v2/generate/async", data=data,
                                      headers={"Content-Type":"application/json","apikey":"0000000000"})
        j = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        job_id = j["id"]
    except Exception as e: return None, f"horde submit: {e}"

    deadline = time.time() + 240
    while time.time() < deadline:
        time.sleep(20)
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                f"https://stablehorde.net/api/v2/generate/status/{job_id}"), timeout=10).read().decode())
        except Exception as e: continue
        if r.get("done"):
            gens = r.get("generations", [])
            if gens and gens[0].get("img"):
                tmp = OUT + ".tier2.webp"
                with open(tmp, "wb") as f: f.write(base64.b64decode(gens[0]["img"]))
                ok, info = verify_real_image(tmp)
                if ok: return tmp, f"horde {info} by {gens[0].get('worker_name','?')}"
                os.remove(tmp)
                return None, f"horde fake from {gens[0].get('worker_name','?')}: {info}"
    return None, "horde timeout"

# === TIER 3: HF Inference (curl, not Python) ===
def try_hf():
    tmp = OUT + ".tier3.jpg"
    cmd = ["curl","-L","-s","-A","Mozilla/5.0","--max-time","180",
           "-X","POST","-H","Content-Type: application/json",
           "-d", json.dumps({"inputs":PROMPT,"options":{"wait_for_model":True,"use_cache":False}}),
           "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-photoreal-2.0",
           "-o", tmp, "-w","%{http_code}"]
    try:
        result = subprocess.run(cmd, timeout=200, capture_output=True, text=True)
        if os.path.exists(tmp):
            ok, info = verify_real_image(tmp)
            if ok: return tmp, f"hf {info}"
            os.remove(tmp)
        return None, f"hf HTTP {result.stdout}"
    except Exception as e: return None, f"hf: {e}"

# === TIER 4: Pexels CC0 (use bank or pass query) ===
def try_pexels_search(queries):
    for q in queries:
        # Hit Pexels search HTML via curl (Python urllib gets 403)
        cmd = ["curl","-L","-s","-A","Mozilla/5.0","--max-time","12",
               f"https://www.pexels.com/search/{q.replace(' ','-')}/"]
        try:
            html = subprocess.run(cmd, timeout=15, capture_output=True, text=True).stdout
        except: continue
        import re
        ids = re.findall(r'/photos/(\d+)/[a-z-]+', html)
        ids = list(dict.fromkeys(ids))[:5]  # dedupe, top 5
        for pid in ids:
            tmp = OUT + f".tier4_{pid}.jpg"
            cmd2 = ["curl","-L","-s","-A","Mozilla/5.0","--max-time","10",
                    "-o", tmp,
                    f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?w=1200"]
            try:
                subprocess.run(cmd2, timeout=15, check=True)
                if os.path.exists(tmp) and verify_real_image(tmp, 50000)[0]:
                    return tmp, f"pexels id={pid}"
                if os.path.exists(tmp): os.remove(tmp)
            except: continue
    return None, "pexels: no candidate passed verify"

tiers = [
    ("Tier 1 Polinations", try_pollinations),
    ("Tier 2 Stable Horde", try_horde),
    ("Tier 3 HF Inference", try_hf),
    ("Tier 4 Pexels", lambda: try_pexels_search([PROMPT])),
]

for name, fn in tiers:
    print(f"\n=== {name} ===")
    tmp, info = fn()
    if tmp and os.path.exists(tmp):
        os.replace(tmp, OUT)
        print(f"✅ {name}: {info} → {OUT}")
        sys.exit(0)
    else:
        print(f"✗ {name}: {info}")

print(f"\n❌ All tiers failed. Please drop a real photo at {OUT}.")
sys.exit(1)
