---
name: auth-module
description: 通用用户认证模块 — FastAPI后端 + Vue3前端。可复用到任何项目，支持注册/登录/JWT/会话管理。触发条件：任何项目需要用户认证系统时使用。
triggers:
  - 用户认证
  - 登录注册
  - JWT
  - user authentication
  - FastAPI auth
  - Vue3 auth
---

# 通用用户认证模块

## 文件结构

```
auth-module/
├── SKILL.md
├── backend/
│   ├── security.py      # JWT + 密码加密
│   ├── database.py      # SQLite数据库
│   ├── models.py        # Pydantic模型
│   ├── service.py       # 业务逻辑
│   ├── router.py        # FastAPI路由
│   └── main.py          # 独立运行入口
└── frontend/
    ├── api/auth.js      # API调用
    ├── stores/auth.js   # Pinia store
    └── components/
        ├── LoginDialog.vue
        └── RegisterDialog.vue
```

## 快速使用

### 1. 复制后端文件

```bash
cp -r ~/.hermes/skills/module/auth-module/backend /你的项目/backend/auth
```

在 `main.py` 中挂载：

```python
from auth.router import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
```

安装依赖：
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic email-validator
```

### 2. 复制前端文件

```bash
cp ~/.hermes/skills/module/auth-module/frontend/api/auth.js /你的项目/src/api/
cp ~/.hermes/skills/module/auth-module/frontend/stores/auth.js /你的项目/src/stores/
cp -r ~/.hermes/skills/module/auth-module/frontend/components/* /你的项目/src/components/auth/
```

在 `App.vue` 中使用：

```vue
<template>
  <LoginDialog v-model="loginVisible" @success="onLoginSuccess" />
  <RegisterDialog v-model="registerVisible" @success="onRegisterSuccess" />
</template>

<script setup>
import { ref } from 'vue'
import LoginDialog from './components/auth/LoginDialog.vue'
import RegisterDialog from './components/auth/RegisterDialog.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const loginVisible = ref(false)
const registerVisible = ref(false)

function onLoginSuccess() {
  // 登录成功后的逻辑
}
</script>
```

## API接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 注册 | 否 |
| POST | `/api/auth/login` | 登录 | 否 |
| POST | `/api/auth/logout` | 登出 | 是 |
| GET | `/api/auth/me` | 获取当前用户 | 是 |
| PUT | `/api/auth/me` | 更新用户信息 | 是 |
| POST | `/api/auth/password` | 修改密码 | 是 |
| POST | `/api/auth/refresh` | 刷新Token | 否 |

## 数据库

SQLite自动创建，无需手动建表。数据库文件：`backend/auth.db`

## JWT配置

- Access Token：15分钟有效期
- Refresh Token：7天有效期
- 密码加密：bcrypt

## 依赖

**后端：**
- python-jose[cryptography]>=3.3.0
- passlib[bcrypt]>=1.7.4
- python-multipart>=0.0.9
- pydantic>=2.0
- email-validator>=2.0
- **Python >= 3.11**（或修改 `dict | None` 为 `Optional[dict]`）

**前端：**
- vue>=3.3
- pinia>=2.0
- element-plus>=2.0
- @element-plus/icons-vue>=2.0

## ⚠️ 已知问题

### access_token 字段名不一致
`service.py` 的 `login()` 方法返回 `"token": access_token`（line 46），但 `models.py` 的 `LoginResponse` 和 `Token` 模型都要求 `access_token` 字段。FastAPI 的 `response_model` 校验会导致 500 错误：`{'type': 'missing', 'loc': ('response', 'token'), 'msg': 'Field required'}`。

**修复：** 将 `service.py` 中 `"token"` 改为 `"access_token"`，同时在 `LoginResponse` 中补充 `refresh_token` 字段：

```python
# service.py — 修复
return {
    "access_token": access_token,   # ← 原为 "token"
    "refresh_token": refresh_token,
    "user": user,
}

# models.py — LoginResponse
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
```

### Python 3.10 兼容
`router.py` 和 `security.py` 使用了 `dict | None` 类型注解（Python 3.11+语法）。如果目标环境是Python 3.10，需要将 `dict | None` 替换为 `Optional[dict]`

### 登录响应字段名陷阱 (token vs access_token) ⚠️

**症状**：登录成功但前端 token undefined 或后端 500 `ResponseValidationError`。

**根因**：`service.py` login() 返回 `{"token": access_token, ...}`，但 `models.py` LoginResponse Pydantic 模型要求 `access_token` 字段。

**修复**：`service.py` 改为 `"access_token": access_token`；`models.py` LoginResponse 确保含 `access_token` + `refresh_token` + `token_type` + `user`。

**React 适配**（原模块为 Vue3）：用 `bare axios` + `window.location.href` 跳转；JWT 存 localStorage（`access_token`/`refresh_token`）；401 拦截器自动 refresh；刷新端点自身 401 不重试。：
```python
# 找到所有 dict | None，替换为 Optional[dict]
# 例如 security.py: verify_token 函数
def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
```

### 集成后必做
1. API层必须自动注入Bearer token（参考 `references/integration-guide.md`）
2. API层必须序列化body对象为JSON
3. Pinia store使用return语法时，函数用 `function` 声明，不用箭头函数
4. 前端必须用 `npm run dev` (Vite Dev Server) 而不是 `serve dist`——否则 API 代理不生效

### 🚨 LoginResponse 字段名不匹配（必修）

`models.py` 中 `LoginResponse` 使用 `token: str`，但 `service.py` 返回 `access_token`。
**这会导致所有登录请求返回 500 错误**。必须修复两处：

```python
# models.py — LoginResponse 改为：
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

# service.py — 返回值 key 改为：
return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "user": user,
}
```

验证：`curl -X POST /api/auth/login -d '{"username":"test","password":"test"}'` 应返回包含 `access_token` 的 JSON（不是 `token`）。

### React 适配

Vue3 组件可直接替换为 React 等价物：
- `auth.js` → `auth.ts`（使用 axios 实例，逻辑不变）
- `stores/auth.js` (Pinia) → `authStore.ts` (Zustand: `create<AuthState>`) 
- `LoginDialog.vue` → `Login.tsx`（遵循 react-vite-patterns：不用 `<form>`，用 `type="button" onClick`，`window.location.href` 做登录后跳转）
- 前端依赖：`zustand` 代替 `pinia`，不需要 `element-plus`

## 集成指南

完整避坑指南、验证步骤和最常见失败原因见 `references/integration-guide.md`（从 `auth-module-integration` skill 沉淀而来，覆盖建筑 AI 助手项目集成实践）。
