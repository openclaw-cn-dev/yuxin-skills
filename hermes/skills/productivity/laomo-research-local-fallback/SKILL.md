---
name: laomo-research-local-fallback
description: 老莫资料收集本地优先工作流 — 外部搜索不可用时，切换本地知识库完成RAS竞品分析等调研任务。
version: 1.0.0
author: 渔芯科技
tags: [老莫, 知识库, 资料收集, 本地优先]
---

# 老莫资料收集本地优先工作流

## 触发条件
执行 research-collection 任务时，外部网络搜索不可用（DuckDuckGo超时、Brave API无key等），立即切换本地知识库。

## 已知本地知识库路径

```
/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/docs/
├── ras-equipment/          # RAS设备知识库（各单元详解）
│   ├── 00-概览与水循环.md
│   ├── 01-养殖池.md
│   ├── 02-旋流固液分离器.md
│   ├── 03-微滤机.md
│   ├── 04-蛋白质分离器.md
│   ├── 05-生物过滤器.md
│   ├── 06-消毒单元.md
│   ├── 07-增氧单元.md
│   ├── 08-温控系统.md
│   ├── 09-循环水泵.md
│   └── 10-支持系统.md
├── 竞品分析-国内RAS设备厂商对比.md  # 竞品分析报告
├── docs1/调研报告.md           # LookForge调研报告
└── README.md

/Users/hua/Desktop/渔芯科技/3-市场销售/
└── RAS设备推广素材.md          # RAS设备详细规格和价格

/Users/hua/Desktop/渔芯科技/团队协作/
├── scanner.py                      # 任务扫描器
├── sync_to_group.py                # 飞书群同步
└── task_queue.py                   # 任务队列（TaskQueue类）
```

## 外部搜索不可用的处理流程

### 1. 立即尝试的备用方案（按顺序）

1. 搜索本地文件（`search_files` 或终端 `grep`）
2. 读取相关 md 文档
3. 基于已有资料整理报告
4. 标注数据来源可靠性为"中低"
5. 建议后续实地/网络调研核实

### 2. 切勿反复尝试的方法（浪费时间）

- DuckDuckGo API（超时）
- Brave Search API（无key）
- terminal curl → python pipe（安全扫描拦截）
- execute_code sandbox python3（网络隔离）

### 3. 可用的免费API

- arxiv.org（学术论文，可访问）
- Wikipedia API（可能超时）

## 任务队列操作规范

```python
from task_queue import TaskQueue
q = TaskQueue()

# 认领任务（claim后status变为claimed）
q.claim_task('task_id', '老莫')

# 启动任务（start后status变为in_progress）
q.start_task('task_id')

# 完成并记录结果
q.complete_task('task_id', result='完成内容简述', actor='老莫')
```

## MEMORY.md 路径

正确路径：`/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维/memory/MEMORY.md`

## 报告输出规范

当使用本地资料而非一手调研时，在报告开头注明：

```
**数据可靠性**：中低（基于本地知识库整理，建议后续实地调研核实）
```

## 经验总结

- 外部搜索不可用是常见情况，本地知识库通常已包含足够素材
- RAS设备知识库（docs/ras-equipment/）和RAS设备推广素材.md是调研的重要一手资料
- delegate_task 搜索子任务执行后无结果返回（token限制），不能依赖它收集信息
- 网络API失败后立即切换本地，节省大量试错时间
