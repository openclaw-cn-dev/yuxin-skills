#!/usr/bin/env python3
"""小红书 10 篇流水线模板

步骤：
1. 读知识库 + 选题
2. 写 10 篇文案（标题 + 正文 + 标签）
3. 拉 4 张/篇 Pexels CC0 图
4. vision 验真图（必须）
5. 写桌面文件夹 + 飞书推送
"""
import os, json, subprocess, urllib.request, urllib.error

OUT_BASE = r"C:\Users\Administrator\Desktop\小红书"
TOPIC = "水产物美"  # 改这个
NUM_NOTES = 10  # 改这个

# === 8 张已验真图（直接复用） ===
VERIFIED_IDS = {
    725992: "白灼虾铁盘+蓝木桌",
    566344: "白灼虾堆+柠檬欧芹",
    566345: "海鲜大餐（青口+虾+柠檬）",
    2098085: "寿司拼盘（有红虾）",
    1267320: "树桩料理（高级餐厅风）",
    1108101: "塔吉锅干冰料理",
    1132047: "鱼缸内部（养殖）",
    259165: "工业罐（设备）",
}

def fetch_pexels(pid, dest):
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?w=1200"
    r = subprocess.run(
        ["curl", "-L", "-s", "-A", "Mozilla/5.0", "--max-time", "10", "-o", dest, "-w", "%{http_code}", url],
        capture_output=True, text=True, timeout=15
    )
    return r.stdout.strip() == "200" and os.path.exists(dest) and os.path.getsize(dest) > 10000

def setup_folder(topic, num_notes):
    """建 10 个子文件夹"""
    base = os.path.join(OUT_BASE, f"{topic}_爆款{num_notes}篇")
    os.makedirs(base, exist_ok=True)
    for i in range(1, num_notes + 1):
        os.makedirs(os.path.join(base, f"{i:02d}_{topic}_{i}"), exist_ok=True)
    return base

# 调用：
# 1. setup_folder("水产物美", 10)
# 2. 在每个子文件夹手写文案.md（参照 xiaohongshu-formula.md）
# 3. 调 fetch_pexels 拉 4 张图/篇（必须 vision 验）
# 4. 写 README.md（总览）
# 5. 调 feishu-push.py 发飞书卡片
