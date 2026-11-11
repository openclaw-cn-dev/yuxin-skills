# 铁律 185-187（1111 cron 旺财lane 新增）

## 铁律 185：分体式撞装闭环判据 = 实跑痕迹，断链必 grep 验证

1111 实锤：11-05 兄弟 lane 装的 14 个 chubby-*（chubbyskills 分体式拆装）全部断链——每个子 skill 的 scripts 引 `chubby_common` 共享模块，ROOT 回退链 `os.path.isdir(join(SKILL_ROOT,"chubby_common")) else dirname(SKILL_ROOT)` 指向 `~/.codex/skills/`（无 chubby_common）→ "装了等于没装"（铁律 153 分体式整组装的反面教材）。

**闭环判据（撞装二选一）**：
- 留「实跑痕迹」份：`quickstart`/pytest/CLI --help 真跑通过的拷贝（1111 本 lane 整仓 router 版 quickstart 6/6 全过）
- 删「断链」份：删前必 grep 验证 `grep -rh "chubby_common\|from tools" <份>/` + 检查 ROOT 回退目标存在性
- 铁律 178 的「保实跑痕迹」扩展：分体式仓单装子目录 ≠ 可独立运行，共享模块断链判定 = 引用模块在 ROOT 回退链上不存在

**断链自查一行命令**：
```bash
grep -rh -E "chubby_common|from tools|import tools" <skill份>/ | grep -v "^#" | head -5
ls <ROOT回退目标>/chubby_common 2>/dev/null || echo "断链"
```

## 铁律 186：「三拷贝 md5 统一」声明 ≠ 实测统一（铁律 169 二次实锤，本地文件操作版铁律 172）

1111 实锤：兄弟 lane 09:11 commit 声明「三拷贝 md5 统一」，本 lane 09:20 实测 repo 份 md5=1466c2d vs Hermes devops 份+知识库 scripts 份=c57a8914（两份 stale：含 chubby-* 14 归 VERT 旧名单 + 缺 chubbyskills DEV 归位）——**声明不是证据，必须自己 md5sum 三份实测**（1109 铁律 169「DEV62 收敛只进仓拷贝」同款事故第二次实锤 = 兄弟 lane 系统性漏 cp）。

**修复方向（沿铁律 169）**：repo 超集重拷到 stale 份，禁反向覆盖；三份齐修后必三份各实跑一遍（不止 md5，防"内容同但路径错"）：
```bash
md5sum <repo>/scripts/skill-categorize.py <hermes_devops>/scripts/skill-categorize.py <知识库>/scripts/skill-categorize.py | awk '{print $1}' | sort -u | wc -l   # 期望 1
# 三份各 cd 到自己目录实跑 python skill-categorize.py，Total 一致才算收敛
```

## 铁律 187：镜像对账按目录名 diff，不看目录数

1111 实锤：codex-skills 镜像 220 项 vs fs 243 项，目录数差 23 引恐慌；实际 name diff 抓出 27 项欠账（镜像多 2 个 infra 目录 golive/hermes-skills-backup + fs 多 1 个 sepia.bak.0903 + 25 个 fs-only 真欠账：13 short-drama* + xiaoma-durex-copywriter + xiaoyuan/xihuan/xingji/xitong/xuanhuan/xuanyi/yule-manju + yuxin-content-engine/fullstack + zhaidou/zhongtian-manju + zh-tech-writing，沿 sync bot 历史误删）。

**对账正解**：
```bash
diff <(ls -d ~/.codex/skills/*/ | xargs -n1 basename | sort) \
     <(cd <镜像>/codex-skills && find . -maxdepth 1 -type d ! -name '.' ! -name 'golive' ! -name 'hermes-skills-backup' | sed 's|^\./||' | sort)
# infra 目录白名单排除后 diff=0 才算对齐；目录数永远对不上（镜像含文件项），禁用 count 比对
```

---
*1111 cron 旺财lane 立铁律编号查重：grep max=184 → 新号 185-187 起始（铁律 151/164 流程）*
