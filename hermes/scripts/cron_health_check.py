#!/usr/bin/env python3
"""
Cron任务健康检查脚本
用法:
  python3 cron_health_check.py              # 检查+打印摘要
  python3 cron_health_check.py --json       # JSON格式输出（供脚本消费）
"""
import json
import sys
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
JOBS_JSON = HERMES_HOME / "cron/jobs.json"


def check_cron_health():
    """检查cron任务健康状态 - 从jobs.json读取"""
    if not JOBS_JSON.exists():
        return {"status": "error", "message": "jobs.json不存在"}
    
    with open(JOBS_JSON) as f:
        data = json.load(f)
    
    jobs = data.get("jobs", [])
    
    # 分类统计
    failed = [j for j in jobs if j.get("last_status") == "failed"]
    paused = [j for j in jobs if not j.get("enabled", True)]
    ok = [j for j in jobs if j.get("last_status") == "ok"]
    
    return {
        "total": len(jobs),
        "ok": len(ok),
        "failed_count": len(failed),
        "paused_count": len(paused),
        "failed_jobs": [
            {
                "job_id": j.get("id", ""),
                "name": j.get("name", ""),
                "status": j.get("last_status"),
                "error": j.get("last_error"),
                "last_run": j.get("last_run_at"),
                "next_run": j.get("next_run_at"),
                "prompt": (j.get("prompt") or "")[:150],
            }
            for j in failed
        ],
        "paused_jobs": [
            {"job_id": j.get("id", ""), "name": j.get("name", ""), "reason": j.get("paused_reason")}
            for j in paused
        ],
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cron健康检查")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")
    args = parser.parse_args()
    
    result = check_cron_health()
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # 人类可读输出
    print("=== Cron健康检查 ===")
    print(f"总计: {result['total']} | 正常: {result['ok']} | 失败: {result['failed_count']} | 暂停: {result['paused_count']}")
    
    if result['failed_jobs']:
        print(f"\n⚠️ 失败任务 ({result['failed_count']}个):")
        for j in result['failed_jobs']:
            error_msg = (j['error'] or "unknown")[:80]
            print(f"  • {j['name']} [{j['job_id'][:8]}]")
            print(f"    错误: {error_msg}")
            print(f"    上次运行: {j['last_run']}")
            # 安全扫描拦截提示
            if 'exfil_curl_data' in (j['error'] or ''):
                print(f"    🔧 修复: prompt含敏感模式 → 抽取为script字段")
    
    if result['paused_jobs']:
        print(f"\n⏸️ 暂停任务 ({result['paused_count']}个):")
        for j in result['paused_jobs']:
            print(f"  • {j['name']} [{j['job_id'][:8]}]: {j['reason'] or '手动暂停'}")
    
    if not result['failed_jobs'] and not result['paused_jobs']:
        print("\n✅ 所有Cron任务正常运行")


if __name__ == "__main__":
    main()
