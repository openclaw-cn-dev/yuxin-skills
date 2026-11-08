"""probe_codex_expected_events.py — 反查 Codex native binary 支持的 SSE 事件清单。

用法: python3 probe_codex_expected_events.py

为什么需要:
Codex 是 compiled Rust binary, 源码不公开. 但所有 SSE 事件类型都是字符串字面量,
strings 命令可以提取. 当 LLM Gateway 想把上游 chat/completions 流翻译成 Codex 期望的
Responses API 事件时, 必须知道 Codex 监听哪些事件 — 否则会像 22:38 那次一样丢 tool_calls.

历史教训 (2026-07-29 22:38):
- llm_gateway.py 的 sse_stream_response 只翻译 delta.content 和 delta.reasoning_content
- 完全忽略 delta.tool_calls → Codex 在 MiniMax/DeepSeek/火山 上丧失所有工具能力
- 这次用 strings 提取了 Codex 完整事件清单才确认缺失的是 response.function_call 事件

未来加新事件类型时: 先跑这个脚本 → 看 Codex 是否期望该事件类型 → 翻译层对应处理.
"""
import subprocess, os, sys, re

BIN = os.path.expanduser(
    "~/.local/lib/node_modules/@openai/codex/"
    "node_modules/@openai/codex-darwin-arm64/"
    "vendor/aarch64-apple-darwin/bin/codex"
)


def extract_response_events():
    """提取所有 response.* 事件名"""
    if not os.path.exists(BIN):
        print(f"ERROR: Codex binary not found at {BIN}", file=sys.stderr)
        print("Hint: 重新安装 codex CLI 或调整 BIN 路径", file=sys.stderr)
        sys.exit(1)

    out = subprocess.run(["strings", BIN], capture_output=True, text=True).stdout
    events = set()
    pattern = re.compile(r'\bresponse\.[a-z][a-z0-9_.]*\b')
    for line in out.splitlines():
        for token in line.split():
            for match in pattern.findall(token):
                events.add(match)
    return sorted(events)


def extract_struct_names():
    """提取 Codex 内部事件 struct 名 (Rust enum)"""
    out = subprocess.run(["strings", BIN], capture_output=True, text=True).stdout
    structs = set()
    for line in out.splitlines():
        for token in line.split():
            if any(token.startswith(p) for p in ("Reasoning", "Function", "ToolCall", "AgentReasoning")):
                if "Event" in token or "Section" in token or "Break" in token:
                    structs.add(token)
    return sorted(structs)


def extract_config_keys():
    """提取 Codex 配置项名 (涉及 reasoning 显示等)"""
    out = subprocess.run(["strings", BIN], capture_output=True, text=True).stdout
    keys = set()
    candidates = (
        "hide_agent_reasoning",
        "show_raw_agent_reasoning",
        "model_reasoning_effort",
        "model_reasoning_summary",
        "wire_api",
        "experimental_bearer_token",
    )
    for c in candidates:
        if c in out:
            keys.add(c)
    return sorted(keys)


def main():
    print("=" * 60)
    print(f"Codex binary: {BIN}")
    print(f"Size: {os.path.getsize(BIN):,} bytes")
    print("=" * 60)

    print("\n[events] SSE 事件类型 (response.*):")
    events = extract_response_events()
    if not events:
        print("  (none found)")
    for e in events:
        marker = ""
        gateway_translated = {
            "response.created",
            "response.output_item.done",
            "response.completed",
            "response.output_text.delta",
        }
        gateway_dropped = {
            "response.reasoning",
            "response.function_call",
            "response.function_call_output",
            "response.local_shell_call",
            "response.web_search_call",
        }
        if e in gateway_translated:
            marker = " [OK translated]"
        elif e in gateway_dropped:
            marker = " [X Gateway drops]"
        print(f"  - {e}{marker}")

    print("\n[structs] Codex internal event structs (Rust enum):")
    structs = extract_struct_names()
    if not structs:
        print("  (none found)")
    for s in structs[:30]:
        print(f"  - {s}")

    print("\n[config] Relevant config keys:")
    keys = extract_config_keys()
    if not keys:
        print("  (none found)")
    for k in keys:
        print(f"  - {k}")

    print("\n" + "=" * 60)
    print("Usage: When extending llm_gateway.py SSE translator, run this")
    print("       to confirm Codex expects that event type")
    print("=" * 60)


if __name__ == "__main__":
    main()