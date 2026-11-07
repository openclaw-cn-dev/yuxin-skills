# 飞书 230002 错误排查

> 适用：飞书机器人推送 → 群消息
> 错误码：[230002] Bot/User can NOT be out of the chat
> 创建：2026-06-09

## 错误现象

```python
send_message(action='send', target='feishu:oc_xxxxx', message='...')
# → {"error": "Feishu send failed: [230002] Bot/User can NOT be out of the chat."}
```

## 根因

**飞书机器人必须先在群里**——`chat_id` 错 / 机器人没被加进群 / 群被解散 / 机器人被踢。

**这是飞书的安全设计**——**机器人不能"凭空"进群**。

## 修复步骤

### 1. 验证 chat_id 正确

- chat_id 格式：`oc_` + 32 位 hex（如 `oc_c1bf60f8d03aefcbcb18f595e7ef4e19`）
- 来源：飞书管理后台 → 应用 → 群机器人 → 详情

### 2. 老大手动加机器人

**步骤**：
1. 飞书 App → 打开群
2. 右上角 `···` → 设置
3. 群机器人 → 添加机器人
4. 搜索"小弟"（或你的机器人名）
5. 添加
6. 给"发消息"权限

**4 群都加一遍**。

### 3. 验证机器人在线

```bash
# 在群里发 @小弟 任意内容
@小弟 在吗
```

机器人应**秒回**——证明在线。

### 4. 重试推送

```python
send_message(action='send', target='feishu:oc_xxxxx', message='test')
```

## 其他常见飞书错误码

| 错误码 | 含义 | 修复 |
|---|---|---|
| 230002 | Bot 不在群 | 老大手动加机器人 |
| 230001 | token 无效 | 重新走 tenant_access_token 流程 |
| 230020 | app 权限不足 | 飞书后台 → 应用权限 → 加 `im:message` |
| 230021 | 群 ID 无效 | 重新拿 chat_id |
| 230022 | 消息超长 | 切分消息（飞书限制 30KB）|

## 群多时的批量配置

```json
// groups_config.json
{
  "groups": [
    {"name": "群1", "chat_id": "oc_xxx1", "status": "active"},
    {"name": "群2", "chat_id": "oc_xxx2", "status": "active"},
    {"name": "群3", "chat_id": "oc_xxx3", "status": "pending"}
  ]
}
```

`status: pending` = 群还没建，**先填 chat_id 占位**——`active` = 已加机器人可推送。

## 推送脚本模板

```python
import subprocess

def push_feishu_group(chat_id: str, message: str) -> bool:
    """推送到指定群"""
    cmd = ["hermes", "send", "feishu", chat_id, "--message", message]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            if "230002" in result.stderr:
                print(f"❌ {chat_id} 机器人不在群，老大手动加")
                return False
            elif "230020" in result.stderr:
                print(f"❌ {chat_id} 权限不足，飞书后台加 im:message")
                return False
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 推送失败: {e}")
        return False
```

## 完整的多群推送流程

1. 老大建 4 群（飞书 App 手動）
2. 老大拿到 4 个 chat_id（DM 小弟）
3. 小弟填 `groups_config.json`
4. **老大把机器人加到 4 群**（**老大手动**）
5. 小弟跑 v2 测试（**4 群各推一条**）
6. 全成功 → 写"4 群上线确认"卡片
7. 接入 stdin watch 模式（**粘贴触发**）或 ngrok（**全自动**）
