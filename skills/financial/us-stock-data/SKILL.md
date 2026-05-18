---
name: us-stock-data
description: 美股数据查询工具。基于 yfinance (Yahoo Finance) + Finnhub + 新浪美股 + S&P 500。支持实时行情、K线、财务报表、标普500行业分类。
version: 1.1.0
metadata:
  hermes:
    tags: [stock, us-stock, yahoo-finance, yfinance, finnhub, sp500]
---

# US Stock Data - 美股数据查询

## Overview

本技能集成 **Finnhub (官方API)** 作为主要美股数据源 → **yfinance (Yahoo Finance)** 降级 → **AKShare 新浪美股** 终极兜底。

## 数据源优先级

```
查询行情时自动优选：
  一级 ▶️ Finnhub（官方API，可靠稳定，60次/分钟免费）
  二级 ▶️ yfinance（Yahoo内部接口，数据更丰富）
  三级 ▶️ 新浪美股国内直连（兜底）
```

| 数据源 | 方式 | 延迟 | 稳定性 | 能力 |
|--------|------|------|--------|------|
| **Finnhub** (官方API) | 硅谷隧道(8889) | ~0.5s | ⭐⭐⭐ 最高 | 行情/基本面/财务指标/新闻 |
| Yahoo Finance (yfinance) | 硅谷隧道(8889) | ~0.7s | ⭐⭐ 可能限流 | 行情/K线/财报/搜索 |
| 新浪美股 (AKShare) | 国内直连 | ~0.5s | ⭐⭐⭐ 国内稳定 | 历史日K线（备选） |
| S&P 500 (Wikipedia) | 硅谷隧道(8889) | ~0.7s | ⭐⭐ | 503只成分股/11行业 |

## Requirements

- 硅谷隧道（端口 8889）必须开启（Vultr已退役，迁移到腾讯云硅谷）
- yfinance 安装在 china-stock-data 的 venv 中
- Finnhub API Key 保存在 `~/.hermes/data/finnhub_config.json`
- 标普500数据由脚本首次查询时自动缓存到 `/tmp/sp500_constituents.csv`

## When to Use

- 查询美股实时行情（价格、PE、PB、市值、股息率、52周高/低）
- 查询美股K线（日/周/月/年）
- 查询美股财务报表（利润表、资产负债表、现金流）
- 查询标普500成分股及行业分布
- 按关键词搜索美股

## How It Works

```bash
PY=~/.hermes/skills/financial/china-stock-data/.venv/bin/python3
US=~/.hermes/skills/financial/us-stock-data/scripts/us_stock.py

# 实时行情
$PY $US quote AAPL                  # 单只
$PY $US quote NVDA,MSFT,TSLA       # 批量

# K线 (period: 1d/5d/1mo/3mo/6mo/1y/5y/max)
$PY $US kline AAPL 1mo              # 近一月日K
$PY $US kline NVDA 1y               # 近一年日K

# 财务报表
$PY $US financials NVDA             # 利润表+资产负债表+现金流

# 标普500
$PY $US sp500                       # 行业分布
$PY $US sp500 Technology            # 某行业下成分股
$PY $US sp500-refresh               # 刷新成分股数据

# 搜索
$PY $US search Nvidia               # 模糊搜索

# 代理状态
$PY $US proxy-status                # 查看代理是否可用
```

## Common Pitfalls

1. **yfinance可能限流** — Yahoo内部接口每IP有速率限制。如果遇到 yfinance 请求超时或股票信息返回为空，先用硅谷隧道检查代理：`curl -x http://127.0.0.1:8889 -s -o /dev/null -w '%{http_code}' --max-time 10 https://www.google.com`
2. **yfinance限流时的降级方案：使用 Finnhub（官方API，需API Key）**
   ```bash
   export FINNHUB_API_KEY="your_key_here"
   curl -s "https://finnhub.io/api/v1/quote?symbol=AAPL&token=$FINNHUB_API_KEY"
   ```
   Finnhub免费60次/分钟，支持行情、财报、公司新闻、IPO日历、内幕交易等，走硅谷隧道即可。
   Python集成：`pip install parsimony-finnhub`
   注册获取Key：https://finnhub.io/register
3. **再降级：使用新浪美股（AKShare，国内直连，免代理）**
   ```bash
   # 新浪美股走国内直连（不需要代理）
   export http_proxy= https_proxy=
   PY=~/.hermes/skills/financial/china-stock-data/.venv/bin/python3
   # 示例：获取标普500 ETF(SHY)行情
   $PY -c "
   import akshare as ak
   # 美股实时行情（新浪接口国内直连）
   df = ak.stock_us_spot_em()  # 全部美股实时行情
   print(df[df['代码'].str.contains('AAPL', case=False)])
   "
   ```
   注意：新浪接口只提供基础行情（价格、涨跌幅、成交量），不提供PE/PB/市值等财务指标。
4. **BRK-B类符号** — 伯克希尔等带特殊字符的股票用 `BRK-B` 参数，脚本自动转换
5. **标普500需要代理** — 首次获取成分股列表需要代理访问 Wikipedia
6. **延迟** — 硅谷隧道到Yahoo/Finnhub约 0.5-0.9s 返回

## Financial Datasets MCP (Evaluated — Not Integrated)

**Financial Datasets** (`financialdatasets.ai`) 是一个专为AI Agent设计的美股数据MCP服务器，覆盖27,000+美股，30年历史数据，实时SEC备案同步。

| 数据 | 是否支持 |
|------|---------|
| 实时行情 | ✅ |
| 财务报表(BS/IS/CF) | ✅ |
| SEC Filings | ✅ |
| 内幕交易 | ✅ |
| 机构持仓 | ✅ |
| 新闻 | ✅ |

**评估结论：不使用。** 最便宜的 Developer 套餐 $200/月（约¥1,450），相比我们现有的免费方案（yfinance+Finnhub+SEC EDGAR）没有足够差异化价值。如果要接入，需：

1. 注册账号获取API Key
2. 走硅谷隧道8889连接 MCP URL: `https://mcp.financialdatasets.ai/`
3. 安装命令: `claude mcp add --transport http financial-datasets https://mcp.financialdatasets.ai/`

仅建议在以下情况启用：①需要有结构化报表数据的Claude Code金融分析 ②yfinance/Finnhub都不可用 ③预算充足。

## Alpaca Paper Trading Integration ✅ 已完成（2026-05-17）

Alpaca 提供免费的美股Paper Trading（模拟交易），初始$100,000虚拟资金，支持股票/ETF/期权/加密货币。

### 认证方式

```python
from alpaca.trading.client import TradingClient

API_KEY = "PK5ZMJM5OF7DAA6EU2PKVXI5Z7"  # Key ID
SECRET = "8mKU43vRGzgM3QFLwdTex1n3Li5FgEGehyVxJJi5Ags1"  # Secret

# Paper Trading（模拟账户）
client = TradingClient(API_KEY, SECRET, paper=True)

# 实时交易
account = client.get_account()
print(account.cash, account.portfolio_value, account.buying_power)
```

### 关键信息

| 项目 | 值 | 
|:---|---:|
| API Key ID | `PK5ZMJM5OF7DAA6EU2PKVXI5Z7` |
| Secret Key | 保存在 `~/.hermes/data/alpaca_config.json` |
| Paper Trading URL | `https://paper-api.alpaca.markets` |
| Market Data URL | `https://data.alpaca.markets` |
| Live Trading URL | `https://api.alpaca.markets` |
| Python SDK | `pip install alpaca-py` |
| 模拟资金 | $100,000 |
| 购买力 | $200,000 (2x margin) |

### 常用操作

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

client = TradingClient(API_KEY, SECRET, paper=True)

# 买入
order = client.submit_order(MarketOrderRequest(
    symbol="SPY",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
))

# 查看持仓
positions = client.get_all_positions()

# 查看账户
account = client.get_account()
```

最新的行情数据也可通过 alpaca.data 模块获取：
```python
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.historical import StockHistoricalDataClient

data_client = StockHistoricalDataClient(API_KEY, SECRET)
quote = data_client.get_stock_latest_quote(
    StockLatestQuoteRequest(symbol_or_symbols=["SPY", "QQQ"])
)
```

### Pitfalls

- Paper账户有独立的API Key，不同于真实账户
- Paper数据源仅限IEX（免费行情），延迟略高于真实市场
- 提交订单后模拟撮合，但不计入实际订单路由和滑点
- 不可用于真实交易！

## Verification

- [x] quote AAPL → 返回价格/PE/PB/市值/股息率/52周高/低
- [x] quote NVDA,MSFT → 批量两只股票
- [x] kline AAPL 5d → 5条日K线
- [x] financials NVDA → 利润表(收入/净利润) + 资产负债表(资产/债务/现金)
- [x] sp500 → 503只，11行业
- [x] sp500 Technology → 73只科技股
- [x] search Nvidia → 匹配到NVDA

## Finnhub Integration ✅ 已完成

| 功能 | 命令 | 状态 |
|:---|:---|:---:|
| 实时行情 | `finnhub quote AAPL` | ✅ 通 |
| 公司基本面 | `finnhub profile AAPL` | ✅ 含PE/PB/股息率/52周高/低 |
| 公司新闻 | `finnhub news AAPL` | ✅ 近7天新闻 |

API Key已保存在 `~/.hermes/data/finnhub_config.json`。
所有Finnhub调用走硅谷隧道(8889)，requests直接HTTP API，无需额外Python包。

## Alpha Vantage Integration ✅ 已完成

| 功能 | 命令 | 状态 |
|:---|:---|:---:|
| 实时报价 | `av quote AAPL` | ✅ 通，自带12s限流保护 |
| 新闻情感分析 | `av news AAPL` | ✅ 含sentiment评分+正面/中性/负面标签 |
| 公司基本面 | `av overview AAPL` | ✅ PE/PB/股息率/市值/52周极值/EPS/Beta |
| RSI技术指标 | `av rsi AAPL` | ✅ 14天RSI值 |

API Key保存在 `~/.hermes/data/alphavantage_config.json`。
限流：25次/天，5次/分钟（已内置time.sleep(12)保护）。
走国内直连（不需要代理，alphavantage.co国内可访问）。
还有很多免费API可用（GOLD_SILVER_SPOT/CURRENCY_EXCHANGE_RATE/SECTOR/TOP_GAINERS_LOSERS等），完整列表见 `references/alphavantage-api.md`。

| 项目 | 值 | 验证方式 |
|:---|:---:|:---|
| 速率限制 | **60次/分钟** | 响应头 `x-ratelimit-limit: 60` |
| 重置间隔 | 1分钟 | 响应头 `x-ratelimit-reset` (Unix时间戳) |
| 免费支持的品种 | **股票/加密货币** | ✅ quote/profile/news全部免费 |
| ❌ 不支持 | **外汇(Forex)** | OANDA: / FOREX: 符号返回 403 |
| 日常用量 | ~20-30次/天 | 完全在限额内，不会被封 |

API Key保存在 `~/.hermes/data/finnhub_config.json`。
所有Finnhub调用走硅谷隧道(8889)，requests直接HTTP API，无需额外Python包。
