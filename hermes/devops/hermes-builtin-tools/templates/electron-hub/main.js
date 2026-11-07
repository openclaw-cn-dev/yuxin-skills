// main.js — Electron 主进程(可复用模板)
// 改 4 处即可用:[HERMES_PORT] [DEFAULT_MODEL] [API_KEY_ENV] [窗口标题]
// 完整 5 步 SOP 见 SKILL.md §9

const { app, BrowserWindow, Tray, Menu, ipcMain, shell, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let tray = null;
let win = null;
let hermesProc = null;

// === 改这里 ===
const HERMES_PORT = 9119;
const HERMES_URL = `http://127.0.0.1:${HERMES_PORT}`;
const DEFAULT_MODEL = 'MiniMax-M3';
const API_KEY_ENV = 'MINIMAX_API_KEY';
const WINDOW_TITLE = 'Hermes 桌面';
// === 改完 ===

// 自动起 dashboard(先 ping,避免 9119 端口冲突)
async function ensureDashboard() {
  try {
    const r = await fetch(`${HERMES_URL}/`);
    if (r.ok) {
      console.log('[hermes] 复用已在跑的 dashboard');
      return;
    }
  } catch {}
  console.log('[hermes] 没检测到 dashboard,启动子进程');
  const apiKey = process.env[API_KEY_ENV] || '';
  hermesProc = spawn('hermes', ['dashboard', '--skip-build', '--host', '127.0.0.1', '--port', String(HERMES_PORT)], {
    env: { ...process.env, [API_KEY_ENV]: apiKey },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true
  });
  hermesProc.stdout.on('data', d => console.log('[hermes]', d.toString().trim()));
  hermesProc.stderr.on('data', d => console.error('[hermes:err]', d.toString().trim()));
  hermesProc.on('exit', code => console.log(`[hermes] 退出 code=${code}`));
}

function createWindow() {
  win = new BrowserWindow({
    width: 1200, height: 800, minWidth: 900, minHeight: 600,
    title: WINDOW_TITLE,
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  win.loadFile('index.html');
  // 关窗不退出 → 缩托盘
  win.on('close', e => {
    if (!app.isQuiting) { e.preventDefault(); win.hide(); }
  });
}

function createTray() {
  tray = new Tray(nativeImage.createEmpty());
  const menu = Menu.buildFromTemplate([
    { label: '📂 显示主窗口', click: () => win.show() },
    { label: '🌐 打开 Hermes Dashboard', click: () => shell.openExternal(HERMES_URL) },
    { type: 'separator' },
    { label: '🔄 重启 Hermes', click: () => {
        if (hermesProc) hermesProc.kill();
        setTimeout(ensureDashboard, 1000);
      }},
    { type: 'separator' },
    { label: '❌ 退出', click: () => {
        app.isQuiting = true;
        if (hermesProc) hermesProc.kill();
        app.quit();
      }}
  ]);
  tray.setToolTip(WINDOW_TITLE);
  tray.setContextMenu(menu);
  tray.on('double-click', () => win.show());
}

app.whenReady().then(async () => {
  await ensureDashboard();
  setTimeout(() => { createWindow(); createTray(); }, 3000);
});

app.on('window-all-closed', e => e.preventDefault());

// IPC:OpenAI 兼容协议 → 走 /v1/chat/completions
ipcMain.handle('chat', async (_, { messages, model }) => {
  const resp = await fetch(`${HERMES_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env[API_KEY_ENV] || ''}`
    },
    body: JSON.stringify({
      model: model || DEFAULT_MODEL,
      messages,
      stream: false
    })
  });
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`HTTP ${resp.status}: ${err}`);
  }
  return await resp.json();
});

ipcMain.handle('get-config', () => ({
  model: DEFAULT_MODEL,
  hermesUrl: HERMES_URL
}));
