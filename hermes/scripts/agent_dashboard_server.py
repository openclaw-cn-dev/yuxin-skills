#!/usr/bin/env python3
"""
渔芯Agent监控面板 V2
- 实时显示5个Agent的工作状态
- 支持HTTP API + 浏览器UI
- 自动刷新
"""
import http.server
import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

PORT = 9118

# Agent配置
AGENTS = ['毛豆', '老莫', '小宝', '黑豆', '阿福', '宽博士', '学习助手']
MEMORY_PATHS = {
    '毛豆': '/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/memory/MEMORY.md',
    '老莫': '/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维/memory/MEMORY.md',
    '小宝': '/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营/memory/MEMORY.md',
    '黑豆': '/Users/hua/Desktop/渔芯科技/4-部门空间/黑豆-行政财务法务/memory/MEMORY.md',
    '阿福': '/Users/hua/Desktop/渔芯科技/4-部门空间/阿福-客服/memory/MEMORY.md',
}
TEAM_DIR = '/Users/hua/Desktop/渔芯科技/团队协作'

# 缓存
_cache = {'data': None, 'timestamp': None}
_cache_lock = threading.Lock()
CACHE_TTL = 30  # 秒


def get_memory_age(path: str) -> tuple:
    """返回 (分钟前, 状态图标, 状态描述)"""
    if not os.path.exists(path):
        return -1, '⚫', '无记录'
    mtime = os.path.getmtime(path)
    age_minutes = (time.time() - mtime) / 60
    if age_minutes < 5:
        return age_minutes, '🟢', '活跃'
    elif age_minutes < 30:
        return age_minutes, '🟡', '正常'
    elif age_minutes < 60:
        return age_minutes, '🟠', '较久'
    else:
        return age_minutes, '🔴', '空闲'


def parse_overseer_report(raw: str) -> dict:
    """解析agent_overseer.py --report的输出"""
    result = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'agents': [],
        'idle_agents': [],
        'busy_agents': [],
        'assigned_tasks': {},  # agent -> task_title
        'pending_count': 0,
        'raw': raw
    }

    lines = raw.split('\n')
    current_idle = []
    current_busy = []

    for line in lines:
        line = line.strip()
        if '空闲Agent' in line:
            # 格式: "空闲Agent（无任务）：无" 或 "空闲Agent（无任务）：黑豆（58分钟）"
            if '无' not in line.split('：')[-1]:
                # 有空闲Agent
                match = re.findall(r'([^（）]+)（(\d+)分钟）', line)
                for name, mins in match:
                    name = name.strip()
                    current_idle.append(name)
                    result['agents'].append({
                        'name': name,
                        'status': 'idle',
                        'minutes_ago': int(mins),
                        'task': ''
                    })
                    result['idle_agents'].append(name)

        elif '有任务进行中' in line:
            # 格式: "有任务进行中：毛豆→任务A, 老莫→任务B, 小宝→任务C"
            # 可能多组以", "分隔，需分别处理
            if '无' not in line.split('：')[-1]:
                part = line.split('：')[-1].strip()
                # 用"→"分割所有任务段，name是每个段中→左边的部分
                # 格式: "毛豆→【任务A】, 老莫→【任务B】, 小宝→【任务C】"
                # 注意：中文逗号"，"和英文逗号","都可能作为分隔符
                raw_line = line.split('：', 1)[-1].strip()
                # 匹配"名字→"后贪婪取所有内容直到遇到下一个"名字→"或字符串结尾
                pattern = r'([\w\u4e00-\u9fff]{2,4})→(.+?)(?=, [\w\u4e00-\u9fff]{2,4}→|$)'
                matches = re.findall(pattern, raw_line, re.DOTALL)
                for name, task in matches:
                    if name and task.strip():
                        current_busy.append(name)
                        result['agents'].append({
                            'name': name,
                            'status': 'busy',
                            'minutes_ago': 0,
                            'task': task.strip()
                        })
                        result['busy_agents'].append(name)
                        result['assigned_tasks'][name] = task.strip()

        elif '待处理任务' in line:
            try:
                nums = re.findall(r'(\d+)个', line)
                if nums:
                    result['pending_count'] = int(nums[0])
            except:
                pass

    # 为未出现的agent补充"未分配"状态
    assigned_names = {a['name'] for a in result['agents']}
    for agent in AGENTS:
        if agent not in assigned_names:
            result['agents'].append({
                'name': agent,
                'status': 'unassigned',
                'minutes_ago': -1,
                'task': '待分配'
            })

    return result


def fetch_status() -> dict:
    """获取最新状态（带缓存）"""
    global _cache
    now = time.time()

    with _cache_lock:
        if _cache['data'] and _cache['timestamp'] and (now - _cache['timestamp']) < CACHE_TTL:
            return _cache['data']

    try:
        result = subprocess.run(
            ['python3', 'agent_overseer.py', '--report'],
            capture_output=True, text=True, timeout=30,
            cwd=TEAM_DIR
        )
        raw = result.stdout.strip()
        data = parse_overseer_report(raw)

        # 补充memory年龄
        for agent_data in data['agents']:
            name = agent_data['name']
            path = MEMORY_PATHS.get(name)
            if path:
                age, icon, desc = get_memory_age(path)
                agent_data['memory_minutes'] = int(age) if age >= 0 else -1
                agent_data['memory_icon'] = icon
                agent_data['memory_desc'] = desc

        with _cache_lock:
            _cache['data'] = data
            _cache['timestamp'] = now

        return data
    except Exception as e:
        return {'error': str(e), 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


HTML = '''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>渔芯 Agent 监控面板 V2</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0e14; color: #e6e6e6; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 24px; }

/* Header */
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #1e2a38; }
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 28px; }
h1 { font-size: 22px; font-weight: 700; background: linear-gradient(135deg, #00d4aa, #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header-right { display: flex; align-items: center; gap: 16px; }
.live-dot { width: 8px; height: 8px; background: #00d4aa; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
.last-update { font-size: 12px; color: #5c7089; }
.btn-refresh { background: #1a2535; color: #e6e6e6; border: 1px solid #2d3d52; padding: 8px 18px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
.btn-refresh:hover { background: #243044; border-color: #3d5a80; }
.btn-refresh.loading { opacity: 0.6; pointer-events: none; }

/* Stats */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.stat { background: #111827; border: 1px solid #1e2a38; border-radius: 14px; padding: 20px; text-align: center; transition: transform 0.2s; }
.stat:hover { transform: translateY(-2px); }
.stat-num { font-size: 38px; font-weight: 800; line-height: 1; }
.stat-label { font-size: 12px; color: #5c7089; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.stat.green .stat-num { color: #00d4aa; }
.stat.blue .stat-num { color: #0ea5e9; }
.stat.orange .stat-num { color: #f59e0b; }
.stat.red .stat-num { color: #ef4444; }

/* Agent Grid */
.section-title { font-size: 14px; color: #5c7089; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px; }
.agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin-bottom: 28px; }
.agent-card { background: #111827; border: 1px solid #1e2a38; border-radius: 14px; padding: 18px; transition: all 0.2s; position: relative; overflow: hidden; }
.agent-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.agent-card.busy::before { background: linear-gradient(90deg, #00d4aa, #0ea5e9); }
.agent-card.idle::before { background: #ef4444; }
.agent-card.unassigned::before { background: #f59e0b; }
.agent-card:hover { border-color: #2d4a6a; transform: translateY(-2px); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.agent-name { font-size: 16px; font-weight: 700; }
.agent-badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; font-weight: 600; }
.badge-busy { background: #00d4aa20; color: #00d4aa; }
.badge-idle { background: #ef444420; color: #ef4444; }
.badge-unassigned { background: #f59e0b20; color: #f59e0b; }
.badge-new { background: #0ea5e920; color: #0ea5e9; }

.agent-task { font-size: 13px; color: #8ba3be; line-height: 1.4; margin-bottom: 10px; min-height: 36px; word-break: break-all; }
.agent-meta { display: flex; gap: 12px; font-size: 11px; color: #5c7089; }
.meta-item { display: flex; align-items: center; gap: 4px; }

/* Progress bar */
.progress-wrap { margin-top: 10px; }
.progress-label { display: flex; justify-content: space-between; font-size: 11px; color: #5c7089; margin-bottom: 4px; }
.progress-bar { height: 4px; background: #1e2a38; border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
.fill-green { background: linear-gradient(90deg, #00d4aa, #0ea5e9); }
.fill-red { background: #ef4444; }
.fill-orange { background: #f59e0b; }

/* Timeline */
.timeline { background: #111827; border: 1px solid #1e2a38; border-radius: 14px; padding: 20px; }
.timeline-item { display: flex; gap: 14px; padding: 10px 0; border-bottom: 1px solid #1a2535; }
.timeline-item:last-child { border-bottom: none; }
.tl-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
.tl-busy { background: #00d4aa; box-shadow: 0 0 8px #00d4aa80; }
.tl-idle { background: #ef4444; }
.tl-content { flex: 1; }
.tl-agent { font-weight: 600; font-size: 14px; }
.tl-task { font-size: 13px; color: #8ba3be; margin-top: 2px; }

/* Loading */
.loading { display: flex; align-items: center; justify-content: center; padding: 60px; color: #5c7089; gap: 10px; }
.spinner { width: 20px; height: 20px; border: 2px solid #1e2a38; border-top-color: #0ea5e9; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-msg { background: #2d1a1a; border: 1px solid #ef444440; border-radius: 12px; padding: 16px; color: #ef4444; }

/* Footer */
footer { margin-top: 32px; padding-top: 20px; border-top: 1px solid #1e2a38; text-align: center; font-size: 12px; color: #3d5066; }
footer a { color: #0ea5e9; text-decoration: none; }
</style>
</head>
<body>
<div class="container">
<header>
<div class="logo">
<span class="logo-icon">🖥️</span>
<h1>渔芯 Agent 监控面板</h1>
</div>
<div class="header-right">
<div class="live-dot"></div>
<span class="last-update" id="lastUpdate">加载中...</span>
<button class="btn-refresh" id="refreshBtn" onclick="loadData()">🔄 刷新</button>
</div>
</header>

<div id="content"><div class="loading"><div class="spinner"></div>加载中...</div></div>

<footer>
Hermes Agent 监控系统 | 渔芯科技 | <span id="renderTime">-</span>
</footer>
</div>

<script>
let loading = false;
async function loadData() {
    if (loading) return;
    loading = true;
    const btn = document.getElementById('refreshBtn');
    btn.classList.add('loading');
    btn.textContent = '🔄 刷新中...';
    
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loading"><div class="spinner"></div>检查中...</div>';
    
    try {
        const t0 = performance.now();
        const resp = await fetch('/api/status');
        const data = await resp.json();
        const renderMs = Math.round(performance.now() - t0);
        document.getElementById('renderTime').textContent = '渲染 ' + renderMs + 'ms';
        render(data);
        document.getElementById('lastUpdate').textContent = data.timestamp;
    } catch(e) {
        content.innerHTML = '<div class="error-msg">❌ 加载失败: ' + e.message + '</div>';
    } finally {
        loading = false;
        btn.classList.remove('loading');
        btn.textContent = '🔄 刷新';
    }
}

function render(data) {
    if (data.error) {
        document.getElementById('content').innerHTML = '<div class="error-msg">❌ ' + data.error + '</div>';
        return;
    }

    const agents = data.agents || [];
    const busyCount = agents.filter(a => a.status === 'busy').length;
    const idleCount = agents.filter(a => a.status === 'idle').length;
    const unassignedCount = agents.filter(a => a.status === 'unassigned').length;

    let html = `
<!-- Stats -->
<div class="stats">
<div class="stat green"><div class="stat-num">${busyCount}</div><div class="stat-label">🟢 进行中</div></div>
<div class="stat red"><div class="stat-num">${idleCount}</div><div class="stat-label">🔴 空闲</div></div>
<div class="stat orange"><div class="stat-num">${unassignedCount}</div><div class="stat-label">🟡 待分配</div></div>
<div class="stat blue"><div class="stat-num">${data.pending_count}</div><div class="stat-label">📋 待处理</div></div>
</div>

<!-- Agent Cards -->
<div class="section-title">▸ Agent 状态</div>
<div class="agent-grid">`;

    for (const a of agents) {
        const statusClass = a.status;
        const badgeClass = a.status === 'busy' ? 'badge-busy' : (a.status === 'idle' ? 'badge-idle' : 'badge-unassigned');
        const statusText = a.status === 'busy' ? '进行中' : (a.status === 'idle' ? '空闲' : '待分配');
        
        // Memory状态颜色
        let memIcon = a.memory_icon || '⚫';
        let memDesc = a.memory_desc || '-';
        let progressClass = 'fill-green';
        let progressPct = 100;
        
        if (a.status === 'busy') {
            progressClass = 'fill-green';
            progressPct = 70;
        } else if (a.status === 'idle') {
            progressClass = 'fill-red';
            progressPct = 10;
        } else {
            progressClass = 'fill-orange';
            progressPct = 30;
        }

        html += `
<div class="agent-card ${statusClass}">
<div class="card-header">
<span class="agent-name">${a.name}</span>
<span class="agent-badge ${badgeClass}">${statusText}</span>
</div>
<div class="agent-task">${a.task || '无任务'}</div>
<div class="agent-meta">
<span class="meta-item">${memIcon} ${memDesc}</span>
</div>
<div class="progress-wrap">
<div class="progress-label">
<span>活跃度</span>
<span>${a.status === 'busy' ? '工作中' : (a.status === 'idle' ? '待任务' : '空闲')}</span>
</div>
<div class="progress-bar">
<div class="progress-fill ${progressClass}" style="width:${progressPct}%"></div>
</div>
</div>
</div>`;
    }

    html += '</div>';

    // Assigned tasks timeline
    const assigned = data.assigned_tasks || {};
    const assignedEntries = Object.entries(assigned);
    if (assignedEntries.length > 0) {
        html += `
<div class="section-title">▸ 已分配任务</div>
<div class="timeline">`;
        for (const [agent, task] of assignedEntries) {
            const agentData = agents.find(a => a.name === agent);
            const dotClass = (agentData && agentData.status === 'busy') ? 'tl-busy' : 'tl-idle';
            html += `
<div class="timeline-item">
<div class="tl-dot ${dotClass}"></div>
<div class="tl-content">
<div class="tl-agent">${agent}</div>
<div class="tl-task">${task}</div>
</div>
</div>`;
        }
        html += '</div>';
    }

    document.getElementById('content').innerHTML = html;
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>'''


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/status':
            data = fetch_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass  # 静默日志


def run():
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'✅ Agent监控面板启动: http://localhost:{PORT}')
    print(f'   局域网访问: http://{get_local_ip()}:{PORT}')
    server.serve_forever()


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'


if __name__ == '__main__':
    run()
