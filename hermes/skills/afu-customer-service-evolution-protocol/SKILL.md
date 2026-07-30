---
name: afu-customer-service-evolution-protocol
description: 阿福（客服）自我进化节奏与盲区规避。触发条件：cron 心跳无任务、复盘无真实对话、维护 SKILL.md/参考资料、规划下一轮进化重点。
version: 1.0.0
owner: afu
status: active
---

# 阿福自我进化节奏与盲区规避

## 触发条件
- `python3 /Users/hua/.hermes/scripts/heartbeat_check.py 阿福` 静默
- `~/.hermes/kanban.db` 与 `tasks.db` 双库均 0 pending/in_progress
- 用户期望阿福进入自我进化模式（话术沉淀、技巧学习、RAS 资讯摘录）

## 五步进化流程（每轮必做）

1. **复盘**：用 `session_search` 检索近 3 次“客户/异议/投诉/售后”关键词；若连续 5+ 次无真实对话，复盘写“连续第 N+X 次无对话”，不要硬凑分析。
2. **新技巧学习**：技能 < 19 个 → 学新技巧；≥ 19 个 → 维护现有技巧或设计实战演练脚本。
3. **行业资讯**：先查 `references/ras-industry-*.md` mtime，若 < 12 小时跳过网络搜索；超 12 小时再用 `delegate_task` 或 `browser_navigate` 核验单条新闻。
4. **技能集检查**：核验版本号、技巧数、辅助框架数与编号体系一致性；修复“双位置”“编号重复”等问题。
5. **输出报告**：路径 `~/.hermes/profiles/afu/evolution/$(date +%Y-%m-%d_%H).md`，每轮 5–9KB。

## 盲区与陷阱（已踩过的坑）

- **跨 Profile 守护**：写入 `/Users/hua/.hermes/skills/afu-customer-service/SKILL.md` 会触发 `Cross-profile write blocked`。**只动 afu profile 本地**：`/Users/hua/.hermes/profiles/afu/skills/...`，不动共享路径。需批量合并时给出 A/B/C 方案给用户决策。
- **重复编号**：Peak-End Rule 同时登记在编号 23 与辅助框架 9 会造成“双位置”。每轮检查“内容-编号-版本”一致性。
- **网络搜索超时**：`delegate_task` web 600s 超时后**不要重试同样方式**，切换短搜索或本地趋势库，并在报告标注“本地梳理（非 web 搜索）”。
- **单条新闻泛化**：单一企业半年报 ≠ 全球行业爆发。引用数据时保留来源、时间和口径，避免“用一句话概括全球”。
- **已登记框架补参考时不要双编号**：当一个辅助框架（如 Anchoring Effect #11）已经登记在 SKILL.md 表格里但参考文件未沉淀时，只需在**原行标 ✅ "参考已沉淀"**即可，**不要新增一行重复编号**（如不要加 #14 Anchoring Effect）。本轮（2026-07-30 12:05）就曾误加 #14 与 #11 重复，触发后立即 patch 修正。
- **"已配置技能" ≠ "有参考文件"**：当 SKILL.md 资源链接区只列文件名但 `references/` 下找不到文件时，该技巧处于"挂空"状态——名义上可调用，实际无任何细节支撑。补齐参考应作为下一轮 P1 优先任务，比新增第 N+1 个技巧价值更高。
- **机械话术**：NVC 四步法（事实→情绪→需求→请求）不能念模板，要先自然说话再检查四要素是否齐全。

## 写文件安全注意事项

- **禁止** `terminal` 用 heredoc 写中文（触发 `[HIGH] Confusable Unicode` 安全扫描拦截）。
- **正确**：`write_file` 直接写目标路径，cron 模式 `execute_code` 被阻止。
- **避免单次 write_file 超 8K token**：超时会被截断；拆成多段 `write_file`/`patch` 调用。

## 进化完成判定

- 报告文件存在且 < 12KB
- 至少 1 项本地参考新增/升级
- 至少 1 个新技巧或新场景演练沉淀
- 待合并清单（阻塞 ≥ 5 天时）已发给用户

## 关联资源

- 当前本地 SKILL.md：`~/.hermes/profiles/afu/skills/productivity/afu-customer-service/SKILL.md`（v1.17.0）
- NVC 四步法：`references/nvc-four-step.md`
- RAS 资讯（核验版）：`references/ras-industry-2026-07-30.md`
- 进化报告目录：`~/.hermes/profiles/afu/evolution/`
- 阻塞合并映射：`evolution/references/skill-update-mapping-2026-07-30.md`