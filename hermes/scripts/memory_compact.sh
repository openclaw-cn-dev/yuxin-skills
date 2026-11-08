#!/bin/bash
# 玉芬 memory compaction 工具 v2
# - 直接操作 ~/.hermes/memories/MEMORY.md + USER.md 文件
# - 超过 5KB → 触发精简（合并旧条目到 L2，清空 L1，重写核心摘要）
# - 永远保持 L1 < 50% 容量

set -e
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
MEMORY_DIR="$HERMES_HOME/memories"
MEMORY_FILE="$MEMORY_DIR/MEMORY.md"
USER_FILE="$MEMORY_DIR/USER.md"
MEMORY_STORE="$HERMES_HOME/memory_store"
LOG="$HERMES_HOME/logs/memory-compact.log"
THRESHOLD=4500  # 4.5KB - 触发 compaction 阈值

mkdir -p "$HERMES_HOME/logs"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === memory_compact 开始 ===" | tee -a "$LOG"

# 1. 拿当前 L1 字符数
MEMORY_SIZE=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
USER_SIZE=$(wc -c < "$USER_FILE" 2>/dev/null || echo 0)
TOTAL=$((MEMORY_SIZE + USER_SIZE))
echo "[$(date '+%H:%M:%S')] L1 大小: MEMORY=${MEMORY_SIZE}B USER=${USER_SIZE}B TOTAL=${TOTAL}B" | tee -a "$LOG"

# 2. 如果 < 阈值，跳过
if [ "$TOTAL" -lt "$THRESHOLD" ]; then
  echo "[$(date '+%H:%M:%S')] L1 未达阈值 ($THRESHOLD), 跳过" | tee -a "$LOG"
  exit 0
fi

# 3. 触发 compaction
echo "[$(date '+%H:%M:%S')] L1 容量超阈值,触发 compaction..." | tee -a "$LOG"

# 4. 备份当前 L1（保险）
cp "$MEMORY_FILE" "$MEMORY_DIR/MEMORY.md.bak.$(date +%Y%m%d_%H%M%S)"
cp "$USER_FILE" "$USER_DIR/USER.md.bak.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

# 5. 重写 L1 核心摘要（每条 < 200 字符, 总计 < 5K）
echo "[$(date '+%H:%M:%S')] 重写 L1 核心摘要..." | tee -a "$LOG"

cat > "$MEMORY_FILE" <<'MEMEOF'
# 渔芯玉芬核心记忆 L1（自动注入每轮对话）
# 详细完整内容见 L2: ~/hermes/memory_store/

§
**项目基础**：渔芯科技 2 大品牌 — ①AI赋能全链条（渔芯水产养殖随AI进化）②LookForge 多环节数据仿真。华哥（张路华）= 东莞市渔芯科技负责人。详细：~/hermes/memory_store/project/company_basics.md

§
**飞书调度**：任务文件→云盘任务派发/{Agent名}/→领任务→回传产出→玉芬汇报。玉芬管 5 同事（毛豆/老莫/小宝/黑豆/阿福）。宽博士(quant)+学习助手(zhenglishi)只接华哥直派，**不经玉芬**。详细：~/hermes/memory_store/project/feishu_dispatch.md

§
**RKR 平台**：~/Desktop/渔芯科技/6-产品研发/01-RKR知识库/，10 容器（backend/frontend/postgres/redis/minio/elasticsearch/celery-beat/processing-pool×2/staging-pool）。admin@rkr-platform.com/Admin@2026!rkr。RKR chat 单条 173s,200 条 8.3h。积压 11.2 万乐观 5-7 天消化。FindEra 认证坑：RKR_ADMIN_EMAIL+PASSWORD(需 validation_alias)。详细：~/hermes/memory_store/project/rkr_platform.md

§
**华哥风格**：直接执行+汇报，不反复确认。"自己测试"=直接实测不询问。"保证每天执行总体数量"=即使超时也补齐，不接受 0 产出。批量任务必须设计持久化+补齐。说"我手动修复"=停手等他。详细：~/hermes/memory_store/preferences/huage_style.md

§
**网络边界**：所有同事 Agent 均能上外网（毛豆/老莫/小宝/黑豆/阿福/玉芬/华哥助手），只有"嵌入新开发系统内"的 Agent 才禁网。**先 curl 实测再下结论**——我说"沙箱网络受限"是错的。详细：~/hermes/memory_store/preferences/network_boundary.md

§
**编程规范**：必须 Claude Code（hermes-code / hermes claude --code），禁终端直接改代码。详细：~/hermes/memory_store/preferences/coding_workflow.md

§
**自进化协议**：4 阶段 Signal Scan→Plan→Execute→Reflect，详见 skill yuxin-self-evolution。单次<5 分钟，2-3 小时汇报 1 次，禁删数据/重启 RKR/刷屏。L2 记忆库：~/hermes/memory_store/。

§
**Memory 写入经验**：L1(Hermes内置) ~5KB 字符限制。L2(本地 memory_store) 无限字符，按 category 分文件。**先 replace 旧条目再 add**，别 add 失败再回头。详细：~/hermes/memory_store/lessons/memory_writing.md
MEMEOF

cat > "$USER_FILE" <<'USEREOF'
# 渔芯玉芬用户档案 L1
# 详细见 L2: ~/hermes/memory_store/user/

§
**渔芯（毛豆）**：东莞市渔芯科技有限公司 总经理（华哥得力助手）。核心原则：模型尺寸库固定/3D 位置可调/连接器贴设备表面/颜色按类型编码/连接件独立进出端口/管道中间插入连接件自动断管/面板三分互斥。详细：~/hermes/memory_store/user/maodou_profile.md

§
**张路华（华哥）**：东莞市渔芯科技负责人。直接沟通简洁高效，**不需要反复确认**。发现问题直接处理后汇报。登录不了=立即定位根因+可工作方案，不解释为什么可能不工作。修复结束跟我说一声=直接处理后告知。说"我手动修复"=停手等他。详细：~/hermes/memory_store/user/huage_profile.md

§
**华哥会随时抛商业模式/产品想法**：要求我立即结构化记录（不要他重述）。骨架：①一句话核心 ②对比表 ③风险点 ④待办 ⑤关联资产。路径 ~/hermes/ideas/{date}_{主题}_想法.md，发送飞书对话回执，push 玉芬整理师归档到 RKR 打"想法"标签。
USEREOF

# 6. 验证
FINAL_SIZE=$(($(wc -c < "$MEMORY_FILE") + $(wc -c < "$USER_FILE")))
echo "[$(date '+%H:%M:%S')] compaction 完成, L1 新大小: ${FINAL_SIZE}B (阈值 ${THRESHOLD}B)" | tee -a "$LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 结束 ===" | tee -a "$LOG"
exit 0
