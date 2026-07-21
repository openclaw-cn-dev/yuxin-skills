#!/usr/bin/env python3
"""寻元 + RKR 知识库运行状态监控（每小时执行一次）"""
import subprocess, json, sys, os
from datetime import datetime

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT ({timeout}s)"
    except Exception as e:
        return -2, "", str(e)

def check_docker_container(name):
    rc, out, err = run(f"docker ps --filter name={name} --format '{{{{.Status}}}}'", timeout=8)
    if rc != 0 or not out:
        return "OFFLINE", f"docker ps 失败: {err or '未找到容器'}"
    status = out
    if "unhealthy" in status:
        return "UNHEALTHY", status
    if "healthy" in status:
        return "HEALTHY", status
    if "starting" in status:
        return "STARTING", status
    return "UNKNOWN", status

def check_http(url, timeout=8):
    """Check HTTP status code using http.client (urllib has proxy issues)"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        import http.client
        conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=timeout)
        conn.request('GET', parsed.path)
        resp = conn.getresponse()
        body = resp.read().decode()
        conn.close()
        return resp.status, body[:200]
    except Exception as e:
        return 0, str(e)[:200]

def check_findera():
    results = {}
    status, detail = check_docker_container("research-backend")
    results["container"] = {"status": status, "detail": detail}

    code, body = check_http("http://localhost:8003/api/v1/health")
    results["api"] = {"status_code": code, "body": body[:100]}

    rc, out, _ = run("lsof -i :8003 2>/dev/null | grep LISTEN", timeout=5)
    results["port"] = "LISTENING" if out else "NOT_LISTENING"

    return results

def check_rkr():
    results = {}
    status, detail = check_docker_container("rkr-backend")
    results["container"] = {"status": status, "detail": detail}

    code, body = check_http("http://localhost:8000/api/v1/health")
    results["api"] = {"status_code": code, "body": body[:100]}

    pg_status, pg_detail = check_docker_container("rkr-postgres")
    results["postgres"] = {"status": pg_status, "detail": pg_detail}

    # 文档统计 - 用写文件方式避免 shell 引号问题
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
    
    rc, out, err = run(f"docker cp {script_path} rkr-backend:/tmp/rkr_doc_stats.py && docker exec rkr-backend python3 /tmp/rkr_doc_stats.py", timeout=15)
    
    if rc == 0 and out:
        try:
            results["documents"] = json.loads(out)
        except:
            results["documents"] = {"error": out[:100]}
    else:
        results["documents"] = {"error": err[:100] if err else "NO_DATA"}

    return results

def format_report(fe_status, rkr_status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📊 系统状态巡检 ({now})", ""]

    # FindEra
    lines.append("【寻元 FindEra】")
    f = fe_status
    lines.append(f"  容器: {f['container']['status']}")
    lines.append(f"  端口: {f['port']}")
    if f['api']['status_code'] == 200:
        lines.append(f"  API: ✅ 正常 (HTTP 200)")
    else:
        lines.append(f"  API: ⚠️ HTTP {f['api']['status_code']} - {f['api']['body'][:60]}")
    lines.append("")

    # RKR
    lines.append("【RKR 知识库】")
    r = rkr_status
    lines.append(f"  容器: {r['container']['status']}")
    lines.append(f"  Postgres: {r['postgres']['status']}")
    if r['api']['status_code'] == 200:
        lines.append(f"  API: ✅ 正常 (HTTP 200)")
    else:
        lines.append(f"  API: ⚠️ HTTP {r['api']['status_code']} - {r['api']['body'][:60]}")

    docs = r.get('documents', {})
    if 'total' in docs:
        lines.append(f"  文档: 总计 {docs['total']} | ✅ 已完成 {docs['completed']} | ⏳ 待处理 {docs['pending']} | ❌ 失败 {docs['failed']}")
    elif 'error' in docs:
        lines.append(f"  文档统计: {docs['error']}")

    # 总体状态
    all_ok = True
    for svc, name in [(fe_status, "寻元"), (rkr_status, "RKR")]:
        if svc['container']['status'] not in ("HEALTHY",):
            all_ok = False
            lines.append(f"\n  ⚠️ {name} 容器状态异常: {svc['container']['detail']}")
        if svc['api']['status_code'] != 200:
            all_ok = False

    if all_ok:
        lines.append(f"\n✅ 所有服务运行正常")
    else:
        lines.append(f"\n🔴 部分服务异常，请关注")

    return "\n".join(lines)

if __name__ == "__main__":
    print("=== 寻元 + RKR 状态巡检 ===")
    fe = check_findera()
    rkr = check_rkr()
    report = format_report(fe, rkr)
    print(report)
    print("\n=== 巡检完成 ===")
