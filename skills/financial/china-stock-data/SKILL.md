---
name: china-stock-data
description: 中国A股综合数据源技能。集成通达信(TDX)实时行情+5档盘口+K线、腾讯财经PE/PB/市值/换手率、同花顺iFinD/热点、AKShare研报/公告、iWencai问财搜索、JQData聚宽量化、Tushare Pro公告、RiceQuant米筐。8大来源自动降级。JQData聚宽试用账号已验证auth通过但⚠️历史数据只到3个月前(2026-02-13)，不可查当日实时行情。账号13986187760试用至2026-08-18，100万条/天。
version: 2.0.1
metadata:
  hermes:
    tags: [stock, finance, a-share, china-stock, tdx, tencent, tonghuashun, akshare, wencai, monitor, news, cron]
    related_skills: [tonghuashun, stock-announcement-analysis, us-stock-data]
---

# China Stock Data - 中国A股综合数据源

## Overview

本技能集成 **8大数据源 + 3大工具**，覆盖 A 股行情、K线、研报、公告、资金流向、板块排行、热点题材、语义搜索、量化指标、价格预警、每日简报等全场景。数据源自动降级，无需担心单点故障。

| # | 数据源/工具 | 能力 | 状态 |
|---|------------|------|------|
| 1 | **通达信(TDX)** | 实时行情、5档盘口、K线(日/周/月/分钟)、逐笔成交 | ✅ 无需Key |
| 2 | **腾讯财经** | PE、PB、市值、换手率、财务估值数据 | ✅ 公开API |
| 3 | **同花顺(iFinD)** | 专业行情、股息率、热点题材、强势股归因 | ✅ 需配置token |
| 4 | **AKShare** | 券商研报、公司公告、资金流向、补充数据 | ✅ 部分受限 |
| 5 | **iWencai(问财)** | 自然语言选股、跨主题语义搜索 | ⚠️需API Key |
| 6 | **JQData(聚宽)** | 行情/ETF/指数/财报/因子/宏观数据 — HTTP MCP模式 | ✅ 已开通(2026-05-17, 试用至8月18日) |
| 7 | **Tushare Pro** | 公告、日线、北向、两融、财报 | ✅ 需token |
| 8 | **RiceQuant(米筐)** | 量化回测数据 | ✅ 需账号 |
| 9 | **巨潮资讯网(CNINFO)** 🆕 | 公告全文搜索，覆盖深沪两市全部A股 | ✅ 公开API，无需Key |
| 🔔 | **Stock Monitor** | 价格预警、自选异动检查、自动盯盘 | ✅ 内置 |
| 📰 | **News Aggregator** | 每日金融简报、指数行情、头条汇总 | ✅ 内置 |

**本文就是根据这些微信公众号文章搭建的：**
- [用 Claude Code 搭建大A稳定数据源](https://mp.weixin.qq.com/s/wWIJOYwfmzQ5EEIZQbby0Q)
- [A股数据平台及工具大全](https://mp.weixin.qq.com/s/SV2TGAppLlmhvQQYLWDRIw)
- [金融AI工具10选](https://mp.weixin.qq.com/s/M5wRDr1sIoYXRzBDIl6sWA)
选型逻辑：通达信+腾讯财经（行情）→ 东财+AKShare（研报）→ 同花顺（热点）→ iWencai（搜索）→ 聚宽/米筐（量化）→ Monitor+News（监控+简报）

## When to Use

自然语言输入即可查询：

```
# 实时行情（自动选择最佳数据源）
查一下 600519 的行情
贵州茅台现在多少钱
批量看 600519,300750,000001

# K线数据
看下 300750 最近30天K线
宁德时代周K线

# 研报与公告
贵州茅台最近研报
300750 最新公告

# 资金流向
茅台资金流向

# 板块排行
今天什么板块涨得好
行业板块排行

# 热点题材
今天热点题材
同花顺热点

# 问财搜索（需配置Token）
搜索：人形机器人 丝杠
问财：华为概念 业绩预增
```

**不要用于：**
- 下单/交易操作（本技能仅提供数据查询）

## How It Works

所有查询通过 `scripts/china_stock.py` 统一执行。

```bash
SCRIPT=scripts/china_stock.py
PY=python3
```

### 命令速查

```bash
# === 智能行情（自动降级）===
$PY $SCRIPT quote 600519            # TDX → 腾讯 → iFinD自动降级（含PE/市值/换手率）
$PY $SCRIPT tencent-quote 000001    # 腾讯财经行情（平安银行）

# === 通达信（实时+盘口）===
$PY $SCRIPT tdx-quote 600519        # 实时行情+5档买卖盘口
$PY $SCRIPT tdx-kline 600519 daily  # K线 (daily/weekly/monthly/60min/30min/15min/5min)
$PY $SCRIPT tdx-kline 300750 weekly # 周K
$PY $SCRIPT tdx-kline 600519 60min  # 60分钟K线

# === 腾讯财经（财务指标）===
$PY $SCRIPT tencent-quote 000001    # PE/PB/市值/换手率
$PY $SCRIPT tencent-batch 600519,300750,000001  # 批量查询

# === 同花顺iFinD（需token）===
$PY $SCRIPT ifind-quote 600519      # 专业行情（含PE/换手率/股息率/振幅）

# === AKShare（研报/资金）===
$PY $SCRIPT report 600519 10        # 最近10份研报
$PY $SCRIPT moneyflow 600519 5      # 最近5天资金流向

# === 公告查询（三级降级：巨潮CNINFO → Tushare Pro → AKShare）===
$PY $SCRIPT announce 600519 20      # 最近20条公告（自动选最佳源）
$PY $SCRIPT moneyflow 600519 5      # 最近5天资金流向

# === 巨潮资讯网(CNINFO) 公告搜索 — 2026年新增首选公告源 ===
$PY $SCRIPT announce 600519           # 自动降级: CNINFO → Tushare → AKShare
$PY $SCRIPT tushare-ann 600519        # Tushare Pro公告（tushare.xyz自定义地址）

# === 板块排行 & 热点 ===
$PY $SCRIPT sector                  # 行业板块排行  TOP20
$PY $SCRIPT themes                  # 热点题材（行业+概念）

# === 问财语义搜索（需配置 WENCAI_TOKEN）===
$PY $SCRIPT search 人形机器人 丝杠   # 自然语言选股

# === Tushare Pro（公告数据当前可用）===
$PY $SCRIPT tushare-ann 600519 20  # 最新20条公告

# === JQData聚宽（需 export JQ_USER/JQ_PASS）===
$PY $SCRIPT jq-financial 600519    # 财报指标数据
$PY $SCRIPT jq-macro               # 宏观数据（GDP/CPI）

# === Stock Monitor 股票监控 ===
MON=~/.hermes/skills/financial/china-stock-data/scripts/stock_monitor.py
$PY $MON check 600519              # 检查贵州茅台当前价格
$PY $MON check 600519 1300 below   # 检查是否跌破1300
$PY $MON watchlist                 # 自选股异动扫描
$PY $MON watchlist 600519,300750,000001  # 指定列表异动

# === News Aggregator 新闻简报 ===
NEWS=~/.hermes/skills/financial/china-stock-data/scripts/news_aggregator.py
$PY $NEWS daily                    # 当日金融简报（指数+头条）
$PY $NEWS indices                  # 主要指数行情
$PY $NEWS headlines                # 同花顺快讯

# === 系统状态 ===
$PY $SCRIPT status                  # 全部数据源状态
```

### 数据源降级策略

```
行情查询自动按顺序降级：
  [1] 通达信(TDX) ── 5档盘口 + 实时行情
  [2] 腾讯财经    ── 补充PE/市值/换手率（与TDX并行）
  [3] 同花顺iFinD ── 专业级行情（需配置token）

板块排行/热点：
  [1] 同花顺官网  ── 实时行业/概念涨幅排行
  [2] EastMoney   ── 被限流时自动切换同花顺
```

### 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 上海A股 | 6xxxxx | 600519 |
| 深圳主板 | 00xxxx | 000001 |
| 深圳创业板 | 30xxxx | 300750 |
| 科创板 | 688xxx | 688xxx |

脚本自动识别代码前缀（6→沪，0/3→深），无需加 sh/sz 前缀。

## Setup

⚠️ **首次使用必须创建 virtualenv + 安装依赖！**.venv 不会预先存在。**

```bash
# 0. 定位到技能目录
cd ~/.hermes/skills/financial/china-stock-data

# 1. 创建 virtualenv（需指定系统 Python3，不要遗漏）
/usr/bin/python3 -m venv .venv   # 或 which python3

# 2. ⚠️ requirements.txt 中 pytdx>=1.74 不存在（最新版为 1.72），
#    直接 pip install -r 会报错。改用无版本限制手动安装：
.venv/bin/pip install pytdx akshare beautifulsoup4 requests lxml pandas openpyxl

# 3. 至此脚本可用
# 快捷路径变量
export PY=~/.hermes/skills/financial/china-stock-data/.venv/bin/python3
export SCRIPT_DIR=~/.hermes/skills/financial/china-stock-data/scripts

# 验证
$PY $SCRIPT_DIR/china_stock.py quote 600519

# 可选：数据源增强（按需安装）
.venv/bin/pip install jqdatasdk    # JQData聚宽量化数据（需账号）
.venv/bin/pip install rqdatac      # RiceQuant米筐量化数据（需账号）
.venv/bin/pip install tushare      # Tushare Pro综合数据（需token）
.venv/bin/pip install wencai       # 同花顺问财语义搜索（需API Key）

# 配置同花顺iFinD token（提升专业行情质量）
# 编辑 ifind_config.json 并放在脚本同目录：
# {"access_token": "your_token", "refresh_token": "your_token"}

# 可选环境变量
export WENCAI_TOKEN=your_token   # 问财搜索
export JQ_USER=your_phone       # JQData账号
export JQ_PASS=your_password    # JQData密码
export RQ_USER=your_username    # RiceQuant账号
export RQ_PASS=your_password    # RiceQuant密码
```

## Data Source Details

### 1️⃣ 通达信(TDX) — 实时交易数据之王
- **协议**: pytdx (开源TCP协议实现)
- **特点**: 无需API Key，直连通达信行情服务器
- **数据**: 实时价格、5档买卖盘口、K线(日/周/月/分钟)、逐笔成交
- **延迟**: 约3-5秒（与通达信客户端同步）
- **限速保护**:
  - 🛡️ 每次TDX调用间隔 ≥0.5秒（随机加0-0.2秒jitter）
  - 🔄 4台服务器轮询（成都电信、北京联通、上海电信、杭州电信）
  - 📦 批量查询优化：指数日报用1次连接查6个指数，而非6次独立连接
- **状态**: ✅ 可用

### 2️⃣ 腾讯财经 — 财务指标补充
- **接口**: `https://qt.gtimg.cn/q={code}`
- **特点**: 公开HTTP API，调用简单
- **数据**: PE(市盈率)、PB(市净率)、市值(总/流通)、换手率
- **状态**: ✅ 可用

### 3️⃣ 同花顺(iFinD) — 专业行情
- **接口**: `https://quantapi.51ifind.com/api/v1/`
- **特点**: 专业级金融数据，含股息率、振幅、PE_TTM
- **数据**: 实时行情、K线、公告(含PDF)、板块排行、热点题材
- **配置**: 需 `ifind_config.json`（access_token + refresh_token）
- **状态**: ✅ 需配置token

### 4️⃣ AKShare — 研报/公告
- **接口**: 开源Python库
- **特点**: 多源聚合（东方财富/新浪等），免费
- **数据**: 券商研报、公司公告、资金流向、补充财务数据
- **注意**: EastMoney接口可能被限流，建议降频调用
- **状态**: ✅ 可用（部分源可能限流）

### 5️⃣ iWencai(问财) — 语义搜索
- **接口**: 同花顺问财API（需SkillHub API Key）
- **特点**: 自然语言选股，独一档的语义搜索能力
- **数据**: 跨主题筛选、复杂选股条件
- **配置**: 设置环境变量 `WENCAI_TOKEN`
- **获取Key**: 访问 [SkillHub](https://skillhub.com) 或联系文章作者
- **状态**: ⚠️ 待配置（已实现接口封装）

### 6️⃣ JQData(聚宽) — 量化因子与宏观数据

- **接口**: `jqdatasdk` (Python SDK, `pip install jqdatasdk`)
- **特点**: 免费注册可用，提供量化指标、财报因子、宏观数据
- **数据**: 基本面指标、日/分钟行情(`get_price`/`get_bars`)、财务单季度(`get_history_fundamentals`)、GDP/CPI等宏观、因子数据、场内基金/ETF行情
- **⚠️ 核心限制 — 试用版有3个月数据滞后，不能查当日实时行情**：
  试用账号的数据范围是 `2025-02-06 ~ 2026-02-13`（约前15个月~前3个月）。
  `get_price(code, end_date=today)` 会报错 `"您的账号权限仅能获取2025-02-06至2026-02-13的数据"`。
  **不能用于**：查当日实时价格、建仓价、当日涨跌幅。
  **只能用于**：历史回测、因子分析、过去15个月的财报/行情数据。
  当日实时行情 → 改用**腾讯财经** `qt.gtimg.cn`（国内直连）或**通达信TDX**。
- **配置**: 
  ```python
  from jqdatasdk import *
  auth('13986187760', 'Yu123(j)')  # 用半角括号(j)，全角（j）会报"用户不存在"
  
  # ✅ 正确用法：end_date必须在范围内
  df = get_price('510300.XSHG', end_date='2026-02-13', count=30, frequency='daily')
  
  # ❌ 错误：end_date='2026-05-18' → 报错超出范围
  ```
- **⚠️ SDK权限开通流程**: 仅是手机上注册了聚宽账号不够。auth()会报"未开通权限"。必须：
  1. 登录网页 https://www.joinquant.com/default/index/sdk#jq-sdk-apply
  2. 填写试用申请表单：姓名(江玉婷)、公司(华泰证券股份有限公司)、部门(湖北分公司)、邮箱(1351712821@qq.com)
  3. 点击"获取邮箱验证码"，查收邮件填入验证码
  4. 勾选"同意用户协议"，提交
  5. 审批通过后(通常即时)auth()即可成功
- **✅ 当前状态**: 已开通(2026-05-17) → auth认证通过，试用期至2026-08-18
  ```python
  auth('13986187760', 'Yu123(j)')
  # 认证成功后 get_account_info() 返回:
  # {'mob': '13986187760', 'query_count_limit': 1000000, 'license': 1,
  #  'expire_time': '2026-08-18 00:00:00',
  #  'date_range_start': '2025-02-06', 'date_range_end': '2026-02-13'}
  ```
- **安装**: `pip install jqdatasdk`（会降级pandas到2.3.x，安装后需 `pip install --upgrade pandas` 恢复）

### 7️⃣ Tushare Pro — 综合数据平台
- **接口**: `tushare` Python SDK + **MCP Server** (`https://api.tushare.pro/mcp/?token=TOKEN`)
- **特点**: 免费注册得基础积分(100~200)，签到/分享可获取更多积分解锁高级接口
- **数据**: stock_basic(股票列表)、index_daily(指数日线)、fund_daily(ETF日线)、公告、北向、两融、财报等
- **⚠️ 积分限制**: 新注册token仅有基础权限(stock_basic等)，index_daily/fund_daily等需更多积分。积分越多接口越多。Tushare Pro主要做数据（不提供回测引擎）
- **MCP配置** (Hermes Agent, **已验证**):
  ```yaml
  mcp_servers:
    tushare:
      url: "https://api.tushare.pro/mcp/?token=YOUR_TOKEN"
      timeout: 120
      connect_timeout: 60
  ```
  MCP接口可通过 `curl` 验证（需 `Accept: application/json, text/event-stream` 头，缺一不可）：
  ```bash
  curl -s -X POST "https://api.tushare.pro/mcp/?token=YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
  ```
  Hermes重启后自动注册 `mcp_tushare_*` 工具集。
- **Python SDK配置**:
  ```python
  import tushare as ts
  ts.set_token('YOUR_TOKEN')
  pro = ts.pro_api()
  df = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name')
  ```
- **注册**: [Tushare Pro官网](https://tushare.pro/) 注册获取token
- **状态**: ✅ Token已配置(2026-05-17)，基础接口可用

### 8️⃣ RiceQuant(米筐) — 量化回测数据
- **接口**: `rqdatac` (Python SDK)
- **特点**: 免费注册可用，提供回测数据和研究环境
- **配置**: `export RQ_USER=用户名 RQ_PASS=密码`
- **状态**: ✅ 已安装，需认证

## References

| 文件 | 内容 |
|------|------|
| `scripts/china_stock.py` | 主脚本，8大数据源集成（行情/K线/研报/公告/资金/板块/搜索/量化） |
| `scripts/stock_monitor.py` | 股票监控/预警（价格检查、自选异动、可配cronjob定时盯盘） |
| `scripts/news_aggregator.py` | 金融新闻聚合（每日简报、指数行情、头条快讯） |
| `requirements.txt` | Python依赖列表 |
| `references/tdx-protocol-notes.md` | TDX通达信协议细节 + 限速策略 |
| `references/eastmoney-limitations.md` | EastMoney限流备忘 / 替代方案 |
| `references/tdx-rate-limiting.md` | TDX限速策略文档（全局间隔/服务器轮询/批量查询） |
| `references/tonghuashun-headlines-api.md` | 同花顺快讯API响应结构说明 |
| `references/cninfo-api.md` | 巨潮CNINFO公告API接口文档 |
| `references/cninfo-pdf-extraction.md` | CNINFO PDF下载方法（浏览器工具） |
| `references/daily-report-workflow.md` | 每日投资晨报工作流（数据源/输出格式/调度） |
| `references/ifind-token-refresh.md` | iFinD双Token刷新工作流（7天/44天过期，脚本+cron，关键陷阱） |
| `references/domestic-sources.md` 🆕 | 国内直连数据源：汇率(currency_boc_safe)、白银(spot_silver_benchmark_sge)等免代理AKShare接口 |
| `references/quant-platforms-comparison.md` 🆕 | 量化平台对比：Tushare Pro vs 聚宽 vs Alpaca，适用场景+权限状态 |\n| `references/jqdata-trial-session.md` 🆕 | JQData聚宽试用接入记录：账号信息、认证代码、可用接口、已知问题 |

## Common Pitfalls

1. **⚠️ .venv 不存在 + requirements.txt 版本错误 — 首次运行必踩的坑**
   - 技能目录下 `.venv/` 不会预先存在，首次使用必须先 `python3 -m venv .venv`
   - `requirements.txt` 中 `pytdx>=1.74` 不存在（pytdx 最新版为 1.72），直接 `pip install -r requirements.txt` 会报错 `No matching distribution found`
   - **正确的首次安装命令**: `.venv/bin/pip install pytdx akshare beautifulsoup4 requests lxml pandas openpyxl`
2. **TDX服务器可能变化** — 脚本内置了4台服务器（成都、北京、上海、杭州），自动轮询+最多尝试4次。每次调用间隔≥0.5秒，防被封IP
2. **腾讯财经字段索引 + GBK编码坑** — 返回的 `~` 分隔字符串，按固定顺序解析（0:市场 1:名称 2:代码 3:现价 4:昨收 ...）。**编码陷阱**：Python的`urllib.request`获取数据会因默认UTF-8解码报错`UnicodeDecodeError`（数据是GBK编码）。修复方法：
   - ❌ `response.read().decode('utf-8')` — 报错
   - ✅ `response.read().decode('gbk')` — 正确
   - ✅ 用`subprocess.run(['curl', '-s', url], capture_output=True)` → `r.stdout.decode('gbk')` 也行
   - ❌ 管道 `curl ... | python3 -c "..."` — stdin遇到GBK字节也会报解码错
   最佳实践：先`curl`输出到临时文件，Python用`codecs.open(path, 'r', 'gbk')`读取。
3. **EastMoney接口不通 → 先检查代理env** — 以前误以为服务器IP被 EastMoney 永久封禁，实测根因是 `http_proxy`/`https_proxy` 环境变量阻塞。修复：调用前清env (`os.environ.pop('HTTP_PROXY', None)`)。详见 Pitfall #17 和 references/domestic-sources.md。个股行情建议直接走通达信/腾讯，更快更稳。
4. **iFinD Token过期** — iFinD access_token 7天有效，script自动用 refresh_token 刷新。**关键**：刷新时必须同时保存新 refresh_token（不是只能存access_token）。详见 `references/ifind-token-refresh.md`。
5. **iWencai需API Key** — 问财搜索目前被IP级别封禁（403），需通过 SkillHub 获取 API Key 配置后使用
6. **行业板块 vs 概念板块** — 同花顺行业板块(thshy)可直接抓取HTML表格数据；概念板块(gn)为历史事件列表，不是当前涨幅排行
7. **港股/美股支持** — 当前脚本主要面向A股，港股/美股需通过其他工具查询
8. **pandas降级风险** — 安装 jqdatasdk 或 rqdatac 时会自动降级 pandas 至 2.3.x，可能影响 akShare 等依赖新版 pandas 的库。降级后需执行 `pip install --upgrade pandas` 恢复
9. **同花顺快讯 API 响应结构变化 (2026-05)** — `data` 现在是对象 `{"list":[...], "filter":..., "total": N}` 而非数组。字段 `share_url` → `shareUrl`
10. **公告查询优先走巨潮 CNINFO** — 三级降级：CNINFO(全文搜索) → Tushare Pro → AKShare。CNINFO 不需要 Key/Token
11. **JQData需网页端开通SDK权限，不光注册账号** — 仅是在joinquant.com注册了账号还不够。auth()会报"未开通权限"。必须登录网页 https://www.joinquant.com/default/index/sdk#jq-sdk-apply 填写试用申请表单（姓名/公司/部门/邮箱+邮箱验证码），审批通过后才能用SDK。试用3个月免费。
12. **`sector` 板块涨跌幅可能不是单日数据** — 同花顺行业板块行情中的涨跌幅(%)字段可能反映的是区间累计涨跌幅（自某个基日算起），而非单纯当日涨跌。实测中出现建筑材料+29.95%、半导体+20.00%等远超A股单日涨跌幅限制的值。使用前需确认数据的统计区间，不要直接当作日涨幅使用。
13. **`tencent-batch` 适合快速批量查估值** — 可一次查询多只股票的代码、名称、现价、涨跌幅、PE，但不含开盘/最高/最低价等日内细节。需要完整日内行情时用 `quote` 逐一查询。
14. **黄金数据：用 SGE/XAU，不用黄金ETF** — 日报需要黄金价格时，优先用 `ak.spot_quotations_sge()` 取 Au99.99（上海黄金交易所现货，元/克），或 `ak.futures_foreign_hist(symbol='XAU')` 取伦敦金（USD/盎司）。腾讯财经 sz159934 是黄金ETF，价格含折溢价不直接等同金价，Keke要求用伦敦金人民币/克。
15. **个股涨幅榜必须先排除新股** — `ak.stock_zh_a_spot()` 返回全市场5516只A股，N开头的新股（如N锐翔+490%）会霸占涨幅榜。必须 `df[~df['名称'].str.startswith('N')]` 过滤，取正常交易的前5。
16. **GPT-Image-2 JSON须用Python构建** — 含emoji/中文的prompt在shell中echo/cat构建JSON会因编码转义导致400 invalid_json。正确做法：Python dict → json.dump(ensure_ascii=False) → 写入文件 → scp到VPS。
17. **EastMoney被"封"的根因是代理env，不是IP封禁** — 实测 `curl --noproxy '*' 'https://push2.eastmoney.com/api/qt/ulist.np/get?...'` 返回正常数据。环境变量 `http_proxy=http://127.0.0.1:8889` 才是元凶。修复：调用AKShare/直连前清掉代理env。
18. **代理env影响数据采集** — `http_proxy`/`https_proxy` 设为本地代理(8889端口)会导致AKShare的EastMoney源和部分新浪源超时/报错。`china-stock-data` 脚本若通过agent调度，需在入口处清env或使用 `--noproxy '*'`。

21. **同花顺行业板块JSON API已失效** — `https://www.10jqka.com.cn/header/industry.json.js` 返回404。改用HTML爬虫 `https://q.10jqka.com.cn/thshy/` (BS4解析table)。偶尔被反爬(57bytes)，稍等重试即恢复。

22. **组合/持仓报告必须显示买入价** — Keke明确要求：展示模拟组合或持仓时，每只标的必须列出**买入价**(买入成本价)列，不能只显示"股数×现价"。格式示例：`买入价 4.878 | 现价 4.880 | 股数 5100 | 成本 24,877.80 | 市值 24,888.00 | 盈亏+10.20`。净值初始为1（未开盘不报涨跌）。

21. **JQData试用版数据范围只有2025-02~2026-02** — 3个月滞后，不能查当日实时行情。当日价格改用腾讯财经 `qt.gtimg.cn` 或通达信TDX。

20. **iFinD API tokens过期处理** — access_token 7天有效，refresh_token 长期有效。当 `-1301` 错误码出现时refresh_token也过期了，需从Windows iFinD客户端重新获取。Linux上无法自助续期。

21. **东方财富push API直连可通** — `curl --noproxy '*' 'https://push2.eastmoney.com/api/qt/ulist.np/get?secids=1.000001&fields=f2,f3,f4'` 返回正常数据。不通的原因是代理环境变量导致连接被断开，不是IP被封。

## Verification Checklist

- [x] `quote 600519` — TDX行情含PE/市值/换手率
- [x] `tdx-quote 600519` — 实时价格+5档盘口
- [x] `tdx-kline 300750 daily` — 30条日K线
- [x] `tencent-quote 000001` — 平安银行PE/市值
- [x] `sector` — 行业板块排行TOP20
- [x] `themes` — 行业+概念热点
- [x] `status` — 全部数据源状态
- [ ] `search 人形机器人 丝杠` — 需配置WENCAI_TOKEN
- [ ] `report 600519` — AKShare研报（可能限流）
- [ ] `jq-financial 600519` — 需开通JQData SDK权限（聚宽网页提交试用申请）
- [ ] `tushare` MCP tools — 需重启Hermes后自动注册
