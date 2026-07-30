#!/usr/bin/env python3
"""
智能 LLM Fallback 代理
- 拦截 HTTP 429/402 → 自动切到 DeepSeek 备用
- 同时服务 Hermes / Claude Code / Codex CLI
- 首次 fallback 时推飞书通知华哥

用法:
  python3 llm_fallback_proxy.py [--port PORT] [--primary PRIMARY_NAME] [--fallback FALLBACK_NAME]

Backend 配置从 ~/.hermes/config.yaml + ~/.hermes/.env 读取。
默认 primary=volcengine-agent-plan, fallback=deepseek-cn
"""

import http.server
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
STATE_FILE = HERMES_HOME / "scripts" / ".fallback_active_state"
LOG_FILE = HERMES_HOME / "logs" / "fallback_proxy.log"
NOTIFY_COOLDOWN = 1800  # 30分钟内不重复推送飞书

# ─── 配置加载 ───────────────────────────────────────────────

def load_backends():
    """从 Hermes 配置加载 primary 和 fallback 后端"""
    import yaml
    cfg_path = HERMES_HOME / "config.yaml"
    env_path = HERMES_HOME / ".env"

    with open(cfg_path) as f:
        cfg = yaml.safe_load(f) or {}

    # 读取 .env 中的 API keys
    env = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip('"').strip("'")

    backends = {}

    # 1. volcengine-agent-plan (primary)
    volc = cfg.get("providers", {}).get("volcengine-agent-plan", {})
    # Try env, then config
    api_key = (env.get("ARK_API_KEY") or volc.get("api_key") or
               env.get("VOLCENGINE_API_KEY") or "")
    base_url = volc.get("base_url", "https://ark.cn-beijing.volces.com/api/plan/v3")
    if api_key:
        backends["volcengine-agent-plan"] = {
            "base_url": base_url.rstrip("/"),
            "api_key": api_key,
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        }

    # 2. deepseek-cn (fallback)
    for cp in cfg.get("custom_providers", []):
        if cp.get("name") == "deepseek-cn":
            dk = cp.get("api_key", "")
            if not dk:
                key_env = cp.get("api_key_env", "")
                dk = env.get(key_env, "")
            backends["deepseek-cn"] = {
                "base_url": cp.get("base_url", "https://api.deepseek.com/v1").rstrip("/"),
                "api_key": dk,
                "auth_header": "Authorization",
                "auth_prefix": "Bearer ",
            }

    return backends


# ─── 飞书通知 ───────────────────────────────────────────────

def send_feishu_notification(primary_name: str, fallback_name: str, status_code: int):
    """推送飞书通知：套餐耗尽，已自动切换"""
    now = time.time()

    # 冷却检查
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            if now - state.get("last_notify", 0) < NOTIFY_COOLDOWN:
                log("feishu notify skipped (cooldown)")
                return
        except Exception:
            pass

    # 更新状态
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({
        "last_notify": now,
        "primary": primary_name,
        "fallback": fallback_name,
        "status": status_code,
        "active": True,
    }, indent=2))

    # 调 Hermes send_message 推飞书
    msg = (
        f"⚠️ **LLM 套餐耗尽 — 已自动切换**\n\n"
        f"主 Provider: {primary_name} → HTTP {status_code}\n"
        f"已切换到: {fallback_name}\n"
        f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"影响范围: Hermes / Claude Code / Codex CLI\n"
        f"建议: 检查火山引擎套餐余额，充值后切回"
    )
    try:
        subprocess.run(
            [sys.executable, "-m", "hermes_cli.send_message", "feishu", msg],
            timeout=10, capture_output=True,
            env={**os.environ, "HERMES_HOME": str(HERMES_HOME)},
        )
        log("feishu notify sent")
    except Exception as e:
        log(f"feishu notify failed: {e}")


# ─── 日志 ───────────────────────────────────────────────────

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, file=sys.stderr, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ─── 代理 Handler ───────────────────────────────────────────

class FallbackProxyHandler(http.server.BaseHTTPRequestHandler):

    backends: dict = {}
    primary_name: str = ""
    fallback_name: str = ""
    fallback_active: bool = False
    fallback_since: float = 0.0

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _copy_headers(self, req: urllib.request.Request, backend: dict):
        """复制客户端 headers 到转发请求"""
        skip = {"host", "content-length", "connection", "authorization",
                backend["auth_header"].lower()}
        for k, v in self.headers.items():
            if k.lower() not in skip:
                req.add_header(k, v)
        # 替换 auth header
        req.add_header(backend["auth_header"],
                       backend["auth_prefix"] + backend["api_key"])

    def _forward(self, backend: dict, body: bytes = None):
        """转发请求到指定后端，返回 (status, headers, body)"""
        path = self.path
        # 替换 base URL
        target_url = backend["base_url"] + path

        req = urllib.request.Request(target_url, data=body, method=self.command)
        self._copy_headers(req, backend)

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_body = resp.read()
                resp_headers = dict(resp.getheaders())
                return resp.status, resp_body, resp_headers
        except urllib.error.HTTPError as e:
            resp_body = e.read() if e.fp else b""
            return e.code, resp_body, dict(e.headers.items())
        except Exception as e:
            return 502, str(e).encode(), {"Content-Type": "text/plain"}

    def _respond(self, status: int, body: bytes, headers: dict = None):
        """发送响应"""
        self.send_response(status)
        if headers:
            for k, v in headers.items():
                if k.lower() not in ("transfer-encoding", "content-length",
                                     "connection", "server", "date"):
                    self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Fallback-Proxy", "active" if self.fallback_active else "standby")
        self.end_headers()
        self.wfile.write(body)

    def _handle_request(self):
        body = self._read_body() if self.command in ("POST", "PUT", "PATCH") else None
        primary = self.backends.get(self.primary_name)
        fallback = self.backends.get(self.fallback_name)

        if not primary:
            self._respond(500, b"No primary backend configured", {})
            return

        # 检查 fallback 是否已激活且未超时
        if self.fallback_active and primary:
            cooldown = 600  # 10 分钟后尝试切回 primary
            if time.time() - self.fallback_since > cooldown:
                # 尝试 primary
                status, resp_body, resp_headers = self._forward(primary, body)
                if status not in (429, 402, 500, 502, 503):
                    self.fallback_active = False
                    log(f"recovered: switched back to {self.primary_name}")
                    self._respond(status, resp_body, resp_headers)
                    return
                # primary still dead, stay on fallback
                self.fallback_since = time.time()

        # 正常路径：先打 primary
        status, resp_body, resp_headers = self._forward(primary, body)

        # 429/402 → fallback
        if status in (429, 402) and fallback:
            log(f"primary {self.primary_name} returned {status}, falling back to {self.fallback_name}")

            if not self.fallback_active:
                self.fallback_active = True
                self.fallback_since = time.time()
                send_feishu_notification(self.primary_name, self.fallback_name, status)

            # 重发到 fallback
            fb_status, fb_body, fb_headers = self._forward(fallback, body)
            log(f"fallback {self.fallback_name} returned {fb_status}")
            self._respond(fb_status, fb_body, fb_headers)
            return

        self._respond(status, resp_body, resp_headers)

    # HTTP 方法
    do_GET = _handle_request
    do_POST = _handle_request
    do_PUT = _handle_request
    do_PATCH = _handle_request
    do_DELETE = _handle_request

    def log_message(self, format, *args):
        """重定向到我们的日志"""
        log(f"access: {self.client_address[0]} - {format % args}")


# ─── 主入口 ─────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="LLM Fallback Proxy")
    parser.add_argument("--port", type=int, default=18793)
    parser.add_argument("--primary", default="volcengine-agent-plan")
    parser.add_argument("--fallback", default="deepseek-cn")
    args = parser.parse_args()

    backends = load_backends()
    if args.primary not in backends:
        print(f"ERROR: primary backend '{args.primary}' not configured", file=sys.stderr)
        sys.exit(1)
    if args.fallback not in backends:
        print(f"ERROR: fallback backend '{args.fallback}' not configured", file=sys.stderr)
        sys.exit(1)

    FallbackProxyHandler.backends = backends
    FallbackProxyHandler.primary_name = args.primary
    FallbackProxyHandler.fallback_name = args.fallback

    # 恢复上次的 fallback 状态
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            if state.get("active"):
                FallbackProxyHandler.fallback_active = True
                FallbackProxyHandler.fallback_since = state.get("last_notify", 0)
                log(f"restored fallback state: active since {time.strftime('%H:%M:%S', time.localtime(FallbackProxyHandler.fallback_since))}")
        except Exception:
            pass

    server = http.server.HTTPServer(("127.0.0.1", args.port), FallbackProxyHandler)
    log(f"LLM Fallback Proxy started on 127.0.0.1:{args.port}")
    log(f"  primary:  {args.primary} ({backends[args.primary]['base_url']})")
    log(f"  fallback: {args.fallback} ({backends[args.fallback]['base_url']})")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
