#!/usr/bin/env python3
"""***SECRET***.py — 三向交叉验证决策树(心跳 #N+82 落地)
====================================================================
替代 SKILL.md §0.5 案 B 内联探测的"漂移≥3 → 直探 importlib.metadata"。

输出:对每个包给出 direct / script / skill 三方版本 + decision
- 三方一致 → ✅ 三方一致
- 直探=新版本, 双源=旧版本 → "B 真实升级(BASELINE stale)" → patch 双源
- 三方全不一致 → "⚠️ 三方全不一致, 需人工判定"

约束(cron mode, pitfall-N+80):必须用 terminal + python3 /tmp/xxx.py 跑,
不要在心跳内调用 execute_code(被 Hermes 拦截)。
"""
import sys, os, re, importlib.metadata as md

HOME = os.environ.get('HOME', '/Users/hua')

PKG_KEYS = [
    'arch', 'riskfolio-lib', 'statsforecast', 'optuna', 'stumpy',
    'baostock', 'ruptures', 'hmmlearn', 'pykalman', 'cvxpy',
    'darts', 'sktime', 'pandas', 'numpy', 'gplearn', 'pymc',
    'emcee', 'prophet', 'tsfresh',
]

SCRIPT_PATH = '/Users/hua/.hermes/profiles/quant/scripts/check_tool_stack.py'
SKILL_PATH = '/Users/hua/.hermes/skills/quant/quantitative-research/SKILL.md'


def main():
    # Step 2: HOME 沙箱自检 (pitfall-N+68 / N+81)
    if HOME.startswith('/Users/hua/.hermes/profiles/'):
        print(f'❌ HOME 沙箱劫持 ({HOME}) → 跳过本检查(pitfall-N+81)')
        sys.exit(0)

    # Step 3.1: 直探 — 真实 Python sys.path 解析的版本(唯一权威)
    direct = {}
    for p in PKG_KEYS:
        try:
            direct[p] = md.version(p)
        except Exception as e:
            direct[p] = f'MISSING:{type(e).__name__}'

    # Step 3.2: 读 check_tool_stack.py BASELINE
    script_base = {}
    try:
        with open(SCRIPT_PATH) as f:
            text = f.read()
        # BASELINE 字典模式: 'pkg': 'X.Y.Z'
        for p in PKG_KEYS:
            m = re.search(rf"'{re.escape(p)}'\s*:\s*'([\d.]+)'", text)
            script_base[p] = m.group(1) if m else 'NOT_FOUND'
    except FileNotFoundError:
        print(f'⚠️  {SCRIPT_PATH} 不存在 — Step 0a 协议,降级到内联')
        script_base = {p: 'N/A' for p in PKG_KEYS}
    except Exception as e:
        print(f'⚠️  读 {SCRIPT_PATH} 失败:{e}')
        script_base = {p: 'N/A' for p in PKG_KEYS}

    # Step 3.3: 读 SKILL.md "实测"列(简化匹配:在文件里找 pkg X.Y.Z 模式)
    skill_text = {}
    try:
        with open(SKILL_PATH) as f:
            text = f.read()
        for p in PKG_KEYS:
            # 匹配 "pkg X.Y.Z 实测" 或 "**pkg X.Y.Z**"
            m = re.search(rf"{re.escape(p)}[\s\.\-]+(\d+\.\d+\.\d+)", text)
            skill_text[p] = m.group(1) if m else 'NOT_FOUND'
    except FileNotFoundError:
        print(f'⚠️  {SKILL_PATH} 不存在')
        skill_text = {p: 'N/A' for p in PKG_KEYS}
    except Exception as e:
        print(f'⚠️  读 {SKILL_PATH} 失败:{e}')
        skill_text = {p: 'N/A' for p in PKG_KEYS}

    # Step 4: 三向决策
    print(f'\n=== 三向交叉验证 (HOME={HOME}) ===')
    print(f'{"pkg":<20} {"direct":<15} {"script":<15} {"skill":<15} {"decision"}')
    print('-' * 85)
    real_upgrades = []    # 结论 B:真实升级(BASELINE stale)
    mixed = []            # 结论 D:三方全不一致,需人工判定
    missing = []
    for p in PKG_KEYS:
        d, s, k = direct[p], script_base.get(p, 'N/A'), skill_text.get(p, 'N/A')
        if d.startswith('MISSING'):
            decision = f'⚠️ MISSING ({d.split(":")[1]})'
            missing.append(p)
        elif d == s == k:
            decision = '✅ 三方一致'
        elif d != s and d != k and s == k:
            # 双源 stale, 直探为准 → 真实升级
            decision = f'B 真实升级 (BASELINE stale,patch→{d})'
            real_upgrades.append(p)
        elif d == s and d != k:
            decision = f'B 真实升级 (skill stale,patch SKILL.md→{d})'
            real_upgrades.append(p)
        elif d == k and d != s:
            decision = f'B 真实升级 (script stale,patch BASELINE→{d})'
            real_upgrades.append(p)
        else:
            decision = '⚠️ 三方全不一致, 需人工判定'
            mixed.append(p)
        print(f'{p:<20} {d:<15} {s:<15} {k:<15} {decision}')

    # 决策汇总
    print(f'\n=== 决策汇总 ===')
    print(f'A 沙箱污染(skipped,HOME 自检通过): 0 项')
    print(f'B 真实升级(BASELINE/SKILL.md stale): {len(real_upgrades)} 项')
    print(f'D 三方全不一致(需人工): {len(mixed)} 项')
    print(f'⚠️ 包缺失: {len(missing)} 项')

    if len(real_upgrades) >= 3:
        print(f'\n🚨 >= 3 项真实升级 → patch BASELINE 双源')
        print(f'   待 patch 包:{", ".join(real_upgrades)}')
        major_bumps = [p for p in real_upgrades
                       if md.version(p).split('.')[0] != script_base.get(p, '0').split('.')[0]]
        if major_bumps:
            print(f'   ⚠️ 主版本升级:{", ".join(major_bumps)}')
            print(f'   必跑:arch 8.0.0 GJR-GARCH / pykalman 0.11.2 shape / riskfolio 7.3.0 RiskParity / sktime 1.1.0 API')

    if len(mixed) > 0:
        print(f'\n🚨 三方全不一致 → 走人工判定(pitfall-N+83 §7)')
        print(f'   优先 export PYTHONPATH 修复(pitfall-69),然后 re-run')

    # 返回非零 exit code 让 cron 能感知
    if len(missing) > 0 or len(mixed) > 0:
        sys.exit(2)  # 部分失败
    sys.exit(0)


if __name__ == '__main__':
    main()