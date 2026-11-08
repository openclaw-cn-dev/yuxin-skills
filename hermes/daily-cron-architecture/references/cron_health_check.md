# Cron 健康检查完整 Snippet（6 点 cron必跑）

> **用途**：6 点 cron prompt里的「任务3：RAG 健康检查」段直接抄
> **验证**：2026-06-10第一次跑通，输出干净的 chunks / size / sample / agent.log 信号

---

## 一、昨日工作总结（session_search）

```python
session_search(query="昨天关键词", limit=5, sort="newest")
#整理4 大块：✅ 完成 / 📊 数据 / 🛑阻塞 / 🔜 待做
# ≤300 字
```

**触发词建议**（按老大常做的事）：
- "水产" / "小红书" / "抖音" / "飞书" / "爆款" / "简报" / "生图" / "codex" / "RAG"
- 不要用通用词如"昨天"（命中太多）

---

## 二、Skill巡检

```bash
hermes skills list
```

**输出格式（实测2026-06-10）**：
```
Installed Skills
┌─────────────────┬─────────┬─────┬─────┬─────────┐
│ Name │ Category│Source│Trust│Status │
├─────────────────┼─────────┼─────┼─────┼─────────┤
│ ... │ │ │ │ │
└─────────────────┴─────────┴─────┴─────┴─────────┘
0 hub-installed,11 builtin,83 local —94 enabled,0 disabled
```

**巡检决策规则**：
- ✅ **保留**：本 session实际用过 / cron引用 /业务直接相关
- ❌ **建议删**：3+ 个月没用 / 被 umbrella覆盖 / 测试桩 / fixture
- 🆕 **建议新装**：等老大批准，**小弟不擅自装**

---

## 三、Cron触发状态（agent.log grep）

```bash
#路径：❌ ~/.hermes/logs/ 不存在
# ✅ canonical: /c/Users/Administrator/AppData/Local/hermes/logs/agent.log

grep "Job.*missed\|Job.*fast-forward\|Job.*ok\|Job.*last_run" \
 /c/Users/Administrator/AppData/Local/hermes/logs/agent.log | tail -15
```

**Signal 解码**：
- `Job 'X' missed its scheduled time (Y, grace=7200s)` → **昨日静默跳过**
- `Fast-forwarding to next run: Z` → **今天也不补**
- `Job ... last run: ... ok` → **昨日跑通**

---

## 四、Provider client凭证信号

```bash
grep "Failed to rebuild shared OpenAI client\|OPENAI_API_KEY" \
 /c/Users/Administrator/AppData/Local/hermes/logs/agent.log | tail -5
```

**Signal 解码**：
-出现 `OPENAI_API_KEY not set`反复 warning → **provider凭证在 cron路径不可见**
-老大手动 `[System.Environment]::RemoveEnvironmentVariable('OPENAI_API_KEY')`调试 key rotation → **副作用是 cron静默 skip**

---

## 五、RAG库健康（3.11 venv python）

```bash
"C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
import os
os.environ['HF_HOME']='C:/Users/Administrator/.cache/huggingface'
os.environ['SENTENCE_TRANSFORMERS_HOME']='C:/Users/Administrator/.cache/huggingface'
import chromadb
from pathlib import Path
CHROMA = Path(r'C:\Users\Administrator\Desktop\知识库\chroma_db')
c = chromadb.PersistentClient(path=str(CHROMA))
co = c.get_collection('langchain')
n = co.count()
docs = co.peek(1)['documents']
sample = docs[0][:100] if docs else 'empty'
size_mb = sum(f.stat().st_size for f in CHROMA.rglob('*') if f.is_file()) /1024 /1024
print(f'chunks:{n}')
print(f'sample:{sample}')
print(f'chroma_db_size_mb:{size_mb:.1f}')
"2>&1 | tail -5
```

**输出（实测2026-06-10）**：
```
sample:# 🌍 水产简报 ·国外篇｜2026-06-08
chroma_db_size_mb:2.8
```

**健康基线**：
| 项 |正常 |异常 |
|---|---|---|
| chunks | >50 | <50 |
| size_mb | >1 MB | <1 MB |
| sample | 中文水产相关 | 空 /乱码 |

---

## 六、最后一句 status

-全部正常 → `🟢一切 OK`
- 有 missed job / size偏小 / OPENAI_API_KEY反复 warning → `🟡 需要关注` + 列报警项

---

## 反模式（2026-06-10验证）

- ❌ `ls ~/.hermes/logs/` → **directory not found**，浪费一次 tool call
- ❌ `python3` / 系统 pip → **找不到 chromadb**，要用3.11 venv python
- ❌ 在 cron prompt 里跑 `session_search(query="昨天")` → **0命中**，要用具体关键词
- ❌ `hermes cron run <id>`验证 cron行为 → 返回 `success: true` 但实际没跑（**只改了 schedule**，见 SKILL.md 已记录）
- ❌ 把9 点 cron missed 当一次性事件 → **连续多天都会 missed**，**今天9:00 是关键验证点**

---

##关联

-父 skill：`daily-cron-architecture`（4-cron模板 + 健康检查）
-协作 skill：`skill-curator-agent`（每日 skill巡检）
-关联 RAG skill：`local-rag-knowledge-base` / `chinese-rag-pipeline`
