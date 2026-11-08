# Secret 截断应对（Hermes 0.15.1）

`security.redact_secrets: true` 是 Hermes 默认行为。**所有 LLM 工具的输出**（write_file / execute_code / patch / terminal stdout 在某些管道里）里的 secret-like 字符串会被截成 `XXXX...YYYY` 形式（保留前 4 后 2 位）。

## 表现

```
# 实际文件内容（disk OK）：
FEISHU_APP_SECRET=REDACTED_REPLACE_VIA_FLYBOOK_CONSOLE
# LLM 工具 cat/od 看到的（截短）：
FEISHU_APP_SECRET=REDACT...LE
```

关键：**磁盘文件是完整的**。截短只发生在 LLM 工具的回显/返回值里。**别因此重新写文件**——会越改越错。

## 正确做法

### 写 secret 到磁盘

```bash
cat > ~/.hermes/profiles/agent-X/.env <<'EOF'
FEISHU_APP_ID=cli_完整
FEISHU_APP_SECRET=完...
EOF

# 验证
od -c ~/.hermes/profiles/agent-X/.env | tail -3
# 看末尾几个字节是 Secret 真实结尾 = 写对了
```

### 验证 secret 落地

```bash
# 字节级验证（推荐）
od -c file | tail -3

# 大小验证
stat -c '%n %s bytes' file

# sha256 哈希（最稳）
sha256sum file
```

### 临时关掉 redaction（仅调试）

```bash
hermes config set security.redact_secrets false
# ⚠️ 写完记得开回去，**重启 session 才生效**
hermes config set security.redact_secrets true
```

⚠️ `redact_secrets` 是 import-time 快照，**当前 session 改了不立即生效**。要么重启，要么就老老实实走 `cat + od -c` 不依赖 LLM 工具回显。

## 哪些工具会被截

| 工具 | 会被截？ | 替代 |
|---|---|---|
| write_file / patch 返回值 | ✅ | `cat > file <<EOF` |
| execute_code print 输出 | ✅ | `od -c` shell 验证 |
| terminal stdout | 部分（heredoc 不截） | 已知坑就 OK |
| browser_get / web_extract | ❌（远程内容不截） | 直接用 |
| read_file 读非 secret 内容 | ❌ | 直接用 |

## 与 OS 加密的搭配

更稳的方案（部署时再做）：

- Windows: `wincred` CLI 存到凭据管理器，`.env` 只存 placeholder，hermes 启动时从 cred 注入
- Linux: `secretstorage` / `keyring` 库
- macOS: Keychain

小弟这台机子没装 keyring 库 + 沙箱拦 pip install，**先用 chmod 600 兜底**。NTFS 不管 POSIX mode，所以文件被所有用户可读——靠 ACL 也兜不住，**部署时必须换正经加密**。
