# 2026-08-27 Codex Evolution Runbook

## 当日运行快照

- CLI：`codex-cli 0.149.1`（doctor 报 `0.150.0 available`，**未升级**——留给老大决策）
- Marketplace：2 → **3**（新增 `openai-primary-runtime`）
- 启用插件：14 → **19**（新增 5 个 primary-runtime 插件：documents/pdf/spreadsheets/presentations/template-creator）
- 本地 skill：88 → **90**（新增 chinese-grammar-proofreader + clean-user-facing-text）
- AGENTS.md：74 → **76 行**（新增 Q&A 分类 + primary-runtime 段）

## 关键发现

### 1. 🆕 Codex 0.149.1 自带第 3 套 marketplace `openai-primary-runtime`

之前日报一直只看 `openai-bundled` + `openai-curated`，8-27 才意识到 Codex 默认装 3 个 marketplace（`~/.codex/config.toml` 已有 `[marketplaces.openai-primary-runtime]` 段，源类型 local，路径 `~/.cache/codex-runtimes/...`）。

**5 个插件默认 enabled**（无需手动 `codex plugin add`）：
- documents（docx 读写，1 skill）
- pdf（PDF 读写，1 skill）
- spreadsheets（xlsx 读写，2 skills）
- presentations（PPT 制作，1 skill）
- template-creator（模板创建器，1 skill）

**业务价值**：yuxin-social-platform 的数据看板 / 报告导出，未来可直接调用这些插件生成 Excel 报告 / PDF 周报 / PPT 月度复盘——目前还未对接，标记为 P2 潜力。

### 2. 🆕 新增 2 个本地 skill 来源查明

`chinese-grammar-proofreader`（中文病句辨析，23KB）+ `clean-user-facing-text`（文本清洗，5KB），时间戳 `8月 26 09:03`，**疑似昨日 cron 装 openai-curated 时**额外拉下来的。

**确认路径**：对比 8-26 AGENTS.md 列表（88 个）vs 今日 `find ~/.codex/skills/`（90 个），差集即这 2 个。

**8-26 日报漏报原因**：昨日日报 `Skills 总览 88 个，今日修复 +1` 实际是 87→88（补 content-boom-monitor），同时这 2 个 skill 已在昨日 9 点后悄悄落到 `~/.codex/skills/`，但日报抓取时序没覆盖。

**铁律（8-27 立）**：日报 skill 计数**永远用当日实时 find**，不要相信昨日日报里的数字——可能有"静默新增"未捕获。

### 3. 🆕 三分类新增 Q&A（质量类）

| 分类 | 数量 | 占比 |
|---|---|---|
| DEV 开发工程 | 24 | 27% |
| MKT 营销自媒体 | 39 | 43% |
| **Q&A 质量** 🆕 | 2 | 2% |
| OTHER 业务其他 | 25 | 28% |

**为什么 Q&A 重要**：渔芯自媒体平台所有输出（小红书爆款 / 抖音脚本 / 客户邮件 / 飞书推送）都经过文案环节，Q&A 类 skill 是**最后一道质量关卡**——chinese-grammar-proofreader 专门捉中文病句，clean-user-facing-text 清不可见 Unicode + 文本打磨。

### 4. ⚠️ Codex exec 真实调用超时

```
$ echo "say hello in 3 words" | codex exec --skip-git-repo-check
[Command timed out after 60s]
```

**判定**：
- `codex doctor` 跑通（CLI 自身 OK）
- `codex exec` API 调用卡 60s+ 超时
- model 显示 `gpt-5.6-sol`，provider `openai`（OpenAI 协议后端）
- 跟 8-26 实测的"WebSocket timed out"症状一致——网络层问题（VPN/代理/DNS），不是 cron 要修的
- **不阻塞本次 cron**：日报出，AGENTS.md 同步，老大自己看 exec 状态

### 5. ⚠️ 飞书 home group 仍 230002

```
$ hermes send --to "feishu:oc_529aff7485ccc35de97a9e7233d665dd"
hermes send: Feishu send failed: [230002] Bot/User can NOT be out of the chat.
```

沿用 8-25 铁律：老大手动去飞书 home 群加 bot (`<FEISHU_APP_ID>`) → 下个 cron 自动恢复推送。

## 8-27 新增铁律

1. **marketplace 必查 3 个（不是 2 个）**：openai-bundled + openai-curated + **openai-primary-runtime**（Codex 0.149.1+ 默认装）
2. **skill 计数永远用实时 find**：不要相信昨日 AGENTS.md 数字，差异 > 1 时必须找具体增量
3. **Q&A 质量类是新增维度**：AGENTS.md 三分类 → 四分类（DEV/MKT/Q&A/OTHER）

## 8-27 未做事项（给老大决策）

- Codex CLI 0.149.1 → 0.150.0 小版本升级（cron 不自动跨小版本）
- Hermes 0.19.0 → 0.20.5 大版本升级（沿用 8-25 铁律，老大手动 ZIP fallback）
- 飞书 home group 加 bot（沿用 8-25 铁律，老大手动加）
- `codex exec` 60s+ 超时（网络层，非 cron 阻塞）

## 备份同步

- ✅ AGENTS.md → `~/Desktop/yuxin-skills/codex/AGENTS.md`（cp 完成，6594 字节）
- ✅ 2 个新 skill → `~/Desktop/yuxin-skills/codex-skills/`（cp 完成）
- ⏳ yuxin-skills git commit + push —— 留给老大手动（撞 push protection 风险）
