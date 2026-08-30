---
name: research-collection
description: '渔芯资料收集技能 — 高效搜集行业信息、公司情报、技术资料，整理成结构化报告。触发条件：需要收集行业信息、公司背景、技术文档、竞品资料、市场数据时加载。覆盖渔芯RAS养殖、AI产品、市场调研场景。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.1.0"
---

# 渔芯资料收集技能

## 职责定位
高效搜集行业信息、公司情报、技术资料，整理成结构化报告。

## 核心工具

### 1. 网络搜索（Web Search）
- 搜索引擎深度抓取
- 行业报告网站
- 学术数据库

### 2. 竞品资料收集
按竞品清单批量搜索：
- 产品功能对比
- 定价策略
- 用户评价
- 公司背景

### 3. 技术文档检索
- 官方文档
- GitHub代码
- 技术博客
- API文档

## 输出格式

### 结构化调研报告
```
# [主题]调研报告

## 1. 核心发现
（3-5条最关键结论）

## 2. 详细信息
### 2.1 [子主题]
### 2.2 [子主题]

## 3. 数据来源
| 来源 | 链接 | 可靠性 |
|------|------|--------|
| XXX | url | 高/中/低 |

## 4. 知识库更新
（存入知识库的关键知识点）
```

## 调研原则
1. 多源交叉验证——不依赖单一来源
2. 优先一手数据——官方文档>媒体报道>道听途说
3. 知识溯源——每条知识标注来源URL
4. 积累优于输出——调研报告存入知识库持续迭代

## GitHub + arXiv 实操 pitfalls（来自 AI 出 3D 模型持续调研，2026-08-29）

### Pitfall 1: GitHub API 的 `size` 字段单位是 **KB**，不是 MB
```bash
# 错误解读：size=796917 → "796KB"
# 正确解读：size=796917 → "796917 KB ≈ 796 MB"
# 陷阱场景：gh-pages 项目页面（README 视频/缩略图）体积动辄上百 MB
```
**正确做法**：报告仓库体积时统一标注 KB 原值，再换算成 MB/GB。不要省略单位。

### Pitfall 2: arXiv API 必须用 `https://` + `-L` 重定向
```bash
# 错误（301 重定向丢 body）：
curl -s "http://export.arxiv.org/api/query?..."   # 0 bytes 空响应

# 正确：
curl -sL "https://export.arxiv.org/api/query?..."  # 200 OK 真实数据
```
HTTP 端点已永久重定向到 HTTPS，不带 `-L` 等于丢 body。所有 cron 必须用 `-L https://`。

### Pitfall 3: GitHub 项目页面与代码仓库可能分离
很多学术论文的开源分两层：
- **主仓**（如 `fraunhoferhhi/KISS-GS`）= gh-pages 项目页面，README 写"carries no source"
- **真代码仓**（如 `w-m/ffsplat`）= 实际 PyTorch 代码，通常通过 README 徽章反向链出去

**排查 SOP**：
```bash
# 1. 抓主仓 README 看是否有"carries no source"声明
curl -sL https://raw.githubusercontent.com/<org>/<repo>/main/README.md | head -20
# 2. 扫描 README 中的 GitHub 徽章链接（shields.io 模式 → 真实仓库名）
# 3. 对真代码仓重跑详情 API + license + size
```

### Pitfall 4: Hugging Face API 在沙箱环境通常不可达（IPv4+UA 都不行）
- `curl https://huggingface.co/api/spaces?search=...` → exit 28 timeout
- **不要反复重试**，直接标"D · 永久放弃"，改走浏览器或归档数据
- cron 自动化场景下，HF 通道视为不存在

### Pitfall 5: arXiv 论文开源追踪有 2-8 周滞后规律
- 论文发布后，开源代码平均 2-8 周内出现（顶级机构/Fraunhofer HHI 通常 < 2 周）
- 监控命令：`curl 'https://api.github.com/search/repositories?q=<PaperName>+in:name,description&sort=updated'`
- **同名陷阱**：搜论文名常碰到无关同名项目（"AquaFlow" = 水处理厂管理），要二次过滤 description

### Pitfall 6: 积累型报告的文件管理惯例
渔芯"AI 出 3D 模型"主题采用**双文件策略**：
1. **累积主文件**（`AI出3D模型研究_<起始日期>.md`）：每次增量都 `cat >>` 追加到末尾（保持文件连续性）
2. **日期归档文件**（`AI出3D模型研究_<本次日期>.md`）：本次飞书交付用，结构精简 + 指向主文件

这样既满足飞书按日期归档，又能在主文件看到完整演进。

## 触发关键词

### GitHub
```bash
curl -s 'https://api.github.com/search/repositories?q={关键词}&sort=stars&order=desc&per_page=15' -o /tmp/gh.json
# 关键字段：stargazers_count / license.spdx_id / pushed_at / topics
```

### arXiv（⚠️ 必须 -L 跟重定向）
```bash
curl -sL 'https://export.arxiv.org/api/query?search_query=all:{关键词}&sortBy=submittedDate&max_results=8' -o /tmp/arxiv.xml
# 不带 -L 会返回 0 bytes（HTTP 301 强制 https）
```

### HuggingFace Spaces（❌ API 永久不可达）
- `https://huggingface.co/api/spaces` 连续多期 cron 返回 0 bytes
- 改用 `web_search 'huggingface.co spaces text-to-cad'` 兜底

详见 `references/cron-execution-cheatsheet.md` 完整命令模板 + 踩坑。

## 鱼芯"路径决策矩阵"框架

开源自技术选型调研时，**Stars × License × 活跃度 × 适配度**四维评分：

| 评估项 | 鱼芯默认偏好 |
|--------|--------------|
| License | MIT > Apache-2.0 > NOASSERTION(需法务) > GPL/AGPL(剔除) |
| 活跃度 | 日更 > 周更 > 月更 > 停滞(剔除) |
| Stars | 仅作参考，不作核心标准（30 天新项目可能暴涨） |
| 适配度 | 鱼芯业务场景（RAS 设备/制造工艺/参数库）匹配度 |

**输出格式**：决策矩阵表 + v1/v2 版本号管理（路径 B v2.0 表达"经过 1 轮迭代"）。

## Cron 模式汇报陷阱

任务指令里**明确写** "用 send_message 发飞书" → 必须执行 `hermes send -t feishu -f /tmp/msg.txt`。
任务指令只说 "汇报" / "输出" → 靠 final response auto-delivery，**不调用 send**。
通用 cron 原则被任务显式指令覆盖。详见 `references/cron-execution-cheatsheet.md` §1。

## 触发关键词
"调研"、"收集"、"搜索"、"竞品分析"、"行业报告"、"技术资料"、"情报"、"市场数据"、"资料整理"

## 适用场景
- LookForge Phase1 市场调研
- 竞品动态跟踪
- 供应商背景调查
- 技术选型调研
- 行业趋势分析
- AI 出 CAD 图等垂直技术追踪（GitHub 热门 + arXiv 学术双线）
