# Feishu Card Construction (interactive card)

Full element reference for building `msg_type: "interactive"` cards. Drawn from
the `feishu-bot-push` skill.

## Complete working template

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": "卡片标题"},
        "template": "blue"  # blue / green / red / orange / purple / grey
    },
    "elements": [
        # 文本块 (supports markdown)
        {"tag": "div", "text": {"tag": "lark_md", "content": "**加粗** 普通文本\n第二行"}},
        # 分隔线
        {"tag": "hr"},
        # 按钮组
        {"tag": "action", "actions": [
            {"tag": "button", "text": {"tag": "plain_text", "content": "主按钮"},
             "type": "primary", "url": "file:///C:/path/"},
            {"tag": "button", "text": {"tag": "plain_text", "content": "次按钮"},
             "type": "default", "url": "https://..."}
        ]},
        # 注释
        {"tag": "note", "elements": [{"tag": "plain_text", "content": "🤖 自动推送 · 时间戳"}]}
    ]
}
```

## Critical field rule

- `content` field MUST be a **JSON string** (not a dict!). This is the #1
  cause of `99992402 "field validation failed"` — see pitfall #1 in the main
  SKILL.md.

## Common element types (compact table)

| Tag | Purpose | Key fields |
|---|---|---|
| `div` | Text block (markdown via `lark_md`) | `text.content` |
| `hr` | Horizontal rule | — |
| `action` | Button group container | `actions[]` |
| `button` | Single button | `type` (primary/default/danger), `url` (supports `file:///C:/...` for local files) |
| `note` | Footer note / time stamp | `elements[].content` |
| `image` | Inline image | `img_key` (upload via `/open-apis/im/v1/images`) |
| `field` | Two-column compact text | `text.content` |

## Common card patterns

### 1. Daily report with quick-action buttons (most used)

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {"title": {"tag": "plain_text", "content": "🦐 水产日报"}, "template": "blue"},
    "elements": [
        {"tag": "div", "text": {"tag": "lark_md", "content": "**今日 10 篇**\n[具体内容...]"}},
        {"tag": "hr"},
        {"tag": "action", "actions": [
            {"tag": "button", "text": {"tag": "plain_text", "content": "打开桌面"},
             "type": "primary", "url": "file:///C:/Users/Administrator/Desktop/知识库/"},
            {"tag": "button", "text": {"tag": "plain_text", "content": "看 RAG"},
             "type": "default", "url": "https://..."}
        ]},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": "🤖 9:00 自动推送"}]}
    ]
}
```

### 2. Header template colors

- `blue` (default) — neutral info
- `green` — success / healthy
- `red` — error / critical
- `orange` — warning
- `purple` — special
- `grey` — de-emphasized

## Source references

- `../2026-06-06-3-business-line-deploy.md` — the 3-业务线 deploy that
  exercised these card patterns in production
- The full send-message API call shape lives in the main SKILL.md (pitfall #1
  covers the `content` field trap)
