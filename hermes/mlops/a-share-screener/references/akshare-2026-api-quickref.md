# akshare akshare 2026-06-12 速查

## 1. 全市场代码列表
```python
import akshare as ak
df = ak.stock_info_a_code_name()  # 5527 只，列：code, name
```

## 2. 单只 K 线
```python
sym = f'sh{code}' if code.startswith('6') else f'sz{code}'
df = ak.stock_zh_a_daily(symbol=sym, adjust='qfq')  # 前复权
# 列：date, open, high, low, close, volume, amount, outstanding_share, turnover
```

## 3. ETF 数据
```python
# 实时行情
df = ak.fund_etf_spot_em()  # 1507 只，列：代码, 名称, 最新价, 涨跌幅, 成交额, ...

# 历史 K 线
df = ak.fund_etf_hist_em(symbol='588010', period='daily', start_date='20260501', end_date='20260612')
# 列：日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率
```

## 4. 个股行业/资料（反爬频繁）
```python
# 不推荐：经常失败
df = ak.stock_individual_info_em(symbol='600301')  # 报 Length mismatch
```

## 5. 行业替代：东方财富 PageAjax
```python
import requests, json
url = 'https://emweb.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code=SH600301'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 ...'}, timeout=15)
data = json.loads(r.text)
jbzl = data['jbzl'][0]
print(jbzl['ORG_NAME'])          # 公司全称
print(jbzl['EM2016'])            # 行业(申万)
print(jbzl['INDUSTRYCSRC1'])     # 行业(CSRC)
print(jbzl['EMP_NUM'])           # 员工
print(jbzl['REG_CAPITAL'])       # 注册资本(万元)
print(jbzl['ORG_PROFILE'])       # 公司简介
print(jbzl['BUSINESS_SCOPE'])    # 经营范围
```

## 6. 实时市值
```python
url = 'https://push2.eastmoney.com/api/qt/stock/get?secid=1.600301&fields=f43,f44,f45,f46,f47,f48,f60,f116,f117,f162,f167'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 ...'}, timeout=15)
d = json.loads(r.text)['data']
print(d['f43']/100, d['f162']/100, d['f116']/1e8)  # 现价/PE/总市值(亿)
```

## 7. 反爬降级链
| 接口 | 风险 | 替代 |
|---|---|---|
| `stock_zh_a_spot` | demjson 解析失败（HTML 触发）| `stock_info_a_code_name` |
| `stock_individual_info_em` | Length mismatch 错误 | 东方财富 PageAjax |
| `fund_etf_spot_em` 1507 只 | 偶发慢/超时 | 缓存 CSV 复用 |
| 多线程 15+ stock_zh_a_daily | RemoteDisconnected 崩 | 6 线程 + 50ms sleep |

## 8. 限速配方（核心）
```python
import threading
sem = threading.Semaphore(6)
def safe_pick(c):
    with sem:
        time.sleep(0.05)
        return pick_one(c)
with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(safe_pick, c) for c in codes}
```
