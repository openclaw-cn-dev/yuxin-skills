# /commit — 智能 commit

按渔芯 git 规范提交代码。

## 流程

1. **检查状态**
   - `git status` 看变更
   - `git diff --staged` 看已暂存内容

2. **确认规范**
   - 检查是否有未暂存但应提交的变更
   - 检查是否有不应提交的文件（.env、node_modules、__pycache__）

3. **生成提交信息**
   - 分析 diff 内容
   - 按 Conventional Commits 规范：`<type>(<scope>): <description>`
   - type: feat / fix / refactor / docs / test / chore / perf
   - scope: 模块名
   - description: 中文或英文简短描述
   - 必要时加 body 详细说明

4. **示例**
   ```
   feat(auth): 添加 JWT 刷新 token 逻辑

   - 401 拦截器自动调用 /auth/refresh
   - 避免无限递归（用 bare axios.post）
   - 增加 3 个单测覆盖正常/失败/刷新中场景
   ```

5. **执行**
   - `git add .`（排除 .gitignore）
   - `git commit -m "<generated message>"`
   - 不自动 push（除非华哥说"push"）

6. **汇报**
   - 提交 hash
   - 变更文件数
   - 提交信息预览

## 规则

- ❌ 不 commit 到 main（提示用 PR 流程）
- ❌ 不 commit .env、密钥、数据库文件
- ✅ 自动跑 lint（hooks 已配），失败不 commit
- ✅ 提交前自动跑测试（hooks 已配）
