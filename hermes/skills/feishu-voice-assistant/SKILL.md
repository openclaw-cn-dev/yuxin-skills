---
name: feishu-voice-assistant
description: "Build a voice-controlled AI assistant that bridges Feishu voice messages to an Agent (e.g. Hermes/RKR) with ASR + TTS round-trip. Use when the user mentions 'voice control', 'voice assistant', '常驻语音助手', 'voice to agent', '小爱/小艺-like', 'speech to code', or wants to receive voice messages in Feishu/IM and respond with synthesized speech. Covers the 4-layer architecture (ASR → Agent → TTS → IM), API choices (DashScope/Deepgram/CosyVoice/ElevenLabs), webhook design, idempotency, and Phase 1-3 MVP path from Feishu voice-only to always-on wake-word device."
version: 1.0.0
author: Hermes Agent + 渔芯科技
metadata:
  hermes:
    tags: [voice, asr, tts, feishu, agent, realtime, cosyvoice, dashscope]
    related_skills: [hermes-agent, feishu-api-notify, hermes-batch-cron-patterns]
---

# 飞书语音助手 / Always-On Voice Agent 实施指南

> **本 skill 解决"语音消息 → Agent → 语音回复"的完整链路**，覆盖从 MVP 到养殖场硬件部署的 3 个阶段。

触发条件：华哥提到"语音指挥 Agent"、"像小爱/小艺"、"常驻语音助手"、"speech to code"、"voice control"、或要在 Feishu/微信/Telegram 上接收语音消息并以语音回复时。

---

## 1. 四层架构（必背）

```
[麦克风永远监听] 
   ↓ 唤醒词（"渔芯"/"Hey 渔芯"）
[ASR 流式转文字]   ← 阿里通义实时 / Deepgram / Whisper
   ↓ 文字流
[LLM Agent + 工具] ← Claude Sonnet + Hermes / GPT-4o / Qwen
   ↓ 文字流
[TTS 流式转语音]   ← CosyVoice / ElevenLabs / OpenAI TTS
   ↓
[扬声器/IM 发送]
```

**关键指标**：端到端 < 1s 才像自然对话。Phase 1 用飞书 IM 中转（4-5s 可接受），Phase 2 上实时流式。

---

## 2. 2026 主流 API 选型

### ASR（语音转文字）

| 方案 | 特点 | 价格 | 适用 |
|---|---|---|---|
| **阿里通义 Paraformer Realtime-v2** | 中文 SOTA / 国内合规 | ~0.0001 元/秒 | **华哥首选（中文）** |
| **Deepgram Nova-3** | 极低延迟 WebSocket | $0.0043/分钟 | 海外项目 |
| **OpenAI Whisper Streaming** | 多语言准 | $0.006/分钟 | 海外 |
| **whisper.cpp** | 本地推理 | 免费 | 隐私/内网 |

### TTS（文字转语音）

| 方案 | 拟人度 | 价格 | 适用 |
|---|---|---|---|
| **阿里 CosyVoice** | 中文 SOTA | ~0.02 元/千字 | **华哥首选（中文）** |
| **ElevenLabs Streaming** | 拟人度 SOTA | $5-22/月 | 演示/海外 |
| **OpenAI TTS-HD Streaming** | 优秀 | $15/1M chars | 海外 |
| **GPT-4o Voice** | 端到端 | 一体化价 | 端到端方案 |

### LLM/Agent
- **Claude Sonnet 4 + Function Calling**（华哥已有 Hermes）
- **GPT-4o Realtime**（一体化语音 + Agent，但贵）
- **通义千问 Qwen3**（国内）

---

## 3. Phase 1 MVP（1 周）—— 飞书语音闭环

**最简实现**：飞书语音消息 → 阿里 ASR → Hermes Agent → 阿里 TTS → 飞书语音回复。

### 工程结构
```
yva-mvp/
├── server.py                  # FastAPI 主服务
├── config.py                  # 环境变量加载
├── asr/
│   ├── base.py                # ASRBase + ASRResult
│   └── aliyun_streaming.py    # 通义实时 ASR 实现
├── tts/
│   ├── base.py                # TTSBase + TTSResult
│   └── cosyvoice.py           # CosyVoice 实现
├── agent/
│   └── hermes_bridge.py       # 接 RKR backend hermes/chat
└── feishu_voice/
    ├── downloader.py          # 飞书语音文件下载
    ├── sender.py              # 文字/语音发送
    └── webhook.py             # 事件编排
```

### 关键代码模式

**Webhook 入口**（必须异步，避免阻塞飞书）：
```python
@app.post("/webhook/feishu")
async def feishu_webhook(request: Request):
    payload = await request.json()
    asyncio.create_task(handle_feishu_voice_event(...))  # 异步
    return JSONResponse({"code": 0})  # 立即 200
```

**完整数据流**（`feishu_voice/webhook.py`）：
```python
async def handle_feishu_voice_event(payload, asr, tts, agent, ...):
    # 1. 解析事件 → 拿 file_key + message_id + chat_id
    # 2. 立即发"正在处理"文字消息（避免用户以为没响应）
    await send_feishu_text_message(chat_id, "正在处理您的语音...")
    # 3. 下载飞书语音文件（.opus）
    await download_feishu_file(file_key, message_id, tmp_path)
    # 4. ASR 转文字
    asr_result = await asr.transcribe_file(tmp_path)
    if not asr_result.text: return  # 失败回退
    # 5. 调 Agent
    agent_response = await agent.chat(asr_result.text)
    # 6. TTS 合成
    tts_result = await tts.synthesize(agent_response)
    # 7. 发飞书语音（带文字 fallback）
    if tts_result.success:
        await send_feishu_voice_message(chat_id, tts_result.file_path, agent_response)
    else:
        await send_feishu_text_message(chat_id, agent_response)
```

**Hermes 桥接**（`agent/hermes_bridge.py`）—— 流式解析 SSE：
```python
async with client.stream("POST", f"{gateway}/api/v1/hermes/chat",
    json={"message": message, "stream": True},
    headers={"Authorization": f"Bearer {token}"}
) as resp:
    full_answer = ""
    async for line in resp.aiter_lines():
        if line.startswith("data:"):
            data = json.loads(line[5:].strip())
            if data.get("type") == "answer":
                full_answer += data.get("content", "")
```

**飞书语音发送**（`feishu_voice/sender.py`）—— 两步走：
```python
# 1. 先上传文件获取 file_key
file_key = await upload_feishu_file(file_path, file_type='opus')
# 2. 用 msg_type='audio' 发送
await send_message(msg_type='audio', content={"file_key": file_key})
```

### 关键 Pitfall

1. **Webhook 同步阻塞** → 必须 `asyncio.create_task` 异步处理，立即返回
2. **TTS 失败回退** → 文字 fallback 必不可少
3. **Hermes 慢** → 设 180s 超时 + 流式而非等完整响应
4. **飞书文件上传** → 必须先 `POST /im/v1/files` 拿 `file_key`，再发消息
5. **沉默期** → 先发"正在处理"文字，避免用户以为卡死
6. **重复事件** → 飞书 webhook 会重试，加 idempotency_key

---

## 4. Phase 2（2-3 周）—— Mac 客户端 + 唤醒

新增能力（2026-07-02 实际实现）：
- **唤醒词**：Whisper ASR（faster-whisper tiny）检测"小张小张"（支持 partial 唤醒）
- **ASR 引擎**：faster-whisper tiny（离线，~300ms 延迟，CPU int8）
- **声纹验证**：librosa MFCC 40 维 + 余弦相似度锁（阈值 0.82）
- **VAD**：基于能量（RMS），静音 800ms 自动结束录制
- **TTS 引擎**：macOS `say -v Tingting --rate=280`（中文女声）
- **桌面浮动窗**：Swift 原生，右上角 6 秒后自动消失
- **交互策略**：任务类 → "好的，现在开始执行" → 静默执行 → "华哥，XXX已完成"；问答类 → 直接念精简回答
- **响应对比**：VOXK 小模型→ 误识别率高；Whisper tiny → 精度明显提升

### 实现架构（已验证可用）

```
┌─────────────────────────────────────────┐
│  [麦克风 - 16kHz, int16, mono]          │
│       ↓ 30ms blocks                     │
│  ┌────────┐  ┌────────────┐  ┌───────┐  │
│  │ VAD    │→│ Whisper ASR │→│Voice- │  │
│  │(RMS   )│  │(faster-wsp)│  │print  │  │
│  │energy) │  │ tiny, int8  │  │Lock   │  │
│  └────────┘  └────────────┘  └───┬───┘  │
│                                   ↓      │
│  mode="wake": 监听 → VAD → Whisper →    │
│    含"小张小张"? → 声纹验证 → 通过 →    │
│    "来了，华哥" → mode="dialogue"        │
│                                          │
│  mode="dialogue": VAD→Whisper→hermes -z │
│    → 任务：确认"好的"→等待→汇报          │
│    → 问答：直接念回答                     │
└─────────────────────────────────────────┘
```

### 关键参数

```python
# VAD 参数
VAD_WINDOW_MS = 30                # 每次处理 30ms 音频块
VAD_ENERGY_THRESHOLD = 300        # RMS 能量阈值（调低=更灵敏）
VAD_BUFFER_SILENCE_MS = 800       # 安静 800ms 结束录音
VAD_MIN_RECORD_MS = 400           # 最少录音时长
DIALOGUE_SILENCE_MS = 1500        # 对话模式安静 1.5s 认为说完
DIALOGUE_MAX_SECONDS = 30         # 最长录制 30s

# 声纹锁参数
VOICEPRINT_THRESHOLD = 0.82       # 余弦相似度阈值
# 注册样本 6 段，注册时一致性 1.000 最稳
# 非管理员声音匹配度约 0.000（清晰区分）
```

### 环境依赖 & 模型下载

```bash
# 依赖
pip install faster-whisper sounddevice librosa numpy
# 测试加载
python3 -c "from faster_whisper import WhisperModel; m = WhisperModel('tiny', device='cpu', compute_type='int8')"
```

**国内模型下载（hf-mirror.com 镜像）**：
```python
import urllib.request, ssl, os
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

files = ['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt']
base = 'https://hf-mirror.com/Systran/faster-whisper-tiny/resolve/main'
cache_dir = os.path.expanduser('~/.cache/huggingface/hub/models--Systran--faster-whisper-tiny/snapshots/main')
os.makedirs(cache_dir, exist_ok=True)
for f in files:
    url = f'{base}/{f}'
    outpath = os.path.join(cache_dir, f)
    urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}),
                           timeout=120, context=ssl_ctx).read()
    with open(outpath, 'wb') as out:
        urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}),
                               timeout=120, context=ssl_ctx)
```

### 启动/停止

```bash
# 停所有旧进程
ps aux | grep yuxin_wake_word | grep -v grep | awk '{print $2}' | xargs kill -9
# 启动（首次会下载 tiny ~72MB）
source ~/.hermes/hermes-agent/venv/bin/activate
python3 ~/hermes/voice/yuxin_wake_word.py &
# 实时日志
tail -f ~/hermes/voice/logs/wake_word.log
```

### 关键 Pitfall

1. **多进程残留**：多次启动会导致多个唤醒词进程并发，需先 `kill -9` 所有旧进程再启动
2. **faster-whisper 默认从 huggingface.co 下载**，国内网络不通，需从 hf-mirror.com 手动下载到缓存目录
3. **device="auto" 可能选 MPS 导致兼容性问题**，强制 `device="cpu", compute_type="int8"` 最稳
4. **声纹验证用声纹识别后的环形缓冲**（最后 5 秒 PCM），不是即时截取——确保缓冲足够长
5. **任务类指令判断**：不完美，靠关键词列表（"做"/"查"/"写"/"建"/"改"/"删"/"发送"等），有时会误判纯问题为任务
6. **`hermes -z` 最长 160s**，大任务可能超时

工程结构：
```
yva-mvp/
├── client/
│   ├── mac/                   # macOS 客户端（pyobjc）
│   ├── wake_word/             # OpenWakeWord 自训
│   └── vad/                   # WebRTC VAD
```

---

## 5. Phase 3（8-12 周）—— 养殖场硬件

硬件清单：
- 主控：ESP32-S3 / 全志 R329
- 麦克风：ReSpeaker 4-mic 阵列
- 扬声器：3W 防水喇叭
- 网络：4G Cat-1 模组
- 防护：IP65 防水外壳

**关键：水产噪声 ASR 模型**
- 录制 100+ 小时养殖场噪声
- 用 whisper-large-v3 微调（或阿里语音定制模型）
- 目标：噪声场景准确率 > 90%

**离线应急指令**：
- 网络断时，本地缓存最近 5 条命令
- 紧急情况用预设指令："启动应急增氧" / "停泵"

---

## 6. v4 战略卡位（重要）

**为什么"语音"是渔芯 v4 战略的差异化**：

| 维度 | 传统水务公司（首创/北控） | 渔芯 |
|---|---|---|
| 平台 | PC Web + 移动 APP | **语音 Agent** |
| 操作 | 鼠标/触屏 | **说话** |
| 工人 | 需培训 | **50+ 岁也能用** |
| 应急 | 找联系人 | **一句话报警** |

**结论**：语音 Agent 不是"附加功能"，是渔芯"中国养殖尾水 WaaS 平台开创者"战略的**前台 + 入口**。

---

## 7. 实施检查清单

### Phase 1 必达
- [ ] 飞书 webhook 收到语音消息
- [ ] ASR 转写中文准确率 > 90%
- [ ] Hermes Agent 推理正常
- [ ] TTS 合成可播放
- [ ] 飞书发送语音 + 文字双 fallback
- [ ] 端到端 < 5s

### Phase 1 加分
- [ ] 多人支持（识别发送者 open_id）
- [ ] 多轮对话（上下文保持）
- [ ] 复杂任务路由（"派给老莫"）
- [ ] 错误隔离（单条失败不影响整批）

### 监控指标
- 日均处理语音条数
- ASR 准确率
- 平均响应时间
- TTS 成功率
- 用户满意度

---

## 8. 成本估算

### 内部 MVP
- ASR 通义：~100 元/月
- TTS CosyVoice：~50 元/月
- Hermes：0（已有）
- 飞书：0
- **合计：~150 元/月**

### 单场养殖场部署
- 硬件：500-2000 元/台
- ASR/TTS：~500 元/月/场
- 带宽：~100 元/月/场
- **合计：单场月成本 1000-2000 元**

### 单场定价
- 包年服务：5-10 万/年
- 毛利率：70-80%
- **投资回收期：3-6 个月**

---

## 9. 关键文件位置

- **完整实施文档**：`~/yva-mvp/实施文档.md`（20K 字详细 spec）
- **MVP 代码**：`~/yva-mvp/`（10 个 Python 文件）
- **服务运行**：`python3 server.py` → http://localhost:8080/health
- **配置文件**：`~/yva-mvp/.env`（从 `.env.example` 复制，填入 DashScope Key）

---

## 10. 相关 Skill

- **hermes-agent**: hermes 命令参考、cron、profile
- **feishu-api-notify**: 飞书消息发送（通用模式）
- **feishu-bot-cloud-drive**: 飞书云盘操作（独立于语音）
- **hermes-batch-cron-patterns**: 长跑任务 + 状态持久化模式
- **cron-health-monitor**: cron 失败诊断

## 11. 支持文件

- `templates/yva-mvp-server.py` — FastAPI 主服务入口模板（webhook + 异步 + health）
- `templates/feishu-voice-webhook.py` — 飞书语音事件编排模板（4 段链路完整）
- `references/2026-06-17-yva-mvp-case.md` — 真实案例：1 周内 10 个文件交付全过程

## 12. 经验来源

- 2026-06-17 渔芯科技 "常驻语音助手 YVA" MVP：华哥在抖音看到 Agent 工程师用语音指挥 AI → 1 周内交付 4 层架构完整代码（10 个 Python 文件 + 完整文档）→ 服务跑通 health 200 OK → 等华哥申请 DashScope Key + 飞书机器人配置 → 端到端可用。
- v4 战略：华哥明确指出"语音 Agent 是 v4 战略卡位"——传统水务公司无语音 → 渔芯可抢先定义行业标准。
- v1-v4 业务迭代：水处理 WaaS 单点 → 金融化平台 → 通用平台 → **战略卡位 + 语音入口**。
