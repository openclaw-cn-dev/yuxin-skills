#!/bin/bash
# 寻元 + 知识库 2 小时健康监测与汇报
# 逻辑：探测容器+API → 判断(白天计划停/夜间应运行) → 夜间异常自动恢复 → 输出状态摘要
# no_agent 模式：stdout 非空即投递给华哥（每 2 小时一次状态汇报）

HOUR=$(date +%H)
# 白天 8:00-22:59 = 计划停止时段（华哥 2026-08-21 定调）；23:00-07:59 = 夜间应运行
if [ "$HOUR" -ge 8 ] && [ "$HOUR" -lt 23 ]; then
  DAYTIME=1
else
  DAYTIME=0
fi

# ── 夜间异常自动恢复 ──
recover_if_needed() {
  local fe_missing=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c '^research-backend$')
  local rkr_missing=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c '^rkr-backend$')

  if [ "$DAYTIME" = "0" ]; then
    # 夜间：容器应该运行，缺失则恢复
    if [ "$rkr_missing" = "0" ] || [ "$fe_missing" = "0" ]; then
      echo "⚠️ 夜间检测到容器缺失，尝试自动恢复..."
      docker context use desktop-linux >/dev/null 2>&1
      cd /Users/hua/6-产品研发/渔芯独角兽/02-产品开发综合平台/02-RKR知识库 && docker compose up -d >/dev/null 2>&1
      cd /Users/hua/6-产品研发/渔芯独角兽/02-产品开发综合平台/01-FindEra寻元 && docker compose up -d >/dev/null 2>&1
      sleep 20
    fi
  fi
}

recover_if_needed

# ── 生成汇报 ──
FE_BACKEND=$(docker ps --format '{{.Names}}|{{.Status}}' 2>/dev/null | grep '^research-backend|' || echo "缺失")
RKR_BACKEND=$(docker ps --format '{{.Names}}|{{.Status}}' 2>/dev/null | grep '^rkr-backend|' || echo "缺失")
FE_API=$(curl -s -m 5 http://localhost:8003/api/v1/health 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','OFFLINE'))" 2>/dev/null || echo 'OFFLINE')
RKR_API=$(curl -s -m 5 http://localhost:8000/api/v1/health 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','OFFLINE'))" 2>/dev/null || echo 'OFFLINE')
RKR_TOTAL=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c '^rkr-')
FE_TOTAL=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c '^research-')

echo "📊 寻元 & 知识库 状态汇报（每 2 小时）"
echo "时间：$(date '+%Y-%m-%d %H:%M') ｜ 时段：$([ "$DAYTIME" = "1" ] && echo '白天(计划停止)' || echo '夜间(应运行)')"
echo ""
echo "【寻元 FindEra】"
echo "  容器：$FE_BACKEND"
echo "  API(8003)：$FE_API ｜ 容器数：$FE_TOTAL"
echo ""
echo "【知识库 RKR】"
echo "  容器：$RKR_BACKEND"
echo "  API(8000)：$RKR_API ｜ 容器数：$RKR_TOTAL"
