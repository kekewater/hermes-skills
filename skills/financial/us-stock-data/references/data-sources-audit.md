# Data Sources Audit — 2026-05-17

Comprehensive audit of all financial and utility data sources available to this agent.

## 🇨🇳 A-Stock

| Source | Type | Cost | Route | Status | Priority |
|--------|------|:----:|:-----:|:------:|:--------:|
| Tencent Finance (qt.gtimg.cn) | real-time quotes/indices | free | domestic direct | ✅ | 🥇 |
| Tongdaxin TDX (pytdx) | K-line, level-2 ticks | free | domestic direct | ✅ | 🥇 |
| Tonghuashun iFinD HTTP API | PE/TTM fundamentals | free key | domestic direct | ✅ (exp: 5/24) | 🥇 |
| AKShare (EastMoney backend) | news, filings, history | free | domestic direct | ✅ | 🥈 |
| Tornadotech AK | valuations ER/FY | free | domestic direct | ✅ | 🥉

## 🌍 Global Markets

| Source | Type | Cost | Route | Status | Priority |
|--------|------|:----:|:-----:|:------:|:--------:|
| **Finnhub** (official API) | US quotes, fundamentals, news, crypto | free (60/min) | SV tunnel | ✅ | 🥇 |
| **Alpha Vantage** (official API) | quotes, sentiment, RSI, fundamentals | free (25/day, 5/min) | domestic direct | ✅ | 🥇 (sentiment/RSI only) |
| Yahoo Finance (yfinance) | K-line, financials, search | free | SV tunnel | ✅ | 🥈 |
| Sina US stocks (AKShare) | historical daily K-line | free | domestic direct | ✅ | 🥉 |
| SEC EDGAR (edgartools) | 10-Q, 10-K, 13F | free | SV tunnel | ✅ | 🥇 |
| Wikipedia | S&P 500 constituents | free | SV tunnel | ✅ | 🥇 |

## 💰 Commodities & FX & Crypto

| Item | Source | Latest | Route | Status |
|------|--------|:------:|:-----:|:------:|
| Gold Au99.99 (CNY/g) | AKShare spot_quotations_sge() | ~1000 | domestic | ✅ |
| Gold ETF (SZ159934) | Tencent Finance | real-time | domestic | ✅ |
| Silver (CNY/kg) | AKShare spot_silver_benchmark_sge() | 21374 | domestic | ✅ |
| Brent Crude (USD/bbl) | AKShare futures_global_spot_em() | $79.3 | domestic | ✅ (slow: 52s) |
| Crude ETF (USO) | Tencent Finance | real-time | domestic | ✅ |
| USD/CNY | AKShare currency_boc_safe() | 6.8415 | domestic | ✅ |
| BTC/USD | Finnhub BINANCE:BTCUSDT | $78,507 | SV tunnel | ✅ |
| ETH/USD | Finnhub BINANCE:ETHUSDT | $2,196 | SV tunnel | ✅ |
| ⛔ Forex (EUR/USD etc.) | Finnhub OANDA | — | — | ❌ 403 (not on free) |

## 🔧 Utility Sources

| Source | Cost | Route | Status |
|--------|:----:|:-----:|:------:|
| **Tavily Search** | 1000/mo free | domestic direct | ✅ |
| AgentMail | ? | ? | ✅ (not actively used) |
| Google Maps (maps skill) | free | domestic direct | ✅ |

## 🤖 AI Models & Image Generation

| Service | Purpose | Cost | Balance | Route | Status |
|---------|---------|:----:|:-------:|:-----:|:------:|
| DeepSeek V4 Flash | primary chat | ¥2.20/day | ¥131.90 (~2mo) | direct | ✅ |
| OpenAI gpt-image-2 | report images | ~$0.055/image | $16.62 (~14mo) | SV tunnel | ✅ |
| ⛔ ChatGPT web | DALL-E 3 free | free | — | SV tunnel | ❌ (403, DC IP) |
| ⛔ OpenRouter | backup gen | key expired | — | SV tunnel | ❌ 401 |

## 🌐 Social Platforms

| Platform | Username | Status | Notes |
|----------|----------|:------:|-------|
| **WeChat** (iLink) | 小墨 | ✅ active | primary channel |
| **Moltbook** | xiao-mo-keke | ✅ active | English historical fiction |
| **The Colony** | xiao-mo-keke | ✅ active | tech/finance colony |
| InStreet | xiao_mo_keke | ⛔ closed | renovation since 2026-05-16 |

## 🏗 Infrastructure

| Machine | Location | Purpose | Cost | Status |
|---------|:--------:|---------|:----:|:------:|
| **Tencent Cloud Shanghai** (106.54.241.187) | 🇨🇳 | my body — 4C4G | paid to 2027 | ✅ |
| **Tencent Cloud Silicon Valley** (43.159.133.35) | 🇺🇸 | proxy tunnel — 2C2G | ¥20.7/mo | ✅ |
| Vultr Singapore (45.76.185.1) | 🇸🇬 | legacy proxy | $5/mo (dying) | 💤 retired |
| Vultr US (student acct) | 🇺🇸 | failed VPS | free | ❌ verification failed |

## 🚫 Blocked / Unavailable

| Resource | Code | Reason | Workaround |
|----------|:----:|--------|------------|
| chatgpt.com | 403 | datacenter IP blocked by OpenAI | use API instead |
| Finnhub Forex | 403 | not on free tier | use AKShare currency_boc_safe |
| InStreet | maintenance | closed for renovation | wait for reopen |
| OpenRouter | 401 | key expired | re-register if needed |
| Vultr student acct | verify fail | ID docs didn't clear | abandoned |

## Auto-Fallback Priority

```
US stock price → Finnhub 🥇 → yfinance 🥈 → Sina AKShare 🥉
US news       → Finnhub 🥇 → Alpha Vantage 🥈 (sentiment)
US K-line     → yfinance 🥇 → Sina AKShare 🥈
US financials → yfinance 🥇 → iFinD (A-stock only)
A-share price → Tencent 🥇 → TDX 🥈 → AKShare 🥉
FX rate       → AKShare BOC 🥇
Gold spot     → AKShare SGE 🥇 → Tencent ETF 🥈
BTC           → Finnhub 🥇
Commodities   → AKShare global futures 🥇 → Tencent ETF 🥈
```

## Key Limitations

1. **Alpha Vantage**: 25 calls/day total. Each `av news` or `av quote` or `av rsi` costs 1 call. Budget accordingly.
2. **AKShare futures_global_spot_em()**: Downloads all 620 contracts across 31 categories. Takes ~52s. Cache aggressively.
3. **Finnhub crypto**: Works on free tier via exchange prefix `BINANCE:SYMBOL`. Forex requires paid plan.
4. **Domestic sources need proxy cleared**: AKShare calls from China MUST clear `HTTP_PROXY`/`HTTPS_PROXY` env vars first, otherwise they hit proxy timeout.
5. **Tencent Finance (qt.gtimg.cn)**: Only returns data during China market hours for real-time. Historical only through separate API.
