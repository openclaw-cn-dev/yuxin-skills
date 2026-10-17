#!/usr/bin/env python3
"""定向账号免登录探测（抖音/B站）— cn-video-acquisition

用法:
  python3 bili_dy_account_probe.py bili-user <昵称>            # B站搜用户 → mid/粉丝/签名
  python3 bili_dy_account_probe.py bili-vids <mid> [limit]     # B站某UP全量视频元数据表
  python3 bili_dy_account_probe.py dy-time <aweme_id> [...]    # 抖音雪花ID → 发布时间

说明:
  - B 站接口免登录但有限频: bili-vids 内部逐条 sleep 1s。
  - 抖音侧: shipin/shipin 单视频页 SSR 无作者数据，本脚本只做雪花 ID 时间解码；
    作品列表需登录态 cookie（见 references/douyin-video-research/target-account-research.md）。
  - 详细打法与实测坑: 同目录 SKILL.md + references/douyin-video-research/target-account-research.md
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
BILI_HEADERS = {"User-Agent": UA, "Referer": "https://www.bilibili.com/", "Cookie": "buvid3=infoc"}


def _get(url):
    req = urllib.request.Request(url, headers=BILI_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def bili_user(nickname):
    q = urllib.parse.quote(nickname)
    d = _get(f"https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword={q}")
    if d.get("code") != 0:
        print(f"API err: {d.get('code')} {d.get('message')}")
        return
    for r in (d.get("data", {}).get("result") or [])[:10]:
        print(f"mid={r.get('mid')} | 昵称={r.get('uname')} | 粉丝={r.get('fans')} | 签名={(r.get('usign') or '')[:60]}")


def bili_vids(mid, limit=30):
    # BV 列表（flat-playlist 等价：走 space 接口需要 wbi 签名，这里用 view API 逐个补会拿不到列表，
    # 所以先用系列接口尝试，412 则提示走 yt-dlp --flat-playlist）
    try:
        d = _get(f"https://api.bilibili.com/x/series/recArchivesByKeywords?mid={mid}&keywords=&ps={limit}&pn=1")
        archives = (d.get("data") or {}).get("archives") if d.get("code") == 0 else None
    except Exception:
        archives = None
    bvids = [a["bvid"] for a in (archives or [])]
    if not bvids:
        print("series 接口 412/为空 → 请执行: yt-dlp --flat-playlist --print '%(id)s' "
              f"'https://space.bilibili.com/{mid}/video' 拿 BV 列表后逐个 bili-vid <bvid>")
        return
    print(f"{'bvid':<14}{'日期':<12}{'时长s':<7}{'播放':<8}{'赞':<6}{'藏':<6}{'评':<6}标题")
    for bv in bvids[:limit]:
        time.sleep(1)
        try:
            v = _get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}").get("data") or {}
        except Exception as e:
            print(f"{bv:<14}ERR {str(e)[:40]}")
            continue
        st = v.get("stat", {})
        dt = datetime.fromtimestamp(v.get("pubdate", 0)).strftime("%Y-%m-%d")
        print(f"{bv:<14}{dt:<12}{v.get('duration', 0):<7}{st.get('view', 0):<8}"
              f"{st.get('like', 0):<6}{st.get('favorite', 0):<6}{st.get('reply', 0):<6}{v.get('title', '')[:46]}")


def dy_time(aweme_ids):
    for aid in aweme_ids:
        try:
            ts = int(aid) >> 32
            print(f"{aid} -> {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            print(f"{aid} -> 非数字ID")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "bili-user":
        bili_user(sys.argv[2])
    elif cmd == "bili-vids":
        bili_vids(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
    elif cmd == "dy-time":
        dy_time(sys.argv[2:])
    else:
        print(__doc__)
