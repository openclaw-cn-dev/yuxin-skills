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
from aiohttp.client_exceptions import ClientConnectionError
import json
import os
import sys
import time
import uuid
import subprocess
from pathlib import Path
from datetime import datetime

# ── 多模型智能调度框架 ──
_MODEL_POOL_LOADED = False
try:
    # Gateway 进程可能不在 scripts/ 目录下
    import os as _os
    _scripts_dir = str(Path(_os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / "scripts")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "llm_model_pool", 
        f"{_scripts_dir}/llm_model_pool.py"
    )
    if spec and spec.loader:
        _pool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_pool)
        MODEL_REGISTRY = _pool.MODEL_REGISTRY
        select_model = _pool.select_model
        QuotaTracker = _pool.QuotaTracker
        get_quota_tracker = _pool.get_quota_tracker
        detect_request_type = _pool.detect_request_type
        model_cost_rank = _pool.model_cost_rank
        _MODEL_POOL_LOADED = True
except Exception as e:
    import traceback
    print(f"[WARN] llm_model_pool load failed: {e}", file=sys.stderr)

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

    mm_key = env.get("MINIMAX_API_KEY", "")
    if not mm_key:
        mm_key = cfg.get("providers", {}).get("minimax-custom", {}).get("api_key", "")

    # ── 免费模型 pool ──
    gemini_key = env.get("GOOGLE_API_KEY", "") or env.get("GEMINI_API_KEY", "")
    glm_key = env.get("ZHIPUAI_API_KEY", "")
    qwen_key = env.get("DASHSCOPE_API_KEY", "")
    doubao_key = env.get("ARK_API_KEY", "")  # 复用火山 Agent Plan key
    groq_key = env.get("GROQ_API_KEY", "")

    backends = {}
    if ark_key:
        backends["volc-anthropic"] = {"name": "火山引擎(Anthropic)", "url": "https://ark.cn-beijing.volces.com/api/plan", "key": ark_key, "auth": "x-api-key"}
        backends["volc-openai"] = {"name": "火山引擎(OpenAI)", "url": "https://ark.cn-beijing.volces.com/api/plan/v3", "key": ark_key, "auth": "Authorization", "prefix": "Bearer "}
    if old_ark_key:
        backends["old-ark-openai"] = {"name": "旧帐号-火山(OpenAI)", "url": "https://ark.cn-beijing.volces.com/api/v3", "key": old_ark_key, "auth": "Authorization", "prefix": "Bearer "}
    if ds_key:
        backends["ds-anthropic"] = {"name": "DeepSeek(Anthropic)", "url": "https://api.deepseek.com/anthropic", "key": ds_key, "auth": "x-api-key"}
        backends["ds-openai"] = {"name": "DeepSeek(OpenAI)", "url": "https://api.deepseek.com", "key": ds_key, "auth": "Authorization", "prefix": "Bearer "}
    if mm_key:
        backends["minimax-anthropic"] = {"name": "MiniMax(Anthropic)", "url": "https://api.minimaxi.com/anthropic", "key": mm_key, "auth": "x-api-key"}
        backends["minimax-openai"] = {"name": "MiniMax(OpenAI)", "url": "https://api.minimaxi.com", "key": mm_key, "auth": "Authorization", "prefix": "Bearer "}
    if gemini_key:
        backends["gemini-openai"] = {"name": "Gemini(OpenAI兼容)", "url": "https://generativelanguage.googleapis.com/v1beta/openai", "key": gemini_key, "auth": "Authorization", "prefix": "Bearer "}
    if glm_key:
        backends["glm-openai"] = {"name": "智谱GLM(OpenAI)", "url": "https://open.bigmodel.cn/api/paas/v4", "key": glm_key, "auth": "Authorization", "prefix": "Bearer "}
    if qwen_key:
        backends["qwen-openai"] = {"name": "通义千问(OpenAI)", "url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "key": qwen_key, "auth": "Authorization", "prefix": "Bearer "}
    if doubao_key:
        backends["doubao-openai"] = {"name": "豆包Seed(OpenAI)", "url": "https://ark.cn-beijing.volces.com/api/v3", "key": doubao_key, "auth": "Authorization", "prefix": "Bearer "}
    if groq_key:
        backends["groq-openai"] = {"name": "Groq(OpenAI)", "url": "https://api.groq.com/openai/v1", "key": groq_key, "auth": "Authorization", "prefix": "Bearer "}
    return backends

BACKENDS = build_backends()

ROUTES = {
    "/anthropic": {"primary": "minimax-anthropic", "fallback": "ds-anthropic"},
    # 2026-08-28: /openai 主路由切到 GLM-5.3-Flash（智谱，OpenAI 兼容），MiniMax 转 fallback 保底
    "/openai": {"primary": "glm-openai", "fallback": "minimax-openai"},
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

# ── 初始化 Quota Tracker（必须在 log() 定义之后）──
_quota_tracker = None
if _MODEL_POOL_LOADED:
    try:
        _quota_tracker = get_quota_tracker()
        log(f"MODEL-POOL: loaded ({len(MODEL_REGISTRY)} models)", "INFO")
    except Exception as e:
        log(f"MODEL-POOL: QuotaTracker init failed: {e}", "WARN")

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
    "MiniMax-M3": "deepseek-v4-pro",  # 全局默认模型名适配
    "gpt-5.6-luna": "deepseek-v4-pro",  # Codex 内部标题生成用
    "gpt-5.5": "deepseek-v4-pro",
    "gpt-5.4": "deepseek-v4-pro",
    "gpt-4o": "deepseek-v4-pro",
    # Claude Code 默认模型名 → deepseek-v4-pro（用户 2026-07-29 决定）
    "claude-sonnet-5": "deepseek-v4-pro",
    "claude-opus-5": "deepseek-v4-pro",
    "claude-haiku-5": "deepseek-v4-pro",
    "claude-fable-5": "deepseek-v4-pro",
    "claude-sonnet-4-6": "deepseek-v4-pro",
    "claude-sonnet-4-5": "deepseek-v4-pro",
    "claude-opus-4-8": "deepseek-v4-pro",
    "claude-opus-4-7": "deepseek-v4-pro",
    "claude-opus-4-6": "deepseek-v4-pro",
    "claude-opus-4-5": "deepseek-v4-pro",
    "claude-sonnet-4-20250514": "deepseek-v4-pro",
    "claude-sonnet-4": "deepseek-v4-pro",
    "claude-3-7-sonnet-20250219": "deepseek-v4-pro",
    "claude-3-5-sonnet-20241022": "deepseek-v4-pro",
    "claude-3-5-sonnet-latest": "deepseek-v4-pro",
    "claude-3-5-haiku-20241022": "deepseek-v4-pro",
    "claude-3-opus-20240229": "deepseek-v4-pro",
    "claude-3-opus-latest": "deepseek-v4-pro",
    "claude-3-haiku-20240307": "deepseek-v4-pro",
    # Claude Code 短别名
    "opus": "deepseek-v4-pro",
    "sonnet": "deepseek-v4-pro",
    "haiku": "deepseek-v4-pro",
}
VOLC_MODEL_ALIASES = {
    "deepseek": "doubao-seed-2-0-pro-260215",
    "gpt-5.6-luna": "doubao-seed-2-0-pro-260215",
    "gpt-5.5": "doubao-seed-2-0-pro-260215",
}

# MiniMax 模型别名：Codex 内部模型名 → MiniMax-M3
MINIMAX_MODEL_ALIASES = {
    "gpt-5.6-sol": "MiniMax-M3",
    "gpt-5.6-luna": "MiniMax-M3",
    "gpt-5.5": "MiniMax-M3",
    "gpt-5.4": "MiniMax-M3",
    "gpt-4o": "MiniMax-M3",
    "deepseek": "MiniMax-M3",
    "deepseek-v4-pro": "MiniMax-M3",
    "deepseek-v4-flash": "MiniMax-M3",
}

def get_ping_model(backend):
    """根据 backend URL 选 health-check ping 模型。

    - minimaxi → MiniMax-M3 (从 MINIMAX_MODEL_ALIASES 任一 value 取)
    - deepseek → deepseek-v4-flash (最便宜)
    - volces → None (火山端点 ID 不固定，跳过自动恢复)
    """
    url = backend.get("url", "")
    if "minimaxi.com" in url:
        # MINIMAX_MODEL_ALIASES 所有 value 都是同一个 model，取第一个即可
        return next(iter(MINIMAX_MODEL_ALIASES.values()), "MiniMax-M3")
    elif "deepseek.com" in url:
        return "deepseek-v4-flash"
    elif "volces.com" in url:
        return None  # 火山端点用 ep-xxx ID 不可硬编码，跳过自动 ping
    else:
        return "deepseek-v4-flash"

def normalize_model_name(body_json, backend):
    """将 Codex 的各种内部模型名统一改写为后端能接受的模型名"""
    model = body_json.get("model", "")
    url = backend.get("url", "")

    # MiniMax 不兼容 OpenAI 的 frequency_penalty/presence_penalty（会让流异常中断）
    # 仅在路由到 MiniMax 后端时过滤，避免影响 DeepSeek/火山
    if "minimaxi.com" in url:
        for k in ("frequency_penalty", "presence_penalty", "logprobs", "top_logprobs"):
            body_json.pop(k, None)

    if "deepseek.com" in url:
        aliases = MODEL_ALIASES
    elif "volces.com" in url:
        aliases = VOLC_MODEL_ALIASES
    elif "minimaxi.com" in url:
        aliases = MINIMAX_MODEL_ALIASES
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
        new_messages = []
        for m in msgs:
            if not isinstance(m, dict):
                continue
            mtype = m.get("type", "message")
            role = m.get("role")

            # 1) 处理 function_call_output (Codex Responses API 的工具结果)
            #    → OpenAI Chat Completions: role=tool + tool_call_id + content
            if mtype == "function_call_output":
                output_text = m.get("output", "")
                # output 可能是字符串或列表
                if isinstance(output_text, list):
                    parts = []
                    for c in output_text:
                        if isinstance(c, dict) and c.get("type") in ("input_text", "output_text", "text"):
                            parts.append(c.get("text", ""))
                        elif isinstance(c, str):
                            parts.append(c)
                    output_text = "\n".join(parts) if parts else ""
                new_messages.append({
                    "role": "tool",
                    "tool_call_id": m.get("call_id", ""),
                    "content": output_text if isinstance(output_text, str) else str(output_text),
                })
                continue

            # 2) 处理 function_call (Codex 端记录的 assistant 工具调用历史)
            #    → OpenAI Chat Completions: role=assistant + tool_calls
            if mtype == "function_call":
                fn_args = m.get("arguments", "{}")
                if isinstance(fn_args, dict):
                    fn_args = json.dumps(fn_args, ensure_ascii=False)
                new_messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": m.get("call_id", ""),
                        "type": "function",
                        "function": {
                            "name": m.get("name", ""),
                            "arguments": fn_args if isinstance(fn_args, str) else str(fn_args),
                        }
                    }]
                })
                continue

            # 3) 标准 message (developer/user/assistant)
            if not role:
                role = "user"  # 默认 user
            if role == "developer":
                role = "system"
            content = m.get("content")
            if isinstance(content, list):
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
                content = "\n".join(texts) if texts else ""
            elif content is None or not isinstance(content, str):
                content = ""
            new_messages.append({"role": role, "content": content})

        if new_messages:
            body_json["messages"] = new_messages
            body_json.pop("input", None)
    if "max_output_tokens" in body_json:
        body_json["max_tokens"] = body_json.pop("max_output_tokens")
    # 强制开启流式（SSE 翻译需要）
    body_json["stream"] = True
    body_json.pop("stream_options", None)

    # 翻译 tools: Responses API 风格 → Chat Completions 风格（结构相同，直接保留）
    if "tools" in body_json:
        tools_in = body_json["tools"]
        if isinstance(tools_in, list):
            tools_out = []
            skipped = 0
            for t in tools_in:
                if not isinstance(t, dict):
                    skipped += 1
                    continue
                # Codex Responses API 工具格式: {type: "function", function: {...}, name?, description?, strict?}
                # OpenAI Chat Completions 工具格式: {type: "function", function: {name, description, parameters, strict?}}
                # 兼容处理：把 name/description 提到 function 内（如果它们在顶层）
                fn = t.get("function") or {}
                if not fn:
                    # 扁平格式兜底
                    fn = {"name": t.get("name"), "description": t.get("description"),
                          "parameters": t.get("parameters")}
                # 确保 function 内含 name + parameters
                if not fn.get("name") and t.get("name"):
                    fn["name"] = t["name"]
                if not fn.get("description") and t.get("description"):
                    fn["description"] = t["description"]
                if "parameters" not in fn and "parameters" in t:
                    fn["parameters"] = t["parameters"]
                # 过滤无效工具：name 为 null/空 或 parameters 为 null（Codex deferred tools）
                tool_name = fn.get("name")
                if not tool_name or not isinstance(tool_name, str):
                    skipped += 1
                    continue
                tools_out.append({"type": "function", "function": fn})
            if tools_out:
                body_json["tools"] = tools_out
                # 保留 tool_choice（Codex 默认 "auto"，MiniMax 也支持）
                if "tool_choice" not in body_json:
                    body_json["tool_choice"] = "auto"
                if skipped:
                    log(f"⚠️ Filtered {skipped} invalid tools (Codex deferred/null name)", "WARN")
            else:
                # 所有工具都无效 — 不发 tools 字段，让模型纯聊天
                body_json.pop("tools", None)
                body_json.pop("tool_choice", None)
        else:
            body_json.pop("tools", None)

    # 移除 Responses API 特有字段（注意保留 tools/tool_choice/parallel_tool_calls）
    keep = ("model", "messages", "max_tokens", "stream", "temperature", "top_p", "stop",
            "tools", "tool_choice", "parallel_tool_calls", "user", "metadata")
    for k in list(body_json.keys()):
        if k not in keep:
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


# ─── Reasoning (思考链) SSE 事件 ────────────────────────────

def ***SECRET***(item_id: str) -> str:
    """response.output_item.added 事件（reasoning item，Codex 用来显示思考过程）"""
    return json.dumps({
        "type": "response.output_item.added",
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "reasoning",
            "summary": [],
        }
    })


def ***SECRET***(item_id: str, summary_index: int, delta_text: str) -> str:
    """response.reasoning_summary_text.delta 事件（推理内容增量）"""
    return json.dumps({
        "type": "response.reasoning_summary_text.delta",
        "item_id": item_id,
        "output_index": 0,
        "summary_index": summary_index,
        "delta": delta_text,
    }, ensure_ascii=False)


def build_sse_reasoning_item_done(item_id: str, summary_text: str) -> str:
    """response.output_item.done 事件（reasoning item 完成）"""
    return json.dumps({
        "type": "response.output_item.done",
        "item_id": item_id,
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "reasoning",
            "summary": [{"text": summary_text}] if summary_text else [],
        }
    })


# ─── Function Call (工具调用) SSE 事件 ────────────────────────

def build_sse_function_call_added(item_id: str, call_id: str, name: str) -> str:
    """response.output_item.added 事件（function_call item，Codex 用来识别工具调用）"""
    return json.dumps({
        "type": "response.output_item.added",
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "function_call",
            "call_id": call_id,
            "name": name,
            "arguments": "",
            "status": "in_progress",
        }
    })


def ***SECRET***(item_id: str, delta_text: str) -> str:
    """response.function_call_arguments.delta 事件（参数增量，OpenAI 流式分块）"""
    return json.dumps({
        "type": "response.function_call_arguments.delta",
        "item_id": item_id,
        "output_index": 0,
        "delta": delta_text,
    }, ensure_ascii=False)


def ***SECRET***(item_id: str, full_args: str) -> str:
    """response.function_call_arguments.done 事件（参数完整）"""
    return json.dumps({
        "type": "response.function_call_arguments.done",
        "item_id": item_id,
        "output_index": 0,
        "arguments": full_args,
    }, ensure_ascii=False)


def build_sse_function_call_done(item_id: str, call_id: str, name: str, full_args: str) -> str:
    """response.output_item.done 事件（function_call item 完成）"""
    return json.dumps({
        "type": "response.output_item.done",
        "item_id": item_id,
        "output_index": 0,
        "item": {
            "id": item_id,
            "type": "function_call",
            "call_id": call_id,
            "name": name,
            "arguments": full_args,
            "status": "completed",
        }
    }, ensure_ascii=False)


def sse_event(event_name, data_json):
    """格式化 SSE 事件，使用双换行确保兼容性"""
    return f"event: {event_name}\r\ndata: {data_json}\r\n\r\n".encode("utf-8")


async def sse_stream_response(backend, rest, headers, body, fallback_backend=None):
    """
    SSE 流式转发 + Responses API 翻译。

    处理上游 chat/completions 流，翻译成 OpenAI Responses API SSE 事件给 Codex。

    支持:
    - reasoning_content (思考链) → response.reasoning_summary_text.delta
    - content (正文) → response.output_text.delta
    - tool_calls (工具调用，多 chunk 流式累积) → response.function_call_arguments.delta
    - finish_reason (tool_calls/stop/length) → 正确关闭所有 item
    """
    target = backend["url"] + rest
    auth_val = backend.get("prefix", "") + backend["key"]

    req_headers = {}
    # MiniMax 网关有 gzip 解压 bug (incorrect header check) — 不发送 Accept-Encoding
    # 走 HTTP/1.1 明文传输，规避服务端响应头标记 gzip 但实际是裸文本的兼容性问题
    skip = {"host", "content-length", "connection", "transfer-encoding",
            "accept", "accept-encoding"}
    for k, v in headers.items():
        if k.lower() not in skip and k.lower() != backend["auth"].lower():
            req_headers[k] = v
    req_headers[backend["auth"]] = auth_val
    req_headers["Accept"] = "text/event-stream"
    # 显式置空（防御 Codex/curl 等客户端额外加进来）
    req_headers["Accept-Encoding"] = "identity"

    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    content_item_id = f"msg_{uuid.uuid4().hex[:12]}"
    reasoning_item_id = f"rs_{uuid.uuid4().hex[:12]}"
    model_name = "unknown"
    full_text = ""
    reasoning_text = ""
    usage = {}
    stream_started = False

    # 状态机
    has_content_item = False    # message item 是否已 .added
    has_reasoning_item = False  # reasoning item 是否已 .added
    tool_calls = {}             # {index: {id, name, arguments, item_id, added}}
    finish_reason = None

    # MiniMax 思考链解析：reasoning_content 字段 OR content 字段里的 <think>...</think> 标记
    content_buf = ""            # 未提交的 content chunk（用于跨边界匹配）
    in_think = False            # 当前是否在 <think>...</think> 块内
    THINK_OPEN = "<think>"
    THINK_CLOSE = "</think>"

    feeder = None
    queue = None
    async def cleanup_feeder():
        nonlocal feeder
        if feeder is not None and not feeder.done():
            feeder.cancel()
            try:
                await feeder
            except (asyncio.CancelledError, Exception):
                pass

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

                # MiniMax 长思考阶段不发心跳，空闲 120s 服务端会断流
                # 用 asyncio.Queue + feeder task 实现 SSE 心跳：每 20s 没数据就 yield ": keepalive\n\n"
                HEARTBEAT_INTERVAL = 20  # 秒（远小于 MiniMax 120s 阈值）

                async def feed_queue():
                    async for chunk in resp.content.iter_any():
                        await queue.put(chunk)
                    await queue.put(None)  # sentinel

                queue = asyncio.Queue()
                feeder = asyncio.create_task(feed_queue())

                # 逐行读取 SSE
                buffer = b""
                while True:
                    try:
                        chunk = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_INTERVAL)
                    except asyncio.TimeoutError:
                        # 20s 没数据，发 SSE 注释行保活（不影响 Codex 解析）
                        yield b": keepalive\n\n"
                        continue
                    if chunk is None:
                        break
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

                        # DEBUG: 记录原始 SSE 数据结构（首个有内容的 chunk）
                        if not has_content_item and not tool_calls and not data.get("usage"):
                            log(f"SSE RAW: {json.dumps(data, ensure_ascii=False)[:300]}")

                        # 提取 model
                        if data.get("model"):
                            model_name = data.get("model")

                        # 提取 usage
                        if data.get("usage"):
                            usage = data.get("usage")

                        # 提取 finish_reason
                        for choice in data.get("choices", []):
                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
                                break

                        # 处理 delta
                        for choice in data.get("choices", []):
                            delta = choice.get("delta", {}) or {}
                            content = delta.get("content", "") or ""
                            reasoning = delta.get("reasoning_content", "") or ""
                            tc_delta = delta.get("tool_calls", []) or []

                            # 1) 处理 reasoning (独立字段)
                            if reasoning:
                                if not has_reasoning_item:
                                    yield sse_event("response.output_item.added",
                                                    ***SECRET***(reasoning_item_id))
                                    has_reasoning_item = True
                                yield sse_event("response.reasoning_summary_text.delta",
                                                ***SECRET***(reasoning_item_id, 0, reasoning))
                                reasoning_text += reasoning

                            # 2) 处理 content (MiniMax 风格：<think>...</think> 标记包在 content 里)
                            if content:
                                content_buf += content
                                while content_buf:
                                    if not in_think:
                                        # 找 <think> 开始标记
                                        idx = content_buf.find(THINK_OPEN)
                                        if idx >= 0:
                                            #<think> 之前的部分是正文
                                            pre = content_buf[:idx]
                                            if pre:
                                                if not has_content_item:
                                                    yield sse_event("response.output_item.added",
                                                                    build_sse_output_item_added(content_item_id))
                                                    has_content_item = True
                                                full_text += pre
                                                yield sse_event("response.output_text.delta",
                                                                build_sse_output_text_delta(pre, content_item_id))
                                            content_buf = content_buf[idx + len(THINK_OPEN):]
                                            in_think = True
                                        else:
                                            # 没有 <think>
                                            # 保留最后 6 字符防跨 chunk 的 "<thin"
                                            safe_len = max(0, len(content_buf) - len(THINK_OPEN) + 1)
                                            safe_text = content_buf[:safe_len]
                                            if safe_text:
                                                if not has_content_item:
                                                    yield sse_event("response.output_item.added",
                                                                    build_sse_output_item_added(content_item_id))
                                                    has_content_item = True
                                                full_text += safe_text
                                                yield sse_event("response.output_text.delta",
                                                                build_sse_output_text_delta(safe_text, content_item_id))
                                            content_buf = content_buf[safe_len:]
                                            break
                                    else:
                                        # 在 think 块内，找 </think> 结束
                                        idx = content_buf.find(THINK_CLOSE)
                                        if idx >= 0:
                                            think_text = content_buf[:idx]
                                            if not has_reasoning_item:
                                                yield sse_event("response.output_item.added",
                                                                ***SECRET***(reasoning_item_id))
                                                has_reasoning_item = True
                                            if think_text:
                                                yield sse_event("response.reasoning_summary_text.delta",
                                                                ***SECRET***(reasoning_item_id, 0, think_text))
                                                reasoning_text += think_text
                                            content_buf = content_buf[idx + len(THINK_CLOSE):]
                                            in_think = False
                                        else:
                                            # 还在 think 块内：保留最后 7 字符防跨 chunk
                                            safe_len = max(0, len(content_buf) - len(THINK_CLOSE) + 1)
                                            safe_text = content_buf[:safe_len]
                                            if safe_text:
                                                if not has_reasoning_item:
                                                    yield sse_event("response.output_item.added",
                                                                    ***SECRET***(reasoning_item_id))
                                                    has_reasoning_item = True
                                                yield sse_event("response.reasoning_summary_text.delta",
                                                                ***SECRET***(reasoning_item_id, 0, safe_text))
                                                reasoning_text += safe_text
                                            content_buf = content_buf[safe_len:]
                                            break

                            # 3) 处理 tool_calls (OpenAI chat/completions 流式分块)
                            for tc in tc_delta:
                                idx = tc.get("index", 0)
                                if idx not in tool_calls:
                                    tool_calls[idx] = {
                                        "id": "",
                                        "name": "",
                                        "arguments": "",
                                        "item_id": f"fc_{uuid.uuid4().hex[:12]}",
                                        "added": False,
                                    }
                                tc_entry = tool_calls[idx]
                                if tc.get("id"):
                                    tc_entry["id"] = tc["id"]
                                func = tc.get("function") or {}
                                if func.get("name"):
                                    tc_entry["name"] = func["name"]
                                # arguments 可能是分块增量
                                if "arguments" in func:
                                    args_chunk = func["arguments"] or ""
                                    # 首次有数据时发 item.added（需要 id 和 name 都已经拿到）
                                    if not tc_entry["added"] and tc_entry["id"] and tc_entry["name"]:
                                        yield sse_event("response.output_item.added",
                                                        build_sse_function_call_added(
                                                            tc_entry["item_id"], tc_entry["id"], tc_entry["name"]))
                                        tc_entry["added"] = True
                                    if args_chunk and tc_entry["added"]:
                                        tc_entry["arguments"] += args_chunk
                                        yield sse_event("response.function_call_arguments.delta",
                                                        ***SECRET***(
                                                            tc_entry["item_id"], args_chunk))

                # ── 收尾：关闭所有 item 并发 response.completed ──

                # 0) 处理 content_buf 残留（think 块未关闭 + 流结束的情况）
                if content_buf:
                    if in_think:
                        # 残留的是 think 内容 → 归入 reasoning
                        if not has_reasoning_item:
                            yield sse_event("response.output_item.added",
                                            ***SECRET***(reasoning_item_id))
                            has_reasoning_item = True
                        yield sse_event("response.reasoning_summary_text.delta",
                                        ***SECRET***(reasoning_item_id, 0, content_buf))
                        reasoning_text += content_buf
                    else:
                        # 残留的是正文 → 归入 content
                        if not has_content_item:
                            yield sse_event("response.output_item.added",
                                            build_sse_output_item_added(content_item_id))
                            has_content_item = True
                        full_text += content_buf
                        yield sse_event("response.output_text.delta",
                                        build_sse_output_text_delta(content_buf, content_item_id))

                # 1) 关闭 reasoning item
                if has_reasoning_item:
                    yield sse_event("response.output_item.done",
                                    build_sse_reasoning_item_done(reasoning_item_id, reasoning_text))

                # 2) 关闭 content item
                if has_content_item:
                    yield sse_event("response.output_item.done",
                                    build_sse_output_item_done(content_item_id, full_text))

                # 3) 关闭所有 tool_call items（按 index 顺序）
                for idx in sorted(tool_calls.keys()):
                    tc_entry = tool_calls[idx]
                    if not tc_entry["added"]:
                        # 收到了 tool_call 但从未发送过 delta（arguments 为空或 id/name 缺失）
                        # 仍要关闭以维持事件完整性
                        if tc_entry["id"] and tc_entry["name"]:
                            yield sse_event("response.output_item.added",
                                            build_sse_function_call_added(
                                                tc_entry["item_id"], tc_entry["id"], tc_entry["name"]))
                            tc_entry["added"] = True
                    if tc_entry["added"]:
                        yield sse_event("response.function_call_arguments.done",
                                        ***SECRET***(
                                            tc_entry["item_id"], tc_entry["arguments"]))
                        yield sse_event("response.output_item.done",
                                        build_sse_function_call_done(
                                            tc_entry["item_id"], tc_entry["id"], tc_entry["name"], tc_entry["arguments"]))

                # 4) 兜底：完全没收到 reasoning/content/tool_calls
                #    某些 backend 可能不发任何 delta，但有 reasoning_text 兜底逻辑
                if not has_reasoning_item and not has_content_item and not tool_calls and reasoning_text:
                    yield sse_event("response.output_item.added",
                                    build_sse_output_item_added(content_item_id))
                    full_text = reasoning_text
                    yield sse_event("response.output_text.delta",
                                    build_sse_output_text_delta(reasoning_text, content_item_id))
                    yield sse_event("response.output_item.done",
                                    build_sse_output_item_done(content_item_id, full_text))

                # 5) 发 response.completed（finish_reason 写入 response.status 提示 Codex）
                yield sse_event("response.completed",
                                build_sse_response_completed(response_id, model_name, full_text, usage))

                log(f"SSE← done (content={len(full_text)} chars, reasoning={len(reasoning_text)} chars, tool_calls={len(tool_calls)}, finish={finish_reason})")

    except asyncio.TimeoutError:
        log("SSE← TIMEOUT", "WARN")
        if stream_started:
            # 超时：尽量关闭已开的 item
            if has_reasoning_item:
                yield sse_event("response.output_item.done",
                                build_sse_reasoning_item_done(reasoning_item_id, reasoning_text))
            if has_content_item:
                yield sse_event("response.output_item.done",
                                build_sse_output_item_done(content_item_id, full_text))
            for idx in sorted(tool_calls.keys()):
                tc_entry = tool_calls[idx]
                if tc_entry["added"]:
                    yield sse_event("response.output_item.done",
                                    build_sse_function_call_done(
                                        tc_entry["item_id"], tc_entry["id"], tc_entry["name"], tc_entry["arguments"]))
            yield sse_event("response.completed",
                            build_sse_response_completed(response_id, model_name, full_text, usage))
    except Exception as e:
        log(f"SSE← ERROR: {e}", "WARN")
        if stream_started:
            yield sse_event("response.completed",
                            build_sse_response_completed(response_id, model_name, full_text, usage))
        else:
            yield json.dumps({"type": "error", "error": {"message": str(e)}}).encode()
    finally:
        # 清理 feeder task（所有退出路径都执行）
        try:
            feeder
            if not feeder.done():
                feeder.cancel()
        except (NameError, UnboundLocalError):
            pass
        try:
            await feeder
        except (asyncio.CancelledError, Exception):
            pass


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

    # ── 修正火山引擎路径：火山 API 路径不含 /v1 前缀 ──
    #    例: /api/plan/v3 + /v1/chat/completions → 404
    #    正: /api/plan/v3 +  /chat/completions   → 200
    if "volces.com" in backend.get("url", "") and rest.startswith("/v1"):
        rest = rest[3:]  # /v1/chat/completions → /chat/completions

    # ── 修正 Responses API 路径（火山引擎不需要 /v1 前缀） ──
    if is_responses and "volces.com" in backend["url"]:
        rest = "/chat/completions"

    body = await request.read() if request.method in ("POST", "PUT", "PATCH") else None
    headers = dict(request.headers)

    # ── 智能路由：模型池自动选模型（替代硬编码 primary/fallback）──
    if route == "/openai" and _MODEL_POOL_LOADED and body:
        try:
            body_json = json.loads(body)
            messages = body_json.get("messages", [])
            if messages:
                selected_mid, reason, warning = select_model(
                    messages, route=route,
                    backends_exists=lambda mid: mid in BACKENDS,
                    quota_tracker=_quota_tracker,
                )
                new_backend = BACKENDS.get(selected_mid)
                if new_backend and new_backend != backend:
                    log(f"SMART-ROUTE: {which} → {selected_mid} ({reason})")
                    backend = new_backend
                    which = selected_mid
                if warning:
                    log(f"SMART-ROUTE-WARN: {warning}", "WARN")
        except Exception as e:
            log(f"SMART-ROUTE error: {e}", "WARN")

    # ── 所有 POST/PUT/PATCH 请求：统一改写模型名（Codex 内部模型名 → 后端模型名） ──
    if body and not is_responses:
        try:
            body_json = json.loads(body)
            body_json = normalize_model_name(body_json, backend)
            body = json.dumps(body_json).encode()
        except Exception as e:
            log(f"model normalize error: {e}", "WARN")

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

        # Codex 客户端可能在 turn.completed 之前主动断开（如已收齐内容）
        # 写 EOF 时吞掉 ClientConnectionResetError，避免污染 stderr
        try:
            await resp.write_eof()
        except (ConnectionResetError, ClientConnectionError):
            log("SSE client disconnected before EOF (Codex 提前关闭，正常)", "INFO")
        return resp

    # ─── 非流式：原有逻辑 ───
    async with aiohttp.ClientSession() as session:
        status_code, resp_body, resp_headers = await forward(
            session, backend, rest, request.method, headers, body)

    # ─── 智能 Fallback：失败模型置黑 → 池子里重选下一个 ───
    if status_code in (429, 402, 500, 502, 503, 504):
        retry_backend = None
        retry_which = None

        if _MODEL_POOL_LOADED and _quota_tracker and which != "fallback":
            # 阻塞失败模型
            _quota_tracker.block_model(which, f"HTTP {status_code}")
            log(f"SMART-FB: blocked {which} ({backend['name']}) — HTTP {status_code}")

            # 从模型池重选
            try:
                body_json = json.loads(body)
                messages = body_json.get("messages", [])
            except Exception:
                messages = []
            selected_mid, reason, warning = select_model(
                messages, route=route,
                backends_exists=lambda mid: mid in BACKENDS,
                quota_tracker=_quota_tracker,
            )
            retry_backend = BACKENDS.get(selected_mid)
            retry_which = selected_mid
            if retry_backend and retry_backend != backend:
                log(f"SMART-FB: → {selected_mid} ({retry_backend['name']}) — {reason}")
                await notify_fallback(route, backend["name"], retry_backend["name"], status_code)
            else:
                log(f"SMART-FB: no alternative, using ds-openai", "WARN")
                retry_backend = BACKENDS.get("ds-openai")
                retry_which = "ds-openai"

        # 旧逻辑兼容：无模型池时用固定 fallback
        elif status_code in (429, 402, 500, 502, 503, 504) and which == "primary":
            fb = BACKENDS.get(cfg["fallback"])
            if fb:
                log(f"FALLBACK: {route} {backend['name']} → {fb['name']} (HTTP {status_code})")
                rs["active"] = "fallback"
                rs["since"] = time.time()
                rs["failures"] += 1
                state["stats"]["fallbacks"] += 1
                save_state()
                await notify_fallback(route, backend["name"], fb["name"], status_code)
                retry_backend = fb
                retry_which = "fallback"

        # 执行重试
        if retry_backend and retry_backend != backend:
            async with aiohttp.ClientSession() as session:
                status_code, resp_body, resp_headers = await forward(
                    session, retry_backend, rest, request.method, headers, body)
            which = retry_which
            backend = retry_backend

    # ─── 记录 token 消耗（估算）──
    if _MODEL_POOL_LOADED and _quota_tracker and status_code == 200:
        try:
            est_tokens = len(resp_body or b"") // 3  # 粗略估算：~3 bytes/token
            _quota_tracker.record_usage(which, max(est_tokens, 1))
        except Exception:
            pass

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
                    ping_model = get_ping_model(backend)
                    if not ping_model:
                        # 火山等需要特定端点 ID 的 backend，跳过自动恢复
                        continue
                    try:
                        ping_url = backend["url"] + "/v1/chat/completions"
                        auth_val = backend.get("prefix", "") + backend["key"]
                        hdrs = {"Content-Type": "application/json", backend["auth"]: auth_val}
                        body = json.dumps({"model": ping_model, "max_tokens": 1,
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
