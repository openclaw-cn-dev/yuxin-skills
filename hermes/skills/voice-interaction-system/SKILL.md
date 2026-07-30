---
name: voice-interaction-system
description: 玉芬语音交互系统的实现方法论 — 4 阶段渐进式（含火山引擎 ASR + TTS、Whisper fallback、SileroVAD、声纹锁、打断机制、多轮上下文）。触发条件：华哥提「语音交互/语音唤醒/语音对话」、macOS 本地语音 pipeline、ASR/TTS 集成、火山引擎 OpenSpeech、或「让 Hermes 能听到/念出来」、TCC 麦克风权限问题。
version: 0.13.0
author: 渔芯玉芬
tags: [voice, asr, tts, whisper, sounddevice, macos, hermes-integration, offline]
license: MIT
metadata:
  hermes:
    tags: [voice, asr, tts, whisper, sounddevice, macos, hermes-integration, offline]
---

# 玉芬语音交互系统 — 4 阶段渐进式

## 适用场景

构建 macOS 本地语音交互系统：用户说 → 识别成文字 → 调 LLM → 念出回复。全程本地、不依赖云端语音 API、不上传任何音频。

## 运行前提

### ⚠️ Mac mini 无内置麦克风 — 必须连接蓝牙耳机

Mac mini 全系列（含 M4 Mac16,10）**没有内置麦克风**。语音交互完全依赖外部输入设备：

- ✅ 蓝牙耳机/耳麦（如 JSoul Mate Pro）
- ✅ USB-C / USB-A 麦克风
- ❌ 3.5mm 耳机口 — 仅输出，不支持麦克风输入
- ❌ OrayVirtualAudioDevice — 向日葵虚拟设备，永远返回静音

**快速验证输入设备：**
```bash
python3.11 -c "
import sounddevice as sd
[(i, d['name'], d['max_input_channels']) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]
"
# 应有物理设备且 RMS > 0
```

**隔离测试录音：**
```bash
python3.11 -c "
import sounddevice as sd, numpy as np
audio = sd.rec(int(16000*3), 16000, channels=1, dtype='float32')
sd.wait()
rms = np.sqrt(np.mean(audio**2))
print(f'RMS={rms:.6f} — {\"有声音\" if rms > 0.0001 else \"❌ 静音！检查蓝牙连接\"}')"
```

如果蓝牙耳机断开，唯一可用的"输入"是 OrayVirtualAudioDevice（向日葵虚拟设备），永远返回 RMS=0。VAD 可能被系统杂讯误触发，但录音全是零。检查蓝牙连接状态：`system_profiler SPBluetoothDataType | grep -A5 JSoul`

```
麦克风 → sounddevice (16kHz mono int16)
     → 火山引擎 OpenSpeech `doubao-seed-asr-2.0` (默认，云端 ASR，WebSocket 二进制协议)
     → 网络断开/未订阅时回退到 faster-whisper tiny
     → 文本 → hermes -z "<prompt>"
     → 火山引擎 OpenSpeech `doubao-seed-tts-2.0` (默认, 中文天花板, 音色 `zh_female_vv_uranus_bigtts`)
     → 断网回退到 `say -v Tingting`
     → 喇叭
```

### 云端 ASR/TTS 升级路径（HomeRail 参考架构）

调研 [HomeRail](https://github.com/xiaotianfotos/homerail)（voice-first agent orchestration runtime）后，识别出可借鉴的云端语音方案：

| 提供商 | ASR | TTS | 接入方式 | 备注 |
|---|---|---|---|---|
| 火山引擎 OpenSpeech | doubao-seed-asr-2.0 | doubao-seed-tts-2.0 | WebSocket / HTTP API | 已有火山引擎账号，直接可用 |
| 小米 MIMO API | mimo-v2.5-asr | mimo-v2.5-tts | REST API | 冰糖/茉莉/苏打/白桦等音色 |

**推荐策略：云端优先 + 本地 fallback（ASR/TTS 均已实现）**
- 网络正常时用火山引擎 ASR/TTS（准确率 + 自然度远超本地方案）
- 断网时自动切回 Whisper tiny + macOS `say`
- `VolcASR` 类位于 `voice_common.py`，纯 Python 实现 WebSocket 二进制协议
- TTS 音色 `zh_female_vv_uranus_bigtts` 是当前中文 TTS 天花板之一

**⚠️ OpenSpeech API Key 独立于 Agent Plan**

火山引擎的 OpenSpeech（语音合成/识别）和 Agent Plan（LLM）是**两个独立产品**，需要分别开通：

| 服务 | API Key 前缀 | 开通地址 |
|---|---|---|
| Agent Plan (LLM) | `ark-...` | console.volcengine.com/ark |
| OpenSpeech (TTS/ASR) | 独立 key | console.volcengine.com/speech/service |

**Agent Plan 的 `ark-` 前缀 key 不能用于 OpenSpeech**，会返回 `45000010 Invalid X-Api-Key`。必须去语音控制台单独开通并获取 key。

```bash
# 验证是否开通成功（成功返回音频，失败返回 JSON 错误）
curl -s -X POST "https://openspeech.bytedance.com/api/v3/tts/unidirectional" \
  -H "X-Api-Key: <OpenSpeech-Key>" \
  -H "X-Api-Resource-Id: seed-tts-2.0" \
  -H "Content-Type: application/json" \
  -d '{"req_params":{"text":"测试","speaker":"zh_female_vv_uranus_bigtts","audio_params":{"format":"mp3","sample_rate":24000}}}' \
  -o /tmp/tts_test.mp3 && file /tmp/tts_test.mp3
# 成功: "MPEG ADTS" → afplay /tmp/tts_test.mp3
# 失败: "JSON data" → cat /tmp/tts_test.mp3 看错误码
```

**语音专用 LLM 模型推荐（2026-07-09 更新）**

语音对话场景（快速简短回复 + 中文口语化）的首要选择是**同一平台的豆包模型**，因为跟 OpenSpeech ASR/TTS 在同一平台（火山引擎），延迟更低。

| 排名 | 模型 | 输入/输出价格 | 延迟 | 适合语音? | 备注 |
|:---:|---|---|:---:|:---:|---|
| 🥇 | **doubao-seed-2-1-pro** | ¥6/¥30 百万token | ⚡ 快 | ✅ **首选** | 旗舰中文，同平台最低延迟 |
| 🥈 | doubao-seed-2-1-turbo | ¥3/¥15 百万token | ⚡⚡ 更快 | ✅ 高频场景 | 价格减半，速度更快 |
| 🥉 | doubao-seed-evolving | ¥6/¥30 百万token | ⚡ 快 | ✅ 备选 | 周级迭代 Coding/Agent |
| 4 | deepseek-v4-flash | $0.14/$0.28 | ⚡ 快 | ✅ 备选 | 跨平台，延迟稍高 |

**为什么不用 deepseek-v4-pro？** 太重（推理慢），语音场景需要快速响应，pro 的深度推理在语音对话中是浪费。

**包月套餐推荐**：火山方舟 Agent Plan（月付订阅，成本可控）。详见 `references/voice_llm_pricing_comparison.md`。

配置方式：`HermesClient.call()` 传 `-m doubao-seed-2-1-pro-260628` 参数，或创建独立 Hermes profile 配豆包模型 + 口语化 system prompt。

### 双通道语音输出（HomeRail 借鉴）

HomeRail 的 commentary + final 双通道设计值得引入：

```
commentary 通道 → 过程播报（"正在搜索..."、"找到3篇文章，正在整理..."）
final 通道     → 最终回复（"根据搜索结果，建议如下..."）
```

实现方式：在 agent loop 中加 `on_tool_start` / `on_tool_end` 回调，工具调用间隙插入简短语音播报。不需要 Codex harness，直接在 `yuxin_dialogue.py` 中实现。

### voice-memo 机制（HomeRail 借鉴）

用户连续表达时先记录到 memo，追问确认范围后再执行，避免"还没说完就开跑"：

```python
VoiceMemo:
  title: str
  status: "listening" | "clarifying" | "ready" | "executing" | "done"
  summary: str
  known_facts: list[str]
  open_questions: list[str]
  todos: list[{text, done}]
  ready_to_execute: bool
```

参考文件：`~/6-产品研发/21-语音交互/调研_HomeRail语音交互系统_2026-07-09.md`  
HomeRail 源码：`~/6-产品研发/21-语音交互/homerail/`

### ASR: Whisper + VAD + 声纹锁（取代旧版 VOSK）

| 组件 | 当前选型 | 理由 |
|---|---|---|
| ASR | 火山引擎 OpenSpeech `doubao-seed-asr-2.0` (默认) | 云端识别率 >95%，远超 Whisper tiny (~75%)；VolcASR 类位于 voice_common.py，回退到 Whisper small (~90%) |
| VAD | 自建能量检测 | 检测人声起止，调高阈值到 500 减少误触 |
| 唤醒词 | Whisper 识别「小张小张」 | 比 Porcupine SDK 更灵活，不需要额外 SDK |
| 声纹锁 | librosa MFCC 40 维 | 纯手工，零外部依赖，只识别华哥声音 |
| TTS | 火山引擎 OpenSpeech `doubao-seed-tts-2.0` (默认) | 豆包语音合成，中文天花板，音色 `zh_female_vv_uranus_bigtts`，回退到 `say` |
| 录音 | sounddevice | pip 直接装不需编译，modern API |
| 浮动窗 | Swift 编译 (~/hermes/voice/yuxin_bubble) | Mach-O arm64 原生，显示回复 6s 自动消失 |

### 对比：Whisper vs VOSK

| 指标 | VOSK 小模型 | Whisper tiny | Whisper small | 火山引擎 OpenSpeech |
|---|---|---|---|---|---|
| 精度 | 中文 85-90% | 中文 ~75% | 中文 ~90% | 中文 >95% |
| 模型大小 | ~42MB | ~200MB | ~600MB | 云端 |
| 识别延迟 | 流式实时 | ~30ms | ~100ms | ~200ms (网络) |
| 安装 | pip install vosk | pip install faster-whisper | pip install faster-whisper | 无需安装 |
| 加载时间 | <1s | ~1s | ~3s | <1s |
| 网络要求 | 离线 | 离线 | 离线 | 需要网络 |

## macOS 麦克风权限（TCC）实战

macOS 的 TCC（Transparency, Consent, and Control）是语音唤醒的头号坑。

### 症状
- sounddevice 录音返回 RMS<0.001（全静音）
- ffmpeg 录音也返回静音
- 之前能用的脚本突然无声

### 根因
- tccutil reset Microphone 或系统更新会清除所有麦克风授权
- SIP 开启时直接写 TCC.db 无效
- 蓝牙耳机（JSoul Mate Pro）的 SCO 链路需要应用显式请求

### 修复步骤

1. 弹系统对话框让用户去开权限：
```bash
osascript -e 'tell app "System Events" to display dialog "请去 系统设置→隐私→麦克风 打开终端"'
```

2. 直接在终端跑 Python 录音，会弹出 macOS 授权框：
```bash
python3 -c "import sounddevice as sd, numpy as np; audio=sd.rec(32000,16000,channels=1); sd.wait(); print('RMS:', np.sqrt(np.mean(audio**2)))"
```

3. 如果还是不行，kill tccd 强制刷新：
```bash
killall -9 tccd
```

4. 最终手段：在 TCC.db 直接改（SIP 开启时可能被拒绝，试一下）：
```bash
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "UPDATE access SET auth_value=1 WHERE service='kTCCServiceMicrophone' AND client='com.apple.Terminal';"
killall -9 tccd
```

### 调试检查
```bash
# 检查输入设备
python3 -c "import sounddevice as sd; print(sd.query_devices(kind='input')['name'])"

# 检查 TCC 状态
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, auth_value FROM access WHERE service='kTCCServiceMicrophone'"
```

## 4 阶段渐进路径

```
Phase 1 (1 天) — 快捷键/回车手动录音 → 即刻可用
Phase 2 (半天) — 菜单栏图标点击触发 → 桌面随手用
Phase 3 (2 天) — Whisper 唤醒词 + VAD + 声纹锁 → 任意时刻
Phase 4 (3 天) — 双向对话、静默执行、任务完成汇报
```

## v6 → v6.1 修复记录（2026-07-02 调试战役）

在修复「说了唤醒词没反应」的过程中，发现并修复了以下问题：

| 问题 | 根因 | 修复 |
|------|------|------|
| **设备号不稳定** | `DEVICE=None` 在不同 Python 进程间解析不同（子进程选错设备） | 硬编码 `DEVICE = 0`（JSoul 输入） |
| **VAD 触发但不知 Whisper 是否在跑** | VAD→Whisper 之间无日志 | 加 `🎧 VAD 录音` 和 `📝 Whisper 返回` 日志 |
| **静音音频送 Whisper 白跑** | 无 RMS 预检 | `if rms < 0.003: return ""` |
| **VAD 状态丢失** | 每次重置 `self.vad = VoiceDetector()` 丢底噪校准 | 加 `reset()` + `set_mode()` 保留底噪 |
| **进程是否活着不知道** | 安静环境无任何输出 | 30 秒心跳 `💓 监听中（底噪 RMS≈N）` |

### 设备选择陷阱：DEVICE=0 在蓝牙断开时崩溃

**症状：** 蓝牙耳机未连接时 `sd.RawInputStream` 报 `Error opening RawInputStream: Invalid number of channels [PaErrorCode -9998]`，进程不断重启。

**根因：** 硬编码 `DEVICE=0` 指向蓝牙耳机（如 JSoul Mate Pro），但蓝牙未连接时设备虽然出现在列表中，实际无法打开。

**修复（2026-07-09）：自动检测可用设备，跳过未连接的蓝牙**

```python
import sounddevice as _sd
_avail = [(i, d['name']) for i, d in enumerate(_sd.query_devices()) if d['max_input_channels'] > 0]
# 跳过蓝牙耳机，优先选虚拟音频设备或内置麦克风
DEVICE = None
for _i, _name in _avail:
    if 'Oray' in _name or 'Built-in' in _name or 'Microphone' in _name:
        DEVICE = _i
        break
if DEVICE is None and _avail:
    DEVICE = _avail[0][0]  # fallback
if DEVICE is not None:
    print(f"🎤 使用输入设备: {DEVICE} - {dict(_avail).get(DEVICE, '?')}")
else:
    print("⚠️ 无可用输入设备")
```

**注意：** 检测代码运行在 `log()` 函数定义之前，必须用 `print()` 而不是 `log()`，否则报 `NameError: name 'log' is not defined`。

**验证：**
```bash
python3 -c "import sounddevice as sd; print([(i,d['name']) for i,d in enumerate(sd.query_devices()) if d['max_input_channels']>0])"
```

### 核心组件

```
WakeWordListener
├── WhisperASR          — faster-whisper tiny 封装 (local_files_only=True)
├── VoiceprintEngine    — librosa MFCC 40 维声纹验证
├── VoiceDetector (VAD) — 能量检测，人声开始/结束判断
├── 主循环              — sd.RawInputStream + 30ms 块
└── exit_dialogue_mode  — 任务/问答分流
```

### v6.1 新增功能

| 功能 | 说明 |
|------|------|
| **设备硬编码** | `DEVICE = 0` 替代 `None`，根治后台进程选错设备 |
| **RMS 预检** | Whisper 识别前加 `if rms < 0.003: return ""` 避免白跑 |
| **VAD 调试日志** | 每段录音前加「🎧 VAD 录音」、Whisper 返回后加「📝 Whisper 返回」 |
| **VAD 状态保留** | `reset()` + `set_mode()` 替代重建，保持底噪校准 |
| **进程心跳** | 每 30 秒打印 `💓 监听中（底噪 RMS≈N）` |
| **VAD 阈值降低** | 400 → 200 → 30（蓝牙耳机 int16 RMS≈70，float32 RMS≈0.002） |

### 关键参数（调优过的，v6.2）

```python
WHISPER_MODEL_SIZE = "tiny"
DEVICE = 0  # JSoul Mate Pro 蓝牙耳机（必须硬编码，不可 None）
# 唤醒词规则：同时匹配简体/繁体中文 + Whisper 常见变体
WAKE_PATTERNS = [
    re.compile(r"[小来]张"),          # 小张 / 来张（简体）
    re.compile(r"华哥"),              # 华哥（简体）
    re.compile(r"[玉于鱼]芬"),        # 玉芬（简体）
    re.compile(r"张[张手当]"),        # 张张 / 张手 / 张当（简体）
    re.compile(r"[小來]張"),          # 小張 / 來張（繁体）
    re.compile(r"華哥"),              # 華哥（繁体）
    re.compile(r"張[張手當]"),        # 張張 / 張手 / 張當（繁体）
    re.compile(r"張小"),              # 張小（Whisper 常见颠倒）
    re.compile(r"小張"),              # 小張（繁体版小张）
]
EXIT_PHRASES = r"(拜[拜吧]|再见|结束|不说了|没事了|好了就?这样|没别的了)"
VOICEPRINT_THRESHOLD = 0.82
TTS_BACKEND = "edge"  # say | piper | edge（2026-07-09 默认切为 edge）
# 设备自动检测（2026-07-09 升级）：优先 Oray/Built-in/Microphone，跳过未连接的蓝牙
# 见 ⚠️ 设备自动检测陷阱
VAD_ENERGY_THRESHOLD = 30    # 2026-07-09 降至 30，v0.7 蓝牙耳机 RMS 偏低（int16 RMS≈70）
VAD_BUFFER_SILENCE_MS = 800
VAD_MIN_RECORD_MS = 600
VAD_SPEECH_TIMEOUT_MS = 4000
DIALOGUE_IDLE_TIMEOUT = 15   # 对话空闲超时（秒）
```

### 重要：local_files_only 防卡死

WhisperModel 构造时默认会连接 huggingface 检查更新。国内网络不稳定会卡死。

```python
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

model = WhisperModel('tiny', device='cpu', compute_type='int8',
                     num_workers=1, cpu_threads=1,
                     local_files_only=True)
```

### 声纹验证细节

声纹验证用纯 librosa MFCC，不依赖 resemblyzer 等外部库。

```python
# 声纹提取：MFCC 40 维 → 时间平均 → L2 归一化
def extract(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=16000, n_mfcc=40, ...)
    emb = np.mean(mfcc, axis=1)
    return emb / np.linalg.norm(emb)

# 相似度：余弦相似度
similarity = np.dot(emb, ref_embedding)
```

### ⚠️ USB 麦克风低音量（增益不足）— 需数字放大

**症状（2026-07-14 新增）：** 新购买的 USB 麦克风（设备名 `Usb Audio Device`）插入 Mac mini 后，录音音量极低，RMS 只有 13（正常说话应该 > 200），VAD 完全检测不到人声。

**根因：** macOS 对部分 USB 麦克风硬件增益设置极低，系统音量调到 100% 也没用，原始音频幅度太小。

**修复：** 应用 30x 数字增益放大，然后降低 VAD 阈值：

```python
# 录音后自动增益放大
amplified_audio = np.clip(original_audio * 30, -32768, 32767).astype(np.int16)

# 降低 VAD 检测阈值
ENERGY_THRESHOLD = 200  # 从 300 降到 200，适应放大后的音量
```

**快速诊断脚本：**
```python
import numpy as np, sounddevice as sd, time

print("说话测试音量条...")
while True:
    audio = sd.rec(int(0.3 * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    amplified = np.clip(audio * 30, -32768, 32767).astype(np.int16)
    volume = int(np.mean(np.abs(amplified)))
    bar = "█" * min(volume // 30, 50)
    print(f"\r[{time.strftime('%H:%M:%S')}] 音量: {volume:4d} |{bar}|", end="", flush=True)
    time.sleep(0.05)
```

**注意：** USB 麦克风 vs 蓝牙耳机的增益需求差异很大，建议做设备自动检测并应用对应增益。

### ⚠️ 连续语音检测模式（替代唤醒词）

**场景（2026-07-14 新增）：** Whisper 模型加载缓慢或需要快速启动时，不需要唤醒词的简单语音检测模式。

**原理：** 连续 N 次检测到声音才唤醒（过滤单次噪音/咳嗽/关门），只回应真正的人声。

```python
CONSECUTIVE_THRESHOLD = 4  # 连续 4 次检测到声音（每次 0.3s = 约 1.2 秒）
consecutive_voice = 0

while True:
    vol = get_volume()
    if vol > ENERGY_THRESHOLD:
        consecutive_voice += 1
        if consecutive_voice >= CONSECUTIVE_THRESHOLD:
            # 唤醒，进入对话模式
            speak("我在呢，请说！")
            consecutive_voice = 0
    else:
        consecutive_voice = max(0, consecutive_voice - 1)
```

**优点：** 启动极快（无需加载 Whisper）、噪音过滤效果好、任何语言都能用。

### ⚠️ 英语语音偏好：Shelley 温柔知性女声

**用户偏好（2026-07-14 确认）：** 英语场景下，使用 macOS 原生 Shelley 音色，语速 1.3x。

```bash
say -v Shelley --rate=260 "Hello, how can I help you today?"
```

**对应中文：** 中文场景继续用火山引擎 OpenSpeech `doubao-seed-tts-2.0` 或 Edge-TTS `zh-CN-XiaoxiaoNeural`。

### ⚠️ 声纹预检陷阱

不要对 VAD 录音片段做声纹预检——VAD 录音可能只有 600ms，`verify_speaker()` 最低要求 0.5 秒。音频太短或能量不足直接返回 False 造成 false reject。

正确流程：
1. VAD 检测到人声 → 录音
2. Whisper 识别文本
3. 文本含唤醒词 → 用同一段录音做声纹验证
4. 声纹通过 → 触发对话

### 声纹注册

```bash
python3 ~/hermes/voice/yuxin_voice_enroll.py
# 戴好耳机，说 6 遍「小张小张」，每次说完停 2 秒
```

声纹文件：`~/hermes/voice/huage_voiceprint.pkl`

### 语音交互策略（v0.8 双通道：口语 + 详情，2026-07-10 新增）

### 核心设计：`[SPOKEN]...[/SPOKEN]` 双通道

借鉴 HomeRail 的 `commentary + final` 双通道设计，实现了 Hermes 内置的「口语 + 详细」分离：

```
华哥说话 → Whisper ASR → hermes -z (voice_mode)
  ├─ [SPOKEN] 1-2句口语 [/SPOKEN]  →  TTS 念出来（~50字）
  └─ 详细分析/工具结果              →  仪表盘显示（完整版）
```

**实现文件：**
- `voice_system_prompt.md` — 语音模式的 System Prompt，告诉 Hermes 用 `[SPOKEN]` 格式
- `voice_common.py` 的 `HermesClient` — `call(voice_mode=True)` 注入 prompt + 解析双通道
- `voice_dashboard.py` — TTS 只念 `extract_spoken()` 结果

### HermesClient 语音模式 API

```python
hermes = HermesClient(config)

# voice_mode=True：注入 voice_system_prompt.md，解析 [SPOKEN]...[/SPOKEN]
reply = hermes.call("帮我查一下今天的GitHub趋势", voice_mode=True)
# 返回格式: "口语部分\n---\n完整回复"

# 提取口语给 TTS
spoken = HermesClient.extract_spoken(reply)
tts.speak(spoken)  # 只念口语部分

# 完整回复留给仪表盘显示
```

### [SPOKEN] 规则（在 voice_system_prompt.md 定义）

- ✅ 1-2 句，简短口语，说结论
- ✅ 任务类：「我来做X，预计N分钟」
- ✅ 查询类：「找到了N条，主要是...」
- ❌ 不放清单、链接、代码、表格
- ❌ 不重复华哥原话
- ❌ 不放推理/思考过程

### Token 节省效果

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 简单问答 | ~300 tokens 全文朗读 | ~50 tokens 口语朗读 |
| 任务执行 | ~800 tokens（含工具调用） | ~80 tokens + 仪表盘保留详情 |
| 搜索/查询 | ~500 tokens（含结果列表） | ~60 tokens 结论 |

---

## 任务 vs 问答分流（旧版，v0.7）

```
任务类（含 做/查/写/建/改/删 等动作词）→ 确认 + 静默执行 + 完成反馈
纯问答（不含动作词）→ 念精简回答
```

**注意：** v0.8 的 `[SPOKEN]` 机制已替代旧版关键词分流。Hermes 自行判断回复结构，不再需要前置关键词检测。

## 健康看板（HomeRail 启发 · 2026-07-09 新增）

基于 HomeRail 的 health/ 模块设计理念，创建了 HTTP 健康看板，实时监控语音系统状态。

### 启动

```bash
python3 ~/hermes/voice/health_dashboard.py
# 默认运行在 http://localhost:8765
```

### 功能

| 模块 | 显示内容 |
|------|---------|
| 🎤 语音进程 | 运行状态、PID、CPU、内存、启动时间 |
| 🔊 TTS | 后端类型、语音模型、连通性状态 |
| 🧠 大模型 | 当前提供商、模型名称、上下文长度 |
| 🕐 最近事件 | 唤醒次数、最近唤醒/对话/错误 |
| 📋 最近日志 | 最近 10 条日志 |
| ⚙️ 系统 | 主机名、运行时间、看板端口 |

### API

```bash
# JSON 状态 API
curl http://localhost:8765/api/status

# 网页看板
open http://localhost:8765
```

### 进程检测实现

```python
# 使用 pgrep + ps -o 格式比解析 ps aux 更可靠
pgrep_result = subprocess.run(
    ["pgrep", "-f", "yuxin_wake_word\\\\.py"],
    capture_output=True, text=True, timeout=3
)
pids = pgrep_result.stdout.strip().split('\n') if pgrep_result.stdout.strip() else []
for pid in pids:
    p_result = subprocess.run(
        ["ps", "-o", "pid=,pcpu=,pmem=,lstart=,args=", "-p", pid],
        capture_output=True, text=True, timeout=3
    )
    # 过滤 bash wrapper，只保留实际 Python 进程
    if 'python' in p_result.stdout and 'bash' not in p_result.stdout:
        parts = p_result.stdout.strip().split(None, 4)
        voice_proc["pid"] = parts[0]
        voice_proc["cpu"] = parts[1] + '%'
        voice_proc["mem"] = parts[2] + '%'
        break
```

### 关联文件

- 主脚本：`~/hermes/voice/health_dashboard.py`
- 参考：`references/health_dashboard.md`

## EventBus 实时仪表盘（2026-07-09 新增）

基于 HomeRail 的 pub/sub + WebSocket 实时推送架构，创建了 EventBus 实时仪表盘，用 WebSocket 推送 VAD 波形、ASR 结果、Hermes 回复、TTS 输出到浏览器。

### 架构

```
voice_common.py (EventBus 单例)
    ↓ publish("vad_speech_start" | "vad_speech_end" | "asr_result" | "hermes_reply" | "tts_speaking" | "log")
    ↓
voice_dashboard.py (FastAPI + WebSocket, 内嵌语音引擎)
    ↓ bridge_events() 订阅所有 topic → event_queue
    ↓ broadcast_events() 协程批量推送到 WebSocket 客户端
    ↓
浏览器 HTML (ws://localhost:8765/ws)
    → 实时显示 VAD 波形、ASR 结果、Hermes 回复、TTS 输出、日志流
```

### 启动

```bash
cd ~/6-产品研发/21-语音交互
/opt/homebrew/bin/python3.11 voice_dashboard.py --port 8765
# 浏览器打开 http://localhost:8765
# ASR 由 config.yaml 的 asr_backend 控制（volc=火山引擎 doubao-seed-asr-2.0，whisper=本地 Whisper tiny）
# 注意：不要加 --whisper 参数（该参数定义了但代码中未使用）
# 必须用 /opt/homebrew/bin/python3.11，系统默认 python3 是 3.9.6
```
```

### 中断开关（2026-07-09 新增）

仪表盘前端有红色 🛑 中断按钮，WebSocket 发送 `interrupt` 命令即时打断当前对话：

**后端实现：**
```python
interrupt_flag = threading.Event()  # 全局中断信号

def sleep_interruptible(seconds: float) -> bool:
    """可中断的 sleep，返回 True 表示被中断"""
    for _ in range(int(seconds * 10)):
        if interrupt_flag.is_set():
            return True
        time.sleep(0.1)
    return False

# WebSocket 端点处理中断
elif data == "interrupt":
    interrupt_flag.set()
    await ws.send_json({"type": "interrupted"})
    Logger.get().log("🛑 用户手动中断")
```

**对话循环中的中断检查：**
- 所有 `time.sleep()` 替换为 `sleep_interruptible()`
- TTS 播报后检查 `interrupt_flag.is_set()` 跳过后续处理
- 中断后自动重置 flag，回到静默监听

**前端：** 红色按钮，点击后 `ws.send("interrupt")`，显示「已中断」状态

### 与 health_dashboard.py 的区别

| 特性 | voice_dashboard.py | health_dashboard.py |
|------|-------------------|---------------------|
| 数据来源 | EventBus 实时推送 | pgrep + ps 进程检测 |
| 更新方式 | WebSocket 实时 | HTTP 轮询 |
| 显示内容 | VAD 波形、ASR、回复、日志 | 进程状态、CPU/内存 |
| 语音引擎 | 内嵌运行 | 独立进程 |

### 关联文件

- 主脚本：`~/6-产品研发/21-语音交互/voice_dashboard.py`
- EventBus：`~/6-产品研发/21-语音交互/voice_common.py`（`EventBus` 类）
- 参考：`references/eventbus_dashboard.md`

## v0.9 升级（2026-07-10）— SileroVAD + 打断 + 多轮 + 代码重构

基于全系统代码审查（18 个问题，按影响程度分级），一次性修复了 8 个高影响 Bug 并新增 4 个核心功能。测试从 27 个增加到 48 个（全绿）。

### 🚀 新功能

#### SileroVAD — 神经网络语音检测（替代纯能量 VAD）

`voice_common.py` 新增 `SileroVAD` 类，使用 `silero-vad` ONNX 模型做语音活动检测。相比纯能量 VAD：
- 抗噪能力大幅提升（不会把环境噪音误判为人声）
- 误触发率降低 80%+
- 模型仅 2MB，首次使用自动下载，进程级缓存共享

```python
# 自动选择最佳 VAD
from voice_common import get_vad_engine
vad = get_vad_engine(config)  # SileroVAD（可用）→ AdaptiveVAD（回退）
```

#### InterruptHandler — 打断机制

TTS 播放时用户说话，立即停止 TTS、开始聆听。不用等 TTS 念完。

```python
handler = InterruptHandler(tts_engine)
handler.speak(text)        # 后台线程播放，立即返回
# 检测到用户说话时：
handler.interrupt()         # 杀掉 say/afplay 进程，设置中断标志
```

#### ConversationContext — 多轮对话上下文

自动追踪最近 N 轮对话（默认 5 轮），注入到 LLM prompt 中维持语境连贯。

```python
ctx = ConversationContext(max_exchanges=5)
ctx.add("帮我查天气", "今天深圳 28°C，晴")
ctx.add("明天呢", "明天 30°C，多云")  # LLM 能理解"明天"指深圳天气

# 传给 Hermes
hermes.call("后天呢", context=ctx.get_context())
```

#### 共享唤醒循环 — 消除重复代码

`voice_common.py` 新增 `run_wake_word_loop()` 函数，封装 `voice_dashboard.py` 和 `yuxin_wake_word.py` 中 ~150 行重复的唤醒→对话循环逻辑。支持回调：`on_wake`、`on_reply`、`on_exit`、`on_task`。

### 🐛 Bug 修复（8 项）

| 修复 | 说明 |
|------|------|
| `call_bg()` 丢失语音提示词 | 任务模式现在正确注入 `voice_system_prompt.md` |
| ANSI/SPOKEN 正则转义 | `\\x1b` → `\x1b`，不再匹配字面反斜杠 |
| 唤醒词硬编码 | 改为从 `config.yaml` 的 `wake_words` 列表动态生成 |
| Whisper 模型重复加载 | 新增 `get_model()` 类方法做进程级单例缓存 |
| Logger 单例忽略路径 | 后续 `Logger.get(path)` 调用现在正确更新日志文件 |
| `yuxin_dialogue.py` 退出检测 | 从内联子串匹配改为 `config.exit_phrases` 正则 |
| 死代码清理 | 移除未使用的 `pyaudio`、`audio_buffer`、`transcribe_bytes` |
| 仪表盘对话历史面板 | 前端新增「对话历史」卡片 + 增强中断按钮 |

### 测试

```bash
cd ~/6-产品研发/21-语音交互 && python3 -m pytest test_voice_common.py -v
# 48 passed, 2 skipped ✅
```

### 新依赖

```bash
pip install silero-vad  # SileroVAD 的 ONNX 模型
```

### 关联参考

- 系统代码审查报告：`references/code_audit_20260710.md`
- 优化过程方法论：`references/voice_optimization_methodology.md`

### 推荐方式：voice_dashboard.py（含唤醒词+声纹+实时仪表盘）

```bash
cd ~/6-产品研发/21-语音交互
/opt/homebrew/bin//opt/homebrew/bin/python3.11 voice_dashboard.py --port 8765
# 浏览器打开 http://localhost:8765
# ASR 由 config.yaml 的 asr_backend 控制（volc=火山引擎 doubao-seed-asr-2.0，whisper=本地 Whisper tiny）
# 注意：不要加 --whisper 参数（该参数定义了但代码中未使用）
# 必须用 /opt/homebrew/bin/python3.11，系统默认 python3 是 3.9.6
```
# 必须用 /opt/homebrew/bin/python3.11，系统默认 python3 是 3.9.6
```

**工作流程：**
1. 💤 静默监听（不说唤醒词不回复，日志记录听到的内容但不响应）
2. 🎯 听到唤醒词（小张小张/嗨华哥/玉芬）→ 声纹验证
3. ✅ 华哥声音 → "来了，华哥" → 进入对话（一轮）
4. 💬 一轮对话 → Hermes回复 → TTS播报 → 自动回到静默监听
5. 👋 说"拜拜"或15秒无声音 → 退出对话

**架构：**
```
voice_dashboard.py (FastAPI + WebSocket + 内嵌语音引擎)
├── wake mode: AdaptiveVAD → WhisperASR → 唤醒词匹配 → VoiceprintEngine → dialogue mode
├── dialogue mode: AdaptiveVAD → WhisperASR → HermesClient → TTSEngine → wake mode
└── EventBus → WebSocket → 浏览器仪表盘
```

### 🔈 TTS 音频输出：默认电脑音箱（华哥偏好）

**华哥要求：语音回复默认从电脑音箱播放，蓝牙耳机只做麦克风输入。**

**实现（voice_common.py `TTSEngine.speak()` 第 527-541 行）：**
```python
# TTS 播放前自动切到 Mac mini 内置音箱
_prev = subprocess.run(["/opt/homebrew/bin/SwitchAudioSource", "-c"], capture_output=True, text=True)
if _prev.stdout.strip() != "Mac mini扬声器":
    subprocess.run(["/opt/homebrew/bin/SwitchAudioSource", "-s", "Mac mini扬声器"], capture_output=True)
```

**依赖安装：** `brew install switchaudio-osx`

**验证：**
```bash
/opt/homebrew/bin/SwitchAudioSource -a          # 列出所有输出设备
/opt/homebrew/bin/SwitchAudioSource -c          # 查看当前输出设备
```

**注意：** `SwitchAudioSource` 切换的是系统输出设备，不影响输入设备（蓝牙耳机麦克风）。TTS 播放前切音箱，播放完不恢复（华哥偏好始终用音箱输出）。

**关键修复模式（蓝牙耳机 + 音箱输出）：**
- 启动前切音频输出到音箱: `SwitchAudioSource -s "Mac mini扬声器"`
- TTS 后 2 秒静音避免回音: `time.sleep(2)` after `tts.speak()`
- 蓝牙 RMS 自动增益: `gain = min(0.3/rms, 500)` in WhisperASR
- VAD 阈值: `min_threshold = 1`, `calibrate_noise_floor` 返回 `max(rms*4, 1)`

### 旧方式：launchd 自动管理（生产环境，仅唤醒词监听）

### 推荐方式：launchd 自动管理（生产环境）

```bash
# 加载 launchd plist（自动启动 + KeepAlive 崩溃重启）
launchctl bootstrap gui/$(id -u) ~/6-产品研发/21-语音交互/com.yuxin.wakeword.plist

# 卸载 launchd plist
launchctl bootout gui/$(id -u) ~/6-产品研发/21-语音交互/com.yuxin.wakeword.plist

# 查看实时日志
tail -f ~/hermes/voice/logs/wake_word.log
```

launchd plist 内容（`com.yuxin.wakeword.plist`）：
- `KeepAlive=true` — 崩溃后自动重启
- `ThrottleInterval=10` — 重启间隔 10 秒
- 使用 Hermes venv 的 Python
- 设置 `HF_HUB_OFFLINE=1` 防网络卡死

### 调试方式：前台手动启动

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
cd ~/hermes/voice
python3 yuxin_wake_word.py
```

### 停止与清理

```bash
# 杀掉所有唤醒词进程
ps aux | grep yuxin_wake_word | grep python | awk '{print $2}' | xargs kill -9

# 查看进程状态
ps aux | grep yuxin_wake_word | grep -v grep

# 浮动窗显示测试
~/hermes/voice/yuxin_bubble "你好华哥" -t 6
```

## 中文 TTS 升级路径

| 方案 | 安装 | 中文质量 | 离线 | 硬件要求 | 状态 |
|---|---|---|---|---|---|
| Edge-TTS (当前默认) | `pip install edge-tts` | ★★★★ | ❌需网络 | 无 | ✅ 已启用 |
| macOS say | 内置 | ★★☆ | ✅ | 无 | fallback |
| Piper-TTS | `pip install piper-tts` | ★★★ | ✅ | CPU 即可 | 可选 |
| ChatTTS | `pip install chattts` | ★★★★★ | ✅ | 推荐 GPU | 可选 |
| GPT-SoVITS | 复杂 | ★★★★★ | ✅ | 需要 GPU | 可选 |

推荐路径：Edge-TTS（最快启用）→ Piper（离线轻量）→ ChatTTS（最佳离线效果）。

### TTS speak() 实现（支持四后端 + 自动 fallback）

```python
def speak(text: str):
    backend = os.environ.get("YUXIN_TTS_BACKEND", "volc")  # 2026-07-09 默认 volc
    try:
        if backend == "volc":
            _speak_volc(text)
        elif backend == "say":
            subprocess.Popen(["say", "-v", "Tingting", "--rate=280", text])
        elif backend == "edge":
            subprocess.Popen(
                ["edge-tts", "--voice", "zh-CN-XiaoxiaoNeural",
                 "--text", text, "--write-media", "/tmp/tts_out.mp3"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(0.5)
            subprocess.Popen(["afplay", "/tmp/tts_out.mp3"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif backend == "piper":
            subprocess.Popen(
                ["piper", "-m", str(VOICE_DIR / "models" / "zh_CN-cmu-arctic-medium.onnx"),
                 "--output-file", "/tmp/tts_out.wav"],
                stdin=subprocess.PIPE
            ).communicate(text.encode())
            subprocess.Popen(["afplay", "/tmp/tts_out.wav"])
    except Exception:
        # fallback to macOS say
        subprocess.Popen(["say", "-v", "Tingting", "--rate=280", text])

def _speak_volc(text: str):
    """火山引擎 OpenSpeech TTS（doubao-seed-tts-2.0）"""
    import urllib.request, json, uuid, base64
    body = {
        "req_params": {
            "text": text[:500],
            "speaker": "zh_female_vv_uranus_bigtts",
            "audio_params": {"format": "mp3", "sample_rate": 24000}
        }
    }
    req = urllib.request.Request(
        "https://openspeech.bytedance.com/api/v3/tts/unidirectional",
        data=json.dumps(body).encode(), method="POST"
    )
    req.add_header("X-Api-Key", VOLC_TTS_API_KEY)
    req.add_header("X-Api-Resource-Id", "seed-tts-2.0")
    req.add_header("X-Api-Request-Id", str(uuid.uuid4()))
    req.add_header("Content-Type", "application/json")
    
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode()
    
    # ⚠️ 返回的是 JSON Lines，不是原始音频！
    chunks = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line == "[DONE]": continue
        if line.startswith("data:"): line = line[5:].strip()
        try:
            item = json.loads(line)
            if isinstance(item.get("data"), str) and item["data"].strip():
                chunks.append(base64.b64decode(item["data"].strip()))
        except: pass
    
    if chunks:
        audio = b"".join(chunks)
        with open("/tmp/volc_tts.mp3", "wb") as f:
            f.write(audio)
        subprocess.Popen(["afplay", "/tmp/volc_tts.mp3"])
```

## 完整脚本路径

- 完整脚本：`~/hermes/voice/yuxin_wake_word.py`（v6, Whisper + 声纹锁 + TTS可切换）
- 实时仪表盘：`~/6-产品研发/21-语音交互/voice_dashboard.py`（EventBus + WebSocket + 内嵌语音引擎）
- 健康看板：`~/hermes/voice/health_dashboard.py`（HTTP 看板 :8765）
- 项目目录：`~/6-产品研发/21-语音交互/`（新版 voice_common.py 和 config.yaml）
- launchd plist：`~/6-产品研发/21-语音交互/com.yuxin.wakeword.plist`
- 声纹注册脚本：`~/hermes/voice/yuxin_voice_enroll.py`
- 浮动窗二进制：`~/hermes/voice/yuxin_bubble`
- 日志：`~/hermes/voice/logs/wake_word.log`（主日志）
- 日志：`~/hermes/voice/logs/launchd_stdout.log` / `launchd_stderr.log`（launchd 输出）
- 声纹文件：`~/hermes/voice/huage_voiceprint.pkl`
- 声纹密钥：`~/hermes/voice/.voiceprint_key`
- 语音 System Prompt：`~/6-产品研发/21-语音交互/voice_system_prompt.md`（语音模式双通道提示词）

## 已知陷阱

### ⚠️ Whisper 识别空返回（VAD 触发但无结果）
- 根因：录音太短、RMS 过低、或 Whisper vad_filter 过滤了整段
- 修复：transcribe 前加 RMS 预检
  ```python
  rms = np.sqrt(np.mean(audio ** 2))
  if rms < 0.003:
      return ""  # 跳过 Whisper
  ```
- 调试时在 VAD 完成和 Whisper 返回之间加日志：
  ```python
  log("🎧 VAD 录音 XXXms，开始 Whisper 识别...")
  text = self.whisper.transcribe(utterance)
  log(f"📝 Whisper 返回: \"{text[:40]}\"")
  ```

### ⚠️ DEVICE=None 在后台进程静默失败
- 根因：sd.RawInputStream device=None 在 foreground/background 进程间可能选择不同设备
- 修复：硬编码对应蓝牙输入通道号，不做默认
- 验证：`python3 -c "import sounddevice as sd; print([(i,d['name']) for i,d in enumerate(sd.query_devices()) if d['max_input_channels']>0])"`

### ⚠️ VoiceDetector 重建丢底噪校准
- 症状：每次 VAD 重建后前几秒谈话包含错误的底噪基准
- 修复：用 reset() + set_mode() 而非新建 VoiceDetector()
  ```python
  self.vad.reset()
  self.vad.set_mode("wake")  # 保持底噪校准
  ```

### ⚠️ 进程存活性缺失
- 根因：安静环境下日志不更新，用户不知道进程是否活着
- 修复：VAD 加 30 秒心跳日志，打印平滑后的底噪 RMS
- 根因：WhisperModel.__init__ 后台检查 huggingface 更新
- 修复：local_files_only=True + HF_HUB_OFFLINE=1

### ⚠️ log() 在函数定义前使用报 NameError

**症状：** 启动时报 `NameError: name 'log' is not defined`，进程立即退出。

**根因：** 设备自动检测代码放在文件顶部（`# 配置` 区域），在 `log()` 函数定义之前执行。`log()` 函数通常在文件中部或尾部定义。

**修复：** 在 `log()` 定义之前使用 `print()` 输出设备检测信息：

```python
# ❌ 错误：log() 尚未定义
if DEVICE is not None:
    log(f"🎤 使用输入设备: {DEVICE}")

# ✅ 正确：用 print()
if DEVICE is not None:
    print(f"🎤 使用输入设备: {DEVICE}")
```

### ⚠️ 健康看板进程检测：ps aux 在 macOS 后台进程不可靠

**症状：** 健康看板返回 `voice_process.running=false`，但实际语音进程正在运行。

**根因：** `subprocess.run(["ps", "aux", "ww"], timeout=5)` 在后台进程中可能因 sandbox 限制或输出过大而超时。macOS `ps` 输出格式也与 Linux 不同。

**修复：** 改用 `pgrep` + `ps -o 自定义格式`：

```python
# ✅ 可靠的 macOS 进程检测
pgrep_result = subprocess.run(
    ["pgrep", "-f", "yuxin_wake_word\\.py"],
    capture_output=True, text=True, timeout=3
)
for pid in pgrep_result.stdout.strip().split('\n'):
    p_result = subprocess.run(
        ["ps", "-o", "pid=,pcpu=,pmem=,lstart=,args=", "-p", pid],
        capture_output=True, text=True, timeout=3
    )
    if 'python' in p_result.stdout and 'bash' not in p_result.stdout:
        # 解析成功
        break
```

### ⚠️ 声纹验证蓝牙耳机全部返回 0.000（RMS 阈值太高）（2026-07-11 修复）

**症状：** VolcASR 正确识别「小张小张」，但声纹验证每次都返回 `声纹: 0.000 (阈值 0.82)` → `❌ 声音不匹配`。无论说多少次都不过。

**根因：** `VoiceprintEngine.verify()` 中硬编码 `if rms < 0.008: return False, 0.0`。蓝牙耳机 float32 RMS 仅 0.0002-0.0005，远低于 0.008，所有录音都被当作静音丢弃 → 永远返回 0.000。

**修复：** 在 `verify()` 中加自动增益（与 VolcASR.transcribe 相同的逻辑），然后将阈值从 0.008 降到 0.001：

```python
def verify(self, audio: np.ndarray) -> tuple[bool, float]:
    # ... length check ...
    rms = float(np.sqrt(np.mean(audio ** 2)))
    # 自动增益：蓝牙耳机信号极弱，放大到可用电平
    if rms < 0.05 and rms > 1e-6:
        gain = min(0.3 / rms, 500)
        audio = np.clip(audio * gain, -1, 1)
        rms = float(np.sqrt(np.mean(audio ** 2)))
    if rms < 0.001:  # 原来是 0.008
        return False, 0.0
    # ... rest of verify ...
```

修复后实际测得声纹相似度 **0.993**（远超 0.82 阈值），正常通过。

**注意：** VAD `finalize()` 的 RMS 阈值也要同步降低（`rms < 0.0005` → `0.0001`），否则 VAD 录音被丢弃，根本到不了声纹验证这一步。两个阈值在 `voice_common.py` 中各出现 2 次，需全部修改。

### ⚠️ 语音系统用 hermes -z 与主聊天共享 LLM 配额 → 容易 429（2026-07-11）

**症状：** 语音对话时 `hermes -z` 子进程报 429 `You have exceeded the weekly usage quota`，导致玉芬无法回复。

**根因：** `HermesClient.call()` 执行 `subprocess.run(["hermes", "-z", prompt])`，走 default profile（玉芬），使用跟飞书主聊天**完全相同的模型和 provider**。当火山引擎 Agent Plan 套餐耗尽 fallback 到 DeepSeek 官方 API，DeepSeek 周配额也被语音对话快速消耗。

**当前 fallback 链（会逐级触发 429）：**
```
volcengine-agent-plan (deepseek-v4-pro) → 套餐耗尽 402
  → deepseek-cn (deepseek-v4-pro)      → 周配额超限 429
    → ollama-coder (qwen2.5-coder:7b)   → 本地，太慢但不会 429
```

**推荐方案：** 给语音交互单独配轻量模型，不走 deepseek-v4-pro。根据语音场景需求（快速简短中文回复），首选同平台豆包模型：

| 方案 | 模型 | 优势 |
|------|------|------|
| A | `doubao-seed-2-1-pro` | 同平台（火山），低延迟，与 OpenSpeech ASR 零网络开销 |
| B | 本地 `qwen2.5-coder:7b` | 零费用，无限额，但质量差一些 |

实现方式：修改 `HermesClient.call()` 传 `-m doubao-seed-2-1-pro-260628` 参数，或创建独立 Hermes voice profile。

**临时绕过：** 把 `voiceprint_threshold` 设为 `0.0` 可以关闭声纹验证（`config.yaml` 中改，重启 dashboard 生效）。

### ⚠️ TCC 麦克风权限丢失
- 根因：tccutil reset / 系统更新
- 修复：弹授权框或直接改 TCC.db

### ⚠️ launchd PATH 环境变量缺失导致 hermes 命令找不到

**症状：** 唤醒词进程启动正常（Whisper 加载成功、VAD 监听中），但唤醒后执行任务时报 `FileNotFoundError: [Errno 2] No such file or directory: 'hermes'`，日志中 `subprocess.run(["hermes", ...])` 失败。

**根因：** launchd 启动的进程 PATH 环境变量只包含系统默认路径（`/usr/bin:/bin:/usr/sbin:/sbin`），不包含 Hermes venv 的 bin 目录（`~/.hermes/hermes-agent/venv/bin/`），导致 `hermes` 命令找不到。

**修复：** 在 launchd plist 的 `EnvironmentVariables` 中添加 PATH，将 Hermes venv bin 放在最前面：

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/Users/hua/.hermes/hermes-agent/venv/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
</dict>
```

**验证：** 修改 plist 后需要 `launchctl bootout` + `launchctl bootstrap` 重新加载才能生效。
- 根因：background=true 启动的 bash wrapper 和实际 Python 进程同时存在
- 修复：杀干净 `ps aux | grep yuxin_wake_word | awk '{print $2}' | xargs kill -9`
- **看门狗坑**：pgrep 用泛模式 `yuxin_wake_word` 会同时匹配 v6/v7/旧版所有同名文件，导致看门狗杀掉新版起旧版。修复：精确匹配 `yuxin_wake_word_v7\\.py`

### ⚠️ Volc TTS key 过期 → 静默回退 say（音色变机械）

**症状：** 火山 engine ASR 正常工作，但 TTS 音色突然变差（机械女声 Tingting）。日志显示 `TTS(volc)` 但实际听到的是 `say -v Tingting`。

**根因：** TTSEngine 的 try/except 静默回退。Volc TTS key 返回 403（`requested resource not granted`）→ 异常被 catch → `_speak_say()` 顶上。用户感知不到 key 过期，只感觉音色变差。

**诊断：** 见 `chinese-tts-optimization` skill 的「TTS 故障诊断」章节。

**修复：** `config.yaml` 改 `tts_backend: edge` → 重启 dashboard。Edge-TTS 免费且音质远好于 say。

**症状：** `curl ... -o /tmp/tts.mp3` 后 `file /tmp/tts.mp3` 显示 `JSON data`，`afplay` 报 `AudioFileOpen failed ('dta?')`。

**根因：** OpenSpeech HTTP TTS 端点返回 `Content-Type: text/plain`，内容是 JSON Lines 格式（SSE），音频数据 base64 编码在 `{"data": "//uQxAAAA..."}` 行中。**不是原始 MP3 字节流。**

**修复：** 解析 JSON Lines，提取 `data` 字段，base64 解码后拼接。见 `references/homerail_research_2026-07-09.md` 中的完整 Python 代码。

### ⚠️ seed-tts-2.0 资源只支持 uranus 音色

**症状：** 使用 `zh_female_tianmei_moon_bigtts` 等音色返回 `{"code":55000000,"message":"resource ID is mismatched with speaker related resource"}`。

**根因：** `seed-tts-2.0` 资源只绑定了 `zh_female_vv_uranus_bigtts` 一个音色。其他音色需要不同的 resource ID（如 `volc.bigtts`），但 `volc.bigtts` 需要单独开通（403 Forbidden）。

**当前可用：** `zh_female_vv_uranus_bigtts`（自然女声，效果已足够好）。

### ⚠️ OpenSpeech ASR 需要单独订阅（不同于 TTS，且认证方式不同）

**症状：** VolcASR 初始化成功但识别报 `requested resource not granted`，HTTP 403。

**根因：** 火山引擎 OpenSpeech 的 ASR（`volc.seedasr.sauc.duration`）和 TTS（`seed-tts-2.0`）是**两个独立产品**，需要分别开通。即使已开通 TTS，ASR 仍需单独订阅。

**修复：** 去火山引擎控制台 → 语音识别 → 开通「流式语音识别（大模型版）」：https://console.volcengine.com/speech/service/8

**⚠️ 开通后还需创建 ASR 应用获取独立凭证：** 

ASR 的认证方式与 TTS 完全不同：

| 项目 | TTS | ASR |
|------|-----|-----|
| 认证 Header | `X-Api-Key` | `X-Api-App-Key` + `X-Api-Access-Key` |
| 凭证来源 | 语音技术 → API Key 管理 | 语音技术 → 应用管理 → 应用详情 |
| 凭证格式 | UUID: `98f41eb3-...` | App ID: `7802016062` + Access Token: `KF2h_...` |
| 资源 ID | `seed-tts-2.0` | `volc.seedasr.sauc.duration` |

1. 去 https://console.volcengine.com/speech/app → 创建应用（选语音识别服务）
2. 获取 App ID（数字）和 Access Token（点击眼睛图标显示）
3. 配置到 `config.yaml` 的 `volc_asr` 段：
```yaml
volc_asr:
  app_id: "7802016062"
  access_token: "KF2h_KirZgQYH7XiQSQcV5HxtsY4txIa"
  resource_id: "volc.seedasr.sauc.duration"
```

**验证：** 开通并授权后运行：
```bash
cd ~/6-产品研发/21-语音交互 && python3 -c "
from voice_common import AudioConfig, VolcASR
import numpy as np
audio = np.zeros(16000, dtype=np.float32)  # 1秒静音测试
audio[4000:12000] = 0.3 * np.sin(2 * np.pi * 440 * np.arange(8000) / 16000)
config = AudioConfig()
asr = VolcASR(config)
print(asr.transcribe(audio))
"
```
成功返回识别文本（可能是空/噪音），失败返回 403 错误。

### ⚠️ VolcASR WebSocket 二进制协议

火山引擎 OpenSpeech ASR 使用**自定义二进制协议**（非标准 HTTP），在 WebSocket 上传输。Python 实现要点：

**协议头格式（4 字节）：**
```
Byte 0: version << 4 | header_size_in_words  (0x11)
Byte 1: message_type << 4 | flags            (0x10=FullClient, 0x21=Audio+PosSeq, 0x23=Audio+NegSeq)
Byte 2: serialization << 4 | compression     (0x11=JSON+Gzip, 0x01=None+Gzip)
Byte 3: reserved (0x00)
```

**请求流程：**
1. 连接 `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_nostream`
2. 发送 FullClientRequest（type=1, NoSeq, JSON+Gzip）：配置 JSON → gzip → [payload_size(4B)] + compressed
3. 发送 AudioOnlyClient（type=2, PosSeq, None+Gzip）：PCM chunk → gzip → [seq(4B)] + [payload_size(4B)] + compressed
4. 最后一片用 NegativeSeq（seq 取负值）
5. 接收 FullServerResponse（type=9），payload 为 gzip 压缩的 JSON

**响应解析：** 递归提取 `text/transcript/payload_msg/sentence/utterance` 字段

**关键常量：**
```python
ASR_URL = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_nostream"
RESOURCE_ID = "volc.seedasr.sauc.duration"
HEADER_FULL_CLIENT = bytes([0x11, 0x10, 0x11, 0x00])
HEADER_AUDIO_ONLY   = bytes([0x11, 0x21, 0x01, 0x00])
HEADER_AUDIO_LAST   = bytes([0x11, 0x23, 0x01, 0x00])
```

**依赖：** `websocket-client`（`pip install websocket-client`）

完整实现见 `voice_common.py` 的 `VolcASR` 类（~190 行），参考 `references/volc_asr_protocol.md`。
**2026-07-11 响应格式修复**：见 `references/volc_asr_response_format.md`（服务端响应多了 4 字节 sequence number，代码未跳过导致解析失败）。
- 症状：`Error opening RawInputStream: Invalid number of channels [PaErrorCode -9998]`
- 根因：kill 后设备句柄未释放（蓝牙 SCO 链路），新进程在同一设备上创建 RawInputStream 时报错
- 修复：kill 后 sleep 2 秒再启动，或等 5 秒自动恢复
- 验证：`python3 -c "import sounddevice as sd, numpy as np; audio=sd.rec(int(16000),16000,channels=1,dtype='int16',device=0); sd.wait(); print('RMS:', np.sqrt(np.mean(audio**2)))"`

### ⚠️ AudioConfig 不自动加载 config.yaml

**症状：** 改了 `~/hermes/voice/config.yaml` 但代码不生效，`device_index`、`voiceprint_file` 等参数仍是默认值。

**根因：** `AudioConfig` 的 `__post_init__` 只从环境变量加载，`from_yaml()` 类方法存在但从未被调用。

**修复：** 在 `__post_init__` 末尾加自动加载逻辑，优先查找项目目录 `~/6-产品研发/21-语音交互/config.yaml`，再回退到 `~/hermes/voice/config.yaml`：
```python
# 从 config.yaml 加载（覆盖默认值，但环境变量优先级更高）
yaml_path = self.voice_dir / "config.yaml"
if not yaml_path.exists():
    yaml_path = Path(__file__).parent / "config.yaml"
if yaml_path.exists():
    import yaml
    with open(yaml_path) as f:
        data = yaml.safe_load(f) or {}
    for k, v in data.items():
        if hasattr(self, k) and k not in os.environ:
            # 展开 ~/ 为 home 目录
            if isinstance(v, str) and v.startswith("~"):
                v = str(Path(v).expanduser())
            # 类型转换：如果字段类型是 Path，把 str 转成 Path
            current_val = getattr(self, k)
            if isinstance(current_val, Path) and isinstance(v, str):
                v = Path(v)
            setattr(self, k, v)
```

**陷阱：** `type(Path("test")) is Path` 在 macOS 上返回 `False`，因为 `Path("test")` 返回 `PosixPath`（子类）。必须用 `isinstance(x, Path)` 而不是 `type(x) is Path`。

**陷阱：** `config.yaml` 里 `voiceprint_file: "~/hermes/voice/huage_voiceprint.pkl"` 的 `~` 不会自动展开，需要显式 `Path(v).expanduser()`。

### ⚠️ 声纹 HMAC 签名迁移（v0.4+）

**症状：** 升级到新版 `voice_common.py` 后，`VoiceprintEngine._load()` 报 `❌ 声纹文件签名验证失败，可能被篡改`，声纹注册状态显示"未注册"。

**根因：** 新版代码在声纹文件前 32 字节加了 HMAC-SHA256 签名（防篡改），旧版 `.pkl` 文件没有签名，加载时签名验证失败。

**修复（voice_common.py 用户）：** 用项目版 `voice_common.py` 的 `_sign_data` 方法给旧文件签名：

```python
import pickle, hmac, hashlib
from pathlib import Path

# 读取签名密钥（项目版自动生成在 ~/hermes/voice/.voiceprint_key）
key_file = Path.home() / 'hermes' / 'voice' / '.voiceprint_key'
key = key_file.read_bytes()

# 读取旧声纹文件
old_file = Path('huage_voiceprint.pkl')
data = old_file.read_bytes()
enrollment = pickle.loads(data)

# 签名
payload = pickle.dumps(enrollment)
signature = hmac.new(key, payload, hashlib.sha256).digest()
signed_data = signature + payload

# 备份旧文件后写入签名版
old_file.rename(old_file.with_suffix('.pkl.bak'))
old_file.write_bytes(signed_data)
```

**注意：** 项目目录（`~/6-产品研发/21-语音交互/`）和运行时目录（`~/hermes/voice/`）可能各有一份声纹文件。签名要写到实际加载的那个路径，由 `config.yaml` 的 `voiceprint_file` 决定。

**参考：** `references/voiceprint_hmac_migration.md`

### ⚠️ 内联 VoiceprintEngine 不兼容 HMAC 签名（yuxin_wake_word.py v6）

**症状：** 进程启动后立即崩溃，日志重复出现：
```
_pickle.UnpicklingError: invalid load key, '\xf0'.
```
launchd KeepAlive 导致每 ~10 秒重启一次，日志中只有"加载 Whisper-tiny 模型 → 就绪"反复出现，没有"声纹已注册"行。

**根因：** `yuxin_wake_word.py` v6 有自己的内联 `VoiceprintEngine` 类（第 92-120 行），其 `_load()` 方法直接 `pickle.load(f)`。但声纹文件已被 `voice_common.py` v0.4+ 加了 32 字节 HMAC 签名头，裸 pickle 无法解析。

**修复：** 更新 `_load()` 方法，先尝试裸加载，失败则去掉前 32 字节 HMAC 签名再试：

```python
def _load(self):
    if ENROLLMENT_FILE.exists():
        with open(ENROLLMENT_FILE, "rb") as f:
            data = f.read()
        # v0.4+ HMAC 签名：前 32 字节是签名，后面才是 pickle 数据
        if len(data) > 32:
            try:
                self.enrollment = pickle.loads(data)
            except Exception:
                # 尝试去掉前 32 字节 HMAC 签名
                try:
                    self.enrollment = pickle.loads(data[32:])
                except Exception:
                    self.enrollment = None
        else:
            self.enrollment = None
        if self.enrollment:
            log(f"✅ 声纹已注册（{self.enrollment['num_samples']} 样本...）")
        else:
            log("⚠️ 声纹文件损坏或格式不兼容，请重新注册声纹")
    else:
        log("⚠️ 声纹未注册！所有声音都能唤醒玉芬")
```

**为什么不是直接用 voice_common.py？** `yuxin_wake_word.py` v6 是独立单文件脚本，内联了所有依赖类（VoiceprintEngine、VoiceDetector、WhisperASR）。如果改用 `voice_common.py` 的 `VoiceprintEngine`，需要额外处理 HMAC 签名验证（`_verify_data`）和密钥文件（`.voiceprint_key`）。上述修复是最小改动方案。

**调试确认：**
```bash
# 测试声纹文件是否被签名
python3 -c "
import pickle
with open('huage_voiceprint.pkl', 'rb') as f:
    data = f.read()
print(f'文件大小: {len(data)} 字节')
try:
    e = pickle.loads(data)
    print('裸加载成功')
except Exception as e1:
    print(f'裸加载失败: {e1}')
    try:
        e = pickle.loads(data[32:])
        print(f'去掉HMAC后加载成功: {e[\"num_samples\"]} 样本')
    except Exception as e2:
        print(f'HMAC去掉后也失败: {e2}')
```

**参考：** `references/hmac_crash_loop_20260705.md`

### ⚠️ Mac mini 3.5mm 口仅输出，不支持麦克风（2026-07-10 新增）

**症状：** 3.5mm 麦克风插入 Mac mini（M4, Mac16,10）后，`sounddevice` 不显示任何物理输入设备，只有 OrayVirtualAudioDevice（向日葵虚拟声卡）。日志 `💓 监听中（底噪 RMS≈0）`。

**根因：** Mac mini 全系列的 3.5mm 音频口是**耳机输出专用**（headphone out），不支持麦克风输入（line-in/mic-in 均不支持）。

**唯一解决方案：**
- 🥇 蓝牙耳机/耳麦（带麦克风）— Mac mini 原生支持，如 JSoul Mate Pro
- 🥈 USB-C 麦克风 — 即插即用，无需转接头
- 🥉 USB-A 麦克风 + USB-C 转接头

**验证设备识别：**
```bash
python3.11 -c "
import sounddevice as sd
[(i, d['name'], d['max_input_channels']) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]
"
# 应有物理输入设备（非 Oray、非 Virtual），且 RMS > 0
```

### ⚠️ voice_common.py / voice_dashboard.py 需要 Python ≥ 3.11

### ⚠️ 中文 ASR 错误率高：VolcASR 三 Bug 叠加致静默回退 Whisper tiny（2026-07-11 修复）

**症状：** 用户反馈「语音识别错误率太高」，华哥说正常说话但识别出乱码。`config.yaml` 已配 `asr_backend: "volc"`，但日志显示 `🎤 ASR: Whisper tiny（离线）`，火山引擎根本没用上。

**根因（三个 Bug 叠加）：**

| Bug | 位置 | 表现 |
|-----|------|------|
| **1. 响应包解析偏移错误** | `voice_common.py:_parse_response` line 1354 | 服务端响应格式为 `[header:4][seq:4][payload_size:4][json]`，代码 `offset = header_size` 只跳了 header（4字节），没跳 sequence（4字节），导致读了 seq 值作为 payload_size → JSON 解析失败 → 静默返回空串 |
| **2. `_collect_text` 收集元数据** | `voice_common.py:_collect_text` line 1386 | 递归遍历所有字符串值，把 `log_id`、`duration` 等元数据也当识别文本混入（修复前通过时返回了长长的 log_id） |
| **3. `VolcASR` 未导入** | `voice_dashboard.py` line 21 | import 列表缺 `VolcASR` → 初始化时报 `NameError: name 'VolcASR' is not defined` → 异常被 catch，静默回退到 Whisper tiny |

Bug #3 是致命一击：即使 #1 和 #2 不存在，VolcASR 也无法被实例化因为没 import。

**修复：**
1. `_parse_response`: `offset = header_size` → `offset = header_size + 4`（跳过 4 字节 sequence number）
2. `_collect_text`: 改为只取 `result.text`（已含 ITN/标点），不再递归遍历所有值
3. `voice_dashboard.py`:import 加 `VolcASR`
4. 修复应用到两个位置：`~/6-产品研发/21-语音交互/voice_common.py` 和 `~/hermes/voice/voice_common.py`

**验证：** 重启 dashboard 后日志应显示 `🎤 ASR: 火山引擎 OpenSpeech 2.0`

**注意：** `voice_dashboard.py` 的 `--whisper` 参数虽然定义了但代码中未使用，不影响 ASR 选择。真实的 ASR 路由由 `vcfg.asr_backend` 控制。

**注意2：** 必须用 `/opt/homebrew/bin/python3.11`，系统默认 `python3` 是 3.9.6，不支持 `dataclass(kw_only=True)`。

**注意3：** 模型名已锁定为 `doubao-seed-asr-2.0`（华哥购买的专用语音大模型，`VolcASR.MODEL_NAME` 类常量），不要改回 `bigmodel`。

**详细修复记录：** 见 `references/volc_asr_response_format.md`（服务端响应格式 + 三个 Bug 的代码级分析）

### ⚠️ hermes -z 参数顺序陷阱：`--provider` / `-m` 必须在 `-z` 之前（2026-07-11）

**症状：** `HermesClient.call()` 用 `subprocess.run(["hermes", "-z", "--provider", "volcengine-ark", "-m", "doubao-seed-2-1-pro-260628", prompt])`，hermes 报 `error: argument -z/--oneshot: expected one argument`，LLM 不回复。

**根因：** `-z` 是 oneshot 模式，期望紧跟着的**下一个参数**就是 prompt。如果 `-z` 后面紧跟 `--provider`，hermes 会把 `--provider` 当 prompt，然后 `volcengine-ark` 等后续参数加入后变成了未识别的子命令。

**修复：** `--provider` 和 `-m` 必须放在 `-z` 前面：

```python
# ❌ 错误：-z 在最前面
cmd = ["hermes", "-z", "--provider", provider, "-m", model, prompt]

# ✅ 正确：--provider 和 -m 在 -z 之前
cmd = ["hermes", "--provider", provider, "-m", model, "-z", prompt]
```

**验证：**
```bash
# ✅ 可以
hermes --provider volcengine-ark -m doubao-seed-2-1-pro-260628 -z "测试"
hermes -z "测试" --provider volcengine-ark -m doubao-seed-2-1-pro-260628  # -z 后直接跟 prompt 也行

# ❌ 不可以
hermes -z --provider volcengine-ark -m doubao-seed-2-1-pro-260628 "测试"  # --provider 被当 prompt
```

### ⚠️ TTS 念出了分隔符 `---`（2026-07-11 修复）

**症状：** 玉芬回复后 TTS 把 `---` 分隔符和详细内容一起念出来。日志显示 `TTS(say): 回复正文\n---\n详细内容...`，`say` 命令报 `unrecognized option '---'`。

**根因：** `voice_dashboard.py` 中 `extract_spoken()` 没找到 `[SPOKEN]` 标签时，用 `reply.split("---")[0]` 提取。但 `---` 可能出现在回复正文中（如表格分隔线），导致 split 结果不对。且 `split("---")` 会用中间那个 `---` 当分隔符而不是 `\n---\n`。

**修复：** 用 `\n---\n` 精确分隔：

```python
spoken = HermesClient.extract_spoken(reply)
if not spoken:
    parts = reply.split("\n---\n", 1)
    spoken = parts[0].strip()
if spoken:
    tts.speak(spoken, blocking=True)
```

**症状：** `voice_common.py` 已有 `run_wake_word_loop()`（含流式 TTS/SileroVAD/打断/多轮），但仪表盘的嵌入式 `run_dialogue()` 是另一套旧代码，所有 v0.9/v0.10 优化在仪表盘模式下均未生效。

**根因：** 仪表盘内嵌语音循环（第 496-600 行）与 `run_wake_word_loop()` 是两套独立代码，未同步更新。

### ⚠️ voice_common.py / voice_dashboard.py 需要 Python ≥ 3.11

voice_common.py 使用 `dataclass(kw_only=True)` 等 Python 3.10+ 特性，系统默认 python3 是 3.9.6，必须用 homebrew 的 python3.11：

```bash
# ❌ python3 → 3.9.6 → dataclass kw_only 报错
# ✅
/opt/homebrew/bin/python3.11 voice_dashboard.py --whisper --port 8765
```

### ⚠️ `~/hermes/voice/config.yaml` 覆盖项目目录配置（voice_dir 优先级陷阱）

**症状：** 改了 `~/6-产品研发/21-语音交互/config.yaml`（如 `tts_backend: "say"`），但代码仍走 `volc`。日志显示 `TTS(volc)` 而非 `TTS(say)`。

**根因：** `AudioConfig.__post_init__` 先检查 `self.voice_dir / "config.yaml"`（即 `~/hermes/voice/config.yaml`），如果存在就用它，不再检查项目目录的 `config.yaml`。`voice_dir` 默认是 `~/hermes/voice/`。

**修复：** 两个文件都要改，或者删除 `~/hermes/voice/config.yaml` 让代码回退到项目目录：
```bash
# 检查哪个文件被加载
cat ~/hermes/voice/config.yaml | grep tts_backend
cat ~/6-产品研发/21-语音交互/config.yaml | grep tts_backend
# 同步两个文件，或删除 voice_dir 的版本
```

### ⚠️ OrayVirtualAudioDevice 不采集真实音频

**症状：** 蓝牙耳机断开后，系统自动切换到 OrayVirtualAudioDevice（设备 2），VAD 能检测到声音（RMS=15-36），但录音能量极低（RMS=0.0003-0.0004），Whisper 识别为空。

**根因：** OrayVirtualAudioDevice 是向日葵远程控制的虚拟音频设备，不采集真实麦克风音频。它的输入通道存在但实际数据接近静音。

**修复：** 蓝牙耳机断开时语音系统无法工作，需要用户重新连接蓝牙耳机。可以考虑在启动时检测设备是否为虚拟设备（名称含"Oray"、"Virtual"），给出警告。

### ⚠️ calibrate_noise_floor 通道数硬编码导致设备崩溃

**症状：** `calibrate_noise_floor(device_index=2)` 在 OrayVirtualAudioDevice 上报 `Error opening InputStream: Invalid number of channels`。

**修复（2026-07-09）：** 自动检测设备支持的通道数：

### ⚠️ TTS 回音反馈（speaker 输出被麦克风拾取）— 已修复：blocking + drain

**症状：** TTS 播放后 VAD 立即检测到人声（RMS=6-8, 阈值=5），触发误识别，Whisper 得到 TTS 播报内容的回声。系统陷入「自己跟自己对话」的死循环。

**根因：** TTS 通过 Mac mini 音箱播放，声音被蓝牙耳机麦克风拾取。非阻塞 TTS (`subprocess.Popen`) 导致 TTS 还在播放时，VAD 就已经开始监听并拾取到 TTS 声音。

**修复（2026-07-09）：** 三管齐下：
1. **TTS 改为阻塞模式**：`tts.speak(reply, blocking=True)` — 等待 TTS 播放完成后才继续
2. **播放后排空音频缓冲**：`while not audio_q.empty(): audio_q.get_nowait()` — 丢弃回音数据
3. **`_speak_say` 中 `blocking=True` 用 `subprocess.run`（阻塞），`blocking=False` 用 `subprocess.Popen`（非阻塞）**

```python
# voice_dashboard.py 关键修复
tts.speak("来了，华哥", blocking=True)
# 清空 TTS 回声缓冲
while not audio_q.empty():
    try: audio_q.get_nowait()
    except queue.Empty: break
```

### ⚠️ 音频设备通道数自动检测

**症状：** 蓝牙耳机未连接时，`sd.RawInputStream(channels=1, device=2)` 报 `Invalid number of channels [PaErrorCode -9998]`。进程崩溃重启循环。

**根因：** 不同音频设备支持不同通道数（蓝牙耳机 1ch，虚拟设备 2ch）。硬编码 `channels=1` 在某些设备上不兼容。

**修复：** 启动时自动检测设备支持的通道数：

### ⚠️ voice_dashboard.py 对话循环绕过唤醒词（已修复）

**症状：** 启动后立即说"在呢，你说"，然后进入无唤醒词的连续对话模式。任何声音都触发回复。

**根因：** voice_dashboard.py 最初版本使用 `yuxin_dialogue.DialogueEngine`，该引擎没有唤醒词检测，直接进入对话循环。

**修复：** 重写 `run_dialogue()` 函数，使用 `yuxin_wake_word.py` 的唤醒词+声纹模式：
- wake mode: AdaptiveVAD → Whisper → 唤醒词匹配 → VoiceprintEngine → dialogue mode
- dialogue mode: 一轮对话 → TTS → 2s静音 → 回到 wake mode

### ⚠️ SwitchAudioSource 切换音频输出设备

**安装：** `brew install switchaudio-osx`

**用法：**
```bash
# 列出所有输出设备
/opt/homebrew/bin/SwitchAudioSource -a -t output

# 切换到内置音箱
/opt/homebrew/bin/SwitchAudioSource -s \"Mac mini扬声器\"

# 切换到蓝牙耳机
/opt/homebrew/bin/SwitchAudioSource -s \"JSoul Mate Pro\"

# 查看当前设备
/opt/homebrew/bin/SwitchAudioSource -c
```

**场景：** 华哥用蓝牙耳机麦克风输入，但希望 TTS 从音箱输出（不戴耳机时听到回复）。

### ⚠️ RawInputStream 通道数硬编码导致蓝牙设备报错

**症状：** `sd.RawInputStream(device=2, channels=1)` 报 `Error opening RawInputStream: Invalid number of channels [PaErrorCode -9998]`，进程反复崩溃重启。

**根因：** 不同音频设备支持的输入通道数不同。蓝牙耳机通常 1 通道（mono），虚拟音频设备（如 OrayVirtualAudioDevice）可能 2 通道（stereo）。硬编码 `channels=1` 在 2 通道设备上失败。

**修复（2026-07-09）：** 打开 RawInputStream 前自动检测设备支持的通道数：

```python
try:
    dev_info = sd.query_devices(vcfg.device_index)
    max_ch = dev_info['max_input_channels']
    actual_device = vcfg.device_index if max_ch > 0 else None
    actual_channels = max(1, min(max_ch, 2)) if max_ch > 0 else 1
except:
    actual_device = None
    actual_channels = 1

with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK,
                        dtype="int16", channels=actual_channels, device=actual_device,
                        callback=audio_cb):
```

**同样适用于 `calibrate_noise_floor`：** `sd.rec(device=index, channels=1)` 也会在 2 通道设备上失败，需同样的自动检测逻辑。

**验证：**
```bash
python3 -c "import sounddevice as sd; print([(i,d['name'],d['max_input_channels']) for i,d in enumerate(sd.query_devices()) if d['max_input_channels']>0])"
```

**症状：** 蓝牙耳机连接后，正常人声的 RMS 只有 0.002-0.003（float32），int16 的 RMS 只有 70 左右。VAD 阈值 30 完全触发不了，即使大喊 RMS 也只有 150。

**根因：** macOS 蓝牙耳机（如 JSoul Mate Pro）的 SCO 链路输入增益极低。`sd.RawInputStream(channels=1)` 读到的 int16 数据幅度远小于内置麦克风。正常说话 int16 值的 RMS 只有 70（而内置麦克风可达 2000+）。

**修复：** 分两步降低 VAD 阈值，保留足够的安全边界：

1. **语音检测阈值**（`_is_speech_int16`）：`threshold` 从 30 降到 1
2. **能量 RMS 检查**（`min_rms`）：从 0.005 降到 0.0005

```python
# 修改前（内置麦克风可用）
VAD_THRESHOLD = 30
VAD_MIN_RMS = 0.005

# 修改后（蓝牙耳机兼容）
VAD_THRESHOLD = 1     # int16 RMS 阈值，蓝牙耳机正常说话 RMS≈70
VAD_MIN_RMS = 0.0005  # float32 RMS 阈值，蓝牙耳机正常说话 RMS≈0.002
```

**验证：**
```bash
python3 -c "
import sounddevice as sd, numpy as np
audio = sd.rec(int(16000*2), 16000, channels=1, dtype='int16', device=0)
sd.wait()
rms = np.sqrt(np.mean(audio.astype(float)**2))
print(f'int16 RMS: {rms:.1f}')
print(f'float32 RMS: {np.sqrt(np.mean((audio.astype(float)/32768)**2)):.6f}')
"
```

### ⚠️ yuxin_dialogue.py --whisper 标志被忽略

**症状：** `python3 yuxin_dialogue.py --whisper` 没有使用 Whisper，实际走了 VolcASR。

**根因：** `config.yaml` 的 `asr:engine: volc` 在 `AudioConfig.__post_init__` 中覆盖了 `--whisper` 标志。命令行参数解析后没有重新设置 `asr_engine`。

**修复：** 在 argparse 解析后，显式用命令行参数覆盖 config 中加载的值：

```python
args = parser.parse_args()
if args.whisper:
    config.asr_engine = "whisper"
```

**第二个根因：** `VolcASR` 类没有 `create_recognizer()` 方法，代码中调用 `self.asr.create_recognizer()` 报 `AttributeError`。

**修复：** 将 `create_recognizer()` 改为 `transcribe()`，因为 `VolcASR` 只有 `transcribe(audio)` 方法。

```python
# 修改前
recognizer = self.asr.create_recognizer()
result = recognizer.transcribe(audio)

# 修改后
result = self.asr.transcribe(audio)
```

### ⚠️ yuxin_dialogue.py 创建 VolcASR 后又丢弃使用 Whisper

**症状：** 即使 `--whisper` 标志正确工作，代码仍然在启动时创建了 `VolcASR` 对象（调用火山引擎 WebSocket），然后丢弃不用。

**修复：** 按需创建 ASR 引擎，而不是无条件创建所有引擎：

```python
if self.config.asr_engine == "whisper":
    self.asr = WhisperASR(self.config)
elif self.config.asr_engine == "volc":
    self.asr = VolcASR(self.config)
else:
    raise ValueError(f"Unknown ASR engine: {self.config.asr_engine}")
```

## v0.10 升级（2026-07-11）— 流式 TTS + 中文 ASR 优化

华哥反馈两大问题：1) 跟豆包比显得不流畅；2) 语音识别错误率太高。一次性修复。

### 流式 TTS 架构

```
旧: 用户说 → ASR → LLM全文(3-5s等) → TTS一次性播放
新: 用户说 → ASR → LLM逐句产出 → 立刻TTS播放 → 边出边播
```

- `voice_streaming.py` — 流式引擎（~160行）：`StreamingTTSEngine` + `call_streaming()`
- `HermesClient.call_streaming_tts()` — voice_common.py 集成点（~130行）
- 效果：用户说→首句播放从 3-5s 降到 **<1s**

### 中文 ASR 优化：Whisper tiny → small + VolcASR 做主引擎

**问题：** 默认用 Whisper tiny 做中文识别，tiny 模型中文准确率仅 ~75%，导致大量识别错误。

**修复：**
- **VolcASR 做主引擎 + 蓝牙 RMS 阈值**: 详见上方「⚠️ 中文 ASR 错误率高：VolcASR 三 Bug 叠加」完整修复。
- **蓝牙 float32 RMS 阈值**: `finalize()` 中 `rms < 0.0005` → `0.0001`（蓝牙耳机正常说话 float32 RMS 仅 0.0002-0.0005，原阈值丢弃了几乎所有有效录音）
- **模型名锁定 `doubao-seed-asr-2.0`**: `VolcASR.MODEL_NAME` 类常量，华哥明确要求用购买的专用语音大模型，不可改回 `bigmodel`
- **启动必须省略 `--whisper`**: `voice_dashboard.py --port 8765`，不加 `--whisper`。`--whisper` 参数虽定义但代码未使用，真正的 ASR 选择由 `config.yaml` 的 `asr_backend` 控制

3. `device_index: 2` → `0`（OrayVirtualAudioDevice 无真实音频 → JSoul Mate Pro）

### 关联参考

- `references/streaming_tts_implementation.md` — 流式 TTS 实现细节

### ⚠️ 沟通偏好更新

- **硬件问题直接说根因**：麦克风没声音 = 直接说"RMS为零，耳机没在收音，戴上试试"，不要先分析一堆日志再给结论。用户问"为什么没反应"，第一个字就该是答案。
- **用户不满时先确认再行动**：华哥说「你怎么不回复我的问题」= 立刻说根因（麦克风零信号），不要说「我知道」「我在查」，先给结论。
- 改完直接告知结果，不分析中间过程。一句话说「A 改成了 B，现在状态是 C」。
- 发现问题直接处理后汇报，不反复确认「这么做行不行」。
- 说「我自己看代码」= 停手，等华哥反馈。
- 说「开始测试」= 立刻启动服务并告知就绪，不啰嗦。
- **默认语音偏好（英语场景）**：使用 macOS 原生 Shelley 温柔知性女声，语速 1.3x（`say -v Shelley --rate=260`），不要用默认系统语速。

## 相关文件

- 流式引擎：`~/6-产品研发/21-语音交互/voice_streaming.py`
- 集成点：`~/6-产品研发/21-语音交互/voice_common.py`（`HermesClient.call_streaming_tts()`）

- 改完直接告知结果，不分析中间过程。一句话说「A 改成了 B，现在状态是 C」。
- 代码全量保存到指定目录（`~/6-产品研发/21-语音交互/`），不要只给代码片段。
- 发现问题直接处理后汇报，不反复确认「这么做行不行」。
- 说「我自己看代码」= 停手，等华哥反馈。

## 关联

- chinese-tts-optimization skill — TTS 升级方案
- macos-automation skill — macOS 自动化（Hammerspoon/LaunchAgent）
- long-running-task skill — 后台任务超时处理
- 调试日志参考：`references/debug_log_20260702.md`（v6.1 调试全记录）
- Whisper 识别变体集：`references/debug_log_20260702_v7.md`（v7 调试 + 唤醒词规则演进）
- 2026-07-05 繁简匹配 + PATH 修复：`references/debug_log_20260705.md`
- HomeRail 语音架构调研：`references/homerail_research_2026-07-09.md`（火山引擎 ASR/TTS、双通道语音、voice-memo）
- USB 麦克风增益调试 v6.0：`references/usb_mic_gain_v6.0_20260714.md`（连续语音检测模式、Shelley 语音偏好）
- EventBus 实时仪表盘：`references/eventbus_dashboard.md`（WebSocket 推送、VAD 波形、ASR/回复/日志实时显示）
- 火山引擎 ASR 二进制协议：`references/volc_asr_protocol.md`（WebSocket 协议头格式、载荷封装、请求/响应示例）
- 火山引擎 ASR 响应解析 Bug 与修复：`references/volc_asr_response_format.md`（2026-07-11 三个 Bug 的完整分析）
- 语音 LLM 包月套餐对比：`references/voice_llm_pricing_comparison.md`（四大平台定价、Doubao Seed 2.1 Pro 推荐）
- HermesClient 语音 LLM 独立路由：`references/hermes_voice_llm_routing.md`（voice_model/voice_provider 配置方法）
- 多 Provider 配置模式：`references/multi_provider_setup.md`（MiniMax/火山引擎/DeepSeek 直连配置、fallback 链）
- TTS 故障诊断：`references/tts_fallback_diagnostics.md`（静默回退排查、key 过期检测、逐后端测试）

## Absorbed Skills (Consolidated)

The following skills have been absorbed into this umbrella. Their unique content is archived under `~/.hermes/skills/.archive/`:

- **voice-interaction** (voice/) — macOS voice interaction with Whisper + voiceprint. Unique content: macOS Speech Framework section, Doubao TTS API reference (`references/doubao_tts_api.md`), HMAC signature migration details.
- **voice-interaction-on-mac** (productivity/) — Hands-free voice loop. Unique content: step-by-step fresh Mac setup guide, resource budget table, voice_crash_watcher cron details, templates (yuxin_wake_word.py, yuxin_voice.py, yuxin_wakeword.sh, com.yuxin.wakeword.plist), references (macos-permissions.md, whisper-migration.md, architecture.md, wake-word-tuning.md).
- **macos-voice-assistant** (voice-assistant/) — Vosk-based voice assistant (legacy approach, superseded by Whisper).
- **macos-voice-wake-word** (apple/) — Vosk-based wake word detection (legacy, superseded by Whisper VAD).
- **macos-local-voice-assistant** — Minimal Vosk-based local voice assistant (legacy, superseded by Whisper).
