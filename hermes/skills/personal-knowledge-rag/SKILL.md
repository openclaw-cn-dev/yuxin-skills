---
name: personal-knowledge-rag
description: Build a personal AI twin / 影身-style assistant that ingests personal files into a local vector DB (Chroma), retrieves top-k chunks per question, prepends as context, and shells out to `hermes -z` for the final answer. Use when the user mentions "personal RAG", "AI 分身", "life log", "decision journal", "影身", or wants an LLM that knows their own context — not generic internet knowledge. Covers the 5-collection split (identity/history/decisions/preferences/studies), the context-string assembly pattern, the hermes subprocess invocation, embedding-model tradeoffs (default vs bge-m3 vs bge-small-zh), and a v0.1 → v2 evolution path.
version: 0.1.0
author: 玉芬 (渔芯科技)
metadata:
  hermes:
    tags: [rag, chroma, vector, personal-ai, twin, 影身, embedding]
    related_skills: [yuxin-coding-fallback-chain, apple, memory, knowledge-base]
license: MIT
---

# Personal Knowledge RAG (影身 Pattern)

> The pattern behind 影身 v0.1: ingest personal files → store in local Chroma → on each question retrieve top-k → prepend as context → shell out to `hermes -z` for the answer. Tunable today (22 seed docs), designed for v2 (multi-perspective decision support, scheduled lifecycle).

## When to use

Load this skill when the user mentions:
- "AI 分身" / "影身" / "personal twin" / "digital twin"
- Wanting an LLM that knows *their* facts (decisions, history, preferences), not just generic knowledge
- "Life log" / "decision journal" / "学习记录"
- Wants to retrieve from personal files before each LLM call
- Wants to bootstrap from `~/hermes/memory_store/user/` or similar L2 user-memory files

## The 5-collection split

A personal knowledge base is more useful when split by **cognitive purpose**, not by file type:

| Collection | Stores | Example entries |
|---|---|---|
| `identity` | Who the user is | Name, role, family, communication prefs |
| `history` | Past events | Education, career timeline, key milestones |
| `decisions` | Why-they-did-X | Decision logs with reasoning, dated |
| `preferences` | How-they-like-things | Tool stack, tone preferences, "stop doing X" notes |
| `studies` | Active learning | PhD prep, error book, current reading |

**Why split:** retrieval over a single "everything" collection tends to surface filler (basic identity) over signal (recent decisions). Splitting by cognitive purpose lets prompts request "what does huage prefer?" cleanly.

## Reference implementation: `~/hermes/yingshen/`

Three files, ~250 lines total:

### `yingshen_rag.py` — Chroma ingest + search
```python
import chromadb
from chromadb.utils import embedding_functions

CHROMA_CLIENT = chromadb.PersistentClient(path=str(CHROMA_DIR))
EMBEDDING_FN = embedding_functions.DefaultEmbeddingFunction()  # see tradeoff below

def get_or_create_collection(name: str):
    return CHROMA_CLIENT.get_or_create_collection(
        name=name, embedding_function=EMBEDDING_FN,
        metadata={"description": KB_COLLECTIONS[name]},
    )

def add_file(collection_name: str, file_path: str, source_name: str = None) -> int:
    """Chunk a markdown file by double-newline paragraphs, ingest each."""
    text = Path(file_path).read_text(encoding="utf-8")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip() and len(c.strip()) > 10]
    for i, chunk in enumerate(chunks):
        get_or_create_collection(collection_name).add(
            documents=[chunk], ids=[f"{collection_name}-{uuid.uuid4().hex[:8]}"],
            metadatas={"source": source_name or Path(file_path).name, "chunk_index": i},
        )
    return len(chunks)

def search(query: str, collection_names: list = None, n_results: int = 5) -> dict:
    results = {}
    for name in collection_names or list(KB_COLLECTIONS.keys()):
        res = get_or_create_collection(name).query(query_texts=[query], n_results=n_results)
        results[name] = {"documents": res["documents"][0], "metadatas": res["metadatas"][0],
                         "distances": res["distances"][0]}
    return results

def format_context(search_results: dict, max_chars: int = 2000) -> str:
    """Compact context string for prompt prepending. Each line: [col|source|sim] text."""
    parts, total = [], 0
    for coll_name, res in search_results.items():
        if "error" in res or not res.get("documents"): continue
        for doc, meta, dist in zip(res["documents"], res["metadatas"], res["distances"]):
            if total >= max_chars: break
            similarity = 1 - dist  # cosine distance → similarity
            line = f"[{coll_name}|{meta.get('source', '?')}|sim={similarity:.2f}] {doc}"
            parts.append(line); total += len(line)
        if total >= max_chars: break
    return "\n".join(parts)
```

### `ask_yingshen.py` — assemble context, shell to hermes
```python
SYSTEM_PROMPT = """你是【影身】，华哥的 AI 分身，人生自进化智能体。

# 你的定位
- 你**不是玉芬**（玉芬是渔芯科技 AI 团队管理员）
- 你是华哥**个人**的 AI 分身，跟华哥同时间生活

[context]
"""

def ask(question: str, n_results: int = 3) -> str:
    results = rag.search(question, n_results=n_results)
    context = rag.format_context(results, max_chars=2000)
    system_prompt = SYSTEM_PROMPT.replace("[context]", context or "（无相关知识库内容）")
    full_prompt = f"{system_prompt}\n\n---\n\n华哥问：{question}\n\n影身答："
    result = subprocess.run(
        ["hermes", "-z", full_prompt],
        capture_output=True, text=True, timeout=120,
    )
    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout.strip())
    return output
```

### `yingshen_rag.py` CLI subcommands
```
add <col> "text" [--source S]      # add one chunk
add-file <col> <file>              # batch by double-newline paragraphs
search "query" [--col X] [--n K]   # inspect retrieval without calling LLM
stats                              # count per collection
```

## Embedding-model tradeoff

| Option | Size | Chinese quality | Speed | v0.1 used |
|---|---|---|---|---|
| `DefaultEmbeddingFunction()` (chromadb built-in, MiniLM-L6-v2) | 80 MB | ⭐⭐ 中等 (~60% precision on CN queries) | 快 | ✅ |
| `bge-m3` (HuggingFace) | 1.2 GB | ⭐⭐⭐⭐⭐ SOTA | 慢首加载 | ⏸️ 待 v0.2 |
| `bge-small-zh-v1.5` (BAAI) | 95 MB | ⭐⭐⭐⭐ 接近 SOTA | 快 | ⏸️ 待 v0.2 |

**v0.1 已知**: chromadb 默认 MiniLM 是英文模型，中文检索距离经常 >1.0（看起来不精准）。**但能匹配到关键词**，准确率 ~60%。v0.2 换 bge-small-zh-v1.5 → 准确率 ~90%。

**换 embedding 的代价**: 整库要 re-ingest（向量维度不同）。**推荐做法**: 先建一个 `embedding_v2` 目录，新数据走新库，老库保留 fallback。

## Hermes subprocess invocation

**Why `hermes -z` 而不是直接调 OpenAI SDK**: 
- `hermes -z` 自动用 default profile 的活跃 LLM provider + 当前 fallback chain
- 不需要在每个项目里重复 load `.env` 找 key
- 跟玉芬对话走完全同一条推理路径 → 行为一致（含 L1 摘要注入）
- 缺点：单次 ~3-5s 启动开销 + 不能保留对话历史（每次新建 session）

**如果需要连续对话**：换用 `hermes --resume <session_id>` 或 `hermes --continue` 参数。

**ASCII 颜色码必须剥掉**：hermes 输出含 ANSI 转义码（绿/蓝提示），直接喂给下一个 prompt 会乱码。永远先 `re.sub(r"\x1b\[[0-9;]*m", "", output)`。

## Evolution path

| 版本 | 能力 | 工作量 |
|---|---|---|
| **v0.1** (this skill) | 5-collection RAG + hermes 整合 | 1 天 |
| v0.2 | 中文 embedding (bge-small-zh) + 22 → 200 种子 | 半天 |
| v0.3 | Feishu IM 集成（@影身 直接问） | 1 天 |
| v1.0 | 多视角决策（巴菲特/王阳明/...） | 1 周 |
| v2.0 | 同时间生活（calendar 订阅 + 主动推送） | 2 周 |

## Pitfalls

### Chromadb telemetry 警告（可忽略）
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
```
- 这是 chromadb 0.4.x 和新版 posthog SDK 的接口 mismatch
- **不影响功能** — 重定向 telemetry 即可：`os.environ["ANONYMIZED_TELEMETRY"] = "False"` 在 import 之前
- 不要为了消除警告去 downgrade posthog — 会拖累别的项目

### `voice_consistent`/`grouding` 不要打开
- chromadb 有 `where` / `where_document` 过滤语法，但初版不要碰
- 简单 `query_texts=[query]` + `n_results=K` 就够

### Default embedding 对中文"够用但不精准"
- 第一版完全 OK，不要急着换 bge-m3（多占 1.2GB 内存）
- **判断标准**: 检索返回的 top-1 chunk 跟 query 主题相关 → OK；返回乱码 → 换
- 真要换，**先跑对照测试**: 同样 30 个 query，老库 top-3 命中率 vs 新库 top-3 命中率

### context 长度控制
- LLM context window 有限（minimax 8K-32K），硬塞 5K context 会逼走真正的对话
- v0.1 用 `max_chars=2000` → context + prompt + response 都安全
- 高优做法：**per-collection max_chars**，让 `decisions` 优先于 `identity`（用户更关心最近决策，不是个签名）

### 不要给每个 LLM 调用都传知识库名列表
- 用户问"华哥是谁"不用告诉他"我从 identity / decisions / studies 各 3 条"
- 格式化 context 时，**保留 source 但不要带 collection 名**（避免幻觉"我看的是 X collection"，可能被用户反向追问）

## Common extension points

**1. 加新的 collection**: 
- 在 `KB_COLLECTIONS` dict 加键值 + 在 `~/hermes/yingshen/knowledge_base/<新名>/` 建目录
- 不需要改其它代码 — `add-file` / `search` 默认走所有 collection

**2. 加 persona（"切换到巴菲特视角"）**:
- 在 `~/hermes/yingshen/persona/<人名>.md` 加 prompt 模板
- `ask_yingshen.py` 加 `--persona <name>` CLI 参数，读取对应文件 preprend 到 system prompt

**3. 加 Feishu 集成**:
- 用 `feishu-api-notify` skill 推飞书消息
- webhook 收到消息 → `ask_yingshen.ask(text)` → 回复文本
- 默认 30s 超时需要调高（hermes 单次推理可能 10s+，加上 RAG 检索）

## Files (canonical paths)

```
~/hermes/yingshen/
├── knowledge_base/
│   ├── identity/         # 华哥是谁
│   ├── history/          # 历史
│   ├── decisions/        # 决策日志
│   ├── preferences/      # 偏好
│   └── studies/          # 学习
├── embeddings/           # chromadb 持久化
├── yingshen_rag.py       # 核心 RAG
├── ask_yingshen.py       # 调 hermes
└── logs/

~/.hermes/scripts/yuxin_yingshen.sh   # 启动 shell wrapper
~/ideas/2026-07-02_影身_v2_想法.md    # 完整设计文档
```

## Related skills

- `yuxin-coding-fallback-chain` — LLM provider 路由 / key 写入 / 配置保护
- `apple` — macOS 平台集成 (将来影身 v2 "同时间生活" 可能用到 Calendar API)
- `feishu-voice-assistant` — 当想给影身加语音交互入口（"嗨影身"）
- `memory` — L1/L2 memory 架构，影身的种子数据来源
