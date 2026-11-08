---
name: deploy
description: 渔芯系部署规范(阿里云 ECS/官网热更/版本管理)(2026-11-07 重建版,原版丢失)
---

# deploy 部署

## 口径
- 「部署上线」= 阿里云生产 release 上线 + 发布渔芯社区官网 /repo 管理员临时仓库(仅管理员可见,匿名 303/非 admin 404);默认不公开不上架市场(§21)

## 动作
1. 版本单源:tauri.conf.json / 官网 workbench_release.json
2. 官网「推=上线」仅 git;ECS 走软链制热更包与 json
3. 代码变更走六步 release;scp 批量大文件会静默失败,须校验
4. pkill -f 自匹配 ssh 致 255 → 用 fuser -k

## 禁
- 直推 main;check-version 不验线上(必须 curl 线上版本)
