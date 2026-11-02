---
name: chinese-tts-optimization
description: macOS 中文语音交互优化。当前 TTS 默认 Edge-TTS (zh-CN-XiaoxiaoNeural，免费自然女声)，Volc TTS key 恢复后可切回。ASR 用火山引擎 doubao-seed-asr-2.0。当用户提到语音音质不好、TTS 难听/ASR 不准、中文语音不自然、TTS key 过期、想换语音引擎时使用。
---

# 中文 TTS 优化方案

## 现状
- 当前 TTS: **Edge-TTS** `zh-CN-XiaoxiaoNeural`（免费、自然女声、需联网）
- 优点: 免费、音质远好于 macOS say、pip 一键安装
- 缺点: 需联网、微软 API 偶尔限流
- 历史: 曾用火山引擎 OpenSpeech `doubao-seed-tts-2.0`（音色 `zh_female_vv_uranus_bigtts`），key 过期（403）后切到 edge
- 回退: 断网时自动回退到 `say -v "Tingting" --rate=280` (macOS 内置)

### TTS 后端决策链（当前生效）

```
volc → (key 有效?) → edge → (网络正常?) → say（兜底）
```

**⚠️ Volc TTS key 可能独立过期**（不跟随 LLM 套餐）。验证方法见下方「故障诊断」。

## TTS 故障诊断

当语音回复音色奇怪（机械女声）时，先确认 volc TTS key 是否有效：

```bash
# 1. 测试 volc TTS key（现有 key）
curl -s -w "\nHTTP %{http_code}" -X POST \
  'https://openspeech.bytedance.com/api/v3/tts/unidirectional' \
  -H 'X-Api-Key: ***SECRET***' \
  -H 'X-Api-Resource-Id: seed-tts-2.0' \
  -H 'Content-Type: application/json' \
  -d '{"req_params":{"text":"测试","speaker":"zh_female_vv_uranus_bigtts","audio_params":{"format":"mp3","sample_rate":24000}}}'
```

| HTTP 码 | 错误码 | 含义 | 处理 |
|---------|--------|------|------|
| 200 | — | TTS 正常 | 确认 config.yaml `tts_backend: volc` |
| **403** | 45000030 | 资源未授权，key 过期 | 去火山语音控制台重新开通 |
| **401** | 45000010 | key 类型不匹配 | 用了 ark 前缀 key，必须用独立 OpenSpeech key |

**注意：** LLM 的 `ark-` 前缀 key **不能**用于 TTS（返回 45000010）。TTS 和 LLM 是火山引擎两个独立产品。

**快速修复（无需等 key 恢复）：** 切到 Edge-TTS：
```bash
# 修改 ~/hermes/voice/config.yaml
tts_backend: edge  # 原来是 volc

# 安装 edge-tts（如未安装）
pip install edge-tts

# 重启仪表盘
pkill -f voice_dashboard.py
cd ~/6-产品研发/21-语音交互 && /opt/homebrew/bin/python3.11 voice_dashboard.py --port 8765
```

## 替代方案对比

| 方案 | Stars | 中文质量 | 离线 | GPU需要 | 安装复杂度 |
|------|-------|---------|------|--------|-----------|
| **火山引擎 doubao-seed-tts-2.0** | - | ★★★★★ | ❌需联网 | 不需要 | ⭐ API |
| **小米 MIMO TTS** | - | ★★★★☆ | ❌需联网 | 不需要 | ⭐ API |
| **ChatTTS** | ~32k | ★★★★★ | ✅ | 推荐GPU | ⭐⭐ pip |
| **GPT-SoVITS** | ~35k | ★★★★★ | ✅ | 需要GPU | ⭐⭐⭐⭐ 复杂 |
| **Fish-Speech** | ~15k | ★★★★ | ✅ | 推荐GPU | ⭐⭐⭐ pip |
| **CosyVoice** | ~7k | ★★★★★ | ✅ | 推荐GPU | ⭐⭐⭐ pip |
| **Piper-TTS** | ~7k | ★★★ | ✅ | CPU即可 | ⭐ brew |
| **Edge-TTS** | ~6k | ★★★★ | ❌需联网 | 不需要 | ⭐ pip |

## 推荐方案（按优先级）

### 方案 A：火山引擎 OpenSpeech TTS（云端，中文效果天花板）⭐ 已验证

已有火山引擎账号可直接用。**⚠️ API Key 必须从语音控制台单独获取，Agent Plan 的 `ark-` 前缀 key 不能用于 OpenSpeech（会返回 45000010 Invalid X-Api-Key）**。

开通步骤：https://console.volcengine.com/speech/service → 开通语音合成 → 密钥管理 → 创建 API Key。

**可用音色：** `seed-tts-2.0` 资源下只有 `zh_female_vv_uranus_bigtts`（自然女声）。其他音色名（如 `***SECRET***`、`zh_female_tianmei_moon_bigtts`）会返回 `55000000 resource ID is mismatched with speaker`。

**⚠️ 返回格式陷阱：** HTTP TTS 端点返回 `Content-Type: text/plain`，内容是 JSON Lines（SSE 格式），音频数据 base64 编码在 `data` 字段中，**不是原始 MP3 字节流**。需要解析后解码。

```bash
# 验证是否开通成功（注意：返回的是 JSON Lines，不是原始音频）
curl -s -X POST "https://openspeech.bytedance.com/api/v3/tts/unidirectional" \
  -H "X-Api-Key: <OpenSpeech-Key>" \
  -H "X-Api-Resource-Id: seed-tts-2.0" \
  -H "Content-Type: application/json" \
  -d '{"req_params":{"text":"测试","speaker":"zh_female_vv_uranus_bigtts","audio_params":{"format":"mp3","sample_rate":24000}}}'
# 成功返回 JSON Lines: {"header":{"code":0,...}}  \n  {"data":"//uQxAAAA..."}
# 需要用下面 Python 代码解析
```

**Python 调用代码（已验证可用）：**

```python
import urllib.request, json, uuid, base64, subprocess

API_KEY = "your-key"
VOICE = "zh_female_vv_uranus_bigtts"
RESOURCE_ID = "seed-tts-2.0"

def volc_tts(text: str, output_path: str = "/tmp/volc_tts.mp3") -> str:
    """调用火山引擎 OpenSpeech TTS，返回音频文件路径"""
    body = {
        "req_params": {
            "text": text,
            "speaker": VOICE,
            "audio_params": {"format": "mp3", "sample_rate": 24000}
        }
    }
    req = urllib.request.Request(
        "https://openspeech.bytedance.com/api/v3/tts/unidirectional",
        data=json.dumps(body).encode(), method="POST"
    )
    req.add_header("X-Api-Key", API_KEY)
    req.add_header("X-Api-Resource-Id", RESOURCE_ID)
    req.add_header("X-Api-Request-Id", str(uuid.uuid4()))
    req.add_header("Content-Type", "application/json")
    
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode()
    
    # 解析 JSON Lines 格式，提取 base64 编码的音频
    chunks = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line == "[DONE]":
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        try:
            item = json.loads(line)
            if isinstance(item.get("data"), str) and item["data"].strip():
                chunks.append(base64.b64decode(item["data"].strip()))
        except (json.JSONDecodeError, base64.binascii.Error):
            pass
    
    if not chunks:
        raise RuntimeError(f"TTS 返回无音频数据: {raw[:200]}")
    
    audio = b"".join(chunks)
    with open(output_path, "wb") as f:
        f.write(audio)
    return output_path

# 使用
path = volc_tts("你好华哥，我是玉芬")
subprocess.run(["afplay", path])
```

**集成到 TTSEngine：** 在 `voice_common.py` 的 `TTSEngine` 中加 `volc` 后端，保留 `say` 作为断网 fallback。参考 HomeRail 源码 `~/6-产品研发/21-语音交互/homerail/homerail_manager/src/server/ark-voice.ts`。

### 方案 B：小米 MIMO TTS（云端，多音色）

```bash
curl -X POST "https://api.xiaomimimo.com/v1/audio/speech" \
  -H "api-key: $MIMO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-v2.5-tts",
    "input": "你好，我是玉芬",
    "voice": "冰糖"
  }' -o /tmp/mimo_tts.wav
afplay /tmp/mimo_tts.wav
```

可选音色：冰糖、茉莉、苏打、白桦、Mia、Chloe、Milo、Dean。

### 方案 C：Piper-TTS（最快、最省资源）
```bash
brew install piper
# 下载中文模型
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/cmu-arctic/cmu-arctic-medium/zh_CN-cmu-arctic-medium.onnx
piper --model zh_CN-cmu-arctic-medium.onnx --output_file /tmp/output.wav <<< "你好，我是玉芬"
afplay /tmp/output.wav
```

### 方案 D：ChatTTS（中文效果最好，Mac mini M 可跑）
```bash
pip install chattts
python3 -c "
from ChatTTS import ChatTTS
import torch, soundfile as sf
chat = ChatTTS.ChatTTS()
chat.load(compile=False)  # Mac 不支持 torch.compile
texts = ['你好华哥，我是玉芬']
wavs = chat.infer(texts, params_infer_code={'spk_emb': None})
sf.write('/tmp/chattts.wav', wavs[0], 24000)
"
afplay /tmp/chattts.wav
```

### 方案 E：Edge-TTS（免费，当前默认 ⭐）

```bash
pip install edge-tts
edge-tts --voice zh-CN-XiaoxiaoNeural --text "你好，我是玉芬" --write-media /tmp/output.mp3
afplay /tmp/output.mp3
```

**音色选择：**
- `zh-CN-XiaoxiaoNeural` — 活泼女声（当前默认）
- `zh-CN-XiaoyiNeural` — 温柔女声
- `zh-CN-YunxiNeural` — 男声
- `zh-CN-YunyangNeural` — 新闻男声

## 集成到唤醒词脚本

v6 唤醒词脚本（`yuxin_wake_word.py`）已原生支持三种 TTS 后端切换：

```python
TTS_BACKEND = "say"  # say | piper | edge
```

### 如何切换

1. 关掉旧进程：`kill -9 $(pgrep -f yuxin_wake_word.py)`
2. 编辑 `yuxin_wake_word.py` 第 89 行改 TTS_BACKEND
3. 启动：`source ~/.hermes/hermes-agent/venv/bin/activate && python3 ~/hermes/voice/yuxin_wake_word.py`

如果 Pipper 模型不存在或 Edge-TTS 连不上，自动回退到 `say`。

```python
# ✅ 方式一：Piper-TTS (CPU, 轻量)
subprocess.Popen(["piper", "--model", "zh_CN-cmu-arctic-medium.onnx", 
                  "--output-file", "/tmp/tts.wav"],
                 stdin=subprocess.PIPE)
# 写文本到 stdin...

# ✅ 方式二：ChatTTS (GPU, 效果好)
import soundfile as sf
from ChatTTS import ChatTTS
chat = ChatTTS.ChatTTS()
chat.load(compile=False)
wav = chat.infer([text])[0]
sf.write("/tmp/tts.wav", wav, 24000)
subprocess.Popen(["afplay", "/tmp/tts.wav"])

# ❌ 当前方式：
# subprocess.Popen(["say", "-v", "Tingting", "--rate=280", text])
# 保持为非阻塞 Popen
```

## 已知陷阱

1. **ChatTTS 不支持 torch.compile**：Mac M 芯片需 `chat.load(compile=False)`
2. **Piper 中文模型**：中文模型少且质量一般，比 macOS say 好一点但有限
3. **GPT-SoVITS** 安装复杂，需要 CUDA，Mac 上不建议
4. **Edge-TTS 国内可用**：但需要网络，且微软 API 偶尔限流
5. **多线程安全**：TTS 必须在主线程或独立进程调用，不能在 callback 里直接跑
6. **macOS say 中文语音**：Shelley 音色（温柔知性女声）+ 1.3x 语速（rate=260）是华哥偏好配置，不要用 Tingting 机械女声
7. **USB 麦克风音量陷阱**：不要上来就加增益！先测量原始音量。实测 USB Audio Device 说话时原始音量可达 1000-3000+，完全不需要增益。盲目加增益会导致环境噪音爆量，系统误触发。

---

## 语音交互系统开发流程

**华哥偏好：直接唤醒，不需要特定唤醒词，简洁高效**

### 第一步：测量原始音量（永远先做这个！）

```python
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
recording = sd.rec(int(0.3 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
sd.wait()
vol = int(np.mean(np.abs(recording)))
print(f"原始音量: {vol}")  # 正常说话: 1000-3000+
```

### 第二步：设置合理门限

| 场景 | 门限值 |
|------|--------|
| 环境噪音 | < 300 |
| 小声说话 | 300-800 |
| 正常说话 | 800-2000 |
| 大声说话 | 2000+ |

**推荐门限：300**（区分环境 vs 说话）

### 第三步：实现简单唤醒 + 对话循环

```python
import time

ENERGY_THRESHOLD = 300
CONVERSATION_TIMEOUT = 45

while True:
    # 唤醒模式
    vol = get_volume()
    if vol > ENERGY_THRESHOLD:
        speak("我在呢！")
        last_active = time.time()
        
        # 对话模式
        while time.time() - last_active < CONVERSATION_TIMEOUT:
            vol = get_volume()
            if vol > ENERGY_THRESHOLD * 2:
                speak("好的收到！")
                last_active = time.time()
            elif vol > ENERGY_THRESHOLD:
                last_active = time.time()
        
        speak("先休息了，有事叫我！")
```

### 第四步：后台运行 + 日志调试

```bash
# 后台运行
python3 voice_system.py &

# 实时查看日志
tail -f voice_log.txt
```

**关键调试指标：**
- 每次检测都打印音量值
- 用户说「叫了没有反应」= 先查日志看系统有没有检测到声音
- 如果日志为空 = 进程挂了
- 如果音量一直低于门限 = 麦克风采不到声音或门限设太高
- 如果一直触发（爆了）= 增益加太大或门限设太低
