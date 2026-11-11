---
name: machine-migration-audit
description: |
  跨机器迁移后的全量资产盘点审计 + 运行面断点扫描（如 Mac→Windows 换机）。触发条件：换机/搬家后用户问"数据是不是全迁过来了""检查所有项目是否迁移完整"，或需要对迁移做完整性验证出报告。
  方法论：Phase 1 盘点审计（找迁移台账→逐项核对磁盘实况→git 仓可用性验证→符号链接分类甄别→数据库行数+内容抽样比对→打包残留识别→出分级报告）；Phase 2 运行面扫描（cron 错误归因→旧平台路径残留→常驻服务/网关核对→记忆库基线→出断点清单）。渔芯 2026-11-10 Mac mini→EVO-X3 (Windows) 全公司盘点实战沉淀。
version: 1.2.0
author: 渔芯
license: MIT
tags: [migration, audit, git, symlink, windows, mac, inventory]
---

# 跨机器迁移资产盘点审计

## 核心原则

**台账是基准，磁盘是真相，两者对不上的每一项都要给出解释**（已解释 / 真缺失 / 打包残留未解包 / 垃圾）。

## 审计流程（按序执行）

### 1. 找迁移台账/清单
迁移执行者通常会留台账（如 `D:\yuxin\company\资产迁移台账-YYYYMMDD.md`），记录批次、源路径、大小、状态。没有台账则直接从目标盘顶层结构反推。

### 2. 逐版块核对磁盘实况
对台账登记的每个版块：实际文件数 + 实际大小 vs 台账登记值。**登记 165GB 实测 108.9GB 不一定是缺失**——差额常是还在打包未删的 tar（本项目差额 56GB ≈ 两个 tar 75.9GB 的未释放部分 + 压缩率）。先识别打包残留再下结论。

⚠️ 目录树大小统计必须容错断链接：`os.walk(p, onerror=lambda e: None)` + `getsize` 包 try/except（迁移过来的 Mac 符号链接在 Windows 上全是断链，裸统计必炸 FileNotFoundError）。

### 3. Git 仓库可用性验证（跨机必踩坑）
- 统计 `.git` 目录数 → 逐仓跑 `git log --oneline -1` 验证
- **坑 1 — dubious ownership**：跨机拷贝后所有仓报 `detected dubious ownership`。批量豁免：逐仓 `git config --global --add safe.directory <绝对路径>`。
- **坑 2 — 清空豁免自坑**：`git config --global --unset-all safe.directory` 会清掉**全部**豁免（包括历史加的）；重新逐条 add 即可，但要知道这步会互相覆盖，先清后加按一个脚本一口气做完。
- **坑 3 — shell=True 管道污染**：Windows git-bash 环境 `subprocess.run("git ... | head -3", shell=True)` 可能落到 cmd 执行，`head` 报乱码"不是内部或外部命令"。**统一用列表参数** `subprocess.run(["git", "-C", repo, "status", "--porcelain"])`。
- **坏壳识别**：`.git` 存在但 `git log` 报 `not a git repository` = 损坏壳（本例 2/94），单独标记。
- **dirty 仓甄别**：`git status --porcelain` 非空的仓是 Mac 时代就有的未提交工作（迁移前状态），**不是迁移丢失**，报告里单列建议后续逐仓 commit。
- 无 remote 的仓（本地仓）正常存在，不算问题。

### 4. 符号链接分类甄别（不要被断链总数吓到）
Mac→Windows 迁移后符号链接 100% 断。先分类再处置：

| 类别 | 识别特征 | 处置 |
|---|---|---|
| 测试垃圾 | `.pytest_tmp`、`SingletonLock/Cookie`、浏览器 profile 锁 | 直接删 |
| venv 内部 | 路径含 `.venv`、指向 homebrew python | 可删，新机重建 |
| 相对断链 | 指向项目内相对路径（构建产物） | 低优先级，用到时重建 |
| **真数据链接** | 指向 `\Users\<mac用户>\...` 且源是数据非垃圾 | **逐一核对源数据是否已实体迁入**，没有则补迁或删链接 |

实例数据：总断链 128 → 真数据链接仅 7，其余 105 条 pytest_tmp + 16 条 venv/锁/相对。**报告只列真数据链接**。

### 5. 数据库类资产验证（行数 + 内容抽样双验证）
行数对上不等于内容一致，做双层：
1. 行数对比：`SELECT COUNT(*), MIN(id), MAX(id) FROM <table>` 新旧库对比
2. 内容抽样：按 id 逐条取 content 做 md5 对比（前 200 条足够）
3. Mnemosyne/记忆库另需验证向量覆盖（见 mnemosyne-cross-machine-sync §八）

### 6. 打包残留识别（迁移完成后的空间释放项）
中途打包产物（`dotgit.tar`、`*-v3.tar`）在解包实体化后即冗余。核对 tar 内容已完整落盘（抽查条目数/大小 vs 现树）后列入"可释放空间"清单，**删除前向用户确认**。

### 7. 出分级报告
- ✅ 已迁移并验证通过（含验证方法）
- ⚠️ P1 真缺失/真数据断链（需用户决策补迁或放弃）
- ⚠️ P2 迁移前历史状态（dirty 仓等，非迁移问题）
- 💡 P3 可释放空间/可清理垃圾（附大小）
- 附磁盘水位（shutil.disk_usage）

## 8. Phase 2：运行面断点扫描（盘点通过后必做）

数据迁齐 ≠ 系统能跑。盘点通过后进入 Phase 2，产出断点清单 + 修复顺序：
1. cron 错误分类（Script not found / exit 1 / 429 自愈 / timeout，先 `os.path.isfile` 验证归因）
2. 旧平台路径残留扫描（剔除档案目录后统计"活文件"，勿被 2 万+ 档案命中吓到）
3. 常驻服务/网关端口核对（launchd 类在新机无等价物，逐项列"是否重建"供用户拍板）
4. 记忆库基线（压缩 cron 断链会静默堆积 working_memory，先手动压再修 cron）

详见 `references/post-migration-runtime-scan.md`（含 cron 分类法表、Mac→Win 路径对照表、EVO-X3 实测 637 活文件/876 条超限案例）。

## Pitfalls

1. **不要只对台账数字做减法**——先解释差额（tar 残留/压缩/垃圾），再判缺失。
2. **断链总数是噪音，真数据链接才是信号**——分类后报告。
3. **git 批量豁免用列表参数不用 shell 管道**（Windows cmd/bash 混环境）。
4. **read_file 工具对中文文件名可能误报 File not found**——用 execute_code 的 python `open()` 读中文文件。
5. **venv/依赖/插件不随数据走**——运行面恢复另见 mnemosyne-cross-machine-sync §八。
6. **dirty≠丢失**——未提交改动是迁移时点快照，迁移本身不会丢 working tree。

📎 完整审计实录（EVO-X3 2026-11-10：108.9GB/127 万文件、94 仓、141 链接、76GB 残留的具体数字与脚本）见 `references/evox3-audit-20261110.md`。
