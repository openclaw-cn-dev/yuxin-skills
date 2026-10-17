---
name: yuxin-community-workflows
description: 渔芯社区工作流管理 — 硬件开发工作流（hardware_workflow.py）、新360行行业工作流（如反向代购/daigou_workflow.py）、07-软件项目开发优化。覆盖工作流自进化 cron、行业数据补充（industries.json）、新行业工作流原型创建。**渔芯社区工作台适配/独立应用上架必读**：双包体系（.yxf 工作流 vs .yxa 独立应用 yuxin.app/v1）、发布链（yxf-tools 打包→预检→投稿→审核→签名→上架）、适配选型铁律（完整应用打 .yxa 维持应用完整性，华哥 2026-10-14）、官方应用储备池管线。**curator 合并 2026-10-16**：原独立 skill workbench-yxf-publishing（工作台发布链 GUI 实操+0.3.0 源码构建）、yuxin-community-app-pipeline（上架管线）、yuxin-community-ops（lookforge.net 生产部署/workbench_release.json 热切）已整档收纳至本 skill references/，渔芯社区全链路（工作流管理+应用上架+官网与工作台部署运维）统一从本 skill 进入。触发条件：渔芯社区充实、新360行工作流、硬件开发工作流、反向代购、07软件项目开发优化、industries.json 补充、工作流付费/交易变现、工作流交易平台对标、把项目适配工作台上架社区仓库、.yxa/.yxf 打包投稿、渔芯工作台/官网代码结构、lookforge.net 模块、上线部署、重新上线、官网安装包更新、应用内直接更新。
---

# 渔芯社区工作流管理

## 双包体系与发布链（2026-10-14 实测定论）

渔芯社区已从「工作流平台」升级为「独立应用平台+订阅制商业平台」。**两条包链并行**：

| | .yxf 工作流 | .yxa 独立应用（yuxin.app/v1） |
|---|---|---|
| manifest | 11 字段 | 15 字段：+modules(1-100, kind=page/workflow) / environmentRequirements / dataContracts / knowledge / migrations |
| permissions | 4 键 | 7 键全必填（+dataRead/dataWrite/knowledgePublish） |
| 文件数 | ≥3 | 6-500；SVG 实际不可用（xmlns 含 http:// 被 INSECURE_URL 阻断）→ 图标一律 PNG |
| 投稿 | POST /api/workbench/submissions | POST /api/workbench/app-submissions |
| 审核 | /api/workbench/review/{id}/decision | /api/workbench/review/apps/{id}/decision（复扫比对 sha256/app_key/version 后才签名） |
| 安装 | 验签下载 | 票据制：5 分钟一次性 + 付费门禁 402（entitled = 已购 OR is_official AND 会员） |
| 生产状态 | catalog 13 条 | 已闭环（2026-10-14）：eq.assistant 首例上架，**但系 API 直投（后被华哥否定），待清库从工作台重走** |

发布链：`社区仓库/yxf-tools 打包 → verify_yxf.py 预检（服务端同款扫描器，预检=审核零偏差）→ **工作台客户端投稿** → 服务端复扫 → admin 审核 → Ed25519 签名 → catalog → 工作台验签安装`。

**⚠️ 上传路径铁律（华哥 2026-10-14 晚明确纠正）：生产投稿必须通过操作本地部署的渔芯工作台客户端**（创作中心上传 → 我的投稿 → 应用审核过审）——**API 直投生产被否定**，管理员凭据只可用于本地 :8891 演练与生产只读验证（GET/票据下载）。API 直投过的记录须清库后从工作台重走（community_app_releases 的 (app_key,version) 唯一性会 409 拦同版本重传）。完整操作单见 `workbench-yxf-publishing` 技能 references/***SECRET***.md。

**适配选型铁律（华哥 2026-10-14「最大限度维持应用本身的完整性」）**：完整独立应用（多页面/多能力）一律打 **.yxa**，不打 .yxf——.yxf 只能装单个工作流，丢应用整体性。已打好的 .yxf 可复用为 .yxa 内嵌的 workflow 模块。官方管线=渔芯独角兽为储备池（IA 1.0 §6.5 拍板）：选品→yxa 打包→审核（官方应用不豁免）→标「渔芯官方」上架（会员免费/非会员单买）；待拍板：官方发布账号。

**运行时现状（首个官方应用须知）**：.yxa 的 page 模块运行时渲染器未实装（GenericAppView 只显示元信息+技能对话）；workflow 模块复用 .yxf 沙箱执行器（完整）。**首个官方应用应全用 workflow 模块承载功能**，等 page 渲染器落地再上声明式页面。

**商业模式锚点**（IA 1.0，2026-10-14 五轮拍板）：订阅 ¥99/月（季238/年713/首月9.9），官方应用会员免费，创作者抽 5%，消费满额自动升档；身份和钱在云端（唯一权威），功能和创作数据在本地；白名单 101699421@qq.com 恒会员。

深度分析报告（2026-10-14 全量代码级）：`/Users/hua/6-产品研发/渔芯社区/分析报告-官网与工作台深度分析-20261014.md`。

> 📁 代码级细节（官网模块行数地图/关键端点速查/工作台 src 结构/本地全链演练 SOP/平台坑位档案）→ `references/workbench-code-map-20261014.md`。改官网或工作台代码前先读它。

---

## 项目定位

渔芯社区（Core 2）是渔芯科技的 AI 产品孵化引擎，当前 11 个项目 + 3 个工作流原型。

社区仓库支持**付费下载/上传工作流**，定位是"卖成品"（工作流/数字产品交易），不是"卖人时"（自由职业平台）。竞品对标（三类平台逻辑 / RunningHub 直接对标 / 打包化铁律 / 抽佣定价）见 `references/***SECRET***.md`。

## 管辖范围（2026-10-13 工作区重整后，4 目录版）

> ⚠️ 2026-10-13 工作区重整：8 目录收敛为 4 个；`渔芯社区官网-v2/` 已改名 `渔芯社区官网/`（=线上代码本体，改它即改线上）；`官网-线上最新版-20261013/`、`工作台/`(React 2.0 Web 版)、`渔芯知识库/` 等旧目录已不存在，勿按旧路径找。

| 项目 | 路径 | 说明 |
|------|------|------|
| 渔芯社区根目录 | `/Users/hua/6-产品研发/渔芯社区/` | 4 目录：官网+工作台+知渔+社区仓库 |
| 官网（纸上芯光 v0.3.0，lookforge.net） | `/Users/hua/6-产品研发/渔芯社区/渔芯社区官网/` | FastAPI+Jinja2 SSR，本地 :8891，生产 systemd :8642；含 workbench_api.py / repo.py / app_security.py / admin_site.py |
| 渔芯工作台（唯一客户端） | `/Users/hua/6-产品研发/渔芯社区/渔芯工作台/` | Tauri 2 + Rust + React/TS + SQLite，16G（多为 node_modules/target，勿整体打包） |
| 社区仓库（独立应用目录） | `/Users/hua/6-产品研发/渔芯社区/社区仓库/` | 服务端逻辑在官网正本；本目录放 yxf-tools（打包+预检工具箱） |
| 知渔 KnowHow | `/Users/hua/6-产品研发/渔芯社区/知渔/` | AI 学习平台 v5.3，:8520，官网 /zhiyu 同源代理挂载 |
| 硬件开发工作流 | `工作流原型/硬件开发/hardware_workflow.py` | 4 步管线: 创意→CMF配色→功能拆解→开发方案 |
| 反向代购工作流 | `工作流原型/反向代购/daigou_workflow.py` | 5 步: 选品→建站→营销→客服→物流 |
| 新360行数据 | `data/industries.json` | 当前 26 个行业，目标 360 个 |
| 07-软件项目开发 | `/Users/hua/6-产品研发/07-软件项目开发/` | v2.1 软件方案生成器，对接 Hermes Gateway |

## 自进化 cron

| Job ID | 名称 | 节奏 |
|--------|------|------|
| `3328b7053970` | 渔芯社区-硬件+新360行工作流进化 | 每 2h，5 方向轮转 |
| `27d759a9c8bd` | 07-软件项目开发-健康检查 | 每 4h，自动拉起 |

## 5 方向轮转 (A→B→E→D→C)

- **A** — 硬件开发工作流充实（为新行业生成硬件案例）
- **B** — 新360行行业工作流原型创建（参照反向代购模式）
- **E** — 优化07-软件项目开发（generator.py/evolution.py/前端）
- **D** — 工作流质量自检
- **C** — 新360行数据补充（搜索新兴行业→industries.json）

## 07-软件项目开发 v2.2 要点

- 对接 Hermes Gateway: `http://localhost:18888/openai/v1`（不是 `/v1`）
- **平台选择器** (v2.2 新增)：用户选择软件使用方式 → 注入平台专属架构上下文
  - 🌐 网页端：响应式/SEO/PWA/CDN/浏览器兼容
  - 💻 电脑版软件：Electron/Tauri 跨平台，Win(.exe)/Mac(.dmg)/鸿蒙(.hap) 打包
  - 📱 手机端：Flutter/RN/UniApp，离线优先，FCM/APNs 推送，应用商店审核
- 平台上下文通过 `_get_platform_context(platform)` 注入到 enhanced_input，随用户需求一起发给 LLM
- 前端 `platform` 参数通过 `GenerateRequest.platform` 传递（pattern: `^(web|desktop|mobile)$`）
- 需求预处理 `preprocess_demand(user_input, platform)`: 识别 28 个渔芯领域→注入技术栈提示→注入平台上下文
- System Prompt 融入 RAS/IoT/农业等渔芯领域知识
- SSE 按行发送（非逐字符），兼容 deepseek `reasoning_content`
- 后端端口 8006，前端 5177
- 健康检查: `curl http://localhost:8006/api/health`

## 避免重复

已有工作流:
- ✅ 硬件开发（hardware_workflow.py）
- ✅ 反向代购独立站（daigou_workflow.py）
- ✅ 软件项目开发（07-软件项目开发）

## 工作流付费功能定位（2026-08-16 竞品调研）

华哥问"渔芯社区付费下载/上传工作流算不算自由职业功能"。核心判断：**这是"卖成品"（数字产品/工作流交易），不是"卖人时"（自由职业平台）**。对标 Gumroad(10%+$0.5)/PromptBase(20%)/RunningHub（中国本土 ComfyUI 工作流交易+云端运行），**不学 Upwork/猪八戒的投标谈判**。

- 工作流本质 = "做一次反复卖"，边际成本趋零、利润 70-90%
- 渔芯最大护城河 = 垂直（"水产养殖/RAS + AI 工作流"全国独一份）
- 运营铁律 = 打包化（定义清晰、明码标价、开箱即用、一键运行，买家零谈判）
- 进化路径 = 付费下载文件（Gumroad 雏形）→ 云端运行+用量分成（RunningHub 模式）
- 警惕低端化（Fiverr 2025 流失 700K 买家，低端短单被 AI 蚕食）

完整竞品数据（平台费用表/真实收入案例/RunningHub/6条运行逻辑/7条启示）见 `references/***SECRET***.md`。

---

## 已吸收：新360行新增行业标准化流程 (new-360-industry)

渔芯社区「新360行」新增一个行业的标准化 SOP（触发：用户说"新360行"/"新增行业"/"补充行业"）。与本 skill 的 `references/add-industry.md` 同主题，合并为权威版：

- 行业入库的标准流程 + `templates/industry-deep-dive.md` 行业深挖模板
- 完整 SOP：`references/new-360-industry-sop.md`

## 已吸收：工作台发布链·桌面客户端运维（curator 合并 2026-10-16 · 原独立 skill workbench-yxf-publishing 整档收纳）

「独角兽项目适配工作台 → 打包 → 投稿 → 审核 → 签名上架」的完整发布链 SOP 已合并至 `references/workbench-yxf-publishing/`（原独立 skill v1.1.1；2026-10-16 整理时原包误删损毁，现为恢复存根：华哥铁律、双包 schema 速查、GUI 上传实操要点、0.3.0 源码构建、eq.assistant 首例档案均在；丢失的 3 references + 2 templates + drill_local_8891.py 待按存根文末指引考古回填）。触发：适配工作台 / 打包上传社区仓库 / 独立应用上架 / .yxa/.yxf 打包投稿 / 工作台投稿 / 工作台构建升级。执行时先读 `references/workbench-yxf-publishing/SKILL.md`。

## 已吸收：应用上架管线·独角兽储备池（curator 合并 2026-10-16 · 原独立 skill yuxin-community-app-pipeline 整档收纳）

独角兽=官方应用储备池管线（华哥 2026-10-14 IA 1.0 §6.5 拍板：选品→打包 .yxa→审核（官方不豁免）→标「渔芯官方」→反馈迭代）已合并至 `references/yuxin-community-app-pipeline/`（原独立 skill v1.0；整理时原包误删损毁，现为恢复存根：华哥铁律 4 条 + 双包选型指引在，build_yxa 模板参照 sec-toolkit 打包器回填）。触发：上架应用 / 官方应用 / 独角兽储备池。与上一节发布链 SOP 是同一条线的「选型+官方身份」侧，冲突时以华哥最新铁律为准。

## 已吸收：官网+工作台发布部署运维（curator 合并 2026-10-16 · 原独立 skill yuxin-community-ops 整档收纳）

生产部署与仓库运营侧（lookforge.net 官网 + 工作台发版）已合并至 `references/yuxin-community-ops/`（原独立 skill v1.0；整理时原包误删损毁，现为恢复存根：发布五步铁律、workbench_release.json 语义、版本 bump 四处同步、ci-artifacts 回传通道均在；2026-10-14 发版实录 reference 可从当日会话记录考古回填）。触发：上线部署 / 重新上线 / 官网安装包更新 / 应用内直接更新 / 下载环境补齐。devops 分类下的同名 skill 已同步归档——渔芯社区全链路（官网部署 / 工作台发版 / 工作流管理 / 应用上架）现在统一从本 skill 进入。
