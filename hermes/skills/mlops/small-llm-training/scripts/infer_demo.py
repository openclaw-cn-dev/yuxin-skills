#!/usr/bin/env python3
"""训练完的小模型推理演示（MiniMind 格式，MPS/CUDA 自适应）。
2026-09-07 渔芯实测：temperature 0.7 / top_p 0.9，3 问实录原始输出（好与差都如实记录）。
改 MODEL_DIR / WEIGHTS / QUESTIONS 后运行。"""
import sys, os, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transformers import AutoTokenizer
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM  # ← 按项目模型类改

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')   # tokenizer 所在
WEIGHTS   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'full_sft_768.pth')
QUESTIONS = [  # ← 改：演示问题（建议：自我介绍 / 领域知识问答 / 开放生成 各一，检验 SFT 效果边界）
    "你好，请介绍一下你自己。",
    "什么是循环水养殖（RAS）？它有什么优点？",
    "请写一句鼓励别人坚持学习的话。",
]
MAX_NEW_TOKENS = 160

device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
cfg = MiniMindConfig(hidden_size=768, num_hidden_layers=8)  # ← 按训练 config 改
model = MiniMindForCausalLM(cfg).to(device).eval()
model.load_state_dict(torch.load(WEIGHTS, map_location=device))  # fp16 权重自动 cast
print(f"[加载成功] device={device}\n", flush=True)

for q in QUESTIONS:
    prompt = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False, add_generation_prompt=True)
    ids = tok(prompt, add_special_tokens=False, return_tensors="pt").input_ids.to(device)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=True,
                             temperature=0.7, top_p=0.9,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
    ans = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=False)
    for stop in ("<|im_end|>", "</s>"):
        if stop in ans: ans = ans.split(stop)[0]
    print(f"🙋 问：{q}\n🤖 答：{ans.strip()}\n{'-'*60}", flush=True)
