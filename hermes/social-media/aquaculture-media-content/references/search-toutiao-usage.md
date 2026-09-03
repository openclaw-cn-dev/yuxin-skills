# search_toutiao.py 通用抓取脚本使用手册

> **作者**：Hermes Agent @ 2026-06-10
> **配套脚本**：`C:\Users\Administrator\Desktop\知识库\search_toutiao.py`（7.5KB）
> **配套库**：`scrape-web` skill 的反爬绕过手册（16 站实战分级）

## 用途

任何关键词 + 多个来源 + 自动入库到 RAG

## 快速开始

### 1. 抓单个关键词
```bash
cd "C:\Users\Administrator\Desktop\知识库"
python search_toutiao.py "白灼虾"
```

### 2. 抓多个关键词（批量）
```bash
python search_toutiao.py "白灼虾" "对虾养殖" "循环水设备"
```

### 3. 多页抓取
```bash
python search_toutiao.py "白灼虾" --pages 3
```

### 4. 指定来源
```bash
python search_toutiao.py "白灼虾" --source toutiao_video
python search_toutiao.py "白灼虾" --source sogou
```

### 5. 自定义输出路径
```bash
python search_toutiao.py "白灼虾" --out /tmp/result.md
```

### 6. 自动入库 RAG（**关键能力**）
```bash
python search_toutiao.py "白灼虾" "对虾养殖" --rag
```

## 支持的来源（**实战分级**）

| 来源 | 状态 | 实战数据 |
|---|---|---|
| `toutiao` | ✅ 稳 | 1.9MB HTML，47+ 条真实标题 |
| `toutiao_video` | ✅ 稳 | 微头条视频内容 |
| `sogou` | ✅ 稳 | 660KB HTML，**含知乎/百科/香哈网** |
| `weibo` | ⚠️ 卡 Visitor System | 需登录 cookie |
| `zhihu_video` | ⚠️ 卡 zse-ck | 知乎 zse-ck 验证 |

## 输出位置

默认：`C:\Users\Administrator\Desktop\知识库\搜索抓取\<时间戳>_<关键词>.md`

## 实战案例

### 案例 1：批量抓美食爆款
```bash
python search_toutiao.py "白灼虾" "椒盐皮皮虾" "蒜蓉蒸虾" "海鲜汤"
```

### 案例 2：抓对虾养殖技术
```bash
python search_toutiao.py "对虾养殖" "南美白对虾" "工厂化养虾" "循环水养殖"
```

### 案例 3：抓设备选型
```bash
python search_toutiao.py "循环水设备" "蛋白分离器" "生物滤池" "增氧机"
```

### 案例 4：抓公司新闻
```bash
python search_toutiao.py "海大集团" "通威股份" "恒兴" "粤海饲料"
```

## 关键修复（**踩过的坑**）

### 1. `re.sub` 配合 unicode 转义在 Windows bash 下报错
**症状**：`re.error: unterminated character set at position 6`
**原因**：Windows bash 环境下 `re.sub(r"\\u003c[^\\]+\\u003e", "", t)` 解析异常
**解决**：永远用字符串 `replace`，**不要用 regex** 处理 unicode 转义：

```python
# ❌ 错
t = re.sub(r"\\u003c[^\\]+\\u003e", "", t)

# ✅ 对
for em_pair in [
    ("\\\\u003cem\\\\u003e", ""),
    ("\\\\u003c/em\\\\u003e", ""),
    ("\\\\u002F", "/"),
    ("\\\\n", " "),
]:
    t = t.replace(*em_pair)
```

### 2. `codecs.decode(t, 'unicode_escape')` 破坏字符串
**症状**：把 `"\\u003cem\\u003e白灼虾"` 解码后变成 `"<em>白灼虾"` ——**转义被吃掉但又没全清**
**解决**：用字符串 `replace`（更可控）

### 3. git-bash `/tmp/` 路径在 Python 里找不到
**症状**：`curl -o /tmp/x.html` 在 git-bash 看得到，但 `python open('/tmp/x.html')` 找不到
**原因**：MSYS 路径映射和 Windows 路径不互通
**解决**：`cp /tmp/x.html "C:/Users/.../x.html"` 再用 Python 读

### 4. `--rag` 必须用 `add_documents()`，不要用 `from_documents()`
**症状**：用 `Chroma.from_documents()` 重建全库 168 秒
**正确**：`vectordb.add_documents(chunks)` 4.3 秒增量
**注意**：**不要 `vectordb.persist()`** —— Chroma 0.4+ 自动持久化

## 4 群 RAG 直接用

抓取的标题会自动入库 RAG，4 业务群问关键词 → 召回"搜索抓取"分类：

| 群 | 问 | 召回 |
|---|---|---|
| 🦐 美食 | "白灼虾" | 美食 + 搜索抓取（10+ 标题）|
| 🐟 养殖 | "对虾养殖" | 搜索抓取（14 标题）+ 物种专项/对虾 |
| ⚙️ 设备 | "循环水设备" | 设备 + 搜索抓取（18 标题）|
| 🏢 公司 | "海大集团对虾" | 设备公司/海大财报 |

## 性能基准

- 单关键词 1 页：~ 5-10 秒
- 3 关键词 × 1 页：~ 30 秒
- 抓取成功率：~ 95%（头条/搜狗最稳）
- 增量入库：~ 4 秒/3 chunks

## 后续升级（待办）

- ⬜ 微博/知乎详情页抓取（需 cookie/zse-ck）
- ⬜ 抖音/小红书抓取（cookie + X-Bogus 签名）
- ⬜ 抓详情页正文（不只标题）
- ⬜ 抓评论/点赞数
- ⬜ 多线程并发抓取

---

*作者：Hermes Agent @ 2026-06-10*
*配套：scrape-web skill / 反爬绕过实战手册 / rag_ingest.py*
