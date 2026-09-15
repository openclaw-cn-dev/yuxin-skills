# 2026-08-25 Codex 进化 runbook

**核心结论**：0 新插件 0 升级；AGENTS.md skill 总数从昨日 87 修正为 88（漏算补录 `content-boom-monitor`）；**飞书 bot 被踢出 home 群，全部 6 个 cron 推送集体失败 [230002]**。

---

## 1. 命令序列（与昨日一致的 6 步）

```bash
# 版本 + marketplace
codex --version
codex plugin marketplace list
codex plugin list
codex plugin marketplace upgrade          # 立即返 "No configured Git marketplaces to upgrade."
codex plugin marketplace upgrade --json   # {"selectedMarketplaces":[],"upgradedRoots":[],"errors":[]} = 0 更新
codex update                              # ✅ "changed 2 packages in 5s" + 🎉 success（EPERM 警告是噪音）

# Skills 真实盘点
ls ~/.codex/skills/ | wc -l               # 88（含 .system hidden dir 不会出现在 ls 默认输出）
find ~/.codex/skills -name SKILL.md | wc -l
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l

# 已装插件数量
codex plugin list 2>&1 | awk '/^Marketplace/ {mkt=$0; next} /@openai-/ {
  if ($0 ~ /installed, enabled/) en++
  else if ($0 ~ /not installed/) ni++
} END {print "Enabled:", en, "NotInstalled:", ni}'
# 实际：Enabled: 7  NotInstalled: 140+
```

---

## 2. 今日变更（4 条）

1. ✅ **`codex update` 跑通**（npm changed 2 packages，CLI exe 被旧进程锁）
2. ✅ **AGENTS.md 修复**：补录 `content-boom-monitor`（8-22 漏入 OTHER，88 总数对齐实际 `ls`）
3. ✅ **bundled marketplace 插件全装满**（7/7）→ 无新插件可装
4. ✅ **无 Git marketplace** → upgrade 立即返回

---

## 3. 踩坑 / 新发现

### 3.1 AGENTS.md skill 总数 drift 又一次复现

- **昨日（8-24）日报**：87（24 DEV / 38 MKT / 25 OTHER）
- **今日（8-25）实测**：`ls ~/.codex/skills/ | wc -l` = **88**
- **根因**：8-22 新增的 `content-boom-monitor` 没进 OTHER 段（昨天数错了 / 或者写完忘 add）
- **修复**：直接 patch AGENTS.md OTHER 段，把 `content-boom-monitor` 加进去（24/39/25=88）

**判定脚本**（铁律，以后 cron 都跑一遍）：
```bash
total=$(ls ~/.codex/skills/ | wc -l)
echo "ls 总数: $total"
echo "find SKILL.md 不含 .system: $(find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l)"
echo "三分类加总应 = 第二行数字**"
```

### 3.2 飞书 bot 被踢群 → 全部 6 个 cron 推送集体失败 [230002]

**症状**：`hermes cron list` 全部 6 任务末尾都报 `230002 Bot/User can NOT be out of the chat`。

**判定**：
```bash
hermes cron list 2>&1 | grep -c "230002"
# 输出 6 = 全部 6 个 cron 任务都报这个错
```

**根因**：飞书 bot 应用被老大/平台从 home 群 `oc_529aff7485ccc35de97a9e7233d665dd` 移除。

**修法（老大手动）**：
1. 飞书 → 进入 home 群 → 群设置 → 群机器人 → 添加 → 搜 `cli_aaaefb812938dbcd` → 加回
2. 等下个 cron 周期自动恢复

**铁律**：cron 看到 230002 → 不重试 / 不切换 chat_id / 不动插件配置。直接放 final response 报告，等老大手动拉 bot。

### 3.3 零升级日的处理

今天 7 个 bundled 插件全装满 + 无 Git marketplace + Codex CLI 锁文件未替换 → 0 新插件可装、0 升级可跑。

**日报仍要输出**：明确写"0 新增 / 0 升级 / AGENTS.md 微调 +1" → 老大看到"没新东西"也是有效信号（不是 cron 没跑）。

---

## 4. 待办 / 老大需决策

- ⚠️ **P0：飞书 bot 被踢群** → 老大手动加 bot 回 `oc_529aff7485ccc35de97a9e7233d665dd`
- 💡 `openai-curated` 140+ 未装插件里有 build-web-apps / github / cloudflare / vercel / netlify / sentry / figma / supabase / neon-postgres 等高价值开发插件，按需 `codex plugin add` 装
- 💡 AGENTS.md 三分类总和 N 天对账铁律已写入 SKILL.md，下次 cron 强制走 ls + find 双验证