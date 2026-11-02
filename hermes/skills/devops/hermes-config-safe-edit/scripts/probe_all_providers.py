#!/usr/bin/env python3
"""探测 Hermes config.yaml 里所有 LLM provider 的存活状态（HTTP 200 / 429 等）。

用途：GLM/minimax/deepseek 任一 provider 报 429 时，一键扫全量 provider，
    找出哪条通道还活着，先切活的那条保命。

为什么写文件而不是 inline：Hermes 对 terminal 命令输入做 secret 脱敏，
    inline 写 key 字面量会被改成 `***`。本脚本从 config.yaml 程序化读 key，
    绝不把 key 硬编码进源码。只输出 HTTP 状态 + 截断的错误 body，不打印 key。

用法：python3 /tmp/probe_all_providers.py
"""
import yaml, json, urllib.request, urllib.error, os

CFG = os.path.expanduser('~/.hermes/config.yaml')
ENV = os.path.expanduser('~/.hermes/.env')


def _load_env():
    env = {}
    if os.path.exists(ENV):
        for line in open(ENV):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def _openai(base_url, key, model, label):
    """OpenAI chat/completions 协议"""
    url = base_url.rstrip('/') + '/chat/completions'
    body = json.dumps({'model': model, 'max_tokens': 5,
                       'messages': [{'role': 'user', 'content': 'hi'}]}).encode()
    req = urllib.request.Request(url, data=body,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return f'[{label}] HTTP {r.status} OK'
    except urllib.error.HTTPError as e:
        return f'[{label}] HTTP {e.code} -> {e.read().decode("utf-8", "replace")[:160]}'
    except Exception as e:
        return f'[{label}] ERR {e}'


def _anthropic(base_url, key, model, label):
    """Anthropic messages 协议（x-api-key）"""
    url = base_url.rstrip('/') + '/v1/messages'
    body = json.dumps({'model': model, 'max_tokens': 5,
                       'messages': [{'role': 'user', 'content': 'hi'}]}).encode()
    req = urllib.request.Request(url, data=body,
        headers={'x-api-key': key, 'anthropic-version': '2023-06-01',
                 'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return f'[{label}] HTTP {r.status} OK'
    except urllib.error.HTTPError as e:
        return f'[{label}] HTTP {e.code} -> {e.read().decode("utf-8", "replace")[:160]}'
    except Exception as e:
        return f'[{label}] ERR {e}'


def main():
    cfg = yaml.safe_load(open(CFG))
    env = _load_env()

    # custom_providers（chat_completions 或 anthropic_messages）
    for p in cfg.get('custom_providers') or []:
        name = p.get('name', '?')
        key = p.get('api_key', '')
        if not key:
            continue
        mode = p.get('api_mode', 'chat_completions')
        model = p.get('model', '?')
        base = p.get('base_url', '')
        if mode == 'anthropic_messages':
            print(_anthropic(base, key, model, f'custom:{name}'))
        else:
            print(_openai(base, key, model, f'custom:{name}'))

    # providers（api_key 直填 或 api_key_env）
    for name, p in (cfg.get('providers') or {}).items():
        if not isinstance(p, dict):
            continue
        key = p.get('api_key', '')
        if not key:
            key = env.get(p.get('api_key_env', ''), '')
        if not key:
            continue
        base = p.get('base_url', '')
        model = p.get('model', '?')
        print(_openai(base, key, model, f'providers.{name}'))


if __name__ == '__main__':
    main()
