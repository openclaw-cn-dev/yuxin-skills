#!/usr/bin/env python3
# TODO(tech-debt): 应改由 Claude Code/Codex 重写（cron 沙箱无 CLI，华哥 2026-08-13 豁免技术债 #4 延续）
"""
全A量化因子每日扫描脚本（收盘版）— 宽博士
========================================
交易日 15:40 由 cron 运行，输出飞书摘要(stdout) + 完整报告(md 落盘)。

覆盖: 沪深300 核心 100 只（硬编码，成分股接口沙箱不通，退而求其次）
因子: 动量(5/20/60日) / RSI(14) / 量比(5日,收盘后可靠) / 趋势(MA排列) / 突破(20日高) / 估值代理(距120日高)
信号评分(5项): 被低估(距120日高≤-25%) + 20日动量(+) + 连续上涨(≥3日) + 趋势确立(多头/金叉) + 突破20日高(≥-1%)

stdout 输出 = 飞书投递内容(纯文本)；日志/调试全部走 stderr。
"""

import urllib.request
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# ================= 配置 =================
REPORT_DIR = '/Users/hua/rkr_staging/文档库/3-公司项目资料/渔芯项目/8-量化研究/workspace'

# 沪深300 核心池（100 只，硬编码）。格式: (腾讯代码, 名称)
STOCK_POOL = [
    ("sz000768", "中航西飞"), ("sz000963", "华东医药"), ("sz002236", "大华股份"),
    ("sz002415", "海康威视"), ("sz002475", "立讯精密"), ("sz002736", "国信证券"),
    ("sz300033", "同花顺"), ("sz300059", "东方财富"), ("sh600009", "上海机场"),
    ("sh600015", "华夏银行"), ("sh600018", "上港集团"), ("sz000001", "平安银行"),
    ("sz000063", "中兴通讯"), ("sz000100", "TCL科技"), ("sz000157", "中联重科"),
    ("sz000333", "美的集团"), ("sz000425", "徐工机械"), ("sz000538", "云南白药"),
    ("sz000568", "泸州老窖"), ("sz000625", "长安汽车"), ("sz000776", "广发证券"),
    ("sz000858", "五粮液"), ("sz000895", "双汇发展"), ("sz000938", "紫光股份"),
    ("sz001979", "招商蛇口"), ("sz002027", "分众传媒"), ("sz002142", "宁波银行"),
    ("sz002230", "科大讯飞"), ("sz002241", "歌尔股份"), ("sz002304", "洋河股份"),
    ("sz002594", "比亚迪"), ("sz002714", "牧原股份"), ("sz300124", "汇川技术"),
    ("sh600000", "浦发银行"), ("sh600010", "包钢股份"), ("sh600016", "民生银行"),
    ("sh600019", "宝钢股份"), ("sh600029", "南方航空"), ("sh600031", "三一重工"),
    ("sh600028", "中国石化"), ("sh600030", "中信证券"), ("sh600036", "招商银行"),
    ("sh600050", "中国联通"), ("sh600061", "国投资本"), ("sh600085", "同仁堂"),
    ("sh600115", "中国东航"), ("sh600196", "复星医药"), ("sh600276", "恒瑞医药"),
    ("sh600309", "万华化学"), ("sh600362", "江西铜业"), ("sh600406", "国电南瑞"),
    ("sh600519", "贵州茅台"), ("sh600547", "山东黄金"), ("sh600585", "海螺水泥"),
    ("sh600741", "华域汽车"), ("sh600886", "国投电力"), ("sh600893", "航发动力"),
    ("sh600900", "长江电力"), ("sh601006", "大秦铁路"), ("sh601088", "中国神华"),
    ("sh601111", "中国国航"), ("sh601166", "兴业银行"), ("sh601186", "中国铁建"),
    ("sh601211", "国泰海通"), ("sh601225", "陕西煤业"), ("sh601288", "农业银行"),
    ("sh601328", "交通银行"), ("sh601336", "新华保险"), ("sh601390", "中国中铁"),
    ("sh601601", "中国太保"), ("sh601618", "中国中冶"), ("sh600048", "保利发展"),
    ("sh600104", "上汽集团"), ("sh600111", "北方稀土"), ("sh600570", "恒生电子"),
    ("sh600588", "用友网络"), ("sh600660", "福耀玻璃"), ("sh600690", "海尔智家"),
    ("sh600795", "国电电力"), ("sh600887", "伊利股份"), ("sh600958", "东方证券"),
    ("sh600999", "招商证券"), ("sh601009", "南京银行"), ("sh601021", "春秋航空"),
    ("sh601169", "北京银行"), ("sh601318", "中国平安"), ("sh601377", "兴业证券"),
    ("sh601398", "工商银行"), ("sh601600", "中国铝业"), ("sh601628", "中国人寿"),
    ("sh601668", "中国建筑"), ("sh601688", "华泰证券"), ("sh601788", "光大证券"),
    ("sh601818", "光大银行"), ("sh601633", "长城汽车"), ("sh601669", "中国电建"),
    ("sh601766", "中国中车"), ("sh601800", "中国交建"), ("sh601857", "中国石油"),
    ("sh601888", "中国中免"),
]

# 华哥当前持仓（2026-08-13 收盘）
HOLDINGS = [
    {"name": "创业AI ETF",    "code": "sz159363", "shares": 8200,  "cost": 1.208, "stop": 1.148},
    {"name": "半导体设备ETF", "code": "sz159516", "shares": 11800, "cost": 0.680, "stop": 0.680},
    {"name": "煤炭ETF",       "code": "sh515220", "shares": 2500,  "cost": 1.288, "stop": 1.224},
    {"name": "沪深300ETF",    "code": "sh510300", "shares": 600,   "cost": 5.005, "stop": None},
    {"name": "光伏ETF",       "code": "sh515790", "shares": 1700,  "cost": 0.859, "stop": 0.816},
    {"name": "军工ETF",       "code": "sh512660", "shares": 800,   "cost": 1.155, "stop": None},
]


def log(msg):
    print(msg, file=sys.stderr)


def fetch_kline(code, days=130):
    """拉取腾讯 K 线（日线，前复权）。失败返回 []。"""
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{days},qfq'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        inner = data.get('data', {}).get(code, {})
        return inner.get('qfqday') or inner.get('day') or []
    except Exception:
        return []


def calc_ma(closes, window):
    if len(closes) < window:
        return None
    return sum(closes[-window:]) / window


def calc_rsi(closes, window=14):
    if len(closes) < window + 1:
        return None
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas[-window:]]
    losses = [-d if d < 0 else 0 for d in deltas[-window:]]
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_volume_ratio(volumes, window=5):
    """量比: 当日量 / 前 N 日均量。收盘后当日量为完整量，可靠。"""
    if len(volumes) < window + 1:
        return None
    recent = volumes[-(window+1):-1]
    avg = sum(recent) / len(recent)
    if avg == 0:
        return None
    return volumes[-1] / avg


def calc_consecutive_up(closes, n=3):
    if len(closes) < n + 1:
        return 0
    count = 0
    for i in range(-1, -(n+1), -1):
        if closes[i] > closes[i-1]:
            count += 1
        else:
            break
    return count


def calc_ma_alignment(ma5, ma10, ma20, ma60):
    if None in (ma5, ma10, ma20, ma60):
        return '数据不足'
    if ma5 > ma10 > ma20 > ma60:
        return '多头排列'
    if ma5 < ma10 < ma20 < ma60:
        return '空头排列'
    if ma5 > ma10 > ma20:
        return '短期偏多'
    if ma5 < ma10 < ma20:
        return '短期偏空'
    if ma5 > ma20 and ma10 < ma20:
        return '金叉初现'
    if ma5 < ma20 and ma10 > ma20:
        return '死叉初现'
    return '交叉纠缠'


def analyze_stock(code, name):
    rows = fetch_kline(code, 130)
    if not rows or len(rows) < 30:
        return None
    closes = [float(r[2]) for r in rows]
    highs = [float(r[3]) for r in rows]
    lows = [float(r[4]) for r in rows]
    volumes = [int(float(r[5])) for r in rows]

    latest = closes[-1]
    prev = closes[-2]
    chg = (latest - prev) / prev * 100

    ma5 = calc_ma(closes, 5)
    ma10 = calc_ma(closes, 10)
    ma20 = calc_ma(closes, 20)
    ma60 = calc_ma(closes, 60)

    mom_5d = (closes[-1] - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 else None
    mom_20d = (closes[-1] - closes[-21]) / closes[-21] * 100 if len(closes) >= 21 else None
    mom_60d = (closes[-1] - closes[-61]) / closes[-61] * 100 if len(closes) >= 61 else None

    rsi14 = calc_rsi(closes, 14)
    vol_ratio = calc_volume_ratio(volumes, 5)

    high_20 = max(highs[-20:]) if len(highs) >= 20 else None
    breakout_20 = (latest / high_20 - 1) * 100 if high_20 else None

    high_120 = max(highs)
    dist_from_high = (latest - high_120) / high_120 * 100

    consec_up = calc_consecutive_up(closes, 3)
    align = calc_ma_alignment(ma5, ma10, ma20, ma60)

    # 5 项信号
    undervalued = 1 if dist_from_high <= -25 else 0
    short_mom = 1 if (mom_20d is not None and mom_20d > 0) else 0
    consec_sig = 1 if consec_up >= 3 else 0
    trend_sig = 1 if ('多头' in align or '金叉' in align) else 0
    breakout_sig = 1 if (breakout_20 is not None and breakout_20 >= -1.0) else 0

    score = undervalued + short_mom + consec_sig + trend_sig + breakout_sig

    return {
        'code': code, 'name': name, 'price': round(latest, 2), 'chg': round(chg, 2),
        'mom5': round(mom_5d, 2) if mom_5d is not None else None,
        'mom20': round(mom_20d, 2) if mom_20d is not None else None,
        'mom60': round(mom_60d, 2) if mom_60d is not None else None,
        'rsi': round(rsi14, 2) if rsi14 else None,
        'vol': round(vol_ratio, 2) if vol_ratio else None,
        'breakout': round(breakout_20, 2) if breakout_20 is not None else None,
        'dist': round(dist_from_high, 2),
        'consec': consec_up, 'align': align, 'score': score,
        'sig': {'undervalued': undervalued, 'short_mom': short_mom, 'consec': consec_sig,
                'trend': trend_sig, 'breakout': breakout_sig},
    }


def get_holding_prices():
    """用新浪批量实时价拉持仓 6 只 ETF 最新价。"""
    codes = [h['code'] for h in HOLDINGS]
    url = 'https://hq.sinajs.cn/list=' + ','.join(codes)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
    try:
        resp = urllib.request.urlopen(req, timeout=8)
        text = resp.read().decode('gbk', errors='ignore')
    except Exception as e:
        log(f'[WARN] 持仓价拉取失败: {e}')
        return {}
    result = {}
    for line in text.strip().split('\n'):
        if '="' not in line:
            continue
        code = line.split('hq_str_')[1].split('=')[0]
        parts = line.split('"')[1].split(',')
        if len(parts) >= 4 and parts[3]:
            result[code] = float(parts[3])
    return result


def build_holding_section(prices):
    lines = []
    lines.append('')
    lines.append('【华哥持仓体检】')
    total_cost = 0
    total_mkt = 0
    for h in HOLDINGS:
        p = prices.get(h['code'])
        if p is None:
            lines.append(f"  {h['name']}: 数据缺失")
            continue
        cost_total = h['shares'] * h['cost']
        mkt = h['shares'] * p
        pnl_pct = (p - h['cost']) / h['cost'] * 100
        total_cost += cost_total
        total_mkt += mkt
        stop_flag = ''
        if h['stop'] and p <= h['stop']:
            stop_flag = ' ⚠️跌破止损线!'
        elif h['stop'] and p <= h['stop'] * 1.02:
            stop_flag = ' 🔶逼近止损线'
        lines.append(f"  {h['name']:<8} ¥{p:<6.3f} {pnl_pct:+.1f}% 止损{h['stop'] if h['stop'] else '—'}{stop_flag}")
    pnl = total_mkt - total_cost
    pnl_pct = pnl / total_cost * 100 if total_cost else 0
    lines.append(f"  合计 成本¥{total_cost:,.0f} 市值¥{total_mkt:,.0f} 浮盈{'+' if pnl >= 0 else ''}{pnl:,.0f}({pnl_pct:+.2f}%)")
    return '\n'.join(lines)


def main():
    start = time.time()
    log(f'[INFO] 开始扫描 {len(STOCK_POOL)} 只...')
    results = []
    fail = 0
    for i, (code, name) in enumerate(STOCK_POOL):
        r = analyze_stock(code, name)
        if r:
            results.append(r)
        else:
            fail += 1
        time.sleep(0.12)
        if (i + 1) % 30 == 0:
            log(f'  [{i+1}/{len(STOCK_POOL)}] 成功{len(results)} 失败{fail}')

    elapsed = time.time() - start
    log(f'[INFO] 完成 {len(results)} 只, 失败 {fail}, 耗时 {elapsed:.1f}s')

    if not results:
        print('❌ 因子扫描失败：无有效数据。请检查网络。')
        return

    results.sort(key=lambda x: x['score'], reverse=True)

    # 共振池: 信号分≥3 且 RSI<75（剔超买）
    resonance = [r for r in results if r['score'] >= 3 and (r['rsi'] or 50) < 75]

    # 板块汇总
    sector_map = {
        '银行': ['银行', '农商', '工商', '建设', '交通', '华夏', '民生', '浦发', '兴业', '招商银行', '平安银行', '农业银行', '北京银行', '南京银行', '光大银行', '宁波银行'],
        '白酒': ['茅台', '五粮液', '泸州', '汾酒', '古井', '舍得', '洋河'],
        '新能源': ['锂电', '宁德', '比亚迪', '阳光', '隆基', '通威', '光伏', '新能源', '汇川'],
        '半导体': ['半导体', '芯片', '中芯', '韦尔', '兆易', '卓胜', '澜起', '寒武纪', '立讯', '歌尔', '海康', '大华'],
        '医药': ['医药', '恒瑞', '复星', '云南白药', '同仁堂', '华东'],
        '军工': ['航空', '航天', '船舶', '军工', '航发', '中航'],
        '汽车': ['汽车', '长城', '长安', '上汽', '华域', '福耀'],
        '地产': ['地产', '保利', '招商蛇口'],
        '有色': ['有色', '紫金', '铜业', '铝业', '稀土', '山东黄金', '中金'],
        '煤炭': ['煤炭', '中国神华', '陕西煤业'],
        '钢铁': ['钢铁', '宝钢', '包钢'],
        '基建': ['建筑', '中国建筑', '中国中铁', '中国铁建', '中国交建', '中国中冶', '中国电建', '基建', '中联重科', '三一', '徐工'],
        '通信': ['通信', '中兴', '中国联通'],
        '计算机': ['计算机', '软件', '科大', '用友', '恒生', '同花顺', '东方财富'],
        '消费': ['伊利', '海天', '双汇', '美的', '海尔', '牧原', '中国中免'],
        '券商': ['证券', '中信', '国泰', '华泰', '广发', '东方', '兴业证券', '招商证券', '国信', '光大证券'],
        '能源': ['中国石油', '中国石化', '长江电力', '国电电力', '国投电力', '大秦'],
        '化工': ['化工', '万华'],
    }
    sector_stats = {}
    for r in results:
        for sec, kws in sector_map.items():
            if any(kw in r['name'] for kw in kws):
                sector_stats.setdefault(sec, []).append(r)
                break
        else:
            sector_stats.setdefault('其他', []).append(r)

    sector_summary = []
    for sec, lst in sector_stats.items():
        if len(lst) < 2:
            continue
        avg_mom = sum(r['mom20'] or 0 for r in lst) / len(lst)
        sector_summary.append((sec, len(lst), avg_mom))
    sector_summary.sort(key=lambda x: x[2], reverse=True)

    # 持仓价
    prices = get_holding_prices()
    holding_section = build_holding_section(prices)

    today = datetime.now().strftime('%Y-%m-%d')
    date8 = datetime.now().strftime('%Y%m%d')

    # ===== 落盘完整报告 md =====
    md = []
    md.append(f'# 全A量化因子扫描 | {today} 收盘')
    md.append('')
    md.append(f'- 样本: 沪深300核心 {len(results)}/{len(STOCK_POOL)} 只，耗时 {elapsed:.1f}s')
    md.append(f'- 因子: 动量(5/20/60日) / RSI14 / 量比5日 / MA排列 / 突破20日高 / 距120日高')
    md.append('')
    md.append('## 1. 双信号共振池 (信号分≥3, RSI<75)')
    md.append('')
    md.append('| 代码 | 名称 | 现价 | 日% | 20日% | 量比 | RSI | 距高% | 排列 | 分 |')
    md.append('|---|---|---|---|---|---|---|---|---|---|')
    for r in resonance:
        md.append(f"| {r['code']} | {r['name']} | {r['price']} | {r['chg']:+.2f} | {r['mom20']:+.2f} | {r['vol']} | {r['rsi']} | {r['dist']:+.2f} | {r['align']} | {r['score']}/5 |")
    md.append('')
    md.append('## 2. Top 20 信号最强')
    md.append('')
    for i, r in enumerate(results[:20]):
        md.append(f"{i+1}. {r['code']} {r['name']} ¥{r['price']} 日{r['chg']:+.2f}% 20日{r['mom20']:+.2f}% RSI{r['rsi']} 距高{r['dist']:+.2f}% {r['align']} {r['score']}/5")
    md.append('')
    md.append('## 3. Bottom 20 信号最弱')
    md.append('')
    for i, r in enumerate(results[-20:][::-1]):
        md.append(f"{i+1}. {r['code']} {r['name']} ¥{r['price']} 日{r['chg']:+.2f}% 20日{r['mom20']:+.2f}% RSI{r['rsi']} 距高{r['dist']:+.2f}% {r['align']} {r['score']}/5")
    md.append('')
    md.append('## 4. 板块 20日均涨幅排序')
    md.append('')
    for sec, cnt, avg_mom in sector_summary:
        md.append(f'- {sec}({cnt}只): {avg_mom:+.2f}%')
    md.append('')
    md.append('## 5. 华哥持仓对比')
    md.append('')
    md.append(holding_section.replace('\n', '\n\n').replace('  ', ' '))

    out_md = f'{REPORT_DIR}/factor_scan_{date8}.md'
    Path(out_md).write_text('\n'.join(md), encoding='utf-8')
    log(f'[INFO] 报告: {out_md}')

    # ===== 飞书摘要 (stdout) =====
    out = []
    out.append(f'📊 全A量化因子扫描 | {today} 收盘')
    out.append('')
    out.append(f'样本 {len(results)}/{len(STOCK_POOL)} 只 · 耗时{elapsed:.0f}s')
    out.append('')
    out.append(f'🎯 双信号共振池({len(resonance)}只):')
    if resonance:
        for r in resonance[:10]:
            out.append(f"  {r['name']} {r['code']} ¥{r['price']} 20日{r['mom20']:+.1f}% 距高{r['dist']:+.1f}% {r['align']} ({r['score']}/5)")
    else:
        out.append('  （今日无满足 3/5 信号个股，市场偏弱）')
    out.append('')
    out.append('📈 板块领涨 Top3:')
    for sec, cnt, avg_mom in sector_summary[:3]:
        out.append(f'  {sec}({cnt}只) 20日均{avg_mom:+.2f}%')
    out.append('📉 板块领跌 Bottom3:')
    for sec, cnt, avg_mom in sector_summary[-3:]:
        out.append(f'  {sec}({cnt}只) 20日均{avg_mom:+.2f}%')
    out.append(holding_section)
    out.append('')
    out.append(f'完整报告: {out_md}')

    print('\n'.join(out))


if __name__ == '__main__':
    main()
