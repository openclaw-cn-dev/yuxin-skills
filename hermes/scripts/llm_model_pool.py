#!/usr/bin/env python3
"""
渔芯 LLM Model Pool — 多模型智能调度框架
──────────────────────────────────────────
功能:
  1. 模型注册表（能力 + 免费额度 + API 端点）
  2. 额度追踪（tokens 用量 + 自动置黑/恢复）
  3. 智能路由（按请求类型 + 可用性 + 成本选模型）
  4. 请求类型检测（纯文本 / 含图片 / 含音频）

集成方式: Gateway import select_model() 替代硬编码路由
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta


# ─── 配置路径 ──────────────────────────────────────────────────

HERMES_HOME = Path.home() / ".hermes"
QUOTA_FILE = HERMES_HOME / "scripts" / ".model_quota_state.json"
QUOTA_RESET_DAYS = 30  # 免费额度按月重置


# ─── 模型注册表 ─────────────────────────────────────────────────
# 
# 每个模型定义：
#   name         显示名
#   endpoint     OpenAI 兼容的 base_url
#   api_key      从 env 读取的 key (在 Gateway 的 build_backends 里注入)
#   capabilities {text, vision, audio, function_calling}
#   free_quota   月免费 tokens 上限（None = 按量计费不限）
#   cost_tier    "free" | "token_plan" | "pay_as_you_go"
#   note         备注

MODEL_REGISTRY = {
    # ── 免费多模态模型（主力） ──
    "gemini-openai": {
        "name": "Google Gemini (免费)",
        "endpoint_key": "gemini",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": {"daily": 1_000_000, "rpm": 15},
        "cost_tier": "free",
        "purpose": "多模态主力，100万 tokens/天免费",
        "note": "需 Gemini API key，OpenAI 兼容模式",
    },

    # ── DeepSeek 按量计费（玉芬+学助专用，不进池） ──
    "ds-openai": {
        "name": "DeepSeek(按量)",
        "endpoint_key": "ds-openai",
        "capabilities": {"text": True, "vision": False, "audio": False, "function_calling": True},
        "free_quota": None,  # 不限量，按量计费
        "cost_tier": "pay_as_you_go",
        "purpose": "文本兜底 + 玉芬/学助专用",
    },

    # ── MiniMax Token Plan（套餐，文本+视觉+音频）──
    "minimax-anthropic": {
        "name": "MiniMax M3 (Anthropic, Token Plan)",
        "endpoint_key": "minimax-anthropic",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": None,  # Token Plan 套餐，非免费
        "cost_tier": "token_plan",
        "purpose": "/anthropic 路由主力（玉芬/学助/Codex）",
    },
    "minimax-openai": {
        "name": "MiniMax M3 (OpenAI, Token Plan)",
        "endpoint_key": "minimax-openai",
        "capabilities": {"text": True, "vision": True, "audio": True, "function_calling": True},
        "free_quota": None,  # Token Plan 套餐，非免费
        "cost_tier": "token_plan",
        "purpose": "/openai 路由主力（Codex/Hermes），含音频",
    },

    # ── 智谱 GLM-4V（免费 100万/月） ──
    "glm-openai": {
        "name": "智谱 GLM-4V (免费)",
        "endpoint_key": "glm",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": {"monthly": 1_000_000},
        "cost_tier": "free",
        "purpose": "国内多模态备用",
        "note": "需申请 API key: open.bigmodel.cn",
    },

    # ── 通义千问 Qwen-VL（免费 100万/月） ──
    "qwen-openai": {
        "name": "通义千问 Qwen-VL (免费)",
        "endpoint_key": "qwen",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": {"monthly": 1_000_000},
        "cost_tier": "free",
        "purpose": "国内多模态备用",
        "note": "需申请 API key: dashscope.aliyuncs.com",
    },

    # ── 火山豆包 Seed（免费 50万/月） ──
    "doubao-openai": {
        "name": "火山豆包 Seed (免费)",
        "endpoint_key": "doubao",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": {"monthly": 500_000},
        "cost_tier": "free",
        "purpose": "火山生态多模态",
        "note": "已有火山帐号 ARK_API_KEY",
    },

    # ── Groq LLaMA 3.2 Vision（高 RPM 免费） ──
    "groq-openai": {
        "name": "Groq LLaMA 3.2 (免费)",
        "endpoint_key": "groq",
        "capabilities": {"text": True, "vision": True, "audio": False, "function_calling": True},
        "free_quota": {"rpm": 30, "tpm": 30_000},
        "cost_tier": "free",
        "purpose": "开源模型加速，极高 RPM",
        "note": "需申请 API key: console.groq.com",
    },
}


# ─── 选择优先级 ─────────────────────────────────────────────────
# 
# 优先级规则:
#   1. 必须有对应能力（text/vision/audio）
#   2. cost_tier 优先: free > token_plan > pay_as_you_go
#   3. free 模型按剩余额度排序（余量大的优先）
#   4. 已耗尽(blocked)的跳过

def model_cost_rank(mid: str) -> int:
    """成本排序: free=0, token_plan=10, pay_as_you_go=100"""
    tier = MODEL_REGISTRY.get(mid, {}).get("cost_tier", "pay_as_you_go")
    return {"free": 0, "token_plan": 10, "pay_as_you_go": 100}[tier]


# ─── 请求类型检测 ───────────────────────────────────────────────

def detect_request_type(messages: list) -> dict:
    """
    分析 messages 数组，返回请求类型。
    
    Returns:
        {"has_image": bool, "has_audio": bool, "is_text_only": bool}
    """
    has_image = False
    has_audio = False
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict):
                    ctype = c.get("type", "")
                    if ctype == "image_url":
                        has_image = True
                    elif ctype in ("input_audio", "audio_url"):
                        has_audio = True
    return {
        "has_image": has_image,
        "has_audio": has_audio,
        "is_text_only": not has_image and not has_audio,
    }


# ─── Quota Tracker ──────────────────────────────────────────────

class QuotaTracker:
    """追踪每个模型的 tokens 用量，管理配额耗尽/恢复"""

    def __init__(self, persist_path: Path = QUOTA_FILE):
        self.path = persist_path
        self._data = self._load()
        self._token_estimates = {}  # mid -> (in_tokens, out_tokens)

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {"models": {}, "reset_day": datetime.now().day}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, default=str))

    def _check_monthly_reset(self):
        """月初自动重置免费额度"""
        today = datetime.now()
        if today.day != self._data.get("reset_day", today.day):
            # 新的一月，重置所有免费模型的累计用量
            for mid, info in self._data.get("models", {}).items():
                model = MODEL_REGISTRY.get(mid, {})
                quota = model.get("free_quota")
                if quota and "monthly" in quota:
                    info["tokens_used"] = 0
                    info["blocked"] = False
                    info["blocked_at"] = None
            self._data["reset_day"] = today.day
            self._save()

    def is_available(self, mid: str, backend_exists: bool) -> bool:
        """
        检查模型是否可用:
        1. 后端必须存在 (Gateway 的 BACKENDS 里)
        2. 未被 block (配额未耗尽)
        3. 免费模型检查月额度

        例外 (2026-08-21 B1): token_plan 类模型(MiniMax-M3)永不被 block，
        防止 SMART-ROUTE 错误降级到 pay_as_you_go (DeepSeek)。
        即便 gateway 抽风时收到 504 也不应被 block，SMART-ROUTE 应继续尝试。
        """
        if not backend_exists:
            return False

        if mid not in MODEL_REGISTRY:
            return False

        self._check_monthly_reset()
        model_info = self._data.get("models", {}).get(mid, {})

        # token_plan 类套餐模型免 block 保护
        model_def = MODEL_REGISTRY.get(mid, {})
        if model_def.get("cost_tier") == "token_plan":
            return True

        if model_info.get("blocked", False):
            return False

        return True

    def record_usage(self, mid: str, tokens_used: int):
        """记录 tokens 消耗"""
        if mid not in self._data.setdefault("models", {}):
            self._data["models"][mid] = {"tokens_used": 0, "blocked": False, "blocked_at": None}

        info = self._data["models"][mid]
        info["tokens_used"] = info.get("tokens_used", 0) + tokens_used

        # 检查是否超过免费额度
        model = MODEL_REGISTRY.get(mid, {})
        quota = model.get("free_quota")
        if quota:
            limit = quota.get("monthly", 0) or quota.get("daily", 0)
            if limit and info["tokens_used"] >= limit:
                info["blocked"] = True
                info["blocked_at"] = datetime.now().isoformat()
                # 估算: 1 次请求 ≈ 500 tokens out + 2000 tokens context in
                # 实际: Gateway 无法精确统计，用响应体长度估算

        self._save()

    def block_model(self, mid: str, reason: str = "manual"):
        """手动或错误触发置黑"""
        if mid not in self._data.setdefault("models", {}):
            self._data["models"][mid] = {}
        self._data["models"][mid]["blocked"] = True
        self._data["models"][mid]["blocked_at"] = datetime.now().isoformat()
        self._data["models"][mid]["block_reason"] = reason
        self._save()

    def unblock_model(self, mid: str):
        """解除置黑"""
        if mid in self._data.get("models", {}):
            self._data["models"][mid]["blocked"] = False
            self._data["models"][mid]["blocked_at"] = None
            self._data["models"][mid]["block_reason"] = None
        self._save()

    def status(self) -> dict:
        """返回所有模型的状态摘要"""
        result = {}
        for mid, model in MODEL_REGISTRY.items():
            info = self._data.get("models", {}).get(mid, {})
            quota = model.get("free_quota")
            limit = None
            if quota:
                limit = quota.get("monthly") or quota.get("daily")
            result[mid] = {
                "name": model["name"],
                "tier": model["cost_tier"],
                "capabilities": model["capabilities"],
                "used": info.get("tokens_used", 0),
                "limit": limit,
                "blocked": info.get("blocked", False),
                "available": not info.get("blocked", False),
            }
        return result


# ─── Smart Router ───────────────────────────────────────────────

def select_model(
    messages: list,
    route: str = "/openai",
    backends_exists: callable = None,
    quota_tracker: QuotaTracker = None,
) -> tuple:
    """
    智能选择最佳模型。
    
    Args:
        messages: 请求中的 messages 数组
        route: 路由前缀 (用于日志)
        backends_exists: 检查后端是否存在的方法
        quota_tracker: 额度追踪器实例
    
    Returns:
        (model_id, switch_reason, warning)
        model_id: BACKENDS 的 key (如 "minimax-openai")
        switch_reason: 为什么选这个模型
        warning: 如有降级，返回警告信息
    """
    req_type = detect_request_type(messages)
    needs_vision = req_type["has_image"]
    needs_audio = req_type["has_audio"]
    is_text_only = req_type["is_text_only"]

    # ── 收集候选模型 ──
    candidates = []
    for mid, model in MODEL_REGISTRY.items():
        # 能力匹配
        caps = model["capabilities"]
        if needs_vision and not caps.get("vision"):
            continue
        if needs_audio and not caps.get("audio"):
            continue
        if is_text_only and not caps.get("text"):
            continue

        # 后端是否存在
        if backends_exists and not backends_exists(mid):
            continue

        # 额度是否可用
        if quota_tracker and not quota_tracker.is_available(mid, True):
            continue

        # 成本排名
        rank = model_cost_rank(mid)
        candidates.append((rank, mid, model))

    if not candidates:
        # 所有模型都不可用，返回 DeepSeek 兜底
        return ("ds-openai", "all_exhausted",
                "所有免费/套餐模型已耗尽，降级到 DeepSeek 按量计费（纯文本，多模态已转为文本描述）")

    # 排序: 成本优先 → 同成本选第一个
    candidates.sort(key=lambda x: x[0])

    rank, best_mid, best_model = candidates[0]
    reason = f"auto_select: tier={best_model['cost_tier']}, text_only={is_text_only}"
    warning = None

    # 如果选了纯文本模型但请求含多模态 → 需要降级
    if needs_vision and not best_model["capabilities"]["vision"]:
        warning = "多模态请求降级到纯文本模型（图片将转为描述，质量下降）"
    if needs_audio and not best_model["capabilities"]["audio"]:
        if warning:
            warning += "；音频不可用"
        else:
            warning = "音频请求在纯文本模型上不可用"

    return (best_mid, reason, warning)


# ─── 单例 ───────────────────────────────────────────────────────

_quota_tracker = None

def get_quota_tracker() -> QuotaTracker:
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = QuotaTracker()
    return _quota_tracker


# ─── 快捷查询 ───────────────────────────────────────────────────

def list_all_models() -> str:
    """列出所有注册模型"""
    lines = ["## 模型池"]
    qt = get_quota_tracker()
    status = qt.status()
    for mid, info in status.items():
        caps = "✅文本" if info["capabilities"]["text"] else ""
        caps += " ✅视觉" if info["capabilities"]["vision"] else ""
        caps += " ✅音频" if info["capabilities"]["audio"] else ""
        blocked = "⚠️已耗尽" if info["blocked"] else ""
        used_str = f"已用{info['used']:,}" if info["used"] else "未使用"
        limit_str = f"/上限{info['limit']:,}" if info["limit"] else "/无上限"
        lines.append(f"- **{info['name']}** [{info['tier']}] {caps} {used_str}{limit_str} {blocked}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(list_all_models())
