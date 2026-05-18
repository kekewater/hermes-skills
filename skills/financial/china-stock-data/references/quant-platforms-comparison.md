# 中国量化平台对比 (2026-05-17)

## 三家平台一览

| 维度 | Tushare Pro 🥇 | 聚宽 JoinQuant 🥈 | Alpaca 🥉 |
|------|---------------|-------------------|-----------|
| 定位 | 金融数据API平台 | 量化策略平台+数据SDK | 美股券商API |
| 覆盖市场 | A股+期货+基金+宏观 | A股+期货+基金+宏观 | 美股+ETF+加密 |
| 数据方式 | REST API / MCP Server | Web回测 / `jqdatasdk` SDK | REST API / MCP Server |
| 回测引擎 | ❌ 无 | ✅ 网页端全功能回测 | ✅ Paper Trading |
| 风险指标 | ❌ 需自己算 | ✅ Alpha/Beta/最大回撤自动出 | ✅ 内置 |
| 本地SDK | `pip install tushare` | `pip install jqdatasdk` | `pip install alpaca-trade-api` |
| Hermes集成 | MCP Server已配 | `auth(手机号,密码)` | 有MCP Server(待配) |
| 费用 | 免费(积分制,初始100~200分) | 免费试用(前15月数据) / 正式付费 | 免佣金(API交易) |
| 美股 | ❌ | ❌ | ✅ |
| 当前状态 | ✅ Token已配,基础接口可用 | ✅ SDK已装,待开通SDK权限 | ❌ 未注册 |

## 适用场景

### Tushare Pro — 数据查询首选
```python
# 最快上手：pip install + token
import tushare as ts
ts.set_token('token')
pro = ts.pro_api()
df = pro.stock_basic(exchange='SSE', list_status='L')
```

**适合:** 轻量数据查询、A股/期货基础数据、不需要回测引擎的场景
**不适合:** 你需要自己算Alpha/Beta/最大回撤等风险指标
**MCP优势:** 在Hermes里直接当工具调用，无需写Python脚本
**MCP配置:**
```yaml
mcp_servers:
  tushare:
    url: "https://api.tushare.pro/mcp/?token=YOUR_TOKEN"
    timeout: 120
    connect_timeout: 60
```
Hermes重启后自动注册 `mcp_tushare_*` 工具。

### 聚宽 JoinQuant — 回测+数据双用
```python
# pip install jqdatasdk
from jqdatasdk import *
auth('手机号', '密码')
df = get_price('000001.XSHE', start_date='2026-01-01', end_date='2026-05-17')
```

**适合:** 写策略、跑回测、自动出风险指标、深度量化分析
**不适合:** 简单查个行情不如Tushare快
**注意:** 试用账号历史数据只覆盖前15个月~前3个月（无近3个月数据）
**Web端优势:** 浏览器写策略→一键回测→Alpha/Beta/夏普/最大回撤全自动出

**⚠️ 开通SDK权限流程:**
1. 登录 joinquant.com → 进入 JQData本地数据 页面
2. 填写试用申请表单：姓名 / 公司 / 部门 / 邮箱
3. 收邮箱验证码 → 提交 → 等待审批（通常即时通过）
4. 然后 `auth()` 才能成功，否则报"未开通权限"

**⚠️ 安装坑:**
```bash
pip install jqdatasdk
# 会自动降级 pandas 到 2.3.x，影响其他依赖库！
# 降级后必须恢复：
pip install --upgrade pandas
```

**试用申请URL:** https://www.joinquant.com/default/index/sdk#jq-sdk-apply
**试用条件:** 3个月有效期, 1M请求/天, 数据范围前15个月~前3个月

### Alpaca — 美股量化+模拟交易
```python
# pip install alpaca-trade-api
from alpaca.trading.client import TradingClient
client = TradingClient('api_key', 'secret_key', paper=True)
```

**适合:** 美股ETF/股票策略、模拟交易、实盘API交易
**不适合:** A股市场
**注意:** 需要美国券商账户(可开Paper模拟账户)
**MCP集成:** 官方MCP Server，配置后可直接在Hermes里使用

## 核心决策：回测 vs 数据源

**重要结论（2026-05-17）：对于回测风险指标（Alpha/Beta/最大回撤），应该用专业回测平台而非自己拉数据算。**

| 方式 | 优点 | 缺点 |
|------|------|------|
| 我自己拉历史数据算 | 灵活, 可定制 | 批量拉数据易触发限流/封IP, 算法不一定准确 |
| 聚宽网页端回测 | 一站式: 数据+引擎+指标自动出 | 需要注册账号, 试用数据有限 |
| Alpaca Paper回测 | 美股专用, 模拟交易 | 需要美国券商身份 |

**推荐分工:**
- 日常轻量数据查询 → 腾讯财经/TDX/Tushare
- 策略回测+风险指标 → **聚宽网页端**（A股）/ **Alpaca Paper**（美股）
- 行情监控+日报 → 现有数据源足够

## 当前Tushare Token权限状态

Token: `be048ffb8d6a29f64139a9da1f88fbd31783ccf4cc10582ce58ad5e1`
权限(2026-05-17):
- ✅ `stock_basic` — 股票列表(2313只沪股)
- ❌ `index_daily` — 指数日线(需更多积分)
- ❌ `fund_daily` — ETF日线(需更多积分)
- ❌ `trade_cal` — 交易日历(需更多积分)

Token积分可以在tushare.pro通过每日签到、推荐新用户获取更多积分。
基础接口（stock_basic）免费可用无限制。

## 当前JQData认证状态

- 手机号: 13986187760
- 密码: `Yu123(j)`（半角括号，全角括号不对）
- 认证结果: 账号密码正确，但报"未开通权限"
- 下一步: 提交试用申请表单 → 开通后 `auth()` 即可使用
- 试用期间: 3个月免费，1M请求/天
