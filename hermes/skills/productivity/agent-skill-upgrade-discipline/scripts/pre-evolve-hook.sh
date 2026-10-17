#!/bin/bash
# pre-evolve-hook.sh
# 阿福 cron evolution 启动前必跑脚本(写入任何 SKILL.md 前)
# 失败时 abort evolve + 飞书告警华哥
# 来源: ***SECRET*** §14.5 (2026-08-25 阿福三轮复发根因新增)
# 玉芬 8/25+ 接入 ~/.hermes/config.yaml 后,此 hook 会在每次 cron 启动时自动跑

set -e

PROFILE="${HERMES_PROFILE:-afu}"
SKILL="${EVOLVE_TARGET_SKILL:-afu-customer-service}"

SKILL_ROOT="$HOME/.hermes/skills/productivity/***SECRET***"
VERIFY_INTEGRITY="$SKILL_ROOT/scripts/verify-skill-integrity.sh"
VERIFY_LEGACY="$SKILL_ROOT/scripts/verify-three-end-version.sh"

LOG_PREFIX="[pre-evolve][$PROFILE/$SKILL]"

echo "$LOG_PREFIX === §14 完整性预检 ==="

# 优先用新脚本(§14),回退到 §13 老脚本
if [ -f "$VERIFY_INTEGRITY" ]; then
  echo "$LOG_PREFIX 跑 verify-skill-integrity.sh (5 项检查)"
  bash "$VERIFY_INTEGRITY" "$PROFILE" "$SKILL"
  RC=$?
elif [ -f "$VERIFY_LEGACY" ]; then
  echo "$LOG_PREFIX ⚠️ verify-skill-integrity.sh 未就位 → 回退到 verify-three-end-version.sh (3 项检查)"
  bash "$VERIFY_LEGACY" "$PROFILE" "$SKILL"
  RC=$?
else
  echo "$LOG_PREFIX ❌ §13/§14 核验脚本都未就位 — 必须先安装 ***SECRET*** skill"
  exit 1
fi

if [ $RC -ne 0 ]; then
  echo "$LOG_PREFIX ❌ 预检失败 (rc=$RC) → abort evolve"
  echo "$LOG_PREFIX 📞 飞书告警华哥..."

  # 飞书通知(可选,失败时仅本地日志)
  NOTIFY_CMD="$HOME/.hermes/scripts/feishu_notify.py"
  if [ -f "$NOTIFY_CMD" ]; then
    python3 "$NOTIFY_CMD" \
      --target 华哥 \
      --message "⚠️ 阿福 cron §14 预检失败 — $PROFILE/$SKILL SKILL.md 三方一致性异常,请手动 review 后再启 evolution" \
      || echo "$LOG_PREFIX (飞书通知失败,仅本地日志)"
  else
    echo "$LOG_PREFIX (feishu_notify.py 不存在,跳过飞书告警)"
  fi
  exit $RC
fi

echo "$LOG_PREFIX ✅ 预检通过 → 可继续 evolution"
exit 0
