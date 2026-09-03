# Gateway not running — bot 静默无响应（区别于 wss-up-but-1000040345）

## 症状（2026-06-15 实测，连发 3 次 "bot 不回"）

- 飞书群发消息，bot 0 响应
- `hermes gateway list` 显示 `gongzuo - not running`（**注意不是 `running` 但鉴权错**）
- 日志目录 `%LOCALAPPDATA%\hermes\profiles\<name>\logs\` 有 `gateway.log` 但**最后一条日志是 5-30 分钟前的旧启动记录**，没有新条目
- `errors.log` 可能在最后一次 stop 后是空的

## 根因（按出现频率排序）

1. **老大说"停"了** — 误以为配置有 bug，`hermes gateway stop -p <name>` 停了，又没起
2. **新 profile 还没起 gateway** — `hermes profile create` 完没跑 `hermes gateway run -p <name>`
3. **重启 gateway 时 `gateway stop` 完没 `gateway run`** — stop 完以为 restart，restart 失败（或没 restart 命令行）
4. **hermes 主进程崩了** — 4 个 gateway 全 not running，看 `%LOCALAPPDATA%\hermes\logs\hermes.log`

## 诊断流程（永远先跑这一行）

```bash
hermes gateway list
```

输出形态：

```
Gateways:
  ✓ default (current)        - PID 35928
  ✗ boss-control             - not running
  ✓ gongzuo                  - PID 35516
  ✓ xiaobao                  - PID 19300
```

**只关心 4 个 profile 的 `✓/✗`**。

## 决策树

```
bot 不响应
├─ gateway list 显示 not running
│  ├─ 老大刚说"停"/"暂停"了 → 问"还要起吗？"
│  ├─ 配完 profile 没起 → 直接 `hermes gateway run -p <name>`
│  └─ hermes 主进程崩了 → 查 `%LOCALAPPDATA%\hermes\logs\hermes.log` 找根因
└─ gateway list 显示 running
   ├─ 查 errors.log 含 1000040345 → pitfall #11
   ├─ 查 errors.log 含 230002 → bot 不在群里，老大手动拉
   └─ errors.log 干净 → 查 allowed_chats 是否 oc_PENDING 占位（pitfall #4）
```

## 修法

**直接起**（最常见 case）：

```bash
hermes gateway run -p <name>
```

**后台跑**（不阻塞 shell）：

```bash
terminal(background=true, notify_on_complete=false) -c "hermes gateway run -p <name>"
```

**不**用 `hermes gateway restart` —— 老 PID 锁可能不释放，新进程起不来。

## 验证

起完跑 `hermes gateway list` 看到 `✓ <name> - PID xxx` 后，**必须**等 5-10 秒再发消息 —— gateway 起来 + wss 握手 + 调一次 healthcheck 走完大约 5-8 秒。

## 区别于 pitfall #11

| 维度 | pitfall #11 (1000040345) | 本文件 (not running) |
|------|------------------------|---------------------|
| `gateway list` | `running` | `not running` |
| `errors.log` | 有 1000040345 行 | 空（或很旧） |
| 修法 | 补 .env + restart | `gateway run` |
| 检测时间 | 飞书发消息时 | 老大发"bot 不回"任意时刻 |

**最常见的错**是看到 `running` 一眼就跳到 wss 鉴权逻辑（pitfall #11），**实际是 gateway 根本没起**。`gateway list` 永远先跑。
