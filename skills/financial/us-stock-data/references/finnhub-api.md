# Finnhub API Reference

API Key: 保存在 `~/.hermes/data/finnhub_config.json`
Base URL: `https://finnhub.io/api/v1/`
Auth: `?token=<API_KEY>` 作为查询参数
代理: 走硅谷隧道 (8889)，requests + _use_proxy()

## Rate Limits (Free Tier)

从响应头读取（2026-05-17实测）：

```
x-ratelimit-limit: 60       # 每分钟60次
x-ratelimit-remaining: 59   # 剩余次数（每次调用减1）
x-ratelimit-reset: 1779014476  # 重置时间戳
```

- **无硬性日限额** — 只要不超过60次/分钟即可
- 日常20-30次/天，完全在限额内
- 不会因为使用量少被封号

## 免费版支持的端点

| 端点 | 路径 | 状态 |
|:---|:---|:---:|
| 实时行情 | `/quote?symbol=AAPL` | ✅ |
| 公司画像 | `/stock/profile2?symbol=AAPL` | ✅ |
| 财务指标 | `/stock/metric?symbol=AAPL&metric=all` | ✅ |
| 公司新闻 | `/company-news?symbol=AAPL&from=...&to=...` | ✅ |
| **加密货币** | `/quote?symbol=BINANCE:BTCUSDT` | ✅ |
| ❌ 外汇 | `/quote?symbol=OANDA:EUR_USD` | ❌ 403 Forbidden |
| ❌ 外汇K线 | `/forex/candle?symbol=...` | ❌ 403 Forbidden |

## 已集成的端点

### 实时行情 `/quote`
```
GET /quote?symbol=AAPL&token=<API_KEY>
GET /quote?symbol=BINANCE:BTCUSDT&token=<API_KEY>   # 加密货币
```
返回: `{c: 当前价, d: 涨跌额, dp: 涨跌幅%, h: 最高, l: 最低, o: 开盘, pc: 昨收, t: 时间戳}`

### 公司画像 `/stock/profile2`
```
GET /stock/profile2?symbol=AAPL&token=<API_KEY>
```
返回: `{name, exchange, finnhubIndustry, marketCapitalization, shareOutstanding, ipo}`

### 财务指标 `/stock/metric`
```
GET /stock/metric?symbol=AAPL&metric=all&token=<API_KEY>
```
返回: `metric` 字段内含 peBasicExclExtraTTM, pbQuarterly, dividendYieldIndicatedAnnual, beta, 52WeekHigh, 52WeekLow

### 公司新闻 `/company-news`
```
GET /company-news?symbol=AAPL&from=2026-05-10&to=2026-05-17&token=<API_KEY>
```
返回: 新闻列表，每项含 headline, datetime(Unix秒), source, url, summary

## 使用方式
```bash
cd ~/.hermes/skills/financial/us-stock-data
python3 scripts/us_stock.py finnhub quote AAPL                # 美股行情
python3 scripts/us_stock.py finnhub quote BINANCE:BTCUSDT     # 比特币
python3 scripts/us_stock.py finnhub profile AAPL              # 基本面
python3 scripts/us_stock.py finnhub news AAPL                 # 新闻
```

## quote() 自动降级优先顺序

```python
def quote(symbols_str):
    # 一级: Finnhub（官方API，稳定可靠，60次/分钟免费）
    r = finnhub_quote(sym)
    if 'error' not in r:
        results.append(r)
        continue
    # 二级: yfinance（Yahoo内部接口，数据更丰富，可能限流）
    ...
```

Finnhub失败 → yfinance → 新浪美股(AKShare国内直连) 三级兜底
