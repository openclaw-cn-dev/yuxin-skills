# Electron 二进制在 Windows + git-bash 装机的踩坑与解法

`npm install electron` 在 Windows 上有时**下不到 `dist/electron.exe`**,但 npm 报"up to date in 2s"、你以为装好了。这篇是 2026-06-13 实测的根因 + 修法,适用于任何"装 Electron 装出来的没 electron.exe"场景。

---

## 症状(必中其一)

- `ls node_modules/electron/dist/` 看到 `locales/` 但**没** `electron.exe`
- 跑 `node install.js` 立刻返 0、**没任何输出**,dist 还在原地
- 跑 `node install.js` 报 `stdin is not a tty` 然后 `process.exit(1)` 被静默吞

**核心假象**:`isInstalled()` 看到 `dist/locales/` 还在,以为装好,直接 `process.exit(0)`。但 `dist/electron.exe` 根本没解压出来。

---

## 根因 1:`extract-zip` 拒绝相对路径(主因)

`electron@32.x` 的 `install.js` 调用 `extract-zip` 时:

```js
const distPath = path.join(__dirname, 'dist');
return extract(zipPath, { dir: distPath });
```

`__dirname` 在 git-bash 的 Windows 进程下被解析成**相对路径**(如 `C:\Users\Administrator\Desktop\foo\node_modules\electron\dist`),`extract-zip@2` 强校验:

```
Error: Target directory is expected to be absolute
    at module.exports (.../extract-zip/index.js:167:11)
```

`install.js` 的 `.catch(err => { console.error(err.stack); process.exit(1) })` 报错时,如果用 `node install.js < /dev/null` 或带 `< /dev/null` 重定向,**stderr 不会回显**,你看到的就是 0 字节输出 + 进程退出。

---

## 根因 2:`stdin is not a tty`

如果用 `node install.js` 在**没有 PTY** 的子进程里跑(hermes 的 `terminal(background=true)` 默认不算 TTY),`@electron/get` 拉子进程时检测到 stdin 不是 TTY,直接 `process.exit(0)`,**zip 都不下**。

**修法**:
- `terminal` 工具加 `pty=true` 让它走伪终端
- 或手动用 `< /dev/null` 喂个空 stdin(部分版本会绕开)

---

## 手动修法(已装好 zip 没解压时)

zip 已经在 `~/AppData/Local/electron/Cache/<sha256>/electron-v<ver>-win32-x64.zip`,113MB+。

```bash
# 1) 找 zip 路径
ls ~/AppData/Local/electron/Cache/ 2>&1

# 2) 删残留 dist(否则 isInstalled() 假阳性)
cd <项目>/node_modules/electron
rm -rf dist path.txt

# 3) git-bash unzip 到绝对路径(关键:不能让它走相对路径)
mkdir -p dist
cd dist
unzip -q "/c/Users/Administrator/AppData/Local/electron/Cache/<hash>/electron-v<ver>-win32-x64.zip"
ls electron.exe  # 应该看到 ~150MB 的 binary

# 4) 写 path.txt 和 dist/version 让 isInstalled() 走真阳性
cd ..
echo "electron.exe" > path.txt
echo "v<ver>" > dist/version   # 如 "v32.3.3"

# 5) 验收
./dist/electron.exe --version  # 期望:v<ver>
```

---

## 自动诊断脚本(1 行判死活)

```bash
[ -f node_modules/electron/dist/electron.exe ] && echo OK || echo BROKEN
```

`BROKEN` = 走上面的手动修法 §3。

---

## 反模式(不要再做)

- ❌ `npm install electron` 后只看 `node_modules/electron/package.json` 有 version 就以为装好 → **没 electron.exe**
- ❌ `node install.js` 报 exit 0 就以为装好 → **要看 dist/electron.exe 真在**
- ❌ `ELECTRON_MIRROR=...` 设了重下还是只有 locales → **zip 已下好,是解压失败,跟镜像无关**
- ❌ 反复 `npm uninstall && npm install` 浪费时间 → **zip 已在 cache,直接 unzip**
- ❌ 在 execute_code 里 `subprocess.run(["npm", ...])` → **FileNotFoundError** → 一律走 `terminal()` 工具
- ❌ 用 `&` shell 层 backgrounding 起 Electron → 在 git-bash 不真后台 → 改 `terminal(background=true)`

---

## 关联引用

- 同 umbrella `llm-cli-setup` SKILL.md:execute_code 子进程找不到 npm 的坑(根因也是 PATH/子进程,这套坑不只 npm install electron)
- 同 umbrella `codex-cli-config.md` §5:Codex 桌面 GUI 启动方法(用 `terminal(background=true)` 拉 `%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\codex.exe`)

---

## 验证矩阵(本会话全过过)

| 命令 | 期望 | 失败诊断 |
|---|---|---|
| `ls node_modules/electron/dist/electron.exe` | 存在,~150MB | 走手动修法 §3 |
| `./dist/electron.exe --version` | 输出版本号 | binary 不活,重下 |
| `npm run dev`(项目内) | 窗口弹出 | 端口冲突 / IPC 错 |
| `tasklist \| grep electron` | 多个 electron.exe 进程 | 主+渲染+GPU,正常 |

**装好 Electron 后,需要写"自己用"的桌面 UI?见 umbrella `devops/hermes-builtin-tools` §9 写自定义桌面 UI 模板**。
