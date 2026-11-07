#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对 Hermes state.db 会话做 LLM 结构化摘要归档（支持批量 + 断点续跑）。

用法:
  python3 session_summarize.py --test
  python3 session_summarize.py --db <db> --session <id>            # 单会话试点
  python3 session_summarize.py --db <db> --list-old <days> --source feishu,cli
  python3 session_summarize.py --db <db> --batch --days <N> \
      --source feishu,cli --archive <归档jsonl> --profile <名>      # 批量归档
"""
import sqlite3, json, os, sys, argparse, urllib.request, urllib.error, time

HERMES_HOME = os.path.expanduser("~/.hermes")
DEEPSEEK_MODEL = "deepseek-chat"


def load_key():
    env = os.path.join(HERMES_HOME, ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY=") and not line.startswith("#"):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    cfg = os.path.join(HERMES_HOME, "config.yaml")
    if os.path.exists(cfg):
        for line in open(cfg, encoding="utf-8"):
            line = line.strip()
            if "api_key:" in line and "sk-" in line:
                v = line.split("api_key:", 1)[1].strip().strip('"').strip("'")
                if len(v) > 15:
                    return v
    return None


def call_llm(messages, key, max_tokens=1200, model=DEEPSEEK_MODEL, retries=3):
    url = "https://api.deepseek.com/v1/chat/completions"
    body = json.dumps({"model": model, "messages": messages,
                       "max_tokens": max_tokens, "temperature": 0.3},
                      ensure_ascii=False)
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body.encode("utf-8"), headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=180)
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"LLM 调用失败: {last_err}")


def test_api(key):
    for m in ["deepseek-v4-pro", "deepseek-chat"]:
        try:
            out = call_llm([{"role": "user", "content": "只回复两个字：正常"}], key, max_tokens=20, model=m)
            print(f"  {m} → OK: {out!r}")
        except Exception as e:
            print(f"  {m} → ERR: {e}")


def read_session(db_path, session_id):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    s = con.execute("SELECT id, title, source, started_at, ended_at, message_count, model "
                    "FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not s:
        con.close()
        return None
    msgs = con.execute(
        "SELECT role, content, tool_name, timestamp FROM messages "
        "WHERE session_id=? AND active=1 ORDER BY timestamp", (session_id,)).fetchall()
    con.close()
    return s, msgs


def build_transcript(s, msgs, max_chars=12000):
    lines = []
    total = 0
    for m in msgs:
        role = m["role"]
        if role not in ("user", "assistant"):
            continue
        content = (m["content"] or "").strip()
        if not content:
            continue
        tag = "华哥" if role == "user" else "玉芬"
        seg = f"[{tag}]\n{content}"
        if total + len(seg) > max_chars:
            break
        lines.append(seg)
        total += len(seg)
    return "\n\n".join(lines)


SUMMARY_PROMPT = """你是渔芯科技的会话归档助手。下面是华哥（负责人）与玉芬（AI 助手）的一段历史对话。
请生成结构化摘要，只输出 JSON（不要 markdown 代码块、不要其他文字），字段如下：
{
  "title": "一句话主题",
  "date_range": "起止日期(如 2026-09-01 ~ 2026-09-05)",
  "summary": "3-5句核心内容概述",
  "decisions": ["达成的决策/结论"],
  "actions": ["待办/后续行动"],
  "key_facts": ["关键数字/文件路径/凭证/配置/模型名等"],
  "projects": ["涉及的项目/系统"]
}
若对话内容少或纯闲聊，summary 简短，decisions/actions 可为空数组。key_facts 里不要放密钥明文。

对话原文：
"""


def summarize(s, msgs, key):
    transcript = build_transcript(s, msgs)
    if not transcript.strip():
        return {"title": s["title"] or "(无内容)", "summary": "(空会话)", "decisions": [],
                "actions": [], "key_facts": [], "projects": []}
    prompt = SUMMARY_PROMPT + transcript
    out = call_llm([{"role": "user", "content": prompt}], key, max_tokens=1200)
    out = out.strip()
    if out.startswith("```"):
        out = out.split("\n", 1)[1] if "\n" in out else out
        if out.rstrip().endswith("```"):
            out = out.rstrip()[:-3]
    try:
        return json.loads(out)
    except Exception:
        return {"title": s["title"] or "(解析失败)", "summary": out[:800],
                "decisions": [], "actions": [], "key_facts": [], "projects": []}


def ts(d):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(d)) if d else None


def list_old(db_path, days, source):
    cutoff = time.time() - days * 86400
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    q = ("SELECT id, title, source, started_at, ended_at, message_count FROM sessions "
         "WHERE started_at < ? AND ended_at IS NOT NULL")
    params = [cutoff]
    if source:
        srcs = [x.strip() for x in source.split(",")]
        q += " AND source IN (%s)" % ",".join("?" * len(srcs))
        params += srcs
    q += " ORDER BY started_at"
    rows = con.execute(q, params).fetchall()
    con.close()
    return rows


def batch(db_path, days, source, archive_path, profile, key, sleep_s=1.0):
    sessions = list_old(db_path, days, source)
    # 断点续跑：读已归档的 session_id
    done = set()
    if os.path.exists(archive_path):
        for line in open(archive_path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                done.add(json.loads(line)["session_id"])
            except Exception:
                pass
    todo = [s for s in sessions if s["id"] not in done]
    print(f"profile={profile} 总计待归档 {len(sessions)}，已完成 {len(done)}，本次处理 {len(todo)}")

    ok = fail = 0
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
    with open(archive_path, "a", encoding="utf-8") as f:
        for i, s in enumerate(todo):
            sid = s["id"]
            try:
                _, msgs = read_session(db_path, sid)
                digest = summarize(s, msgs, key)
                rec = {
                    "session_id": sid,
                    "source": s["source"],
                    "started_at": ts(s["started_at"]),
                    "ended_at": ts(s["ended_at"]),
                    "message_count": s["message_count"],
                    "title": s["title"],
                    "digest": digest,
                    "archived_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                ok += 1
                if (i + 1) % 10 == 0:
                    print(f"  进度 {i+1}/{len(todo)} (ok={ok} fail={fail})")
            except Exception as e:
                fail += 1
                print(f"  [FAIL] {sid}: {e}")
            time.sleep(sleep_s)
    print(f"完成: ok={ok} fail={fail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--db")
    ap.add_argument("--session")
    ap.add_argument("--list-old", type=int)
    ap.add_argument("--source")
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--archive")
    ap.add_argument("--profile", default="default")
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("未找到 API key"); sys.exit(1)

    if args.test:
        test_api(key); return

    db = args.db or os.path.join(HERMES_HOME, "state.db")

    if args.list_old:
        rows = list_old(db, args.list_old, args.source)
        print(f"待摘要旧会话: {len(rows)} 个")
        for r in rows[:50]:
            print(f"  {r['id']} | {r['source']} | {ts(r['started_at'])} | {r['message_count']}条")
        return

    if args.batch:
        archive = args.archive or os.path.join(HERMES_HOME, "session_archive", f"{args.profile}.jsonl")
        batch(db, args.days, args.source, archive, args.profile, key, sleep_s=args.sleep)
        return

    if args.session:
        s, msgs = read_session(db, args.session)
        if not s:
            print("会话不存在"); return
        print(f"会话: {s['title'] or '(无标题)'} | source={s['source']} | {len(msgs)} 条消息")
        print(json.dumps(summarize(s, msgs, key), ensure_ascii=False, indent=2))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
