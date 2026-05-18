# Multi-Source Data Architecture

## Overview

The tonghuashun skill uses a **primary + fallback** multi-source architecture for each data type. This ensures reliability when one API provider is rate-limited, temporarily down, or blocking certain IPs.

## Source Priority

```
For each data type:
  1. PRIMARY SOURCE — most reliable, hit first
  2. FALLBACK SOURCE — used only if primary fails
  3. ERROR — only if both fail
```

## Source Matrix

| Data | Primary | Fallback | Why this order |
|------|---------|----------|---------------|
| Real-time quote | AKShare(Sina) `stock_zh_a_spot()` | EastMoney `push2.eastmoney.com` | Sina handles Cloudflare better; single call returns all 5500+ stocks |
| Index data | AKShare(Sina) `stock_zh_index_spot_sina()` | EastMoney per-index calls | Sina returns all indices in one call |
| K-line | AKShare `stock_zh_a_hist()` | EastMoney `push2his.eastmoney.com` | AKShare gives pre-adjusted data with proper timestamps |
| Fund flow | AKShare `stock_individual_fund_flow()` | EastMoney `fflow/daykline/get` | AKShare returns cleaner data with column names |
| Sector ranking | 同花顺 JSONP API | EastMoney `clist/get` | 同花顺 JSONP is simple and fast |
| Stock search | EastMoney `suggest/get` | — | EastMoney search is the most complete |
| News | 同花顺 `industryNewsList` | — | Only 同花顺 provides news per stock |

## Known API Blocking Patterns

### EastMoney (东方财富)
- **Symptoms**: `RemoteDisconnected: Remote end closed connection without response`, `Connection aborted`
- **Trigger**: >5 requests/second from same IP, or >~100 requests/minute
- **Cooldown**: ~30-60 seconds after rate limit triggered
- **Mitigation**: 
  - 0.3s delay between calls in the script
  - AKShare Sina fallback for real-time data
  - Some EastMoney endpoints (fund flow, K-line) are more permissive than others (sector, board)

### Sina Finance (新浪财经)
- **Symptoms**: Slow response, progress bar in AKShare output
- **Trigger**: Rarely rate-limited
- **Mitigation**: Single batch call returns all stocks; cache results for the session

### 同花顺 (10jqka)
- **Symptoms**: JSONP response fails to parse
- **Trigger**: Unusual User-Agent or missing Referer header
- **Mitigation**: Always set `Referer: https://www.10jqka.com.cn/`

## Python venv Strategy

Skills with pip dependencies should use an isolated virtual environment:

```bash
SKILL_DIR=~/.hermes/skills/<category>/<name>
python3 -m venv "$SKILL_DIR/.venv"
"$SKILL_DIR/.venv/bin/pip install akshare requests"
```

The main script should reference the venv Python in its shebang or be invoked with the venv Python explicitly. AKShare must be importable at module level (not inside a function call that happens after a fork).

## Credential Safety Rule

**Never** use user-provided financial account credentials (username/password) to log into any API or service. Instead:

1. Use only public, free API endpoints that require no authentication
2. If the user wants authenticated/professional data (e.g., iFinD), tell them it requires:
   - A different platform (Windows for iFinD)
   - A paid license
   - A manual install process outside the agent's scope
3. Document the iFinD setup guide in `references/ifind-sdk-guide.md` instead of implementing it in the script
