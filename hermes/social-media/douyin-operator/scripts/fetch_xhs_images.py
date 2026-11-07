"""
fetch_xhs_images.py — 小弟自抓小红书配图（实战验证版 2026-06-09 v3）

用法：
    from scripts.fetch_xhs_images import fetch_images
    paths = fetch_images(
        topic="白灼虾",
        queries=["基围虾 海鲜 高清", "白灼 基围虾 摆盘"],
        out_dir=r"C:\Users\Administrator\Desktop\小红书\白灼虾",
        labels=["img1", "img2", "img3", "img4"],
        count=4,
    )

原理（2026-06-09 验证）：
- Bing 图片搜 HTML scrape（不用 Bing API key）
- 关键正则：`murl&quot;:&quot;(https?://...)&quot;`（HTML 实体编码）
- 中文关键词命中率高（35/35），英文关键词基本 0
- 国内 CDN 实测通：699pic/126.net/sinaimg/alicdn
- 抓完每张必须 vision 验图，不对就跳下一个候选
"""
import os, re, urllib.parse, subprocess
from pathlib import Path

# 国内可用 CDN
CN_DOMAINS = ['qpic', '126.net', 'sinaimg', 'bdimg', 'csdn', 'sohu',
              'alicdn', '699pic', 'nipic', 'meishichina', 'k.sinaimg',
              'n.sinaimg', 'faiusr', '588ku', 'zcool', 'hellorf',
              'bcebos', 'dpsjsj', 'reefbuilders', 'rednet']

# 噪声排除（字库/百科/杂物/书法站）
NOISE = ['hanyuguoxue', 'gei6', 'hancibao', 'cidianwang', 'baike',
         'fiba', 'basketball', 'hao86', 'sandwitch', 'zidian',
         'bksy/', 'shufazhi', 'shufa', 'calligraphy', 'wenhua',
         'wudao', 'yishu', '艺术', '书法', 'fanyi']

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


def curl(url, out, timeout=15):
    """用 curl 抓单文件（沙盒外）"""
    cmd = ['curl', '-sL', '--max-time', str(timeout),
           '-A', USER_AGENT, '-e', 'https://www.bing.com/',
           '-o', out, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    return Path(out).stat().st_size if Path(out).exists() else 0


def bing_search_urls(query, n=10):
    """
    Bing 图片搜，返 URL 列表
    关键：HTML 实体编码 — 双引号是 &quot;
    """
    tmp = Path(os.environ['TEMP']) / f'bing_{abs(hash(query))}.html'
    url = (f'https://www.bing.com/images/search?q={urllib.parse.quote(query)}'
           f'&form=HDRSC2&qft=+filterui:photo-photo')
    curl(url, str(tmp), timeout=12)
    if not tmp.exists() or tmp.stat().st_size < 1000:
        return []
    html = tmp.read_text(encoding='utf-8', errors='ignore')
    # ✅ 2026-06-09 验证：murl 字段用 HTML 实体编码
    urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+?\.(?:jpg|jpeg|png|webp))&quot;', html)
    # 过滤噪声
    urls = [u for u in urls if not any(d in u for d in NOISE)]
    # 优先国内 CDN
    cn_urls = [u for u in urls if any(d in u for d in CN_DOMAINS)]
    other_urls = [u for u in urls if u not in cn_urls]
    return (cn_urls + other_urls)[:n]


def fetch_images(topic, queries, out_dir, labels, count=4, min_size_kb=80, vision_verify=None):
    """
    主函数：抓 N 张图
    topic: 用于日志/标识
    queries: 关键词列表（按序匹配 labels，找不到下一个）
    out_dir: Windows 路径（推荐 C:\\Users\\...）
    labels: N 个文件名（不带扩展名）
    count: 想要几张
    min_size_kb: 最小文件大小（KB），过滤缩略图/水印图
    vision_verify: 可选，函数 (path, label) -> bool，验图不通过返 False
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []

    for label, query in zip(labels, queries):
        candidates = bing_search_urls(query, n=8)
        ok = False
        for url in candidates[:6]:
            target = out / f'{label}.jpg'
            sz = curl(url, str(target), timeout=20)
            if sz >= min_size_kb * 1024 and _is_jpeg(str(target)):
                # vision 验图（外部传）
                if vision_verify and not vision_verify(str(target), label):
                    target.unlink(missing_ok=True)
                    print(f'  ⏭  {label}: {sz//1024}KB 验图不通过  {url[:80]}')
                    continue
                print(f'  ✅ {label}: {sz//1024}KB  {url[:80]}')
                saved.append((label, sz, url))
                ok = True
                break
            else:
                target.unlink(missing_ok=True)
        if not ok:
            print(f'  ❌ {label}: 没找到合适的（query={query}）')

    print(f'\n共 {len(saved)}/{count} 张')
    return saved


def _is_jpeg(path):
    """验证文件头是 JPEG"""
    try:
        with open(path, 'rb') as f:
            return f.read(3) == b'\xff\xd8\xff'
    except Exception:
        return False


# === 设备类关键词模板（2026-06-09 验证）===
EQUIP_QUERIES = {
    "工厂化循环水": [
        "工厂化循环水养殖 车间",
        "室内循环水养殖 鱼池",
        "循环水养殖设备 水泵",
        "工厂化养鱼车间",
    ],
    "蛋白分离器": [
        "protein skimmer",            # 英文产品名
        "reef aquarium sump",         # 英文应用场景
        "saltwater filtration system",
        "cone protein skimmer aquarium",
    ],
    "对虾养殖": [
        "对虾养殖塘 增氧机",
        "南美白对虾养殖",
        "对虾工厂化养殖",
        "对虾养殖池 投饵",
    ],
    "海鲈vs罗非": [
        "海鲈鱼 鲜活",
        "罗非鱼 鲜活",
        "海鲜市场 鲈鱼",
        "冰鲜鱼 展示",
    ],
    "循环水设备价格": [
        "水产养殖 水泵 设备",
        "池塘增氧机 叶轮",
        "生物滤池 循环水",
        "水产养殖设备",
    ],
}


# === 独立跑（命令行） ===
if __name__ == '__main__':
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else 'shrimp'

    # 设备类主题用 EQUIP_QUERIES
    if topic in EQUIP_QUERIES:
        queries = EQUIP_QUERIES[topic]
    else:
        queries = [
            f'{topic} 海鲜 高清',
            f'{topic} 摆盘',
            f'{topic} 制作',
            f'{topic} 成品',
        ]

    fetch_images(
        topic=topic,
        queries=queries,
        out_dir=rf'C:\Users\Administrator\Desktop\小红书\{topic}',
        labels=['img1', 'img2', 'img3', 'img4'],
    )
