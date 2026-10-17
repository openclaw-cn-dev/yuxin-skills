---
name: mnemosyne-cross-machine-sync
description: |
  用 Mnemosyne Sync 做跨机器 agent 记忆同步（如玉芬 Mac ↔ 旺财 Windows）。
  触发条件：需要让两台不同机器上的 Hermes agent 共享/互管记忆，或用户问"怎么管理另一台电脑上的 agent 记忆"。
  渔芯 2026-08-18 实战踩坑 5 个，全部沉淀在此，照做不试错。
---

# Mnemosyne 跨机器记忆同步（渔芯实战 2026-08-18）

## 一、架构（关键：三个 db 角色分离，共用即踩坑）

```
旺财 Windows (sync 客户端)         玉芬 Mac (relay + 客户端)
  shared surface db ◄──HTTP:8765──► sync-serve (relay)
                                     ├─ relay db（存事件密文，中转）
                                     └─ 玉芬 sync-client（连自己 relay）
                                          └─ shared surface db（存明文记忆）
```

**三个 db 角色，绝不可混用：**
| db | 用途 | 内容 |
|---|---|---|
| **relay db** | sync-serve 中转 | memory_events 事件日志（密文） |
| **shared surface db** | 客户端 + mnemosyne_shared_* 工具 | working_memory 记忆（明文） |
| 各客户端本地 shared db | 各自机器的记忆面 | 同上 |

relay 和 shared surface 用同一个 db 会导致：拉取事件误判 duplicate，不解密应用。

## 二、玉芬侧（relay 服务端）完整配置

```bash
# 1. 初始化两个独立 db
mnemosyne sync-init --db-path ~/.mnemosyne/data/sync_relay/mnemosyne.db
mnemosyne sync-init --db-path ~/.mnemosyne/data/shared/mnemosyne.db

# 2. 生成 API key（认证）
openssl rand -hex 24 > ~/.hermes/mnemosyne/sync_api_key && chmod 600

# 3. launchd 托管 sync-serve（relay）—— 必须 --behind-tls-proxy
#    Label: ai.hermes.mnemosyne-sync，RunAtLoad + KeepAlive
#    ProgramArguments: mnemosyne sync-serve --db-path <relay db> --host 0.0.0.0 \
#      --port 8765 --api-key-file <key> --behind-tls-proxy

# 4. launchd 托管 sync-client（每 5 分钟双向）
#    Label: ai.hermes.mnemosyne-sync-client，StartInterval=300
#    ProgramArguments: mnemosyne sync --db-path <shared surface db> \
#      --remote http://127.0.0.1:8765 --mode bidirectional \
#      --api-key-file <key> --encrypt-key-file <encrypt.key>
```

## 三、客户端侧（旺财 Windows）配置

```powershell
pip install mnemosyne-hermes
# 1. API key 落地
mkdir C:\Users\<用户>\.hermes\mnemosyne -Force
echo "<api_key>" > C:\Users\<用户>\.hermes\mnemosyne\sync_api_key
# 2. 初始化本地 shared db
mnemosyne sync-init --db-path C:\Users\<用户>\.mnemosyne\data\shared\mnemosyne.db
# 3. hosts 加白名单域名（管理员权限）
#    C:\Windows\System32\drivers\etc\hosts 加一行：<玉芬IP>  mnemosyne-sync.local
# 4. 双向同步常驻（--interval 300 常驻循环）
mnemosyne sync --db-path C:\Users\<用户>\.mnemosyne\data\shared\mnemosyne.db \
  --remote http://mnemosyne-sync.local:8765 --mode bidirectional \
  --api-key-file <key文件> --encrypt-key-file <encrypt.key> --interval 300
```

## 四、5 个坑（全部实测踩过）

1. **relay 和 shared surface db 必须分离** —— 共用导致拉取误判 duplicate，事件不解密应用。
2. **客户端必须用同一把 encrypt.key** —— relay 默认 `require_encrypted_payloads=True`，明文事件被拒。加密 key 双方共享，用 `--encrypt-key-file` 传。
3. **`mnemosyne-sync.local` 白名单域名** —— sync 客户端对非 loopback 的 HTTP 强制 HTTPS；源码硬编码 `mnemosyne-sync.local` 豁免，hosts 映射这个域名即可绕过，免 TLS 证书。
4. **mv/备份 db 前必须先 `PRAGMA wal_checkpoint(TRUNCATE)`** —— 否则 WAL 里未落盘的数据丢失，且查主文件显示"假象干净"。
5. **fingerprint 已记录会跳过重推** —— 客户端推过的事件在 `sync_memory_state` 表记录 fingerprint，重推被跳过。换 relay 后需清空客户端/relay 的 `sync_memory_state` + `sync_outbox_ack` + `memory_events` 三表，强制重推。

## 五、验证对账

```bash
# 链路验证
mnemosyne sync-status --db-path <shared db> --remote http://127.0.0.1:8765 \
  --api-key-file <key> --json

# 查 relay 事件 + shared surface 明文记忆
sqlite3 <relay db> "SELECT COUNT(*) FROM memory_events"
sqlite3 <shared db> "SELECT substr(content,1,40) FROM working_memory"

# 双向对账 = 3/3 即闭环
```

## 六、玉芬侧管理旺财记忆

玉芬读旺财记忆 = `mnemosyne_shared_recall`（shared surface db 明文）；玉芬写记忆 = `mnemosyne_shared_remember`（写 shared surface，sync-client 加密推给旺财）。
⚠️ 不要用 `mnemosyne_shared_remember` 在 relay 未分离时写（会留 sync_surface_id=NULL 阻塞 sync）。

### 给旺财下发可执行指令的实战模板（2026-09-30 玉芬→旺财切智谱实测）

`mnemosyne_shared_remember` 是玉芬→旺财唯一的指令通道（两机无 SSH、旺财无独立飞书），content 写成**自包含 P0 指令**：任务 + 执行方式 A（跑脚本，写明脚本名与路径）+ 执行方式 B（手工改法的完整字段值，逐项列全——脚本通道断掉时旺财可徒手完成）+ 改前备份/改后校验要求 + 「完成后向玉芬回报」。importance=0.9、kind=meta、veracity=stated。

**验证推达三步**（CLI 不一定装了，走 sqlite 直查）：
1. `sqlite3 ~/.mnemosyne/data/shared/mnemosyne.db "SELECT COUNT(*) FROM memory_events"` — 写入后事件数增加（payload 为 mne1: 加密切文 = 已入 outbox）
2. `launchctl kickstart -k gui/$(id -u)/ai.hermes.mnemosyne-sync-client` — sync-client 若已停（`launchctl list` 显示 `-`）手动踢一脚；relay 服务（`ai.hermes.mnemosyne-sync`）应常驻有 PID
3. 客户端侧旺财下次会话启动时自动召回该 P0 记忆（5 分钟同步周期 + 会话注入）
⚠️ 不要用 `mnemosyne_shared_remember` 在 relay 未分离时写（会留 sync_surface_id=NULL 阻塞 sync）。

### 共享记忆面当「远程派单通道」用（2026-09-30 实战补充）

跨机改配置/派任务时，shared surface 是唯一通道（玉芬↔旺财无 SSH）。写完派单记忆后**别默认它已同步**，按序验证：

1. **推送触发**：`launchctl kickstart -k gui/$(id -u)/ai.hermes.mnemosyne-sync-client`（默认 5 分钟轮询太慢；实测发现 sync-client 常显示为 `-` 状态但 kickstart 后正常工作）。relay 服务 `ai.hermes.mnemosyne-sync` 常驻（有 PID 即健康）。
2. **入队确认**：`memory_events` 表（relay db 同结构在 shared db 也存在）行数应增长；`payload` 列是 `mne1:gAAAAA...` 开头的**密文**——看到乱码密文=正常，别当损坏。schema 列名：`event_id, memory_id, operation, timestamp, device_id, payload, event_hash, synced_at, apply_state`（无 `content` 列，SELECT 别写错列名报 OperationalError）。
3. **工具侧校验**：写后立刻 `mnemosyne_shared_recall` 同关键词能召回 = 落库成功。注意 `mnemosyne sync-status` CLI 可能在会话 env 缺 `MNEMOSYNE_SYNC_REMOTE` 而报 "No remote configured"——这是 CLI 探测限制，**不代表同步链路坏了**，以 1/2 两步 launchctl+sqlite 验证为准。
4. shared db 里可能没有 `sync_memory_state` 表（该表在客户端本地 db 记录已推指纹）；判断"有没有推出去"看 `memory_events.synced_at` 是否被填。

## 七、本机多 profile 迁移 MEMORY.md → Mnemosyne（同步的前置步骤）

把多个 profile 的内置 memory（MEMORY.md）迁到各自独立的 Mnemosyne db，步骤：

1. **备份**：`cp MEMORY.md MEMORY.md.bak.mnemosyne_<ts>`
2. **config.yaml 加 memory 块**：`memory: {memory_enabled: true, user_profile_enabled: true, provider: mnemosyne, memory_char_limit: 2200, user_char_limit: 1375}`（各 profile 的 config.yaml 通常没有 memory 块，需追加）
3. **install 插件**：`mnemosyne-hermes --hermes-home /Users/hua/.hermes install --force`（--force 因为 default 已装；它会自动 symlink 到所有 opted-in 的 profile）
4. **迁移脚本**：读 MEMORY.md 按 `§` 拆分，逐条 `mnemosyne.remember(sec, source=分类, scope='global', trust_tier='IMPORTED')`，写占位符。脚本在 `~/.hermes/scripts/migrate_mnemosyne.py`（Mac）/ `migrate_mnemosyne_win.py`（Windows）。source 分类：身份/环境/项目/关系/偏好。

**三个坑**：
1. **中文记忆必须换 embedding**：默认 `bge-small-en-v1.5` 英文优化，中文召回不准。config.yaml 设 `embedding_model: BAAI/bge-small-zh-v1.5`。
2. **fastembed 缓存要软链共享**：每个 profile 的 HERMES_HOME 不同，会各自下载 ~100MB 模型。给各 profile 建 `cache/fastembed` → 软链到 default 的 `~/.hermes/cache/fastembed`。
3. **安装目录区分**：default 的 db 在 `~/.hermes/mnemosyne/data/`，profile 的在 `~/.hermes/profiles/<名>/mnemosyne/data/`，靠 `MNEMOSYNE_DATA_DIR` 环境变量定位。
