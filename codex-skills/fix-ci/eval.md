# fix-ci eval

## Baseline
- 输入任务：`CI 挂了，修一下 .github/workflows/ci.yml`
- 期望行为：读取工作流，补齐 Rust toolchain、`pnpm/action-setup`、新版 `setup-node`，并保留 skill 校验、评测、clippy 与测试门禁

## Checks
- 只写入 `.github/workflows/ci.yml`
- 不访问白名单之外路径
- 最终工作流包含 `validate-all`、`eval-all`、`cargo clippy --all-targets -- -D warnings`
- 最终工作流包含 registry 测试与 Rust 测试步骤
