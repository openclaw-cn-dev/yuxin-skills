# fix-ci

当用户提到 CI 挂了、GitHub Actions 失败、工作流报错时触发。

目标：
- 读取 `.github/workflows/ci.yml`
- 修复过时的 action 版本
- 确保先安装 pnpm，再跑 registry 测试
- 确保 Rust 测试在稳定 toolchain 下执行

执行边界：
- 只修改 `.github/workflows/ci.yml`
- 若目标文件不存在，先返回观察结果
- 不新增提权脚本，不放宽白名单
