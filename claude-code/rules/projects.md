# 渔芯项目 — 项目索引

> 加载时机：所有项目自动加载
> 用途：让 Claude Code 知道渔芯有哪些项目、各自定位

## 渔芯科技 2 大品牌

### 1. 渔芯水产养殖（RAS 循环水养殖）
**定位**：AI 赋能全链条的水产养殖智能化
**核心能力**：
- RAS 系统设计
- 智能监控（鱼乐宝、投喂策略）
- 数据采集（FindEra 寻元）
- 仿真预测（AquaForge）

### 2. LookForge（数据仿真平台）
**定位**：多环节数据仿真
**核心能力**：
- 3D 工厂建模
- 流程仿真
- 设备拼接
- 数据可视化

## 项目目录结构

```
~/Desktop/渔芯科技/6-产品研发/
├── 00-FindEra寻元/          # 资料采集（arXiv/HuggingFace/博客）
├── 01-RKR知识库/            # RKR 平台（10 容器架构）
├── 02-AquaForge养殖仿真/    # 养殖仿真引擎
├── 03-EDAI硬件开发/         # 硬件 + AI 边缘计算
└── (未来项目)
```

## 各项目要点

### 00-FindEra 寻元
- 用途：自动从 arXiv/HuggingFace/博客采集 + 切片 + 入 RKR
- 路径：`~/Desktop/渔芯科技/6-产品研发/00-FindEra寻元/`
- 配置：`~/hermes/findera_config.json`
- 认证坑：RKR admin 需要 `validation_alias` 字段

### 01-RKR 知识库
- 用途：内部知识库 + 文档管理 + AI chat
- 架构：10 容器（backend/frontend/postgres/redis/minio/elasticsearch/celery-beat/processing-pool×2/staging-pool）
- 账号：`admin@rkr-platform.com / Admin@2026!rkr`
- **慢**：单条 chat 173s，200 条 8.3h，积压 11.2 万+
- **建议**：用 RKR 文档上传 API，不跑 RKR chat 批处理

### 02-AquaForge 养殖仿真
- 用途：RAS 系统仿真（鱼乐宝核心）
- 关联：鱼乐宝 simulation_core.py（生长计算/FCR/投喂量）
- 调试：`fish-sim-debug` skill

### 03-EDAI 硬件开发
- 用途：硬件 + AI 边缘计算设备
- 部署：阿里云 ECS（参考 `alicloud-ecs-website-deploy` skill）
- 端口冲突：注意 Docker 镜像名 + 中文目录

## 团队 Agent（玉芬管理）

| Agent | 负责 | 接任务方式 |
|---|---|---|
| 毛豆 | 产品经理 + LookForge | 飞书云盘 `任务派发/毛豆/` |
| 老莫 | 知识库 + 测试 | 飞书云盘 `任务派发/老莫/` |
| 小宝 | 销售 + 自媒体 | 飞书云盘 `任务派发/小宝/` |
| 黑豆 | 行政 + 财务 + 法务 | 飞书云盘 `任务派发/黑豆/` |
| 阿福 | 客服 | 飞书云盘 `任务派发/阿福/` |
| **玉芬**（我） | 运营 + 监督 | 调度所有 Agent |
| 宽博士 | 量化研究 | 华哥直派 |
| 学习助手 | 知识整理 | 华哥直派 |

## 关键规范

- **编程必须用 Claude Code**（不直接终端改代码）
- **中文路径陷阱**：`--workdir` 拒绝 → `ln -s` 到 `/tmp`
- **网络能上**（api/内网/GitHub 都没问题）
- **批量任务设计持久化**（保证每天数量）

## 想法记录

- 华哥抛想法 → 立即结构化记录到 `~/hermes/ideas/`
- 骨架：①核心 ②对比 ③风险 ④待办 ⑤关联
- 同步给玉芬整理师归档到 RKR
