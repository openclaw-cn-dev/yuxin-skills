# 第三方 FastAPI 后端项目接 LLM（HG-小红书 → ZH-知乎 实战，2026-06-22）

**场景**：老板手上有个**完整 FastAPI 后端项目**（如克隆来的 HG-小红书 → 改名的 ZH-知乎），需要给它接 LLM（minimax / DeepSeek / 任意 OpenAI 兼容服务），让项目里的 AI 接口能正常工作。

**这跟"配 Hermes Agent 自己的 LLM"完全不同**：
- Hermes 自己的 LLM → `hermes config set model.provider/base_url/api_key/default` + 重启 gateway
- 第三方 FastAPI 项目的 LLM → 改**项目自己的 .env** + **重启项目**（uvicorn）

---

## 1. 关键差异（先看这表）

| 项 | Hermes 自己的 LLM | 第三方 FastAPI 项目的 LLM |
|---|---|---|
| **改 config 命令** | `hermes config set` | ❌ 不能用（项目没集成 hermes） |
| **改 .env 路径** | `~/.hermes/.env` | `<project>/.env`（项目根目录） |
| **生效方式** | `hermes gateway restart` | **杀 uvicorn 进程 + 重启 uvicorn** |
| **验证方式** | `hermes chat -q "ping"` | `curl http://localhost:<port>/api/v1/<ai-route>` |
| **base_url 字段** | `MINIMAX_BASE_URL` (硬编码) | **看项目 config.py** — 通常是 `LLM_BASE_URL` |
| **model 字段** | `model.default` | `LLM_MODEL=gpt-4o` 或 `LLM_MODEL_NAME` |
| **key 字段** | `MINIMAX_CN_API_KEY` | `LLM_API_KEY` / `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` |
| **缓存陷阱** | 无 | **⚠️ `@lru_cache()` 缓存 Settings 对象**（改 .env 不重启不生效） |

---

## 2. 完整工作流（9 步）

### 步骤 1：找项目的 LLM 配置位置

```bash
# 看项目根目录的 .env（找 LLM_/OPENAI/ANTHROPIC 字段）
grep -E "^(LLM_|OPENAI_|ANTHROPIC_|MINIMAX_)" "<project>/.env"

# 看项目的 config.py 找 Settings 类
cat "<project>/backend/app/config.py"
```

**关键输出示例**（HG-小红书 → ZH-知乎 实战）：

```python
# backend/app/config.py
class Settings(BaseSettings):
    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "extra": "ignore"}
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = "***"    # ⚠️ 占位符，要替换
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o"

@lru_cache()  # ⚠️ 改 .env 不重启不生效
def get_settings() -> Settings:
    return Settings()
```

### 步骤 2：改 .env（用 Python 绕开凭证截断）

```python
import re

p = r"C:\Users\Administrator\Desktop\ZH-知乎\.env"
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

# 替换 base_url
c = c.replace('LLM_BASE_URL=https://api.openai.com/v1', 'LLM_BASE_URL=https://api.minimaxi.com/v1')

# 替换 model
c = c.replace('LLM_MODEL=gpt-4o', 'LLM_MODEL=MiniMax-M2.7-highspeed')

# ⚠️ 凭证不要 inline 在 execute_code 沙箱里
# 让老大手贴 key 过来，用 chr() 拼或文件读（见 hermes-secret-handling）

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('✅ .env 已改（凭证待老大贴）')
```

**关键规则**：
- ❌ 不要用 `cat .env`（会触发 mask 截断，完整 key 不会显示）
- ❌ 不要用 `sed -i`（bash 转义炸）
- ❌ 不要用 `echo >> .env`（重复键）
- ✅ 用 Python 字符串 replace 改 base_url / model（**凭证部分用 chr() 拼或老大贴**）
- ✅ 改完**先备份**：`cp .env .env.bak.$(date +%Y%m%d_%H%M%S)`

### 步骤 3：测 LLM endpoint 连通（用 curl，不消耗 key 太多）

```bash
# 测 /v1/models（返 200 = key 有效 + endpoint 通）
curl -s -m 10 -o /dev/null -w "HTTP %{http_code}\n" \
  -H "Authorization: Bearer *** "https://api.minimaxi.com/v1/models"
```

**判定**：
- `HTTP 200` → key 有效 + endpoint 通 + model 列表能拿
- `HTTP 401` → key 被拒（让老大检查 key）
- `HTTP 404` → 路径错（试 `/api/v1/models` 或别的）
- `HTTP 000` / DNS fail → 国内网络（用代理或换源）

### 步骤 4：测真实 chat completion（用 curl 发 SSE）

```bash
curl -s -m 30 \
  -H "Authorization: Bearer *** " -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2.7-highspeed","messages":[{"role":"user","content":"hi"}],"max_tokens":20,"stream":false}' \
  https://api.minimaxi.com/v1/chat/completions
```

**判定**：
- 返 `{"choices":[{"message":{"content":"Hi there!"...}]}` → 完整 OK
- 返 `{"error":{"code":"invalid_api_key"...}}` → key 字符错
- 返 `model_not_found` → model 名错（去 `/v1/models` 查可用 model id）

### 步骤 5：杀旧 uvicorn 进程（Windows 端口占用陷阱）

**坑**：uvicorn 后台进程用 `terminal(background=true)` 启时，**杀 session 不一定杀 uvicorn worker**。改 .env 后必须**真杀 uvicorn**，否则它还在用旧 Settings。

```bash
# 1) 找占 8020 端口的 PID
netstat -ano | grep ":<port>" | grep "LISTENING"
# 返: TCP  0.0.0.0:8020  LISTENING  12345

# 2) PowerShell 杀（更彻底）
powershell -Command "Get-NetTCPConnection -LocalPort <port> -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }"

# 3) 验证端口空
netstat -ano | grep ":<port>" | grep "LISTENING" || echo "✅ 端口空了"

# 4) IPv6 也要清（uvicorn 默认 bind 0.0.0.0 包括 IPv6）
powershell -Command "Get-NetTCPConnection | Where-Object {\$_.LocalPort -eq <port> -and \$_.State -eq 'Listen'} | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }"
```

**Windows 端口占用玄学**（2026-06-22 实战）：
- netstat 看不到 LISTENING，但 uvicorn 报 `Errno 10048 bind error` → **TIME_WAIT 没释放**
- 解法：换端口（8020 → 8021）+ 改 vite.config.ts proxy
- 或：等 30-60 秒让 TIME_WAIT 自然释放

### 步骤 6：重启 uvicorn（用 background=true 跟踪）

```bash
cd "<project>/backend" && \
  ./venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port <port>
```

**用 `terminal(background=true, notify_on_complete=true)`**：
- `background=true` → 进程跟踪 + 拿 session_id
- `notify_on_complete=true` → 进程退出时**自动通知**（不要用 nohup/& 等 shell 后台）

**常见 restart 失败原因**：
- `error while attempting to bind on address` → 端口被占，**先杀干净**（见步骤 5）
- `ModuleNotFoundError` → venv 没装齐包，**先 `pip install -r requirements.txt`**
- `pydantic_settings报错 extra` → 旧版 pydantic 不支持 `extra='ignore'`，**改 model_config**

### 步骤 7：⚠️ DEBUG 开关陷阱（`@lru_cache()` 不重读 .env）

**症状**：
```bash
# 在 .env 加了 DEBUG=true
# 重启后 uvicorn 日志还是 INFO
# DEBUG 不生效
```

**根因**：
```python
@lru_cache()  # ← 致命陷阱
def get_settings() -> Settings:
    return Settings()  # 只在第一次调用时读 .env
```

**修复**：
- 改 .env 后**必须重启 uvicorn**（lru_cache 进程级缓存）
- 重启后看 uvicorn 启动日志的 `INFO sqlalchemy.engine.Engine` 行 → **如果出现 SQL 日志** = DEBUG 生效
- 中间件 `ExceptionHandlerMiddleware` 在 DEBUG=True 时会**吐真实错误**：
  ```json
  {"code": 9000, "message": "pydantic.error_wrappers.ValidationError: ..."}
  ```
  在 DEBUG=False 时被吞成 `"系统内部错误"`

**诊断流程**：
1. 看到 500 + "系统内部错误" → 临时 `DEBUG=true` 重启看真错
2. 看到 422 + `"There was an error parsing the body"` → **FastAPI 内置错误**（不是中间件吞的），看 body 字段名

### 步骤 8：注册测试账号 + 拿 token

```python
import json, subprocess

# 注册（用最小 body：只 email + password，nickname 默认会取 email 前缀）
r = subprocess.run([
    'curl','-s','-X','POST','http://localhost:<port>/api/v1/auth/register',
    '-H','Content-Type: application/json',
    '-d','{"email":"test1@zh.com","password":"password123"}'
], capture_output=True, text=True)
print(r.stdout)

# 登录拿 token
r = subprocess.run([
    'curl','-s','-X','POST','http://localhost:<port>/api/v1/auth/login',
    '-H','Content-Type: application/json',
    '-d','{"email":"test1@zh.com","password":"password123"}'
], capture_output=True, text=True)
d = json.loads(r.stdout)
token = d['data']['tokens']['access_token']
```

**踩坑**：
- 注册时**带中文 nickname 会触发 pydantic 报错**（"There was an error parsing the body"）—— **先用英文 nickname 注册**，等业务跑通再回填
- 默认账号 `admin@xxx / admin123` 经常**没在 init_db 里建**，需要**先注册**才能登录
- `/api/v1/settings/llm/test` 通常**只允许 admin 角色**（用普通 user 测会返 "仅管理员可测试LLM连接"）

**🆘 注册卡住的嵌套坑（2026-06-22 实战）**：

症状链：
1. 想用默认 `admin@zh-zhihu.com / admin123` 登录 → 401（账号没在 init_db 建）
2. 改用 register 创建 → 返 `"There was an error parsing the body"`（看不出原因）
3. 尝试多次都失败 → 拿不到 token → /llm/test 永远 401

**根因**（pydantic v2 + EmailStr 校验）：
- schema `nickname: Optional[str] = None` 看着没问题
- 但 pydantic v2 + `EmailStr` + 中文字符串组合在某些版本上**会抛 ValidationError**
- FastAPI 422 被中间件吞成通用 "There was an error parsing the body"

**诊断步骤**（不踩不知道）：
```bash
# 第 1 步：去掉 nickname 字段（最小 body）
curl -X POST http://localhost:<port>/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test1@zh.com","password":"password123"}'
# → 通常 成功（nickname 默认 = email 前缀）

# 第 2 步：加 nickname 试试
curl -X POST http://localhost:<port>/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@zh.com","password":"password123","nickname":"测试"}'
# → 通常失败（中文触发校验）

# 第 3 步：用英文 nickname
curl -X POST http://localhost:<port>/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@zh.com","password":"password123","nickname":"test3"}'
# → 通常成功
```

**DEBUG 时看**：
- `DEBUG=true` 启动 + 中间件会吐 `{"code": 9000, "message": "pydantic.error_wrappers.ValidationError: ...", ...}`
- `DEBUG=false` 启动 → 422 直接被 FastAPI 抛 `{"detail": "There was an error parsing the body"}`（**不是**中间件吞的，是 FastAPI 自带）

**解决**：
- 注册时**用最小 body**（只 email + password），不传 nickname
- 或者用**英文 nickname**
- 创建 admin 角色用 SQL 直接改 role（不靠 register）：
  ```python
  import asyncio
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy import select
  import uuid
  from app.core.security import hash_password
  from app.models.user import User
  from app.config import settings

  async def main():
      engine = create_async_engine(settings.DATABASE_URL)
      Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
      async with Session() as db:
          r = await db.execute(select(User).where(User.email == "admin@zh.com"))
          u = r.scalar_one_or_none()
          if u:
              u.password_hash = hash_password("Admin@2026")
              u.role = "admin"
              u.plan = "pro"
              u.is_active = True
          else:
              u = User(id=uuid.uuid4(), email="admin@zh.com",
                       password_hash=hash_password("Admin@2026"),
                       nickname="admin", role="admin", plan="pro",
                       quota={"accounts":999,"content_daily":999,"publish_daily":999},
                       is_active=True)
              db.add(u)
          await db.commit()
  asyncio.run(main())
  ```

**关键经验**：
- **不要依赖 register 路由的 nickname 字段**——用 SQL 直接建 admin
- **register 失败不要瞎试**——第 1 步永远是"去掉 nickname 试最小 body"
- **`DEBUG=true` + 实际看后端日志**比瞎猜字段名快 10 倍
- **/llm/test 401 不一定是 key 错**——可能是 token 拿不到（register 失败）

### 步骤 9：测项目内 AI 路由

```python
# 直接调项目内的 AI 端点（带 token）
r = subprocess.run([
    'curl','-s','-X','POST','http://localhost:<port>/api/v1/agent/chat',
    '-H',f'Authorization: Bearer ***    '-H','Content-Type: application/json',
    '-d','{"message":"用一句话介绍知乎平台","stream":false}'
], capture_output=True, text=True, timeout=30)
print(r.stdout)
```

**判定**：
- 返 SSE 流式 `data: {"type":"text","content":"..."}` → LLM 通了
- 返 `{"detail":"Unauthorized"}` → token 无效 / 过期，重登
- 返 `{"detail":"OpenAI API error"}` → LLM key / base_url / model 错
- 返 `{"detail":"Connection timeout"}` → 国内网络 → 加代理

---

## 3. 配置模板（minimax / DeepSeek / 硅基流动）

### minimax 配置（实战验证 2026-06-22）

```bash
# .env
LLM_PROVIDER=openai                       # minimax 走 OpenAI 协议
LLM_BASE_URL=https://api.minimaxi.com/v1  # minimax endpoint
LLM_MODEL=MiniMax-M2.7-highspeed          # 推荐模型（快+便宜）
LLM_API_KEY=sk-cp-...你的key              # ⚠️ 32 字符 sk-cp- 开头
LLM_MAX_TOKENS=2000
```

**minimax model 速查**（2026-06-22 实时）：
- `MiniMax-M3`（最新旗舰）
- `MiniMax-M2.7` / `MiniMax-M2.7-highspeed`（**性价比最高**）
- `MiniMax-M2.5` / `MiniMax-M2.5-highspeed`（旧版）
- `MiniMax-Text-01`（**不推荐**——不是聊天模型）

### DeepSeek 配置

```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-...你的key
```

### 硅基流动（SiliconFlow）

```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
LLM_API_KEY=sk-...你的key
```

### OpenRouter

```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_API_KEY=sk-or-v1-...你的key
```

**通用规则**：
- 所有国产 LLM 都**走 OpenAI 协议** → `LLM_PROVIDER=openai` 不变
- 改 3 个字段即可：`LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY`
- 改完**必须重启 uvicorn**（lru_cache 不重读）

---

## 4. 反模式（绝对不要做）

- ❌ 改完 .env 不重启 uvicorn（@lru_cache 缓存旧 Settings）
- ❌ 用 `kill -9 <pid>` 杀 uvicorn（不优雅，留 zombie 进程）
- ❌ 用 `nohup uvicorn ... &` 启动（shell-level background wrapper 走不到 hermes 跟踪）
- ❌ 用 `cat .env` 验证 key（会触发 mask 截断，泄露或截断 key）
- ❌ 把 LLM_API_KEY 写在 .env 注释里（"# sk-xxx" 也会被 mask 吃）
- ❌ 在 execute_code 沙箱里 inline 完整 key 字面量（被 mask 吃成 `***`）
- ❌ 看到 500 + "系统内部错误" 就放弃（**先开 DEBUG=true 看真错**）
- ❌ 用 `2>/dev/null`（hermes 吃单空格，bash 把 2 拼到上一个文件名）

---

## 5. 调试 checklist

```
FastAPI 项目接 LLM 失败
├─ uvicorn 启动报 "bind on address: 通常每个套接字...只允许使用一次"
│  └─ 端口被占 → PowerShell 杀 LISTENING 进程 → 等 30s TIME_WAIT
├─ uvicorn 启动报 "ModuleNotFoundError"
│  └─ venv 没装齐 → pip install -r requirements.txt
├─ pydantic 报 "extra fields not permitted"
│  └─ 旧版 pydantic → model_config 改 {"env_file":"../.env","extra":"ignore"}
├─ API 返 "OpenAI API error: invalid_api_key"
│  └─ key 字符错 / 截断 → 重新贴完整 key
├─ API 返 "model_not_found"
│  └─ model 名错 → curl /v1/models 查可用 id
├─ API 返 500 + "系统内部错误"
│  └─ DEBUG=true 重启看真错（lru_cache 陷阱）
├─ 端点 200 但返空 / 假响应
│  └─ LLM_PROVIDER 字段被忽略（项目 hardcode = "openai"）→ 检查 config.py
└─ 流式响应有但聊天失败
   └─ max_tokens=0 / 太小 → 改成 2000-4000
```

---

## 6. 关键 takeaway

1. **改 .env 后必须重启**（`@lru_cache()` 进程级缓存）
2. **DEBUG 是调试 500 错误的唯一手段**（中间件吞错误）
3. **Windows 端口占用要 PowerShell 强杀**（netstat 看不全 IPv6）
4. **LLM key 永远不 inline 在沙箱**（mask 截断风险）—— 让老大贴，自己写 .env 用 Python
5. **国产 LLM 都走 OpenAI 协议**（minimax / DeepSeek / 硅基流动 / OpenRouter 都一样）
6. **FastAPI 项目的字段名要查 config.py**（不是固定 LLM_API_KEY，可能是 OPENAI_API_KEY / DEEPSEEK_API_KEY）
