#!/usr/bin/env python3
"""火山方舟模型可见性批量探测（2026-11-02 实测验证的判定逻辑）

用法: python3 ark_model_probe.py [API_KEY]
不传 key 则读环境变量 VOLC_ARK_API_KEY。
判定: ✅已可用 / ⚠️可见待开通(控制台点开通) / ❌不可见 / ↪️已开通但端点不对
改 CHAT_MODELS / EMBED_MODELS 清单即可复用到新模型。
"""
import json
import os
import sys
import urllib.request

key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('VOLC_ARK_API_KEY', '')
assert key, '缺少 API key（参数或 VOLC_ARK_API_KEY）'
BASE = 'https://ark.cn-beijing.volces.com/api/v3'

CHAT_MODELS = [
    'doubao-seed-2-1-pro-260628',
    'doubao-seed-2.0-mini',
    'doubao-seed-2.0-lite',
    'doubao-pro-32k',
]
EMBED_MODELS = [
    '***SECRET***',
    'doubao-embedding',
    'doubao-embedding-large',
    'doubao-embedding-text',
]


def post(endpoint, payload, timeout=20):
    req = urllib.request.Request(f'{BASE}/{endpoint}', method='POST', data=json.dumps(payload).encode())
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + key)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {'raw': f'HTTP {e.code}'}
    except Exception as e:
        return {'raw': str(e)[:80]}


def judge(r, ok):
    if ok:
        return '✅ 已可用'
    code = r.get('error', {}).get('code', '?')
    if code == 'ModelNotOpen':
        return '⚠️ 可见待开通(控制台点开通)'
    if 'NotFound' in str(code):
        return '❌ 不可见'
    if code == 'InvalidParameter':
        return '↪️ 已开通但端点不对'
    return f'❌ {code}'


print('=== chat 端点 ===')
for m in CHAT_MODELS:
    r = post('chat/completions', {'model': m, 'messages': [{'role': 'user', 'content': 'OK'}], 'max_tokens': 5})
    print(f'{judge(r, "choices" in r):28s} {m}')

print('=== embeddings 端点 ===')
for m in EMBED_MODELS:
    r = post('embeddings', {'model': m, 'input': '测试', 'dimensions': 1024})
    d = r.get('data')
    dim = len(d[0]['embedding']) if isinstance(d, list) and d else '-'
    print(f'{judge(r, bool(dim != "-")):28s} {m} (维度{dim})')

# vision 模型补测 multimodal 端点（普通 /embeddings 会报端点不对）
r = post('embeddings/multimodal', {
    'model': '***SECRET***',
    'input': [{'type': 'text', 'text': '测试'}],
    'dimensions': 1024,
})
d = r.get('data')
ok = isinstance(d, dict) and bool(d.get('embedding'))
dim = len(d['embedding']) if ok else '-'
print(f'{judge(r, ok):28s} ***SECRET*** @multimodal (维度{dim})')
