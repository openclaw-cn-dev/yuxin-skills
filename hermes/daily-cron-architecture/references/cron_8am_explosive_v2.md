# 8 点爆款反向分析 V2 - 完整实战参考

**实战日期**：2026-06-12
**关联 cron**：0 8 * * *（"8点爆款分析"，deliver=feishu）
**关联脚本**：`C:\Users\Administrator\Desktop\知识库\search_toutiao.py`、`feishu_push_bakiku_v2.py`、`rag_query_v2.py`

---

## 1. 数据源（已验证稳定）

| 源 | URL 模板 | 抓法 | 实测产出 |
|---|---|---|---|
| 头条 | `https://so.toutiao.com/search?keyword={kw}&pd=information&page=N` | 真 UA + curl + 正则 `"title":"xxx"` | 18-20 条/关键词 |
| 搜狗 | `https://www.sogou.com/web?query={kw}&page=N` | 同上，正则 `class="vr-title..."` | 9-12 条/关键词 |

**死路（别再试）**：
- ❌ 抖音搜索（需 X-Bogus 签名）
- ❌ 知乎/微博/36kr 热榜（403）
- ❌ 搜狗**微信**搜索（命中即限流）
- ❌ Python urllib + SSL（同机 curl 通 Python SSL 挂）

详见 `aquaculture-content-sourcing` skill 的死路清单。

---

## 2. 完整 cron prompt（已跑通版本）

```python
PROMPT = """
【8 点每日爆款反向分析 - 升级版 V2】

**目标**：每天 8:00 自动从头条 + 搜狗抓取最新爆款标题，分析水产养殖/美食/设备的爆款规律，
输出可执行选题 + 推飞书 + 入库 RAG。

**执行步骤**（不要问，按顺序做）：

1. 抓取（terminal 中执行）：
   /c/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \\
     C:/Users/Administrator/Desktop/知识库/search_toutiao.py \\
     --source toutiao --rag "对虾养殖" "白灼虾" "循环水设备" "工厂化养殖" "海大集团"
   /c/.../python.exe .../search_toutiao.py --source sogou --rag "白灼虾" "对虾养殖" "循环水设备"

2. 加载抓取结果：读 搜索抓取/ 当天文件，提取所有标题（已去重）。

3. 分析 4 维度：
   - 标题公式：反常识 / 悬念 / 数字反差 / 大厨背书（每种公式举 3 个例子）
   - 钩子句：开头黄金 3 句
   - 选题打分：从今天抓的标题里挑 3-5 个最有爆款潜力的
   - 节奏规律：观察标题字数、emoji、#标签 使用频率

4. 入库 RAG（已通过 --rag 自动完成，只需验证）：
   - 用 rag_query_v2.py 查关键词验证召回
   - **失败不阻断**：用 try/except 包，记录 ⚠️

5. 推飞书（用 send_message）：
   - 收件人：feishu home channel (oc_529aff7485ccc35de97a9e7233d665dd)
   - 格式：4 维度 markdown 卡片 + 3-5 选题
   - 字数：≤ 1500 字

**重要约束**：
- 不要问老大，直接做完 —— 8 点跑的时候老大在睡觉
- 不要重复抓太多次（1-2 页够用）
- 失败用 try/except 跳过，**不中断流程**
- 输出文件路径要在推飞书时写明

**完整 prompt 字数控制**：≤ 1000 字
"""
```

---

## 3. 4 维度分析模板（**这是核心输出**）

### 维度 1：标题公式（4 种 × 各举 3 例）

每种公式必须给 3 个**真实抓取**的例子（不是模板）：

| 公式 | 模式 | 真实例子（2026-06-12 抓取）|
|---|---|---|
| 🔴 反常识 | "你以为的 XX 全错了" | 白灼大虾放油放盐都不对!大厨教你一招 / 用水煮就错了 / 持续阴雨天养虾核心技巧全做对 |
| 🟡 悬念/反问 | "到底是 XX 还是 XX" | 白灼虾煮 5 分钟还是 10 分钟 / 需要冷水下锅吗 / 怎么养对虾赚得多 |
| 🟢 数字反差 | "用数字做承诺" | 对虾养殖 4 大神器 / 潍坊成本降低 50% / 节能 20% |
| 🔵 大厨/老渔民背书 | "权威人物代言" | 大厨教你一招 / 老黄海鲜 / 老渔民教你避开 90% 新手会踩的坑 |

### 维度 2：钩子句模板（黄金 3 句）

输出**具体模板 + 频次 + 适用业务线**：

| 模板 | 频次 | 业务线 |
|---|---|---|
| "xxx 就错了/不对！教你正确方法" | 5 条 | 美食白灼 |
| "xxx 别猛喂/别直接……，五个诀窍少亏钱" | 3 条 | 养殖技术 |
| "看似简单其实全是坑：教你避开 90% 新手会踩的坑" | 2 条 | 养殖全攻略 |

**结论**：美食类最稳的钩子是"否定 + 教你一招"；养殖类最稳的是"数字 + 诀窍"；设备类最稳的是"节能 X%"。

### 维度 3：选题打分（TOP 5 候选）

表格形式：**排序 + 选题 + 业务线 + 公式 + 一句话立意**

```markdown
| ⭐⭐⭐ | **白灼大虾，放油放盐都不对！老渔民女儿教你一招** | 美食 | 反常识+IP | 把"大厨"换成本号 IP "老渔民女儿" |
| ⭐⭐⭐ | **南美白对虾 135 多茬养殖=年入 90 万？实地探访潍坊昌邑工厂** | 养殖 | 数字反差+探秘 | 用技术黑话 + 数字 |
```

**排序标准**（**核心判断**）：
- ⭐⭐⭐ = 公式极强 + 业务契合 + IP 可复用
- ⭐⭐ = 公式可用 + 业务相关
- ⭐ = 仅作参考

### 维度 4：节奏规律（数据说话）

| 指标 | 数值 | 启示 |
|---|---|---|
| 标题字数均值 | 21.2 字 | 黄金 18-25，**不要超 30** |
| 字数 ≤ 15 字（短） | 24% | 美食类偏短 |
| 字数 26-35 字（中长） | 34% | 养殖/设备类需装技术词 |
| 感叹号使用 | 13% | **不要滥**——美食钩子可以，新闻稿不要 |
| 问号使用 | 10% | 强悬念（"5 分钟还是 10 分钟？"），抖音视频号适配 |
| emoji 使用 | 0% | **头条/搜狗端几乎不用**；小红书/抖音可加 🦐🐟 |

**核心结论**：爆款 = **18-25 字 + 反常识钩子 + 数字/大厨背书**。超 30 字直接划走。

---

## 4. RAG 入库验证（**容易失败的步骤**）

### 验证命令

```bash
cd /c/Users/Administrator/Desktop/知识库 && \\
  /c/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \\
  rag_query_v2.py "白灼虾" 2>&1 | tail -10
```

### 已知失败模式（**2026-06-12 实战**）

| 错误 | 原因 | 修法 |
|---|---|---|
| `np.float_ was removed in the NumPy 2.0 release` | chromadb 旧版本用 np.float_，NumPy 2.0 已移除 | `pip install -U chromadb langchain-chroma langchain-huggingface` |
| `HNSW index loading failed` | chromadb 1.x 已知 bug（已在 chinese-rag-pipeline skill 详述） | 锁死 `chromadb==0.4.24` |

**关键**：**RAG 失败不阻断整个 cron 流程**——报告照写，飞书照推，只在报告末尾标注 ⚠️ 待修复。

---

## 5. 飞书多群 fan-out（**home channel 不可用时的 fallback**）

### 4 个目标群（已验证）

| 群 | chat_id | 用途 |
|---|---|---|
| RAS-老板总控 | `oc_80be3150a8bbf2c78cddfc8f1fd2cbc8` | **最优先**（home channel 语义）|
| RAS-水产美食 | `oc_b08d60b1a7f68597a7b2698d4e8d60ef` | 美食选题 |
| RAS-水产养殖 | `oc_9ed97e79f135f42c7e1f0669930cca51` | 养殖选题 |
| RAS-养殖设备 | `oc_42c00a76d4dd198c2c575369ad5582cb` | 设备选题 |

### Home channel 验证

`feishu_push_bakiku_v2.py` 硬编码的 `oc_529aff7485ccc35de97a9e7233d665dd`：
- 飞书 API 返 `bot_count=0, user_count=0` → **空群，机器人没在里面**
- 推送会返 230002 "Bot/User can NOT be out of the chat"
- **结论**：cron 必须自己 fan-out 到机器人**确实在**的 4 个群

### 推送代码模板

```python
import json, urllib.request, os
from pathlib import Path

# 凭证从环境变量取（避免 hermes 渲染层截断）
APP_ID = os.environ.get("FEISHU_APP_ID", "<FEISHU_APP_ID>")
APP_SECRET=os.env...n = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=data, headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())["tenant_access_token"]

# 读 md
md = Path(md_path).read_text(encoding="utf-8")
if len(md) > 4000:  # feishu_push_bakiku_v2.py 硬限制
    md = md[:4000] + "\n\n_...已截断_"

# Fan-out 4 个群
TARGETS = [
    ("oc_80be3150a8bbf2c78cddfc8f1fd2cbc8", "老板总控"),
    ("oc_b08d60b1a7f68597a7b2698d4e8d60ef", "水产美食"),
    ("oc_9ed97e79f135f42c7e1f0669930cca51", "水产养殖"),
    ("oc_42c00a76d4dd198c2c575369ad5582cb", "养殖设备"),
]
for chat_id, name in TARGETS:
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"🐟 8点爆款分析 · {TODAY}"}, "template": "blue"},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": md}},
            {"tag": "hr"},
            {"tag": "action", "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "📄 打开报告"}, "type": "primary", "url": file_url}
            ]},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "8:00 自动"}]}
        ]
    }
    msg = {"receive_id": chat_id, "msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)}
    url2 = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    req2 = urllib.request.Request(url2, data=json.dumps(msg).encode(),
                                  headers={"Content-Type": "application/json", "Authorization": "Bearer " + token})
    try:
        j = json.loads(urllib.request.urlopen(req2, timeout=10).read().decode())
        print(f"{name}: {j.get('code')} {j['data'].get('message_id') if j.get('code')==0 else j.get('msg')}")
    except Exception as e:
        print(f"{name}: ERROR {e}")
```

---

## 6. 关联文件 / 资源

| 路径 | 用途 |
|---|---|
| `C:\Users\Administrator\Desktop\知识库\search_toutiao.py` | 头条 + 搜狗 + 微头条 通用搜索脚本 |
| `C:\Users\Administrator\Desktop\知识库\feishu_push_bakiku_v2.py` | 飞书 markdown 卡片推送（硬编码 home channel）|
| `C:\Users\Administrator\Desktop\知识库\rag_query_v2.py` | RAG 检索验证 |
| `C:\Users\Administrator\Desktop\知识库\搜索抓取\` | 抓取结果落盘目录 |
| `C:\Users\Administrator\Desktop\知识库\YYYY-MM-DD-8点爆款分析报告.md` | 本次报告落盘模板 |

---

## 7. 改进空间

- 选题打分目前靠经验（⭐⭐⭐），下一步用历史爆款数据反推打分公式
- emoji 频率 0% 反映头条/搜狗调性——**小红书/抖音自动加成 1-2 个 emoji**
- "大厨" 在美食类重复 3 次，**建议建立人设库**（老渔民女儿 / 老黄海鲜 / 海洋大叔）轮换