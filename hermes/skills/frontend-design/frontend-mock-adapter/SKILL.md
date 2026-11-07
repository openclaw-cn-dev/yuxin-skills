---
name: frontend-mock-adapter
description: 前端 Mock Adapter 架构模式 — 当后端API未完成时，用 mockAdapter.js + getApi() 动态切换实现前端独立开发调试
version: "1.0.0"
tags: [frontend, mock, api, vue, pinia]
---

# Frontend Mock Adapter Pattern

## When to Use
当后端API未完成，前端需要开发+调试时，采用Mock Adapter架构。

## 架构模式

```
frontend/src/api/
├── client.js          # 统一 HTTP client（fetch封装）
├── game.js            # 真实 API（对后端 /api/v1/game/*）
├── incentive.js       # 真实激励 API
└── mockAdapter.js     # Mock 适配器 ← 新建这个

frontend/src/stores/
├── game.js            # 使用 getApi() 动态切换
└── incentive.js       # 独立的激励 store
```

## 核心实现

### 1. mockAdapter.js — Mock API 模块

```javascript
const MOCK_DELAY = 300

const delay = (ms = MOCK_DELAY) => new Promise(r => setTimeout(r, ms))

// Mock数据
const MOCK_DATA = { ... }

// Mock API实现
export const mockGameApi = {
  async getAchievements() {
    await delay()
    return { success: true, data: MOCK_DATA.achievements }
  },
  // ... 其他方法
}

// 安装/卸载
export function installMockAdapter() { ... }
export function uninstallMockAdapter() { ... }
```

### 2. Store 中的动态切换

```javascript
import { gameApi } from '../api/game'
import { mockGameApi } from '../api/mockAdapter'

const USE_MOCK = true  // 后端完成改为 false

function getApi() {
  return USE_MOCK ? mockGameApi : gameApi
}

// 使用
async function fetchAchievements() {
  const data = await getApi().getAchievements()
  // 统一响应格式处理
  const items = data.data?.achievements || data.data || []
}
```

## 关键经验

### 响应格式兼容
后端和Mock的响应形状往往不一致，统一用这个模式处理：
```javascript
const raw = data.data || data
// 然后用 raw.xxx 而不是 data.xxx
```

### Store 分离原则
- game.js store 管游戏化功能（成就/签到/事件/公会）
- incentive.js store 管商业激励（鱼币/排行榜/奖金/积分）
- 两者都调用 getApi() 动态切换 mock/real

### Mock 数据质量
- 必须有 300ms 延迟模拟网络
- 字段名用 snake_case（与后端一致）
- 包含空状态、加载状态的真实数据结构

### user_id 处理
后端API的 user_id 有三种来源：
1. Header Authorization token 解析
2. Query parameter `?user_id=xxx`
3. Mock 硬编码 `mock_user_001`

Store 调用时不需要传，API client 自动从 token 解析或用 Mock 预设值。

## 切换到真实 API
1. 后端 API 完成
2. `const USE_MOCK = false` 
3. 确认后端响应字段名与前端预期一致
4. 移除 `data.data || data` 兼容层
