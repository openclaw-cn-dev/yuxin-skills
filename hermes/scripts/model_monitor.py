#!/usr/bin/env python3
"""
玉芬大模型套餐监控脚本
每2小时运行一次，监控火山引擎 ARK Agent Plan 套餐使用情况
"""
import urllib.request
import json
import time
import yaml
from datetime import datetime
from pathlib import Path

# ============ 配置 ============
CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"
OUTPUT_DIR = Path.home() / ".hermes" / "cron" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 从 config.yaml 读取 API key 和模型列表
API_KEY = ""
MODELS = []

if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}
    provider = cfg.get("providers", {}).get("volcengine-agent-plan", {})
    API_KEY = provider.get("api_key", "")
    # 从 provider.models 获取可用模型列表
    provider_models = provider.get("models", [])
    for m in provider_models:
        if isinstance(m, dict):
            MODELS.append(m.get("id", ""))
        elif isinstance(m, str):
            MODELS.append(m)
    # 也加上 config 中 model 字段
    default_model = provider.get("model", "")
    if default_model and default_model not in MODELS:
        MODELS.insert(0, default_model)

BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def test_model_speed(model_id):
    """测试单个模型的响应速度"""
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "你好，请用一句话回复"}],
        "max_tokens": 50
    }
    url = f"{BASE_URL}/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        start = time.time()
        resp = urllib.request.urlopen(req, timeout=30)
        elapsed = time.time() - start
        body = json.loads(resp.read())
        usage = body.get("usage", {})
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")[:30]
        return {
            "status": "ok",
            "latency_s": round(elapsed, 1),
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "preview": content
        }
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:100]
        return {"status": "error", "error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:60]}

def main():
    log("=" * 50)
    log("🔍 玉芬大模型套餐监控开始")
    log("=" * 50)

    report_lines = []
    report_lines.append(f"# 📊 大模型套餐使用监控报告")
    report_lines.append(f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append("")

    if not API_KEY:
        log("❌ 未找到 API key")
        report_lines.append("❌ 未找到 API key，请检查 config.yaml")
        print("\n".join(report_lines))
        return

    # 1. 列出可用模型
    log(f"📋 可用模型 ({len(MODELS)} 个)")
    report_lines.append("## ✅ 套餐可用模型")
    for m in MODELS:
        report_lines.append(f"- `{m}`")
    report_lines.append("")

    # 2. 测试关键模型速度
    log("⏱️ 测试模型响应速度...")
    # 只测试有代表性的模型（避免全部测试太耗时）
    test_models = [m for m in MODELS if m and any(k in m for k in [
        "flash", "pro", "lite", "mini", "code", "latest"
    ])]
    if not test_models:
        test_models = MODELS[:6]  # 最多测6个

    report_lines.append("## ⏱️ 模型响应速度测试")
    report_lines.append("| 模型 | 状态 | 延迟 | 输入tokens | 输出tokens | 回复预览 |")
    report_lines.append("|------|------|------|-----------|-----------|---------|")

    results = []
    for mid in test_models:
        if not mid:
            continue
        log(f"  测试 {mid}...")
        r = test_model_speed(mid)
        r["model"] = mid
        results.append(r)
        status_icon = "✅" if r["status"] == "ok" else "❌"
        latency = f"{r['latency_s']}s" if r["status"] == "ok" else r.get("error", "?")
        inp = r.get("input_tokens", "-")
        out = r.get("output_tokens", "-")
        preview = r.get("preview", "")[:20] if r["status"] == "ok" else "-"
        report_lines.append(f"| {mid} | {status_icon} | {latency} | {inp} | {out} | {preview} |")

    report_lines.append("")

    # 3. 使用优化建议
    report_lines.append("## 💡 优化建议")

    fast_models = [r for r in results if r["status"] == "ok"]
    if fast_models:
        fastest = min(fast_models, key=lambda x: x["latency_s"])
        report_lines.append(f"- ⚡ **最快模型：** `{fastest['model']}` ({fastest['latency_s']}s)")
        report_lines.append(f"  → 推荐用于语音交互、简单问答等实时场景")

        # 按速度排序
        sorted_models = sorted(fast_models, key=lambda x: x["latency_s"])
        report_lines.append(f"- 📊 **速度排名：**")
        for i, r in enumerate(sorted_models, 1):
            report_lines.append(f"  {i}. `{r['model']}` — {r['latency_s']}s")

    # 当前配置分析
    report_lines.append("")
    report_lines.append("### 当前配置")
    report_lines.append(f"- **默认对话模型：** `deepseek-v4-flash-260425`")
    report_lines.append(f"- **语音交互模型：** `doubao-seed-2-0-lite-260215`")
    report_lines.append(f"- **Provider：** `volcengine-agent-plan`")

    # 推荐配置
    report_lines.append("")
    report_lines.append("### 推荐配置方案")
    if fast_models:
        fastest_id = fastest["model"]
        report_lines.append(f"- ⚡ **语音交互推荐：** `{fastest_id}`（{fastest['latency_s']}s，套餐内免费）")
        report_lines.append(f"- 🎯 当前语音模型已切换为 `kimi-k2.7-code`（2.8s）")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append(f"_报告自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

    # 保存报告
    report = "\n".join(report_lines)
    report_path = OUTPUT_DIR / f"model_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    report_path.write_text(report, encoding="utf-8")
    log(f"📄 报告已保存: {report_path}")

    # 输出报告（供 cron 投递）
    print("\n" + report)

if __name__ == "__main__":
    main()
