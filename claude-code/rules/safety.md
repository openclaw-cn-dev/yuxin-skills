# 渔芯项目 — 安全规则

> 加载时机：所有项目自动加载
> Hooks 已自动拦截危险命令（pre-bash-guard.sh）

## 命令禁区

### 绝对禁止
- ❌ `rm -rf /` / `rm -rf ~` / `rm -rf .`
- ❌ `git push --force` 到 main/master
- ❌ `sudo` 任意命令
- ❌ `chmod 777`
- ❌ `curl ... | bash` / `wget ... | sh`
- ❌ 改 `~/.ssh/` / `~/.aws/` / `~/.bashrc` / `~/.zshrc` / `/etc/`
- ❌ `dd if=... of=/dev/sd*`
- ❌ `chown -R` 改系统目录

### 软禁止（需华哥确认）
- ⚠️ 删文件（非系统目录）
- ⚠️ 重启服务
- ⚠️ push 远端
- ⚠️ 数据库变更（DROP/ALTER）

## 凭证管理

### 禁做的事
- ❌ 把 token / API key / 密码写进代码
- ❌ 把 `.env` 提交到 git
- ❌ 在 log / print 中输出敏感信息
- ❌ 硬编码数据库连接字符串

### 应做的事
- ✅ 用 `os.environ.get()` 或 `pydantic-settings` 读环境变量
- ✅ `.env` 写进 `.gitignore`
- ✅ 敏感字段输出时 mask（`***`）

## 安全扫描规避

### tirith 拦截模式（自动触发 HIGH 警报）
- ❌ `curl URL | python3` → 拆成两步
- ❌ `cat file | python3` → 用 `python3 file.py`
- ❌ 含 confusable 字符（→/✓/全角符号）→ 改用 ASCII

## 网络安全

- 默认允许外网（`api.*`、GitHub、内网 RKR 都没问题）
- 嵌入新开发系统的 Agent 禁网 → 配置时检查
- 钓鱼链接、下载可疑脚本 → 立即停手汇报
