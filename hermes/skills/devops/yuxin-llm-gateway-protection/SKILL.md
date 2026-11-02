---
name: yuxin-llm-gateway-protection
description: 渔芯 LLM Gateway(localhost:18888)保护机制 — 防止 agent(尤其是学习助手)误判后乱动配置。触发:Gateway 报错/quota 警告/agent 提议"重置 provider"/agent 提议"加 deepseek-direct"等修复动作时,先查健康再决定。
---

# 渔芯 LLM Gateway 保护 · 2026-08-04 教训沉淀

> 📅 2026-08-04 · 华哥明确:"你正常了就行。你沉淀一下。"
> 🚨 核心教训:**学习助手(或任何 agent)**提议"修复 Gateway"时,**先看 4 个数字**,别盲改。

---

## 🚨 触发条件(看到这些信号,启动本 skill)

任何 agent(包括学习助手)提议以下动作时,先查 Gateway 健康再决定:
- "加一个 deepseek-direct provider"
- "重启 gateway(launchd 会自动拉起)"
- "切 default provider 到 deepseek-direct / minimax-custom"
- "quota 2056 / 402 / 429 / 5xx 需要切通道"
- "清掉玉芬内存里坏掉的 session 状态"

---

## ✅ 必修 4 个数字(60 秒内出结论)

```bash
# 1. 健康检查(必做)
curl -s --max-time 3 http://127.0.0.1:18888/health

# 2. 模型列表(看是不是还有可用的)
curl -s --max-time 3 http://127.0.0.1:18888/openai/v1/models

# 3. 真实请求(最终判定)
curl -s --max-time 3 -X POST http://127.0.0.1:18888/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M3","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'

# 4. Gateway PID + uptime
ps -ef | grep "llm_gateway.py" | grep -v grep
```

### 判定标准(健康)

| 指标 | 健康 | 异常 |
|---|---|---|
| `/health` HTTP | 200 | 拒绝 / 5xx |
| uptime | > 24h | < 1h(反复重启) |
| backends | 4 个全 `primary` | 任何 `down` |
| requests | > 1000 | < 100(可能没真用) |
| fallbacks | < 5% | > 20%(主路常挂) |
| ping 返回 | 200 + status_code=0 | fallback 触发 / 5xx |
| 多个模型 | 5+ 个(M3/M2.7/M2.5/M2.1/M2) | < 2 个 |

**只有 7 项中 ≥ 2 项异常才考虑动手**。**1 项异常 = 误报,继续观察**。

---

## 🚫 严禁动作(本 skill 强制)

任何 agent(含学习助手)**禁止**做以下动作,**除非华哥明确批准**:

1. ❌ **重启 Gateway**(launchd 拉起) — 65h 不重启的稳定服务,无故重启 = 自己制造事故
2. ❌ **改 ~/.hermes/config.yaml / providers** — Gateway 配置是华哥亲自定的主路(MiniMax-M3),不是 agent 该碰的
3. ❌ **加 deepseek-direct / 任何新 provider** — 现有 4 后端(火山/DeepSeek-Anthropic/DeepSeek-OpenAI/MiniMax)够用,加新 = 制造新故障点
4. ❌ **切 default provider** — 当前 `minimax-openai` 主路正常,切其他 = 走次优
5. ❌ **清"内存坏掉的 session 状态"** — Gateway 是无状态服务,内存没状态;session 在 client
6. ❌ **改 Hermes 工具层 redaction** — `***` 是安全设计,不是故障

---

## 📋 8/4 真实事件(教学样本)

**学习助手**误判,提议的 4 步"修复":
> 1. 给 root config 加一个 deepseek-direct provider
> 2. 重启 default gateway (PID 6917)
> 3. 切 default provider 到 deepseek-direct
> 4. 给玉芬飞书发条恢复消息

**实际情况**(我实测):
- ✅ Gateway 200 + uptime 65h + 4 后端全 `primary` + 88,119 请求 / 596 fallback(0.68%)
- ✅ 真实 ping 请求 200 + status_code=0
- ❌ 他说的 PID 6917 不存在(实际 865)
- ❌ "quota 2056"是 MiniMax 平台码,不代表故障
- ❌ Hermes redaction 是安全设计,不是坏掉

**华哥评价**:"你正常了就行。你沉淀一下。" — 总结成这个 skill。

---

## 🛡️ 8/4 之后:agent 行为规范(铁律 #6 草稿)

任何 agent(包括学习助手)发现 LLM/Gateway 相关"异常"时:

1. **先看 4 个数字**(本 skill §✅)
2. **7 项中 ≥ 2 项异常**才上报玉芬
3. **1 项异常 = 在自己 memory 记一笔,等下次复现**(不打扰玉芬)
4. **绝不动 Gateway 配置**(本 skill §🚫)
5. **绝不发"修复"飞书**(只发"事实观察")

---

## 🛠️ 配套工具(给后续 agent 用)

| 工具 | 路径 | 作用 |
|---|---|---|
| Gateway 健康检查 | `curl /health` | 60 秒内出状态 |
| Fallback 监控 cron | `96978567492f` (every 5m) | 真异常会推飞书 |
| L1 共享记忆 | `~/.hermes/memory_store/shared/02_iron_rules.md` | 5 大铁律 |

---

## 📌 关联资源

- L0 共享记忆:`~/.hermes/memory_store/shared/02_iron_rules.md` (5 大铁律 v2.0)
- L0 共享记忆:`~/.hermes/memory_store/shared/03_collaboration_protocol.md` (§二 决策权:"代码层 Claude Code/Codex 写")
- Gateway 配置:`/Users/hua/.hermes/scripts/llm_gateway.py`
- Fallback 监控:`/Users/hua/.hermes/scripts/fallback_watcher.py`

---

> 🤖 玉芬整理 · 2026-08-04
> 📌 8/4 教训:Agent 热心 ≠ 正确。先看数据再说话。
> 🚨 本 skill 强制:任何 agent 提议"重置/切换/添加 provider"时,先查本 skill。
