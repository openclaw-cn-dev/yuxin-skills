#!/usr/bin/env python3
"""Weekly ai_jobs update: insert new AI job postings, expire stale ones.

Reusable template — copy, edit the `new_jobs` list and `expire_ids`, then run:
    python3 update_ai_jobs.py

Key facts (verified 2026-08-17):
- Canonical DB: /Users/hua/6-产品研发/ok-KnowHow知渔/db/ai_learning.db
- term_ids MUST reference real terms.id values (see references/job-database.md
  for the accurate T001-T287 map). Verify with:
      SELECT id, name FROM terms WHERE id IN (...)
- `requirements` is multiline; `skills` and `term_ids` are pipe-separated.
"""
import sqlite3, datetime, shutil

DB = "/Users/hua/6-产品研发/ok-KnowHow知渔/db/ai_learning.db"
NOW = datetime.datetime.now().isoformat(timespec="seconds")
POSTED = "2026-08"  # update to current month

shutil.copy2(DB, DB + f".bak_{datetime.date.today().strftime('%Y%m%d')}")
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Each dict = one job row. Fill every field.
new_jobs = [
    {
        "title": "示例岗位名称",
        "company": "公司",
        "location": "地点",
        "salary": "30-60K·16薪",
        "experience": "2-5年",
        "education": "本科及以上",
        "requirements": (
            "1. 第一行要求\n"
            "2. 第二行要求\n"
            "3. 第三行要求"
        ),
        "skills": "Python|RAG|LangChain|向量数据库",
        "term_ids": "T061|T062|T128|T004|T181",
        "source": "BOSS直聘",
        "category": "技术岗",
    },
    # ... add 5-10 representative jobs ...
]

for j in new_jobs:
    cur.execute(
        """
        INSERT INTO ai_jobs
        (title, company, location, salary, experience, education,
         requirements, skills, term_ids, source, category, posted_date, updated_at, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 'active')
        """,
        (j["title"], j["company"], j["location"], j["salary"],
         j["experience"], j["education"], j["requirements"], j["skills"],
         j["term_ids"], j["source"], j["category"], POSTED, NOW),
    )

# Expire stale/superseded jobs (have a concrete reason for each).
expire_ids = []  # e.g. [4, 18, 27, 38]
for i in expire_ids:
    cur.execute(
        "UPDATE ai_jobs SET status='expired', updated_at=? WHERE id=? AND status='active'",
        (NOW, i),
    )

conn.commit()

# --- report ---
cur.execute("SELECT COUNT(*) FROM ai_jobs WHERE status='active'")
active = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ai_jobs WHERE status='expired'")
expired = cur.fetchone()[0]
print(f"active={active}  expired={expired}  total={active+expired}")
cur.execute("SELECT id, title, company, salary, category FROM ai_jobs WHERE posted_date=? ORDER BY id", (POSTED,))
print("--- new jobs this run ---")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  @{r[2]}  {r[3]}  [{r[4]}]")
conn.close()

# NOTE: avoid fetching the same cursor twice in a loop — fetchone() consumes the row.
# Use one fetchall() and iterate, or store the row in a variable first.
