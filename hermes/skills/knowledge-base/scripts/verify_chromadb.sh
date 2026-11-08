#!/bin/bash
# ChromaDB Health Verification Script
# Usage: bash verify_chromadb.sh
#
# IMPORTANT: Do NOT use `set -e` — errors in individual checks should not abort the whole script.
# All operations use docker exec + PersistentClient (not HttpClient) to avoid port conflicts.
# Known issue: HttpClient at port 8001 returns HTTP 502 due to Docker Desktop proxy conflict.

echo "=== Docker Daemon Check ==="
docker ps --filter "name=lookforge-chromadb" --format "{{.Names}}\t{{.Status}}" || echo "Docker not responding"

echo ""
echo "=== Collection Listing ==="
docker exec lookforge-chromadb python3 -c "
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
cols = client.list_collections()
print(f'Collections ({len(cols)}):', [c.name for c in cols])
" 2>/dev/null

echo ""
echo "=== Triple Validation: lookforge_knowledge ==="
docker exec lookforge-chromadb python3 -c "
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
try:
    c = client.get_collection('lookforge_knowledge')
    count = c.count()
    print(f'count() = {count}')
    peek = c.peek(limit=3)
    print(f'peek() = {len(peek[\"ids\"])} docs')
    q = c.query(query_texts=['RAS', '养殖'], n_results=3)
    print(f'query() = {len(q[\"documents\"][0]) if q[\"documents\"] and q[\"documents\"][0] else 0} results')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null

echo ""
echo "=== Triple Validation: competitor_analysis ==="
docker exec lookforge-chromadb python3 -c "
import os, chromadb, json, statistics
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
try:
    c = client.get_collection('competitor_analysis')
    count = c.count()
    print(f'count() = {count}')
    # Chunk quality check: sample 10 docs
    sample = c.peek(limit=min(count, 10))
    lengths = [len(d) for d in sample['documents']]
    mean_len = statistics.mean(lengths) if lengths else 0
    min_len = min(lengths) if lengths else 0
    print(f'chunk lengths: mean={mean_len:.0f}, min={min_len}')
    if mean_len < 300:
        print('  ⚠️ 平均长度 <300，疑似分块过碎！')
    if min_len < 100:
        print('  🔴 存在 <100 字符碎片，检索质量严重受损！')
    q = c.query(query_texts=['RAS设备', '对虾养殖'], n_results=3)
    hits = len(q['documents'][0]) if q['documents'] and q['documents'][0] else 0
    print(f'query() = {hits} results')
    if hits == 0 and count > 0:
        print('  🔴 count>0但query返回0！向量可能未生成（HTTP API add()不生成向量）')
except Exception as e:
    print(f'DOES NOT EXIST or ERROR: {e}')
" 2>/dev/null

echo ""
echo "=== Done ==="
