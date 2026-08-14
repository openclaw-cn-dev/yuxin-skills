#!/usr/bin/env python3
# TODO(tech-debt): 应改由 Claude Code/Codex 重写（cron 沙箱无 CLI，华哥 2026-08-13 豁免）
"""
全A量化因子盘中快扫脚本 — 宽博士
================================
交易日 10:30 / 14:30 由 cron 运行，秒级完成（只用新浪批量实时价，不拉K线）。

输出(stdout): 持仓止损预警 + 沪深300核心池实时异动 Top/Bottom + 板块快照。
日志走 stderr。
"""

import urllib.request
import sys
from datetime import datetime

# 沪深300 核心池（与 daily_factor_scan.py 一致，100 只）
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

# 华哥持仓（2026-08-13）
HOLDINGS = [
    {"name": "创业AI ETF",    "code": "sz159363", "shares": 8200,  "cost": 1.208, "stop": 1.148},
    {"name": "半导体设备ETF", "code": "sz159516", "shares": 11800, "cost": 0.680, "stop": 0.680},
    {"name": "煤炭ETF",       "code": "sh515220", "shares": 2500,  "cost": 1.288, "stop": 1.224},
    {"name": "沪深300ETF",    "code": "sh510300", "shares": 600,   "cost": 5.005, "stop": None},
    {"name": "光伏ETF",       "code": "sh515790", "shares": 1700,  "cost": 0.859, "stop": 0.816},
    {"name": "军工ETF",       "code": "sh512660", "shares": 800,   "cost": 1.155, "stop": None},
]

SECTOR_MAP = {
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


def log(msg):
    print(msg, file=sys.stderr)


def fetch_realtime(codes):
    """新浪批量实时价。返回 {code: {'name','price','prev','chg'}}。"""
    result = {}
    # 分 2 批，避免 URL 过长
    batch_size = 60
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        url = 'https://hq.sinajs.cn/list=' + ','.join(batch)
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
        try:
            resp = urllib.request.urlopen(req, timeout=8)
            text = resp.read().decode('gbk', errors='ignore')
        except Exception as e:
            log(f'[WARN] 批量拉取失败: {e}')
            continue
        for line in text.strip().split('\n'):
            if 'hq_str_' not in line or '="' not in line:
                continue
            code = line.split('hq_str_')[1].split('=')[0]
            parts = line.split('"')[1].split(',')
            if len(parts) < 4:
                continue
            try:
                name = parts[0]
                prev = float(parts[2])
                price = float(parts[3])
            except (ValueError, IndexError):
                continue
            if prev <= 0:
                continue
            chg = (price - prev) / prev * 100
            result[code] = {'name': name, 'price': price, 'prev': prev, 'chg': chg}
    return result


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    codes = [c for c, _ in STOCK_POOL] + [h['code'] for h in HOLDINGS]
    rt = fetch_realtime(codes)
    log(f'[INFO] 拉取 {len(rt)}/{len(codes)} 条实时价')

    if not rt:
        print('❌ 盘中快扫失败：无实时数据。')
        return

    out = []
    out.append(f'⚡ 盘中快扫 | {now}')
    out.append('')

    # 1. 持仓预警
    out.append('【持仓预警】')
    alert_any = False
    for h in HOLDINGS:
        d = rt.get(h['code'])
        if not d:
            continue
        pnl = (d['price'] - h['cost']) / h['cost'] * 100
        flag = ''
        if h['stop'] and d['price'] <= h['stop']:
            flag = ' 🚨跌破止损线!'
            alert_any = True
        elif h['stop'] and d['price'] <= h['stop'] * 1.02:
            flag = ' 🔶逼近止损线'
            alert_any = True
        if abs(d['chg']) >= 2.5:
            flag += f" ⚡波动{d['chg']:+.1f}%"
            alert_any = True
        out.append(f"  {h['name']:<8} ¥{d['price']:<6.3f} {d['chg']:+.2f}% 浮盈{pnl:+.1f}%{flag}")
    if not alert_any:
        out.append('  ✅ 持仓无异常')

    # 2. 沪深300 异动 Top/Bottom
    pool_rt = [(c, n, rt[c]) for c, n in STOCK_POOL if c in rt]
    pool_rt.sort(key=lambda x: x[2]['chg'], reverse=True)
    out.append('')
    out.append('📈 沪深300 核心池 实时领涨 Top8:')
    for c, n, d in pool_rt[:8]:
        out.append(f"  {n} {d['chg']:+.2f}% ¥{d['price']:.2f}")
    out.append('📉 实时领跌 Bottom8:')
    for c, n, d in pool_rt[-8:][::-1]:
        out.append(f"  {n} {d['chg']:+.2f}% ¥{d['price']:.2f}")

    # 3. 板块实时快照
    sector_chg = {}
    for c, n, d in pool_rt:
        for sec, kws in SECTOR_MAP.items():
            if any(kw in n for kw in kws):
                sector_chg.setdefault(sec, []).append(d['chg'])
                break
        else:
            sector_chg.setdefault('其他', []).append(d['chg'])
    sector_avg = []
    for sec, chgs in sector_chg.items():
        if len(chgs) >= 2:
            sector_avg.append((sec, sum(chgs) / len(chgs)))
    sector_avg.sort(key=lambda x: x[1], reverse=True)
    out.append('')
    out.append('板块实时强弱:')
    for sec, avg in sector_avg[:5]:
        out.append(f"  🔴 {sec} {avg:+.2f}%")
    for sec, avg in sector_avg[-5:]:
        out.append(f"  🟢 {sec} {avg:+.2f}%")

    print('\n'.join(out))


if __name__ == '__main__':
    main()
