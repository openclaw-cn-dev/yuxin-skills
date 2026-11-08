# FAO GLOBFISH 13 物种页 — 真实可用清单（2026-06-08 实测）

## 真实可抓的 14 个 URL（含 SOFIA）

```text
# 1. SOFIA 蓝色转型旗舰报告（必抓）
https://www.fao.org/fishery/en/sofia

# 2-14. GLOBFISH 13 物种
https://www.fao.org/in-action/globefish/species-analysis/pangasius/en
https://www.fao.org/in-action/globefish/species-analysis/salmon/en
https://www.fao.org/in-action/globefish/species-analysis/shrimps/en         ← 注意 s
https://www.fao.org/in-action/globefish/species-analysis/tilapia/en
https://www.fao.org/in-action/globefish/species-analysis/tuna/en
https://www.fao.org/in-action/globefish/species-analysis/seabass-and-seabream/en
https://www.fao.org/in-action/globefish/species-analysis/lobster/en
https://www.fao.org/in-action/globefish/species-analysis/crab/en
https://www.fao.org/in-action/globefish/species-analysis/cephalopods/en
https://www.fao.org/in-action/globefish/species-analysis/bivalves/en
https://www.fao.org/in-action/globefish/species-analysis/seaweed/en
https://www.fao.org/in-action/globefish/species-analysis/groundfish/en
https://www.fao.org/in-action/globefish/species-analysis/small-pelagics/en
```

## 一键抓 + 解析脚本

```python
import os, json, urllib.request, re
SLUGS = ["pangasius","salmon","shrimps","tilapia","tuna",
         "seabass-and-seabream","lobster","crab","cephalopods",
         "bivalves","seaweed","groundfish","small-pelagics"]
ZH = {"pangasius":"巴沙鱼","salmon":"三文鱼","shrimps":"对虾",
      "tilapia":"罗非鱼","tuna":"金枪鱼",
      "seabass-and-seabream":"鲈鱼/鲷鱼","lobster":"龙虾","crab":"螃蟹",
      "cephalopods":"头足类","bivalves":"双壳贝类","seaweed":"海藻",
      "groundfish":"底栖鱼","small-pelagics":"小型中上层鱼"}

results = []
for s in SLUGS:
    url = f"https://www.fao.org/in-action/globefish/species-analysis/{s}/en"
    html = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}),
        timeout=10).read().decode("utf-8","ignore")
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    paras = [p for p in re.split(r"\.\s", txt) if len(p) > 100]
    results.append({"zh": ZH[s], "slug": s, "url": url,
                    "intro": ". ".join(paras[:3])[:600]})
    print(f"  ✓ {ZH[s]}: {len(html)} bytes")

# SOFIA 蓝色转型
sofa = urllib.request.urlopen(
    urllib.request.Request("https://www.fao.org/fishery/en/sofia",
                           headers={"User-Agent":"Mozilla/5.0"}),
    timeout=12).read().decode("utf-8","ignore")
sofa_txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sofa))
print(f"\n✓ SOFIA: {len(sofa)} bytes, "
      f"2.14 亿吨数据: {'214 million tonnes' in sofa_txt}")

# 保存
out = r"C:\Users\Administrator\Desktop\知识库\fao_raw.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"species": results, "sofia_intro": sofa_txt[:2000]},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nSaved: {out}")
```

## 关键引文（可直接抄进简报）

> "Total fisheries and aquaculture production reached an all-time record of **214 million tonnes**."
> "Aquatic food production is forecast to increase by a further **15% by 2030**."
> — FAO State of World Fisheries and Aquaculture 2024

## 4 个 SOFIA 报告 PDF 直链（备用）

- https://www.fao.org/3/cc0461en/cc0461en.pdf （2024 SOFIA，237 KB）
- https://www.fao.org/3/cc4775en/cc4775en.pdf （另一份，295 KB）

## 失败 URL 列表（**别再试**）

- `https://www.fao.org/newsroom/detail/state-of-world-fisheries-and-aquaculture-2024/en` → 404
- `https://www.fao.org/in-action/globefish/species-analysis/shrimp/en` → 404（少 s）
- `https://www.fao.org/fishery/en/2023` → 200 但内容是导航页
