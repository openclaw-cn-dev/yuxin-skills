"""Patch SKILL.md to add N+151 + N+152 pitfall entries + v1.11 header + 关键词漏斗 protocol.

Usage: python3 scripts/_patch_skill_v111.py
维护: 宽博士 心跳 #N+129 curator pass
"""
import os, sys

SKILL = "/Users/hua/.hermes/skills/quant/quantitative-research/SKILL.md"

def main():
    content = open(SKILL, encoding='utf-8').read()

    # 1. 追加 v1.11 增量头注 (after v1.10)
    v110_marker = "> 🤖 **v1.10 增量 (2026-09-24 心跳 #N+129)**"
    v111_block = """

> 🤖 **v1.11 增量 (2026-09-24 心跳 #N+129 沉淀)** — 新增 **pitfall-N+151**(arXiv 精筛关键词打分漏斗:33 篇 → Top 3 才抓 abstract,沿用 N+142/N+145/N+149/N+150) + 新增 **pitfall-N+152**(evolution 报告"持仓陈旧度声明"标准 header,与 N+148 协议配对的报告层产物) + 沿用 N+150 预判协议端到端 0 失败验证(本次心跳 10 tool call 完成 3 篇精筛)| Step 0 持仓陈旧度核验 → snapshot 9 天 🚨🚨🚨 拒绝 actionable, 只做方法论复盘 + arXiv 精筛 + 双注册 + evolution 报告"""
    if v110_marker not in content:
        print("FAIL: v1.10 marker not found"); return False
    content = content.replace(v110_marker, v110_marker + v111_block, 1)

    # 2. arXiv 精筛 SOP §1 后追加 §1.5 关键词打分漏斗 (在 §2 四档优先级筛选规则前)
    section_2_marker = "### 2. 四档优先级筛选规则(2026-09 心跳精炼)"
    keyscore_block = """
### 1.5 关键词打分漏斗(沿用 pitfall-N+151,心跳 #N+129 实测)

> 50 篇 listing 抓全 + 对比 SKILL.md 已记录 ID 后,**通常有 30+ 篇本周新文**。不必都抓 abstract,先打关键词分 → Top 3-5 才精筛:

```python
score_kw = ["portfolio", "optim", "risk", "regime", "factor", "multilevel",
            "calibration", "hedging", "Bayesian", "kernel", "spectral",
            "Markowitz", "covariance", "robust", "deep hedging",
            "mean-field", "switching", "long-memory"]

scores = []
for aid, title in new_ids.items():
    s = sum(1 for k in score_kw if k.lower() in title.lower())
    scores.append((s, aid, title))
scores.sort(reverse=True)

top_candidates = [aid for s, aid, _ in scores[:5] if s > 0]
# score >= 2: 优先抓 abstract
# score = 1: 候选池,Top 3 不够时补
# score = 0: 不抓(节省 tool call)
```

**实战**:心跳 #N+129 33 篇新文 → Top 10(score=2 5 篇,score=1 5 篇)→ 选 Top 3 抓 abstract 一次成功 → 10 tool call 完成全部精筛。详见 `references/pitfall-N+***SECRET***.md`。

"""
    if section_2_marker not in content:
        print("FAIL: 2 marker not found"); return False
    content = content.replace(section_2_marker, keyscore_block + section_2_marker, 1)

    # 3. pitfall 表追加 N+151 + N+152 (在 N+150 行后)
    pitfall_n150 = "| **N+150** | **SKILL.md table anchor 字符串脆弱 + 跨 profile 写文件预判跳过 write_file (N+128 实测:anchor 漏 `**` 闭合浪费 2 tool call + 跨 profile write_file 必失败)** | **#N+128** | `references/pitfall-N+***SECRET***.md` |"
    new_pitfall_rows = """
| **N+151** | **arXiv 精筛关键词打分漏斗:33 篇 → Top 3 才抓 abstract (N+129 实测,节省 50%+ tool call)** | **#N+129** | `references/pitfall-N+***SECRET***.md` |
| **N+152** | **evolution 报告"持仓陈旧度声明"标准 header(沿用 N+148 协议的报告层产物,N+129 实测)** | **#N+129** | `references/pitfall-N+***SECRET***.md` |"""
    if pitfall_n150 not in content:
        print("FAIL: N+150 row not found"); return False
    content = content.replace(pitfall_n150, pitfall_n150 + new_pitfall_rows, 1)

    # 4. evolution 工作流 §1 后追加 §1.5 持仓陈旧度声明模板(沿用 N+152)
    step1_marker = "1. heartbeat_check → 无任务 → 进入自我进化\n2. arXiv 精筛"
    step1_replacement = """1. heartbeat_check → 无任务 → 进入自我进化
1.5. **evolution 报告顶部声明(沿用 N+152)**:如果 holdings.json snapshot_time 陈旧(>3 天 STALE / >7 天 CRITICAL),evolution 报告必加"持仓陈旧度声明"段,沿用 N+148 阈值。模板:
```
## 持仓陈旧度声明(沿用 pitfall-N+148)
- snapshot_time: <ISO>
- age: N 天
- 判定: CRITICAL STALE / STALE / FRESH
- actionable 状态: 暂停 / 受限 / 正常
- boss_decision_pending: 「我的持仓」页请上传新截图(若 STALE)
```
详见 `references/pitfall-N+***SECRET***.md`。
2. arXiv 精筛"""
    if step1_marker not in content:
        print("FAIL: step1 marker not found"); return False
    content = content.replace(step1_marker, step1_replacement, 1)

    with open(SKILL, 'w', encoding='utf-8') as f:
        f.write(content)

    # 验证
    new = open(SKILL, encoding='utf-8').read()
    checks = [
        ("v1.11 增量" in new, "v1.11 头注"),
        ("1.5 关键词打分漏斗" in new, "关键词漏斗 §1.5"),
        ("pitfall-N+151" in new, "N+151 pitfall 引用"),
        ("pitfall-N+152" in new, "N+152 pitfall 引用"),
        ("持仓陈旧度声明" in new, "持仓声明 §1.5"),
    ]
    for ok, msg in checks:
        print(f"{'OK' if ok else 'FAIL'} {msg}")
    print(f"SKILL.md 总行数: {new.count(chr(10))}")
    return all(ok for ok, _ in checks)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)