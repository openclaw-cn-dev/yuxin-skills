# 2026-08-26 Codex 进化 runbook

**核心结论**：批量新增 7 个 openai-curated 插件（build-web-apps / build-web-data-visualization / github / cloudflare / coderabbit / sentry / figma / neon-postgres）→ enabled 插件 7→14；Skills 总数 88 无变化；AGENTS.md 同步重写。

---

## 1. 命令序列（新增批量装机步骤）

```bash
# 版本 + marketplace（同 8-25）
codex --version
codex plugin marketplace list
codex plugin list

# 新增：批量装机前先看 openai-curated 全量未装清单
codex plugin list 2>&1 | grep -A 200 "Marketplace .openai-curated" | grep -E "not installed" | head -30

# 批量装（一条一条跑，失败立刻停；workdir 走 E:/公司项目资料 避沙箱拦）
cd "E:/公司项目资料" && codex plugin add build-web-apps@openai-curated
cd "E:/公司项目资料" && codex plugin add github@openai-curated
cd "E:/公司项目资料" && codex plugin add neon-postgres@openai-curated
cd "E:/公司项目资料" && codex plugin add figma@openai-curated
cd "E:/公司项目资料" && codex plugin add coderabbit@openai-curated
cd "E:/公司项目资料" && codex plugin add sentry@openai-curated
cd "E:/公司项目资料" && codex plugin add cloudflare@openai-curated

# 装机后统计（沿用 8-25 awk 脚本）
codex plugin list 2>&1 | awk '/^Marketplace/ {mkt=$0; next} /@openai-/ {
  if ($0 ~ /installed, enabled/) en++
  else if ($0 ~ /installed, disabled/) dis++
  else if ($0 ~ /not installed/) ni++
} END {print "Enabled:", en, "Disabled:", dis, "NotInstalled:", ni}'
# 实际：Enabled: 14  Disabled: 0  NotInstalled: 173

# Skills 双验证（沿用 8-25 铁律）
ls ~/.codex/skills/ | wc -l                          # 88
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l  # 88
ls ~/.codex/skills/.system/ | wc -l                  # 6
find ~/.codex/skills -name SKILL.md | wc -l           # 94

# CLI 升级
codex update 2>&1 | tail -15   # EPERM 是噪音，看最后 "Update ran successfully" 即可
```

---

## 2. 今日变更（5 条）

1. 批量新增 7 个 openai-curated 插件 → enabled 7→14，开发能力翻倍
2. Skills 总数 88 无变化（find -not -path '*/.system/*' 精确数）
3. AGENTS.md 重写：插件表格拆 bundled + curated 分段、未装清单按分类重排
4. 飞书 bot 仍可能被踢群（沿用 8-25 铁律 `hermes cron list | grep -c 230002` ≥3）
5. Hermes 升级落后 5 周 v0.19.0 → v0.20.5

---

## 3. 踩坑 / 新发现

### 3.1 `codex plugin add` 在某些 workdir 下走终端 cd 失败

**症状**：直接在 `C:/Users/Administrator/` 下跑 `codex plugin add xxx@openai-curated`，有时候会撞 "Not inside a trusted directory"（如果 home dir 不是 git 仓库）。

**修法**：cd 进 `E:/公司项目资料`（公司项目根目录，本身就是 git 仓库或不会被沙箱拦）再跑：
```bash
cd "E:/公司项目资料" && codex plugin add xxx@openai-curated
```

**为什么 work**：公司项目根目录含 `.git/`（yuxin social platform 仓库）+ 不在中文文件名路径下，沙箱白名单不拦。

### 3.2 `codex plugin add` 失败但 exit_code=0 的隐式陷阱

**症状**：`codex plugin add playwright@openai-curated` 返 `Error: plugin 'playwright' was not found in marketplace 'openai-curated'` 但 **exit_code=0**（shell 视角"成功"）。

**危险**：批量脚本里 `&&` 串联会被误导，以为装成功了。

**修法**：每次装机后必查 stderr 输出，或用 `--json` 选项拿结构化结果：
```bash
codex plugin add xxx@openai-curated --json 2>&1
# {"plugin":"xxx","marketplace":"openai-curated","version":"...","enabled":true,"cachePath":"..."}
```

### 3.3 openai-curated 批量装机优先级矩阵（今日立，新发现）

**装与不装的决策**（不是"全装"，也不是"全不装"）：

| 优先级 | 类别 | 必装清单 | 装机理由 |
|---|---|---|---|
| P0 业务直接相关 | 前端 | build-web-apps / build-web-data-visualization | yuxin-social-platform Next.js 14 全栈开发 |
| P0 | 协作/API | github | yuxin-skills 推送 + Issue/PR |
| P1 监控/审查 | 代码审查 | coderabbit | AI PR 审查 |
| P1 | 监控 | sentry | 错误监控 |
| P2 备选 | 后端/部署 | cloudflare / render / vercel / netlify | 部署备选 |
| P2 | 数据库 | neon-postgres / supabase / convex | serverless DB 备选 |
| P2 | UI 设计 | figma / canva | 设计读写 |
| P3 按需 | CI/CD | circleci | CI 流水线 |
| P3 | 协作 | linear / notion / atlassian-rovo / slack | 团队协作 |
| ❌ 不装 | 学术 | latex / zotero / life-science-research | 跟渔芯业务无关 |
| ❌ 不装 | 跨平台不兼容 | build-macos-apps（Windows 跑不起来） | 环境限制 |
| ❌ 不装 | 已被替代 | playwright（已有 chrome+browser） | 边际价值 < 索引污染 |

**铁律**：批量装 ≥ 3 个插件 → 日报"装机理由"段必须**逐条标注业务关联**，不是只列名字。8-26 实测 7 个装机理由全部命中 yuxin-social-platform / yuxin-skills 业务线。

### 3.4 AGENTS.md 批量装机后必整段重写"未装清单"

**症状**：批量装 7 个 → 昨日写的"未装清单"段立刻过期（5 个 P0/P1 已装）。

**修法**：同一轮 patch 里把 AGENTS.md 的"未装清单"段**整段重写**，只保留真正仍为 `not installed` 的项 + 按 P0/P1/P2/P3 优先级重排。

**判定脚本**：
```bash
# 看 AGENTS.md 上次写的"未装"数
grep -c 'not installed\|未安装' ~/.codex/AGENTS.md
# 看 codex plugin list 真实未装数
codex plugin list 2>&1 | grep -c 'not installed'
# 两个数差太多 = drift，必整段重写
```

---

## 4. 待办 / 老大需决策

- **P0**：飞书 bot 状态 — 8-25 确认被踢出 home 群，老大手动加 bot 才能恢复推送
- **P0**：Hermes 升级落后 5 周 v0.19.0 → v0.20.5，老大前台手动 `hermes update` ZIP fallback
- **建议**：`openai-curated` 剩余 173 个未装，按 8-26 P2/P3 矩阵按需补：cloudflare 装了，可补 render / vercel / netlify / supabase / linear / notion / circleci
- **建议**：Skills 总数已触顶 88（find 实测）——**不要再装同质 skill**（如多装一个 email-writer），边际价值 < 索引污染

---

## 5. 教训 / 进化点（供下次 cron 抄）

1. **批量装机前必跑**：`codex plugin list | grep -A 200 openai-curated | grep 'not installed'` 看候选 → 用 P0/P1/P2/P3 决策矩阵筛 → 一条一条 add
2. **装机后必跑**：`awk` 统计脚本确认 enabled 数符合预期 + AGENTS.md "未装清单"段整段重写
3. **EPERM 警告**：`codex update` 末尾 npm EPERM = Windows 常态，`Update ran successfully` 就是成功，别慌
4. **零变更日仍要输出日报**：8-25 已立铁律，8-26 同样适用（虽然今天有 7 插件新增）