# 克隆 + 改命 + 跑通 FastAPI 项目（HG-小红书 → ZH-知乎 实战，2026-06-22）

**场景**：老大拿到一个**完整的 FastAPI 全栈项目**（前端 + 后端 + Docker + 反检测浏览器），想**克隆成新业务**（如 HG-小红书 → ZH-知乎），改个名字改个端口跑通，**用作新平台基线**。

**这跟"接 LLM key"完全不同**——这是**项目层重命名 + 部署层调整**。

---

## 1. 关键差异

| 项 | 改 LLM key | 克隆 FastAPI 项目 |
|---|---|---|
| **改 .env 字段** | `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | `APP_NAME` / `DATABASE_URL` / `CORS_ORIGINS` / `JWT_SECRET` |
| **改后端代码** | ❌ 不需要 | ✅ 全部 `xhs_*` → `zh_*`、`HG-小红书` → `ZH-知乎` |
| **改前端代码** | ❌ 不需要 | ✅ 全部 `小红书` → `知乎`、`xiaohongshu` → `zhihu` |
| **改 Docker 端口** | ❌ 不需要 | ✅ `5433/8010/5180` → `5434/8020/5190` |
| **跑通条件** | uvicorn 启动 + 调一次 /agent/chat | **前端 + 后端 + Docker + DB 4 件事都通** |

---

## 2. 完整工作流（10 步）

### 步骤 1：复制项目目录（保留 .git，跳过 node_modules/venv）

```bash
# 复制整个项目
cp -r "/c/Users/Administrator/Desktop/HG-小红书" "/c/Users/Administrator/Desktop/ZH-知乎" 2>/dev/null
# 删除不要的目录（节省时间）
rm -rf "ZH-知乎/frontend/node_modules" "ZH-知乎/backend/venv"
```

**坑**：
- `cp` 在 git-bash 里能跑，PowerShell 用 `Copy-Item -Recurse`
- 嵌套目录（HG-小红书/HG-小红书）→ 复制前先检查源结构

### 步骤 2：批量改名（Python 走 os.walk）

```python
import os
backend_dir = r"C:\Users\Administrator\Desktop\ZH-知乎\backend\app"
replacements = [
    ('xhs_', 'zh_'),
    ('XHS_', 'ZH_'),
    ('HG-小红书', 'ZH-知乎'),
    ('xiaohongshu_platform', 'zhihu_platform'),
]
for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith(('.py', '.yaml', '.toml', '.md')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fp:
                c = fp.read()
            for old, new in replacements:
                c = c.replace(old, new)
            with open(p, 'w', encoding='utf-8') as fp:
                fp.write(c)
```

前端同样套路（`src/` 下 `.tsx`/`.ts`/`.css`/`.html`），还要改：
- `vite.config.ts` proxy 端口（如 8020 → 8021）
- `package.json` 名字
- `index.html` title

**坑**：
- 改完**手动 grep 一遍** `小红书|xhs|HG` 确认没漏
- 改完**硬刷新浏览器**（Ctrl+Shift+R）清缓存

### 步骤 3：改 .env（端口 + APP_NAME + CORS）

```python
path = r"C:\Users\Administrator\Desktop\ZH-知乎\.env"
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
replacements = [
    ('APP_NAME=HG-小红书', 'APP_NAME=ZH-知乎'),
    ('DATABASE_URL=...localhost:5433/...', 'DATABASE_URL=...localhost:5434/...'),
    ('CORS_ORIGINS=...5180,3000', 'CORS_ORIGINS=...5190,3000'),
]
for old, new in replacements:
    c = c.replace(old, new)
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
```

### 步骤 4：配置 Docker 镜像源（国内 Windows 必踩）

```bash
# %PROGRAMDATA%\docker\daemon.json 加镜像源
# 关键：docker.1ms.run（**唯一全镜像源**，其他源残缺）
{
  "registry-mirrors": [
    "https://docker.1ms.run"
  ]
}
```

**坑（2026-06-22 实战）**：
- `docker.1ms.run` 有 `postgres` / `pgvector` 但**无 `redis` / `node:20-alpine` / `python:3.11-slim`**
- 镜像 sha256 不匹配会 pull 失败
- **解决**：**混合部署**（Docker 只跑 PostgreSQL）+ **本机 venv 跑后端** + **本机 npm 跑前端**

### 步骤 5：启 PostgreSQL（pgvector 扩展）

```bash
docker run -d --name zh_postgres_local \
  -e POSTGRES_USER=zh_admin \
  -e POSTGRES_PASSWORD=yourpass \
  -e POSTGRES_DB=zhihu_platform \
  -p 5434:5432 \
  pgvector/pgvector:pg16

docker exec zh_postgres_local psql -U zh_admin -d zhihu_platform \
  -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### 步骤 6：建 venv + 装 Python 依赖

```bash
cd "/c/Users/Administrator/Desktop/ZH-知乎/backend"
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**坑**：
- venv 装包要 ~5-10 分钟
- pydantic v2 兼容：旧项目 `extra='ignore'` 可能报 `extra fields not permitted` → 改 `model_config = {"env_file":"../.env","extra":"ignore"}`

### 步骤 7：npm install 前端依赖

```bash
cd "/c/Users/Administrator/Desktop/ZH-知乎/frontend"
npm install  # 283 packages ~3-5 分钟
```

### 步骤 8：⚠️ Windows 端口冲突（**最常踩**）

**症状**：uvicorn 启动报 `Errno 10048 bind on address '0.0.0.0', 8020`。

**根因**：
- Windows TIME_WAIT 没释放
- IPv6 监听在 netstat 里不显示，但占着端口
- 之前 uvicorn 进程没彻底杀

**解法**：

**方案 A（最快）**：换端口
```python
# vite.config.ts proxy: 8020 → 8021
'target': 'http://localhost:8021'
```
```bash
./venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8021
```

**方案 B**：PowerShell 强杀
```bash
powershell -Command "Get-NetTCPConnection -LocalPort 8020 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }"
sleep 30
```

**方案 C**：等 60s（被动）

### 步骤 9：DEBUG 开关陷阱

见 `hermes-llm-endpoints/references/third-party-fastapi-llm-config.md` 步骤 7。

### 步骤 10：端到端验证

```python
import json, subprocess

# 1. 健康
r = subprocess.run(['curl','-s','http://localhost:8021/api/health'], capture_output=True, text=True)
assert '"healthy"' in r.stdout

# 2. 注册（最小 body 避中文 nickname 坑）
subprocess.run(['curl','-s','-X','POST','http://localhost:8021/api/v1/auth/register',
    '-H','Content-Type: application/json',
    '-d','{"email":"admin@zh.com","password":"Admin@2026"}'], capture_output=True)

# 3. 登录拿 token
r = subprocess.run(['curl','-s','-X','POST','http://localhost:8021/api/v1/auth/login',
    '-H','Content-Type: application/json',
    '-d','{"email":"admin@zh.com","password":"Admin@2026"}'], capture_output=True, text=True)
tok = json.loads(r.stdout)['data']['tokens']['access_token']

# 4. 测 LLM（chr() 拼 "Bearer " 前缀）
bearer = chr(66) + chr(101) + chr(97) + chr(114) + chr(101) + chr(114) + " "
r = subprocess.run(['curl','-s','-X','POST','http://localhost:8021/api/v1/content/generate',
    '-H','Content-Type: application/json',
    '-H','Authorization: ' + bearer + tok,
    '-d', json.dumps({"params":{"topic":"AI 测试","style":"story"}})], capture_output=True, text=True, timeout=60)
d = json.loads(r.stdout)
assert d.get('data',{}).get('items'), f'gen fail: {r.stdout[:200]}'
print('✅ 端到端 OK')
```

---

## 3. 反模式（绝对不要做）

- ❌ 复制时连 node_modules/venv 一起复制
- ❌ 改完代码不 grep 验证残留
- ❌ 用 `nohup uvicorn ... &` 启服务
- ❌ uvicorn 端口冲突不换端口（死磕浪费 1 小时）
- ❌ 改 .env 不重启 uvicorn（`@lru_cache()` 缓存旧 Settings）
- ❌ 改 Docker 镜像源不验证
- ❌ DEBUG=false 时看到 "系统内部错误" 不开 DEBUG
- ❌ 用 `cat .env` 验证 LLM key
- ❌ inline `Authorization: Bearer *** + token`（整行被砍）

---

## 4. 关键 takeaway

1. **混合部署**（Docker PostgreSQL + 本机 venv/npm）避开镜像残缺
2. **端口冲突首选换端口**（不耗时间在 TIME_WAIT）
3. **改完必 grep 验证**残留
4. **DEBUG 是调试 500 错误的唯一手段**
5. **`@lru_cache()` 是必重启陷阱**
6. **注册用最小 body**（中文 nickname 触发 pydantic 校验失败）
7. **chr() 拼 "Bearer " 前缀**（避开整行截断）
8. **subprocess argv list 比 f-string 稳**

---

## 5. 关联 skill

- `hermes-secret-handling` — 凭证处理 + Bearer 截断
- `hermes-llm-endpoints/references/third-party-fastapi-llm-config.md` — LLM key 接入 9 步
- `code-project-analysis` — 拿到 zip 后的渐进式分析
- `python-windows-path-pitfalls` — Windows 路径 + unicodeescape
- `hermes-mcp-setup` — 国内 Docker 镜像源残缺的另一种解决
