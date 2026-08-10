#!/usr/bin/env python3
"""老莫进化 - pgvector (RKR) 知识库健康检查（直连 PostgreSQL，无需 token）

基于2026-08-10 R13 验证的快速 pgvector 健康检查脚本。
绕过 RKR API token 过期问题（§10），直接通过 docker exec 进入 postgres。

适用场景:
    - Cron 模式下需要做知识库健康检查
    - RKR v3.0 token 已过期但 docker daemon 仍可用
    - 快速判断 uploaded/failed/completed 队列健康状态

不适用:
    - KNN 检索（需要计算 embedding 向量）
    - SQL 写入（Drizzle migration 仍需走 backend）

用法:
    python3 pgvector-health-check.py [--json]

输出:
    - 文档处理状态分布
    - chunks/vectors 完整性
    - embedding_model 分布
    - 项目文档计数（Top 20）
    - 24h 处理趋势
"""
import subprocess, json, sys, argparse


def psql(query, db="rkr_knowledge"):
    """执行 SQL 查询（-t -A 简化输出）"""
    cmd = ["docker", "exec", "rkr-postgres", "psql", "-U", "rkr_user", "-d", db, "-t", "-A", "-c", query]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def get_postgres_user():
    """从 docker inspect 获取 POSTGRES_USER（兼容 rkr_user/postgres）"""
    try:
        env_out = subprocess.run(
            ["docker", "inspect", "rkr-postgres", "--format", "{{.Config.Env}}"],
            capture_output=True, text=True, timeout=10
        ).stdout
        for line in env_out.split():
            if line.startswith("POSTGRES_USER="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return "rkr_user"


def health_check():
    """主要健康检查"""
    user = get_postgres_user()
    print(f"POSTGRES_USER: {user}\n")

    print("========== 文档处理状态 ==========")
    for line in psql("SELECT processing_status, COUNT(*) FROM documents GROUP BY processing_status ORDER BY COUNT(*) DESC;").split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) == 2:
                print(f"  {parts[0]:20s} {parts[1]}")

    print("\n========== Chunk & Vector 统计 ==========")
    chunks = psql("SELECT COUNT(*) FROM document_chunks;")
    vectors = psql("SELECT COUNT(*) FROM vectors;")
    null_model = psql("SELECT COUNT(*) FROM vectors WHERE embedding_model IS NULL;")
    print(f"  chunks:        {chunks}")
    print(f"  vectors:       {vectors}")
    print(f"  NULL model:    {null_model}")
    try:
        diff = int(chunks) - int(vectors)
        print(f"  diff:          {diff} (≈{diff} chunks 未生成向量)")

        # uploaded 阈值告警（§11）
        uploaded = int(psql("SELECT COUNT(*) FROM documents WHERE processing_status = 'uploaded';"))
        if uploaded > 15000:
            print(f"  ⚠️  WARNING: uploaded={uploaded} 超阈值（>15000）— 需检查 Celery worker")
        elif uploaded > 5000:
            print(f"  ⚠️  CAUTION: uploaded={uploaded} 偏高（>5000）")
        else:
            print(f"  ✅ uploaded={uploaded} 健康")
    except (ValueError, TypeError):
        pass

    print("\n========== embedding_model 分布 ==========")
    for line in psql("SELECT embedding_model, COUNT(*) FROM vectors GROUP BY embedding_model ORDER BY COUNT(*) DESC LIMIT 10;").split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) == 2:
                print(f"  {parts[0]:30s} {parts[1]}")

    print("\n========== 知识库项目（按文档数 Top 20） ==========")
    projects = psql("""
SELECT p.name, COUNT(d.id) as doc_count
FROM projects p LEFT JOIN documents d ON d.project_id = p.id
GROUP BY p.name ORDER BY doc_count DESC LIMIT 20;
""")
    for line in projects.split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) == 2:
                print(f"  {parts[0]:40s} {parts[1]}")

    print("\n========== 最近 24h 处理趋势 ==========")
    for line in psql("""
SELECT DATE_TRUNC('hour', created_at) as hr, processing_status, COUNT(*)
FROM documents WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hr, processing_status ORDER BY hr DESC LIMIT 20;
""").split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) == 3:
                print(f"  {parts[0]:25s} {parts[1]:15s} {parts[2]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式（机器可读）")
    args = parser.parse_args()

    if args.json:
        # TODO: 实现 JSON 输出（按需）
        print("JSON 模式待实现")
    else:
        health_check()
        print("\n========== 完成 ==========")


if __name__ == "__main__":
    main()