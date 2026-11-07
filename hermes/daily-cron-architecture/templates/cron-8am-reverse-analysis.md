# 8 点 cron 爆款反向分析 prompt V2 模板

> **用途**：每天 8:00 自动从头条 + 搜狗抓取最新爆款标题，分析水产养殖/美食/设备的爆款规律，输出可执行选题 + 推飞书 + 入库 RAG。
> **验证时间**：2026-06-10
> **适用场景**：老大在睡觉，cron 自动跑，跑完直接推飞书

---

## 📝 完整 prompt（≤ 1000 字）

```
【8 点每日爆款反向分析 - 升级版 V2】

**目标**：每天 8:00 自动从头条 + 搜狗抓取最新爆款标题，分析水产养殖/美食/设备的爆款规律，输出可执行选题 + 推飞书 + 入库 RAG。

**执行步骤**（不要问，按顺序做）：

1. **抓取**（在终端中执行）：
```bash
cd /c/Users/Administrator/Desktop/知识库
/c/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe search_toutiao.py --source toutiao --rag "对虾养殖" "白灼虾" "循环水设备" "工厂化养殖" "海大集团"
/c/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe search_toutiao.py --source sogou --rag "白灼虾" "对虾养殖" "循环水设备"
```

2. **加载抓取结果**：读 `C:/Users/Administrator/Desktop/知识库/搜索抓取/` 当天文件，提取所有标题（已去重）。

3. **分析 4 维度**（用 4 个固定角度）：
   - **标题公式**：反常识 / 悬念 / 数字反差 / 大厨背书（每种公式举 3 个例子）
   - **钩子句**：开头黄金 3 句（"xxx 就错了" / "看似简单" / "老渔民教你"）
   - **选题打分**：从今天抓的标题里挑 3-5 个最有爆款潜力的
   - **节奏规律**：观察标题字数、emoji、#标签使用频率

4. **入库 RAG**（已通过 --rag 自动完成，**只需验证**）：
   - ⚠️ **不要**用 `rag_query_v2.py` 直接查 —— 撞 HNSW 损坏会 raise `Cannot open header file` 把 cron 整跑挂（**2026-06-19 实测**，连续多日 HNSW 损坏）
   - ✅ **走 SQLite 元数据检查**（绕开 HNSW 索引文件）：
     ```bash
     "C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" -c "
     import sqlite3
     DB = r'C:\Users\Administrator\Desktop\知识库\chroma_db\chroma.sqlite3'
     con = sqlite3.connect(DB)
     n = con.execute('SELECT COUNT(*) FROM embeddings').fetchone()[0]
     last = con.execute(\"SELECT datetime(max(strftime('%s', created_at)), 'unixepoch') FROM embeddings\").fetchone()[0]
     con.close()
     print(f'chunks:{n} | last:{last}')
     "
     ```
   - **健康基线**：chunks 比昨天增加 1-30、last 时间 = 今天 → 入库成功
   - **异常**：chunks 与昨天相同 + last 时间是昨天 → ⚠️ 入库失败，sqlite 元数据完整，需老大跑 `python rag_setup.py` 重建 HNSW

5. **推飞书**（用 send_message）：
   - 收件人：feishu home channel (oc_529aff7485ccc35de97a9e7233d665dd)
   - 格式：4 维度 markdown 卡片 + 3-5 选题
   - 字数：≤ 1500 字

**重要约束**：
- **不要问老大，直接做完** —— 8 点跑的时候老大在睡觉
- 不要重复抓太多次（1-2 页够用）
- 失败用 try/except 跳过，**不中断流程**
- 输出文件路径要在推飞书时写明
```

---

## 🎯 4 维度分析（固定模板）

### 1. 标题公式
- **反常识**：「xxx 就错了」「xxx 不直接下锅就煮」
- **悬念**：「看似简单，其实每一步都有窍门」
- **数字反差**：「一上桌就抢光」「好吃绝了」
- **大厨背书**：「酒店大厨」「老渔民」「老师傅」

每种公式举 3 个今天抓到的真实例子。

### 2. 钩子句
开头黄金 3 句（最容易爆的句式）：
- 「虾最忌X就错了，大厨分享不用Y的Z」
- 「看似简单的X，其实每一步都有窍门」
- 「X不直接下锅就煮，YY教你方法」

### 3. 选题打分
从当天抓的标题里挑 3-5 个最有爆款潜力，按潜力分排序：
- 5⭐ = 完美符合公式 + 有反差
- 4⭐ = 公式齐全但缺反差
- 3⭐ = 单一公式

### 4. 节奏规律
- 标题字数（**15-30 字最易爆**）
- emoji 使用（**0-1 个**）
- # 标签（**3-5 个**）

---

## ⚙️ 配 cron 步骤

```bash
# 1. 创建 cron job
hermes cron create \
  --name "每日 8 点爆款反向分析 V2" \
  --schedule "0 8 * * *" \
  --prompt "$(cat templates/cron-8am-reverse-analysis.md | head -50)" \
  --deliver feishu

# 2. 编辑 prompt（如果用模板）
hermes cron edit <job_id> --prompt "$(cat templates/cron-8am-reverse-analysis.md | head -50)"

# 3. 验证
hermes cron list | grep "8 点"
```

---

## 🛑 Pitfall（必看）

1. **prompt 字数 ≤ 1000** —— 超长会爆 cron 缓存
2. **8 点跑时老大在睡觉** —— 失败不要重试（sleep 1.5s 即可），**不要问老大**
3. **`<repositories>` 选 1-2 个** —— 太多会触发反爬
4. **`--rag` 选 run 后** —— RAG 重建需要 3-5 秒
5. **推飞书一定要附上输出文件路径** —— 老大点开就能看
6. **RAG 验证走 SQLite 不走 rag_query_v2.py** —— 撞 HNSW `Cannot open header file` 会让 cron 整跑挂（**2026-06-19 实测**：连续多日 HNSW 损坏，sqlite 元数据完好但 HNSW 头文件打不开），详见上方 step 4

---

## 🧪 验证清单

跑完 cron 后问自己：
- [ ] 头条 3 关键词都跑出 ≥ 10 条
- [ ] 搜狗 3 关键词都跑出 ≥ 5 条
- [ ] RAG chunks +1~+5（用 SQLite 元数据查，不走 rag_query_v2.py）
- [ ] 飞书卡片 4 维度齐全
- [ ] 推了 3-5 个选题

---

*最后更新：2026-06-19*
*维护人：Hermes Agent*
*验证人：老大*
