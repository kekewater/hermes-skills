---
name: tonghuashun
description: Chinese stock market data skill with multi-source fallback (iFinD HTTP API → AKShare → EastMoney). A-share/HK/US real-time quotes, K-line, fund flow, announcements, research reports, dividend yield, and watchlist management.
version: 2.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [stock, finance, chinese-stock, a-share, tonghuashun, akshare, 10jqka, ifind]
    related_skills: [stocks, financial, china-stock-data, us-stock-data]
---

# 同花顺 - 中国股市行情查询

## Related Skills

本技能已被 [**china-stock-data**](https://hermes-agent.nousresearch.com/docs) 技能扩展升级。
`china-stock-data` 新增了 **通达讯(TDX)** 实时行情+5档盘口+K线 和 **腾讯财经** PE/PB/市值/换手率 两个数据源，且实现了自动降级。

| 场景 | 推荐技能 |
|------|---------|
| A股实时行情+盘口+K线 | **`china-stock-data`**（新增通达讯+腾讯财经） |
| A股公告查询（备用源） | **`china-stock-data`**（Tushare Pro anns_d, 当前已可用） |
| 港股/美股行情 | **本技能（tonghuashun）** |
| iFinD股息率/专业公告 | **本技能（tonghuashun）** |
| 公告深度分析（减持/权益变动） | **`stock-announcement-analysis`** |
| 问财语义搜索 | **`china-stock-data`**（需SkillHub API Key） |
| 量化因子/宏观数据 | **`china-stock-data`**（JQData聚宽, 需账号） |
| 研报查询 | **`china-stock-data`**（AKShare+备选） |

## Overview

查询**A股、港股、美股**实时行情、K线数据、板块排行、资金流向、公告新闻、券商研报、股息率等金融数据。三层数据源自动降级：**iFinD HTTP API**（专业级）→ **AKShare**（新浪）→ **东方财富**（备选）。

## When to Use

- 查询某只股票的实时行情（价格、涨跌幅、成交量、PE、换手率、市值、**股息率**）
- 查询A股大盘指数（上证、深证、创业板、科创50等）
- 查询板块/行业涨跌排行
- 获取个股K线数据（日K、周K、月K）
- 查询资金流向（主力净流入/流出）
- 获取公司公告（含PDF下载链接）
- 获取券商研报（含评级、机构名）
- 按关键词搜索股票代码
- 管理自选股列表
- 查询港股/美股行情
- 分析减持/权益变动公告正文，提取股份来源等关键要素

**不要用于：**
- 下单/交易操作（本技能仅提供数据查询）

## How It Works

本技能使用 Python 脚本（`scripts/stock_api.py`）通过多层数据源获取数据。必须使用技能目录下的 venv Python 执行。

```bash
# ✅ 正确用法
~/.hermes/skills/financial/tonghuashun/.venv/bin/python3 scripts/stock_api.py quote sh600519

# ❌ 错误用法（缺少AKShare依赖）
python3 scripts/stock_api.py quote sh600519
```

### 数据源优先级

```
查询数据时，脚本按优先级自动降级：
  1️⃣ iFinD HTTP API  ── 专业级实时行情/公告/K线（含PE/换手率/市值，需token配置）
  2️⃣ AKShare(新浪)   ── 稳定可靠，全市场5514只A股
  3️⃣ 东方财富公开API  ── 备选（当前服务器IP可能被限流）
```

| 数据 | 首选来源 | 说明 |
|------|---------|------|
| **实时行情** | **通达讯(TDX)** → iFinD → AKShare(新浪) → 东方财富 | 四级降级；新增TDX(免Key)含5档盘口；腾讯财经补充PE/市值 |
| **大盘指数** | **iFinD** → AKShare(新浪) | iFinD 实时 |
| **K线数据** | **通达讯(TDX)** → iFinD → AKShare → 东方财富 | TDX K线数据（含日/周/月/分钟级） |
| **公司公告** | **iFinD** → 巨潮资讯(CNINFO) | iFinD 含PDF下载链接，支持正文阅读 |
| **公告深度分析** | **iFinD report_query** | 下载PDF正文提取股份来源/减持主体/方式/数量 |
| **股息率** | AKShare(分红明细) + 股价计算 | 使用已实施分红自动计算 |
| 资金流向(详细) | AKShare | 主力/超大单/大单/中单/小单 |
| 券商研报 | AKShare(东方财富) | 含评级/机构/PDF（EastMoney限流时可能失败） |
| 板块排行 | 同花顺页面抓取（2026年起替代EastMoney） | 行业排行TOP20 |
| 资金流向(基本) | 东方财富 | 快速 |
| 股票搜索 | 东方财富 | 模糊搜索 |
| 全市场搜索 | AKShare(新浪) | 5514只A股按名称/代码过滤 |
| 🇭🇰 港股行情 | AKShare(日K) | 日K最新行作为近似行情 |
| 🇺🇸 美股行情 | AKShare(日K) | 日K最新行作为近似行情 |

### 脚本用法

```bash
SCRIPT=~/.hermes/skills/financial/tonghuashun/scripts/stock_api.py
PY=~/.hermes/skills/financial/tonghuashun/.venv/bin/python3

# === A股行情 ===
$PY $SCRIPT quote sh600519                     # 综合查询（自动选最佳数据源）
$PY $SCRIPT index                               # 大盘指数
$PY $SCRIPT kline sh600519 daily                # K线

# === iFinD 专业数据（需配置token）===
$PY $SCRIPT ifind-quote sh600519                # iFinD实时行情（PE/换手率/市值/股息率）
$PY $SCRIPT ifind-dy sh600519                   # 只看股息率+PE+市值
$PY $SCRIPT ifind-kline sh600519 20260501 20260513 daily
$PY $SCRIPT ifind-announce sh600519 2026-01-01 2026-05-13 20  # 公告含PDF链接
$PY $SCRIPT ifind-refresh                       # 手动刷新 token（用 refresh_token 换新 access_token）
$PY $SCRIPT ifind-status                        # 连接状态（含 token 过期时间）

# === 公告和研报 ===
$PY $SCRIPT announce sh600519 2026-01-01 2026-05-13 10
$PY $SCRIPT research sh600519 5
$PY $SCRIPT news sh600519 10

# === 港股/美股 ===
$PY $SCRIPT hk-quote 00700
$PY $SCRIPT us-quote NVDA

# === 其他 ===
$PY $SCRIPT sector industry
$PY $SCRIPT search 茅台
$PY $SCRIPT moneyflow sh600519
$PY $SCRIPT akshare-flow sh600519                # AKShare详细资金流向
$PY $SCRIPT akshare-spot 茅台 10                 # 全市场搜索
$PY $SCRIPT akshare-status                       # 数据源状态
$PY $SCRIPT watchlist list
$PY $SCRIPT watchlist add sh600519
$PY $SCRIPT watchlist quote
```

### 股息率计算

由 `add_dividend_yield()` 函数自动追加到行情查询结果中：

```python
# 计算逻辑
dividend_per_share = 最新已实施分红(每10股派息) / 10
dividend_yield = dividend_per_share / 当前股价 * 100%
```

数据来源：`ak.stock_history_dividend_detail(symbol)` 返回的最近一次「实施」进度分红记录。输出字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `dividend_yield` | float | 股息率（%） |
| `dividend_per_10` | float | 最新已实施每10股派息（元） |
| `dividend_plan_per_10` | float | 预案中每10股派息（元，可能为 None） |

## Available Queries

格式：用自然语言描述需求即可，技能会自动路由到正确的数据源。

### 1. 股票实时行情（含股息率）
```
同花顺 行情 sh600519        # 自动走最佳数据源，含PE/换手率/股息率
同花顺 股息率 sh601398      # 只看股息率
```

### 2. 大盘指数
```
同花顺 大盘
```

### 3. K线数据
```
同花顺 K线 sh600519 [daily|weekly|monthly]
```

### 4. 板块排行
```
同花顺 板块 [industry|concept]
```

### 5. 搜索股票
```
同花顺 搜索 茅台
```

### 6. 资金流向
```
同花顺 资金 sh600519
```

### 7. 公告新闻/研报
```
同花顺 公告 sh600519
同花顺 研报 sh600519
同花顺 新闻 sh600519
```

### 8. 自选股管理
```
同花顺 自选股 添加 sh600519
同花顺 自选股 列表
同花顺 自选股 行情
```

### 9. 公告深度分析（减持/权益变动）
```
同花顺 分析减持公告 300393.SZ     # 分析某只股票的解禁后减持情况
同花顺 提取股份来源 300393.SZ     # 专门提取股份来源信息
```

## Setup

```bash
# 安装依赖
~/.hermes/skills/financial/tonghuashun/.venv/bin/pip install akshare requests

# 可选：配置iFinD HTTP API token（大幅提升数据质量）
# 编辑 ~/.hermes/skills/financial/tonghuashun/ifind_config.json
# 格式见 references/ifind-sdk-guide.md
```

## Reference Files

| 文件 | 内容 |
|------|------|
| `references/ifind-api-integration.md` | iFinD HTTP API 完整文档（接口/参数/错误码/认证/自动刷新/公告查询） |
| `references/ifind-sdk-guide.md` | iFinD Windows Python SDK 安装指南 |
| `references/dividend-yield-calculation.md` | 股息率计算规范（为什么用全年分红而非单次分红） |
| `references/wind-dividend-definitions.md` | Wind 四种股息率定义、交叉验证方法与常见误用 |
| `references/ifind-token-management.md` | iFinD Token 管理：生命周期、自动刷新、主动刷新 cron、双过期恢复流程 |
| `references/api-fields.md` | 东方财富 API 字段参考 |
| `references/multi-source-architecture.md` | 多层数据源架构设计 |
| `references/api-strategies.md` | AKShare API 策略备忘录（哪些接口当前可用） |
| `scripts/stock_api.py` | 主脚本，所有查询功能实现 |
| `scripts/cninfo_download.py` | 巨潮公告下载脚本 |

## Common Pitfalls

1. **必须使用 venv 的 Python** — AKShare 安装在 `.venv/` 中，用系统 python3 会报 `ModuleNotFoundError`：
   ```bash
   # ✅ 正确
   ~/.hermes/skills/financial/tonghuashun/.venv/bin/python3 scripts/stock_api.py quote sh600519
   ```

2. **tqdm 进度条干扰 JSON** — AKShare 部分函数输出进度条到 stderr。用 `2>/dev/null` 过滤得到干净 JSON。进度条不是错误，是 AKShare 的正常行为。

3. **EastMoney 被阻断的根因是代理env，不是IP封禁** — 环境中 `http_proxy` 变量(`http://127.0.0.1:8889`)才是导致EastMoney返回 `Connection aborted` 的元凶。实测 `curl --noproxy '*' 'https://push2.eastmoney.com/api/qt/clist/get?...'` 返回正常数据。
   - 影响范围：`sector industry` 板块排行、`research` 研报查询、`announce` 公告等所有EastMoney源的调用
   - 修复：调用AKShare/直连前清掉代理环境变量
     ```python
     for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY']:
         os.environ.pop(k, None)
     ```
   - 同花顺行业板块页面 `q.10jqka.com.cn/thshy/` 爬取不受影响

4. **港股/美股行情是近似值** — 来自日K数据的最近交易日记录，不是实时分笔。收盘价准确但盘中没有实时更新。

5. **股票代码格式必须正确** — 沪市 `sh600519`，深市 `sz300750`，港股 `00700`（纯数字），美股 `AAPL`（纯字母）。代码前缀错误会导致查询失败。

6. **iFinD Token 过期自动刷新** — access_token 7天有效。脚本检测到 `-1010`/`-1300`/`-1302` 错误码时自动用 refresh_token 刷新（同时保存新 refresh_token 到配置文件）。建议设置 cron 每周主动刷新避免双过期（详见 `references/ifind-token-management.md`）。

7. **iFinD ≠ iFinDPy** — 本技能使用 iFinD **HTTP API**（Linux 可用），不是 Windows 专用 Python SDK `iFinDPy`。后者不在 PyPI 上，需单独获取。

8. **iFinD 每周数据量配额（-4317错误）** — 基础数据每周配额仅 **1万条**。`report_query` 每次调用消耗大量配额。批量下载公告PDF时必须先用列表筛选出关键公告（优先下载"减持完成公告"和"简式权益变动报告书"），缓存 PDF 文本到 `/home/ubuntu/announcements_pdf/`，避免重复下载。配额超限后所有 `report_query` 返回空，需等下周一重置。

9. **股息率计算必须用全年分红，不是单次分红** — 中国很多公司（尤其银行股）一年分两次红。只取最近一次会得到 ~2.67% 的错误值，正确值应为 ~7.95%（全年合计）。Wind 有4种股息率定义，本技能计算的是 **股息率(近12个月)**，对应 `wind-dividend-definitions.md` 中的第②类。

10. **定期与 Wind 交叉验证** — 出现异常低的股息率时（银行股 < 3%），应怀疑只用了半年分红。用 Wind 对比数据验证，详见 `references/wind-dividend-definitions.md`。

12. **PDF 表格解析陷阱** — fitz 提取表格时每个单元格是独立行。搜索\u201c股份来源\u201d后需合并后续5-10行才能拼出完整内容。详见 `references/announcement-deep-reading.md` 第6b节。

13. **代理环境变量（http_proxy）破坏数据源连通性** — 环境中 `http_proxy=http://127.0.0.1:8889` 会导致AKShare的东方财富源报 `ProxyError`，EastMoney push API 也被阻断。
    - 修复：调用AKShare前清掉代理变量：
      ```python
      for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY']:
          os.environ.pop(k, None)
      ```
    - 腾讯财经 `qt.gtimg.cn` 不受代理影响

14. **iFinD Token 双过期（2026-05-17确认）** — `access_token` 已过期(-1302)，`refresh_token` 也已过期(-1301)。
    - 主动预防：设置 cron `0 10 * * 1,4` 执行 `ifind-refresh`
    - 恢复：Windows iFinD 客户端登录获取新 token（账号/密码在 `references/ifind-token-management.md`）
    - 已修复：自动刷新现在会同时保存新 refresh_token 到 ifind_config.json
    - 详见：`references/ifind-token-management.md`

15. **同花顺行业板块JSON API已404** — `https://www.10jqka.com.cn/header/industry.json.js` JSONP端点404。`fetch_sectors()`降级到EastMoney（代理阻断）返回空。
    - 替代：同花顺行业板块HTML `https://q.10jqka.com.cn/thshy/` 页面爬取（BeautifulSoup）

12. **公告分析必须同时读 减持 和 权益变动 两类公告** — 权益变动报告书（简式权益）中同样包含减持的股份来源、减持方式、减持数量等关键信息。不可只读"减持完成"类公告。优先下载：减持完成公告 > 简式权益变动报告书 > 减持触及阈值公告。

## Verification Checklist

- [x] `quote sh600519` → 返回价格/涨跌幅/PE/换手率/市值/股息率
- [x] `index` → 返回 7 个主要指数
- [x] `ifind-quote sh600519` → iFinD 专业数据含全部指标
- [x] `ifind-dy sh600519` → 股息率 1.77%
- [x] `ifind-announce sh600519` → 37条2026年公告
- [x] `hk-quote 00700` → 腾讯 457.20
- [x] `us-quote NVDA` → NVIDIA 220.78
- [ ] `search 茅台` → 应返回匹配列表
- [ ] `watchlist add/quote` → 自选股管理