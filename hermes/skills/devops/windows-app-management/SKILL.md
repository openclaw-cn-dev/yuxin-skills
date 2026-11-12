---
name: windows-app-management
description: Windows 软件与应用管理 — 装/卸桌面软件、移动应用套壳识别（腾讯应用宝/移动应用引擎安卓模拟层）、卸载程序卡死诊断、注册表卸载入口清理、"删移动应用装电脑版"类任务的标准姿势。触发条件：华哥要求安装/删除/清理 Windows 应用、卸载卡死、找不到应用真实安装位置。
trigger: Windows 应用安装/卸载/清理、卸载程序无响应卡死、"删除XX应用装电脑版"、应用列表里有可疑的移动应用
---

# Windows 软件与应用管理

> 渔芯 Windows 主机（2026-11 迁移机）上的应用管理经验。核心教训：**华哥说的"移动应用"往往不是普通 Windows 程序，而是装在安卓模拟引擎里的安卓应用**——直接按普通程序卸载会失败或卡死。

## 第一步：识别"移动应用"的真实载体（勿直接当普通程序卸）

华哥指令形如「小红书、抖音、快手删除，装电脑版」时，**先查是不是安卓套壳**：

1. `Get-AppxPackage` 查 UWP 商店应用（本机 61 个包，无四件套 → 不是 UWP）
2. `tasklist | grep -iE "<应用名特征|助手|store>"` 查常驻进程
3. 注册表卸载入口扫描（中文 key 直接 python winreg 读，PowerShell 输出中文会乱码）：
```python
import winreg
for root, path in [(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                   (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")]:
    # 遍历子键读 DisplayName / UninstallString / Publisher
```

**本机事实（2026-11-11）**：小红书/抖音/抖音精选/快手（另有飞书/QQ 安卓版）装在**腾讯移动应用引擎 Tencent Androws**（`D:\Program Files\Tencent\Androws\`）——安卓模拟层，非 Windows 程序。

## 腾讯 Androws 应用卸载：VM 必须能开机

详见 `references/tencent-androws-app-removal.md`。要点：

- 官方卸载 CLI：`Androws\Application\Uninstall.exe --uninstall-app <安卓包名>`（如 `com.xingin.xhs`）
- **该命令要连安卓 VM 才能执行；VM 起不来就无限挂起**（无窗口、无输出、120s 超时）。卡死实例用 `taskkill //F //IM Uninstall.exe` 清理
- VM 启动失败诊断：`Androws\Application\5.10.*\logs\Androws.log` 里 `boot step error` + `OnVmBootError`
- 错误码 **111303 = ABoxSVC / ABoxHeadless 虚拟化服务不存在**；`sc create ABoxSVC binPath=... ` 补注册后 `sc start` 若报 **1053（服务未及时响应）= 驱动 ABoxSup.sys 未安装**，服务层修复不完整
- adb 通道不可用兜底：引擎 VM 不开机时 `adb devices` 恒为空，`adb connect 127.0.0.1:5555` 等全部失败

## 决策分支：修引擎 vs 连锅端（给华哥的 A/B/C 格式）

引擎 VM 损坏且应用都有官方 PC 版时，给三选项回单字母拍板：

- **A 修引擎正规卸载**：修 ABox 驱动到 VM 开机 → adb `pm uninstall`。干净但驱动损坏原因不明，可能要重装引擎
- **B 连锅端**（引擎只为这几个应用存在且已残废时推荐）：卸载整个引擎（注册表 Uninstall 入口 `--oem-uninstall=0 --uninstall-entry=1` + 安装目录 + data.vhd 11.6GB 安卓数据一并释放），再装官方电脑版
- **C 只删注册表伪装卸载**（不推荐）：安卓数据留着占 10GB+，引擎仍是坏的

**汇报必须含**：引擎里全部安卓应用清单（华哥可能不知道飞书/QQ 也在里面，别擅自动没点名的）+ VM 损坏证据（日志错误码原文）+ 各选项风险。

## 通用纪律

- 卸载/清注册表前先扫快照（备份注册表导出或记录包名清单），硬删除无 undo
- PowerShell 中文输出乱码时改用 python `winreg` 直读
- `cmd //c start "" <exe>` 启动 GUI 程序不阻塞会话；等进程起来后单独验证（tasklist + 日志），不要在同一命令里长 sleep 死等
