# 旺财 Windows 部署说明书

**部署包位置**: `~/Desktop/wangcai-transfer/`
**目标机器**: Windows PC
**部署时间**: 约 15-30 分钟

---

## 目录结构

```
wangcai-transfer/
├── profile/                   # 旺财身份
│   ├── MEMORY.md             # L1 记忆 (复制到 ~/.hermes/profiles/wangcai/memories/)
│   ├── USER.md               # L2 用户档案 (复制到 ~/.hermes/profiles/wangcai/memories/)
│   └── config.yaml           # Hermes 配置 (复制到 ~/.hermes/profiles/wangcai/)
├── skills/                    # 旺财专属技能
│   ├── wangcai-cad/          # CAD/SolidWorks 出图
│   └── wangcai-social-media/ # 自媒体自动化运营
├── scripts/                   # 部署工具
│   ├── setup_wangcai.ps1     # 一键部署脚本 (PowerShell)
│   └── AGENTS.md             # Codex CLI 配置
└── references/
    └── windows/               # Windows 相关资料
```

---

## 安装步骤

### 方式 A：一键部署（推荐）
1. 将 `wangcai-transfer/` 整个目录复制到 Windows PC
2. 打开 **PowerShell（管理员）**
3. 执行：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup_wangcai.ps1
   ```
4. 脚本自动完成所有步骤

### 方式 B：手动部署

#### Step 1: 安装依赖
```powershell
# Python 3.11+ (如果未安装)
# 下载: https://www.python.org/downloads/

# Git for Windows (如果未安装)
# 下载: https://git-scm.com/download/win

# Node.js (Codex CLI 需要)
# 下载: https://nodejs.org/
```

#### Step 2: 安装 Hermes Agent
```powershell
pip install hermes-agent
```

#### Step 3: 创建旺财 Profile
```powershell
# 创建 profile 目录
mkdir -p ~\.hermes\profiles\wangcai\memories
mkdir -p ~\.hermes\profiles\wangcai\config

# 复制配置
copy profile\* ~\.hermes\profiles\wangcai\memories\
copy profile\config.yaml ~\.hermes\profiles\wangcai\

# 复制技能
copy skills\wangcai-cad ~\.hermes\skills\wangcai-cad\
copy skills\wangcai-social-media ~\.hermes\skills\wangcai-social-media\
```

#### Step 4: 拉取 yuxin-skills 仓库
```powershell
git clone git@github.com:openclaw-cn-dev/yuxin-skills.git ~\.hermes\skills-repo
```

#### Step 5: 安装 Codex CLI
```powershell
npm install -g @openai/codex
codex auth login
copy scripts\AGENTS.md ~\.codex\AGENTS.md
```

#### Step 6: 启动 Gateway
```powershell
hermes gateway run --profile wangcai
```

---

## 验证

### 飞书连接验证
在飞书私聊旺财，发送 `/start` 或"你好"
→ 旺财应回复

### CAD 出图验证
```powershell
# 让旺财画一个箱体
# 输入: "画一个 600x400x300 壁厚5的箱体，出 STEP 和 DXF"
# 检查: ~/wangcai-workspace/cad_outputs/ 下有文件
```

### 自媒体发布验证
```powershell
# 让旺财发一篇抖音
# 输入: "发一篇水产养殖科普到抖音"
# 检查: 浏览器自动打开抖音创作者平台
```

---

## 运维命令

```powershell
# 查看 Gateway 状态
hermes gateway status --profile wangcai

# 停止 Gateway
hermes gateway stop --profile wangcai

# 启动 Gateway
hermes gateway run --profile wangcai

# 查看日志
Get-Content ~\.hermes\logs\wangcai.log -Tail 50

# 拉取最新技能
cd ~\.hermes\skills-repo && git pull
```

---

## 常见问题

### Q: Gateway 启动报错 "Feishu WebSocket connection failed"
A: 检查 config.yaml 中的 APP_ID 和 APP_SECRET 是否正确

### Q: SolidWorks COM 无法连接
A: 确保 SolidWorks 已安装，且在"管理员权限"下运行 Hermes
   ```powershell
   # 测试 COM
   python -c "import win32com.client; sw = win32com.client.Dispatch('SldWorks.Application'); print(sw.RevisionNumber())"
   ```

### Q: 浏览器自动化无法登录抖音/小红书
A: 第一次需要手动登录，Hermes 会自动保存 session
   - 在浏览器中登录账号
   - 下次 Hermes 会自动复用 Cookie

### Q: Codex CLI 无法安装
A: 先确保 Node.js 已安装
   ```powershell
   node --version  # 需要 v18+
   npm install -g @openai/codex
   ```
