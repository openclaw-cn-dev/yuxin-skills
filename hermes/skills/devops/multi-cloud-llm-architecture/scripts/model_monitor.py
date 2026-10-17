#!/usr/bin/env python3
"""
模型套餐监控脚本 — 测试 volcengine-agent-plan 下所有可用模型的响应速度。

用法:
  python3 model_monitor.py

输出:
  每个模型的延迟排名和优化建议。

依赖:
  - ~/.hermes/.env 中包含 ARK_API_KEY (volcengine-agent-plan 的 API key)
  - ~/.hermes/config.yaml 中配置了 volcengine-agent-plan provider

原理:
  1. 从 config.yaml 读取 volcengine-agent-plan 的 models 列表
  2. 对每个模型发送一个简单的 chat completion 请求
  3. 记录响应时间并排名
  4. 输出优化建议
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_api_key() -> Optional[str]:
    """从 .env 读取 ARK API key"""
    env_path = Path.home() / ".hermes" / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("ARK_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return None


def get_models_from_config() -> list:
    """从 config.yaml 读取 volcengine-agent-plan 的模型列表"""
    config_path = Path.home() / ".hermes" / "config.yaml"
    if not config_path.exists():
        return []

    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    providers = config.get("providers", {})
    volc_provider = providers.get("volcengine-agent-plan", {})
    models = volc_provider.get("models", [])
    return [m["id"] for m in models if isinstance(m, dict) and "id" in m]


def test_model(api_key: str, model_id: str, base_url: str, timeout: int = 30) -> dict:
    """测试单个模型的响应速度"""
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "请用一句话回复：你好"}],
        "max_tokens": 20,
        "temperature": 0.1,
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        elapsed = time.time() - start
        body = json.loads(resp.read().decode())
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "model": model_id,
            "latency": round(elapsed, 2),
            "status": "ok",
            "response": content[:50],
        }
    except urllib.error.HTTPError as e:
        return {
            "model": model_id,
            "latency": None,
            "status": f"HTTP {e.code}",
            "response": "",
        }
    except Exception as e:
        return {
            "model": model_id,
            "latency": None,
            "status": f"error: {e}",
            "response": "",
        }


def get_base_url() -> str:
    """从 config.yaml 获取 volcengine-agent-plan 的 base_url"""
    config_path = Path.home() / ".hermes" / "config.yaml"
    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)
    providers = config.get("providers", {})
    volc_provider = providers.get("volcengine-agent-plan", {})
    return volc_provider.get("base_url", "https://ark.cn-beijing.volces.com/api/plan/v3")


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 玉芬大模型套餐监控开始")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'='*50}")

    api_key = get_api_key()
    if not api_key:
        print("❌ 未找到 ARK_API_KEY")
        sys.exit(1)

    models = get_models_from_config()
    if not models:
        print("❌ 未找到模型列表")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 可用模型 ({len(models)} 个)")
    base_url = get_base_url()

    results = []
    for i, model_id in enumerate(models, 1):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏱️ 测试 {i}/{len(models)}: {model_id}...")
        result = test_model(api_key, model_id, base_url)
        results.append(result)
        if result["latency"]:
            print(f"  ✅ {result['latency']}s")
        else:
            print(f"  ❌ {result['status']}")

    # 排序
    ok_results = [r for r in results if r["latency"] is not None]
    ok_results.sort(key=lambda r: r["latency"])

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 速度排名")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'='*50}")

    for i, r in enumerate(ok_results, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        print(f"  {medal} {r['model']}: {r['latency']}s")

    failed = [r for r in results if r["latency"] is None]
    if failed:
        print(f"\n❌ 失败 ({len(failed)} 个):")
        for r in failed:
            print(f"  - {r['model']}: {r['status']}")

    # 优化建议
    if ok_results:
        fastest = ok_results[0]
        slowest = ok_results[-1]
        print(f"\n💡 优化建议:")
        print(f"  🏆 最快: {fastest['model']} ({fastest['latency']}s)")
        print(f"  🐢 最慢: {slowest['model']} ({slowest['latency']}s)")
        print(f"  差距: {slowest['latency'] - fastest['latency']:.1f}s ({(slowest['latency']/fastest['latency']-1)*100:.0f}%)")
        print(f"  建议: 语音交互等低延迟场景使用 {fastest['model']}")


if __name__ == "__main__":
    main()
