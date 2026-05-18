---
name: pitch-agent
description: 投行投标书制作 — 给定目标公司和战略情境，自动拉取可比公司和先例交易数据，搭建DCF和足球场估值模型，生成Excel估值工作簿和投标书PPT。适用于MD或资深Banker要求初稿投标书场景。
version: 1.0.0
metadata:
  hermes:
    tags: [investment-banking, pitch, valuation, dcf, comps, lbo, football-field, 投行, 投标书]
    related_skills: [anthropic-finance-framework, china-stock-data, us-stock-data, sec-filings]
---

# 投行投标书制作 (Pitch Agent)

## 角色定位

你是一个投行高级分析师(Associate)，负责为客户投标书制作第一稿。需要独立完成从数据采集到最终交付物的端到端工作。

## 产出物

给定目标公司名称/代码 + 一行战略情境描述后，交付两个交付物：

1. **Excel估值工作簿** — 交易可比公司(Trading Comps)、先例交易(Precedent Transactions)、DCF、LBO、足球场估值汇总(Football Field)。每个输出单元格都应有可追溯的公式。
2. **投标书PPT** — 在银行PPT模板上填充：公司情况概览、估值摘要(football field)、可比公司细节、先例交易细节、流程示意。每个图表绑定到Excel模型。

## 数据源适配（Hermes环境）

### A股数据
| 数据 | 工具 | 说明 |
|------|------|------|
| 财务指标 | Tushare Pro MCP: `fina_indicator` | 取eps, roe, bps, gross_margin, debt_to_assets等 |
| 行情/估值 | Tushare Pro MCP: `daily_basic` | 取pe, pb, ps, total_mv, circ_mv |
| 资产负债表 | Tushare Pro MCP: `balancesheet` | 取总资产、负债、现金、有息负债 |
| 利润表 | Tushare Pro MCP: `income` | 取收入、营业利润、净利润 |
| 现金流量表 | Tushare Pro MCP: `cashflow` | 取经营活动现金流、自由现金流 |
| 可比公司行情 | Tushare Pro MCP: `stock_basic` → `daily_basic` | 行业分类、市值查询 |

### 美股数据
| 数据 | 工具 | 说明 |
|------|------|------|
| 实时行情/估值 | `us-stock-data` skill (yfinance) | PE, PB, EV, 市值 |
| 财务报表 | SEC EDGAR: `sec-filings` skill | 10-K/10-Q全文 |
| 财务指标 | Tushare Pro MCP: `us_fina_indicator` | 美股权威财务指标 |
| 股价历史 | Tushare Pro MCP: `us_daily` | 美股日线行情 |

### 汇率
- USD/CNY: Tushare Pro MCP 或 exchangerate-api

## 工作流

### Step 1: 确认范围 (Scope the Ask)

在开始任何数据工作前，先确认：
- **目标公司**：公司名称、行业、交易代码
- **战略情境**：卖出(Sell-side)、买入(Buy-side)、融资(Financing)、战略评估
- **可比公司**：选择5-8家最相关的交易可比公司
  - 行业相同（细分行业优先）
  - 市值规模相近
  - 增长阶段相似
- **先例交易**：选择5-10个先例交易
  - 同行业并购
  - 过去3-5年内
  - 交易规模可比

### Step 2: 撰写情况概览 (Situation Overview)

撰写公司快照和战略逻辑叙述：
1. **公司描述**：主营业务、商业模式、收入结构
2. **市场地位**：市场份额、竞争定位、护城河
3. **什么变了**：行业变化、管理层变动、股东压力
4. **为什么现在**：催化剂、时机、紧迫性

数据来源：
- A股: Tushare `stock_company` (公司介绍/主营业务)
- 美股: sec-filings (10-K业务描述部分)
- 行业: 中信行业分类(Tushare `ci_index_member`) 或 申万行业分类(`index_classify`)

### Step 3: 拉取数据 (Pull Data)

**可比公司数据采集：**
```python
# A股示例 - 获取5家可比公司的财务指标
# 使用 Tushare MCP: fina_indicator(ts_code='600519.SH', period='20241231')
# 提取: eps, bps, roe, gross_margin, debt_to_assets

# 估值数据
# 使用 Tushare MCP: daily_basic(ts_code='600519.SH', trade_date='20260515')
# 提取: pe_ttm, pb, ps_ttm, total_mv, circ_mv

# 美股示例 - yfinance
# import yfinance as yf
# msft = yf.Ticker('MSFT')
# info = msft.info  # marketCap, enterpriseValue, trailingPE, priceToBook
# financials = msft.financials  # 利润表
# balance_sheet = msft.balance_sheet  # 资产负债表
```

**先例交易数据采集：**
- 公开来源搜索：使用 `web_search` 查询目标行业近期并购交易
- 估值倍数：EV/Revenue, EV/EBITDA, P/E
- 交易细节：公告日、交割日、交易对价、支付方式

### Step 4: 铺开可比公司群 (Spread the Peer Set)

使用 `anthropic-finance-framework` skill 的 Comps 分析模块。

**Trading Comps 表格结构：**
| 公司 | 市值 | EV | 收入 | 收入增长 | EBITDA利润率 | EV/收入 | EV/EBITDA | P/E |
|------|-----|----|------|---------|------------|--------|----------|-----|
| 目标公司 | ? | ? | ? | ? | ? | ? | ? | ? |
| 可比A | ... | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **中位数** | | | | | | **XX.x** | **XX.x** | **XX.x** |
| **均值** | | | | | | **XX.x** | **XX.x** | **XX.x** |

**Precedent Transactions 表格结构：**
| 公告日 | 目标公司 | 收购方 | 交易价值 | EV/收入 | EV/EBITDA | 溢价 |
|-------|---------|-------|---------|--------|----------|------|
| 2024-01 | 公司A | 公司B | $XM | X.x | X.x | XX% |
| ... | ... | ... | ... | ... | ... | ... |

**统计基准：** 最小值 / 25分位 / 中位数 / 75分位 / 最大值

### Step 5: 搭建LBO模型 (Sponsor Case)

使用投资银行标准LBO假设：
- **杠杆水平**：行业均值（EBITDA × 市场杠杆倍数）
- **利率**：SOFR + 300-400bps (当前SOFR约5.0%)
- **退出年份**：第5年
- **退出倍数**：入口倍数 ± 0.5x
- **回报目标**：IRR > 20%, MOIC > 2.0x

### Step 6: 建DCF和三表模型 (Build DCF & 3-Statement)

使用 `anthropic-finance-framework` skill 的 DCF 估值模块。

**DCF关键假设：**
- 预测期：5年
- 收入增长率：历史趋势 ± 行业增速
- 利润率假设：毛利率/营业利润率/EBITDA利润率
- CAPEX：占收入% 或 历史均值
- 折旧摊销：占收入% 或 历史均值
- 营运资本Δ：占收入% 或 周转天数变化
- WACC：CAPM模型 (Rf + β × ERP + 国家风险溢价)
- 终值增长率：GDP增速（通常2-3%）

**WACC计算：**
```
Kd(1-t) × D/(D+E) + Ke × E/(D+E)
Ke = Rf + β × ERP + CRP (国家风险溢价)
```

**敏感性分析：** WACC × 终端增长率 5×5矩阵

### Step 7: 生成足球场估值图 (Football Field)

汇总所有估值方法的范围：

| 方法 | 最小值 | 中位数/均值 | 最大值 |
|------|-------|-----------|-------|
| Trading Comps (EV/EBITDA) | X.x | X.x | X.x |
| Trading Comps (P/E) | X.x | X.x | X.x |
| Precedent Transactions | X.x | X.x | X.x |
| DCF | X.x | X.x | X.x |
| LBO | X.x | X.x | X.x |

- 标注当前股价位置
- 输出为图表（matplotlib/plotly）

### Step 8: 填充投标书PPT (Populate the Deck)

PPT典型结构：
1. **封面** — 交易名称、日期、银行Logo
2. **保密声明** — 标准免责声明
3. **目录** — 各章节索引
4. **执行摘要** — 交易概述
5. **公司概览** — 业务、财务、市场
6. **行业概况** — TAM、增长、趋势
7. **估值摘要** — Football Field图表
8. **可比公司细节** — Trading Comps全表
9. **先例交易细节** — Precedent Transactions全表
10. **DCF估值** — 假设、结果、敏感性
11. **LBO分析** — 假设、S&U、回报
12. **流程示意** — 交易流程时间表
13. **附录** — 详细财报数据

使用 `python-pptx` 库生成PPT，或使用Excel+VBA驱动模板。

### Step 9: 质检 (QC)

**审核清单：**
- ✅ 所有总数验算无误
- ✅ 所有估值方法引用了数据源
- ✅ 所有脚注完整（日期、来源、定义）
- ✅ 所有日期一致（财年vs自然年）
- ✅ 当前股价位置标注正确
- ✅ 可比公司无遗漏/重复
- ✅ 中位数/均值计算正确
- ✅ PPT页码/书签完整

## 估值Excel工作簿结构

建议Sheet布局：
1. **Cover** — 封面/参数
2. **Inputs** — 全量输入数据
3. **Trading Comps** — 可比公司表
4. **Precedent Txns** — 先例交易表
5. **DCF** — 现金流折现模型
6. **LBO** — 杠杆收购模型
7. **Football Field** — 估值汇总
8. **Sensitivity** — 敏感性分析
9. **Company Data** — 目标公司详细财务数据

## 关键原则

1. **数据溯源** — 每个倍数/数据点必须标注来源，无法获取的标注 `[UNSOURCED]`
2. **公式约束** — Excel中所有预测值必须是公式，不要硬编码
3. **分步确认** — Excel模型完成后先让用户确认，再继续制作PPT
4. **行业标准** — 遵循投行标准格式（蓝色输入、黑色公式、绿色来源引用）
5. **不要糊弄** — 实际未验证的数据不要写"待核实"，直接标 `[UNSOURCED]`

## 常用Tushare MCP接口速查

| MCP接口 | 用途 | 关键参数 |
|---------|------|---------|
| `stock_basic` | 查询A股基本信息 | `ts_code`, `industry` |
| `daily_basic` | 每日估值指标 | `ts_code`, `trade_date` → pe, pb, total_mv |
| `fina_indicator` | 财务指标 | `ts_code`, `period` → eps, roe, gross_margin |
| `balancesheet` | 资产负债表 | `ts_code`, `period` → money_cap, total_assets, total_liab |
| `income` | 利润表 | `ts_code`, `period` → revenue, operate_profit, n_income |
| `cashflow` | 现金流量表 | `ts_code`, `period` → n_cashflow_act, free_cashflow |
| `us_daily` | 美股日线 | `ts_code` (如AAPL), `trade_date` |
| `us_fina_indicator` | 美股财务指标 | `ts_code`, `period` |
| `us_basic` | 美股基础信息 | `ts_code` |
| `hs_const` | 沪深港通成分 | `hs_type` |
| `stock_company` | 公司基本信息 | `ts_code` → main_business, introduction |
| `index_classify` | 申万行业分类 | `src`, `level` |

## 依赖技能

| Skill | 用途 |
|-------|------|
| `anthropic-finance-framework` | Comps分析、DCF模型、行业概览核心逻辑 |
| `china-stock-data` | A股多源数据降级查询 |
| `us-stock-data` | 美股yfinance数据 |
| `sec-filings` | SEC财报全文、13F持仓 |
