---
name: remote-machine-access
description: 跨机器远程访问类技能（Tailscale mesh 为主实现）— mesh 入网/登录授权/状态验证/机器台账、登录链接一次性几分钟过期的坑、Windows CLI 全路径调用、远程连 18890 LLM 网关、Mac/新机器入网成双机网格。触发条件：华哥发来 Tailscale 登录链接、"远程访问 XX 机器"、tailscale 登录/掉线/查 IP、公网不可达但要连公司内网服务（18890 网关/SSH/飞书通道）、把 Mac 或旺财机拉入 tailnet。
version: 1.0.0
---

# 远程机器访问（Tailscale mesh）

渔芯多机拓扑的远程访问层：Tailscale 给每台机器发固定 100.x.y.z mesh IP，公网/NAT 怎么变都不影响直连。用途：远程连 18890 LLM 网关、SSH、飞书通道、跨机文件通道；也是 Mac ↔ Windows 直连（升级/补充 Mnemosyne 记忆面中转）的基础设施。

## 当前 mesh 台账（2026-11-12）

| 节点 | 机器 | Tailscale IP | 状态 |
|---|---|---|---|
| openclaw-cn-dev@ | Windows（EVO-X3，玉芬宿主机） | **100.65.195.9** | ✅ 已入网在线 |

- 账号 `openclaw-cn-dev@`，ControlURL controlplane.tailscale.com，UDP 直连可用，版本 v1.104.6
- **CLI 不在 PATH**：二进制在 `C:\Program Files\Tailscale\tailscale.exe`，git-bash 里必须全路径调用：`TS="/c/Program Files/Tailscale/tailscale.exe"; "$TS" status`
- Mac / 旺财机尚未入网；入网 = 装 Tailscale + 登录同一账号（Mac 入网后即成双机网格）

## 常用命令（Windows git-bash）

```bash
TS="/c/Program Files/Tailscale/tailscale.exe"
"$TS" status     # 网格状态；本机状态行示例：100.65.195.9  node  openclaw-cn-dev@  windows  -（行尾 - = self）
"$TS" ip -4      # 本机 Tailscale IPv4
"$TS" login      # 生成新登录链接并阻塞等待授权 → 用 terminal(background=true) 跑
```

## 登录授权流程与「链接过期」坑（2026-11-12 实战）

1. **华哥转发的登录链接大概率已过期**：授权链接是一次性、几分钟失效（过期后请求返回 400）。收到链接可以直接试一次，400 就**不要反复重试同一链接**。
2. **正确姿势**：本机自己跑 `"$TS" login` 生成全新链接（stdout 打印 URL）→ 浏览器打开授权 → 轮询 `"$TS" status` 直到本机行出现 mesh IP 为止。
3. `login` 会阻塞等待授权 → 必须 `terminal(background=true)` + `process poll`，授权完成后**清理残留后台进程**。
4. 前提：Windows 服务 `Tailscale` 处于 RUNNING（登录和连接都走它）；status 卡死先查服务再查网络。
5. 验收双查：`status` 本机行有 IP + `ip -4` 返回 100.x 地址，两步都过才算入网成功。

## 远程访问用途与拓扑价值

- 任何装了 Tailscale 同账号的设备，可直接 `100.65.195.9:18890` 访问本机 LLM 网关（免公网暴露端口）；SSH/文件通道同理。
- Mac 入网 → 双机网格：跨机同步、网关调用、SSH 全直连。`hermes-config-safe-edit` 中「旺财只能走 Mnemosyne 记忆面」的约束**在目标机入网后解除**——改远程配置前先 `tailscale status` 看目标机在不在网，在线走直连，不在网再走 Mnemosyne。

## 相关 skill 边界

| skill | 边界 |
|---|---|
| `hermes-config-safe-edit` | 远程改配置的手术流程（旺财三段式 playbook）；通道选择见其 2026-11-12 拓扑更新注 |
| `mnemosyne-cross-machine-sync` | 记忆面同步本身；Tailscale 是其可选的直连升级路径 |
| `multi-cloud-llm-architecture` | 18890 网关与本地模型五件套拓扑（被远程访问的对象） |
