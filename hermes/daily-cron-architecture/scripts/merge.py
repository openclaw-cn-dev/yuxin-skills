#!/usr/bin/env python3
"""把 fao_tmp/ 抓的素材 + 抖音热榜合并成 1 份简报 markdown
用法：python merge.py <tmp_dir> <out_md_path>
"""
import sys, os, re, io, json
from datetime import datetime

if len(sys.argv) < 3:
    print("usage: merge.py <tmp_dir> <out_md>")
    sys.exit(1)
TMP, OUT = sys.argv[1], sys.argv[2]

def safe_read(p):
    for enc in ("utf-8", "gbk", "latin-1"):
        try: return io.open(p, mode="r", encoding=enc, errors="ignore").read()
        except: pass
    return ""

def strip_html(html):
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()

# 1) 解析 cappma
CAT_MAP = {
    "cap_5_24": "标准资讯", "cap_5_25": "团体标准", "cap_5_26": "意见征求", "cap_5_27": "标准查询",
    "cap_7_30": "产业报告", "cap_7_31": "行业数据", "cap_7_32": "统计数据", "cap_7_33": "价格行情",
    "cap_66_67": "政策法规", "cap_66_68": "质量安全", "cap_66_69": "市场预警", "cap_66_70": "国际资讯",
    "cap_66_227": "综合信息", "cap_66_340": "输美预警",
    "cap_4_23": "展览动态", "cap_4_61": "会议动态",
    "cap_1_11": "协会活动", "cap_1_12": "通知公告", "cap_1_338": "刀鲚养殖",
    "cap_6_28": "国际会议", "cap_6_29": "交流合作",
}
cappma = []
seen_ids = set()
for f in os.listdir(TMP):
    if not f.startswith("cap_") or not f.endswith(".html"): continue
    key = f[:-5]
    cat = next((v for k, v in CAT_MAP.items() if k in key), "其他")
    html = safe_read(os.path.join(TMP, f))
    if len(html) < 10000: continue
    for u, vid, t in re.findall(r'<a[^>]+href="(view\.php\?id=(\d+))"[^>]*>(.*?)</a>', html, re.S):
        ts = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()
        if not ts or len(ts) < 6 or vid in seen_ids: continue
        seen_ids.add(vid)
        cappma.append({"cat": cat, "id": vid, "title": ts,
                       "url": f"http://www.cappma.org.cn/{u}"})

# 2) 解析 FAO
SPECIES_ZH = {
    "pangasius": "巴沙鱼", "salmon": "三文鱼", "shrimps": "对虾", "tilapia": "罗非鱼",
    "tuna": "金枪鱼", "seabass-and-seabream": "鲈鱼/鲷鱼", "lobster": "龙虾",
    "crab": "螃蟹", "cephalopods": "头足类", "bivalves": "双壳贝类", "seaweed": "海藻",
    "groundfish": "底栖鱼", "small-pelagics": "小型中上层鱼",
}
fao_species = []
for slug, zh in SPECIES_ZH.items():
    path = os.path.join(TMP, f"sp_{slug}.html")
    if not os.path.exists(path): continue
    html = safe_read(path)
    if len(html) < 10000: continue
    text = strip_html(html)
    paras = [p for p in re.split(r"\.\s", text) if len(p.strip()) > 100]
    intro = (". ".join(paras[:3]) + ".")[:600] if paras else text[:600]
    fao_species.append({"zh": zh, "slug": slug,
                        "url": f"https://www.fao.org/in-action/globefish/species-analysis/{slug}/en",
                        "intro": intro})

# 3) 蓝色转型
blue = {}
bt = os.path.join(TMP, "blue_transformation.html")
if os.path.exists(bt):
    text = strip_html(safe_read(bt))
    paras = [p for p in re.split(r"\.\s", text) if len(p.strip()) > 80]
    blue = {"url": "https://www.fao.org/fishery/en/sofia",
            "intro": ". ".join(paras[:6]) + ".",
            "key": "全球渔业+水产养殖 2.14 亿吨（历史新高），预计 2030 年再增 15%"}

# 4) 抖音
dy_aqua = safe_read("/tmp/dy_aqua.txt") if os.path.exists("/tmp/dy_aqua.txt") else ""

# 5) 写简报
md = [f"# 📰 每日水产简报｜{datetime.now().strftime('%Y-%m-%d')}\n"]
md.append("> **国内**中国渔业协会 21 频道 | **国际**FAO 13 物种 + SOFIA 蓝色转型 | **热度**抖音\n")
md.append("---\n")
md.append("## 🌍 FAO 全球权威\n")
if blue:
    md.append("### 1. Towards Blue Transformation（蓝色转型）")
    md.append(f"- 来源：FAO 联合国粮农组织 / SOFIA 旗舰报告")
    md.append(f"- 链接：{blue['url']}")
    md.append(f"- 关键数据：{blue['key']}")
    md.append(f"- 摘要：{blue['intro'][:500]}\n")

md.append("## 🦐 FAO 13 个水产品种市场数据\n")
md.append("| 品种 | 链接 | 摘要 |")
md.append("|---|---|---|")
for s in fao_species:
    md.append(f"| **{s['zh']}** | [link]({s['url']}) | {s['intro'][:120]}... |")
md.append("")

md.append("## 🇨🇳 中国渔业协会精华 10 篇\n")
picks = cappma[:10]
for i, p in enumerate(picks, 1):
    md.append(f"### {i}. [{p['cat']}] {p['title'].split('时间')[0].strip()}")
    md.append(f"- 链接：{p['url']}\n")

md.append("## 🔥 抖音热榜水产话题\n")
md.append(dy_aqua.strip() if dy_aqua.strip() else "今日无水产相关话题\n")

md.append("## 📊 数据看板\n")
md.append(f"| 维度 | 数量 |\n|---|---|\n| FAO 报告 | 1 |\n| FAO 物种 | {len(fao_species)} |\n| 国内文章 | {len(picks)} |\n| **合计** | **{len(fao_species) + len(picks) + 1}** |\n")
md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"✅ 简报: {OUT}")
print(f"   cappma: {len(cappma)} 篇 / FAO 物种: {len(fao_species)} 种")
