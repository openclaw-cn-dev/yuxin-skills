---
name: ***SECRET***
description: 'CRITICAL tool fact for any skill curator pass: skill_manage action=delete physically shutil.rmtree()s the skill directory — it does NOT archive to .archive/. Task briefs claiming "delete = archive" are wrong for current builds. Safe merge workflow + recovery sources documented. Trigger: any skill consolidation/curator/merge pass, any "archive a skill" request, recovering deleted skills.'
version: 1.0.0
author: curator incident 2026-10-16
tags: [skills, curator, delete, rmtree, archive, recovery, pitfall]
---

# skill_manage delete = rmtree（不是归档）

## 事故实录（2026-10-16）

一次 umbrella 合并整理中，按任务简报「delete = 归档到 .archive/」的认知执行了 7 次 `skill_manage action=delete`。实际行为（源码 `hermes-agent/tools/skill_manager_tool.py` `_delete_skill`）：**`shutil.rmtree(skill_dir)` 物理删除**。7 个已 merge 的 skill 包被销毁。事后恢复：仅 2 个可完整找回（Codex 同步仓 + state.db skill_view 快照），3 个只能重建恢复存根，2 个部分丢失。

## 安全合并工作流（替代顺序）

1. 先把内容（目录级 `mv` 或逐文件 `cp`）放进 umbrella 的 `references/` / `templates/` / `scripts/`。
2. **归档 = `mv <skill_dir> ~/.hermes/skills/.archive/<name>`（terminal 手动 mv）**——skill 注册表由文件系统派生，mv 出去即等于注销，且保留可恢复副本。
3. **之后不要再调 `skill_manage action=delete`**：要么报 not found，要么（在别的 skills root 找到同名时）把 .archive 里的副本也 rmtree 掉。
4. umbrella patch + absorbed 声明照常做；只有「真垃圾且已有其他备份」才允许直接 delete。

## 事后恢复源（按可靠性排序）

1. **state.db 的 skill_view tool 结果**：`messages` 表 `role='tool' AND tool_name='skill_view'`，content 是 JSON（`content` 键 = SKILL.md 全文，`linked_files` 键 = 支持文件**清单**但不含内容）。用 assistant 请求（`role='assistant' AND tool_calls LIKE '%skill_view%'`）里 arguments.name 匹配 + tool_call_id 关联定位。
2. **Codex 同步仓 `/Users/hua/yuxin-skills/hermes/skills/`**：agent-tool-sync 每日推的子集，滞后数天——恢复整包（含 references）最可靠的源。
3. maodou/zhenglishi 等 profile 的 state.db 与 sessions/*.jsonl（命中率低，本次为 0）。
4. 不可用：Trash（rmtree 不经过）、APFS 本地快照（无）、Time Machine（无权限/未配）。

## 恢复存根纪律

找不回全文时，只允许写「恢复存根」：显式标注 `⚠️ 恢复说明`、只写删除前**实际读到过的**内容骨架、给回填指引（哪个会话/哪个活文档可考古）。禁止编造细节冒充原文。
