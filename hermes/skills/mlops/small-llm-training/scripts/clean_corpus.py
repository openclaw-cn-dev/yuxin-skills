#!/usr/bin/env python3
"""领域语料清洗四刀（2026-09-07 RAS 语料 1668→1258 篇实测验证）。
改顶部常量后运行：文档级去重 → URL/导航噪音剔除 → 超短丢弃 → 迁移元数据剥离。
产出 {"text": ...} jsonl（MiniMind pretrain 格式直连）。"""
import os, re, json, hashlib

ROOTS = [  # ← 改：语料根目录列表
    "/Users/hua/rkr_staging/文档库/2-专业知识/202-RAS设备与技术工程",
    "/Users/hua/rkr_staging/文档库/2-专业知识/201-水产养殖科学基础",
]
OUT = "/Users/hua/6-产品研发/渔芯独角兽/01-开发中/渔芯RAS小模型/dataset_ras/pretrain_ras.jsonl"  # ← 改
MAX_CHARS = 20000  # 单篇封顶

URL = re.compile(r'^https?://\S+$')
NOISE = re.compile(r'^(首页|登录|注册|搜索|导航|下一篇|上一篇|相关推荐|版权所有|免责声明|阅读全文|\d+/\d+)$')
META = re.compile(r'<!--\s*migration_meta[\s\S]*?migration_meta\s*-->', re.I)

def clean(t):
    out = []
    for ln in META.sub('', t).splitlines():
        ln = ln.strip()
        if len(ln) < 8 or URL.fullmatch(ln) or NOISE.match(ln):
            continue
        out.append(ln)
    return '\n'.join(out)

def main():
    seen_doc, seen_head, docs, junk = set(), set(), [], 0
    for root in ROOTS:
        if not os.path.isdir(root):
            print(f"跳过不存在: {root}"); continue
        for dp, _, fns in os.walk(root):
            for fn in fns:
                if not fn.endswith('.md'): continue
                p = os.path.join(dp, fn)
                raw = open(p, encoding='utf-8', errors='ignore').read()
                h = hashlib.md5(raw.encode()).hexdigest()
                if h in seen_doc: junk += 1; continue
                seen_doc.add(h)
                t = clean(raw)
                if len(t) < 100: junk += 1; continue
                head = hashlib.md5(t[:200].encode()).hexdigest()
                if head in seen_head: junk += 1; continue
                seen_head.add(head)
                docs.append({"text": t[:MAX_CHARS]})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    chars = sum(len(re.sub(r'\s', '', d['text'])) for d in docs)
    print(f"入库 {len(docs)} 篇（剔 {junk}）| {chars/10000:.1f} 万净字符 ≈ {int(chars/1.5/10000)} 万 tokens | {os.path.getsize(OUT)/1048576:.1f} MB")

if __name__ == '__main__':
    main()
