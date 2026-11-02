#!/bin/bash
# KB Watchdog 健康检查脚本
# 用法: bash kb_watchdog_health_check.sh

echo "=== KB Watchdog 健康检查 ==="
echo ""

# 1. 进程检查
echo "1. 进程检查:"
ps aux | grep kb_watchdog | grep -v grep | awk '{print "   PID:"$2, "PPID:"$3, "状态:"$8, "启动时间:"$9}'
PROCESS_COUNT=$(ps aux | grep kb_watchdog | grep -v grep | wc -l | tr -d ' ')
echo "   进程数: $PROCESS_COUNT"
if [ "$PROCESS_COUNT" -gt 1 ]; then
    echo "   ⚠️ 警告: 多于1个进程！手动 kill 重复进程"
fi
echo ""

# 2. 日志检查
echo "2. 日志检查:"
if [ -f ~/.hermes/logs/kb-watchdog.log ]; then
    LAST_LOG=$(tail -5 ~/.hermes/logs/kb-watchdog.log 2>/dev/null)
    echo "$LAST_LOG" | sed 's/^/   /'
    echo ""
fi
echo ""

# 3. ChromaDB 三重验证
echo "3. ChromaDB 三重验证:"
docker exec lookforge-chromadb python3 -c "
import chromadb
from chromadb.config import Settings
client = chromadb.PersistentClient(path='/chroma/chroma', settings=Settings(anonymized_telemetry=False))
coll = client.get_or_create_collection('lookforge_knowledge')

cnt = coll.count()
results = coll.query(query_texts=['RAS 循环水养殖'], n_results=3)
peek = coll.peek(limit=3)

status = '✅' if cnt > 0 and len(results['documents'][0]) == 3 and len(peek['documents']) == 3 else '❌'
print(f'   {status} count={cnt}, query={len(results[\"documents\"][0])} results, peek={len(peek[\"documents\"])} results')
" 2>&1 | grep -v "onnxruntime cpuid_info warning"
echo ""

echo "=== 检查完成 ==="
