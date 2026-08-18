import sqlite3, requests, sys

DB = '/Users/hua/6-产品研发/ok-KnowHow知渔/db/ai_learning.db'
GATEWAY = 'http://127.0.0.1:18888/openai/v1/chat/completions'
MODEL = 'deepseek-v4-pro'
KEY = 'gateway-local-no-key-required'

SYSTEM = """你是渔芯「知渔」AI学习平台的教程作者。为名词卡片写教程正文（content_md）。
要求：
1. 用 2~3 个 `## 二级标题` 组织
2. 第一个标题讲「是什么/为什么需要」（痛点或动机），让零基础读者秒懂
3. 第二个标题讲「核心原理/关键要点」（分点或流程）
4. 可选第三个标题讲「实际应用/常见误区」
5. 总长 400~700 字，通俗但专业，用 **加粗** 标重点，用 `代码` 标术语
6. 直接输出 markdown 正文，不要任何前言/后记/「好的」之类客套话"""

def build_prompt(name, en, desc, group, diff):
    return f"""为下面这张名词卡片写教程正文：

- 名称：{name}
- 英文：{en}
- 一句话描述：{desc}
- 分类：{group}
- 难度：{diff}

请直接输出 content_md："""

def gen_content(name, en, desc, group, diff):
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': build_prompt(name, en, desc, group, diff)},
        ],
        'temperature': 0.7,
        'max_tokens': 6000,  # 推理模型 reasoning_content 会吃掉 token，必须放大
    }
    r = requests.post(GATEWAY, headers={'Authorization': f'Bearer {KEY}'}, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    content = data['choices'][0]['message'].get('content', '').strip()
    if not content or len(content) < 200:
        raise RuntimeError(f"content 过短({len(content)}字符)，可能被 reasoning 截断")
    return content

if __name__ == '__main__':
    conn = sqlite3.connect(DB)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # 默认只处理 1 张，全量传大数
    rows = conn.execute("""
        SELECT id, name, en, description, group_name, difficulty FROM terms
        WHERE (content_md IS NULL OR content_md='')
        ORDER BY CAST(substr(id,2) AS INTEGER) LIMIT ?
    """, (limit,)).fetchall()

    for tid, name, en, desc, group, diff in rows:
        print(f"[生成] {tid} {name} ...", flush=True)
        try:
            md = gen_content(name, en or '', desc or '', group or '', diff or '')
            conn.execute("UPDATE terms SET content_md=? WHERE id=?", (md, tid))
            conn.commit()
            print(f"  OK {len(md)} 字符: {md[:80]}...", flush=True)
        except Exception as e:
            print(f"  FAIL: {e}", flush=True)
    conn.close()
