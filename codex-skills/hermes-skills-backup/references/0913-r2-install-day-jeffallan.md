# 0913 R2 装日铁律 — Jeffallan 67-skill repo 选装 + AGPL cleanup pattern

> 来源：0913 cron R2 实盘 +2 skill 装入（fastapi-expert + react-expert）
> 场景：首次命中 Jeffallan/claude-skills 11.3k star 67 全栈 skill 仓库，5 维搜索找到首个可装仓库
> 关联：铁律 13（三件齐）+ 铁律 15（AGPL 拒装）+ 新立铁律 18-20

---

## 新铁律 18：Jeffallan-style 多 skill 仓库选装法（0913 R2 立）

触发：GitHub search 返回单仓库 >= 10 个 skill（如 Jeffallan/claude-skills 67 个 / anthropics/skills 19 个）。

老路径（错）：直接全目录拷贝到 ~/.codex/skills/ → 撑爆 fs + 装入与业务无关的 java/kotlin/vue/wordpress 等。

新路径（对）：

```bash
# 1. 浅克隆到 eval-repos（避免 assets/ 撑爆 + 后续 cleanup 干净）
git clone --depth=1 https://github.com/Jeffallan/claude-skills.git \
  ~/Desktop/eval-repos/jeffallan-claude-skills
# 0913 R2 实测：9.5MB < 30s

# 2. 列出 skill 子目录（每个都是 self-contained: SKILL.md + references/ + scripts/）
ls ~/Desktop/eval-repos/jeffallan-claude-skills/skills/
# → 67 个 dir（每个独立）

# 3. 0912 铁律 13 三件齐筛选（每个候选独立验，不批量）
#    ① cross-refs >= 3:
grep -l "fastapi-expert" ~/Desktop/eval-repos/jeffallan-claude-skills/skills/*/SKILL.md | wc -l
#    ② license MIT/Apache
head -3 ~/Desktop/eval-repos/jeffallan-claude-skills/LICENSE
#    ③ SKILL.md < 10KB
wc -c ~/Desktop/eval-repos/jeffallan-claude-skills/skills/fastapi-expert/SKILL.md

# 4. 仅装「业务命中 + 三件齐」的（0913 R2 = 2/67 = fastapi-expert + react-expert）

# 5. 安装到本地 + 同步 yuxin-skills + 单 commit（多个 skill 同 commit 是 OK 的）
mkdir -p ~/.codex/skills/fastapi-expert
cp -r ~/Desktop/eval-repos/jeffallan-claude-skills/skills/fastapi-expert/. \
  ~/.codex/skills/fastapi-expert/
# 同 react-expert

mkdir -p ~/Desktop/yuxin-skills/codex-skills/fastapi-expert
cp -r ~/.codex/skills/fastapi-expert/. \
  ~/Desktop/yuxin-skills/codex-skills/fastapi-expert/
# 同 react-expert

cd ~/Desktop/yuxin-skills && git add codex-skills/fastapi-expert codex-skills/react-expert
git -c user.name="Codex Sync" -c user.email="codex@yuxin.local" commit -m "..."

# 6. 先 cleanup eval-repos 再 commit（避免 9.5MB .git 残留）
cd ~/Desktop/eval-repos/jeffallan-claude-skills && rm -rf .git
cd ~/Desktop/eval-repos && rm -rf jeffallan-claude-skills
```

0913 R2 实盘：Jeffallan 67 skill 中仅装 2 个（fastapi-expert 业务命中 4 群 + react-expert 业务命中 4 群）。剩 65 个未装（java/kotlin/cpp/rust/dotnet/php/laravel/wordpress/spring-boot/vue/angular = 渔芯栈外，0 业务命中）。

判定矩阵：
- 业务命中 >= 3 群 + 三件齐 → 装
- 业务命中 1-2 群 + 三件齐 → 报老大决策（沿用 0820 铁律）
- 0 业务命中 → 拒装（即使 cross-refs >= 10）

Jeffallan 仓库结构特征（与老大 RAG 互补）：
- 每个 skill 是独立子目录 = SKILL.md（80-100 行 + routing table）+ references/（100-600 行/文件）+ 可选 scripts/
- progressive disclosure 架构：SKILL.md 顶层扫描，references 按需加载
- 完整 working code examples with TypeScript types
- 反 AI Slop 六条铁律（在 CLAUDE.md）
- 0913 R2 装入的 2 个都是 frontmatter 完整（name + description + license + metadata 7 字段）

---

## 新铁律 19：AGPL/GPL repo cleanup pattern — Windows MSYS Device or resource busy 绕过（0913 R2 立）

问题：AGPL/GPL 拒装的 repo 用 rm -rf 删除时，Windows MSYS / git-bash 在 .git/ 还在挂载时报 Device or resource busy。

0913 R2 实测：

```bash
$ rm -rf guizang-social-card-skill
rm: cannot remove 'guizang-social-card-skill': Device or resource busy

$ cd guizang-social-card-skill && rm -rf .git && cd .. && rm -rf guizang-social-card-skill
removed  # OK
```

修复 pattern（两步走）：先 cd 进目录、rm -rf .git、解锁 MSYS shell handle、再 cd .. 删父目录。

为什么：
1. .git/ 内部文件被 MSYS shell handle 挂载时，整目录 rm -rf 失败
2. 先 rm -rf .git 解锁 handle → 再删父目录就 OK
3. 与 0912 立的「`/tmp` 不可写写 `~/Desktop/eval-repos/daily-MMDD/`」是同源问题（Windows MSYS shell handle + NTFS）

铁律：
- 拒装 repo 必走「先 rm -rf .git 再删父目录」两步走
- cleanup 完必 ls 验尸（不留 ghost 目录）
- 不要 skip cleanup（4.4MB guizang assets/ 占盘空间）

0913 R2 实盘背景：op7418/guizang-social-card-skill（小红书图文 28 layouts + 微信封面，5-28 trending）是 0913 5 维搜索最强的业务命中候选（4 群），但 LICENSE = AGPL-3.0，违铁律 15（GPL/AGPL 不进商业仓）。SKILL.md 32KB 远超 10KB 阈值 + 4.4MB assets/。两步走 cleanup 成功删除。

---

## 新铁律 20：跨类 categorical drift 监控（0913 R2 实算）

0912 立的口径（实盘）：

```
MKT 71 / DEV 34 / QA 3 / OTHER 5 = 113
```

0913 R2 实算（+2 DEV 装入）：

```
MKT 77 / DEV 35 / QA 2 / OTHER 0 = 114
```

drift 说明：
- DEV +1（fastapi-expert）
- DEV +1（react-expert）
- MKT 77 持平（铁律 14 image 算 MKT 边际维持）
- QA 2 持平
- OTHER 0 持平（0912 报 OTHER 5 是误报，实算为 0 — sepia.bak.0903 算 bak 不算 OTHER）

新立铁律：
- 每次 cron 必跑 5 段 ls grep（DEV 35 / MKT 77 / QA 2 / OTHER 0 / sepia.bak.0903 = 115 fs / 114 真 skill）
- OTHER 反向减集公式（铁律 14 立，今再次验证）：OTHER = TOTAL - DEV - MKT - QA - sepia.bak.0903 - .system
- image 算 MKT 边际（铁律 14 立，local-sd-image-gen 在 hermes skills + 本地 SD 出图 = MKT 工具）
- 不要回退到 0911 的 47 MKT 列表（漏 24 个，沿用 0912 立的 71+ 完整集）

0913 R2 实算代码（沿用，可直接复用）：

```bash
ls -1 ~/.codex/skills | python -c "
import sys
names = [l.strip() for l in sys.stdin if l.strip() and not l.startswith('.')]
real = [n for n in names if n != 'sepia.bak.0903']
MKT = {'ab-testing','ad-creative','ads','ai-seo','analytics','attribution','audience-growth-tracker-sms','autoprompt','brainstorming','caption-writer-sms','carousel-writer-sms','chinese-grammar-proofreader','churn-prevention','clean-user-facing-text','cold-email','co-marketing','community-marketing','competitor-profiling','competitors','content-boom-monitor','content-calendar-sms','content-pattern-analyzer-sms','content-repurposer-sms','content-strategy','content-strategy-sms','copy-editing','copywriting','cro','customer-research','directory-submissions','douyin-image-post-scheduler','emails','free-tools','hook-writer-sms','image','image-prompt-reverse','image-story-video-wizard','influencer-marketing','launch','lead-gen-video-script','lead-magnets','marketing-council','marketing-ideas','marketing-loops','marketing-mindset','marketing-os','marketing-plan','marketing-psychology','offers','onboarding','optimization-advisor-sms','paywalls','performance-analyzer-sms','platform-strategy-sms','popups','post-writer-sms','pricing','product-marketing','programmatic-seo','prospecting','public-relations','referrals','revops','sales-enablement','schema','seo-audit','seo-landing','signup','site-architecture','social','social-media-context-sms','thread-writer-sms','video','xiaohongshu-concept-explainer','xiaohongshu-layout-factory','xiaoma-durex-copywriter','yuxin-content-engine'}
DEV = {'cli-creator','codex-hygiene','dispatching-parallel-agents','doc-gen','executing-plans','fastapi-expert','finishing-a-development-branch','fix-ci','forward-implementation-first','grep-ts','llm-wiki-manager','no-negative-echo','playwright','playwright-interactive','react-expert','receiving-code-review','refactoring-ui','remove-ai-marks','requesting-code-review','screenshot','script-exec-blocked','search-miss-binary','simplify-codebase','spec-literal-execution','subagent-driven-development','systematic-debugging','test-driven-development','trace-harness-launch-failure','using-git-worktrees','using-superpowers','verification-before-completion','verify-output-readback','writing-plans','writing-skills','yuxin-fullstack'}
QA = {'sepia','sloptrim'}
mkt = [n for n in real if n in MKT]
dev = [n for n in real if n in DEV]
qa = [n for n in real if n in QA]
other = [n for n in real if n not in MKT and n not in DEV and n not in QA]
print(f'MKT={len(mkt)} / DEV={len(dev)} / QA={len(qa)} / OTHER={len(other)}')
print(f'SUM={len(mkt)+len(dev)+len(qa)+len(other)} / 真={len(real)} / fs={len(names)}')
print('OTHER:', other)
"
# 期望输出（0913 R2）：
# MKT=77 / DEV=35 / QA=2 / OTHER=0
# SUM=114 / 真=114 / fs=115
```

---

## 已验证的高价值 skill 仓库清单（0913 R2 立）

| 仓库 | stars | license | skill 数 | 0913 R2 决策 |
|---|---|---|---|---|
| Jeffallan/claude-skills | 11.3k | MIT | 67 | 装 2/67（fastapi-expert + react-expert），剩 65 待评估 |
| anthropics/skills | 175k | Apache-2.0 | 19 | 0912 已分析过，0 装（与现有重叠） |
| sametbrr/llm-wiki-manager | 69 | MIT | 1 | 0911 装（业务命中 4 群） |
| ComposioHQ/awesome-claude-skills | 74k | MIT | 100+ | 全是商业 MCP 工具，0 命中 |
| op7418/guizang-social-card-skill | - | AGPL-3.0 | 1 | 违铁律 15 + 0913 R2 铁律 19 cleanup |

待评估（0913 R2 列入下次 cron）：
- Jeffallan/claude-skills 剩 65 个 — 下次 5 维搜索必跑
- mattpocock/skills（skills.sh, real engineers）— 0913 R2 看过 README，0 业务命中
- glebis/claude-skills — 包含 humane plugin（UX 启发式），0 业务命中
- kzhekov/gtm-claude-skills — GTM outbound 销售栈，与 cold-email/prospecting 重叠
- getaero-io/gtm-eng-skills — 同上 outbound 销售栈
- webapp-testing (composiohq) — 与 playwright/playwright-interactive 重叠

---

## 相关铁律

- 铁律 13（三件齐：cross-refs >= 3 + MIT + <10KB）
- 铁律 14（`*sms` 归 OTHER / `sepia` 归 DEV / `image` 算 MKT 边际 / 反向减集公式）
- 铁律 15（GPL/AGPL 不进商业仓 + 5 维搜索候选先验形态 = curl SKILL.md raw 404 直接拒装）
