# /rkr-sync — RKR 知识库同步

把当前工作产出同步到 RKR 平台。

## 流程

1. **检查变更**
   - `git diff --name-only HEAD~1 HEAD` 看最近 1 次提交改了哪些文件
   - 或 `git status` 看未提交

2. **分类**
   - 代码变更 → 同步到对应项目（LookForge/RKR/FindEra/EDAI/AquaForge）
   - 文档变更 → 同步到知识库
   - 配置变更 → 同步到基础设施分类

3. **调用 RKR API**
   ```python
   import requests
   
   # 登录获取 token
   token_resp = requests.post(
       "https://rkr.yuxin-tech.cn/api/auth/login",
       json={"email": "admin@rkr-platform.com", "password": "Admin@2026!rkr"}
   )
   token = token_resp.json()["access_token"]
   
   # 上传文档
   upload_resp = requests.post(
       "https://rkr.yuxin-tech.cn/api/documents",
       headers={"Authorization": f"Bearer {token}"},
       files={"file": open("path/to/file", "rb")},
       data={"project": "LookForge", "tags": "sync,auto"}
   )
   ```

4. **验证**
   - 检查 RKR 返回 200
   - 在 RKR 平台搜索文件名确认能搜到

5. **汇报**
   - 同步文件数
   - 失败项（如有）
   - RKR 文档链接

## 注意事项

- RKR 平台有 11.2 万+ 积压，单条 chat 173s → **不要**用 RKR chat 批处理
- 同步用 `findera_setup` skill 的配置（已在 `~/hermes/findera_config.json`）
- 失败重试 3 次，仍失败则汇报华哥
