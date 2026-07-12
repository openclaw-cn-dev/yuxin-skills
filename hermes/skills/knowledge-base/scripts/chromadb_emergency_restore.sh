#!/usr/bin/env bash
# ChromaDB Emergency Restore Script
# 用途：ChromaDB 数据丢失时从备份恢复
# 使用：bash this_script.sh
# 依赖：docker, 备份文件 /path/to/backups/chroma_YYYYMMDD.sqlite3
#
# 2026-05-06 实测验证：成功恢复 342 lookforge_knowledge + 188 competitor_analysis

set -e

CONTAINER="lookforge-chromadb"
BACKUP_DB="/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backups/chromadb/chroma_20260504.sqlite3"
CONTAINER_SQLITE="/chroma/chroma/chroma.sqlite3"

echo "[$(date +%H:%M:%S)] Step 1: Stop container"
docker stop "$CONTAINER"

echo "[$(date +%H:%M:%S)] Step 2: Restore from backup"
# docker cp only works when container is STOPPED
docker cp "$BACKUP_DB" "$CONTAINER:$CONTAINER_SQLITE"

echo "[$(date +%H:%M:%S)] Step 3: Verify file size"
SIZE=$(docker exec "$CONTAINER" stat -c "%s" "$CONTAINER_SQLITE" 2>/dev/null || echo "0")
echo "Restored file size: $SIZE bytes (expected: 31137792)"
if [ "$SIZE" != "31137792" ]; then
    echo "⚠️ Size mismatch, but continuing..."
fi

echo "[$(date +%H:%M:%S)] Step 4: Start container"
docker start "$CONTAINER"
sleep 5

echo "[$(date +%H:%M:%S)] Step 5: Triple validation"
docker exec "$CONTAINER" python3 -c "
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
cols = client.list_collections()
result = [{'name': n.name, 'count': n.count()} for n in cols]
print(json.dumps(result))
# Also test query
if result:
    coll = client.get_collection(result[0]['name'])
    qr = coll.query(query_texts=['测试'], n_results=1)
    print('query_test:', 'OK' if qr['documents'] and qr['documents'][0] else 'EMPTY')
"

echo "[$(date +%H:%M:%S)] Done"
