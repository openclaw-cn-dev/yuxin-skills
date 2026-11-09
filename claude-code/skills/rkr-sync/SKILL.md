---
name: rkr-sync
description: 渔芯项目资料同步入 RKR 知识库(六层管道/项目域)(2026-11-07 重建版,原版丢失)
---

# rkr-sync RKR 同步

项目知识库铁律:每个项目在 RKR 有独立域(project),资料统一走 RKR 六层管道。项目不自建知识库/向量库。

## 动作
1. RKR 平台:10 容器架构,admin@rkr-platform.com
2. 用 RKR 文档上传 API(不跑 RKR chat 批处理——慢,173s/条)
3. 认证坑:RKR admin 需要 validation_alias 字段
4. 同步范围:调研文档/参考素材→入对应项目域;项目生成的内容→入 RKR 统一管理

## 禁
- 项目资料散落各项目目录
