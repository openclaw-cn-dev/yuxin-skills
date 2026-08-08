#!/usr/bin/env python3
"""
Multi-Model Intelligent Router for Hermes Agent
================================================
配额感知 + 任务类型路由 + 自动 fallback

用法:
  python3 multi_model_router.py list              # 列出所有 provider
  python3 multi_model_router.py health            # 健康检查所有 provider
  python3 multi_model_router.py route text "hello" # 测试文本路由
  python3 multi_model_router.py route vision       # 测试视觉路由
  python3 multi_model_router.py reset <provider>   # 重置配额
  python3 multi_model_router.py stats              # 配额统计

设计原则:
  - 免费优先，付费兜底
  - 能力匹配（视觉请求不走纯文本模型）
  - 配额追踪持久化，重启不丢失
  - 单 provider 故障不影响整体
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path
from typing import Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
REGISTRY_PATH = HERMES_HOME / "state" / "provider_registry.json"
QUOTA_PATH = HERMES_HOME / "state" / "model_quotas.json"
LOG_PATH = HERMES_HOME / "logs" / "model_router.log"


# ─── Quota Manager ────────────────────────────────────────────────


class QuotaManager:
    """追踪每个 provider 的日/月配额消耗"""

    def __init__(self, path: Path = QUOTA_PATH):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return {"daily": {}, "monthly": {}, "last_reset_day": str(date.today())}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def _check_reset(self):
        """按天/月重置计数器"""
        today = str(date.today())
        if self.data.get("last_reset_day") != today:
            self.data["daily"] = {}
            self.data["last_reset_day"] = today
        # 月初重置
        if date.today().day == 1 and self.data.get("last_reset_month") != today[:7]:
            self.data["monthly"] = {}
            self.data["last_reset_month"] = today[:7]
            self._save()

    def record(self, provider_name: str, count: int = 1):
        """记录一次使用"""
        self._check_reset()
        d = self.data["daily"]
        d[provider_name] = d.get(provider_name, 0) + count
        m = self.data["monthly"]
        m[provider_name] = m.get(provider_name, 0) + count
        self._save()

    def daily_used(self, provider_name: str) -> int:
        self._check_reset()
        return self.data["daily"].get(provider_name, 0)

    def monthly_used(self, provider_name: str) -> int:
        self._check_reset()
        return self.data["monthly"].get(provider_name, 0)

    def is_exhausted(self, provider_name: str, daily_limit=None, monthly_limit=None) -> bool:
        """检查是否配额耗尽"""
        self._check_reset()
        if daily_limit and self.daily_used(provider_name) >= daily_limit:
            return True
        if monthly_limit and self.monthly_used(provider_name) >= monthly_limit:
            return True
        return False

    def reset(self, provider_name: str):
        """手动重置某 provider 配额"""
        self.data["daily"].pop(provider_name, None)
        self.data["monthly"].pop(provider_name, None)
        self._save()
        _log(f"配额已重置: {provider_name}")

    def summary(self) -> str:
        self._check_reset()
        lines = ["日配额消耗:"]
        for name, used in sorted(self.data["daily"].items()):
            lines.append(f"  {name}: {used}")
        if self.data["monthly"]:
            lines.append("月配额消耗:")
            for name, used in sorted(self.data["monthly"].items()):
                lines.append(f"  {name}: {used}")
        return "\n".join(lines)


# ─── Provider Registry ────────────────────────────────────────────


def load_registry() -> dict:
    """加载 provider 注册表"""
    if not REGISTRY_PATH.exists():
        _log(f"注册表不存在: {REGISTRY_PATH}", "ERROR")
        return {"providers": [], "task_routing": {}, "rotation_policy": {}}
    return json.loads(REGISTRY_PATH.read_text())


def get_api_key(env_var: str) -> Optional[str]:
    """从环境变量获取 API key"""
    # 尝试当前进程环境
    key = os.environ.get(env_var)
    if key:
        return key
    # 尝试从 .env 文件读取
    env_file = HERMES_HOME / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{env_var}="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and val != "YOUR_KEY_HERE":
                    return val
    return None


def check_health(provider: dict, timeout: int = 10) -> tuple[bool, str]:
    """检查 provider 连通性"""
    name = provider["name"]
    base_url = provider.get("base_url", "")
    api_key_env = provider.get("api_key_env", "")
    model = provider.get("model", "")

    key = get_api_key(api_key_env)
    if not key:
        return False, f"API key 未设置 ({api_key_env})"

    url = f"{base_url.rstrip('/')}/chat/completions"
    body = json.dumps({
        "model": model,
        "max_tokens": 5,
        "messages": [{"role": "user", "content": "hi"}]
    }).encode()

    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    })

    try:
        urllib.request.urlopen(req, timeout=timeout)
        return True, "OK"
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, str(e)[:100]


# ─── Intelligent Router ───────────────────────────────────────────


class ModelRouter:
    """多模型智能路由器"""

    def __init__(self):
        self.registry = load_registry()
        self.quota = QuotaManager()
        self.providers = self.registry.get("providers", [])
        self.routing = self.registry.get("task_routing", {})
        self.policy = self.registry.get("rotation_policy", {})

    def _get_sorted_providers(self, task_type: str) -> list:
        """按优先级返回匹配 task_type 的 provider 列表"""
        routing_cfg = self.routing.get(task_type, {})
        required = routing_cfg.get("required_capabilities", ["text"])
        prefer_free = routing_cfg.get("prefer_free", True)
        allow_paid = routing_cfg.get("allow_paid", False)

        candidates = []
        for p in self.providers:
            caps = p.get("capabilities", [])
            # 检查能力匹配
            if not all(c in caps for c in required):
                continue
            # 检查付费限制
            if p.get("cost_tier") == "paid" and not allow_paid:
                continue
            # 检查 API key
            if not get_api_key(p.get("api_key_env", "")):
                continue
            # 检查配额
            if self.quota.is_exhausted(
                p["name"],
                daily_limit=p.get("daily_limit"),
                monthly_limit=p.get("monthly_limit")
            ):
                continue

            candidates.append(p)

        # 排序：免费优先 + 优先级数字小优先
        def sort_key(p):
            cost_order = 0 if p.get("cost_tier") == "free" else 100
            return (1 if self.quota.daily_used(p["name"]) > 0 else 0,
                    cost_order,
                    p.get("priority", 99))

        candidates.sort(key=sort_key)
        return candidates

    def route(self, task_type: str, messages: list = None, **kwargs) -> dict:
        """
        路由请求到最佳 provider。
        返回: {"provider": "...", "model": "...", "base_url": "...", "api_key": "...", "headers": {...}}
        失败: {"error": "..."}
        """
        candidates = self._get_sorted_providers(task_type)

        if not candidates:
            return {"error": f"No available provider for task_type='{task_type}'"}

        # 尝试每个候选，直到成功
        last_error = None
        for p in candidates:
            name = p["name"]
            health_ok, health_msg = check_health(p, timeout=5)
            if health_ok:
                key = get_api_key(p["api_key_env"])
                self.quota.record(name)
                full_url = f"{p['base_url'].rstrip('/')}/chat/completions"
                return {
                    "provider": name,
                    "model": p["model"],
                    "base_url": full_url,
                    "api_key_env": p.get("api_key_env", ""),
                    "api_key": key,
                    "headers": {
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    "cost_tier": p.get("cost_tier", "unknown"),
                    "capabilities": p.get("capabilities", [])
                }
            else:
                last_error = f"{name}: {health_msg}"
                _log(f"跳过 {name}: {health_msg}")
                continue

        return {"error": f"All providers failed. Last: {last_error}"}

    def list_providers(self) -> str:
        """列出所有 provider 状态"""
        lines = []
        for p in self.providers:
            name = p["name"]
            has_key = bool(get_api_key(p.get("api_key_env", "")))
            daily = self.quota.daily_used(name)
            dl = p.get("daily_limit")
            exhausted = self.quota.is_exhausted(name, daily_limit=dl)
            status = "🔴 配额耗尽" if exhausted else ("🟢 就绪" if has_key else "⚫ 无 Key")
            limit_str = f"{daily}/{dl}" if dl else f"{daily}/∞"
            lines.append(
                f"  {status}  {name:30s} | {p.get('model','?'):30s} | "
                f"{p.get('cost_tier','?'):6s} | 日配额:{limit_str:12s} | "
                f"{','.join(p.get('capabilities',[]))}"
            )
        return "\n".join(lines)

    def health_all(self) -> str:
        """健康检查所有 provider"""
        lines = []
        for p in self.providers:
            name = p["name"]
            has_key = bool(get_api_key(p.get("api_key_env", "")))
            if not has_key:
                lines.append(f"  ⚫ {name}: 无 API Key")
                continue
            ok, msg = check_health(p)
            icon = "🟢" if ok else "🔴"
            lines.append(f"  {icon} {name}: {msg}")
        return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────


def _log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line, file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    router = ModelRouter()

    if cmd == "list":
        print("=== 多模型 Provider 状态 ===\n")
        print(router.list_providers())
        print(f"\n{router.quota.summary()}")

    elif cmd == "health":
        print("=== 健康检查 ===\n")
        print(router.health_all())

    elif cmd == "route":
        if len(sys.argv) < 3:
            print("用法: route <task_type> [message]")
            sys.exit(1)
        task_type = sys.argv[2]
        msg = sys.argv[3] if len(sys.argv) > 3 else "test"
        result = router.route(task_type, messages=[{"role": "user", "content": msg}])
        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)
        else:
            print(f"✅ 路由到: {result['provider']} ({result['model']})")
            print(f"   费用: {result['cost_tier']}")
            print(f"   能力: {','.join(result['capabilities'])}")

    elif cmd == "reset":
        if len(sys.argv) < 3:
            print("用法: reset <provider_name>")
            sys.exit(1)
        provider_name = sys.argv[2]
        router.quota.reset(provider_name)

    elif cmd == "stats":
        print(router.quota.summary())

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
