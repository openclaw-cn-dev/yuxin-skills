#!/usr/bin/env python3
"""
Quick Serve — 智能检测项目类型并启动本地服务器
用法: python3 quick_serve.py [port]

自动检测:
  - Vite/React/Vue/Svelte → npm run dev
  - 静态 HTML → python3 http.server
  - FastAPI/Flask → python3 server/app.py
  - dist/ 目录 → 优先 serve dist/
"""
import os, sys, subprocess, json
from pathlib import Path

CWD = Path.cwd()
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

print(f"🔍 检测项目: {CWD.name}")

# 1. Vite/React/Vue/Svelte
if (CWD / "vite.config.js").exists() or (CWD / "vite.config.ts").exists():
    print(f"📦 Vite 项目 → npm run dev -- --port {PORT}")
    subprocess.run(["npm", "run", "dev", "--", "--port", str(PORT), "--host"], check=False)
    sys.exit(0)

# 2. package.json with dev script
pkg_json = CWD / "package.json"
if pkg_json.exists():
    try:
        pkg = json.loads(pkg_json.read_text())
        if "dev" in pkg.get("scripts", {}):
            print(f"📦 npm run dev → port {PORT}")
            subprocess.run(["npm", "run", "dev"], check=False)
            sys.exit(0)
        if "start" in pkg.get("scripts", {}):
            print(f"📦 npm start → port {PORT}")
            subprocess.run(["npm", "start"], check=False)
            sys.exit(0)
        if "preview" in pkg.get("scripts", {}):
            print(f"📦 npm run preview (Vite build)")
            subprocess.run(["npm", "run", "preview", "--", "--port", str(PORT)], check=False)
            sys.exit(0)
    except Exception:
        pass

# 3. FastAPI/Flask (backend/app/main.py pattern)
for pattern in ["backend/app/main.py", "app/main.py", "main.py", "server.py"]:
    server_py = CWD / pattern
    if server_py.exists():
        print(f"🐍 FastAPI → uvicorn {server_py}")
        subprocess.run([sys.executable, "-m", "uvicorn", 
                       f"{'.'.join(pattern.replace('/', '.').replace('.py','').split('.'))}:app",
                       "--host", "0.0.0.0", "--port", str(PORT)], check=False)
        sys.exit(0)

# 3b. Standalone Python web server (voice_center.py pattern)
for py_file in sorted(CWD.glob("*.py")):
    if py_file.name.startswith("_") or py_file.name == "quick_serve.py":
        continue
    content = py_file.read_text()
    if ("uvicorn" in content or "FastAPI" in content or "Flask" in content) and \
       ("HTMLResponse" in content or "HTML_FILE" in content or "send_file" in content or "static" in content):
        print(f"🐍 Python Web → python3 {py_file.name} --port {PORT}")
        subprocess.run([sys.executable, str(py_file), "--port", str(PORT)], check=False)
        sys.exit(0)

# 4. dist/ directory (built frontend)
dist_dir = CWD / "dist"
serve_dir = dist_dir if dist_dir.exists() else CWD
print(f"🌐 静态文件服务 → http://localhost:{PORT}")
print(f"   目录: {serve_dir}")
print(f"   按 Ctrl+C 停止")

import http.server
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(serve_dir), **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"\n✨ 打开: http://localhost:{PORT}\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")
