---
name: us-stock-trading
description: US stock trading via Alpaca Paper Trading API — simulation, order placement, portfolio tracking, key management.
version: 1.0.0
author: Hermes Agent (xiao-mo-keke)
tags: [alpaca, paper-trading, us-stocks, portfolio]
related_skills: [us-stock-data]
---

# US Stock Trading (Alpaca)

Setup and usage of **Alpaca Paper Trading** for simulated US stock investing. Alpaca offers commission-free API-first trading with a $100K virtual paper account for simulation.

## Credentials

- **API Key ID:** `PK5ZMJM5OF7DAA6EU2PKVXI5Z7` (saved to `~/.hermes/data/alpaca_config.json`)
- **Secret Key:** `8mKU43vRGzgM3QFLwdTex1n3Li5FgEGehyVxJJi5Ags1` (same file)
- **Paper URL:** `https://paper-api.alpaca.markets`
- **Data URL:** `https://data.alpaca.markets`
- **Account ID:** `f6844062-c2b1-4b1a-8bc1-4faf032c8794`
- **Initial Balance:** $100,000 USD

## Setup

```bash
pip install alpaca-py
```

Python test:
```python
from alpaca.trading.client import TradingClient
client = TradingClient("API_KEY", "SECRET", paper=True)
account = client.get_account()
print(account.status)  # AccountStatus.ACTIVE
```

## User Preferences (Keke)

1. **No margin/leverage** — "别上杠杆啊，我胆子小". Set buying_power to equal cash. Never use margin.
2. **Buy stocks, not just ETFs** — allowed to pick individual stocks like MSFT, NVDA, BRK.B, JPM, CVX
3. **Portfolio verification requested** — Keke wants buy prices listed in portfolio reports. Always show purchase price, current price, and P&L in reports.
4. **Single-account plan** — Paper Trading $100K, long-only, buy-and-hold with quarterly rebalance.

## Portfolio Initialization Rule ⚠️

**NEVER use simulated/historical prices to backfill portfolio entry.** User explicitly corrected: "你这收盘价买不现实呢" — portfolio must initialize with real market prices from the actual first trading day. 

Workflow:
1. Wait for next market open
2. Place real market orders through Alpaca API
3. Record actual fill prices as the buy prices
4. Only after orders execute, report portfolio status with real buy prices

## Current Portfolio (Xiao-Mo Portfolio — US Side)

| Stock | Allocation | Rationale |
|:------|:----------:|:----------|
| MSFT  | 30% | AI+cloud dual engine, most stable mega-cap |
| BRK.B | 25% | Berkshire Hathaway, Buffett's defensive shield |
| NVDA  | 20% | AI compute backbone, growth alpha |
| JPM   | 15% | Largest US bank, benefits from rate environment |
| CVX   | 10% | Energy, Berkshire Q1 new position (2026) |

Buy trigger: Next US market open after user confirms. Allocate approximately:
- MSFT: ~$30K at market price
- BRK.B: ~$25K
- NVDA: ~$20K
- JPM: ~$15K
- CVX: ~$10K

**User delegation:** "你自己定" — when user says this, proceed with execution autonomously. No need to reconfirm.

## Rebalancing Strategy

| | A-share ETF | US stock (Alpaca) |
|:---|---:|---:|
| **Frequency** | Quarterly (3/6/9/12月末) | Semi-annual (May/Nov) |
| **Trigger** | Any deviation from target | ±5% deviation from target weight |
| **Threshold to skip** | Single-side adjustment < 5% | No rebalance if all within ±5% |
| **Execution** | Manual signal to user | API auto-trade |
| **Exceptions** | Only if user says fundamentals changed or systemic risk | Same |

## Dual-Market Portfolio Structure

A-share ETF ("墨渊组合") + US stocks (Alpaca) are tracked separately but reported together:

- **A-share ETFs** (¥100,000 initial, 2026-05-18 rebuild with real-time prices):
  | ETF | Code | Weight | Shares | Cost/Share |
  |:----|:----:|:-----:|:-----:|:----------:|
  | 沪深300ETF | 510300 | 25% | 5,100 | 4.845 |
  | 中证500ETF | 510500 | 15% | 1,700 | 8.638 |
  | 创业板ETF | 159915 | 10% | 2,500 | 3.923 |
  | 科创50ETF | 588000 | 5% | 2,700 | 1.804 |
  | 国债ETF | 511010 | 20% | 100 | 141.073 |
  | 黄金ETF | 518880 | 15% | 1,500 | 9.502 |
  | 纳指ETF | 513100 | 10% | 4,800 | 2.073 |
  | Cash | — | 7.6% | — | ¥7,616.90 |
  - **Portfolio file**: `~/.hermes/portfolio/墨渊组合.json`
  - Use腾讯财经 real-time prices for daily tracking (`qt.gtimg.cn`)
  - Rebuild with `portfolio_report.py` or `portfolio_h5.py`

- **US stocks** ($100,000 initial): MSFT(30%)+BRK.B(25%)+NVDA(20%)+JPM(15%)+CVX(10%)
- Portfolio tracking managed via cron jobs (see below)

## API Usage

### Account & Positions

```python
from alpaca.trading.client import TradingClient

client = TradingClient(API_KEY, SECRET, paper=True)

# Account info
account = client.get_account()
print(account.cash, account.portfolio_value, account.buying_power)

# Positions
positions = client.get_all_positions()
for p in positions:
    print(p.symbol, p.qty, p.market_value)
```

### Market Data

Free IEX real-time data (paper accounts):
```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

data_client = StockHistoricalDataClient(API_KEY, SECRET)
quote = data_client.get_stock_latest_quote(
    StockLatestQuoteRequest(symbol_or_symbols=["SPY", "QQQ", "MSFT"])
)
for sym, q in quote.items():
    print(f"{sym}: bid ${q.bid_price:.2f} ask ${q.ask_price:.2f}")
```

**Pitfall:** Free IEX plan does NOT support historical bar requests. Paper trading accounts only get real-time quotes. For historical data, use yfinance (via proxy port 8889) or Alpha Vantage (25 req/day, domestic direct).

### Place Orders

```python
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

order = MarketOrderRequest(
    symbol="MSFT",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)
client.submit_order(order)
```

## Market Context (May 17, 2026)

S&P 500 at 7,444 (5/14 close) — recently hit ALL-TIME HIGH after a ~7% YTD correction earlier in 2026. Key factors:
- PPI 6% YoY (inflation)
- New Fed chair Kevin Warsh confirmed
- NVDA CEO joined Trump on China visit → tech sector catalyst
- Oil prices elevated (US-Iran conflict) → energy sector benefits
- "Sell in May" seasonal weakness vs. strong tech momentum

## Portfolio Monitoring & Cron Jobs (As of May 17, 2026)

Three cron jobs manage the full portfolio lifecycle:

### 1. Daily Portfolio Report + News (weekday 17:00 Beijing)
- **Job:** `ef6e544d7bf9` — "墨渊组合每日净值+新闻"
- **Trigger:** `0 17 * * 1-5` (Mon-Fri, after A-share close)
- **Sources:** A-share ETFs via JQData (close price), US stocks via Alpaca API, news via web_search
- **Report:** Combined portfolio value + daily P&L + important news on holdings
- **Delivery:** WeChat (origin chat delivery)
- **Format:** Pure text, phone-friendly, no emoji. News section only shown when significant events exist.
- **News coverage:** All 12 portfolio holdings (7 A-share ETFs + 5 US stocks), filtering for: earnings surprises >±5%, policy changes, analyst rating changes, major corporate events, macro events directly affecting holdings.
- **Merged from two separate jobs** — Keke requested combining the 9:00 net-value check and 13:00 news scan into one 17:00 report.

### 2. Weekly Portfolio Review (Saturday 9:00 Beijing)
- **Job:** `c42aec080bc4` — "墨渊组合周度复盘"
- **Trigger:** `0 9 * * 6` (Saturday, after full week data available)
- **Content:** Weekly P&L by asset, cumulative returns, asset ranking by performance, market events digest, rebalance recommendations (triggered at ±5% deviation from target)
- **Delivery:** WeChat (origin chat delivery)

### 3. Portfolio Build Script (Monday 18 May 21:30 Beijing)
- **Job:** `2f06fc93acda` — "墨渊美股建仓"
- **Trigger:** one-time at US market open (21:30 Beijing)
- **Action:** Run `~/.hermes/scripts/alpaca_build_positions.py` to place market orders for all 5 US stocks.
- ⚠️ **A-share ETF build is manual** — no trading API for A-shares, so the script calculates share quantities at open price and gives Keke a buy signal.

### Report Requirements
- MUST show buy/purchase price alongside current price
- MUST separate A-share and US stock sections clearly
- Total portfolio value (CNY) for combined view
- Include market-moving events (2-3 bullet points)
- No news = no news section (don't send empty "no news" messages)

## Key Management

**NEVER lose API keys like Moltbook verification codes.** Alpaca secret key is saved to `~/.hermes/data/alpaca_config.json`. Brief reference saved to memory. If the key is ever lost, Keke must regenerate from the Alpaca dashboard: login → API → Generate New Key.

## Scripts (Support Files)

| Script | Purpose |
|:-------|:--------|
| `scripts/alpaca_build_positions.py` | Build initial US stock portfolio via Alpaca API market orders (triggered by cron at 21:30 Beijing). **Requires `pip install alpaca-py`**. |
| `scripts/portfolio_report.py` | **Unified portfolio text report** — combines A-share ETFs (Tencent real-time prices via `qt.gtimg.cn`) + US stocks (Alpaca API) into a single text report for WeChat delivery. Run: `python3 ~/.hermes/scripts/portfolio_report.py`. Call on-demand when user says "看持仓" or "查持仓". |
| `scripts/portfolio_h5.py` | **H5 portfolio dashboard** — Flask web app serving real-time portfolio data as a mobile-friendly HTML page. Accessible at `http://106.54.241.187:3000` (requires Tencent Cloud security group to allow TCP port 3000/0.0.0.0/0). Auto-refreshes every 30s. Run: `cd ~/.hermes && python3 scripts/portfolio_h5.py &`. Kill: `pkill -f portfolio_h5.py`. |

### H5 Dashboard Display Format (final layout, confirmed 2026-05-18 after 3+ iterations)

Each holding row uses a **single 6-column CSS grid** (labels on top, values below):

```
[Top]    名称 代码
[Middle] 成本 ¥X.XXX | 现价 ¥X.XXX | 市值 ¥XX,XXX | 持仓 XX股 | 盈亏金额 +XX | 盈亏比例 +X.XX%
```

All 6 data columns (`grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr`) are in one row. The grid ensures equal-width columns and perfect alignment across rows.

**Key design decisions from user feedback (3+ layout iterations):**
1. ❌ **No daily % change (涨跌幅)** — Conflicted with total P&L since purchase when buy price differs from yesterday's close. Removed entirely.
2. ✅ **All 6 columns in one row** — 成本, 现价, 市值, 持仓, 盈亏金额, 盈亏比例 in a single CSS grid. User explicitly rejected splitting into two rows (盈亏 below the other four).
3. ✅ **Labels on top, values below** — NOT inline label-value pairs. Each column has `.lbl` (10px gray) above `.val` (14px light).
4. ✅ **Short labels** — "成本价"→"成本" to fit 6 columns on mobile screen.
5. ✅ **Shares as dedicated column** — "持仓" column with integer value, not buried in detail text.
6. ✅ **Color scheme**: 红色(#e74c3c) for profits, 绿色(#27ae60) for losses (Chinese stock convention).
7. ✅ **Horizontal scroll** for very narrow screens: `overflow-x: auto` on `.holding-row`.

**Pitfalls:**
- Flask must be started with the system Python3 (Flask installed via `pip install --break-system-packages flask`)
- If the page errors, check Flask is running (`curl -s http://127.0.0.1:3000`) and that port 3000 is open in Tencent Cloud security group
- The dashboard reads A-share portfolio from `~/.hermes/portfolio/墨渊组合.json` — if that file is missing or malformed, the page loads without data. Rebuild it with `portfolio_report.py` first.

## Related Skills

- `us-stock-data` — market data queries (yfinance, Finnhub, Alpha Vantage, Sina US)
- `daily-investment-report` — daily summary report that should include both portfolios
- `china-stock-data` — A-share market data (JQData, TDX, Tencent Finance), provider of the A-share ETF portfolio component
