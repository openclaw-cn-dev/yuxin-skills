#!/usr/bin/env python3
"""Analyze an image using MiniMax-M3 vision API.

Usage:
    python3 analyze_image.py <image_path> [question]

Reads MINIMAX_API_KEY from ~/.hermes/.env.
Sends the image as base64 to MiniMax's /v1/chat/completions endpoint.
"""

import base64
import json
import os
import sys
import urllib.request

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_image.py <image_path> [question]")
        sys.exit(1)

    img_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "详细描述这张图片中的所有文字内容"

    if not os.path.exists(img_path):
        print(f"ERROR: file not found: {img_path}")
        sys.exit(1)

    # Read and encode image
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # Read API key from .env
    env_path = os.path.expanduser("~/.hermes/.env")
    api_key = None
    with open(env_path) as f:
        for line in f:
            if line.startswith("MINIMAX_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break

    if not api_key:
        print("ERROR: MINIMAX_API_KEY not found in ~/.hermes/.env")
        sys.exit(1)

    # Call MiniMax vision API
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
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content:
            # Strip thinking tags if present
            if "<think>" in content and "</think>" in content:
                content = content.split("</think>")[-1].strip()
            print(content)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
