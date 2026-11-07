# akshare 7 大坑 + mini_racer crash 修复实录

**记录时间**: 2026-06-12
**akshare 版本**: >= 1.12.0, < 2.0
**Python**: 3.11.15
**OS**: Windows 10

---

## 坑 1: stock_zh_a_spot() demjson 解析失败

### 现象
```python
import akshare as ak
df = ak.stock_zh_a_spot()
# akshare.utils.demjson.JSONDecodeError: Can not decode value starting with character '<'
```

### 原因
新浪接口 (`hq.sinajs.cn`) 偶尔返回 HTML（限流/降级页），demjson 解析失败。

### Workaround
用 stock_info_a_code_name() 拿代码列表（永远 200 + JSON）：
```python
df = ak.stock_info_a_code_name()  # 5527 行
```

实时行情跳过（反正筛选时也用不上实时价）。

---

## 坑 2: stock_zh_a_spot_tx() 不存在

```python
ak.stock_zh_a_spot_tx()
# AttributeError: module 'akshare' has no attribute 'stock_zh_a_spot_tx'
```

文档说有这个接口，源码实际没有。别浪费时间找。

---

## 坑 3: stock_zh_a_daily 单只拉数据 - 偶发失败

```python
df = ak.stock_zh_a_daily(symbol='sh600000', adjust='qfq')
# 偶发: ConnectionError, RemoteDisconnected, JSONDecodeError
```

### 修复
3 次重试 + 退避：
```python
def get_kline(code, days=60):
    for retry in range(3):
        try:
            sym = f'sh{code}' if code.startswith('6') else f'sz{code}'
            df = ak.stock_zh_a_daily(symbol=sym, adjust='qfq')
            if df is None or len(df) < 30: return None
            return df.tail(days).reset_index(drop=True)
        except Exception:
            time.sleep(0.3 * (retry + 1))
    return None
```

### 关键参数
- symbol: f'sh{code}' 或 f'sz{code}'（带前缀）
- adjust='qfq'（前复权）
- 返回列: date, open, high, low, close, volume, amount, outstanding_share, turnover

---

## 坑 4: mini_racer 崩（多线程抢资源）— 全 A 必看

### 现象
15 线程跑全 A 5527 只时崩：
```
#0 0x7ffdc70bad32 py_mini_racer/mini_racer.dll+0x158ad32
#1 0x7ffdc702e5a7 py_mini_racer/mini_racer.dll+0x14fe5a7
#2 0x7ffdc6f7827d py_mini_racer/mini_racer.dll+0x144827d
#3 0x7ffdc5e7e104 py_mini_racer/mini_racer.dll+0x34e104
... (栈追溯 15+ 层)
```

### 原因（不是被 IP 封）
akshare 内部用 py_mini_racer（mini_racer.dll）跑 JS 解析。
- 多线程抢同一进程内的 mini_racer 句柄
- 单只票失败率从 5% 飙升到 20%+
- 沪市 1700 只 15 线程 0 失败（单次请求 < 0.3s，资源竞争温和）
- 全 A 5500 只 15 线程崩（请求频率高，资源争用白热化）

### 修复
Semaphore 限速 + 间隔 sleep：
```python
import threading
sem = threading.Semaphore(6)  # 6 并发上限

def safe_pick(c):
    with sem:
        time.sleep(0.05)  # 每个请求间隔 50ms
        return pick_one(c)

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(safe_pick, c): c for c in all_codes}
    for f in as_completed(futures):
        r = f.result()
        if r: all_results.extend(r)
```

### 战绩对比

| 范围 | 线程 | 限速 | 用时 | 结果 |
|------|------|------|------|------|
| 沪市 2314 | 15 | 无 | 4'44" | OK 0 失败 |
| 全 A 5527 | 15 | 无 | (崩) | FAIL mini_racer crash |
| 全 A 5527 | 6 | 50ms | 10'17" | OK 0 失败 |

### 教训
- 不要无脑开 15+ 线程 — akshare 内部有 JS 引擎瓶颈
- 全 A 起步用 6 线程 + sleep(0.05)，再观察
- mini_racer 是进程内共享，信号量是唯一可靠隔离方式

---

## 坑 5: stock_individual_info_em 崩（Length mismatch）

### 现象
```python
info = ak.stock_individual_info_em(symbol='600301')
# Length mismatch: Expected axis has 3 elements, new values have 2 elements
```

### 原因
东财个股信息接口（f10.emoney.com.cn）某些环境格式错位。

### Workaround — HSF10 JSON 接口（超稳）
```python
import requests, json
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = f'https://emweb.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code=SH{code}'
r = requests.get(url, headers=headers, timeout=15)
data = json.loads(r.text)
jbzl = data['jbzl'][0]
print(jbzl['ORG_NAME'])         # 广西华锡有色金属股份有限公司
print(jbzl['EM2016'])           # 行业(申万): 有色金属-基本金属-锡
print(jbzl['INDUSTRYCSRC1'])    # 行业(CSRC)
print(jbzl['PROVINCE'])         # 广西
print(jbzl['REG_CAPITAL'])      # 63256.7479 万元
print(jbzl['EMP_NUM'])          # 4822
print(jbzl['ORG_PROFILE'])      # 公司简介
```

### 返回字段
- SECURITY_NAME_ABBR / SECUCODE / STR_CODEA / ORG_NAME / ORG_NAME_EN / FORMERNAME
- EM2016 (申万行业) / INDUSTRYCSRC1 (CSRC 行业) / SECURITY_TYPE (上交所主板A股)
- TRADE_MARKET / PROVINCE / ADDRESS / REG_ADDRESS
- PRESIDENT / LEGAL_PERSON / CHAIRMAN / SECRETARY
- ORG_TEL / ORG_EMAIL / ORG_WEB / ORG_FAX
- REG_CAPITAL (万元) / REG_NUM / EMP_NUM / TATOLNUMBER (总分公司数)
- LAW_FIRM / ACCOUNTFIRM_NAME
- ORG_PROFILE (公司简介 500+ 字) / BUSINESS_SCOPE (经营范围)
- 嵌套字段 fxxg[0]: FOUND_DATE / LISTING_DATE / ISSUE_PRICE / ISSUE_WAY / TOTAL_ISSUE_NUM

### URL 格式
- 沪市: code=SH600xxx / SH688xxx
- 深市: code=SZ000xxx / SZ300xxx

---

## 坑 6: 涨停判定

```python
def is_limit_up(row, prev_close):
    if prev_close <= 0: return False
    return (row['close'] - prev_close) / prev_close >= 0.095  # 9.5% 容差
```

- 主板 10% 涨停 -> 0.095 容差足够
- 创业板/科创板 20% 涨停 -> 需 >= 0.19（或单独 code.startswith('300') or code.startswith('688')）
- ST 票 5% 涨停 -> 需 >= 0.045
- 新股首日不限涨幅（北交所/创业板/科创板）

---

## 坑 7: 周末/节假日数据

akshare 的 date 列是字符串（"2026-06-11"），最后一行是最近交易日。无需判断"今天周几"。

| 跑批时间 | 数据日期 | 备注 |
|---|---|---|
| 周一晚 | 周五收盘 | 最有价值（完整周数据） |
| 周五晚 | 周五收盘 | 同上 |
| 周六/日 | 周五收盘 | 一样 |
| 节假日前 | 最后一个交易日 | 同样 |
| 节后第一天 | 节日最后一天 | （如国庆 10/7） |

### 反爬策略
- akshare 不严格限速（15 线程 1700 只 0 失败）
- 全 A 限速是为 mini_racer 资源争用，不是反爬
- 真要担心，加 time.sleep(0.1) 即可
- 失败重试 3 次够用

---

## 实战对照表

| 接口 | 是否能用 | Workaround |
|---|---|---|
| ak.stock_zh_a_spot() | demjson 崩 | 用 stock_info_a_code_name() |
| ak.stock_zh_a_spot_tx() | 不存在 | 跳过 |
| ak.stock_info_a_code_name() | OK | 首选 |
| ak.stock_zh_a_daily(symbol, adjust='qfq') | OK | 3 次重试 + 退避 |
| ak.fund_etf_spot_em() | OK | ETF 池（1507 只） |
| ak.fund_etf_hist_em() | OK | ETF 历史 K 线 |
| ak.stock_individual_info_em() | Length mismatch | 用 HSF10 JSON 接口 |
| emweb.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax | OK | 基本面首选 |
| push2.eastmoney.com/api/qt/stock/get | OK | 实时价/PE/市值 |
