# Alpaca Paper Trading Setup (2026-05-17)

## Account Info
- API Key ID: `PK5ZMJM5OF7DAA6EU2PKVXI5Z7`
- Secret: saved in `~/.hermes/data/alpaca_config.json`
- Account ID: `f6844062-c2b1-4b1a-8bc1-4faf032c8794`
- Paper URL: `https://paper-api.alpaca.markets`
- Data URL: `https://data.alpaca.markets`
- Initial balance: $100,000 (paper), Buying power: $200,000 (2x margin)

## Registration Flow
1. Create account at app.alpaca.markets (email 1351712821@qq.com)
2. Must enable 2FA using authenticator app (Google Auth/Authy)
3. Accept Customer Agreement (33-page standard US brokerage agreement)
4. Create Paper Trading account
5. Get API keys from Dashboard → API section

## Registration Pitfalls
- 2FA setup requires scanning QR code with authenticator app, NOT taking a screenshot
- "Emergency code" shown after 2FA activation is NOT the API key (it's a recovery code for lost device)
- API keys are generated from the Dashboard under "API" section, NOT from docs.alpaca.markets
- The docs.alpaca.markets pages are documentation only — no key generation there
- Paper account has different API keys from live account
- API keys from Dashboard show Key ID + Secret Key (both needed)

## SDK Setup
```bash
pip install alpaca-py
# Using tsinghua mirror for faster download:
pip install alpaca-py -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Connection Test
```python
from alpaca.trading.client import TradingClient

client = TradingClient(API_KEY, SECRET, paper=True)
account = client.get_account()
# Returns: account id, status (ACTIVE), cash ($100,000), portfolio_value, buying_power
```

## Customer Agreement Notes (Non-US User)
- Section 1(b) Non-Domestic Customer: Alpaca allows non-US customers but they must confirm they were NOT solicited by Alpaca
- Must submit Form W-8 to certify non-US tax status
- Section 4: Self-directed account — user makes all trading decisions
- Section 16: User is responsible for API key/PIN security
- SIPC insurance: up to $500,000 (including $250,000 cash)

## Current Market Prices (Sunday May 17, 2026)
- SPY (S&P 500 ETF): bid $738.48 / ask $738.62
- QQQ (Nasdaq 100 ETF): bid $707.44 / ask $707.53
