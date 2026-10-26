---
name: yuxin-community-site-ops
description: 渔芯社区官网（lookforge.net，阿里云ECS 121.43.127.211）生产运维与「应用看不到」类问题排查。覆盖：两套独立应用体系判定（官方移动WEB版块 /webapps vs 工作台市场 community_apps）、会话与门禁三通道架构（主站Python门禁 / nginx auth_request eqsim-session-gate / 独立后端服务）、部署切流=全员掉线机制、nginx日志取证法（admin操作归属）、带会话端到端实测法。触发条件：华哥或用户报「官网上看不到某应用」「应用打不开」「303跳登录」「上传的应用不见了」「后台应用管理里没有」，排查 lookforge.net 生产问题、webapp_access 档位、community_apps 上下架、社区会话失效、releases 切流。
version: 1.1.0
author: 渔芯科技 · 玉芬
tags: [渔芯社区, lookforge-net, 生产运维, webapps, 门禁, 会话, nginx取证, 排查]
---

# 渔芯社区官网（lookforge.net）生产运维（类级）

生产服务器：阿里云 ECS `121.43.127.211`（`ssh root@`，7.3G 内存，hostname iZbp16mna1dres0qvgts51Z）。社区后端 `systemd yuxin-community` = uvicorn `127.0.0.1:8642`，WorkingDirectory=`/opt/yuxin/current/community`。部署为符号链接切流：`/opt/yuxin/current/community -> /opt/yuxin/releases/community-<日期>-<名>-v<N>`（`community.previous` 指上一版）。**运行库定位以进程为准**：`ls -l /proc/<pid>/cwd` 或 `/proc/<pid>/maps` 里打开的 `data/app.db`——各 release 的库是独立文件，旧版本库内容不代表线上。

## 1. ⚠️ 第一问：哪个入口？——两套独立应用体系

「应用看不到」必须先分清体系，否则修错地方：

| | ① 官方移动WEB版块 | ② 工作台市场 |
|---|---|---|
| 用户入口 | 官网导航「官方应用」→ `/webapps` | 渔芯工作台客户端内市场 |
| 唯一来源 | `webapps.py` 的 WEBAPPS 注册表（代码，17 应用（2026-10-24 geo 上架后），**发版才变**；geo 等新卡片由 `registry_patch.py` 管理） | `community_apps` 表（app_key，status∈online/suspended/draft） |
| 档位/上下架 | `webapp_access` 表（slug 主键）覆盖代码默认值；管理页 `/admin/webapps`，**改完即时生效无需发版** | `/admin/apps` 页上架/下架；**只有 status='online' 才在工作台客户端显示**（suspended 全隐藏） |
| 档位语义 | free=注册登录可用（**不是匿名可看**）；advanced=会员；未登录访问一律 303 → /u/login | 上架即可装，无登录档位 |
| 后台列表页 | `/admin/webapps`（官方应用权限） | `/admin/apps`（应用管理）+ `/admin/market`（只读一览） |

**华哥术语映射（2026-10-24 口头确认）**：他说「后台的应用管理」= `/admin/apps`（工作台体系）；说「官方应用」= `/webapps` 体系。他现在上架应用走官方体系（registry_patch + 发版），不再走工作台 GUI 上传。

## 2. 会话与门禁三通道

同一个 `yuxin_session` cookie、同一个库 `community_sessions`（token_hash=sha256(token)），但校验路径有三条：

1. **主站 Python 门禁**：`server.py` `_render_webapp_index`——container/steel/house-designer 等走这条（`identity.resolve_session` 直查库）。
2. **nginx auth_request 门禁**：`eqsim-session-gate.service`（127.0.0.1:8033，脚本 `/opt/eqsim-webapp/gate/session_gate.py`，env `EQSIM_COMMUNITY_DB=/opt/yuxin/current/community/data/app.db`）——**geo、eq-sim、pond-sim、鱼价雷达、ai-knowledge-graph** 的页面与同源 API 走这条（页面未登录 303、API 未登录 401 JSON）。
3. **独立后端服务**：geo=geo-webapp-backend(8671 只读演示)、aikg、aquabaike 等各有序号端口，只承接 API，门禁仍在 1 或 2。

**geo 类应用的部署会连带主站**：部署 geo（`/opt/geo-webapp/deploy/install.sh`）会同时重启主站 yuxin-community + reload nginx（要在 /webapps 挂卡片、插 nginx 路由块）。geo 上线 = current -> `/opt/geo-webapp/releases/<日期>-<名>`，安装包残留 `incoming/*.tgz` 属正常收尾态。所以「部署 geo 后全员又掉线」不是事故是必然——journalctl 里看到 geo-webapp-backend 与 yuxin-community 同秒重启即互相印证，勿误判为外人操作。

**部署切流 = 全员掉线**：切版本/重启服务后所有已登录会话作废，用户需重新登录。切流日重启可达 51 次/天 → 反复「看不到应用」多为会话失效，不是应用丢失。**判定口诀：303=程序门禁逻辑正常（登录态问题）；500/超时/连接重置=资源或崩溃问题**（内存/OOM 另查 dmesg）。

## 3. 排查方法论（顺序执行）

1. **问清入口**：官方 /webapps 还是工作台客户端市场？哪个设备/浏览器？什么时间发现？
2. **nginx 日志取证**：`grep <用户IP> /var/log/nginx/access.log`（北京 +0800 时区）。重点看 POST 端点（`/admin/webapps/access`=改档、`/admin/apps/status`=上下架、`/admin/users/role`=提权）。DB 行 `updated_at` 与日志 POST 秒级吻合 = 后台手动操作（先确认是不是管理员自己改的，勿当 bug 修）。
3. **服务端实测渲染**：`curl -s http://127.0.0.1:8642/webapps | grep -o "webapps/[a-z-]*/"` 看列表页真实输出；模板（webapps.html / admin/apps.html）是否有过滤条件。
4. **端到端带会话实测**（决定性证据）：往运行库 `community_sessions` 造一条临时会话（随机 token + sha256 入库 + user_id=3 + 未来 expires_at）→ `curl -H "Cookie: yuxin_session=<token>"` 打门禁 `/check`(8033)、目标应用页、匿名对照（应303）→ **测完立刻 DELETE 清理**。
5. **汇报时区分体系**：明确说清问题在①还是②、修了哪套、另一套状态如何。
6. **「修完还看不到」≠ 修复失败**：先查 nginx 日志该用户最后一次真实请求的时间——浏览器本地缓存/未重新登录时用户看到的可能是旧页面，服务器端 curl 实测才是真相。华哥重新部署/上传后必提醒：服务重启了，所有设备要重新登录再看。
7. **nginx 日志时区**：access.log 里是北京时间(+0800)，但 `community_sessions.created_at` 等 DB 时间戳是 **UTC**——对比「日志时间 vs 会话创建时间」时 +8 换算，否则会误判「没有新登录」（10-24 实踩：22:53 北京的重启对应 DB 里 14:53 UTC，直接按日志时间查会话表查空）。

## 4. 华哥自己动手部署时的 agent 角色分工（2026-10-24 模式）

华哥说「我从电脑上再部署一次看看」时，agent 的正确角色是**盯盘+验证**，不是代部署：
1. 部署前存基线快照到服务器（current 指向、进程 PID/启动时间、会话数、门禁表行数、关键服务 active 状态），落盘 `/opt/yuxin/backups/pre-redeploy-baseline-<时间戳>.txt`
2. 挂后台监视：`ssh ... "journalctl -u yuxin-community -f | grep --line-buffered 'Started Yuxin Community'"`（terminal background + notify_on_complete）
3. 华哥报「我传好了/部署了」后立即跑部署后体检：版本切换确认、会话存活、目标应用端到端实测、部署收尾完整性（release 目录唯一、incoming 只剩安装包）
4. geo/应用类部署触发的连带重启要主动向华哥点破因果关系（「你这次部署把会话又清了」），避免他误以为应用又丢了

## 5. 切流掉卡体检 + webapps.py 注册表热修 SOP（v18 事故沉淀，2026-10-24）

**根因模式**：v18（smsotp）打包基点用了旧代码快照，切流后注册表 23 卡→17 卡（aquaculture-news/aquaforge/edai/eq-sim/fish-price-radar/pond-sim 六卡消失），且 aquaculture-news 的 `webapps/` 静态目录只在 v17 release 里被落下（点进去 404）。其余 5 个应用本体走各自独立服务（nginx 托管静态 + 独立后端），不受 release 影响——**掉卡≠应用丢**。此类丢失发生在打包时刻，与用户当时在用什么外部工具（如 ChatGPT 优化项目）无关，以打包时间线为准。

**每次切 release 必做体检**（顺序）：
1. 卡片 diff：`grep -o '"slug": "[a-z0-9-]*"' webapps.py | sort` 新旧 release 对比
2. 渲染计数：`curl -s http://127.0.0.1:8642/webapps | grep -o "webapps/[a-z0-9-]*/" | sort -u | wc -l`
3. 卡/目录双向 diff：注册表 slug 集合 vs `webapps/` 目录集合——「有卡无目录」= 页面 404，「有目录无卡」= 列表不显示
4. 独立应用入口逐个公网 curl：匿名 303=活着，404=静态/路由没了

**热修 SOP**（在运行 release 内直接改，立即生效）：
1. 备份：`cp webapps.py webapps.py.bak-<用途>-<时间戳>`
2. 从好 release 抽卡片 dict：定位 `"slug": "<s>"` → 向前找 `    {` → 括号配对取整块。**⚠️ CRLF 陷阱（10-26 实踩）**：house-v17/webapps.py 是 Windows 打包的 CRLF 文件，行级正则 `^    \{$` 全部落空——抽卡前必须先 `read().replace("\r\n", "\n")` 归一化
3. 插入点：WEBAPPS 是 **tuple（`)` 收尾）**，geo 卡后有 `# ==== END 擎观 GEO 移动 Web 卡片 ====` 标记行——**用标记行定位插入点，勿猜 `]`**。**⚠️ 插入前必须 assert 标记行存在**：10-26 曾在 16 卡文件（无标记行）里走了"找最后一个 )"的兜底路径，把卡片插进了函数体，磁盘文件直接语法损坏——服务没重启所以线上无感，但差点演成事故。损坏时保留现场文件（.broken-insert-*）再从干净基底重做
4. 幂等保护：写入前查目标 slug 已存在则 abort
5. 验证：`py_compile` → 临时 import 跑 `all_apps()` 核对**总数 + 无重复 + 目标 slug 在列**。**⚠️ import 必须用 app venv 的 python（`/opt/yuxin/venv/bin/python3`）且 cwd=release 目录**（webapps.py `import access` 是同目录模块；系统 python 3.6 连 subprocess capture_output 都没有）。验证不过立即从基底回滚
6. `systemctl restart yuxin-community` → 公网 curl 端到端（匿名 303、带会话 200）。**公网 308/303 辨析**：本机 `curl 127.0.0.1/webapps/<s>/ -H "Host: lookforge.net"` 命中 nginx 的 308 是正常（可能无尾斜杠规则），判活看公网 curl 匿名 303
7. 静态目录补齐：`cp -a <旧release>/webapps/<slug> <新release>/webapps/`（静态按请求读，无需重启）
8. **热修是临时的，且已二次应验**：10-25 23:26 webapps.py 又被覆盖回 16 卡（SSH publickey 自 113.79.168.77=华哥深圳侧自动部署动作），昨天的 7 卡恢复全被打掉，同模式第二次发生。**根治唯一路径=修打包基点**。当前权威正本（23 卡）已存 `/opt/yuxin/backups/webapps.py.canonical-23cards-20261026*`，**任何打包前先把这份同步进打包源**，华哥下次发版前必须提醒

**历史 release 是恢复源**：v17 等旧 release 的 webapps.py 与 webapps/ 静态目录是掉卡/掉文件的唯一拷回来源，**不可随手清理**。

## 6. Pitfalls 档案

- **改档会被改回**：admin 后台多人可操作，`webapp_access` 的 free 改完可能被另一端手动改回 advanced（updated_at+nginx日志秒级吻合即实锤），先取证再动手。
- **脏行清理**：`webapp_access`/`community_apps` 里 release 已不存在的 slug（如 pond-sim）是脏数据，删除前先 `cp app.db app.db.bak-<用途>-<日期>`，行级操作无需重启服务（即时生效）。
- **工作台市场 suspended ≠ 官方 /webapps 不可用**：两套完全独立，10-23 曾批量下架 11 个工作台应用，官方版块不受影响。
- **geo 类应用双层健康**：页面门禁（8033）和后端 API（8671）是两个服务，分别 `systemctl status`。
- **登录卡住优先查手机绑定**：v18(SMS-OTP版) 起登录页以手机验证码为主，未绑手机号的账号（phone=None）在手机端会卡登录——这是「反复登录不成功」的常见根因。
- **匿名视角+缓存的「少了应用」误报**：用户报「XX 应用不见了」但服务端实测列表全在时，基本是浏览器缓存/匿名视角——verify 流程第 6 条。注意官方 /webapps 列表页是公开渲染的（不登录也能看到卡片），所以「列表少卡」若为真必是注册表变了；而应用内页匿名一律 303，**静态资源也在登录墙内**（fish-price-radar 模式：连 app.js 都 auth_request）。
- **admin 后台多人多端**：华哥至少三台设备（深圳 IP 14.120.x Mac、14.26.x Windows+平板），他自己也常不知道另一端做过什么操作——改档/下架/提权类「异常」先对时间线问人，别急着当入侵或 bug。

## 7. 会话档案

- `references/***SECRET***.md` — 三仿真应用+geo「看不到」完整排查时间线（两体系分叉实证、nginx 取证命令、端到端实测记录、v17→v18 切流会话失效链）。
- `references/***SECRET***.md` — v18 掉卡事故：23→17 卡的版本比对法、6 卡清单、热修执行记录与验证输出。

## 8. 关联 skill

- `geo-monitor-dev` — 擎观 GEO 应用本身的功能开发（本 skill 管 geo 在官网的门禁/上架面）
- `alicloud-ecs-website-deploy` — ECS 上部署/Nginx/端口冲突通用流程
- `hermes-config-safe-edit` — 改配置类操作的 5 阶段铁律（备份→验证同款纪律适用于生产库操作）
