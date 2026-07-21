#!/usr/bin/env python3
"""
渔芯 LLM Gateway — 公司级大模型管理代理 (aiohttp 版)

路由:
  /anthropic/*       → Anthropic Messages API (Claude Code)
  /openai/*          → OpenAI Chat API (Codex, Hermes)
  /openai/responses  → Responses API SSE 流式翻译 (Codex v0.142+)
  /health            → 状态查询

Primary: DeepSeek 原生, Fallback: 火山引擎 Agent Plan
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import os
import sys
import time
import uuid
import subprocess
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
LOG_DIR = HERMES_HOME / "logs"
STATE_FILE = HERMES_HOME / "scripts" / ".llm_gateway_state.json"

NOTIFY_COOLDOWN = 1800
RECOVERY_INTERVAL = 600

# ─── 配置 ──────────────────────────────────────────────────

def load_env():
    env = {}
    env_file = HERMES_HOME / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def build_backends():
    import yaml
    env = load_env()
    cfg = {}
    cfg_path = HERMES_HOME / "config.yaml"
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}

    ark_key = env.get("ARK_API_KEY", "")
    if not ark_key:
        ark_key = cfg.get("providers", {}).get("volcengine-agent-plan", {}).get("api_key", "")

    # 旧帐号（标准 Ark API，独立配额）
    old_ark_key = env.get("VOLC_ARK_API_KEY", "")
    if not old_ark_key:
        old_ark_key = cfg.get("providers", {}).get("volcengine-ark", {}).get("api_key", "")

    ds_key = env.get("DEEPSEEK_API_KEY", "")
    if not ds_key:
        for cp in cfg.get("custom_providers", []):
            if cp.get("name") == "deepseek-cn":
                ds_key = cp.get("api_key", "")
                if not ds_key:
                    ds_key = env.get(cp.get("api_key_env", ""), "")
                break

    backends = {}
    if ark_key:
        backends["volc-anthropic"] = {"name": "火山引擎(Anthropic)", "url": "https://ark.cn-beijing.volces.com/api/plan", "key": ark_key, "auth": "x-api-key"}
        backends["volc-openai"] = {"name": "火山引擎(OpenAI)", "url": "https://ark.cn-beijing.volces.com/api/plan/v3", "key": ark_key, "auth": "Authorization", "prefix": "Bearer "}
    if old_ark_key:
        backends["old-ark-openai"] = {"name": "旧帐号-火山(OpenAI)", "url": "https://ark.cn-beijing.volces.com/api/v3", "key": old_ark_key, "auth": "Authorization", "prefix": "Bearer "}
    if ds_key:
        backends["ds-anthropic"] = {"name": "DeepSeek(Anthropic)", "url": "https://api.deepseek.com/anthropic", "key": ds_key, "auth": "x-api-key"}
        backends["ds-openai"] = {"name": "DeepSeek(OpenAI)", "url": "https://api.deepseek.com", "key": ds_key, "auth": "Authorization", "prefix": "Bearer "}
    return backends

BACKENDS = build_backends()

ROUTES = {
    "/anthropic": {"primary": "ds-anthropic", "fallback": "volc-anthropic"},
    "/openai": {"primary": "ds-openai", "fallback": "volc-openai"},
}

# ─── 状态 ──────────────────────────────────────────────────

state = {
    "started": time.time(),
    "routes": {},
    "stats": {"requests": 0, "fallbacks": 0},
}
_last_notify = {}

for r in ROUTES:
    state["routes"][r] = {"active": "primary", "since": time.time(), "failures": 0}

def save_state():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))

if STATE_FILE.exists():
    try:
        saved = json.loads(STATE_FILE.read_text())
        for k in ("routes", "stats"):
            if k in saved:
                state[k].update(saved[k])
        state["started"] = time.time()
    except Exception:
        pass

# ─── 日志 ──────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, file=sys.stderr, flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "llm_gateway.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{level}] {msg}\n")
    except Exception:
        pass

# ─── 飞书通知 ──────────────────────────────────────────────

async def notify_fallback(route, primary_name, fb_name, status):
    global _last_notify
    now = time.time()
    if now - _last_notify.get(route, 0) < NOTIFY_COOLDOWN:
        return
    _last_notify[route] = now
    msg = (f"⚠️ **LLM Gateway 自动切换**\n\n"
           f"路由: {route}\n主: {primary_name} → HTTP {status}\n已切: {fb_name}\n"
           f"时间: {datetime.now():%Y-%m-%d %H:%M:%S}")
    try:
        subprocess.run([sys.executable, "-m", "hermes_cli.send_message", "feishu", msg],
                       timeout=10, capture_output=True,
                       env={**os.environ, "HERMES_HOME": str(HERMES_HOME)})
    except Exception as e:
        log(f"feishu fail: {e}", "WARN")

async def notify_recovered(route, name):
    msg = f"✅ **LLM Gateway 已恢复**\n\n路由: {route}\n{name} 已恢复正常\n时间: {datetime.now():%Y-%m-%d %H:%M:%S}"
    try:
        subprocess.run([sys.executable, "-m", "hermes_cli.send_message", "feishu", msg],
                       timeout=10, capture_output=True,
                       env={**os.environ, "HERMES_HOME": str(HERMES_HOME)})
    except Exception:
        pass

# ─── 模型名规范化 ────────────────────────────────────────────

# Codex 内部模型名 → 后端期望的模型名
MODEL_ALIASES = {
    "deepseek": "deepseek-v4-pro",  # deepseek 系列统一
    "gpt-5.6-luna": "deepseek-v4-pro",  # Codex 内部标题生成用
    "gpt-5.5": "deepseek-v4-pro",
    "gpt-5.4": "deepseek-v4-pro",
    "gpt-4o": "deepseek-v4-pro",
}
VOLC_MODEL_ALIASES = {
    "deepseek": "doubao-seed-2-0-pro-260215",
    "gpt-5.6-luna": "doubao-seed-2-0-pro-260215",
    "gpt-5.5": "doubao-seed-2-0-pro-260215",
}

def normalize_model_name(body_json, backend):
    """将 Codex 的各种内部模型名统一改写为后端能接受的模型名"""
    model = body_json.get("model", "")
    url = backend.get("url", "")

    if "deepseek.com" in url:
        aliases = MODEL_ALIASES
    elif "volces.com" in url:
        aliases = VOLC_MODEL_ALIASES
    else:
        return body_json

    # 精确匹配
    if model in aliases:
        body_json["model"] = aliases[model]
        return body_json

    # 前缀匹配（deepseek-v4-flash-260425 → deepseek-v4-pro）
    for prefix, target in aliases.items():
        if model.startswith(prefix):
            body_json["model"] = target
            return body_json

    return body_json

# ─── Responses API ↔ Chat Completions 翻译 ─────────────────

def translate_responses_to_chat(body_json):
    """OpenAI Responses API → Chat Completions API 请求体"""
    # input 可能是字符串（单轮）或消息列表（多轮对话）
    input_val = body_json.get("input")
    if isinstance(input_val, str):
        # 单轮：字符串 → 一条 user 消息
        body_json["messages"] = [{"role": "user", "content": input_val}]
        body_json.pop("input", None)
    else:
        msgs = input_val or body_json.get("messages") or []
        for m in msgs:
            if isinstance(m, dict):
                # 修复 role 缺失（Codex Responses API 可能不带 role）
                if not m.get("role"):
                    m["role"] = "user"  # 默认 user
                if m.get("role") == "developer":
                    m["role"] = "system"
                content = m.get("content")
                # Responses API content 可能是复杂结构，统一转为 Chat 格式
                if isinstance(content, list):
                    # 提取所有 content 中的 text 拼接
                    texts = []
                    for c in content:
                        if isinstance(c, dict):
                            ctype = c.get("type", "")
                            if ctype in ("input_text", "output_text", "text"):
                                texts.append(c.get("text", ""))
                            elif ctype == "refusal":
                                texts.append("[refusal]")
                            elif ctype == "image_url":
                                texts.append("[image]")
                            elif ctype == "input_file":
                                texts.append("[file]")
                            # 忽略未知 type，保留原始结构
                    m["content"] = "\n".join(texts) if texts else ""
                elif content is None or not isinstance(content, str):
                    # null 或非标准类型 → 空字符串
                    m["content"] = ""
        if "input" in body_json:
            body_json["messages"] = body_json.pop("input")
    if "max_output_tokens" in body_json:
        body_json["max_tokens"] = body_json.pop("max_output_tokens")
    # 强制开启流式（SSE 翻译需要）
    body_json["stream"] = True
    body_json.pop("stream_options", None)
    # 移除 Responses API 特有字段
    for k in list(body_json.keys()):
        if k not in ("model", "messages", "max_tokens", "stream", "temperature", "top_p", "stop"):
            body_json.pop(k, None)
    return body_json


def build_sse_response_created(response_id, model, request_body):
    """构建 response.created SSE 事件"""
    return json.dumps({
        "type": "response.created",
        "response": {
            "id": response_id,
            "object": "response",
            "model": model,
            "status": "in_progress",
            "output": [],
            "usage": None,
        }
    })


def build_sse_output_item_added(item_id):
    """构建 response.output_item.added SSE 事件"""
    return json.dumps({
        "type": "response.output_item.added",
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "message",
            "role": "assistant",
            "status": "in_progress",
            "content": [],
        }
    })


def build_sse_output_text_delta(text: str, item_id: str) -> str:
    """response.output_text.delta 事件（Codex用的是beta版Responses API）"""
    return json.dumps({
        "type": "response.output_text.delta",
        "delta": text,
        "item_id": item_id,
        "output_index": 0
    }, ensure_ascii=False)


def build_sse_output_item_done(item_id: str, full_text: str = "") -> str:
    """response.output_item.done 事件"""
    content = []
    if full_text:
        content.append({"type": "output_text", "text": full_text})
    return json.dumps({
        "type": "response.output_item.done",
        "item_id": item_id,
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": content
        }
    }, ensure_ascii=False)


def build_sse_response_completed(response_id, model, full_text, usage):
    """构建 response.completed SSE 事件"""
    output = []
    if full_text:
        output.append({
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": full_text}],
        })
    # 翻译 usage: prompt_tokens → input_tokens, completion_tokens → output_tokens
    normalized_usage = {"input_tokens": 10, "output_tokens": len(full_text) // 4, "total_tokens": 0}
    if usage:
        # Volcengine 可能用 prompt_tokens 或 input_tokens
        normalized_usage["input_tokens"] = usage.get("prompt_tokens") or usage.get("input_tokens", 10)
        normalized_usage["output_tokens"] = usage.get("completion_tokens") or usage.get("output_tokens", len(full_text) // 4)
    normalized_usage["total_tokens"] = normalized_usage["input_tokens"] + normalized_usage["output_tokens"]
    return json.dumps({
        "type": "response.completed",
        "response": {
            "id": response_id,
            "object": "response",
            "model": model,
            "status": "completed",
            "output": output,
            "usage": normalized_usage,
        }
    })


def sse_event(event_name, data_json):
    """格式化 SSE 事件，使用双换行确保兼容性"""
    return f"event: {event_name}\r\ndata: {data_json}\r\n\r\n".encode("utf-8")


async def sse_stream_response(backend, rest, headers, body):
    """
    SSE 流式转发 + Responses API 翻译。
    向 DeepSeek 发起 stream=true 请求，边收边翻译成 Responses API SSE，
    通过 async generator yield 字节。
    """
    target = backend["url"] + rest
    auth_val = backend.get("prefix", "") + backend["key"]

    req_headers = {}
    skip = {"host", "content-length", "connection", "transfer-encoding", "accept"}
    for k, v in headers.items():
        if k.lower() not in skip and k.lower() != backend["auth"].lower():
            req_headers[k] = v
    req_headers[backend["auth"]] = auth_val
    req_headers["Accept"] = "text/event-stream"

    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    item_id = f"msg_{uuid.uuid4().hex[:12]}"
    model_name = "unknown"
    full_text = ""
    reasoning_buf = ""   # 缓冲推理过程（思考链），不直接发送
    usage = {}
    stream_started = False
    has_content = False
    in_content_phase = False  # True=已进入正式回复，抛弃之前的 reasoning_buf

    log(f"SSE→ {target[:80]}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(target, headers=req_headers, data=body,
                                     timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    err_body = await resp.read()
                    log(f"SSE← HTTP {resp.status}: {err_body[:200]}", "WARN")
                    yield json.dumps({"type": "error", "error": {"message": f"upstream {resp.status}"}}).encode()
                    return

                # 发送 response.created
                yield sse_event("response.created", build_sse_response_created(response_id, model_name, body.decode()[:200]))
                stream_started = True

                # 逐行读取 SSE
                buffer = b""
                async for chunk in resp.content.iter_any():
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        line = line.strip()
                        if not line or line == b"data: [DONE]":
                            if line == b"data: [DONE]":
                                break
                            continue
                        if not line.startswith(b"data: "):
                            continue

                        try:
                            data = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue

                        # DEBUG: 记录原始 SSE 数据结构
                        if not has_content and not data.get("usage"):
                            log(f"SSE RAW: {json.dumps(data, ensure_ascii=False)[:300]}")

                        # 提取 model
                        if data.get("model"):
                            model_name = data.get("model")

                        # 提取 usage
                        if data.get("usage"):
                            usage = data.get("usage")

                        # 提取 delta content + reasoning
                        choices = data.get("choices", [])
                        for choice in choices:
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            reasoning = delta.get("reasoning_content", "")

                            if content:
                                # 正式回复内容：丢弃之前的思考链缓冲
                                if not in_content_phase:
                                    in_content_phase = True
                                    reasoning_buf = ""  # 不再需要
                                # 首次内容时先发送 item.added
                                if not has_content:
                                    yield sse_event("response.output_item.added", build_sse_output_item_added(item_id))
                                has_content = True
                                full_text += content
                                yield sse_event("response.output_text.delta", build_sse_output_text_delta(content, item_id))
                            elif reasoning:
                                # 推理过程：只缓冲，不发送（避免 Codex 把思考链当工具调用）
                                reasoning_buf += reasoning

                # 发送 response.output_item.done + response.completed
                if stream_started:
                    # 如果全程只收到 reasoning 没收到 content，用 reasoning 兜底
                    if not has_content and reasoning_buf:
                        yield sse_event("response.output_item.added", build_sse_output_item_added(item_id))
                        full_text = reasoning_buf
                        yield sse_event("response.output_text.delta", build_sse_output_text_delta(reasoning_buf, item_id))
                    yield sse_event("response.output_item.done", build_sse_output_item_done(item_id, full_text))
                    yield sse_event("response.completed", build_sse_response_completed(response_id, model_name, full_text, usage))

                log(f"SSE← done ({len(full_text)} chars)")

    except asyncio.TimeoutError:
        log("SSE← TIMEOUT", "WARN")
        if stream_started:
            yield sse_event("response.output_item.done", build_sse_output_item_done(item_id, full_text))
            yield sse_event("response.completed", build_sse_response_completed(response_id, model_name, full_text, usage))
    except Exception as e:
        log(f"SSE← ERROR: {e}", "WARN")
        if stream_started:
            yield sse_event("response.output_item.done", build_sse_output_item_done(item_id, full_text))
            yield sse_event("response.completed", build_sse_response_completed(response_id, model_name, full_text, usage))
        else:
            yield json.dumps({"type": "error", "error": {"message": str(e)}}).encode()


# ─── 请求转发（非流式）─────────────────────────────────────

async def forward(session, backend, path, method, headers, body):
    """转发请求到指定后端（非流式）"""
    target = backend["url"] + path
    auth_val = backend.get("prefix", "") + backend["key"]

    req_headers = {}
    skip = {"host", "content-length", "connection", "transfer-encoding"}
    for k, v in headers.items():
        if k.lower() not in skip and k.lower() != backend["auth"].lower():
            req_headers[k] = v
    req_headers[backend["auth"]] = auth_val

    log(f"→ {method} {target[:100]}")
    try:
        async with session.request(method, target, headers=req_headers, data=body,
                                    timeout=aiohttp.ClientTimeout(total=60)) as resp:
            resp_body = await resp.read()
            log(f"← HTTP {resp.status} ({len(resp_body)}B)")
            return resp.status, resp_body, dict(resp.headers)
    except asyncio.TimeoutError:
        log(f"← TIMEOUT", "WARN")
        return 504, b'{"error":"upstream timeout"}', {"Content-Type": "application/json"}
    except Exception as e:
        log(f"← ERROR: {e}", "WARN")
        return 502, json.dumps({"error": str(e)}).encode(), {"Content-Type": "application/json"}


# ─── HTTP Handler ──────────────────────────────────────────

async def handle(request: web.Request):
    state["stats"]["requests"] += 1

    # /health
    if request.path in ("/health", "/health/"):
        return web.json_response({
            "gateway": "渔芯 LLM Gateway",
            "uptime": f"{time.time() - state['started']:.0f}s",
            "routes": {r: state["routes"][r]["active"] for r in ROUTES},
            "backends": {k: v["name"] for k, v in BACKENDS.items()},
            "stats": state["stats"],
        })

    # ── Admin API: 模型切换 ──
    if request.path in ("/admin/switch", "/admin/switch/"):
        action = request.query.get("action", "status")
        route_key = request.query.get("route", "/openai")

        if action == "status":
            rs = state["routes"].get(route_key, {})
            return web.json_response({
                "route": route_key,
                "active": rs.get("active", "?"),
                "primary": ROUTES[route_key]["primary"],
                "fallback": ROUTES[route_key]["fallback"],
            })

        if action == "to-primary":
            state["routes"][route_key]["active"] = "primary"
            state["routes"][route_key]["since"] = time.time()
            state["routes"][route_key]["failures"] = 0
            save_state()
            log(f"ADMIN: {route_key} → primary ({ROUTES[route_key]['primary']})")
            return web.json_response({"switched": True, "route": route_key, "now": "primary"})

        if action == "to-fallback":
            state["routes"][route_key]["active"] = "fallback"
            state["routes"][route_key]["since"] = time.time()
            state["routes"][route_key]["failures"] = 0
            save_state()
            log(f"ADMIN: {route_key} → fallback ({ROUTES[route_key]['fallback']})")
            return web.json_response({"switched": True, "route": route_key, "now": "fallback"})

        if action == "flip":
            # 反转 primary ↔ fallback
            old = ROUTES[route_key]
            ROUTES[route_key] = {"primary": old["fallback"], "fallback": old["primary"]}
            state["routes"][route_key]["active"] = "primary"
            state["routes"][route_key]["since"] = time.time()
            state["routes"][route_key]["failures"] = 0
            save_state()
            log(f"ADMIN: {route_key} flipped → primary={ROUTES[route_key]['primary']}, fallback={ROUTES[route_key]['fallback']}")
            return web.json_response({
                "switched": True,
                "route": route_key,
                "primary": ROUTES[route_key]["primary"],
                "fallback": ROUTES[route_key]["fallback"],
            })

        return web.json_response({"error": f"unknown action: {action}"}, status=400)

    # 路由匹配
    route = None
    rest = request.path
    for prefix in sorted(ROUTES.keys(), key=len, reverse=True):
        if request.path.startswith(prefix):
            route = prefix
            rest = request.path[len(prefix):] or "/"
            break

    # ── Responses API → Chat Completions SSE 翻译（Codex v0.142+） ──
    is_responses = request.path.startswith("/openai/responses") or request.path.startswith("/openai/v1/responses")
    if is_responses:
        route = "/openai"
        rest = "/v1/chat/completions"

    if not route:
        return web.json_response({"error": "no route", "routes": list(ROUTES.keys())}, status=404)

    cfg = ROUTES[route]
    rs = state["routes"][route]

    # 选后端
    if rs["active"] == "fallback":
        backend = BACKENDS.get(cfg["fallback"])
        which = "fallback"
    else:
        backend = BACKENDS.get(cfg["primary"])
        which = "primary"

    if not backend:
        return web.json_response({"error": "no backend"}, status=502)

    # ── 修正 Responses API 路径（火山引擎不需要 /v1 前缀） ──
    if is_responses and "volces.com" in backend["url"]:
        rest = "/chat/completions"

    body = await request.read() if request.method in ("POST", "PUT", "PATCH") else None
    headers = dict(request.headers)

    # ── Responses API: 翻译请求体 + SSE 流式返回 ──
    if is_responses and body:
        try:
            body_json = json.loads(body)
            # DEBUG: 记录原始 input 类型（方便排查 Codex 格式变化）
            inp = body_json.get("input")
            if isinstance(inp, list):
                log(f"RESPONSES input is list[{len(inp)}]: first={json.dumps(inp[0], ensure_ascii=False)[:200] if inp else 'empty'} last={json.dumps(inp[-1], ensure_ascii=False)[:200] if len(inp)>1 else ''}")
            body_json = translate_responses_to_chat(body_json)
            # 统一模型名（Codex 会用各种内部模型名）
            body_json = normalize_model_name(body_json, backend)
            body = json.dumps(body_json).encode()
            log("RESPONSES→CHAT: SSE streaming")
        except Exception as e:
            log(f"RESPONSES→CHAT error: {e}", "WARN")

    # ── SSE 流式响应 ──
    if is_responses:
        resp = web.StreamResponse(status=200)
        resp.headers["Content-Type"] = "text/event-stream"
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["Connection"] = "keep-alive"
        resp.headers["X-Gateway-Route"] = route
        resp.headers["X-Gateway-Backend"] = which
        await resp.prepare(request)

        try:
            async for chunk in sse_stream_response(backend, rest, headers, body):
                await resp.write(chunk)
        except Exception as e:
            log(f"SSE stream error: {e}", "WARN")

        await resp.write_eof()
        return resp

    # ─── 非流式：原有逻辑 ───
    async with aiohttp.ClientSession() as session:
        status_code, resp_body, resp_headers = await forward(
            session, backend, rest, request.method, headers, body)

    # Fallback 判断
    if status_code in (429, 402, 500, 502, 503, 504) and which == "primary":
        fb = BACKENDS.get(cfg["fallback"])
        if fb:
            log(f"FALLBACK: {route} {backend['name']} → {fb['name']} (HTTP {status_code})")
            rs["active"] = "fallback"
            rs["since"] = time.time()
            rs["failures"] += 1
            state["stats"]["fallbacks"] += 1
            save_state()
            await notify_fallback(route, backend["name"], fb["name"], status_code)

            async with aiohttp.ClientSession() as session:
                status_code, resp_body, resp_headers = await forward(
                    session, fb, rest, request.method, headers, body)

    resp = web.StreamResponse(status=status_code)
    resp.headers["X-Gateway-Route"] = route
    resp.headers["X-Gateway-Backend"] = which
    for k, v in resp_headers.items():
        if k.lower() not in ("transfer-encoding", "content-length", "connection", "server", "date"):
            resp.headers[k] = v
    resp.headers["Content-Length"] = str(len(resp_body))
    await resp.prepare(request)
    await resp.write(resp_body)
    return resp


# ─── 恢复循环 ──────────────────────────────────────────────

async def recovery_loop(app):
    while True:
        await asyncio.sleep(RECOVERY_INTERVAL)
        async with aiohttp.ClientSession() as session:
            for route, cfg in ROUTES.items():
                rs = state["routes"][route]
                if rs["active"] == "fallback":
                    backend = BACKENDS.get(cfg["primary"])
                    if not backend:
                        continue
                    try:
                        ping_url = backend["url"] + "/v1/chat/completions"
                        auth_val = backend.get("prefix", "") + backend["key"]
                        hdrs = {"Content-Type": "application/json", backend["auth"]: auth_val}
                        body = json.dumps({"model": "deepseek-v4-flash", "max_tokens": 1,
                                           "messages": [{"role": "user", "content": "."}]})
                        async with session.post(ping_url, headers=hdrs, data=body,
                                                 timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status == 200:
                                log(f"RECOVERY: {route} primary restored")
                                rs["active"] = "primary"
                                rs["since"] = time.time()
                                rs["failures"] = 0
                                save_state()
                                await notify_recovered(route, backend["name"])
                    except Exception:
                        pass


# ─── 启动 ──────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18888)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    for r, c in ROUTES.items():
        if c["primary"] not in BACKENDS:
            print(f"FATAL: {r} primary '{c['primary']}' not configured", file=sys.stderr)
            sys.exit(1)

    log("=" * 40)
    log(f"渔芯 LLM Gateway {args.host}:{args.port}")
    log("  SSE streaming enabled for /openai/responses")
    for r, c in ROUTES.items():
        p = BACKENDS.get(c["primary"], {})
        f = BACKENDS.get(c["fallback"], {})
        log(f"  {r}: {p.get('name','?')} → {f.get('name','?')}")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle)

    async def startup(app):
        asyncio.create_task(recovery_loop(app))

    app.on_startup.append(startup)

    runner = web.AppRunner(app)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, args.host, args.port)
    loop.run_until_complete(site.start())
    log(f"listening on {args.host}:{args.port}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()

if __name__ == "__main__":
    main()
