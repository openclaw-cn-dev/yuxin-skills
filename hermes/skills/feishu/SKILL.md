---
name: feishu
description: "飞书(Lark)集成操作 — 云盘文件管理、Wiki知识库、Bot权限限制、跨Bot协作、OAuth用户授权。覆盖 drive/v1、wiki/v2、docx/v1、auth/v3 API。"
version: 1.0.0
author: Hermes Agent (consolidation)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [feishu, lark, drive, wiki, bot, api, oauth, collaboration]
---

# 飞书(Lark) API 集成操作

飞书Bot与企业API的完整操作指南。覆盖云盘文件管理、Wiki知识库、权限协作、OAuth授权。

## 1. 认证与Token

**Base URL:** `https://open.feishu.cn/open-apis`

**Tenant Access Token（Bot级别，2小时有效期）:**
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "...", "app_secret": "..."}'
```

**User Access Token（用户级别，通过OAuth获取）:**
用于Wiki写操作等需要用户授权的场景。获取方式见 §4 Wiki操作。

### ⚠️ 核心概念：Wiki vs 云盘是两套独立API

| 系统 | API前缀 | Token类型 |
|------|---------|----------|
| 飞书Wiki | `/open-apis/wiki/v2/*` | 创建空间需user_access_token（99991663错误=Bot token无效） |
| 飞书云盘 | `/open-apis/drive/v1/*` | tenant_access_token可用 |

两者token不通用。Wiki GET list可用Bot token（返回空=没有创建权限），POST create不行。

## 2. 云盘操作 (Drive API)

### 创建文件夹

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/create_folder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "文件夹名", "folder_token": "父目录token"}'
```
⚠️ 用 `folder_token` 不是 `parent_node`。

### 上传文件

```bash
SIZE=$(stat -c%s /path/to/file)  # 或 os.path.getsize()
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/file" \
  -F "file_name=filename.ext" \
  -F "parent_type=explorer" \
  -F "parent_node=$FOLDER_TOKEN" \
  -F "size=$SIZE"
```
⚠️ `size` 必须是文件的精确字节数，否则返回 `1062009` 错误。

### 列出文件 / 下载 / 删除

```bash
# 列文件
curl -s "https://open.feishu.cn/open-apis/drive/v1/files?folder_token=XXX" -H "Authorization: Bearer $TOKEN"

# 下载
curl -s "https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download" -H "Authorization: Bearer $TOKEN" -o output

# 删除
curl -s -X DELETE "https://open.feishu.cn/open-apis/drive/v1/files/{token}?type=file" -H "Authorization: Bearer $TOKEN"
```

### 添加协作者（已验证可用）

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/{token}/members?type=folder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_type":"openid","member_id":"ou_xxx","perm":"full_access","need_notification":false}'
```

## 3. Docx API（创建文档）

### Block类型权限限制（重要！）

tenant_access_token（Bot）可用的block类型：
- ✅ text(2), heading1(3), heading2(4), heading3(5), divider(22)
- ❌ bullet(14), ordered(15), code(12), quote(13), callout(17), todo(18) → 返回 `1770001 invalid param`

**解决方案**：降级为普通文本 + 符号替代（• 代替列表、"```"包裹代码、"│"前缀代替引用）。

### 创建独立文档（user token可用）

```python
# 通过 Hermes MCP
mcp_lark_mcp_docx_builtin_import(
    data={"file_name": "[部门] 文档标题", "markdown": "# 内容..."},
    useUAT=True  # user access token
)
```

## 4. Wiki 知识库操作

Bot无法创建Wiki空间或子节点。两种解法：

### 方案A：OAuth User Token（推荐）

用户在自己的Mac终端执行登录（AI Agent终端无法完成OAuth交互）：
```bash
npx -y @larksuiteoapi/lark-mcp login -a <APP_ID> -s <APP_SECRET> \
  --scope "wiki:wiki wiki:wiki:readonly docx:document drive:drive"
```

**scope注意事项**：
- ❌ 不要包含 `wiki:node:readonly` 或 `wiki:node:write`（报20043错误，无效scope）
- ✅ 正确：`wiki:wiki` `wiki:wiki:readonly` `docx:document` `drive:drive`

配置 Hermes MCP 使用用户Token：
```yaml
mcp_servers:
  lark-mcp:
    command: "npx"
    args: ["-y", "@larksuiteoapi/lark-mcp", "mcp", "-a", "<APP_ID>", "-s", "<APP_SECRET>", "--token-mode", "user_access_token"]
```

### 方案B：手动操作

1. 用 `docx_builtin_import` 创建独立文档
2. 告知用户文档链接
3. 用户在飞书中：文档右上角「···」→「添加到知识库」
4. 或：用户在飞书中手动创建知识库，将Bot添加为管理员

## 5. 跨Bot协作限制（平台级）

飞书平台**禁止Bot之间互相分享文件夹**：
- API: `POST /drive/v1/permissions/{token}/members`
- 所有Bot互相分享均返回 `code=1063002 Permission denied`
- 这是平台级限制，与App权限无关
- Hermes `feishu_drive` 工具集只有评论功能（add/reply/list），不能管理文件

**替代方案**：阿里云ECS共享目录（SCP/SFTP），或通过群里发文件→手动整理。

## 6. 渔芯专属配置

### 玉芬Bot凭证

云盘根目录: `Vb83fsimklzqKDdd0dHcc3g2nhd`

### 知识库 node_token

| 知识库 | node_token |
|--------|-----------|
| 产品部门 | `YVerwmGxVi86Lak6KXicbm0EnWg` |
| 学习交流 | `Ftc2wrfK9iPwcLkmwAvcRF25nwe` |
| 销售部 | `Kz7hwHOkZi1fJPkkyYxcTteznsg` |
| RAS循环水系统 | `XBuwwX6Dki1rWWkfGJQcqxicnQc` |

### 各Agent OpenID

| Agent | OpenID |
|-------|--------|
| 渔芯/玉芬 | `ou_40267dada4a4e58c8cd9abc2d2d71083` |
| 毛豆 | `ou_f13964b2f75bd13571a486a8067347fd` |
| 老莫 | `ou_b2037876ed0d472be3df1e3ec436700d` |
| 黑豆 | `ou_a045f6ce109198fab5c90d56005550b8` |
| 阿福 | `ou_d7c9503a37be77c7ed3a40c3698e57ae` |
| 小宝 | `ou_7f65b28c189b3c0ed5cec0f97c618943` |

### 知识库批量上传脚本

路径: `/Users/hua/Desktop/渔芯科技/团队协作/feishu_kb_background.py`
支持断点续传，自动跳过已上传文件。

## 7. 错误码速查

| 错误码 | 含义 | 解决 |
|--------|------|------|
| 20043 | Invalid scope | 去掉 `wiki:node:readonly/write`，用 `wiki:wiki` |
| 1062009 | File size mismatch | 上传时 `size` 必须是精确字节数 |
| 1063002 | Permission denied（Bot间分享）| 平台限制，无解；改用ECS共享目录 |
| 1770001 | Invalid param（Docx block）| block类型不支持，降级为text |
| 99991663 | Invalid access token（Wiki写）| 改用user token |
| 99991661 | Missing access token | 请求未带Authorization头 |
| 99992402 | Field validation failed | API参数格式错误 |
