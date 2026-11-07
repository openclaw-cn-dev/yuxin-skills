#!/usr/bin/env python3
# 语料预切块：绕过 MiniMind 系 PretrainDataset 的每篇 truncation 截断
# 用法: python corpus_chunker.py --tok <tokenizer目录> --input corpus.jsonl --output corpus_chunked.jsonl [--win 330] [--min 20] [--field text]
# 依赖: transformers（只需 tokenizer，不需要 torch）
# 2026-09-08 渔芯 RAS 语料实测: 1,258 篇(截断后仅 27% 利用) → 10,730 块(100% 利用), 8 epochs loss 5.91→0.99
import argparse, json

p = argparse.ArgumentParser()
p.add_argument('--tok', required=True, help='tokenizer 目录（含 tokenizer.json）')
p.add_argument('--input', required=True, help='原始 jsonl（每行 {"text": ...}）')
p.add_argument('--output', required=True, help='输出切块 jsonl')
p.add_argument('--win', type=int, default=330, help='每块 token 上限（应 ≤ 训练 max_seq_len - 10）')
p.add_argument('--min', type=int, default=20, help='丢弃过短尾块')
p.add_argument('--field', default='text', help='jsonl 文本字段名')
a = p.parse_args()

from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(a.tok)

n_docs = n_chunks = total_tokens = 0
with open(a.input, encoding='utf-8') as f, open(a.output, 'w', encoding='utf-8') as out:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            text = json.loads(line)[a.field]
        except Exception:
            continue  # 残缺行跳过
        ids = tok(text, add_special_tokens=False).input_ids
        total_tokens += len(ids)
        n_docs += 1
        for i in range(0, len(ids), a.win):
            chunk = ids[i:i + a.win]
            if len(chunk) < a.min:
                continue
            out.write(json.dumps({a.field: tok.decode(chunk)}, ensure_ascii=False) + '\n')
            n_chunks += 1

# 预检：假设 batch=32
est_steps = n_chunks // 32
print(f'文档 {n_docs} 篇 / 总tokens {total_tokens} / 切块 {n_chunks} 块 / 预计 ~{est_steps} 步/epoch (batch=32)')
print('对照训练日志实际步数——明显偏小仍说明有截断/丢行，先修数据再开训。')
