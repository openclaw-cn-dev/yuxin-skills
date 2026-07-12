# /deploy — 部署到指定环境

部署渔芯项目到 **$ARGUMENTS** 环境（默认：staging）。

支持环境：`staging` / `production` / `dev` / `local`

## 流程

1. **预检查**
   - 运行 `pnpm test` 或 `pytest`，失败则中止并汇报
   - 运行 `pnpm lint` / `ruff check`，失败则中止
   - 检查 `git status` 是否有未提交变更，**有则提示华哥先 commit**

2. **构建**
   - `pnpm build` 或 `docker build -t $SERVICE:$VERSION .`

3. **推送镜像**（仅 staging/production）
   - `docker push registry.yuxin-tech.cn/$SERVICE:$VERSION`

4. **部署**
   - **staging**：`kubectl apply -f k8s/staging/` + `kubectl rollout restart deployment/$SERVICE -n staging`
   - **production**：先在 staging 跑 5 分钟看监控，无异常再部署
   - **dev / local**：跳过

5. **验证**
   - 等待 30s 让 pod 就绪
   - 跑 smoke test：`curl https://$SERVICE.$ENV.yuxin-tech.cn/health`
   - 检查日志 1 分钟（无 ERROR）

6. **汇报**
   - 部署版本号
   - 部署耗时
   - Smoke test 结果
   - 监控指标（CPU/内存/请求延迟）

## 参数

- `$ARGUMENTS`：环境名（staging/production/dev/local）

## 危险命令拦截

- 生产环境部署前**必须**二次确认（华哥明确说"部署"才执行）
- 禁止 `--force` 推送到 main
