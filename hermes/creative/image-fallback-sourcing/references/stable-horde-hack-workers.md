# Stable Horde Hack 节点识别

> 测试日期：2026-06-08

## 现象

提交 job 后 **30-50 秒** 返回 "done"，但返回的 base64 图像：
- 大小 **< 200 字节**（实真图至少 30KB+）
- 解码后**不是合法 PNG 头**（`\x89PNG\r\n\x1a\n` 缺失）
- 解码后是 `0x86 0xDB 0x69 0xB3` 之类的随机数据
- 实际保存到磁盘会失败或显示"图片格式错"

## 已确认的 hack 节点

- **`Zikeri`** —— 7 个 job 全部返 92B 假图
- 已知真 worker：`smellycat1`（1.2 M/s，最快）、`Roaring 3050` 系列、`Gravitate7706 Dreamer`

## 防御代码

```python
def is_valid_image(path, data):
    size = os.path.getsize(path)
    # 严格验证
    if size < 30000:
        return False
    if data[:8] != b'\x89PNG\r\n\x1a\n' and data[:4] != b'RIFF':
        return False
    return True
```

## 推荐配置（仍有 hack 风险）

```python
data = json.dumps({
    "prompt": p,
    "params": {"width": 512, "height": 512, "steps": 25, "sampler_name": "k_euler_a", "cfg_scale": 7.0, "n": 1},
    "models": ["Edge Of Realism"],   # 写真模型
    "r2": True,                       # R2 CDN
}).encode()
```

## 结论

**当前环境下 Stable Horde 不靠谱**。如果 6+ 个 job 全返 < 1KB，**直接放弃**，用 Pexels CC0 真图复用。

## 替代方案（按可行性排序）

1. ✅ Pexels CC0 + vision 验真图（最稳）
2. ⚠️ Stable Horde（**不推荐** — hack 节点多）
3. ❌ Polinations（付费墙）
4. ❌ Unsplash source（已死）
5. ❌ HF Inference（SSL 全挂）
6. ❌ DeepAI（连不上）
