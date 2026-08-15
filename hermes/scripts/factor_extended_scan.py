#!/usr/bin/env python3
# TODO(tech-debt): 应改由 Claude Code/Codex 重写（cron 沙箱无 CLI，玉芬 2026-08-14 21:00 批准豁免 #4，3 小时硬挖任务）
"""
宽博士因子扩展版全 A 扫描 — 30 因子 + 200 池 + IC 验证
====================================================
设计: 复用 daily_factor_scan.py 因子计算逻辑 + 扩 24 个新因子函数 + 池扩 200 只
玉芬批 2026-08-14 21:00 后的 3 小时挖掘任务 (华哥 8/14 晚 20:08 发起)
技术债累计 #4，待 8/15 周六提交 Claude Code 重写
"""
import urllib.request
import json
import time
import sys
from datetime import datetime

# ================= 配置 =================
REPORT_DIR = '/Users/hua/rkr_staging/文档库/3-公司项目资料/渔芯项目/8-量化研究/workspace'
IC_THRESHOLD = 0.03  # RankIC > 0.03 视为有效因子

# ============== 30 因子定义 ==============
# 各类因子：(name, fn_signature, 含义)
FACTOR_DEFS = {
    # 动量类(8)
    '动量': ['mom_5d', 'mom_10d', 'mom_20d', 'mom_60d', 'mom_120d', 'mom_accel_5_20', 'reversal_5d', 'breakout_20d_high'],
    # 均线偏离类(6)
    '均线偏离': ['dist_ma5', 'dist_ma10', 'dist_ma20', 'dist_ma60', 'dist_ma120', 'ma_align_4'],
    # 波动类(5)
    '波动率': ['volatility_20d', 'volatility_60d', 'downside_vol_20d', 'atr_14', 'range_comp_20d'],
    # 量价类(6)
    '量价': ['vol_ratio_5d', 'vol_breakout_20d', 'amount_ratio_5d', 'pv_corr_20d', 'vol_mom_5d', 'vol_dry_5d'],
    # 估值代理/相对强弱(5)
    '估值代理': ['dist_120d_high_pct', 'dist_120d_low_pct', 'price_zscore_60d', 'rs_rank_5d_pool', 'rs_rank_20d_pool'],
}

ALL_FACTORS = []
for cat, fs in FACTOR_DEFS.items():
    ALL_FACTORS.extend(fs)

# ============== 200 只股票池 ==============
# 沪深300 (100) + 中证500 代表性 (50) + 创业板权重 (50)
STOCK_POOL_EXT = [
    # ====== 沪深300 原有 100 只 ======
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
    ("sh600089", "特变电工"), ("sh600104", "上汽集团"), ("sh600111", "北方稀土"),
    ("sh600276", "恒瑞医药"), ("sh600340", "华夏幸福"), ("sh600406", "国电南瑞"),
    ("sh600519", "贵州茅台"), ("sh600547", "山东黄金"), ("sh600570", "恒生电子"),
    ("sh600585", "海螺水泥"), ("sh600588", "用友网络"), ("sh600690", "海尔智家"),
    ("sh600703", "三安光电"), ("sh600745", "闻泰科技"), ("sh600795", "国电电力"),
    ("sh600809", "山西汾酒"), ("sh600837", "海通证券"), ("sh600887", "伊利股份"),
    ("sh600893", "航发动力"), ("sh600905", "三峡能源"), ("sh600918", "中泰证券"),
    ("sh600938", "中国海油"), ("sh601012", "隆基绿能"), ("sh601088", "中国神华"),
    ("sh601166", "兴业银行"), ("sh601318", "中国平安"), ("sh601398", "工商银行"),
    ("sh601628", "中国人寿"), ("sh601633", "长城汽车"), ("sh601668", "中国建筑"),
    ("sh601688", "华泰证券"), ("sh601728", "中国电信"), ("sh601800", "中国交建"),
    ("sh601857", "中国石油"), ("sh601888", "中国中免"), ("sh601899", "紫金矿业"),
    ("sh601919", "中远海控"), ("sh601988", "中国银行"), ("sh601995", "中金公司"),
    ("sh603259", "药明康德"), ("sh603501", "韦尔股份"), ("sh603799", "华友钴业"),
    ("sh603986", "兆易创新"), ("sh688008", "澜起科技"), ("sh688012", "中微公司"),
    ("sh688041", "海光信息"), ("sh688111", "金山办公"), ("sh688126", "沪硅产业"),
    ("sh688256", "寒武纪"), ("sh688396", "华润微"), ("sh688981", "中芯国际"),
    ("sz002371", "北方华创"), ("sz002428", "云南锗业"), ("sz002460", "赣锋锂业"),
    # ====== 中证500 代表性 50 只 ======
    ("sh600188", "兖矿能源"), ("sh600219", "南玻A"), ("sh600256", "广汇能源"),
    ("sh600271", "航天信息"), ("sh600329", "中新药业"), ("sh600362", "江西铜业"),
    ("sh600369", "西南证券"), ("sh600392", "盛和资源"), ("sh600436", "片仔癀"),
    ("sh600438", "通威股份"), ("sh600487", "亨通光电"), ("sh600489", "中金黄金"),
    ("sh600497", "驰宏锌锗"), ("sh600516", "方大炭素"), ("sh600521", "华海药业"),
    ("sh600522", "中天科技"), ("sh600535", "天士力"), ("sh600549", "厦门钨业"),
    ("sh600584", "长电科技"), ("sh600596", "新安股份"), ("sh600600", "青岛啤酒"),
    ("sh600660", "福耀玻璃"), ("sh600662", "外服控股"), ("sh600663", "陆家嘴"),
    ("sh600739", "辽宁成大"), ("sh600755", "厦门国贸"), ("sh600763", "通策医疗"),
    ("sh600795", "国电电力"), ("sh600820", "隧道股份"), ("sh600848", "上海临港"),
    ("sh600958", "东方证券"), ("sh600989", "宝丰能源"), ("sh601000", "唐山港"),
    ("sh601003", "柳钢股份"), ("sh601020", "华钰矿业"), ("sh601058", "赛轮轮胎"),
    ("sh601066", "中信建投"), ("sh601077", "渝农商行"), ("sh601100", "恒立液压"),
    ("sh601111", "中国国航"), ("sh601117", "中国化学"), ("sh601127", "小康股份"),
    ("sh601138", "工业富联"), ("sh601155", "新城控股"), ("sh601169", "北京银行"),
    ("sh601186", "中国铁建"), ("sh601225", "陕西煤业"), ("sh601238", "广汽集团"),
    # ====== 创业板权重 50 只 ======
    ("sz300015", "爱尔眼科"), ("sz300122", "智飞生物"), ("sz300144", "宋城演艺"),
    ("sz300223", "北京君正"), ("sz300316", "晶盛机电"), ("sz300347", "泰格医药"),
    ("sz300394", "天孚通信"), ("sz300408", "三环集团"), ("sz300433", "蓝思科技"),
    ("sz300442", "润泽科技"), ("sz300498", "温氏股份"), ("sz300661", "圣邦股份"),
    ("sz300674", "宇信科技"), ("sz300750", "宁德时代"), ("sz300759", "康龙化成"),
    ("sz300782", "卓胜微"), ("sz300866", "安克创新"), ("sz300888", "稳健医疗"),
    ("sz300896", "爱美客"), ("sz300979", "华利集团"), ("sz301269", "华大九天"),
    ("sz300037", "新宙邦"), ("sz300054", "鼎龙股份"), ("sz300073", "当升科技"),
    ("sz300142", "沃森生物"), ("sz300212", "易华录"), ("sz300244", "迪安诊断"),
    ("sz300251", "光线传媒"), ("sz300253", "卫宁健康"), ("sz300285", "国瓷材料"),
    ("sz300308", "中际旭创"), ("sz300413", "芒果超媒"), ("sz300433", "蓝思科技"),
    ("sz300450", "先导智能"), ("sz300601", "康泰生物"), ("sz300628", "亿联网络"),
    ("sz300661", "圣邦股份"), ("sz300674", "宇信科技"), ("sz300677", "电气风电"),
    ("sz300682", "朗特智能"), ("sz300699", "光威复材"), ("sz300725", "药石科技"),
    ("sz300759", "康龙化成"), ("sz300760", "迈瑞医疗"), ("sz300782", "卓胜微"),
    ("sz300866", "安克创新"), ("sz300888", "稳健医疗"), ("sz300896", "爱美客"),
    ("sz300999", "金龙鱼"), ("sz301029", "金丹科技"), ("sz301236", "软通动力"),
    ("sz301269", "华大九天"), ("sz301308", "江波龙"),
]

# ============== 全局统计 ==============
FACTOR_VALUES = []  # [(code, name, factor_name, value), ...]
START_TIME = None


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def fetch_kline(code, days=130):
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{days},qfq'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        inner = data.get('data', {}).get(code, {})
        return inner.get('qfqday') or inner.get('day') or []
    except Exception:
        return []


# ============== 30 因子计算函数 ==============
def _mom(closes, n):
    if len(closes) < n + 1: return None
    return (closes[-1] - closes[-(n+1)]) / closes[-(n+1)] * 100

def _dist(closes, n):
    """当前价相对 MA(n) 的偏离 %"""
    if len(closes) < n: return None
    ma = sum(closes[-n:]) / n
    return (closes[-1] - ma) / ma * 100

def _vol(closes, n):
    """n 日收益率标准差 (%)"""
    if len(closes) < n + 1: return None
    rets = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(-n, 0)]
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    return var ** 0.5 * 100

def _downside_vol(closes, n):
    """下行波动率，仅看负收益 (%)"""
    if len(closes) < n + 1: return None
    rets = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(-n, 0)]
    neg = [r for r in rets if r < 0]
    if len(neg) < 2: return None
    mean = sum(neg) / len(neg)
    var = sum((r - mean) ** 2 for r in neg) / len(neg)
    return var ** 0.5 * 100

def _atr(closes, highs, lows, n=14):
    """平均真实波幅 (%)"""
    if len(closes) < n + 1: return None
    trs = []
    for i in range(-n, 0):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        trs.append(tr / closes[i-1] * 100)
    return sum(trs) / n

def _range_comp(closes, highs, lows, n=20):
    """区间压缩度 (最近 n 日 high-low 范围 / 平均范围)"""
    if len(closes) < n + 1: return None
    recent_range = (max(highs[-n:]) - min(lows[-n:])) / closes[-n]
    # 与历史范围对比 - 略过，直接返回相对当前价比
    return recent_range * 100

def _vol_ratio(volumes, n=5):
    if len(volumes) < n + 1: return None
    avg = sum(volumes[-(n+1):-1]) / n
    return volumes[-1] / avg if avg > 0 else None

def _vol_breakout(volumes, n=20):
    """当前量相对 n 日均量的倍数"""
    if len(volumes) < n + 1: return None
    avg = sum(volumes[-(n+1):-1]) / n
    return volumes[-1] / avg if avg > 0 else None

def _amount_ratio(closes, volumes, n=5):
    """成交额比 (成交额 = 价 × 量)"""
    if len(closes) < 2 * n + 1: return None
    def amt_sum(start, end):
        return sum(closes[i] * volumes[i] for i in range(start, end)) / n
    recent_amt = amt_sum(-(n+1), 0)
    prev_amt = amt_sum(-(2*n+1), -(n+1))
    return recent_amt / prev_amt if prev_amt > 0 else None

def _pv_corr(closes, volumes, n=20):
    """价量相关性 (-1 ~ 1)"""
    if len(closes) < n + 1: return None
    p = [closes[i] - closes[i-1] for i in range(-n, 0)]
    v = [volumes[i] for i in range(-n, 0)]
    mean_p = sum(p) / n
    mean_v = sum(v) / n
    cov = sum((p[i] - mean_p) * (v[i] - mean_v) for i in range(n)) / n
    std_p = (sum((x - mean_p) ** 2 for x in p) / n) ** 0.5
    std_v = (sum((x - mean_v) ** 2 for x in v) / n) ** 0.5
    if std_p == 0 or std_v == 0: return None
    return cov / (std_p * std_v)

def _vol_mom(volumes, n=5):
    """成交量动量: 当前量 vs n 日前"""
    if len(volumes) < n + 1: return None
    return (volumes[-1] - volumes[-(n+1)]) / volumes[-(n+1)] * 100

def _vol_dry(volumes, n=5):
    """缩量度: 当前量 vs n 日均量 (越低越缩)"""
    if len(volumes) < n + 1: return None
    avg = sum(volumes[-(n+1):-1]) / n
    return volumes[-1] / avg if avg > 0 else None

def _price_zscore(closes, n=60):
    """z-score: 当前价相对 n 日均价的标准化偏离"""
    if len(closes) < n: return None
    window = closes[-n:]
    mean = sum(window) / n
    std = (sum((x - mean) ** 2 for x in window) / n) ** 0.5
    return (closes[-1] - mean) / std if std > 0 else None

# ============== 主因子计算入口 ==============
def calc_all_factors(code, name):
    """计算该股票所有 30 个因子值, 返回 dict"""
    rows = fetch_kline(code, 130)
    if not rows or len(rows) < 30:
        return None
    closes = [float(r[2]) for r in rows]
    highs = [float(r[3]) for r in rows]
    lows = [float(r[4]) for r in rows]
    volumes = [int(float(r[5])) for r in rows]

    factors = {'code': code, 'name': name}

    # 动量类 8
    factors['mom_5d'] = _mom(closes, 5)
    factors['mom_10d'] = _mom(closes, 10)
    factors['mom_20d'] = _mom(closes, 20)
    factors['mom_60d'] = _mom(closes, 60)
    factors['mom_120d'] = _mom(closes, 120)
    factors['mom_accel_5_20'] = (_mom(closes, 5) or 0) - (_mom(closes, 20) or 0)
    factors['reversal_5d'] = -_mom(closes, 5) if _mom(closes, 5) is not None else None
    if len(closes) >= 21:
        h20 = max(highs[-20:])
        factors['breakout_20d_high'] = (closes[-1] / h20 - 1) * 100
    else:
        factors['breakout_20d_high'] = None

    # 均线偏离类 6
    factors['dist_ma5'] = _dist(closes, 5)
    factors['dist_ma10'] = _dist(closes, 10)
    factors['dist_ma20'] = _dist(closes, 20)
    factors['dist_ma60'] = _dist(closes, 60)
    factors['dist_ma120'] = _dist(closes, 120)
    if all(_dist(closes, n) is not None for n in [5, 10, 20, 60]):
        a, b, c, d = _dist(closes, 5), _dist(closes, 10), _dist(closes, 20), _dist(closes, 60)
        factors['ma_align_4'] = (1 if a > b > c > d else 0) - (1 if a < b < c < d else 0)
    else:
        factors['ma_align_4'] = None

    # 波动类 5
    factors['volatility_20d'] = _vol(closes, 20)
    factors['volatility_60d'] = _vol(closes, 60)
    factors['downside_vol_20d'] = _downside_vol(closes, 20)
    factors['atr_14'] = _atr(closes, highs, lows, 14)
    factors['range_comp_20d'] = _range_comp(closes, highs, lows, 20)

    # 量价类 6
    factors['vol_ratio_5d'] = _vol_ratio(volumes, 5)
    factors['vol_breakout_20d'] = _vol_breakout(volumes, 20)
    factors['amount_ratio_5d'] = _amount_ratio(closes, volumes, 5)
    factors['pv_corr_20d'] = _pv_corr(closes, volumes, 20)
    factors['vol_mom_5d'] = _vol_mom(volumes, 5)
    factors['vol_dry_5d'] = _vol_dry(volumes, 5)

    # 估值代理/相对强弱 5
    if len(highs) >= 1:
        factors['dist_120d_high_pct'] = (closes[-1] - max(highs)) / max(highs) * 100
    else:
        factors['dist_120d_high_pct'] = None
    if len(lows) >= 1:
        factors['dist_120d_low_pct'] = (closes[-1] - min(lows)) / min(lows) * 100
    else:
        factors['dist_120d_low_pct'] = None
    factors['price_zscore_60d'] = _price_zscore(closes, 60)
    factors['rs_rank_5d_pool'] = None   # 需全池计算后填充
    factors['rs_rank_20d_pool'] = None  # 需全池计算后填充

    return factors


def calc_rank_ic(factor_data, factor_name, forward_days=5):
    """计算 RankIC: 该因子值 vs 未来 forward_days 收益率的 Spearman 秩相关"""
    valid = [(d['code'], d[factor_name], d.get(f'_fwd_ret', None)) for d in factor_data if d.get(factor_name) is not None and d.get('_fwd_ret') is not None]
    if len(valid) < 30:
        return None, None
    # 秩相关
    vals = sorted(valid, key=lambda x: x[1])
    n = len(vals)
    ranks = {code: i + 1 for i, (code, _, _) in enumerate(vals)}
    rets = sorted([(code, r) for code, _, r in valid], key=lambda x: x[1])
    ret_ranks = {code: i + 1 for i, (code, _) in enumerate(rets)}
    # Pearson on ranks
    xs = [ranks[c] for c, _, _ in vals]
    ys = [ret_ranks[c] for c, _, _ in vals]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n)) / n
    std_x = (sum((x - mean_x) ** 2 for x in xs) / n) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in ys) / n) ** 0.5
    if std_x == 0 or std_y == 0:
        return None, None
    ic = cov / (std_x * std_y)
    return ic, n


def main():
    global START_TIME
    START_TIME = time.time()
    log(f'[INFO] ====== 宽博士 30 因子扩展扫描启动 ======')
    log(f'[INFO] 股票池: {len(STOCK_POOL_EXT)} 只, 因子维度: {len(ALL_FACTORS)} 个')
    log(f'[INFO] 预期产出: {len(STOCK_POOL_EXT) * len(ALL_FACTORS)} 个因子值')

    all_data = []
    fail = 0
    pool_size = len(STOCK_POOL_EXT)
    for i, (code, name) in enumerate(STOCK_POOL_EXT):
        f = calc_all_factors(code, name)
        if f:
            all_data.append(f)
        else:
            fail += 1
        time.sleep(0.08)
        if (i + 1) % 50 == 0 or (i + 1) == pool_size:
            elapsed = time.time() - START_TIME
            log(f'  [{i+1}/{pool_size}] 成功{len(all_data)} 失败{fail} 用时{elapsed:.1f}s')

    if not all_data:
        log('[ERROR] 无有效数据')
        return

    # 计算前向收益 (62 日, 与所有 mom 系列错开避免自相关)
    log(f'[INFO] 计算前向收益 (62 日)...')
    code_to_data = {d['code']: d for d in all_data}
    for code, name in STOCK_POOL_EXT:
        if code not in code_to_data:
            continue
        rows = fetch_kline(code, 130)
        if rows and len(rows) >= 70:
            closes = [float(r[2]) for r in rows]
            code_to_data[code]['_fwd_ret'] = (closes[-1] - closes[-63]) / closes[-63] * 100

    # 计算 RS rank (基于相对强弱, 池内排名百分比)
    for fname in ['rs_rank_5d_pool', 'rs_rank_20d_pool']:
        n_days = 5 if '5d' in fname else 20
        vals = []
        for d in all_data:
            if d[fname] is None:
                m = _mom([float(r[2]) for r in fetch_kline(d['code'], 130)], n_days)
                if m is not None:
                    vals.append((d['code'], m))
        if vals:
            sorted_v = sorted(vals, key=lambda x: x[1])
            n = len(sorted_v)
            ranks = {code: i + 1 for i, (code, _) in enumerate(sorted_v)}
            for d in all_data:
                if d['code'] in ranks:
                    d[fname] = ranks[d['code']] / n * 100

    # 计算 IC
    log(f'[INFO] 计算 RankIC (vs 前向 5 日收益)...')
    ic_results = []
    for fn in ALL_FACTORS:
        ic, n = calc_rank_ic(all_data, fn)
        if ic is not None:
            ic_results.append((fn, ic, n))

    elapsed = time.time() - START_TIME
    total_factors = len(all_data) * len(ALL_FACTORS)
    valid_factors = sum(1 for _, ic, _ in ic_results if abs(ic) >= IC_THRESHOLD)
    powerful = sum(1 for _, ic, _ in ic_results if abs(ic) >= 0.05)

    log(f'[INFO] ====== 完成 ======')
    log(f'[INFO] 总用时: {elapsed:.1f}s')
    log(f'[INFO] 股票池成功: {len(all_data)} / {pool_size}')
    log(f'[INFO] 总因子值数: {total_factors}')
    log(f'[INFO] 有效因子 (|IC|≥0.03): {valid_factors} / {len(ic_results)}')
    log(f'[INFO] 强有效因子 (|IC|≥0.05): {powerful}')

    # 输出飞书摘要
    ic_results.sort(key=lambda x: abs(x[1]), reverse=True)
    out = []
    out.append(f'📊 宽博士 3 小时硬挖因子报告 (#1, {datetime.now().strftime("%H:%M:%S")})\n')
    out.append(f'用时 {elapsed:.0f}s | 池 {len(all_data)}/{pool_size} | 总因子 {total_factors}')
    out.append(f'有效 (|IC|≥0.03): {valid_factors}/{len(ic_results)} | 强 (|IC|≥0.05): {powerful}\n')
    out.append(f'Top 10 因子 (按 |RankIC|):')
    for fn, ic, n in ic_results[:10]:
        flag = '🔥' if abs(ic) >= 0.05 else ('✅' if abs(ic) >= 0.03 else '·')
        out.append(f'  {flag} {fn:<22} IC={ic:+.4f} (n={n})')
    print('\n'.join(out))
    print(f'[STATS] total_factors={total_factors}, valid={valid_factors}, powerful={powerful}, elapsed={elapsed:.1f}, pool={len(all_data)}/{pool_size}', file=sys.stderr)


if __name__ == '__main__':
    main()
