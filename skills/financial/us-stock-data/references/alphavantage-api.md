# Alpha Vantage API Reference

**API Key:** V03ZKLQR9FW5N7VF
**Config file:** `~/.hermes/data/alphavantage_config.json`
**Base URL:** `https://www.alphavantage.co/query`
**Auth:** `?apikey=KEY` query param
**Network:** Domestic China direct connect — no proxy needed

## Rate Limits (Free Tier)

| Limit | Value | Protection |
|---|---|---|
| Per minute | 5 calls | `time.sleep(12)` between calls |
| Per day | 25 calls | Rolling 24h window |
| On limit hit | 429 + Note in response body | Stop and wait |

Excess response body:
```json
{"Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day..."}
```
**500/day mentioned in error message is misleading** — actual limit per 2026 policy is 25/day. Track via response headers or local counter.

## Implemented Commands (us_stock.py)

| Command | AV Function | Description |
|---|---|---|
| `av quote AAPL` | `GLOBAL_QUOTE` | Real-time price, change, vol, OHLC |
| `av news AAPL` | `NEWS_SENTIMENT` | News articles + sentiment score (-1 to +1) + label |
| `av overview AAPL` | `OVERVIEW` | PE/PB/dividend yield/market cap/EPS/Beta/52w |
| `av rsi AAPL` | `RSI` | RSI(14) values over time |

## Free Tier — Available Endpoints (Not Yet Wired)

Use 25 daily calls wisely. Add these only when a need arises.

### Commodities (replaces AKShare for gold/silver/copper)
- `GOLD_SILVER_SPOT` — Real-time gold & silver spot prices
- `WTI` — Crude oil spot
- `BRENT` — Brent crude
- `COPPER`, `ALUMINUM` — Base metals
- `NATURAL_GAS` — Nat gas
- `WHEAT`, `CORN`, `COTTON`, `SUGAR`, `COFFEE` — Softs
- `ALL_COMMODITIES` — Broad commodity index

### Forex (replaces AKShare bank rates)
- `CURRENCY_EXCHANGE_RATE` — Real-time FX pair (e.g., USD/CNY)
- `FX_DAILY`, `FX_WEEKLY`, `FX_MONTHLY` — Historical FX

### Crypto
- `DIGITAL_CURRENCY_DAILY` — BTC/ETH daily history
- `CRYPTO_INTRADAY` — Intraday crypto

### Market Data
- `SECTOR` — Sector performance (real-time)
- `TOP_GAINERS_LOSERS` — Today's market movers
- `MARKET_STATUS` — Market open/close status

### Fundamentals (supplements yfinance financials)
- `INCOME_STATEMENT` — Quarterly/annual income statement
- `BALANCE_SHEET` — Balance sheet
- `CASH_FLOW` — Cash flow statement
- `EARNINGS` — Historical earnings per share
- `EARNINGS_CALENDAR` — Upcoming earnings dates
- `DIVIDENDS` — Dividend history
- `SPLITS` — Stock split history

### Economic Indicators
- `REAL_GDP`, `REAL_GDP_PER_CAPITA`
- `CPI`, `INFLATION`
- `UNEMPLOYMENT`, `NONFARM_PAYROLL`
- `TREASURY_YIELD` — US bond yields
- `FEDERAL_FUNDS_RATE` — Interest rate
- `RETAIL_SALES`, `DURABLES`

### Technical Indicators (more than just RSI)
- `SMA`, `EMA`, `WMA` — Moving averages
- `MACD`, `MACDEXT` — MACD with customizable options
- `BBANDS` — Bollinger Bands
- `STOCH`, `STOCHF`, `STOCHRSI` — Stochastic oscillators
- `ADX`, `ADXR` — Trend strength
- `CCI`, `CMO`, `ROC` — Momentum
- `ATR`, `NATR` — Volatility
- `OBV`, `AD`, `ADOSC` — Volume indicators

## Usage Notes

- **Priority:** Finnhub (0.5s, 60/min) > yfinance (0.7s) > Alpha Vantage (25/day)
- Alpha Vantage's unique value is: (1) news sentiment scoring, (2) technical indicators, (3) gold/silver/commodities spot prices
- Domestic direct connect means it works even when the Silicon Valley proxy is down
- When implementing new AV endpoints, always use `_av_get()` wrapper (handles throttling + proxy clearing)
