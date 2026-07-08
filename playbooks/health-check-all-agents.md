# 全智能体健康检查 SOP

## 场景
需要确认所有智能体是否在线、功能正常。

## 检查清单

### 1. Hermes Agent 检查

```bash
# 列出所有 profile gateway 状态
hermes gateway list

# 或逐个检查
for prof in default maodou laomo xiaobao heidou afu quant zhenglishi; do
  echo "=== $prof ==="
  launchctl list | grep "ai.hermes.gateway-$prof" || echo "  ❌ NOT RUNNING"
  ps aux | grep "hermes.*gateway.*$prof" | grep -v grep | awk '{print "  ✅ PID="$2}' || echo "  ❌ NO PROCESS"
done
```

### 2. Codex CLI 检查

```bash
codex --version
```

### 3. Claude Code 检查

```bash
claude --version
```

### 4. OpenClaw 检查

```bash
openclaw --version
```

### 5. 飞书 Bot 可达性

```bash
# 检查每个 bot 是否能获取 token
# 用对应 App ID + Secret
```

## 一键检查

参考: `~/hermes/team/runbooks/verify_team_health.sh`
