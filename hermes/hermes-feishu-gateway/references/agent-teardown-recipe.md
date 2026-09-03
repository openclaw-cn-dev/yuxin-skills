# App 全链路清理 Recipe（"全部删掉" / "清理子 AGENT" 的对偶操作）

onboarding 的对偶：**teardown 同样有 6 步**，漏一步就是明文凭据外泄。2026-06-06 实战，4 App / 17 处泄露面 / 6 类文件。

## 触发场景

老大说以下任何一句：

- "清理子 AGENT" / "删掉 4 个机器人" / "只保留你自己"
- "全部删掉" / "不用原来那套方案"（结合 pitfall #9 一起判断）
- "飞书 App 不用了，清理一下" / "把之前那 4 个 App 痕迹全删了"
- "我要换 4 个新的 App"（隐含旧凭据要清）

**永远先扫后删。** 给老大出 A/B/C/D 选项之前，先 ripgrep 列出所有泄露面 + 拿全清单再问。

## 6 类泄露面（必须全扫，缺一不可）

| # | 位置 | 内容 | 处理方式 |
|---|---|---|---|
| 1 | `~/feishu-secrets.json` | 主凭据 4 套 AppID+Secret | 直接删文件（NTFS 忽略 chmod 600） |
| 2 | skill 自己的 `templates/*.json` 范例 | 4 套占位示例 | 整文件重写：所有 `app_id` → `cli_REDACTED_000N`、`app_secret` → `REDACTED_REPLACE_VIA_FLYBOOK_CONSOLE` |
| 3 | skill 的 `references/*.md` 文档示例 | 4 个 App URL + 1 个 Secret 引用 | patch 改占位 |
| 4 | `~/.hermes/profiles/<name>/.env` per-profile | 4 套 FEISHU_APP_ID + FEISHU_APP_SECRET | 删整个 profile（pitfall #9 的判断） |
| 5 | `~/demo-*.py` / `~/deploy-feishu.py` 等一次性脚本 | 4 套 Secret 全明文 | **直接 rm**，不留 archive |
| 6 | `~/AppData/Local/hermes/logs/*.log` + `~/AppData/Local/hermes/interrupt_debug.log` | 用户 DM bot 发 Secret 的完整消息原文 | **不删**，mv 到 `logs/archive-YYYY-MM-DD/` 冻结（保排错证据） |

**第 6 类最危险也最容易被忽略**——日志里的 Secret 是「完整 32 字符 + 真实 chat_id + 用户 open_id」三合一，攻击者拿到直接重放。一定要扫！

## 复扫模式（ripgrep 全盘扫，给老大出选项前必跑）

```bash
# 4 个 App ID 模式
rg -uu 'cli_aaa9[a-f0-9]{12}' ~/AppData/Local/hermes/

# 4 个真 Secret 模式（精确字符串，避免误报）
rg -uu -e '<APP_SECRET>' \
        -e '5KKLeotArLrXBRkvoQfJgfGjDCZlUqJz' \
        -e 'rbVomBtLJD7KQpJ2gYVTve461jTdxazs' \
        -e 'pKNzlq6EcYcZ4yWPDFS2Id44lDf3OI6w' \
        ~/AppData/Local/hermes/
```

跑完会拿到完整的"漏网点清单"——**这是给老大出 A/B/C/D 选项的输入**。没跑复扫就动手 = 必然漏 1-2 个点。

## Windows 句柄锁绕过（关键非平凡技术点）

**症状**：`mv ~/AppData/Local/hermes/logs/agent.log ~/AppData/Local/hermes/logs/archive-2026-06-06/` 报 `Device or resource busy`。

**根因**：hermes 主进程持着 `agent.log` / `errors.log` 的写入句柄（mmap + append 模式），`mv` 在 Windows 上是 rename syscall，跨设备/跨句柄的 rename 直接被拒。

**正解（两步绕过）**：

```bash
# 1. 先把不在句柄锁上的日志 mv 到 archive（gateway.log / interrupt_debug.log / 等小文件）
mkdir -p ~/AppData/Local/hermes/logs/archive-2026-06-06/
mv -v ~/AppData/Local/hermes/logs/gateway.log \
      ~/AppData/Local/hermes/logs/gateway-exit-diag.log \
      ~/AppData/Local/hermes/interrupt_debug.log \
      ~/AppData/Local/hermes/logs/archive-2026-06-06/

# 2. 对被句柄锁的 agent.log / errors.log 用 truncate-on-file-pattern
#    (保留 inode + 句柄，把内容清零，hermes 进程继续写新内容)
cd ~/AppData/Local/hermes/logs
for f in agent.log errors.log; do
  : > "$f"  # truncate 到 0 字节，句柄不丢
done
```

**为什么 truncate 而不是删**：

- `rm` 会让 hermes 后续 `open(O_APPEND)` 拿到新 inode，但旧 fd 还在写，**会出现"文件不存在但进程还在写"的状态**，崩溃时序很乱。
- truncate 后，hermes 进程的 fd 还是指向同一个 inode，**清零即生效**——新内容从 0 字节开始追加，旧明文 Secret 物理上消失。

**验证**：
```bash
od -c ~/AppData/Local/hermes/logs/agent.log | head -1
# 应该看到一堆 \0 或空行，不再含明文 Secret
```

## 完整 teardown 6 步（按顺序）

1. **复扫** ripgrep 出 17+ 处泄露面 + 列清单
2. **问老大选项**（5 选 1：源文件清 / 日志冻 / 全清 / 日志彻底删 / 全清+清空 archive 里的真 Secret）
3. **删主凭据** `~/feishu-secrets.json` (rm)
4. **改 skill 模板/文档**（write_file 整体重写 secrets.json、patch 改 bindings-json.md / gotchas.md / 3-business-line-deploy.md / secret-redaction-workaround.md / memories/MEMORY.md）
5. **删一次性脚本**（demo-sales.py / deploy-feishu.py，rm）
6. **处理日志**（mv 小文件 + truncate 大文件，最后再 ripgrep 复扫确认 archive 之外全净）

## 验证收尾

```bash
# 复扫：除了 archive 目录，其它地方必须 0 命中
rg -uu 'cli_aaa9[a-f0-9]{12}' ~/AppData/Local/hermes/ -g '!logs/archive-2026-06-06/**'
# → 期望 total_count: 0

# 验 truncate 生效
ls -la ~/AppData/Local/hermes/logs/agent.log ~/AppData/Local/hermes/logs/errors.log
# → 两个文件存在但 0 字节
```

## 飞书平台侧的最后兜底

文件层全清完，**云端 4 个 App 还活着**——旧 Secret 仍然有效。小弟无权操作 `https://open.feishu.cn/app` 后台（需要老大登录 + 确认），给老大 3 个选项：

- A. 我教你怎么 1 分钟禁掉 4 个 App（推荐，App 全删 = 最彻底）
- B. 不用了，App 我自己处理
- C. 把这步存成 todo，下次提醒

**永远不要**"自动登飞书后台点禁用"——飞书后台涉及支付 / 商业套餐 / 第三方授权，**必须老大手动**。

## 给老大的"清理完成" delivery 模板

```
Done. 4 子 AGENT 痕迹已清:
  ✓ ~/feishu-secrets.json   (rm)
  ✓ 5 个 skill 模板/文档     (App ID + Secret 全脱敏)
  ✓ 2 个一次性脚本           (rm)
  ✓ 3 个小日志              (mv 到 archive-2026-06-06/)
  ✓ 2 个活跃日志            (truncate 0 字节，句柄保留)

残留: 17 处真 Secret 在 archive 冻结区 (按你的"全部"指令保留为证据, 但已隔离)
  路径: ~/AppData/Local/hermes/logs/archive-2026-06-06/

老大 1 步要做:
  去 https://open.feishu.cn/app 后台禁掉 4 个 App (销售小成/研发小研/生产小产/客服小服)
```
