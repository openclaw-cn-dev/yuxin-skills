import sqlite3, requests, sys

DB = '/Users/hua/6-产品研发/ok-KnowHow知渔/db/ai_learning.db'
GATEWAY = 'http://127.0.0.1:18888/openai/v1/chat/completions'
MODEL = 'deepseek-v4-pro'
KEY = 'gateway-local-no-key-required'

SYSTEM = """你是渔芯「知渔」AI学习平台的路径设计师。为学习路径的阶段写一句「阶段产出」（phase_outcome）。
要求：
1. 一句话，20~40 字
2. 描述"学完这个阶段，学习者能独立做出什么/掌握什么"，面向求职/实战、具体可检验
3. 不要空话（"了解XX"太弱，要"能独立搭建/实现/完成XX"）
4. 直接输出这一句话，不要任何前缀/引号/客套"""

def gen_outcome(path, phase, desc, cards):
    card_str = '、'.join(cards[:6]) + ('…' if len(cards) > 6 else '')
    prompt = f"""路径「{path}」的第 {phase} 阶段：
- 阶段名：{phase}
- 阶段描述：{desc}
- 本阶段卡片：{card_str}

请输出这个阶段的「阶段产出」（一句话）："""
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.6,
        'max_tokens': 4000,  # 推理模型 reasoning_content 会吃掉 token，必须放大
    }
    r = requests.post(GATEWAY, headers={'Authorization': f'Bearer {KEY}'}, json=payload, timeout=180)
    r.raise_for_status()
    content = r.json()['choices'][0]['message'].get('content', '').strip()
    if not content or len(content) < 8:
        raise RuntimeError(f"产出过短({len(content)})")
    return content

if __name__ == '__main__':
    conn = sqlite3.connect(DB)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10000

    # 缺 phase_outcome 的阶段，JOIN 阶段内卡片名喂给 LLM
    rows = conn.execute("""
        SELECT pp.career_name, pp.phase_order, pp.phase_name, pp.phase_desc,
               GROUP_CONCAT(t.name, '、')
        FROM path_phases pp
        LEFT JOIN path_terms pt ON pt.career_name=pp.career_name AND pt.phase_order=pp.phase_order
        LEFT JOIN terms t ON t.id=pt.term_id
        WHERE (pp.phase_outcome IS NULL OR pp.phase_outcome='')
        GROUP BY pp.career_name, pp.phase_order
        ORDER BY pp.career_name, pp.phase_order
        LIMIT ?
    """, (limit,)).fetchall()

    done = 0
    for path, order, phase, desc, cards in rows:
        cards_list = [c for c in (cards or '').split('、') if c]
        try:
            outcome = gen_outcome(path, phase, desc or '', cards_list)
            conn.execute("UPDATE path_phases SET phase_outcome=? WHERE career_name=? AND phase_order=?",
                         (outcome, path, order))
            conn.commit()
            done += 1
            print(f"[{done}/{len(rows)}] OK {path} · {phase} -> {outcome}", flush=True)
        except Exception as e:
            print(f"[{done}/{len(rows)}] FAIL {path} · {phase}: {e}", flush=True)
    print(f"\n完成 {done}/{len(rows)}")
    conn.close()
