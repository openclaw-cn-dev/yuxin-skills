#!/usr/bin/env python3
"""
直接通过 SQLite 提取 ChromaDB 数据，重建带 embedding function 的 collection
绕过 count()/peek()/query() 的 BLOB/u64 bug
修复 ChromaDB 0.4.x seq_id BLOB 问题
"""
import sys, os
sys.path.insert(0, '/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend')

import sqlite3
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings

DATA_DIR = '/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/data/chroma'
OLD_NAME = 'lookforge_knowledge'

def main():
    print("Step 1: 通过 SQLite 直接提取数据")
    
    db_path = os.path.join(DATA_DIR, 'chroma.sqlite3')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Find the lookforge_knowledge collection id
    c.execute("SELECT id FROM collections WHERE name = ?", (OLD_NAME,))
    row = c.fetchone()
    if not row:
        print(f"ERROR: Collection '{OLD_NAME}' not found!")
        return
    coll_id = row[0]
    
    # Find the METADATA segment for this collection
    c.execute("""
        SELECT id FROM segments 
        WHERE collection = ? AND type LIKE '%metadata/sqlite'
    """, (coll_id,))
    seg_row = c.fetchone()
    if not seg_row:
        print("ERROR: No metadata segment found!")
        return
    seg_id = seg_row[0]
    
    # Get all embeddings
    c.execute("""
        SELECT id, segment_id, embedding_id FROM embeddings 
        WHERE segment_id = ?
    """, (seg_id,))
    emb_rows = c.fetchall()
    print(f"Found {len(emb_rows)} embeddings")
    
    ids, docs, metas = [], [], []
    for (emb_id, seg_id, emb_emb_id) in emb_rows:
        c.execute("SELECT key, string_value FROM embedding_metadata WHERE id = ?", (emb_id,))
        meta_rows = c.fetchall()
        meta_dict = dict(meta_rows)
        
        content = meta_dict.get('chroma:document', '')
        ids.append(emb_emb_id)
        docs.append(content)
        metas.append({k: v for k, v in meta_dict.items() if k != 'chroma:document'})
    
    conn.close()
    print(f"Extracted {len(ids)} records")
    
    # Step 2: Delete old collection
    print("\nStep 2: 删除旧 collection")
    client = chromadb.PersistentClient(path=DATA_DIR, settings=Settings(anonymized_telemetry=False))
    client.delete_collection(OLD_NAME)
    
    # Step 3: Create new with embedding function
    print("\nStep 3: 创建新 collection（带 embedding function）")
    ef = embedding_functions.DefaultEmbeddingFunction()
    new_col = client.get_or_create_collection(
        name=OLD_NAME,
        embedding_function=ef,
        metadata={'description': 'LookForge product development knowledge base'}
    )
    
    # Step 4: Add documents
    print("\nStep 4: 添加文档")
    for i in range(0, len(ids), 50):
        new_col.add(documents=docs[i:i+50], metadatas=metas[i:i+50], ids=ids[i:i+50])
        print(f"  Added {min(i+50, len(ids))}/{len(ids)}...")
    
    # Step 5: Verify
    print("\nStep 5: 验证 query()")
    result = new_col.query(query_texts=['RAS'], n_results=3)
    print(f"Query 'RAS' returned {len(result['ids'][0])} results")
    print(f"\n重建完成！Records: {new_col.count()}")

if __name__ == '__main__':
    main()
