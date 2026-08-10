#!/usr/bin/env python3
"""午夜切换6个同事agent到MiniMax套餐（sk-cp-订阅key）"""
import yaml, os, subprocess, sys, json, urllib.request

HERMES_HOME = '/Users/hua/.hermes'
PROFILES = ['maodou', 'laomo', 'xiaobao', 'heidou', 'afu', 'zhenglishi']

# 1. 测试 MiniMax 额度
print('=== 1. 测试 MiniMax 额度 ===')
key = ''
with open(f'{HERMES_HOME}/.env') as f:
    for line in f:
        if line.startswith('MINIMAX_API_KEY=') and not line.startswith('#'):
            key = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
            break

url = 'https://api.minimaxi.com/anthropic/v1/messages'
data = json.dumps({
    'model': 'MiniMax-M3',
    'max_tokens': 10,
    'messages': [{'role': 'user', 'content': 'hi'}]
}).encode()
req = urllib.request.Request(url, data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {key}',
})
try:
    resp = urllib.request.urlopen(req, timeout=20)
    result = json.loads(resp.read())
    if 'error' in result:
        print(f'  额度测试失败: {result["error"]}')
        print('  ⚠️ 仍然切换，但可能失败')
    else:
        print(f'  ✅ 额度正常')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'  测试失败: HTTP {e.code} - {body[:200]}')
    if '2056' in body or '用量上限' in body:
        print('  ❌ 额度仍未恢复，取消切换')
        sys.exit(1)

# 2. 更新 root config 的 minimax provider
print('\n=== 2. 更新 minimax provider ===')
root_cfg_path = f'{HERMES_HOME}/config.yaml'
with open(root_cfg_path) as f:
    cfg = yaml.safe_load(f)

providers = cfg.get('providers', {})
# 确保 minimax-cn provider 配置正确
providers['minimax-cn'] = {
    'base_url': 'https://api.minimaxi.com/anthropic',
    'model': 'MiniMax-M3',
    'api_key_env': 'MINIMAX_API_KEY',
}
cfg['providers'] = providers

with open(root_cfg_path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print('  ✅ root config updated')

# 3. 切换每个 profile
print('\n=== 3. 切换 6 个同事 ===')
for prof in PROFILES:
    cfg_path = f'{HERMES_HOME}/profiles/{prof}/config.yaml'
    with open(cfg_path) as f:
        pcfg = yaml.safe_load(f)
    
    old_model = pcfg.get('model', '?')
    old_provider = pcfg.get('provider', '?')
    pcfg['model'] = 'MiniMax-M3'
    pcfg['provider'] = 'minimax-cn'
    
    with open(cfg_path, 'w') as f:
        yaml.dump(pcfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f'  ✅ {prof}: {old_provider}/{old_model} → minimax-cn/MiniMax-M3')

# 4. 重启 gateway
print('\n=== 4. 重启 gateway ===')
uid = os.getuid()
for prof in PROFILES:
    plist = f'ai.hermes.gateway-{prof}'
    subprocess.run(['launchctl', 'kickstart', '-k', f'gui/{uid}/{plist}'], 
                   capture_output=True)
    print(f'  🔄 {prof} 已重启')

print('\n✅ 全部切换完成！')
