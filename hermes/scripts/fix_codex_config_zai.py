#!/usr/bin/env python3
"""修复 CC Switch 改坏的 Codex config.toml：恢复 model_provider=ZAI + 补回 ZAI 段.
key 从 8/28 良好备份程序化提取，避免手抄出错。"""
import re
import shutil
import time

CONFIG = "/Users/hua/系统文件夹/Codex/config.toml"
GOOD_BAK = "/Users/hua/系统文件夹/Codex/config.toml.bak.20260828-140420"

# 1. 备份当前损坏现场
ts = time.strftime("%Y%m%d-%H%M%S")
broken_bak = f"{CONFIG}.bak.ccswitch-broken-{ts}"
shutil.copy2(CONFIG, broken_bak)
print(f"损坏现场已备份: {broken_bak}")

c = open(CONFIG).read()

# 2. model_provider 恢复为 ZAI
if 'model_provider = "custom"' in c:
    c = c.replace('model_provider = "custom"', 'model_provider = "ZAI"', 1)
    print("model_provider: custom -> ZAI")
elif 'model_provider = "ZAI"' in c:
    print("model_provider 已是 ZAI")
else:
    raise SystemExit("未知的 model_provider 值，中止")

# 3. 从良好备份提取 ZAI 段
good = open(GOOD_BAK).read()
m = re.search(r'\[model_providers\.ZAI\][^\[]*', good)
if not m:
    raise SystemExit("良好备份里没找到 ZAI 段，中止")
zai_block = m.group(0).rstrip() + "\n"

# 4. 校验提取的 key 非代理占位
if "PROXY_MANAGED" in zai_block:
    raise SystemExit("提取到 PROXY_MANAGED，提取逻辑出错，中止")
key_prefix = re.search(r'"(.{6})', re.search(r'experimental_bearer_token = "([^"]*)"', zai_block).group(0)).group(1)

# 5. 若 ZAI 段不存在则补回（插在 custom 段之后）
if "[model_providers.ZAI]" in c:
    print("ZAI 段已存在，跳过插入")
else:
    anchor = 'experimental_bearer_token = "PROXY_MANAGED"\n'
    if anchor not in c:
        raise SystemExit("找不到 custom 段锚点，中止")
    c = c.replace(anchor, anchor + "\n" + zai_block, 1)
    print("已补回 [model_providers.ZAI] 段")

open(CONFIG, "w").write(c)

# 6. 校验
import tomllib
with open(CONFIG, "rb") as f:
    d = tomllib.load(f)
assert d["model_provider"] == "ZAI", "model_provider 不对"
assert "ZAI" in d.get("model_providers", {}), "ZAI 段缺失"
assert d["model"] == "glm-5.3", f"model={d['model']} 不对"
print("TOML 解析 OK | provider:", d["model_provider"], "| model:", d["model"])
print("ZAI key 前缀:", key_prefix, "| base_url:", d["model_providers"]["ZAI"]["base_url"])
