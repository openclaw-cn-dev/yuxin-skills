# 策略索引

> 玉芬/宽博士维护 · 最后更新 2026-09-01

每个策略一个 JSON 骨架 + 一份参数 + 一份回测结果。

## 当前策略

| 策略 ID | 名称 | 类型 | 标的 | 状态 |
|---|---|---|---|---|
| strat-001 | 沪深 300 行业动量轮动 | 趋势/动量 | 沪深 300 成分 | 回测中 |
| strat-002 | 纳指 EMA60 通道 | 趋势跟踪 | NQ100 ETF (QQQ) | 实盘观察 |
| strat-003 | 恒生 AH 折溢价回归 | 均值回归 | AH 同时上市股票 | 调研中 |

## 文件命名规范

- `strat-XXX-name.json` — 策略骨架
- `strat-XXX-name.params.json` — 参数
- `strat-XXX-name.backtest.md` — 回测报告
- `strat-XXX-name.live.md` — 实盘跟踪
