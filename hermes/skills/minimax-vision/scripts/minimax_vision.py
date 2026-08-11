#!/usr/bin/env python3
"""MiniMax Vision API direct caller — bypasses Hermes broken vision_analyze auth.
Usage: python3 minimax_vision.py <image_path> [question]
"""
import base64, json, os, sys, urllib.request

img_path = sys.argv[1]
question = sys.argv[2] if len(sys.argv) > 2 else "详细描述图片中的所有文字内容"

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

with open(os.path.expanduser("~/.hermes/.env")) as f:
    api_key = None
    for line in f:
        if line.startswith('MINIMAX_API_KEY=***            api_key = line.strip().split('=', 1)[1]
            break

if not api_key:
    print("ERROR: MINIMAX_API_KEY not found in ~/.hermes/.env")
    sys.exit(1)

url = "https://api.minimaxi.com/v1/chat/completions"
payload = {
    "model": "MiniMax-M3",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": question}
        ]
    }],
    "max_tokens": 2000
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read())
content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
print(content if content else json.dumps(result, indent=2, ensure_ascii=False))
