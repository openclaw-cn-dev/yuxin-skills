---
name: a-share-quant-library-usage
description: '渔芯 A 股量化研究的科学计算库全景速查 — 覆盖 iisignature(路径签名)、PyWavelets/pywt(小波时频)、scipy(linalg/optimize/stats/signal/cluster)、torch(PyTorch 深度学习 + macOS MPS)、emcee(networkx 多通道融合)、statsmodels VAR、scipy.stats DSR、split-conformal Wasserstein DRO 八大库在 A 股场景的安装协议、核心 API、真实数据验证与踩坑。触发条件:量化研究、路径签名/Itô Signature、小波分析/阶跃检测/Hurst、矩阵谱半径/组合优化/极值理论/协整检验、深度学习/LSTM/BiGRU/Deep Hedging、Whalley-Wilmott no-trade band、或任何"A 股因子工程 + 科学计算库"落地。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.6.0"
---

> 📌 **AGENTS.md 协调** (2026-08-29 v7): 宽博士现已**完全独立运作**, 唯一直属**华哥** (不请示玉芬, 不参与公司其它任务)。本 skill 所有内容继续由宽博士维护, 但汇报对象/触发决策者 = 华哥本人。

# A 股量化科学计算库全景速查 (A-Share Quant Library Usage)

渔芯 A 股量化研究（渔芯猎手/宽博士）中四个核心科学计算库的统一入口。四个库按"路径几何 / 时频局部化 / 矩阵与优化 / 截面融合"分工，零新增依赖，全部经真实 A 股数据（沪深300/300750 等）验证。

## 四库分工一览

| 库 | 领域 | 核心场景 | 版本 | 完整文档 |
|----|------|---------|------|---------|
| **iisignature** | 路径签名 (rough path) | Itô Signature 因子、Path Portfolio、配对交易执行 | 0.24 | `references/iisignature.md` |
| **empyrical** 🆕 | 因子风险调整评估 (轻量 alphalens 替代) | 渔芯猎手因子稳定性/衰减监控、Sharpe/Sortino/Calmar/Stability/Tail Ratio、零新增依赖 (pyfolio-reloaded 自带) | (pyfolio-reloaded 依赖) | `references/empyrical-usage.md` |
| **pywt (PyWavelets)** | 小波时频局部化 | 涨跌停阶跃检测、趋势因子频域诊断、Hurst 估计 | **1.6.0** (pip3 PyWavelets 包名 → `import pywt` 模块名, 切勿 `import pywavelets`) | `references/pywt-wavelets.md` |
| **scipy** | 矩阵/优化/统计/信号 | 谱半径监控、KellyBoost、CVaR、协整、极值理论、bootstrap 稳健区间、**Student-t/Skew-Normal 厚尾偏度建模 (df=2.35 茅台实测 / 三分决策协议)** | 1.17.1 | `references/scipy.md` + `references/scipy-stats-bootstrap.md` + `references/scipy-stats-skew-t.md` 🆕 |
| **emcee + networkx** | 截面多通道融合门控 | 稳健精选行业风险传染、渔芯猎手多源因子融合、Multiplex GNN 轻量化 (2608.27295) | 3.1.6 / 3.6.1 | `references/multiplex-fusion-gate-emcee.md` |
| **statsmodels VAR** | 多变量时序 + 协方差预测 | 稳健精选协方差预测器、Granger 领先指标、IRF 冲击传导、FEVD 方差分解、VAR 残差协方差替代历史滚动协方差 (条件数 65→41) | 0.14.6 (内置) | `references/statsmodels-vector-ar.md` 🆕 |
| **scipy.stats DSR** | Deflated Sharpe Ratio + Leakage-safe 评估 | FactorGate v1.0 G5 门禁、LLM/搜索生成策略的 trial-count 惩罚、2608.27734 方法论落地 | (scipy 1.17.1 内置 norm + 自实现) | `references/deflated-sharpe-leakage-safe.md` 🆕 |
| **split-conformal + Wasserstein DRO** | 分布无关覆盖率校准 + LP 可解 DRO | FactorGate Gate 4 校准层、渔芯稳健精选 6 DRO 论文拼图执行端 (2608.18123 + 2608.07032) | (numpy/scipy/cvxpy 内置) | `references/***SECRET***.md` 🆕 |
| **torch (PyTorch)** | 深度学习（NN/Autograd/JIT）+ macOS MPS | 渔芯猎手神经网络信号、Deep Hedging LSTM/FF、BiGRU 神经协方差 (2608.30446 Layer 7)、Whalley-Wilmott no-trade band Layer 6.5 | 2.13.0 | `references/torch-deep-hedging.md` 🆕 + `scripts/whalley_wilmott_baseline.py` 🆕 |
| **Adaptive Convex Combination (DisclosureBeta)** | LLM-as-noisy-channel 文本/窗口双通道融合 | 渔芯猎手 G2.5 IPO/限售解禁薄历史 β 估计、text + rolling window 自适应权重、`σ_c² > σ_w²` 安全降级协议 | (numpy + sklearn RandomForestRegressor, 全内置) | `references/***SECRET***.md` 🆕 |
| **arch 8.0.0** 🆕 | GARCH/GJR-GARCH/EGARCH 波动率建模 + 厚尾识别 + Kupiec LR 校准 | 渔芯猎手波动率因子 (conditional_volatility)、Student-t ν → CVaR 厚尾输入、**VaR 校准门禁** (Gate 3.5)、EGARCH 残差绝对值 > 2.5σ → 高波动日标签 (与 hmmlearn/ruptures/stumpy 四层体制检测互补) | 8.0.0 | `references/arch-garch-volatility.md` 🆕 |
| **sentence-transformers** 🆕 | LLM 嵌入 → Wasserstein-2 风险证书 (无 Σ 协方差) | 渔芯猎手替代协方差估计路径、8 公司 24 snippets PoC 验证、HRP leaf order 多视角稳健性检查、var_bound = w^T W2 w 系统性方差上界 | 5.4.1 (依赖 transformers 5.14.1 + torch 2.13.0, 零独立安装) | `references/***SECRET***.md` 🆕 |
| **scipy.stats W2 (1D)** 🆕 | Wasserstein-2 distance 5 行闭式 (零新增依赖) | 已有日收益/因子值序列 → pairwise W² dispersion → 风险分布相干性门禁；HRP 多视角稳健性检查第三视角；体制切换前后 W² 漂移检测 | (scipy.stats + numpy.quantile 内置) | `references/***SECRET***.md` 🆕 |
| **riskfolio-lib** 🆕 | 组合优化: 均值-方差 / 风险平价 / CVaR / MaxSharpe / Black-Litterman / HRP | 渔芯稳健精选策略权重、4 ETF 池实证对比 (心跳 #N+31 baostock 164d)、FactorGate v2.5 G5 三关全过 (dutch book/Wasserstein/决策相干性) | **6.1.1 cron session / 7.3.0 hermes venv** (双版本差异显著, 必做 §0 诊断) — API break: rp_optimization rename / b=None 移除 / MaxSharpe 返回 None ⚠️ 必须 try/except; 6.1.1 wc_optimization 有 'to_numpy' bug → fallback 单资产 (论文一致) | `references/***SECRET***.md` (7.3.0) + `references/riskfolio-6.1.1-cron-session.md` 🆕 (6.1.1 + doubly stochastic + ρ-knob) |

## 共享踩坑（三库通用，A 股数据源相关）

12. **同一 skill 文档跨 Python 环境版本漂移 (心跳 #N+43 实测)** — riskfolio-lib 在 hermes-agent venv (Python 3.11) 是 7.3.0, 在 cron session (Python 3.9) 是 6.1.1, **API 显著不同** (wc_optimization 签名 / BL 参数路径 / b 参数支持)。**踩坑症状**: 心跳 #N+31 写的 7.3.0 优化代码, 心跳 #N+43 在 cron session 跑就 `TypeError: unexpected keyword 'P'` 或 `'NoneType' has no attribute 'to_numpy'`。**渔芯铁律**: 任何组合优化/Black-Litterman/wc_optimization 代码开工前必做 §0 (references/riskfolio-6.1.1-cron-session.md) 5 步版本诊断, **不要盲信 skill 文档的历史版本号**。两份文档同时维护 (7.3.0 + 6.1.1) 是当前现实, 不接受合并为单版本。


1. **baostock login 必须放函数首行** — `query_hs300_stocks()` 内部抛 `AttributeError: user_id` 若未 login；每函数 `bs.login()` 开头、`bs.logout()` 结尾。
2. **pandas 3.0+ `pct_change` 必须显式 `fill_method=None`** — 否则 FutureWarning；vol_change / mom5 等均受影响。
3. **A 股涨跌停导致路径/序列不连续** — 路径签名 driver 拟合必须纳入 jump 维度；小波阶跃检测用百分位阈值（非 σ 倍数，N<500 样本 σ 不可靠）。
4. **cron 模式 `execute_code` 被 BLOCKED** — 量化心跳在 cron 下跑时，Python subprocess 一律不可用；改走标准工具链（web_search / write_file / terminal 单独调用）。
5. **包名 ≠ 模块名 + pip3 metadata 与 site-packages 漂移（心跳 #N+6 实测 4 工具中招）** — 验证已安装包时**永远不要信 `pip3 list` 单独结果**，必须 `pip3 list` + `python3 -c 'import X'` 双源交叉核对：
   - `PyWavelets` 1.6.0 包名是 PyWavelets, **模块名是 `pywt`**（`import pywavelets` 必失败）→ 工具栈表里的 "pywavelets 1.8.0" 是误记, 实际是 pywt 1.6.0。**心跳 #N+8 实战**: 工具栈校验脚本里写 `import pywavelets` → ModuleNotFoundError; 改 `import pywt` → 正常工作。**别再踩这个坑**
   - `alphalens-reloaded` 0.4.5 包名带 -reloaded 后缀, **模块名仍是 `alphalens`**（`from alphalens_reloaded import ...` 失败, `from alphalens import ...` 成功）
   - `python-constraint` 不是 `python_constraint`（pip 包名 `python-constraint`, 模块名 `constraint`）
   - `pytensor` pip3 metadata 显示 2.15.0 已装, 但 site-packages/pytensor 目录不存在 → `import pytensor` 失败（pitfall #18 永久不可用）
   **诊断流程**:
   ```bash
   # Step 1: pip 视角
   pip3 show <package> | grep -E "Name|Version|Location"
   # Step 2: 真实 import 视角（cron 模式必须用 terminal + python3 -c）
   python3 -c "import <actual_module_name>; print('OK')"
   # Step 3: alias 全部尝试（PyWavelets/alphalens 案例）
   python3 -c "import pywt; from alphalens import performance; from constraint import Problem; print('all OK')"
   ```
   **修复**: 工具栈表里写错包名的条目，立即更正（避免下次心跳误信）。重装仍无效的永久失活（pitfall #18/23），用替代工具覆盖。
6. **DSR 实现双坑（心跳 #N+10 实测）** — Deflated Sharpe Ratio Python 实现易踩两类坑，详见 `references/deflated-sharpe-leakage-safe.md`：
   - **多行表达式断行**: `+` 放行首时 Python 视为新语句丢弃值，必须放行尾或用括号跨行
   - **n_trials=1 inf 陷阱**: `norm.ppf(1-1/n)` 在 n=1 返回 `-inf`，导致 SR_deflated=`-inf` 把所有单 trial 都判为不可信；必须 fallback 到渐进式 `√(2 ln n) - ln(ln(en))/(2√(2 ln n))`
7. **Deep Hedging LSTM "坐等"陷阱（心跳 #N+11 实测, 2608.29025 复现）** — 神经网络 LSTM/FF 即使配 CVaR loss + 20× 交易频率惩罚, **仍学不出"少交易"行为**: 实测 GBM σ=0.6 / 5 bp 成本下 LSTM DH 净 PnL=-0.34 / Sharpe=-7.30（亏损），而 Whalley-Wilmott k=0.1 用 13× 少交易仍保持 45% 净 PnL/Sharpe=32.9。**渔芯猎手铁律**: 神经网络信号 → Whalley-Wilmott band → 订单（Layer 6.5），绝不让神经网络直接生成订单。详见 `references/torch-deep-hedging.md` § 渔芯 A 股场景适配 + `scripts/whalley_wilmott_baseline.py`。
8. **合成蒙特卡洛数据 Shape Buffer 陷阱（心跳 #125 实测, DisclosureBeta PoC 复现）** — 用 `np.random.multivariate_normal(size=(N_OBS, N_SIM))` 固定 shape 后, 模拟滚动窗口/变长切片时 `factor_returns[:n_obs]` 直接 IndexError。**正确做法**: 一次性 over-generate buffer (`size=(N_OBS_MAX, N_SIM)`, N_OBS_MAX = 最大可能窗口长度), 后续任意 `n_obs ≤ N_OBS_MAX` 安全。**触发场景**: IPO 限售解禁前 60 天 / 后 60 天变长窗口、VaR 估计 expanding window、LLM Agent 训练时变长 context。详见 `references/***SECRET***.md` § 5。
9. **Adaptive Convex Combination "never worse" 条件性陷阱（心跳 #125 实测, 2609.02900 PoC 证伪）** — 论文 DisclosureBeta 声称 adaptive 凸组合 "never worse than either component", 但 PoC 实证: 当 `σ_text > σ_window`（文本 LLM 噪声超过窗口方差）, adaptive 反而劣于纯 window。**渔芯猎手铁律**: 任何 adaptive 融合器必须配 **安全降级机制** —— `if σ_c > σ_w: use pure window`, 与 2608.20842 Compatibility Gap 论文"realism vs fidelity 分离"思路一致（adaptive 的目标不是追求最低 MSE, 而是保证最坏情况不超过任何单通道）。详见 `references/***SECRET***.md` § 3 + § 4.1。

10. **GARCH 厚尾识别正确 ≠ VaR 校准通过（心跳 #131 实测, arch 8.0.0 PoC 验证, 与 2607.16229 FinBench 校准 P1 对齐）** — 渔芯实测 1000 天合成 Student-t(df=5) + GARCH 聚类数据：MLE 厚尾识别 Student-t ν 估计 5.17-5.26（真值 5，误差 < 5% ✅），但 Kupiec LR VaR 5% 校准**全部 FAIL**（22 violations/1000 vs 期望 50，LR p<0.0001）。**结论**: 即使 MLE 把分布尾部参数估对了，**条件波动率本身的时变结构**仍可能系统性低估左侧风险。**渔芯铁律**: 任何波动率模型上线前**必须**走 kupiec LR / Christoffersen 独立性测试双关（Gate 3.5 新增）。**触发场景**: arch / GARCH-family / stochastic vol / EVT-POT 模型上线前的最后一关。详见 `references/arch-garch-volatility.md` § 关键结果 3。**与 pitfall #14 互补**: #14 是"自建 PoC 假阴性", 本坑是"标准 PoC PASS 但校准 FAIL"——共同教训 = **任何波动率/分布模型都需要校准度量化审计, 不能只看 AIC/BIC/对数似然**。

11. **W¹ vs W² 跨分布放大不对称陷阱（心跳 #N+36 实测, 2608.29692 P0 学习落地）** — 在 1D 上 W¹ 和 W² 对同一对分布给出**不同量级**的放大倍数：实测 normal(μ=0.001, σ=0.02) vs Student-t(df=3)·0.03 stress 分布, **W¹ 跨分布放大 21.3× (0.000803 → 0.017094)** 而 **W² 仅 10.9× (0.002087 → 0.022731)**。直觉解读: W² 是 W¹ 的"二阶矩版本", 对分布**形状变化**更敏感（捕获厚尾细节、偏度、峰度），但**整体距离量级较小**。**渔芯铁律**: ① 报告 W² 时同时报告 W¹ 作为 sanity check（差距 > 3× 即怀疑分布 shape 异常）② W² 不能直接与 W¹ 阈值互换使用（不能把 W¹=0.01 阈值搬到 W²）③ 多视角稳健性检查必须把 W² 单独列出，不能与 W¹ 合并。**触发场景**: FactorGate v2.5 G5.4 W² 风险分布相干性门禁设计 / 多公司 dispersion matrix 上界推导（2608.29692 §3）/ 体制切换前后漂移检测。详见 `references/***SECRET***.md` § W1 vs W2 关系 + § 边界与陷阱。

## 子文档索引

- `references/iisignature.md` — iisignature 0.24 安装协议（`--no-build-isolation --no-deps`）、API 速查（sig/logsig/Stream）、A 股真实数据验证（沪深300 × 6 年，degree=3 Top-5 融合 ΔPearson +0.0510）、配套论文（2608.18120 / 2608.02355 / 2607.19005 / 2606.31387）。附 `references/***SECRET***.md`。
- `references/empyrical-usage.md` 🆕 — empyrical A 股因子评估轻量管线（心跳 #130, 2026-09-05）。零新增依赖的 20+ 风险调整指标库，作为 alphalens-reloaded 的轻量替代方案 — 渔芯双轨流水线: 日常/实时评估用 empyrical, 完整 tearsheet 用 alphalens-reloaded。Stability<0.3 自动告警 / roll_sharpe_ratio 衰减监控 / FactorGate v2.5 G5.1 概率相干性实证补强。心跳 #130 验证: 4/4 PASS 阈值 (Sharpe>0.5 / Stability>0.5 / MDD>-30% / |Beta|<1.5)。
- `references/pywt-wavelets.md` — PyWavelets 1.6.0 阶跃检测（DWT cD1 90% 百分位，300750 真实数据 5.95x 动量放大）、SWT vs DWT、CWT 时频、Hurst 估计、LLM 因子校准诊断。配套论文（2608.08625 / 2607.19497 / 2608.00127 / 2608.20304）。
- `references/scipy.md` — scipy 1.17.1 五子模块 × 11 场景（谱半径/Loop-Gain、KellyBoost、Physical Crash Frontier SOCP、CVaR 约束、Wasserstein 漂移、协整、极值 GPD/GEV、HRP 聚类、频谱）。附 `references/scipy-heartbeat-95.md`、`references/scipy-heartbeat-99.md`。
- `references/scipy-stats-bootstrap.md` 🆕 — scipy.stats.bootstrap 心跳 #110 实测验证：替代手写 np.percentile Bootstrap（代码量 -50%），支持 percentile/basic/BCa 三种 method，FactorGate Gate 4.2 杠杆存活率 CI 升级路径，配对 Bootstrap 因子 IC 漂移检测。
- `references/scipy-stats-skew-t.md` 🆕 — scipy.stats Student-t/Skew-Normal 厚尾偏度建模（心跳 #113, 2026-09-03）。贵州茅台 1212 天实证：Student-t **df=2.35 极厚尾**、Norm 99% VaR **低估 1.67%**、t 误差仅 0.14%。三分决策协议 PASS/ABSTAIN/REJECT（对接 2609.02535 P0）。30 只合成股票单股偏度估计**方向不稳**（panel bias 风险）→ 因子模型必须 panel 联合估计。完整 PoC 脚本 + 渔芯猎手 v2.0 升级路径（Norm 残差→t-GARCH / t-copula）。
- `references/multiplex-fusion-gate-emcee.md` — emcee 3.1.6 + networkx 3.6.1 截面多通道融合门控（2608.27295 Multiplex GNN 风格贝叶斯实现，零依赖 softmax 参数化 + Dirichlet 平坦先验 + 8 步 A 股模板 + 7 条踩坑）。配套论文（2608.27295 / 2607.00475 / 2607.15195 / 2608.13913 "融合门控 2026 范式"）。
- `references/statsmodels-vector-ar.md` 🆕 — statsmodels VAR(p) 多变量时序 + Granger + IRF + FEVD + 残差协方差预测器（心跳 #N+13 实测）。4 变量×940 样本拟合 1.0 ms，FEVD 解释 69.0% 中证500 预测方差，VAR 残差协方差条件数 41 远低于历史滚动 65。配套论文（2608.24449 / 2606.27462 / 2608.23393 / 2606.09420 / 2607.05320），三连洞见（FEVD>Granger / 隐式正则化 / IRF 1.5% 仓位降权门禁）。
- `references/wsvi-w-shape-validation.md` 🆕 — WSVI (W-shape IV smile) 数学验证 PoC (心跳 #N+8, 2026-08-30) 加法扰动实现 + Breeden-Litzenberger 双峰密度检测 + 凸性放宽三维验证 (W-shape ✅ / 双峰 ✅ / 凸性放宽 ✅) + IV 五层架构 L2.5 升级 (L1 L-FM / L2 SAAM / **L2.5 WSVI** / L3 Transport / L4 DSPM / L5 Unified Theory)。零新增依赖 (scipy.signal.argrelextrema + numpy 高斯核)。配套论文 (2608.22620 + 2608.00616 + 2608.12493 + 2608.08625)。A 股 50ETF/300ETF 财报/政策事件窗口 straddle 信号。
- `references/deflated-sharpe-leakage-safe.md` 🆕 — Deflated Sharpe Ratio + Leakage-safe 评估（心跳 #N+10, 2026-08-31）。核心论点:**统计校正 ≠ 结构性消除** (Gençay 实证: 故意泄漏 SR=35 仍通过 DSR SR_deflated=15.73), 必须 Registry-validated tools + Trial-count deflation 联合使用。PoC 验证 n_trials=100 时 E[max|null]=0.24。配套论文 2608.27734 + 2607.20093 + 2607.04958 + 2607.20168 形成"渔芯因子评估铁四角"。FactorGate v1.0 新增 G5 门禁设计。
- `references/***SECRET***.md` 🆕 — Split-Confinite Calibration + Empirical Wasserstein DRO（心跳 #N+11, 2026-09-01）。两个 zero-new-deps 函数组合: split_conformal_calibrate (分布无关有限样本 marginal coverage) + empirical_wasserstein_radius (W1/W2/W_inf 1D 闭式估计) + Wasserstein DRO LP (cvxpy SCS 求解器)。4 demo 全部 PASS: n_cal=500→ coverage 88.4% / shift regime W2=0.0171 vs baseline 0.0009 (18× 区分) / Gate 4 calibration 93.9% PASS / DRO LP 4资产×60场景 optimal。FactorGate Gate 4 升级路径 = 关 0: split-conformal calibrated IC 区间 → 关 1-6 继承心跳 #76 → 关 0 FAIL 切换 riskfolio-lib DRO weights。配套论文 2608.18123 (P0 learned Wasserstein DRO, split-conformal 提供有限样本覆盖) + 2608.07032 (P0 certified DRO LP) + 2608.13748 (P1 multi-period VaR DC) + 2606.27462 (P0 决策几何协方差) 形成 6 DRO 论文方法论拼图。
- `references/torch-deep-hedging.md` 🆕 — torch 2.13.0 (PyTorch) 渔芯 A 股量化研究速查（心跳 #N+11, 2026-09-01）。macOS MPS 后端 + Autograd + LSTM/BiGRU/MLP + CVaR 自定义 Loss + 与 riskfolio/cvxpy 集成 + Whalley-Wilmott no-trade band baseline。配套论文 2608.29025 (P0 Deep Hedging BTC 经验拷问 — LSTM/FF 在真实数据反亏, W-W k=0.1 用 13× 少交易保持 45% 净 PnL) + 2608.31041 (P0 Agentic QT Survey 五阶段框架) + 2608.30446 (P0 Pairwise-complete 神经协方差 Layer 7)。渔芯猎手 Layer 6.5 风控必入。
- `references/***SECRET***.md` 🆕 — Adaptive Convex Combination 渔芯猎手 G2.5 IPO/限售解禁薄历史 β 估计（心跳 #125, 2026-09-04）。LLM-as-noisy-channel 理论下界 + DIM (Disclosure Incentive Measure) + `w_text = σ_w² / (σ_c² + σ_w²)` 自适应权重。PoC 实证 "never worse" 声明条件性证伪（σ_text > σ_window 时 adaptive 反而劣于纯 window）→ 安全降级协议 `if σ_c > σ_w: use pure window`。配套论文 2609.02900 (P1 DisclosureBeta) + 2609.03552 (P0 EFM 稳定期) + 2608.01494 (P0 Conformal Kelly 事件期) 形成"稳定期 + 初创期 + 事件期"三阶段自适应 β 估计体系。渔芯猎手 G2.5 子门禁设计草案 + DIM 评分工程化代码模板。
- `references/arch-garch-volatility.md` 🆕 — arch 8.0.0 GARCH/GJR-GARCH/EGARCH 实战学习笔记（心跳 #131, 2026-09-05）。三模型 AIC/BIC 差距 < 1 → 默认 GJR-GARCH(1,1) 兼顾杠杆+经典；**核心教训**: Student-t ν 估计误差 < 5% 但 Kupiec LR VaR 5% 校准全部 FAIL → **渔芯铁律**: 任何波动率模型上线必须经 kupiec LR + Christoffersen 独立性双关（Gate 3.5 新增）。配套论文 2606.09478 (CSI 300 GARCH+XGBoost P1) + 2607.16450 (台湾 ETF GJR-GARCH P1) + 2607.16229 (FinBench 校准 P1)。渔芯落地路径: ① GJR-GARCH conditional_volatility → 渔芯猎手波动率因子 ② ν 输出 → riskfolio-lib 厚尾 CVaR 优化 ③ EGARCH 残差绝对值 > 2.5σ → 高波动日标签（与 hmmlearn/ruptures/stumpy 四层体制检测互补）。
- `references/***SECRET***.md` — riskfolio-lib 7.3.0 组合优化速查（心跳 #N+31, 2026-09-06）。4 个 7.3.0 API break: `b=None` 移除 / `risk_parity` → `rp_optimization(rm='MV')` 重命名 / MaxSharpe 熊市返回 None / MinCVaR 必须 try-except。A 股 4 ETF 池 baostock 164d 实战: 能源 ETF corr=0.987 伪分散 / MinVar 自动剔除冗余资产 / MaxSharpe 无解 / EW Sharpe=0.911 反而最优。FactorGate v2.5 G5 三关 (dutch book/Wasserstein/决策相干性) 集成验证全部 PASS。Cron 实例锁定 7.3.0, 别盲目 `pip install --upgrade`。
- `references/riskfolio-6.1.1-cron-session.md` 🆕 — riskfolio-lib **6.1.1** cron session (Python 3.9) 专门版（心跳 #N+43, 2026-09-08）。**与主文件互补**: 主文件记录 hermes-agent venv (Python 3.11) 的 7.3.0, 本文件记录 cron session 实际安装的 6.1.1 — 两者 API 差异显著 (6.1.1 wc_optimization 有 bug / BL 参数需走 blacklitterman_stats helper / 必做 §0 版本诊断)。**新增技术**: ① doubly stochastic matrix + Sinkhorn-Knopp 投影 (2609.04496 majorization 落地) ② Concentration Paradox ρ-Knob 混合部署策略 (60% HRP + 40% WC 单 defensive ETF, 8× HHI 差距实证) ③ wc_optimization bug fallback 完美吻合 paper 预测。配套 PoC 5 件 (心跳 #N+43 实证)。
- `references/***SECRET***.md` 🆕 — sentence-transformers 5.4.1 + Wasserstein-2 风险证书（心跳 #N+31, 2026-09-06）。LLM 嵌入作为"分布值特征" → 多公司 W² 离散度矩阵 → 系统性方差证书 `var_bound = w^T W2 w`（**无需估计交叉协方差 Σ**，仅需边际波动率）。8 公司 24 片段 PoC: HRP leaf order ward 聚类 → 多样化友好配置 + 风险上界 vs 等权对比。支撑论文 2608.29692 / 2608.29669 (P1 Gawronsky/Huang Distributional Fields)。零独立安装（sentence-transformers + transformers + torch 已预装），中文感知 (all-MiniLM-L6-v2 80MB) + 大规模 Qwen3-Embedding-8B 替换路径。渔芯猎手协方差管线新支线：传统 Σ vs W² 证书双视角稳健性检查。
- `references/***SECRET***.md` 🆕 — scipy.stats Wasserstein-2 1D quantile integration 5 行闭式实现（心跳 #N+36, 2026-09-07）。**零新增依赖** 路径：当特征已计算好（baostock 日收益 / HRP leaf / hmmlearn 体制 / arch GARCH vol / 因子 IC）时，不需要拉起 sentence-transformers。W¹ (scipy.stats.wasserstein_distance 内置) vs W² (自实现 quantile integration) 1D 闭式对比 + 数学保证（单调/对称/三角不等式）+ 渔芯 3 种落地模式（多公司 dispersion / HRP 多视角 / 体制切换漂移）。**核心陷阱**: W² 跨分布放大倍数 10.9× vs W¹ 的 21.3× — 二者不能直接互换阈值，报告时需同时列。配套论文 2608.29692 / 2608.29669 / 2609.02525 / 2607.21170。FactorGate v2.5 G5.4 W² 风险分布相干性门禁直接落地。
- `scripts/whalley_wilmott_baseline.py` 🆕 — Whalley-Wilmott vs Deep Hedging 6 策略对比可重跑 PoC（心跳 #N+11）。命令行工具，支持自定义 σ/n_paths/cost_bps/k，完整复现 2608.29025 实测结果。渔芯猎手 Layer 6.5 风控层决策依据。

## 与主研究 skill 的关系

`quantitative-research` 是渔芯量化研究的**顶层工作流**（策略研究、论文检索、报告输出）；本 skill 是其中**科学计算库落地层**的速查手册。做策略时先按 `quantitative-research` 走流程，需要具体库的 API/踩坑时查本 skill 对应子文档。