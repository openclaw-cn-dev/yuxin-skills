#!/usr/bin/env python3
"""玉芬公司整体情况每小时巡检 — 整合所有子系统状态"""
import subprocess, json, sys, os, http.client
from datetime import datetime
from urllib.parse import urlparse

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT ({timeout}s)"
    except Exception as e:
        return -2, "", str(e)

def check_http(url, timeout=8):
    try:
        parsed = urlparse(url)
        conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=timeout)
        conn.request('GET', parsed.path)
        resp = conn.getresponse()
        body = resp.read().decode()
        conn.close()
        return resp.status, body[:200]
    except Exception as e:
        return 0, str(e)[:200]

def check_docker_container(name):
    rc, out, err = run(f"docker ps --filter name={name} --format '{{{{.Status}}}}'", timeout=8)
    if rc != 0 or not out:
        return "OFFLINE", err or "未找到"
    status = out
    if "unhealthy" in status: return "UNHEALTHY", status
    if "healthy" in status: return "HEALTHY", status
    if "starting" in status: return "STARTING", status
    return "UNKNOWN", status

def check_gateway():
    """检查所有同事 gateway 状态"""
    colleagues = ["maodou", "laomo", "xiaobao", "heidou", "afu", "quant", "zhenglishi"]
    results = {}
    for p in colleagues:
        # 查 launchd
        rc, out, _ = run(f"launchctl list 2>/dev/null | awk -v lbl='ai.hermes.gateway-{p}' '$3==lbl {{print $1}}'", timeout=5)
        if out:
            results[p] = f"launchd PID={out}"
        else:
            # 查手动进程
            rc2, out2, _ = run(f"ps aux | grep 'hermes.*gateway.*{p}' | grep -v grep | awk '{{print $2}}'", timeout=5)
            if out2:
                results[p] = f"manual PID={out2}"
            else:
                results[p] = "OFFLINE"
    return results

def check_rkr_docs():
    """RKR 文档统计 - 用 docker cp 避免 shell 引号问题"""
    script_path = "/tmp/rkr_doc_stats.py"
    script_content = '''#!/usr/bin/env python3
import asyncio, asyncpg, json
async def q():
    conn = await asyncpg.connect(
        host='postgres', port=5432,
        user='rkr_user', password='rkr_dev_2026',
        database='rkr_knowledge'
    )
    total = await conn.fetchval('SELECT COUNT(*) FROM documents')
    completed = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE processing_status='completed'")
    failed = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE processing_status='failed'")
    pending = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE processing_status='uploaded'")
    await conn.close()
    print(json.dumps({'total':total,'completed':completed,'failed':failed,'pending':pending}))
asyncio.run(q())
'''
    with open(script_path, 'w') as f:
        f.write(script_content)
    rc, out, err = run(
        f"docker cp {script_path} rkr-backend:/tmp/rkr_doc_stats.py && "
        f"docker exec rkr-backend python3 /tmp/rkr_doc_stats.py",
        timeout=15
    )
    if rc == 0 and out:
        try: return json.loads(out)
        except: return {"error": out[:100]}
    return {"error": err[:100] if err else "NO_DATA"}

def check_cron_health():
    """检查 cron 任务健康状况"""
    rc, out, _ = run("hermes cron list 2>/dev/null", timeout=10)
    if rc != 0:
        return {"failed": 0, "paused": 0, "total": 0}
    lines = out.split('\n')
    # Each job starts with a UUID-like line
    total = sum(1 for l in lines if len(l.strip()) > 20 and l.strip()[0].isalnum() and '[' in l)
    # Count "error" in last_run lines
    failed = sum(1 for l in lines if 'last_run' in l.lower() and 'error' in l.lower())
    # Count paused
    paused = sum(1 for l in lines if 'paused' in l.lower() and 'true' in l.lower())
    return {"failed": failed, "paused": paused, "total": total}

def check_self_evolution():
    """检查自进化状态"""
    rc, out, _ = run("cat ~/.hermes/state/yva-self-evolution.json 2>/dev/null || echo '{}'", timeout=5)
    try: return json.loads(out) if out else {}
    except: return {}

def format_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🏢 渔芯科技整体巡检 ({now})", ""]

    # 1. 基础设施
    lines.append("=== 基础设施 ===")
    fe_con, fe_detail = check_docker_container("research-backend")
    rkr_con, rkr_detail = check_docker_container("rkr-backend")
    pg_con, pg_detail = check_docker_container("rkr-postgres")
    lines.append(f"  FindEra: {fe_con}")
    lines.append(f"  RKR: {rkr_con}")
    lines.append(f"  Postgres: {pg_con}")

    # API 检查
    fe_api, _ = check_http("http://localhost:8003/api/v1/health")
    rkr_api, _ = check_http("http://localhost:8000/api/v1/health")
    lines.append(f"  FindEra API: {'✅' if fe_api==200 else '❌'} (HTTP {fe_api})")
    lines.append(f"  RKR API: {'✅' if rkr_api==200 else '❌'} (HTTP {rkr_api})")
    lines.append("")

    # 2. 同事 Gateway 状态
    lines.append("=== 同事 Gateway ===")
    gw = check_gateway()
    all_gw_ok = True
    for name, status in gw.items():
        icon = "✅" if "PID=" in status else "❌"
        if "OFFLINE" in status: all_gw_ok = False
        lines.append(f"  {icon} {name}: {status}")
    if all_gw_ok:
        lines.append("  ✅ 所有 Gateway 运行正常")
    lines.append("")

    # 3. RKR 文档统计
    lines.append("=== RKR 知识库 ===")
    docs = check_rkr_docs()
    if 'total' in docs:
        lines.append(f"  文档: 总计 {docs['total']} | ✅ 已完成 {docs['completed']} | ⏳ 待处理 {docs['pending']} | ❌ 失败 {docs['failed']}")
        if docs['failed'] > 0:
            lines.append(f"  ⚠️ 有 {docs['failed']} 条失败文档需要关注")
    else:
        lines.append(f"  文档统计: {docs.get('error', '未知')}")
    lines.append("")

    # 4. Cron 健康
    lines.append("=== Cron 任务 ===")
    cron = check_cron_health()
    lines.append(f"  总任务: {cron['total']} | 失败: {cron['failed']} | 暂停: {cron['paused']}")
    lines.append("")

    # 5. 自进化状态
    lines.append("=== 自进化 ===")
    evo = check_self_evolution()
    if evo.get('rkr_pending') is not None:
        lines.append(f"  玉芬自进化: 运行中 (RKR积压={evo.get('rkr_pending')}, 失败={evo.get('rkr_failed')})")
    else:
        lines.append(f"  玉芬自进化: 状态文件未找到")
    lines.append("")

    # 6. 总体状态
    all_ok = True
    issues = []
    if fe_con != "HEALTHY": issues.append(f"FindEra 容器: {fe_con}")
    if rkr_con != "HEALTHY": issues.append(f"RKR 容器: {rkr_con}")
    if fe_api != 200: issues.append(f"FindEra API 异常")
    if rkr_api != 200: issues.append(f"RKR API 异常")
    if not all_gw_ok:
        offline = [n for n,s in gw.items() if "OFFLINE" in s]
        issues.append(f"Gateway 离线: {', '.join(offline)}")
    if docs.get('failed', 0) > 100:
        issues.append(f"RKR 失败文档过多: {docs['failed']}")

    if issues:
        lines.append("🔴 需关注的问题:")
        for i in issues:
            lines.append(f"  - {i}")
    else:
        lines.append("✅ 所有系统运行正常")

    return "\n".join(lines)

if __name__ == "__main__":
    print(format_report())
