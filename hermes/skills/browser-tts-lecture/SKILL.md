---
name: browser-tts-lecture
description: Generate natural Chinese lecture speech from structured card/data using browser SpeechSynthesis API — segmented narration, visual highlight sync, mode toggle (lecture/quick). Zero API cost.
category: creative
triggers:
  - 语音讲解 / TTS / text-to-speech / 朗读 / 讲稿 / 配音
  - 学习卡片 + 音频
  - 教育类前端项目需要语音功能
  - "给卡片加语音"
---

# Browser TTS Lecture System

Generate natural, lecture-style Chinese speech for educational web apps using the browser built-in SpeechSynthesis API. Zero API cost, works offline, sounds human.

## Architecture

```
Structured card data → Lecture script builder → Segmented sections → 
SpeechSynthesis queue → Visual highlight sync → Done callback
```

## Core Engine

```javascript
const tts = {
  synth: window.speechSynthesis,
  mode: 'lecture',      // 'lecture' | 'quick'
  sections: [],          // lecture text segments
  secIdx: 0,             // current section being spoken
  voice: null,           // preferred Chinese voice
  speaking: false,
  onHighlight: null,     // callback(idx) — highlight section idx
  onDone: null,          // callback() — lecture finished
  
  init() {
    // Prefer Chinese female voice 'Tingting'
    const voices = this.synth.getVoices();
    this.voice = voices.find(v => 
      v.lang.startsWith('zh-CN') && v.name.includes('Tingting')
    ) || voices.find(v => v.lang.startsWith('zh-CN'))
      || voices.find(v => v.lang.startsWith('zh'))
      || voices[0];
  },
  
  // Markdown → clean spoken text
  clean(md) {
    return (md || '')
      .replace(/\*\*(.+?)\*\*/g, '$1')   // strip bold
      .replace(/###?\s*/g, '')            // strip headings
      .replace(/`(.+?)`/g, '$1')          // strip code
      .replace(/\|/g, '，')               // pipes → commas
      .replace(/\n+/g, '。')              // newlines → periods
      .replace(/\s+/g, ' ')               // collapse whitespace
      .trim();
  },
  
  // Build lecture script from card data
  buildLecture(card, rich) {
    const s = [];
    // 1. Welcome + name
    s.push(`你好，我们来学习「${card.name}」这个概念。`);
    // 2. English name (if exists)
    if (card.en) s.push(`它的英文是 ${card.en}。`);
    // 3. One-line definition
    if (card.description) s.push(`简单来说呢，${card.description}。`);
    // 4. Detailed explanation — chunk into 80-char segments
    if (rich?.content?.detail_md) {
      const cleaned = this.clean(rich.content.detail_md);
      const sentences = cleaned.split('。').filter(x => x.trim());
      let chunk = '';
      for (const sen of sentences) {
        chunk += (chunk ? '。' : '') + sen;
        if (chunk.length > 80) {
          s.push(chunk + '。');
          chunk = '';
        }
      }
      if (chunk) s.push(chunk + '。');
    }
    // 5. Examples
    if (rich?.content?.examples) {
      const ex = rich.content.examples.replace(/\|/g, '，还有');
      s.push(`来看几个实际案例。${ex}。`);
    }
    // 6. Common mistakes (first 3)
    if (rich?.content?.common_mistakes) {
      const ms = this.clean(rich.content.common_mistakes)
        .split('。').filter(x => x.trim()).slice(0, 3);
      if (ms.length) s.push(`注意避开常见误区。${ms.join('。')}。`);
    }
    // 7. Summary
    s.push(`总结一下，「${card.name}」的核心就是，${(card.description || '').substring(0, 60)}。你学会了吗？`);
    return s;
  },
  
  // Quick read (single segment, no intro/summary)
  buildQuick(card, rich) {
    const p = [];
    p.push(card.name + '。');
    if (card.description) p.push(card.description + '。');
    if (rich?.content?.detail_md) p.push(this.clean(rich.content.detail_md));
    return [p.join(' ')];
  },
  
  // Start segmented lecture
  startLecture(sections, highlightFn, doneFn) {
    this.stop();
    this.sections = sections;
    this.secIdx = 0;
    this.onHighlight = highlightFn;
    this.onDone = doneFn;
    this.speaking = true;
    if (highlightFn) highlightFn(0);  // pre-highlight first section
    this._speakNext();
  },
  
  _speakNext() {
    if (this.secIdx >= this.sections.length) {
      this.speaking = false;
      if (this.onDone) this.onDone();
      return;
    }
    const utter = new SpeechSynthesisUtterance(this.sections[this.secIdx]);
    utter.voice = this.voice;
    utter.rate = 0.9;    // slightly slower for clarity
    utter.pitch = 1.08;  // slightly brighter
    utter.volume = 1;
    utter.lang = 'zh-CN';
    const idx = this.secIdx;
    utter.onstart = () => { if (this.onHighlight) this.onHighlight(idx); };
    utter.onend = () => { this.secIdx++; this._speakNext(); };
    utter.onerror = () => { this.secIdx++; this._speakNext(); };
    this.synth.speak(utter);
  },
  
  stop() {
    this.synth.cancel();
    this.speaking = false;
    this.sections = [];
    this.secIdx = 0;
    if (this.onDone) this.onDone();
  }
};
tts.init();
speechSynthesis.onvoiceschanged = () => tts.init();
```

## Visual Highlight Sync

Add CSS class for active section:
```css
.tts-highlight {
  background: #fffdf5 !important;
  border-radius: 8px;
  transition: background 0.3s;
}
```

In the highlight callback, toggle the class on the matching DOM element:
```javascript
tts.startLecture(sections,
  (idx) => {
    const secEls = document.querySelectorAll('.detail-section');
    secEls.forEach((el, i) => el.classList.toggle('tts-highlight', i === idx));
  },
  () => {
    document.querySelectorAll('.tts-highlight').forEach(el => el.classList.remove('tts-highlight'));
  }
);
```

## Mode Toggle UI

Provide two buttons: lecture (segmented, with intro/summary) and quick (single pass):
```html
<span class="tts-btn-trigger" onclick="speakCardTTS('${id}', this)">🎙️ 细致讲解</span>
<span class="tts-mode-switch" onclick="toggleTtsMode()">切换</span>
```

Button state management:
- Idle: `🎙️ 细致讲解` or `⚡ 快速朗读` (depending on mode)
- Loading: `⏳ 准备讲稿...` (with pulsing animation)
- Speaking: `⏹️ 停止讲解` (pulsing yellow)

## Pitfalls

1. **Voice availability**: `speechSynthesis.getVoices()` is async — voices may not be available synchronously. Always call `init()` both at startup AND on `onvoiceschanged` event.

2. **Chrome requires user gesture**: SpeechSynthesis won't speak without a user-initiated event (click). Don't try to auto-play on page load.

3. **Long text truncation**: Some browsers truncate utterances > 200 chars. Always split into segments ≤ 120 chars for reliability.

4. **Chinese voice detection**: Not all browsers ship Chinese voices. Test with `voices.find(v => v.lang.startsWith('zh'))`. Fallback gracefully — the default voice will read Chinese with acceptable quality.

5. **SSML not supported**: Browser SpeechSynthesis doesn't support SSML. Use punctuation (。，) and strategic pauses (empty strings between utterances) for pacing instead.

## Voice Quality Tips

- `rate: 0.9` — slightly slower than default for lecture clarity
- `pitch: 1.08` — slightly brighter, more engaging
- Split at natural pause points (periods, commas)
- Add conversational fillers: "简单来说呢", "来看几个", "总结一下", "你学会了吗？"
- Keep segments 40-80 chars for natural breathing rhythm
