Always respond in Chinese-simplified

# 华哥 / 渔芯科技 — Claude Code 全局铁律

## 🔒 数据安全铁律（2026-07-21 新增）

### 分层持久化原则
**每一层处理完成后必须将数据写入宿主机磁盘，禁止仅存 Docker 命名卷或容器内存。**

```
L1 扫描清洗 → 原始文件存 文档库/  + 清洗文本存 cleaned/
L2 向量化   → PG表(宿主绑定挂载)  + chunks 存 文档库/
L3 知识图谱 → PG表(宿主绑定挂载)
L4 GBrain  → PG表 + gbrain_reports/ JSON文件
L5 替换     → PG表 + document_quality_scores
L6 回流     → Redis缓冲 + 中转站/user_content/ .md文件
```

### 容器化部署铁律
- ❌ 禁止 PostgreSQL 数据仅存 Docker 命名卷 → 必须绑定挂载到宿主机路径
- ❌ 禁止日志仅写容器内文件 → 必须双写 PG表 + 宿主机 JSONL
- ❌ 禁止中间产物仅存容器内存 → 必须落盘（如 cleaned/ 桥接文件）
- ✅ 所有持久化路径必须在 `/Users/hua/rkr_staging/` 下统一管理
- ✅ docker-compose 中所有有状态服务必须用 bind mount，不用 named volume

### 为什么
Docker Desktop 在 macOS 上跑在 Linux VM 里。内存不足时 macOS 杀掉 VM → 重启后 VM 是新的 → 命名卷全部清空。
宿主机路径不受影响。
