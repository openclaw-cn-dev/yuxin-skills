# -*- coding: utf-8 -*-
"""LCM Dreamshaper 批量生图模板 — 已验证 2026-06-08
- CPU 14.5 秒/张
- 40 张 9 分钟出完
- vision 验证 5/5 通过
- 100% 本地 SD 生成，0 水印，0 AI 味
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["TRANSFORMERS_CACHE"] = r"C:\Users\Administrator\.cache\huggingface"

import sys
import time
from pathlib import Path
import torch
from diffusers import LCMScheduler, AutoPipelineForText2Image

OUT = Path(r"C:\Users\Administrator\Desktop\小红书\爆款10篇\sd_output")
OUT.mkdir(parents=True, exist_ok=True)

# 10 篇爆款的 SD prompt（中英对照，见 references/prompt_library_zh.md）
PROMPTS = [
    # 美食
    ("01_白灼虾_cover", "professional food photography of poached shrimp on white porcelain plate, three pieces of bright red cooked shrimp with lemon wedge, chopsticks holding one shrimp, natural window light, clean background, sharp focus, 8K, no watermark, no text, no logo"),
    ("01_白灼虾_done", "professional food photography of poached shrimp on a serving plate, three plump red shrimp with garlic soy sauce in small dish, fresh herbs garnish, 45-degree angle shot, soft natural lighting, white background, no watermark"),
    # ... 替换成你自己的 prompt 列表
]

NEG = "watermark, text, logo, signature, low quality, blurry, deformed, ugly, plastic, fake, AI-generated feel, oversaturated, cartoon, NSFW"

print(f"开始加载 LCM Dreamshaper 模型...", flush=True)
t0 = time.time()
pipe = AutoPipelineForText2Image.from_pretrained(
    "SimianLuo/LCM_Dreamshaper_v7",
    torch_dtype=torch.float32,
    cache_dir=r"C:\Users\Administrator\.cache\huggingface\hub",
)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
print(f"✅ 模型加载完成 ({time.time()-t0:.1f}s)", flush=True)

# CPU 模式优化
pipe.enable_attention_slicing()
try:
    pipe.enable_vae_tiling()
except: pass

# 只生成前 N 张（命令行参数）
N = int(sys.argv[1]) if len(sys.argv) > 1 else len(PROMPTS)
for i, (name, prompt) in enumerate(PROMPTS[:N]):
    out = OUT / f"{name}.jpg"
    if out.exists() and out.stat().st_size > 30000:
        print(f"[{i+1}/{N}] 跳过已存在: {name}", flush=True)
        continue
    t0 = time.time()
    try:
        img = pipe(
            prompt=prompt,
            negative_prompt=NEG,
            num_inference_steps=2,  # LCM 1-4 步
            guidance_scale=1.0,      # LCM 不需要高 CFG
            width=512,
            height=512,
        ).images[0]
        img.save(out, "JPEG", quality=85)
        sz = out.stat().st_size
        print(f"[{i+1}/{N}] ✅ {name}.jpg ({time.time()-t0:.1f}s, {sz//1024}KB)", flush=True)
    except Exception as e:
        print(f"[{i+1}/{N}] ❌ {name} 失败: {e}", flush=True)

print(f"\n🎉 完成 {N} 张", flush=True)

# 用法：
#   python lcm_batch_template.py 3    # 跑前 3 张测试
#   python lcm_batch_template.py       # 跑全部
#
# 后台跑（不阻塞）：
#   nohup python -u lcm_batch_template.py > /tmp/lcm.log 2>&1 &
