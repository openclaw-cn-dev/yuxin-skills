"""
心跳 Step 1 工具栈版本审计 — 心跳 #N+65 落地(2026-09-13 周日)
=========================================================
替代 SKILL.md §0.5 案 B 内联探测的封装脚本(可重跑,与 baseline diff)。

⚠️ pitfall-64: SKILL.md 历史列出的 `check_tool_stack.py` 路径长期未生成
    (心跳 #N+60/#N+62/#N+63 一直走内联降级),心跳 #N+65 终于落地。
    落地后 §0.5 心跳 Step 1 应优先跑这个脚本,失败时降级到 §0.5 案 B。

⚠️ pitfall-67(新增,心跳 #N+65 实测): **`importlib.metadata.version()` key
    ≠ `pip3 show` 显示的包名**:
    - `importlib.metadata.version("riskfolio")` → PackageNotFoundError
    - `importlib.metadata.version("riskfolio-lib")` → "6.1.1" ✅
    - `pip3 show riskfolio` → "Name: riskfolio, Version: 6.1.1" ✅
    心跳 Step 1 baseline 必须用 metadata 名(见 PKG_KEYS),不要凭 pip3 install 时写的名。

⚠️ pitfall-61: **不要用 `pkg.__version__`** — stumpy 等包的 `__version__` 是 setup.py
    占位符,必须用 `importlib.metadata.version()` 唯一权威判定。

用法:
    # 标准审计(对比 baseline):
    python3 /Users/hua/.hermes/profiles/quant/scripts/check_tool_stack.py
    python3 /Users/hua/.hermes/profiles/quant/scripts/check_tool_stack.py --baseline
    # 仅打印当前实测(不 diff):
    python3 /Users/hua/.hermes/profiles/quant/scripts/check_tool_stack.py --current
    # 用自定义 baseline:
    python3 /Users/hua/.hermes/profiles/quant/scripts/check_tool_stack.py --baseline-file /path/to/baseline.json
"""
import sys
import json
import argparse
import importlib.metadata as md

# ⚠️ pitfall-67: metadata key 与 pip3 显示包名不一致的,必须按 metadata key 写
# 例如 riskfolio 安装包名是 `riskfolio`,但 metadata distribution name 是 `riskfolio-lib`
PKG_KEYS = [
    'arch', 'riskfolio-lib', 'statsforecast', 'optuna', 'stumpy',
    'baostock', 'akshare', 'ruptures', 'hmmlearn', 'pykalman',
    'cvxpy', 'emcee', 'pymc', 'gplearn', 'tsfresh', 'darts', 'sktime', 'prophet',
]

# baseline(心跳 #N+60 实测,2026-09-13 心跳 #N+65 验证 0 漂移)
BASELINE = {
    'arch': '7.2.0',
    'riskfolio-lib': '6.1.1',
    'statsforecast': '2.0.3',
    'optuna': '4.8.0',
    'stumpy': '1.13.0',
    'baostock': '0.9.3',
    'akshare': '1.18.57',
    'ruptures': '1.1.10',
    'hmmlearn': '0.3.3',
    'pykalman': '0.10.2',
    'cvxpy': '1.7.5',
    'emcee': '3.1.6',
    'pymc': '5.8.0',
    'gplearn': '0.4.2',
    'tsfresh': '0.21.2',
    'darts': '0.37.1',
    'sktime': '0.35.0',
    'prophet': '1.3.0',
}


def probe_current():
    """返回 {pkg_key: {'status': 'OK'|'MISSING', 'version': str|None, 'error': str|None}}"""
    results = {}
    for key in PKG_KEYS:
        try:
            ver = md.version(key)
            results[key] = {'status': 'OK', 'version': ver, 'error': None}
        except Exception as e:
            results[key] = {'status': 'MISSING', 'version': None, 'error': f'{type(e).__name__}: {e}'}
    return results


def diff_baseline(current, baseline):
    """对比 baseline,返回漂移包列表"""
    drift = []
    for key in PKG_KEYS:
        if key not in baseline:
            continue  # 新增包,不算漂移
        c = current[key]
        b = baseline[key]
        if c['status'] == 'MISSING':
            drift.append({'pkg': key, 'baseline': b, 'current': 'MISSING', 'type': 'disappeared'})
        elif c['version'] != b:
            drift.append({'pkg': key, 'baseline': b, 'current': c['version'], 'type': 'version_drift'})
    return drift


def main():
    parser = argparse.ArgumentParser(description='心跳 Step 1 工具栈版本审计')
    parser.add_argument('--baseline', action='store_true', help='与 baseline diff 模式')
    parser.add_argument('--current', action='store_true', help='仅打印当前实测(不 diff)')
    parser.add_argument('--baseline-file', type=str, help='自定义 baseline JSON 路径')
    args = parser.parse_args()

    # 加载 baseline
    baseline = BASELINE
    if args.baseline_file:
        with open(args.baseline_file) as f:
            baseline = json.load(f)

    # 探测当前
    current = probe_current()
    ok_count = sum(1 for v in current.values() if v['status'] == 'OK')

    # 输出
    if args.current or not args.baseline:
        # 仅打印当前
        print(f'=== 工具栈实测 ({ok_count}/{len(PKG_KEYS)} 包可用) ===')
        for key in PKG_KEYS:
            v = current[key]
            if v['status'] == 'OK':
                print(f'  OK {key}: {v["version"]}')
            else:
                print(f'  MISS {key}: {v["error"]}')
        print()

    if args.baseline:
        # diff baseline
        drift = diff_baseline(current, baseline)
        print(f'=== Baseline Diff ({len(drift)} 漂移 / {ok_count}/{len(PKG_KEYS)} 可用) ===')
        for d in drift:
            print(f'  DRIFT {d["pkg"]}: baseline={d["baseline"]} -> current={d["current"]} ({d["type"]})')

        # pitfall-62 P0 红旗协议
        if len(drift) >= 3:
            print(f'\n[P0 RED] {len(drift)} 漂移 >= 3 阈值')
            print('   协议: 不执行任何基于工具栈的下游决策 + evolution 报告 P0 红旗段')
            print('   + 飞书事件驱动直达 boss + 列降级运行方案')
            return 2  # exit code = 2 -> P0
        elif len(drift) >= 1:
            print(f'\n[WARN] 普通漂移: {len(drift)} 包,记录到 evolution 报告即可')
            return 0
        else:
            print('\n[OK] 0 漂移,工具栈正常')
            return 0

    # 默认 current 模式(无 args): exit 0
    return 0


if __name__ == '__main__':
    sys.exit(main())