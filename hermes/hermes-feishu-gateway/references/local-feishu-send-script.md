# 本地 feishu_send.py 模板 — 绕开 hermes 内置 send_message 的 99992402

## 何时用

- hermes gateway 收到飞书消息 + LLM 调通 + 生成回复,但回话推送 `99992402 field validation failed`
- text fallback 也失败(skill 表里第 1 行"PID 僵尸"那条修法无效)
- 根因:hermes 内置 `send_message` 工具的 `content` 字段序列化方式跟飞书 API 不兼容(text fallback 用的同一路径,所以也救不了)

## 修法

写一个**零依赖(标准库 only)** 的 Python 脚本,放 `profile/workspace/tools/feishu_send.py`,SOUL.md 引导 LLM 调它,**不走** hermes 内置 `send_message`。

零依赖是关键 —— `execute_code` 沙箱是干净 Python 3.11(临时目录),**没装 requests**。`urllib` 是标准库,在沙箱和 hermes 系统 python 下都能跑。

## 完整脚本

```python
"""feishu_send.py — 小宝专用飞书 send 脚本,零依赖,标准库 only

用法:
  python feishu_send.py "消息内容" [chat_id]
  python feishu_send.py "消息内容"          # 默认推目标群
"""
import json
import sys
import urllib.request

# TODO: 替换成你的目标群
DEFAULT_CHAT = "oc_xxxxx"
ENV_PATH = r"C:\Users\Administrator\AppData\Local\hermes\profiles\<PROFILE>\.env"


def load_env():
    env = {}
    with open(ENV_PATH, "rb") as f:
        for line in f:
            if b"=" in line and not line.startswith(b"#"):
                k, _, v = line.partition(b"=")
                env[k.decode().strip()] = v.decode().strip()
    return env


def http_post_json(url, payload, token=None, timeout=15):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_token(app_id, app_secret):
    data = http_post_json(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        {"app_id": app_id, "app_secret": app_secret},
    )
    if data.get("code") != 0:
        raise RuntimeError(f"token 失败: {data}")
    return data["tenant_access_token"]


def send_text(token, chat_id, text):
    # ⚠️ 关键:content 必须是 {"text": "..."} 字符串 JSON
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    return http_post_json(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        payload, token=token,
    )


def main():
    if len(sys.argv) < 2:
        print("用法: python feishu_send.py '消息' [chat_id]", file=sys.stderr)
        sys.exit(1)
    text = sys.argv[1]
    chat_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CHAT
    env = load_env()
    token = get_token(env["FEISHU_APP_ID"], env["FEISHU_APP_SECRET"])
    result = send_text(token, chat_id, text)
    if result.get("code") == 0:
        print(f"✅ 发送成功 msg_id={result['data']['message_id']}")
    else:
        print(f"❌ {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## SOUL.md 怎么写

`xiaobao/workspace/SOUL.md` 工作流里加:

```markdown
4. **推送**:**用本地脚本** `python "C:\Users\Administrator\AppData\Local\hermes\profiles\xiaobao\workspace\tools\feishu_send.py" "消息"`,**不要**用 hermes 内置 `send_message` 工具(它有 99992402 格式 bug)
```

红线里加:

```markdown
- **回飞书消息用本地脚本** `python tools/feishu_send.py "text"`,**绝不用** hermes 内置 `send_message` 工具(有 99992402 格式 bug)
- **回飞书消息必须纯文本短句**,不嵌套卡片/链接预览/复杂 mentions
```

## 为什么不用 hermes 内置 send_message 也能工作

- wss 收到飞书事件 → hermes 创建 session → LLM 调通 → 生成回复字符串
- LLM 按 SOUL.md 引导,调 `terminal` 工具跑 `python tools/feishu_send.py "..."`
- 脚本独立打飞书 REST API,完全绕开 hermes 内置 send_message 工具链
- 飞书侧看到的就是 bot 发的纯文本消息(跟内置工具推的效果一样)

## 验证

```bash
# 直接跑
python tools/feishu_send.py "test message"

# 走 hermes chat 触发 LLM
hermes --profile xiaobao chat -q "用 python 调本地脚本给我推一条'链路通了'到飞书"
```

## 已知限制

- 不支持富文本/卡片/图片,只发纯 text
- 没用 `requests` 是因为 hermes `execute_code` 沙箱没装(用 `urllib` 标准库即可)
- 如果要发文件/图片,扩 `send_text` 加 `msg_type=file/image` 分支即可(API 参考 [feishu-toolkit skill](../../openclaw-imports/feishu-toolkit/SKILL.md))
