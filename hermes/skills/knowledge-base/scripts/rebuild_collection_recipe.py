#!/usr/bin/env python3
"""
rebuild_collection_recipe.py
===========================
重建 ChromaDB collection 的标准步骤。

用途：修复 "count()>0 但 query()=0" 的向量丢失问题。
场景：competitor_analysis 因 HTTP API add() 不生成向量而 query() 失效（2026-05-06 实录）。

用法：
  # 1. 在容器内导出当前数据（避免丢失）
  docker exec lookforge-chromadb python3 -c "
    import os, chromadb, json
    from chromadb.config import Settings
    os.chdir('/chroma')
    client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
    coll = client.get_collection('competitor_analysis')
    all_data = coll.get()
    export = []
    for i in range(len(all_data['ids'])):
        export.append({
            'id': all_data['ids'][i],
            'document': all_data['documents'][i],
            'metadata': all_data['metadatas'][i] if all_data['metadatas'] and i < len(all_data['metadatas']) else {}
        })
    with open('/tmp/export.json', 'w', encoding='utf-8') as f:
        json.dump(export, f, ensure_ascii=False)
    print(f'Exported {len(export)} docs')
  "

  # 2. 复制到宿主机（docker cp 有 bug，用容器内 cat 重定向）
  docker exec lookforge-chromadb cat /tmp/export.json > /tmp/competitor_export.json

  # 3. 用容器内 Python 重建 collection（自动生成向量）
  docker exec lookforge-chromadb python3 -c "
    import os, chromadb, json
    from chromadb.config import Settings
    os.chdir('/chroma')
    client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))

    # 删除旧 collection
    client.delete_collection('competitor_analysis')
    print('Deleted old collection')

    # 重建
    coll = client.create_collection('competitor_analysis', metadata={'description': '竞品分析', 'version': 'v6'})
    print('Created new collection')

    # 读取导出数据（在 /tmp 下，容器内可访问）
    with open('/tmp/export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    ids = [d['id'] for d in data]
    docs = [d['document'] for d in data]
    metas = [d['metadata'] for d in data]

    # add() 会自动触发 ONNXMiniLM_L6_V2 embedding 生成
    coll.add(ids=ids, documents=docs, metadatas=metas)
    print(f'Added {len(ids)} documents')

    # 验证
    print(f'count: {coll.count()}')
    qr = coll.query(query_texts=['RAS养殖'], n_results=3)
    hits = len(qr['documents'][0]) if qr['documents'] and qr['documents'][0] else 0
    print(f'query hits: {hits}')
    if hits > 0:
        print('SUCCESS: vectors generated correctly')
    else:
        print('ERROR: vectors still not generated!')
  "

关键约束：
  - 永远不要用 HTTP API add() 创建需要 embedding 的新 collection
  - 必须用容器内 PersistentClient add()（自动触发 embedding）
  - docker cp 有 Docker Desktop bug，必须用容器内 cat 重定向
"""

import json, os, sys

# 步骤1：确认导出数据
EXPORT_PATH = '/tmp/competitor_export.json'
if not os.path.exists(EXPORT_PATH):
    print(f"ERROR: {EXPORT_PATH} not found. Run export step first.")
    sys.exit(1)

with open(EXPORT_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Export contains {len(data)} documents")
print(f"Sample ID: {data[0]['id']}")
print(f"Sample doc length: {len(data[0]['document'])}")
print(f"Sample metadata: {data[0]['metadata']}")
