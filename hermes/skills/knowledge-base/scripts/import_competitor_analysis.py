#!/usr/bin/env python3
"""
Import market files into competitor_analysis collection.
Usage: 
  1. Copy files to container: docker cp /tmp/market_files/. lookforge-chromadb:/tmp/market_files/
  2. Run this script: docker exec lookforge-chromadb python3 /tmp/import_competitor_analysis.py
"""
import os, glob, hashlib, chromadb
from chromadb.config import Settings

os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))

coll = client.get_or_create_collection(
    name='competitor_analysis',
    metadata={'description': 'RAS竞品分析、市场行情、竞争对手资料'}
)
print(f'Collection: {coll.name}, existing count: {coll.count()}')

kb_path = '/tmp/market_files/'
files = glob.glob(os.path.join(kb_path, '*.md'))
print(f'Found {len(files)} files at {kb_path}')

def split_text(text, chunk_size=600, overlap=100):
    """Split text into overlapping chunks by paragraphs."""
    lines = text.split('\n')
    chunks, current, current_len = [], [], 0
    for line in lines:
        current.append(line)
        current_len += len(line) + 1
        if current_len >= chunk_size:
            chunks.append('\n'.join(current))
            overlap_lines, overlap_len = [], 0
            for l in reversed(current):
                overlap_lines.insert(0, l)
                overlap_len += len(l) + 1
                if overlap_len >= overlap:
                    break
            current = overlap_lines if overlap_lines else [current[-1]]
            current_len = overlap_len
    if current:
        chunks.append('\n'.join(current))
    return chunks

docs, metas, ids = [], [], []
for f in sorted(files):
    name = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    # Split by paragraphs (double newline or long enough single blocks)
    paras = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
    print(f'  {name}: {len(paras)} paras, {len(content)} chars')
    for i, para in enumerate(paras):
        cid = hashlib.md5(f'{name}_{i}'.encode()).hexdigest()[:16]
        docs.append(para)
        metas.append({
            'source': f'市场行情/{name}',
            'category': 'competitor_analysis',
            'file': name,
            'chunk': i
        })
        ids.append(f'comp_{cid}')

if docs:
    coll.add(documents=docs, metadatas=metas, ids=ids)
    print(f'Added {len(docs)} chunks, new count: {coll.count()}')
else:
    print('No files found - check /tmp/market_files/ exists in container')
