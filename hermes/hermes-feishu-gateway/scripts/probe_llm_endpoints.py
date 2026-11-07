"""用 key 并行 probe 多个 LLM 端点，找出哪个通。

【使用场景】配完 model 4 件套但不知道 base_url 用哪个、key 是哪个平台时跑这个。
【输出】每个端点的 HTTP code + 前 80 字符响应体；✅ 200 = 端点+key 匹配。
【关键】Key 从 ~/minimax_key_value.txt 读，不进 LLM 通道（绕开 secret redaction）。

用法：
  1. 先把 key 写到 ~/minimax_key_value.txt（od -c 验过原始字节长度）
  2. python scripts/probe_llm_endpoints.py
  3. 看输出里哪个端点 ✅ 200 → 改 hermes config set model.base_url <那行 url>

【新增候选端点】直接编辑下面的 ENDPOINTS 列表。
【为什么用 GET /v1/models 而不是 POST /v1/messages】
  - GET /models 零 token 消耗、毫秒级响应、纯 healthcheck 性质
  - POST /messages 真发聊天请求，token 计入配额，还会被 model 路由到
    不同子模型产生误导（你以为 401 其实是 model 不认）
  - 2026-06-07 实测：MiniMax 官方端点 GET /v1/models 返回 200 + 模型列表
"""
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

# 默认 key 路径，可被环境变量 KEY_FILE 覆盖
KEY_PATH = Path(os.environ.get("KEY_FILE", Path.home() / "minimax_key_value.txt"))

# 候选端点 (base_url, mode) —— mode = "openai" (Bearer) 或 "anthropic" (X-Api-Key)
# 脚本会 GET {base_url}/v1/models 做 healthcheck —— 零 token、毫秒级
ENDPOINTS = [
    ("https://api.minimaxi.com",          "openai"),       # MiniMax 官方 v1
    ("https://api.minimaxi.com/anthropic","anthropic"),    # MiniMax 官方 Anthropic 兼容
    ("https://api.minimax.com",          "openai"),       # 旧域名
    ("https://api.minimax.com/anthropic","anthropic"),    # 旧域名
    ("https://api.packycode.com",        "openai"),       # PackyCode
    ("https://api.packycode.com/anthropic","anthropic"),
    ("https://api.aicodemirror.com",     "openai"),       # AICodeMirror
    ("https://api.aicodemirror.com/anthropic","anthropic"),
    # 自定义公司代理（如果有）
    # ("https://minimax-proxy.yourcompany.com", "openai"),
]


def main() -> None:
    if not KEY_PATH.exists():
        print(f"❌ 找不到 key 文件: {KEY_PATH}")
        print("   先把 key 写到那个路径（od -c 验原始字节数）")
        return

    key = KEY_PATH.read_text(encoding="utf-8").strip()
    # 不再硬编码 120 —— 2026-06-07 实测 MiniMax 官方新 key 是 126 字符；
    # PackyCode 是 120；Claude 直连是 108。只警告、不拒绝。
    if len(key) < 50:
        print(f"❌ key 长度 {len(key)} 太短，疑似截断")
        return
    if len(key) not in (108, 120, 126, 128):
        print(f"⚠️  key 长度 {len(key)}（常见值 108/120/126/128）—— 不一定错，但请用 od -c 验证")

    print(f"Key 长度: {len(key)}  前缀: {key[:12]}...  末尾: ...{key[-6:]}")
    print("=" * 70)

    for base, mode in ENDPOINTS:
        url = base.rstrip("/") + "/v1/models"
        try:
            if mode == "openai":
                headers = {"Authorization": f"Bearer {key}"}
            else:
                headers = {
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                }
            req = urllib.request.Request(url, headers=headers, method="GET")
            resp = urllib.request.urlopen(req, timeout=10)
            body = resp.read().decode("utf-8", errors="ignore")[:120]
            # 尝试解析列出模型名
            models = ""
            try:
                j = json.loads(body)
                if "data" in j and j["data"]:
                    models = ",".join(m.get("id", "?") for m in j["data"][:3])
            except Exception:
                pass
            print(f"✅ {base:50s}  HTTP {resp.status}  models={models or body[:60]}")
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="ignore")[:100]
            icon = "❌" if e.code in (401, 403) else "⚠️ "
            print(f"{icon} {base:50s}  HTTP {e.code}  {err}")
        except urllib.error.URLError as e:
            print(f"⚠️  {base:50s}  网络异常  {str(e.reason)[:60]}")
        except Exception as e:
            print(f"⚠️  {base:50s}  异常  {str(e)[:60]}")


if __name__ == "__main__":
    main()
