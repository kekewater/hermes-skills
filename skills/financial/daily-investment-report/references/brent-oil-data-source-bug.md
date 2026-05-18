# 布伦特原油数据源坑（2026-05-18排查记录）

## 问题现象

投资日报图片显示 "ICE布油 91.51 USD (+0.58%)"，但真实布伦特原油5月15日是 $109.26 (+3.35%)。

## 根因

Cron agent运行 `ak.futures_global_spot_em()` 查找布伦特原油。该接口返回620行数据，涵盖所有期限合约（2026年远至2027年）。**近期合约的"最新价"字段全是 `nan`**，因为东方财富这个接口没有加载近月合约的实时价格。

Agent只能看到有数值的远期合约，误选了 Dec 2026 合约 $91.51 当作"最活跃近月合约"。

## 验证过程

### 1. 确认akshare接口不可用
```python
import akshare as ak
df = ak.futures_global_spot_em()
brent = df[df['名称'].str.contains('布伦特', na=False)]
# 所有近期合约的"最新价"都是nan
```

### 2. 确认USO ETF也不对
腾讯财经 `usUSO` 价格 $148.23 (2026-05-15收盘)。
USO是美国原油基金ETF，跟踪WTI近月期货，价格结构完全不同。

### 3. 找到真实价格
- TradingEconomics: Brent $109.26 (May 15, 2026, +3.35%)
- ICE交易所官网: May27 contract at $83.43
- countryeconomy.com: May 2026 avg $107.98

### 4. 数据源对比

| 来源 | 价格 | 类型 | 可用性 |
|------|------|------|--------|
| TradingEconomics | $109.26 | 布伦特现货参考价 | ✅ web_search直达 |
| ICE交易所 | $83.43 (May27) | 期货合约 | 🔒 需翻墙 |
| akshare futures_global_spot_em | $91.51 (Dec26) | 远期期货 | ❌ 近期合约全nan |
| USO ETF | $148.23 | WTI跟踪ETF | ❌ 非布伦特 |

## 修复措施

1. SKILL.md注明禁用akshare和USO，改用web_search
2. cron prompt中明确列出禁用数据源和正确做法
3. 每次日报运行前先web_search确认当前价

## 海量数据过滤陷阱

**教训**：当akshare返回620行数据时，不要用眼睛挑"看起来对"的那一行。如果接口的近期合约全是nan，说明这个接口对这个品种不可用——直接换数据源，而不是从非nan的行里选。

## 相关文件

- `~/scripts/monitor_usage.py` 不受影响
- `~/scripts/market_daily_report.py` 的 `get_oil()` 函数使用USO ETF，已标记禁用
- SKILL.md的数据采集流程已更新
