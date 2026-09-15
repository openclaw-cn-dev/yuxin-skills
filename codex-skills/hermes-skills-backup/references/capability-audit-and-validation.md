# Codex 能力盘点与验收（2026-08-10 实测）

## 1. 统计口径：只数“当前启用”，不要扫完整 cache

`~/.codex/plugins/cache/` 会保留已卸载插件、旧版本和其他 marketplace 的缓存。直接递归统计会虚高。

正确顺序：

1. 用 `codex plugin list` 获取状态为 `installed, enabled` 的插件；也可读取 `config.toml` 中已启用的 `[plugins."name@marketplace"]`。
2. 只进入这些插件当前激活版本目录，递归统计 `SKILL.md`。
| 本地 skills | `~/.codex/skills/<name>/` | 有有效 `SKILL.md`；排除 `.system` 和半成品 |
| 插件 skills | `~/.codex/.tmp/plugins/plugins/` + `~/.codex/.tmp/bundled-marketplaces/openai-bundled/plugins/`（8-16 实测路径，旧 `~/.codex/plugins/cache/` 已不存在） | 先从 `codex plugin list` / `config.toml` 确定 `installed, enabled`，再统计这些插件当前版本 |
5. 分类固定为：开发 / 营销 / 浏览器 / 其他。名称不明确时读 frontmatter/description，不靠目录名猜。

## 2. 安装本地 skill：必须拿完整子树

只下载 `SKILL.md` 容易漏掉 `references/`、`scripts/`、`assets/`，形成“看似已装、调用时报缺文件”的半成品。

安装流程：

1. 读取仓库 tree，确认许可证、`SKILL.md` 和所有支持文件。
2. 下载该 skill 的完整子树；Git clone 不稳时，改用 GitHub Contents API，API 限流时用 raw URL 拉明确路径。
3. 扫描 `SKILL.md` 中出现的 `references/`、`scripts/`、`assets/` 字面路径，确认全部存在。
4. 对附带的 Python/JS 脚本跑语法检查；不要把 `__pycache__`、构建产物写入备份仓库。

## 3. 真实验收：版本号不算通过

每次新增插件或 skill 后必须跑：

1. `codex plugin list`：目标插件必须是 `installed, enabled`。
2. 检查全部本地 `SKILL.md`：首行 YAML frontmatter 必须由 `---` 开始，并含 `name`、`description`。
3. 用 `codex exec --ephemeral -s read-only -o <output-file> "只回复：CODEX巡检通过"` 做真实模型调用。
4. 检查 stderr 是否出现 `failed to load skill`；如有，修 frontmatter/引用文件后重跑，直到消失。
5. 分开报告两件事：模型调用是否成功、需要 OAuth 的插件是否已认证。前者成功不代表后者就绪。

## 4. 上下文预算：总数不是越大越好

若真实调用出现：

`Exceeded skills context budget ... N additional skills were not included`

说明“已安装总数”已经大于本轮模型可见能力。此时：

- 停止为凑数量继续安装同质插件/skills。
- 报告“已安装总数”和“本轮不可见数”，不要把安装数冒充可用数。
- 按当前项目保留/启用相关插件，禁用重叠、低频或需要但尚未配置认证的插件。
- 优先补真正缺口；新增能力必须能替代旧能力或给活跃项目带来唯一价值。
- 不要用第二套 skills 目录规避上限；它只会扩大索引污染。

## 5. Marketplace 与备份避坑

- Codex 0.142.5 的 `codex plugin marketplace upgrade` 没有 `--dry-run`；先看 `--help`，再执行实际 upgrade。
- 新 marketplace/插件不能只按“Developer Tools”标签盲装，还要检查：Windows 是否适用、是否与现有能力重叠、是否服务当前项目。
- 备份 push 前排除缓存/编译产物并做凭证扫描。若 GitHub Push Protection 指向旧历史，禁止绕过；保留本地提交，另开清洁历史修复，而不是把旧密钥继续推上去。
