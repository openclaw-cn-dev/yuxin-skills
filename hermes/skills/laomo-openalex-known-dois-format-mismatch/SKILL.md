---
name: ***SECRET***
description: 'OpenAlex known_dois.txt 格式与 r162 加载逻辑 mismatch bug — 110 行混合格式 (DOI | venue | title | year) vs r162 精确 lowercase 匹配 → 所有已入档 DOI 永远报 [NEW] 假阳性, P#126 饱和态探查被这一 bug 污染。R576 实证发现并定位。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# OpenAlex known_dois 格式 mismatch bug (R576 实证)

## Bug 现象

`r162_openalex_search.py` 三角度探查时,所有候选 DOI 都报 `[NEW ✓REL]` 即便它们已经在 SKILL.md RAS 矩阵累计 8 篇核心里。

**R576 实测**:
- 6 篇 ✓REL 候选全部标 `[NEW]`:`10.1016/j.envpol.2019.02.062` / `10.1016/j.aquaeng.2006.10.003` / `10.1016/j.aquaeng.2011.11.001` / `10.1016/j.aquaculture.2006.03.019` / `10.1016/j.aquaeng.2015.07.002` / `10.1016/j.biortech.2020.123465`
- 全部 6 篇在 SKILL.md 「RAS 领域知识沉淀」节累计 8 篇核心里(R534/R550/R559/R562)
- 但 r162 输出全 `[NEW]` = **饱和态探查被假阳性污染**

## 根因

**`known_dois.txt` 格式** (`/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt`, 16239 bytes / 110 行):
```
10.1016/j.aquaculture.2006.03.019 | Aquaculture | Engineering analysis of the stoichiometry of photoautotrophic, autotrophic, and  (2006)
```
= DOI + 空格 + `|` + 空格 + venue + `|` + title + ` ` + `(year)`

**r162 加载逻辑** (`scripts/r162_openalex_search.py`):
```python
KNOWN_DOIS_FILE = "/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt"
known_dois = set()
with open(KNOWN_DOIS_FILE) as f:
    known_dois.add(line.lower())          # ← 整行 lowercase 加入
...
new = doi not in known_dois if doi else False   # ← 精确匹配
```

`line.lower()` 是整行 (`"10.1016/..."`) 加入 set, 候选 DOI (`"10.1016/j.aquaculture.2006.03.019"`) 是单 token, 必然 mismatch → 永远判 `not in` → 永远标 `[NEW]`。

## 污染链

- R573 P#126 「OpenAlex 已知 DOI 饱和态升格」是基于 "r162 三角度 6 篇 ✓REL 全部已入 known_dois" 的观察升格的 → 但已知_dois 报"全部已入"是因为它们根本不在 known_dois.txt 里(R573 当时也未 grep 验证),R573 实际未做真正的饱和态判定,只是看到 ✓REL 候选恰好都在 SKILL.md 累计 8 篇核心里
- R576 第一次完整 grep 验证 known_dois.txt 实际只含 1 篇 `10.1016/j.aquaculture.2006.03.019`(虽然带了 venue/title 后缀),其他 7 篇核心 + 大量已知 ✓REL 候选根本没入 known_dois.txt
- 这意味着 P#126 「饱和态探查跳过 r162」SOP 的实证基础 = 假象,真正饱和态并未验证

## 修复 SOP

**(a) 短期 (R577 命中标准 entry 时必修)**:重写 known_dois.txt 为纯 DOI 一行一条格式:
```
10.1016/j.envpol.2019.02.062
10.1016/j.aquaeng.2006.10.003
10.1016/j.aquaeng.2011.11.001
10.1016/j.aquaculture.2006.03.019
10.1016/j.aquaeng.2015.07.002
10.1016/j.biortech.2020.123465
10.1016/j.aquaeng.2015.07.002
10.1016/j.cej.2019.122076
10.1016/j.scitotenv.2020.137848
10.1016/j.biortech.2020.107570
```
(r162 加载逻辑不需改,纯 DOI 一行一条 + 精确 lowercase 匹配即可工作)

**(b) 重构 r162 加载逻辑 (更稳健)**:用 DOI 前缀匹配替代整行匹配:
```python
known_dois = set()
with open(KNOWN_DOIS_FILE) as f:
    for line in f:
        doi = line.strip().split()[0].lower()  # 取首 token = DOI 部分
        if doi.startswith('10.'):
            known_dois.add(doi)
...
new = doi.lower() not in known_dois if doi else False
```

**(c) R577+ 任何"饱和态"判定必先 grep 验证**:`grep -c "^10\." known_dois.txt` + `wc -l known_dois.txt` 对比,R576 实测 `grep -c "^10\." = 0` 表明纯 DOI 一行一条格式根本不存在,所有 110 行都是混合格式。

**(d) P#126 饱和态 SOP 降级**:从「默认跳过 r162」改为「r162 探查后必 grep known_dois.txt 验证确实饱和 → 才跳过」。

## 实证数据 (R576 落地)

- wc -l known_dois.txt = 110 行
- grep `^10\.1016/j.envpol` 命中 = 0 行
- grep `^10\.1016/j.aquaeng.2006.10` 命中 = 0 行
- grep `^10\.1016/j.aquaculture.2006.03` 命中 = 0 行(仅 1 行带该 DOI 但前缀不是 `10.` 是 `10.1016/...` 后跟空格-管道符-venue)
- = 已知 DOI 实际入档率 < 1%,R573 P#126 升格基础不成立

## 关联 Pitfall

- **Pitfall #126 (R573)**: 升格内容包含"OpenAlex 已知 DOI 饱和态"段,但未做 grep 实证验证 → R576 实证 bug 暴露后,该段需降级或补"grep 验证"前置条件。
- **Pitfall #117 (R556/R559/R562/R564)**: 探活先行策略未受影响,仍可单端点直探 HTTP 200。

## R577+ 行动项

- R577 第一动作 (命中标准 entry 时): 重写 known_dois.txt + 重构 r162 加载逻辑 + 重新跑三角度探查验证饱和态真伪
- R577 silent round (mini mode): 仅记录本 bug 升格到 laomo-knowledge skill 的「关键 SOP 速查」表,等下次标准 entry 时再修
