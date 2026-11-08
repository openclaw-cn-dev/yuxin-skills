---
name: hermes-gateway-profile-ops
description: 每小时部下巡检/gateway 在线检测必读——第一步先读 references/gateway-online-detection.md，全正常回 [SILENT]。Hermes 多 Profile 的 gateway 运维 + LLM Gateway (port 18888) 全链路运维。Profile 侧：启动/停止/重启、配置诊断（LLM provider、env、cron）、飞书连通验证、健康检查、quota 限速应对。Gateway 侧：Codex CLI SSE 翻译、502/429/401 故障排查、Provider 切换、Responses API 兼容性。触发条件：同事 agent 报告"不能工作"、"找不到 provider"、gateway 进程异常、配置漂移、用户要求"启用/停用/恢复"某个 profile、Codex 挂了、Gateway 502 坏网关、豆包 DeepSeek 模型不匹配、18888 端口不通、玉芬每小时 cron 巡检、**玉芬每日工作状态巡检（zhenglishi 5 项健康检查）→ 加载 references/yufen-daily-health-patrol.md**、学习助手(zhenglishi)汇报玉芬健康、minimax key 前缀校验、cron jobs.json last_status=error 巡检、**msg GW 某个 profile launchctl 缺失（launchctl list 无条目）→ 先读 references/***SECRET***.md（区分 plist 从未创建 vs 未加载；补建用 load -w 不用 bootstrap，bootstrap 报错 5）**、**网关为什么重启/关闭/被顶替（重启取证）→ 先读 references/gateway-restart-forensics.md（2026-09-26 10:15 实录：ai.hermes.gateway legacy 与 ai.hermes.gateway-default 双服务并存，巡检 kickstart legacy 触发 --replace 顶替风暴；legacy label 常驻 not running 是正常态）**。
triggers:
  - hermes gateway start/stop/restart
  - profile 不能工作
  - No inference provider configured
  - Provider authentication failed
  - 量化部-宽博士
  - 同事 agent 网关
  - gateway_state.json
  - MINIMAX_CN_API_KEY
  - launchd hermes-gateway
  - quota 429 限速
  - 启用某 profile
  - X 不回了 / X 不回复
  - RKR 资源保障
  - 同事 gateway 全消失
  - HTTP 402 insufficient balance
  - minimax 欠费
  - 关停/保留 3 个 gateway
  - bootstrap 5: Input/ou
  - 重启循环/反复 Starting/收到网关关闭通知 → 先读 references/restart-loop-classification.md 鉴别自愈 vs 故障tput error
  - port 18888
  - 巡检 gateway 在线检测（用 launchctl list，勿用 ps grep gateway run；见 references/gateway-online-detection.md）
  - 玉芬每日工作状态巡检 / 学习助手巡检玉芬 / zhenglishi 5 项健康检查（gateway/model/errors/api-key/cron 5 项；区分近期失败 vs 长期 stale；只读不擅改；含 MINIMAX_CN_API_KEY 前缀陷阱 + jobs.json 分类脚本 + 5 同事 cron 顺手验证；见 references/yufen-daily-health-patrol.md）
  - Codex 不工作 / Codex 挂了
  - 502 Bad Gateway
  - 改玉芬模型 / 切 default 模型 / 玉芬用哪个大模型
  - 又重启了 / 模型被改回来 / 玉芬改死了
  - model_rotation_daemon / com.yuxin.model-rotation
  - 玉芬模型配置三大坑（--profile default、自动轮换守护进程、minimax provider 切错）见 references/***SECRET***.md
  - 设置/核验同事模型（改模型 = 改 config.yaml 顶层 model+provider + profile .env 的 key；见 references/***SECRET***.md）
  - $HOME 被 profile 镜像劫持（echo $HOME 返回 profiles/<名>/home，须用绝对路径）
  - llm_gateway.py
  - Responses API
  - SSE 事件翻译
  - 豆包模型不匹配
  - DeepSeek input_tokens 缺失
  - codex plugin add / remove
  - 不能识别图片
  - vision
  - 图片识别
  - 看图
  - 读图
---

# Hermes Gateway Profile 运维

Hermes 每个 profile（maodou/laomo/xiaobao/heidou/afu/zhenglishi/quant/default 等）有独立 `config.yaml` + `.env` + `gateway_state.json` + cron jobs + 飞书 channel。本 skill 管 **profile 的启动 / 配置诊断 / 飞书连通 / LLM provider 健康**。任务派发、agent 监督、task 调度 → 那是 `agent-overseer` 的事。

> **本 umbrella 吸收了五个姊妹 skill（已归档到 references/）**：
> - `references/hermes-batch-cron-patterns.md` — 设计/运行批量 cron 任务（避免 LLM 假执行、跨天持久化状态、长任务可靠性）。
> - `references/hermes-profile-llm-routing.md` — Hermes profile 的 LLM provider/key 接线诊断（404、429、No inference provider 错误、MINIMAX_CN_API_KEY 与 custom_providers 冲突）。
> - `references/cron-inspection-pitfalls.md` — **玉芬每小时 cron 巡检实测踩坑**：launchctl 而非 ps aux 当权威、`curl|python3` 被 tirith 拦截、`execute_code` 在 cron 拒跑、bootstrap exit 5 = 已运行、非授权 profile 永不 bootstrap。
> - `llm-gateway` — LLM Gateway (port 18888) 架构与路由配置。
> - `codex-gateway` — Codex CLI 通过 Gateway 的 SSE 翻译与运维。
> - `codex-gateway-ops` — Gateway 502/429/401 故障排查与 Provider 切换。
>
> 多数 gateway 故障先看本 skill，再按需下沉到上述 references。
- `references/multi-model-smart-routing.md` — 2026-08-06 多模型智能路由集成实录

---

## 核心原则（华哥 2026-06-26 明确）

1. **简洁 + 直接修**：用户说"修好就行了" = 先做 A/B 对比找根因，再动手术，不要长篇分析占用户时间。
2. **基于事实下结论**：gateway "能跑" ≠ 配置对。要看 ps + lsof + 日志，不要凭"感觉跑得顺"。
3. **AIAgent 直调 ≠ gateway 路径**：CLI/`AIAgent(...)` 直调会走错误的 base_url（404），**真正判断 provider 工作必须看 gateway 日志**。

---

## 关键架构事实（2026-06-26 验证）

### Profile 隔离
每个 `~/.hermes/profiles/<name>/` 是完全独立的运行环境：
- `config.yaml` — 模型/provider/toolsets 配置
- `.env` — API key + 飞书凭证（敏感文件不能 read_file）
- `gateway_state.json` — pid/state/platforms[feishu].state
- `gateway.pid` — 启动时记录的 pid（被 `--replace` 替换）
- `cron/jobs.json` — cron 任务定义
- `logs/gateway.log` + `logs/gateway.error.log`
- `sessions/` — 历史会话

### LLM Provider 路由（最常踩坑）
**`MINIMAX_CN_API_KEY` 必须在 `.env` 里**，hermes-agent 内部从 env 注入 `minimax-cn` 内置 provider。不要在 `config.yaml` 的 `custom_providers` 里手写 minimax 配置（会跟 env 路由冲突导致 404）。

**`hermes status` 显示 Model+Provider 不代表能跑通** —— 那是静态配置检查；真正的 LLM 调用看 `gateway.log` 里的 `response ready:` 行。

### Gateway 启动方式两种
- **launchd 托管**：`launchctl list | grep hermes` 看到 `ai.hermes.gateway`（默认 profile = default），用 `launchctl unload/load` 管
- **手动启动**：`hermes gateway run --profile <name> --replace`（其他同事 agent 用这种方式，PID 记录到 `~/.hermes/profiles/<name>/gateway.pid`）

**坑**：shell 级 `nohup &` 启动 gateway 会被 Hermes 拦截（用 `terminal(background=true)` 跟踪代替）。

### AIAgent vs Gateway 的 base_url 差异
CLI/AIAgent 直调 `from run_agent import AIAgent; AIAgent(quiet_mode=True)` 构造出来的 `a.base_url` 是 `https://api.minimaxi.com/anthropic`（带 /anthropic 后缀），这个端点 **MiniMax 没开放 404**。但 gateway 路径内部有 model catalog 解析层，能正确路由到 `/v1/chat/completions`。

**实战含义**：用 CLI 测 provider → **永远 404**，不要因此误判配置错。要测就发飞书消息看 `gateway.log` 的 `response ready:`。

---

## 标准操作流程

### 0. 快速侦察（最重要 — 30 秒内搞清楚现状）

**🚨 巡检 cron 的 prompt 本身还在用「naive 命令」——不要照抄**（2026-08-14 每小时巡检确认）：任务文本里仍写着 `curl -s .../health | python3 -m json.tool` 和 `ps aux | grep "gateway run"` 两条已知陷阱命令。前者触发 tirith `pending_approval`（cron 无人审批 → 卡死，本 session 实测第一步就卡住），后者返回空（wrapper 进程 COMM 是 `hermes`，grep 漏报 → 假警报）。**正确做法**：① LLM Gateway 健康用**裸 `curl -s http://127.0.0.1:18888/health`（不接 pipe）**，直接返回 JSON；② profile 在线判定用 **`launchctl list | grep ai.hermes.gateway`** 一条命令拿全量 PID+status。看到 prompt 里的 naive 命令时，静默替换成本 skill 的权威命令，不要逐字执行。

**🚨 CRON 巡检铁律（2026-08-10 第 5 次实战确认）：永远先做 launchctl print，再做 ps aux，绝不要反过来。**

`ps aux | grep "gateway run"` 只能看到手动启动的 gateway（default + community 的 Python 命令行），**看不到 launchd wrapper 启动的 6-7 个 gateway**（进程名显示为 `hermes`）。如果你先跑 ps、发现只命中 2-3/9、然后去修 → 你正在修一个不存在的问题，还有概率引入新故障（bootout→bootstrap 时序竞争、kickstart -kp 杀正常进程）。

**正确顺序（不可颠倒）**：
1. **先跑 `launchctl print` 循环**（下方"金标准诊断"的 Step 1）→ 这是唯一权威来源

**⭐ 最快的权威单源（2026-08-14 巡检确认）**：判断「哪些 profile gateway 在线」时，`launchctl list | grep ai.hermes.gateway` **一条命令**即可拿到每个 profile 的 PID + exit status 表（比 `launchctl print` 逐 profile 循环更快）。**注意 PID 列含义随启动模式而异**：wrapper 模式的 profile 显示 **wrapper 的 PID**（`gateway_launchd_wrapper.sh`，其 hermes 子进程 PID≈wrapper+1 但需 `ps -o ppid=` 确认）；直接 Python plist 的 profile（如 zhenglishi）显示 **hermes daemon 本身的 PID**（`ps -o pid,ppid,command` 看 PPID=1 + command=`hermes`）。**两种都算在线**，不要因 PID 指向的不是 wrapper 就误判 down。
2. 如果 launchctl 显示 9/9 `state=running` → **巡检结束，报告正常。不要跑 ps，不要读日志。**
3. 仅当 launchctl 显示某个 profile `state != running` → 才进入修复流程（§7/§8）
4. `ps aux` 仅用于"launchctl 说有问题时"辅助验证 PID，不作为独立判断依据

**⚠️ 进程名截断陷阱**（2026-08-09 两次实战 + 2026-08-10 第五次）：通过 `gateway_launchd_wrapper.sh` 启动的 gateway 进程在 ps 中显示为 **`hermes`**（不是完整的 Python 命令行），`grep "gateway run"` 或 `grep "hermes.*--profile"` 会漏报。**必须用 `launchctl print` + 全量 ps 双源对照**才能准确判断。

**⭐ 首选诊断命令**（2026-08-09 三次 + 2026-08-10 第五次实战确认）：当需要快速判断所有 9 个 profile gateway 状态时，**直接用 `hermes gateway status`**（不带 `--profile`），它一次性列出所有 profile 的 PID 和运行状态，是 multi-profile 巡检的**权威单源**。比 `launchctl print` 逐个查 + `ps aux` 手动对更快、更不易出错。注意：`hermes --profile X gateway status`（带 `--profile`）会返回 default 的 PID（misleading），不要用这个变体。

**🚨 假警报应对铁律**（2026-08-09 三次 + 2026-08-10 第五次实战确认）：当 `launchctl print` 显示 `state=running` 但 ps grep 找不到进程时，**信任 launchctl，不执行任何修复**。五次 hourly 巡检中，9/9 launchctl 全显示 running，但 grep "gateway run" 仅命中 1-3/9 → 触发不必要修复链（kickstart→bootout→bootstrap→load）→ 最终验证确认 9/9 始终健康。**假警报下的修复链有引入新故障的风险**。尤其是 `kickstart -kp`（kill + restart）——对健康进程是破坏性的，不应在"我觉得可能有问题"时使用。🆕 2026-08-10：第 5 次假警报中 7 profile 的 plist 文件确实缺失（进程存活但无 launchd 备份），重建 plist 有益但非紧急。详见 `references/***SECRET***.md`。

**🚨 旧错误日志陷阱**（2026-08-09 第三次实战识别）：当 gateway 处于 zombie 状态后恢复时，`gateway-launchd.error.log` 中仍保留恢复前的旧错误（如 MiniMax 429 Token Plan 耗尽、LLM Gateway 504 超时、missing skill、SIGTERM shutdown）。读取这些日志做根因诊断会误判为"当前故障"，触发不必要的修复和告警。**正确做法**：① 先以 `launchctl print` 判定 state；② state=running → 跳过日志诊断，不读旧错误；③ state 非 running → 才读最新错误日志（`tail -5` 而非 `tail -10`，只看最近 2 分钟内的行）。

```bash
# ═══════════════════════════════════════════════════
# CRON 巡检 — 正确执行顺序（不可颠倒）
# ═══════════════════════════════════════════════════

# Step 0: LLM Gateway (port 18888) 健康 — 首选裸 `curl -s`（不接 pipe），2026-08-15 实测不触发 scanner
#   只有 `curl | python3`（pipe 到解释器）才被 tirith 拦成 pending_approval（cron 无人审批 → 卡死）。
#   裸 curl 直接返回 JSON。下方 urllib 作兜底（极端情况下裸 curl 也被拦时用）。
curl -s --max-time 5 http://127.0.0.1:18888/health
python3 -c "
import urllib.request, json
try:
    r = urllib.request.urlopen('http://127.0.0.1:18888/health', timeout=5)
    data = json.loads(r.read())
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f'LLM Gateway DOWN: {e}')
"

# Step 1: launchctl 状态（最权威 — 先跑这个，它说了算）
# ⚠️ 列表必须匹配华哥当前授权（不固定 9 个），例：2026-08-11 授权 default zhenglishi quant
MYUID=$(id -u)
ALL_RUNNING=true
# 将下方列表替换为华哥当前授权的 profile
for p in default zhenglishi quant; do
  # 🆕 2026-08-14：default 的 launchd label 也是 `ai.hermes.gateway-default`（与其它 profile 同格式，plist 文件同名），
  # 不是 `ai.hermes.gateway`。所有 profile（含 default）统一用 `ai.hermes.gateway-$p`，不要给 default 做 `ai.hermes.gateway` 特判。
  lbl="ai.hermes.gateway-$p"
  state=$(launchctl print "gui/$MYUID/$lbl" 2>/dev/null | grep "state =" | head -1 | awk '{print $3}')
  if [ "$state" != "running" ]; then ALL_RUNNING=false; fi
  echo "$p: ${state:-not loaded}"
done

# 🚨 关键判断点：
# ⚠️ 期望列表必须匹配华哥当前授权（不一定是 9 个）。华哥可能随时缩小授权范围释放资源。
# 例：华哥 2026-08-11 明确只授权 default/zhenglishi/quant 共 3 个 gateway。
# 每次巡检前确认授权名单，不要用硬编码的全量列表。
EXPECTED_COUNT=<授权数量>  # 不是固定的 9！
if $ALL_RUNNING; then
  echo "✅ $EXPECTED_COUNT/$EXPECTED_COUNT launchctl 全部 running — 巡检结束，跳过 Step 2-3。"
  # ⛔ 不要跑 ps aux！不要读日志！不要 kickstart！
  # ⛔ 如果 default 是手动启动的（launchctl 显示 not loaded 但 ps 能找到），也算健康。
  exit 0
fi

# 🆕 2026-08-11 空壳 wrapper 检测：launchctl running 但 Python 子进程可能已死
# launchctl 显示 running 后，快速验证 wrapper 是否有活着的 Python 子进程：
#   for p in ...; do
#     wrapper_pid=$(pgrep -f "gateway_launchd_wrapper.sh $p" | head -1)
#     if [ -n "$wrapper_pid" ]; then
#       children=$(pgrep -P $wrapper_pid 2>/dev/null)
#       [ -z "$children" ] && echo "⚠️ $p: 空壳 wrapper — Python 子进程已死" && ALL_RUNNING=false
#     fi
#   done
# 仅在检测到空壳 wrapper 时才进入修复流程（绕过 launchd 直接启动）。

# 🆕 2026-08-14 `pgrep -P` 假阴性陷阱：`pgrep -P <wrapper>` 返回空 ≠ 子进程死了
# 实测：wrapper 69237(default) 的活子进程 69239(hermes) 明明在跑（CPU 103min、stat 在 S/U 间），
# 但 `pgrep -P 69237` 返回空 → 误判「空壳 wrapper → default down」→ 差点对 default 错误 bootstrap。
# 正解：判定「空壳 wrapper / 子进程是否存活」必须用 `ps -o ppid=` 对照全量进程列表，不要单信 `pgrep -P`：
#   ps aux | grep -i hermes | grep -v grep   # 先拿全量 hermes 进程 + PID
#   ps -o pid=,ppid=,stat=,command= -p <candidate_pid>   # 再逐个确认 ppid 是否指向 wrapper
# 子进程 PID 只是「靠近」wrapper PID（实测 +2~+14 不等，非固定 +1），必须用 `ps -o ppid=` 确认，不能靠 PID 差值猜。
# ⭐ 一击定案（2026-08-14 巡检再确认）：`ps -axo pid,ppid,stat,etime,command | grep -i hermes`
#   一条命令输出完整 wrapper→hermes 子进程树（ppid 列直接指向对应 wrapper 的 PID），
#   一次看清「哪个 wrapper 有活子进程、哪个是空壳」，无需逐个 `pgrep -P` 或 `ps -o ppid=` 猜测。
#   实测：wrapper 798(default) 的 `pgrep -P 798` 返回空，但该命令显示 821 ppid=798 仍在跑 → 假阴性瞬间消解。

# 🆕 2026-08-13 「无 wrapper」≠「down」：直接 Python plist 的 profile 会显示 NO WRAPPER，这是正常的
# 授权 profile 中 zhenglishi 走「直接 Python 调用 plist」（无 gateway_launchd_wrapper.sh，进程 PPID=1，command 就是 hermes），
# 而 default/quant/afu/heidou/laomo/maodou/xiaobao 走 wrapper（bash wrapper → 子进程 hermes）。
# 上面「空壳 wrapper 检测」循环对 zhenglishi 会输出 "NO WRAPPER"——不要据此误判 zhenglishi down。
# 判定「是否有 wrapper」永远不能作为「是否在线」的依据；唯一权威是 `launchctl list`（有 PID + status=0 = 在线）。
# 区分两种模式：`ps -o pid,ppid,command -p <pid>` → PPID=1 且 command=hermes = 直接 Python（无 wrapper）；PPID=某 wrapper 的 PID = wrapper 模式。

# 🆕 2026-08-14 「U」stat 状态 ≠ 挂死：直接 Python plist 的 gateway（如 zhenglishi）主循环阻塞在 I/O（飞书 WS / cron scheduler），
# `ps -o stat= -p <pid>` 常显示 "U"（uninterruptible sleep）。这不是 hang——用「日志 mtime 是否近期」判活，不用 "U"：
#   stat -f "%Sm" ~/.hermes/profiles/<name>/logs/gateway.error.log
#   若 mtime 在最近几分钟内 → 进程活跃，别因 "U" 误判 down 触发不必要修复。实测：zhenglishi PID 81307 stat=U 但 error.log 每 1-7 分钟仍在写，属正常。

# 🆕 2026-08-13 批量启动时间戳指纹：非授权 profile 意外在线时的根因定位
# 发现非授权 profile（afu/heidou/laomo/maodou/xiaobao 等）在线、需报告"是否停掉"时，
# 顺手查它们的启动时间，判断是批量拉起还是人工逐个启动：
#   for pid in <在线非授权 profile 的 PID>; do ps -o pid,lstart= -p $pid; done
#   （或 ps -o etime= -p $pid，多个进程的 etime 相同 = 同一批）
# 若多个 profile 的时间戳完全相同（实战：5 个全在 09:06AM 同一刻），
# → 是脚本/agent 批量拉起，不是人工逐个 start。根因候选：
# 🆕 2026-08-15 单个非授权 profile 在线的判定：把它的 lstart 跟**授权 profile 那一批**的 lstart 对比。
#   若显著不同（实战：laomo 16:48 vs 授权三 profile default/quant/zhenglishi 14:49，晚约 2h）→ 排除「同一批
#   full-team-launch」，更可能是被单独/人工拉起，或某 agent 的定向任务残留；若相同/接近 → 优先怀疑批量脚本。
# 🆕 2026-08-15 非授权在线 profile 的 cron 也在空烧：报告「非授权 profile 意外在线」前，顺手 `tail -5` 它的
#   gateway-launchd.error.log，看其 cron 是否反复失败（实战 laomo：`Skill 'laomo-knowledge' not found` +
#   execute_code BLOCKED + 命令 pending_approval 卡死——心跳根本跑不通）。这既佐证「它在线纯属空烧资源」，
#   也强化「建议华哥停掉」的依据；若 cron 全绿则它可能在做实事，报告语气应更审慎（问清是否华哥有意保留）。
# 🆕 2026-08-15 报告里给出的「停掉」命令必须是**完整四步关停**（§6），不能只给 `launchctl bootout`。
#   只 bootout 会因 KeepAlive 在 ~20 分钟内复活（§6 已多次踩坑）——那是「临时暂停」不是「停掉」。
#   要么给 kill wrapper + bootout + disable + rm plist 完整块，要么至少 bootout + disable 两步。
#   实战：本轮巡检报告曾只写 `launchctl bootout gui/$UID/ai.hermes.gateway-laomo` 一条，属不完整建议，会误导华哥以为已停掉、实则 20 分钟内复活。
#   ① 其他 agent 残留的「保障同事在线」任务（见 ***SECRET***.md）
#   ② RKR auto_ops --restore-gateways 批量恢复
#   ③ 过期 cron 的期望列表过宽（见下方「巡检 cron 静默覆盖授权策略」坑）
#   ④ full-team-launch-sop 批量注册（multi-agent-team-architecture/references/full-team-launch-sop.md）
# 时间戳相同 = 排除人工启动，把排查方向直接指向脚本/任务/agent，省掉逐个 profile 查。
# ⭐ 完整「谁拉起了这个 profile」五步反查法（含 plist mtime 指纹 + 交叉比对 SOP/cron 输出）见
#   references/***SECRET***.md（2026-08-14 实战：5 非授权 profile 被 full-team-launch-sop 批量注册成 launchd 自启）

# 🆕 2026-08-10：crash-loop 检测（state=running 但 last exit code != (never exited)）
# 当 launchctl 显示 running 但 last exit code = 1（非 never exited）时，
# 是 crash-loop 而非假警报 → 进入修复流程 §7/§8，优先试 plist wrapper 迁移
# 🆕 如果所有 launchctl bootstrap 都成功但进程 5 秒内消失 → 可能是 launchd SIGTERM 问题
# 详见 references/***SECRET***.md
for p in ...; do
  last_exit=$(launchctl print "gui/$MYUID/$lbl" 2>/dev/null | grep "last exit code")
  if echo "$last_exit" | grep -qv "never exited"; then
    echo "⚠️ $p: crash-loop detected (last exit code ≠ never exited)"
    ALL_RUNNING=false
  fi
done

# Step 2（仅在 launchctl 发现异常时才跑）: 全量 ps 辅助验证
echo "=== launchctl 发现异常，ps 辅助验证 ==="
ps aux | grep -i hermes | grep -v grep | grep -v pyright | grep -v model_rotation | grep -v snap | grep -v bash | awk '{print $2, $11, $12, $13, $14, $15, $16}'

# Step 3: 对 launchctl 显示非 running 的 profile 进入修复流程
# （不要对 launchctl 显示 running 的 profile 做任何操作！）

# ═══════════════════════════════════════════════════
# 🆕 修复后验证铁律（2026-08-11 第 6 次实战）
# ═══════════════════════════════════════════════════
# ❌ 禁止：修复后用 `ps aux | grep "gateway run"` 验证 — wrapper 启动的进程
#         COMM 显示为 "hermes"，grep 永远漏报。会触发假警报 → 不必要二次修复。
# ✅ 正确验证三步（按顺序）：
#
# 1. launchctl list（看 label + PID）：
#    launchctl list | grep ai.hermes.gateway
#    期望：9 行，每行有 PID（不是 "-"）且 status=0
#
# 2. 等 5-8 秒让 python 子进程启动，然后验证 wrapper 有活子进程：
#    for pid in $(pgrep -f gateway_launchd_wrapper); do
#      child=$(pgrep -P $pid | head -1)
#      profile=$(ps -o args= -p $pid | grep -oP 'gateway_launchd_wrapper\.sh \K\S+')
#      [ -n "$child" ] && echo "✅ $profile (wrapper=$pid → child=$child)" || echo "⚠️ $profile: 空壳 wrapper"
#    done
#
# 3. 如果某个 profile 的 wrapper 无子进程 → 绕过 launchd 直接启动：
#    terminal(background=true, notify_on_complete=true):
#      python -m hermes_cli.main gateway run --replace --profile <name>
#
# 🚨 常见误判：步骤 2 的 pgrep -P 找不到子进程 ≠ 进程死了。
#    新启动的 gateway 需要 5-10 秒初始化（import hermes + 连接飞书 WS），
#    python 子进程可能还没 spawn 出来。等 10 秒再查。
```

### 1. 修复"找不到 provider"（最常见 case）

**症状**：飞书 / CLI 报 `No inference provider configured. Run 'hermes model' to choose a provider`

**根因**：`~/.hermes/profiles/<name>/.env` 缺 `MINIMAX_CN_API_KEY`

**修复**（3 步）：
```bash
# 1. 从 default .env 同步 key
grep "^MINIMAX_CN_API_KEY=*** /Users/hua/.hermes/.env >> /Users/hua/.hermes/profiles/<name>/.env

# 2. 重启该 profile 的 gateway
kill -TERM $(cat /Users/hua/.hermes/profiles/<name>/gateway.pid 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['pid'])")
sleep 4
hermes gateway run --profile <name> --replace &
sleep 10  # 等飞书 connected

# 3. 验证
cat ~/.hermes/profiles/<name>/gateway_state.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'pid={d[\"pid\"]} state={d[\"gateway_state\"]} feishu={d[\"platforms\"][\"feishu\"][\"state\"]}')"
```

**关键**：不要在 `config.yaml` 里加 `custom_providers: [{api_key: ..., base_url: ...}]` 段 — 会跟 env 的内置 provider 路由冲突报 404。

### 1b. 修复"不能识别图片 / vision 不可用"

**症状**：用户在飞书发图片给 agent，agent 无法识别/处理图片内容。

**三层诊断法（按顺序，30秒定位根因）**：

```bash
# 一步诊断（替换 <name> 为 profile 名）
python3 -c "
import yaml
with open('/Users/hua/.hermes/profiles/<name>/config.yaml') as f:
    d = yaml.safe_load(f)
toolsets = d.get('toolsets') or []
print(f'Provider: {d.get(\"provider\")}')
print(f'Model: {d.get(\"model\")}')
print(f'Toolsets: {toolsets}')
print(f'vision tool: {\"vision\" in toolsets}')
# deepseek-direct → 直连纯文本，不支持 vision
# deepseek-cn → 走 Gateway，自动路由到多模态模型
"
```

**常见组合与修复**：

| 症状 | 根因 | 修复 |
|------|------|------|
| toolsets 无 vision | 工具未启用 | `hermes --profile <name> config set toolsets '[vision]'` |
| provider = deepseek-direct | 直连纯文本模型 DeepSeek V4 Pro | `hermes --profile <name> config set provider deepseek-cn` |
| 两个问题叠加 | toolsets 空 + 直连纯文本 | 两步都修（先改 provider，再加 toolsets） |

**修复后必须**：`launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<name>` 重启 gateway。
**注意**：`kickstart -k` 对 fragile profile 有杀伤力（见已知坑表），重启后等 5-8 秒让 gateway 初始化。

**原理**：
- `deepseek-direct` → `https://api.deepseek.com/v1` — DeepSeek V4 Pro 不支持多模态图片输入
- `deepseek-cn` → `http://127.0.0.1:18888/openai/v1` — LLM Gateway 智能路由，自动将 vision 请求分发到支持多模态的后端
- `vision` toolset 启用后，Hermes 将图片数据注入 LLM 请求，由 Gateway 做模型选择

具体修复案例见 `references/***SECRET***.md`。

**⚠️ 2026-08-13 结论：`deepseek-cn`（Gateway 智能路由）对 vision 的自动分发实际不可靠**——8/12 曾把 quant 从 `deepseek-direct` 改成 `deepseek-cn`，期望 Gateway 自动把图片请求分发到 minimax/gemini 等多模态后端，但华哥 8/13 反馈"还是没有图形处理能力"，最终**直接切 `minimax-cn` + `MiniMax-M3`（原生多模态）**才解决。教训：需要图片识别的 profile，**首选直接换多模态原生模型**，不要依赖 Gateway 智能路由的 vision 分发（理论上支持，实际不稳定）。切换只需改 config.yaml 顶层 `model: MiniMax-M3` + `provider: minimax-cn`（minimax-cn 是内置 provider，从 `.env` 的 `MINIMAX_CN_API_KEY` 注入，无需在 providers 段显式定义），然后 `launchctl kickstart`（纯 kickstart，不带 `-k`，避免 fragile profile 收到 SIGTERM）重启。

### 2. 健康检查（"同事们都正常工作吗"）

```bash
# 完整体检脚本
/Users/hua/.hermes/hermes-agent/venv/bin/python << 'PY'
import os, json, subprocess
profiles = ['maodou','laomo','xiaobao','heidou','afu','zhenglishi','quant']
ps_out = subprocess.run(['ps','auxww'], capture_output=True, text=True).stdout
running = set()
for line in ps_out.split('\n'):
    if 'hermes' in line and '--profile' in line and 'gateway run' in line:
        tok = line.split('--profile',1)[1].split()[0].strip("'")
        running.add(tok)
print(f"运行中的 profiles: {sorted(running)}\n")
print(f"{'profile':<12} {'proc':<5} {'.env':<5} {'key':<5} {'ws':<4} {'cron':<5}")
for p in profiles:
    env_f = f'/Users/hua/.hermes/profiles/{p}/.env'
    has_key = False
    if os.path.exists(env_f):
        with open(env_f) as f:
            for l in f:
                if l.startswith('MINIMAX_CN_API_KEY='): has_key = True
    cron_n = 0
    cjf = f'/Users/hua/.hermes/profiles/{p}/cron/jobs.json'
    if os.path.exists(cjf):
        with open(cjf) as f:
            cron_n = sum(1 for j in json.load(f).get('jobs',[]) if j.get('enabled',True))
    print(f"{p:<12} {'✓' if p in running else '✗':<5} {'✓' if os.path.exists(env_f) else '✗':<5} {'✓' if has_key else '✗':<5} {'?':<4} {cron_n:<5}")
PY
```

### 3. 停某个 profile（释放资源）

```bash
# 手动启动的（同事 agent）
kill -TERM $(cat /Users/hua/.hermes/profiles/<name>/gateway.pid | python3 -c "import json,sys; print(json.load(sys.stdin)['pid'])")
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-default.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-zhenglishi.plistt.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-zhenglishi.plist
sleep 4 && ps aux | grep "hermes.*--profile <name>" | grep -v grep
```

**注意**：单纯 `kill` 对 launchd 管理的服务无效 — 必须 `unload + disable + kill` 三步走（详见 `openclaw-launchd-macos` skill）。

### 4. 应对 MiniMax Token Plan quota 限速

**症状**：gateway.log 里反复 `HTTP 429: 已达到 Token Plan 用量上限`
**根因**：包月套餐配额耗尽（不是 token 余额 — Token Plan 无"余额"概念）
**判断"是否真限速"**：看最近 30 分钟的 `response ready:` 行 — 有成功响应 = 限速但能用，全 429 = 真用完

**解决路径**：
- A. 用户升级 Token Plan（最快）
- B. 临时切 DeepSeek / Anthropic（.env 里换 API key + config.yaml 改 provider）
- C. 减并发 — pause 部分 profile 的 cron jobs（`hermes cron pause <job_id>`）

**不要自己换 provider** — 这是用户决策，给方案让用户选。

### 5. HTTP 402 `insufficient_balance_error (1008)` — 余额不足（**不是** 429 quota）

**症状**（2026-06-29 实战）：quant gateway 多个调用失败，日志报：
```
HTTP 402: insufficient balance (1008)
ERROR agent.conversation_loop: Non-retryable client error: Error code: 402 -
  {'type': 'error', 'error': {'type': 'insufficient_balance_error', 'message': 'insufficient balance (1008)'}}
```
**根因**：minimax-cn 账户**欠费**（不是 Token Plan 配额耗尽）。`1008` 是 minimax 的业务 code。

**与 429 的区别**：
| 现象 | 含义 | 解法 |
|---|---|---|
| `HTTP 429` | Token Plan 用量上限 | 升级 Token Plan / 减并发 / 换模型 |
| `HTTP 402 (1008)` | 账户欠费 / 余额为 0 | 用户去 minimax 后台**充值**，技术侧无法绕过 |

**注意**：`402` 是 `Non-retryable` — 重试 3 次照样挂。**不要在 profile 侧改任何配置**，技术侧唯一能做的就是等用户充值后**重启 gateway 重新加载凭据 + 重发挂起消息**。

**坑**：误把 402 当 429 quota 限流会让用户浪费时间调并发配比，**先看 error code 数字再判断**。

### 5b. minimax API key 两种账户体系 — `sk-cp-` 订阅 vs `sk-api-` 按量（2026-06-30 实战）

**两个账户体系的 key 前缀区分**：
| Key 前缀 | 账户类型 | 额度机制 | 标识来源 |
|---|---|---|---|
| `sk-cp-`（125 字符） | **包月订阅** (TokenPlanMax / 类似) | 折扣包月 + 月度 ~18 亿 token + 并发 4-5 Agent | minimax plan 页订阅 key |
| `sk-api-` / `sk-api-v2-`（126 字符） | **按量付费** | token 计费，账户余额扣完即停 | 通用 API key 页面 |

**关键事实**：
- **两个池的额度不互通** — 订阅 key 用尽不会拖累按量余额，反之亦然
- **同一个 `MINIMAX_CN_API_KEY` 变量可以放任意一种 key**，但**走的是不同账户**
- 用户在 platform.minimaxi.com/console/plan 看到的"订阅 Key"通常是 `sk-cp-` 前缀的订阅 key；用户在 user-center/apikeys 创建的 key 是 `sk-api-` 按量 key

**诊断方法**（**先看 key 前缀再判断**）：
```bash
# 看某个 profile 的 key 属于哪种账户
awk -F= '/^MINIMAX_CN_API_KEY/ {k=$2; print substr(k,1,6)}' ~/.hermes/profiles/<name>/.env
# 输出 "sk-cp-" = 订阅；"sk-api" = 按量

# 看 8 个 profile 的 key 一致性（按 sha256 短前缀）
for prof in default afu heidou laomo maodou quant xiaobao zhenglishi; do
  if [ "$prof" = "default" ]; then
    src="$HOME/.hermes/.env"
  else
    src="$HOME/.hermes/profiles/$prof/.env"
  fi
  if [ -f "$src" ]; then
    sha=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$src" | shasum -a 256 | awk '{print substr($1,1,16)}')
    head=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print substr($2,1,6)}' "$src")
    echo "$prof: head=$head sha256=${sha}..."
  fi
done
```

**踩坑教训**（2026-06-30）：
- 6 同事的 `.env` 全用 `sk-api-v2-` 按量 key → 账户烧光 → **6 同事同时 402**
- default + zhenglishi 用 `sk-cp-` 订阅 key → 仍 200，**救了命**
- 用户在 plan 页看到"包月还有额度" ≠ 按量账户有钱（**两种账户独立**）
- 看到同事报 402 时，**先看 key 前缀**：订阅 key 报的 402 = 订阅池满（升级套餐），按量 key 报的 402 = 按量账户欠费（充值）

**应急方案**（按量 key 烧光但订阅 key 还有）：
1. 用户授权"用 default 的订阅 key 铺到 N 个同事 .env"
| **改 key 一定要配套改 launchd**（见 §9），否则 bot 仍然哑 |
| **`hermes cron pause <id>` 报错 "Job with ID or name '...' not found" — 用错工具了（2026-07-31 实战）** | 同事 gateway 关停时按 §6 应该 pause 该 profile 的 cron 心跳，但 `hermes cron pause <id>` 反复报 not found。**根因**：CLI 接受的 `<id>` 跟 `~/.hermes/profiles/<name>/cron/jobs.json` 里的 id 不是同一个 ID 空间。jobs.json 里的 id 看起来像 MCP `cronjob` 的 12 位 hex 前缀，但**根本对不上**。**正确做法**：用 MCP `cronjob(action='list')` 拿到 52 个 job 的真 id，再用 `cronjob(action='pause')`。 | `jobs.json` 跟 cronjob 系统是两套独立存储 |
| **`jobs.json` 里的 cron 任务根本不在 cronjob 系统里**（2026-07-31 实战） | quant 的 jobs.json 写了 4 个 enabled cron（量化日报、周一提醒、深度调研、持仓监控），zhenglishi 写了 9 个，laomo 2 个，maodou 3 个 — **这些 job 在 cronjob 全局 52 个里一个都没有**！意味着 jobs.json 是过期的本地副本，真正在跑的只有每个 profile 的"心跳 + 自我进化"两个 cronjob。**后果**：§6 配套 pause cron 只能 pause 真在跑的几个，"看起来存在"但实际没跑的 job 无法 pause（因为它们根本没注册到 cronjob 系统）。**诊断方法**：对比 `~/.hermes/profiles/<name>/cron/jobs.json` 跟 `cronjob(action='list')` 返回的 jobs。 | jobs.json 跟 cronjob 系统是两套独立存储 |
3. 注意订阅池有 **4-5 Agent 并发上限**，不要把 7 profile 全铺上去会撞限

### 9. 修 .env 一定要配套修 launchd — 端点 200 ≠ bot 真能回复（2026-06-30 实战教训）

**核心事实**：
- **端点 HTTP 200** = `.env` 里的 key 没问题
- **gateway 进程在跑** = launchd 起得来
- **gateway.log 显示 `feishu connected` / `connected to wss://...`** = WebSocket 已建
- **以上 3 项全 OK ≠ 飞书 bot 能收到消息**

**为什么**：bot 在飞书侧有没有"回执"取决于飞书服务器能不能找到该 bot 进程的 WebSocket 长连接。如果 gateway **刚启动** / 飞书侧认为**超时无回执**，飞书会**默默丢弃消息**，用户看不到回复但日志里也没错误。

**完整验证 SOP**（修完 .env 必跑）：
```bash
# 1. .env key 检查
for prof in <list>; do
  sha=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' ~/.hermes/profiles/$prof/.env | shasum -a 256 | awk '{print substr($1,1,16)}')
  echo "$prof: sha256=${sha}..."
done

# 2. 端点单测（用该 profile .env 里的 key）
for prof in <list>; do
  KEY=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' ~/.hermes/profiles/$prof/.env)
  HTTP=$(curl -sS -o /dev/null -w "%{http_code}" \
    -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
    -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}')
  echo "$prof: HTTP $HTTP"
done

# 3. launchd 状态
launchctl list | grep "ai.hermes" | awk '{print "  PID="$1"  "$3}'

# 4. ⭐ 真正验证 — 飞书发消息端到端测试
#    这一步是人工的，但可以让用户帮忙：让华哥"在飞书里 DM 5 同事的 bot，看 5-15 秒内能不能收到回复"
```

**实战流程**（2026-06-30 15:48-15:54 6 步走）：
1. 改 6 同事 .env（订阅 key）
2. 端点单测 6 同事全 200
3. **没有拉 launchd**（因为 6/29 把同事 gateway 全 bootout 了）
4. 华哥测试 → 报"5 同事没反应"
5. `launchctl load` 5 同事 plist → 全部启动
6. 华哥再测 → 3 同事通了（毛豆/老莫/小宝），2 同事还卡（黑豆/阿福 — gateway 刚连上 WS 还没收到消息）

**教训**：
- **改 .env 永远配套 launchctl**（5 步：①改 .env ②端点单测 ③拉 launchd ④等 WS 连上 ⑤飞书 DM 端到端测）
- 5 同事同时拉 launchd 后**至少等 30 秒**再让用户测，**不要在 15:54 拉起来 15:55 就让用户测**（WS 还没真正握手）
- "3 网关保留"模式下同事 gateway 永远是关的 → 任何 .env 修复对 5 同事**毫无意义**（bot 在飞书侧根本找不到进程接消息）

### 10. `send_message` 工具的 [230002] 限制（华哥测试时的坑）

**症状**：用 `send_message` 工具发消息给某个同事的 home channel，报：
```
Feishu send failed: [230002] Bot/User can NOT be out of the chat.
```

**根因**：当前 session 用的 bot（即 default 玉芬）**不在目标 chat 的成员列表里** — 飞书的 chat 是私有的，没加入就发不进去。

**实战含义**（2026-06-30 15:55）：
- 我想主动发心跳给黑豆/阿福 → 失败（我不在他们的 home channel）
- 玉芬的 home channel 是 `***SECRET***`，和黑豆 `***SECRET***` / 阿福 `***SECRET***` 不是同一个 chat
- **同事之间的 home channel 是隔离的**，要发消息得先在飞书侧把对方加为协作者

**替代方案**（华哥主动测 / 写 L2 记忆 / 改 .env 验证）：
- 让华哥在飞书里 DM bot 测（人类在 chat 里）
- 用 launchctl 日志 / 端点 curl 验证（技术侧）
- 写一个 `cron health check` 推到 default 自己的 home channel（玉芬自己能收）

### 6. 华哥 2026-06-29 明确："同事 gateway 只留 3 个"（M3 限流硬约束）

**华哥 2026-06-29 下达**：
> "保留你、宽博士与学习助手三个的网关就行，其它的关闭，让出资源"
> "minimax-m3会限流，同时只允许开三四个"

**保留名单（华哥钦定）**：
- `ai.hermes.gateway-default` — default（玉芬/华哥助手）
- `ai.hermes.gateway-quant` — 宽博士（量化研究）
- `ai.hermes.gateway-zhenglishi` — 学习助手（整理师）

**关闭名单**：afu / heidou / laomo / maodou / xiaobao（5 个同事 agent gateway）

**操作 SOP**（保留模式 — 🚨 四步缺一不可，否则 20 分钟内自动复活）：

```bash
UID_NUM=$(id -u)

# ⭐ 彻底关闭 = kill 进程 + bootout + disable + 删 plist（四步必须全做）
# 只做 bootout 不 disable + 不删 plist → KeepAlive 会在几分钟内批量拉回所有 gateway

# Step 1: 先杀进程（kill bash wrapper，子进程会自动退出）
# ⚠️ wrapper 模式的进程名是 `gateway_launchd_wrapper.sh $name`，不是 `gateway run --profile $name`。
#   后者只匹配手动启动的 gateway；`pkill -f "gateway run"` 对 wrapper 会静默漏杀（同 §0 的 grep 漏报坑）。
#   权威做法：从 `launchctl list | grep ai.hermes.gateway` 拿 wrapper 的 PID 直接 `kill -9 <pid>`，
#   或两个 pattern 都 pkill 兜底。zhenglishi 无 wrapper（直接 Python），只匹配第二个 pattern。
for name in afu heidou laomo maodou xiaobao community; do
  pkill -f "gateway_launchd_wrapper.sh $name" 2>/dev/null
  pkill -f "gateway run --profile $name" 2>/dev/null
done
sleep 2

# Step 2: 清理僵尸 bash wrapper（ps aux 看残留的 bash -lic 行）
ps aux | grep "gateway run.*--profile" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# Step 3: bootout + disable + 删 plist
for name in afu heidou laomo maodou xiaobao community; do
  launchctl bootout gui/$UID_NUM/ai.hermes.gateway-$name 2>&1
  launchctl disable gui/$UID_NUM/ai.hermes.gateway-$name 2>&1
  rm -f /Users/hua/Library/LaunchAgents/ai.hermes.gateway-$name.plist
done

# Step 4: 清理孤儿 hermes worker（不携带 --profile 标志，需单独处理）
# 这些 worker 的 PPID 是被杀的 gateway bash wrapper，杀 wrapper 后它们可能残留
ps aux | grep "[h]ermes " | grep -v bash | awk '{print $2}' | while read pid; do
  ppid=$(ps -o ppid= -p $pid 2>/dev/null | tr -d ' ')
  # 如果 PPID=1（孤儿）或 PPID 不是已知保留 gateway 的 PID → kill
  if [ "$ppid" = "1" ]; then
    kill -9 $pid 2>/dev/null
  fi
done

# 最终确认
launchctl list | grep -i hermes
# 期望: 3 个 hermes gateway（default + quant + zhenglishi）
ps aux | grep "gateway run" | grep -v grep | wc -l
# 期望: 3
```

**配套要做的**（不配套会浪费 cron 资源）：同事 agent 的 cron 心跳也要 pause，否则 gateway 关了但 cron 还在跑会反复失败：

```bash
# ⚠️ 关键：用 MCP cronjob 工具，不是 heremes cron CLI（CLI 接受 jobs.json 里的 id 但报 not found）
# 正确流程：
# 1. cronjob(action='list') 拿 52 个 job 的真 id
# 2. cronjob(action='pause', job_id=<真 id>) 逐个 pause
# 3. 特别注意：jobs.json 里的很多 cron 任务根本不在 cronjob 系统里（jobs.json 是过期本地副本）
#    实际只能 pause "心跳"和"自我进化"两个 profile-level cronjob
```

**何时启动被关的 gateway**：华哥明确说"启用 X 同事" → 走标准 §0+§1 流程（`enable` + `bootstrap`）。

**注意**：M3 限流是按**实际 LLM 调用并发**算，不是按 gateway 进程数算（gateway idle 时不占额度）。3 个 gateway 平时是 listen 状态，只有 cron/对话触发时才打 M3。但**整点 cron 心跳叠加可能瞬时打到 3-4 并发**，这是真实约束。

### 7. `bootstrap` 报 `5: Input/output error` — plist 仍 `disabled`，**或用 `load` 兜底**

**症状**（2026-06-29 实战）：
```
$ launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.hermes.gateway-laomo.plist
Bootstrap failed: 5: Input/output error
```

**根因**：plist 文件还在 launchd 的 `disabled` 集合里（RKR auto_ops V4 "Agent 资源保障" 触发 bootout 时**同时 disable 了服务**，导致后续 bootstrap 失败）。

**诊断**：
```bash
launchctl print-disabled gui/$UID 2>&1 | grep -i "ai.hermes"
# 期望: 列出当前 disabled 的 hermes gateway（说明 launchd 记着它是关的）
```

**修复顺序 A（标准）— 先 enable 再 bootstrap**：
```bash
UID_NUM=$(id -u)
PLIST=~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist
launchctl enable gui/$UID_NUM/ai.hermes.gateway-<name>   # 先解除 disabled
launchctl bootstrap gui/$UID_NUM "$PLIST"                  # 再启动
sleep 3
launchctl list | grep "ai.hermes.gateway-<name>"            # 确认有 PID
**修复顺序 A（标准）— 先 enable 再 bootstrap**：

**修复顺序 B（2026-08-09 新增，2026-08-11 更新）— 服务已注册但进程不在时，纯 `kickstart`**：
当 `launchctl list` 能看到服务（有 label 但 PID 为空或 stale）但 `ps` 无对应进程时，**优先用纯 `kickstart`（不带 `-k`）**，不需要先 enable（服务未被 disabled）也不需要 bootout→bootstrap（太重）。**2026-08-09 6/6 服务全部一次成功**。

**⚠️ `kickstart -k` 对 fragile profile 的杀伤力（2026-08-11 实战）**：afu profile（使用直接 Python 调用 plist，非 wrapper 模式）在 `kickstart -k` 后正常启动、连接飞书、启动 cron ticker，但 **14 秒后收到 SIGTERM 退出**（gateway.log 显示完整启动→SIGTERM 序列，exit code 1）。改用纯 `kickstart`（不带 `-k`）后 afu 稳定运行。**结论**：对已知脆弱的 profile（直接 Python 调用 plist 的），始终先用纯 `kickstart`；仅当纯 `kickstart` 无效（进程未启动）时才升级到 `kickstart -k`。详见 `references/***SECRET***.md`。
```bash
UID_NUM=$(id -u)
for p in afu heidou laomo maodou xiaobao quant; do
  launchctl kickstart gui/$UID_NUM/ai.hermes.gateway-$p
done
sleep 5
launchctl list | grep ai.hermes  # 验证 PID 已生成
```
**与路径 A 的区别**：路径 A 适用于 `print-disabled` 中能看到 label 的服务（disabled=true），路径 B 适用于 list 中能看到 label 但无 PID 的服务（registered, not disabled, not running）。**与路径 Z 的区别**：路径 Z 适用于 `print` 显示 `state=running` 但 ps 无进程的 zombie，路径 B 适用于更轻的"已注册未运行"状态。

**修复顺序 Z（zombie 状态 — 2026-08-09 两次实战）— `launchctl print` 显示 `state=running` 但 ps 无进程时**：

这是最常见的 gateway 集体死亡后残留状态：进程被 SIGTERM 杀掉但 launchd 缓存未刷新。
```bash
# 三步：bootout（清僵尸）→ 验证已清除 → bootstrap（新起）
launchctl bootout gui/$UID_NUM/ai.hermes.gateway-<name>
# 验证：launchctl print 应返回 "Could not find service"
launchctl bootstrap gui/$UID_NUM "$PLIST"
```

**坑**：`enable` 对 zombie 无意义（zombie 的 disabled 位是 false），`load` 同样报 I/O error。**唯一有效路径是 `bootout → bootstrap`**。

**坑 2**：批量 bootout→bootstrap 时，部分 profile 的 bootstrap 可能报 `5: Input/output error`（launchd 时序竞争）。**重试即可** — `sleep 2` 后再 `bootstrap`，不要重复 bootout。实战（2026-08-09）：6 个 zombie 中 4 个一次成功、2 个（laomo/maodou）需重试。

**坑 3 `gateway.pid` + `gateway.lock` 僵尸残留**（2026-08-09 实战）：bootout 成功后 bootstrap 仍失败，gateway log 报 `❌ Gateway already running (PID <stale>)`。根因：`gateway.pid` 和 `gateway.lock` 文件（格式 `{"pid": <stale>, ...}`）未被 bootout 清理，新 gateway 读到旧 pid 误判为冲突。**修复**：清空这两个文件（`write_file` 写空内容） + 修复 `gateway_state.json`（`pid→null, gateway_state→"stopped"`），然后 `launchctl kickstart` 或等待 KeepAlive 自动重启。**不要**只清 pid 不清 lock —— gateway 同时检查两个文件。

**修复顺序 B（兜底 — 2026-06-30 实战）— `bootstrap + enable` 仍报 I/O 错误时**：

```bash
# 用 legacy 的 launchctl load 兜底
launchctl load "$PLIST"
sleep 3
launchctl list | grep "ai.hermes.gateway-<name>"
```

**实战情况**（2026-06-30 15:54）：5 同事 plist 存在、`enable` 成功、`bootstrap` 仍报 `5: Input/output error`，**`load` 一次成功**。如果 A 路径走不通，**直接试 B 路径**不要死磕。

**不要尝试**：`launchctl kickstart -k` 找不回 `disabled` 的服务（会报 `Could not find service`）。**对 loaded 但 crashed（exit code=1）的服务，`kickstart -k` 同样不可靠**：返回 exit 0 无报错，但进程不复活（2026-08-09 实战确认）。唯一可靠修复路径是 `bootout → bootstrap`。

**修复顺序 U（unloaded — 2026-08-14 实战）— `launchctl list` 完全看不到 label 且 `kickstart`/`kickstart -k` 报 `Could not find service in domain for user gui: <uid>` 时**：服务被彻底 bootout/unload 清出了 gui 域（既非 disabled、也非 zombie、也非 loaded-but-dead——`print-disabled` 也看不到它）。**直接 `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<plist>` 一次成功**，无需先 `enable` 也无需 `bootout`。bootstrap 成功后若再跑 `launchctl load` 会报 `5: Input/output error`（服务已加载，属**预期良性报错**，忽略即可）；验证用 `launchctl list | grep <label>` 看 PID 已生成即可，勿被 load 的 I/O 报错误导二次重试。

### 8. RKR V4 "Agent 资源保障" 自动关停同事 gateway（**这是同事 gateway 全消失的最大常见原因**）

**机制**（RKR V4 2026-06-18 上线）：
当 RKR 积压 > 10000 且 5min 产出 < 30 时，`auto_ops.py` 自动 `launchctl bootout + disable` **8 个同事 gateway**（保留 default），释放 CPU 给 RKR 全力运转。

**触发证据**（cron `4c849d264b0b` / `1262b15958f4` 报告里出现）：
```
[INFO] 当前同事网关 = 0/7 运行 (无活体可关停)
[INFO] 条件未同时满足,不触发 launchctl 关停
```
或 RKR 巡检时 `WARNING: 无法获取 gateway 状态,跳过资源保障检查`（gateway 已经先于 RKR 被关过/没起）。

**用户故事**：华哥发"宽博士/X 同事不回了" → **90% 是这个机制**或历史 bootout 没恢复。

**恢复（华哥批准时）**：
```bash
# 一键恢复所有 7 个同事 gateway（RKR auto_ops 脚本自带的恢复命令）
python3 ~/Desktop/渔芯科技/6-产品研发/01-RKR知识库/scripts/auto_ops.py --restore-gateways

# 或手动逐个
UID_NUM=$(id -u)
for name in afu heidou laomo maodou quant xiaobao zhenglishi; do
  launchctl enable gui/$UID_NUM/ai.hermes.gateway-$name
  launchctl bootstrap gui/$UID_NUM ~/Library/LaunchAgents/ai.hermes.gateway-$name.plist
done
```

**注意**：RKR auto_ops **不会自动恢复**被关的 gateway（设计就是"关停"模式，不是"恢复"模式）。人工/华哥命令恢复后，下一轮 RKR 巡检如果条件还满足**会再关**。

---

## 12. 2026-07-31 实战：jobs.json 与 cronjob registry 错位 + state 文件滞后（4 个独立坑）

**这次执行"开老莫毛豆 + 关宽博士学习助手"4 网关调度时同时踩到的 4 个坑，互相耦合、必须一并修：**

### 坑 A：`hermes cron` CLI 用的 id 和 cronjob registry 不一致（最严重）

**症状**：`hermes cron pause <id>` 报 `Failed to pause job: Job with ID or name '<id>' not found`，但 id 是从 profile 的 `~/.hermes/profiles/<name>/cron/jobs.json` 拿的、看起来是合法的 12 字符 hex。

**根因**：jobs.json 是**profile 本地副本**，里面的 id **从未**同步到 Hermes 的全局 cronjob registry（`cronjob list` 看到的 52 个 job）。两个 id 体系根本不通用。

**修复**：永远用 MCP `cronjob` 工具，不用 CLI：

```python
# 1. 列真正的 id
cronjob(action='list')  
# → 返回 52 个 job，每条带 12-char hex job_id（如 7b7693454f0f）

# 2. pause/resume 必须用 MCP，不能用 hermes cron CLI
cronjob(action='pause', job_id='7b7693454f0f')
cronjob(action='resume', job_id='...')
```

**识别技巧**：如果 `jobs.json` 里的 id 都是 `ac5cebd95da9` / `79b94adf523f` 这种格式，而 `cronjob list` 看到的 id 是 `4c849d264b0b` / `7b7693454f0f` 这种 → **两个不是同一个体系**。

### 坑 B：jobs.json 里的 cron 任务大部分**根本没在跑**

**症状**（2026-07-31 实测）：quant 的 jobs.json 列出 4 个 cron（量化日报 / 周一提醒 / 深度调研 / 持仓监控），zhenglishi 9 个，laomo 1 个，maodou 2 个 —— 但 `cronjob list` 全局 52 个里**一个都找不到**。

**意味着什么**：
- 这些任务**实际从未同步**到 cronjob 系统，可能用别的方式跑（外部 launchd？人手触发？）
- 或者 jobs.json 是历史过期副本
- **真在跑的只有每个 profile 的"心跳 + 自我进化"2 个 cronjob**（如 quant → `4c849d264b0b` 量化研究心跳 + `7b7693454f0f` 自我进化）

**操作原则**：
- 暂停 gateway 时，**只 pause 全局 cronjob 里的心跳/自我进化**（坑 A 用对工具）
- **不要相信 jobs.json 列出的 cron 数量**——查 `cronjob list` 看真在跑的

**要不要修这个设计漏洞**：这是华哥决策。可以另开任务把 profile 的 jobs.json 同步到 cronjob registry。

### 坑 C：launchctl 启动后 gateway_state.json 显示滞后 `stopped/disconnected`

**症状**（2026-07-31 实测）：`launchctl bootstrap` 成功 + 有 PID（4446/4449），但立即 `cat gateway_state.json` 显示 `pid=<旧pid> state=stopped feishu=disconnected`。

**根因**：gateway_state.json 是 gateway 进程**自己**在 WS 连上后写的，launchctl 启动 gateway 后到它写 state 文件有几秒延迟（要初始化 + 飞书 WS 握手）。

**修复**：启动后等 6-8 秒再查 state 文件：

```bash
launchctl bootstrap gui/$UID_NUM "$PLIST"   # exit_code=0
sleep 8
cat .../gateway_state.json                  # → state=running feishu=connected
```

**判断标准**：如果等了 10 秒还是 `stopped`，才是真有问题（看 launchd error.log）。

### 坑 D：同事 profile 的 launchd plist 会被删掉（不是 disable）

**症状**（2026-07-31 实测）：5 个同事（afu/heidou/laomo/maodou/xiaobao/zhenglishi）的 `~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist` **文件不存在**，但 `launchctl print-disabled` 还能列出 label——说明文件被人为删了（不是 bootout disable）。

**根因**：RKR auto_ops V4 资源保障机制触发时**会删 plist 文件**（不只是 bootout）。重新建 plist 后 bootstrap 能正常起。

**模板**（见 `templates/launchd-gateway-plist.xml` —— 替换 `<NAME>` 为 profile 名）：

```bash
# 1. 复制模板 + 替换占位符
sed "s/<NAME>/maodou/g" templates/launchd-gateway-plist.xml \
  > ~/Library/LaunchAgents/ai.hermes.gateway-maodou.plist

# 2. 必须建在 ~/Library/LaunchAgents/（不是 ~/.hermes/profiles/<name>/），launchd 才能找到
```

### 4 坑联动执行清单（华哥要"关 A 开 B"时按此顺序）

```bash
# 1. 关：先 kill -9 手动启动的 gateway 进程（如有），再 bootout + disable + 删 plist
UID_NUM=$(id -u)
# ⭐ 关键：手动 `gateway run --replace` 启的 gateway 进程不在 launchd 控制里，bootout 不会杀它；
#    而且 launchd KeepAlive 会在 bootout 后短暂触发自动重启。要彻底关：先 kill -9。
ps auxww | grep "hermes.*--profile <关A>" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>&1
sleep 1
launchctl bootout gui/$UID_NUM/ai.hermes.gateway-<关A> 2>&1
launchctl disable gui/$UID_NUM/ai.hermes.gateway-<关A> 2>&1
rm -f /Users/hua/Library/LaunchAgents/ai.hermes.gateway-<关A>.plist   # 必须绝对路径！

# 2. 开：建 plist（如缺）+ enable + bootstrap
# ⭐ 关键：sed 必须替换 &lt;NAME&gt;（XML 实体编码）而不是裸 <NAME>，否则 plist Label/路径仍是字面 <NAME>
sed "s/&lt;NAME&gt;/<开B>/g" /Users/hua/.hermes/skills/devops/hermes-gateway-profile-ops/templates/launchd-gateway-plist.xml > /Users/hua/Library/LaunchAgents/ai.hermes.gateway-<开B>.plist
launchctl enable gui/$UID_NUM/ai.hermes.gateway-<开B> 2>&1
launchctl bootstrap gui/$UID_NUM /Users/hua/Library/LaunchAgents/ai.hermes.gateway-<开B>.plist  # 必须绝对路径！

# 3. 等 8 秒 + 验证 state（坑 C）
sleep 8
cat ~/.hermes/profiles/<开B>/gateway_state.json

# 4. 端点单测（确认 sk-cp- key 没失效）
KEY=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' ~/.hermes/profiles/<开B>/.env)
curl -sS -o /dev/null -w "%{http_code}" \
  -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'

# 5. cron pause/resume：用 MCP 工具（坑 A），不是 CLI
cronjob(action='list')  # 先查真在跑的 job_id
cronjob(action='pause', job_id='<关A对应心跳id>')
cronjob(action='pause', job_id='<关A对应自我进化id>')
# 开的 profile 通常 enabled=true 已经在跑，不需要 resume

# 6. 私聊路由激活提醒（§11）— 飞书侧 DM bot 第一句话必须华哥手动
```


## 已外置章节索引（瘦身R2）
- `split_r2_00_已知坑_踩过的_.md` ← 已知坑（踩过的）
- `split_r2_01_13_集中管理视图层_yuxin_team_2026_08_01_上线_.md` ← 13. 集中管理视图层 `~/yuxin-team/`（2026-08-01 上线）
- `split_r2_02_已外置章节索引_瘦身_.md` ← 已外置章节索引（瘦身）


## Profile 优雅关闭与重启（macOS launchd KeepAlive 语义,2026-10-01 收纳自 openclaw-gateway-setup）

launchd 管理的 gateway profile 直接 `kill` 无效（KeepAlive 立即拉起）;完全停止须先 `launchctl unload <plist>` 移除 KeepAlive 再操作,恢复用 `load -w`。状态码语义（0=运行中 / -9=已停止待重启 / 无输出=未加载）与完整关闭/重启流程:`references/***SECRET***.md`。
