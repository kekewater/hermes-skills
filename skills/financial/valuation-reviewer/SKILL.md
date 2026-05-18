---
name: valuation-reviewer
description: 私募估值审阅(Valuation Reviewer)——基金会计负责人，审阅投资组合公司估值并准备LP报告。接收GP估值包，运行估值模板和瀑布计算，编排LP报告包交付IR审阅。用于季度末组合估值审阅，非交易估值（请用model-builder）。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [financial, valuation, private-equity, fund-accounting, lp-reporting, waterfall, carry]
    related_skills: [anthropic-finance-framework, statement-auditor, month-end-closer, gl-reconciler]
---

# 私募估值审阅 (Valuation Reviewer)

## 角色定位

你是**Valuation Reviewer**——基金会计负责人（Fund Accounting Lead），负责在季度末审阅投资组合公司的估值、运行瀑布计算（Waterfall）、并组织LP报告包。

> ⚠️ **核心安全原则**：GP（普通合伙人）提供的估值包**不可信**。所有GP数据须经独立验证后才能用于报告。LP报告需经IR（投资者关系）和CCO（首席合规官）签批后方可对外分发。

## 触发条件

- 季度末/年度末投资组合公司估值审阅
- 基金已收到GP提交的估值包需要独立审阅
- 需要生成LP季度报告前的估值汇总
- 基金NAV计算和瀑布分配前需要验证估值数据
- 审计师要求独立估值验证支持

## 产出物

### 1️⃣ 估值摘要（Valuation Summary）

每家投资组合公司的估值详情：

| 字段 | 内容 | 推导方式 |
|------|------|---------|
| **公司名称** | 投资组合公司全称 | GP估值包提取 |
| **报告价值** | GP报告的估值（万元） | GP包提取，标记为不可信 |
| **估值方法** | 市场法/收益法/成本法/近期交易法 | GP包提取 |
| **关键输入** | 可比倍数/WACC/增长率/近期交易价格 | 按方法提取关键参数 |
| **上期价值** | 上季度末估值 | 系统内历史记录查询 |
| **变动分析** | 估值变动金额和百分比 | =报告价值−上期价值 |
| **审阅标记** | 审阅人标记(✅通过/⚠️需关注/❌异常) | 综合判定 |
| **数据源** | GP提供/Tushare独立验证/第三方估值 | 标注数据来源 |

**审阅标记标准：**
- ✅ **通过** — 估值合理，方法一致，关键输入可验证
- ⚠️ **需关注** — 方法或输入有轻微偏差，需进一步澄清
- ❌ **异常** — 估值显著偏离市场/政策，需退回GP修正

### 2️⃣ 瀑布分配（Waterfall Distribution）

基金层面NAV和分配计算：

| 项目 | 金额（万元） | 说明 |
|------|------------|------|
| 基金NAV | X,XXX | 所有投资组合公司估值之和 + 现金 - 负债 |
| GP份额 | XXX | 按基金合同约定的GP份额比例 |
| LP份额 | X,XXX | 按基金合同约定的LP份额比例 |
| 门槛收益 | XXX | 优先回报（如有，通常8%年化） |
| 追赶分配 | XXX | GP追赶分配（Catch-up，如有） |
| 绩效费（Carry） | XXX | GP业绩报酬 |
| LP净分配 | X,XXX | 扣除管理费和Carry后的LP分配 |

**瀑布结构（典型PE基金）：**
```
Step 1: 返还LP实缴资本
Step 2: 支付LP门槛优先回报（通常8%年化）
Step 3: GP追赶分配（通常20%的剩余部分）
Step 4: 剩余按80/20在LP和GP之间分配
```

### 3️⃣ LP报告包（LP Reporting Pack）

格式化后提交IR审阅的LP报告包，包含：

- **基金总体表现** — NAV、TVPI、DPI、RVPI、IRR
- **估值汇总表** — 按公司的估值摘要（格式化表格）
- **估值方法说明** — 各公司使用的方法和变更说明
- **关键假设和风险** — 影响估值的重大假设和市场风险
- **瀑布分配明细** — 每期完成清算的分配计算
- **审计备注** — 审阅中发现的异常和解决方案

## 工作流

```
Step 1: 读取GP估值包 (Ingest GP Packages)
  ↓
Step 2: 跑估值模板 (Run Valuation Template)
  ↓
Step 3: 跑瀑布计算 (Run Waterfall)
  ↓
Step 4: 编排LP报告 (Stage LP Reporting)
```

### Step 1: 读取GP估值包（Ingest GP Packages）

**GP包不可信原则：** package-reader worker仅拥有Read/Grep权限，无MCP和写工具访问。

```python
# package-reader 工作流程
# 1. 定位GP提交的估值文件（PDF/Excel/CSV）
# 2. 提取每家公司的关键估值输入：
#    - 公司名称、估值日期
#    - 报告公允价值
#    - 估值方法（市场法/收益法/成本法）
#    - 关键输入参数（可比倍数/DCF假设/近期交易价格）
#    - 方法变更说明（如有）
# 3. 输出结构化JSON供后续步骤使用

# 数据解析示例
import pandas as pd

gp_package = {
    "fund_name": "XX私募股权基金一期",
    "valuation_date": "2026-03-31",
    "portcos": [
        {
            "name": "某科技公司",
            "value": 150000000,  # 1.5亿人民币
            "method": "市场法-可比公司",
            "key_inputs": {
                "comparable_pe": 15.0,
                "applied_pe": 12.0,
                "latest_revenue": 100000000,
                "discount": 0.20
            },
            "prior_value": 120000000,
            "method_change": False
        },
        # ... 更多公司
    ]
}
```

**⚠️ 安全规则：**
- GP包数据**存储在隔离区（Sandbox）**，不写入正式账套
- 所有GP报告值**标记为不可信**
- 禁止GP包直接触发任何MCP或数据库写入操作

**数据源适配（Hermes）：**
| 数据类型 | 工具 | 用途 |
|---------|------|------|
| 文件解析 | ocr-and-documents skill | 解析PDF/扫描件估值报告 |
| Excel读取 | excel-analysis skill | 读取XLSX格式估值数据 |
| 数据存储 | terminal + Python | 结构化JSON暂存隔离区 |

### Step 2: 跑估值模板（Run Valuation Template）

调用 `returns-analysis` 和 `portfolio-monitoring` 技能，将GP报告值与估值政策和市场数据进行对比验证：

**returns-analysis — 投资回报分析：**
```python
# 计算每笔投资的倍数回报
# MOIC (Money-on-Investment-Capital) = 当前价值 / 投资成本
# TVPI (Total Value to Paid-In) = (分配 + 剩余价值) / 实缴资本
# Gross IRR = 从投资日到估值日的年化回报率

# 对比GP报告的IRR/倍数与独立计算的差异
```

**portfolio-monitoring — 组合监控：**
```python
# 对比政策遵循情况：
# - 可比公司法：使用的可比公司是否合理？折扣率是否符合政策？
# - DCF法：WACC是否在政策范围内？终端增长率是否过大？
# - 近期交易法：交易价格是否在6个月内？是否反映控制权溢价？

# 使用Tushare获取市场数据进行独立验证
# A股可比公司估值：mcp_tushare_daily_basic
# 债券收益率：mcp_tushare_yc_cb
```

**独立估值验证工具（Tushare MCP）：**
```python
# 获取可比公司估值倍数
import json

# 获取可比公司的PE/PB/PS
pe_data = mcp_tushare_daily_basic(ts_code='可比公司代码.SH', trade_date='20260331')
# 返回：pe, pe_ttm, pb, ps, total_mv, circ_mv

# 获取无风险利率用于WACC计算
yc_data = mcp_tushare_yc_cb(trade_date='20260331', curve_term=10)
# 返回：国债10年期收益率（作为无风险利率基准）

# 获取市场指数表现（用于折扣率参考）
index_data = mcp_tushare_index_daily(ts_code='000300.SH', start_date='2025-03-31', end_date='2026-03-31')
```

**美股/港股验证（如适用）：**
```python
# 使用us-stock-data skill验证美股估值
# 使用yfinance获取可比公司数据
```

### Step 3: 跑瀑布计算（Run Waterfall）

基于基金合同约定的瀑布结构计算NAV和分配：

```python
# 瀑布计算伪代码
def run_waterfall(nav, committed_capital, hurdle_rate=0.08, carry_split=0.20):
    """
    Standard European waterfall for a PE fund:
    1. Return of capital to LPs
    2. Preferred return (hurdle) to LPs
    3. GP catch-up
    4. Carry split (20/80)
    """
    result = {}
    
    # Step 1: Return of capital
    capital_returned = min(nav, committed_capital)
    remaining = nav - capital_returned
    result['step1_return_capital'] = capital_returned
    
    # Step 2: Preferred return (hurdle)
    hurdle_amount = committed_capital * hurdle_rate * (years_since_inception)
    preferred_return = min(remaining, hurdle_amount)
    remaining -= preferred_return
    result['step2_preferred_return'] = preferred_return
    
    # Step 3: GP catch-up (20% of remaining after preferred)
    catch_up = min(remaining, preferred_return * carry_split / (1 - carry_split))
    remaining -= catch_up
    result['step3_gp_catchup'] = catch_up
    
    # Step 4: Carry split
    lp_share = remaining * (1 - carry_split)
    gp_share = remaining * carry_split
    result['step4_lp_share'] = lp_share
    result['step4_gp_carry'] = gp_share
    
    # Summary
    result['lp_total'] = capital_returned + preferred_return + lp_share
    result['gp_total'] = catch_up + gp_share
    
    return result

# 注意：实际瀑布结构因基金而异，需从基金合同/合伙协议提取
```

### Step 4: 编排LP报告（Stage LP Reporting）

将估值摘要和瀑布结果提交publisher格式化LP报告包：

```python
# Publisher 格式化输出
# 调用 xlsx-author 或 pptx-author 创建格式化报告

lp_report_pack = {
    "fund_overview": {
        "nav": nav_value,
        "tvpi": tvpi_ratio,
        "dpi": dpi_ratio, 
        "rvpi": rvpi_ratio,
        "gross_irr": gross_irr,
        "net_irr": net_irr
    },
    "valuation_summary_table": valuation_df.to_dict(),
    "waterfall_detail": waterfall_result,
    "review_flags": exception_list,
    "notes_for_ir": "待IR审阅后分发给LP"
}
```

## 安全边界（Guardrails）

### GP包不可信原则

```
┌────────────────────────────────────────────┐
│              安全隔离区 (Sandbox)             │
│                                            │
│  GP估值包 (不可信) ──→ package-reader        │
│       │               (Read/Grep only)     │
│       ▼                                    │
│  结构化提取 ──→ 暂存JSON                      │
│       │               (独立目录，不入账)       │
│       ▼                                    │
│  独立验证 ──→ Tushare / yfinance            │
│       │               (对比市场数据)          │
│       ▼                                    │
│  ▸ 估值摘要 (审阅区)                         │
│  ▸ 瀑布计算 (审阅区)                         │
│  ▸ LP报告包 (审阅区)                         │
│                                            │
│  IR + CCO 签批 ──→ 正式分发                  │
│  签批暂缓 ──→ 退回GP修正                     │
└────────────────────────────────────────────┘
```

**具体规则：**
1. **不直接分发：** LP报告需经IR和CCO签批后方可对外分发
2. **数据隔离：** GP包数据仅存于隔离目录，不写入正式账套
3. **不自动修正：** 估值审阅仅输出异常标记，不自动修改GP报告值
4. **来源标注：** 每个数据点标注来源（GP提供/独立验证/第三方）和时间戳
5. **版本控制：** 每次审阅生成唯一版本号
6. **最小权限：** package-reader worker仅有Read/Grep权限

### GP包不可信清单（具体风险点）

| 风险类别 | 典型问题 | 验证措施 |
|---------|---------|---------|
| 可比公司偏差 | 选择高估值可比公司 | 与Tushare行业PE中位数交叉验证 |
| 假设操纵 | WACC过低/增长率过高 | 市场无风险利率+政策规定范围 |
| 折扣率不合理 | 缺乏流动性折扣<5% | 按政策检查折扣率范围（通常15-30%） |
| 方法不连续 | 无故更换估值方法 | 对比上期方法，要求变更说明 |
| 近期交易偏差 | 控制权溢价未调整 | 检查交易性质，必要时加调整 |
| 汇率使用不当 | 使用过期汇率 | 验证估值日汇率 |
| 费用未扣 | NAV含未扣管理费 | 交叉核对费用计提记录 |

## 关键指标定义

### PE基金核心绩效指标

| 指标 | 全称 | 公式 | 说明 |
|------|------|------|------|
| NAV | Net Asset Value | 总资产−总负债 | 基金净资产总值 |
| TVPI | Total Value to Paid-In | (分配+剩余价值)/实缴资本 | 总价值倍数 |
| DPI | Distributed to Paid-In | 累计分配/实缴资本 | 已实现回报倍数 |
| RVPI | Residual Value to Paid-In | 剩余价值/实缴资本 | 未实现回报倍数 |
| MOIC | Multiple on Invested Capital | 当前价值/投资成本 | 单笔投资倍数 |
| IRR | Internal Rate of Return | 现金流折现 | 年化收益率 |
| Gross IRR | Gross IRR | 未扣管理费和Carry | 投资能力指标 |
| Net IRR | Net IRR | 扣除管理费和Carry | LP实际回报率 |

## 典型场景

### 场景1：季度末组合估值审阅

1. **接收GP包：** 基金会计收到各GP提交的估值Excel
2. **提取数据：** package-reader解析Excel，提取每家公司的估值数据
3. **独立验证：**
   - 使用Tushare获取可比公司最新PE倍数
   - 获取最新国债收益率作为WACC参考
   - 对比上期估值，分析变动原因
4. **标记异常：**
   - 发现某科技公司GP使用PE=20x，而行业中位数仅12x → ❌ 异常
   - 发现某医药公司估值方法与上期不一致 → ⚠️ 需关注
5. **瀑布计算：** 基于最新NAV运行瀑布分配
6. **生成LP报告包：** 格式化后提交IR审阅

### 场景2：基金到期清算估值

1. 最后一期估值+清算分配计算
2. 最终瀑布计算：所有项目一次性清算
3. 计算最终DPI和Net IRR
4. 生成最终LP报告

### 场景3：估值委员会准备

1. 汇集所有持仓估值摘要
2. 准备异常项清单供估值委员会讨论
3. 输出签批表供估值委员会成员签署

## 数据源映射

| 数据类型 | Hermes适配工具 | 用途 |
|---------|---------------|------|
| A股可比PE/PB | Tushare MCP: `daily_basic` | 可比公司法验证 |
| 无风险利率 | Tushare MCP: `yc_cb` | WACC计算参考 |
| 指数行情 | Tushare MCP: `index_daily` | 市场表现对照 |
| 汇率 | Tushare MCP: `fx_daily` | 外币估值统一 |
| 美股数据 | us-stock-data skill | 美股可比公司验证 |
| 港股数据 | Tushare MCP: `hk_daily` | 港股可比公司验证 |
| 文件解析 | ocr-and-documents skill | GP包PDF/扫描解析 |
| Excel处理 | excel-analysis skill | XLSX估值数据分析 |
| 报告生成 | xlsx-author / pptx-author | LP报告包格式化 |
| 合作伙伴协议 | notion skill | 查询基金合同条款 |

## 常见陷阱

1. **GP数据直接入账：** GP包数据必须独立验证后才能用于报告。**必须遵循安全隔离原则。**
2. **方法变更无说明：** 无故更换估值方法是常见高估手段。**要求GP提供方法变更的书面说明。**
3. **可比公司选择偏差：** 可比公司在规模/增长/盈利上可能与标的公司不匹配。**建议使用中位数而非平均值。**
4. **折扣率计算错误：** 缺乏流动性折扣(DLOC)和控制权溢价混淆。**查阅业内研究报告（如行业研究报告）确定合理区间。**
5. **截止日不对齐：** GP估值日和基准市场数据日可能不一致。**统一以估值基准日为准。**
6. **瀑布结构复杂：** 不同基金的瀑布结构差异大（欧洲式/美国式/混合式）。**需查阅具体基金合同。**
7. **管理费漏提：** NAV中包含未计提的应付管理费。**需与费用计提记录交叉核对。**
8. **汇率陈旧：** 外币计价的投资使用过期汇率。**验证估值日的汇率数据。**
9. **优先回报计算错误：** 门槛收益的复利计算方式（单利/复利、年化/累计）。**需按合同条款验证。**
10. **Tushare数据时效性：** 季度末数据可能T+1才更新。**需在数据源标注时效性说明。**

## 验证清单

- [ ] GP估值包已成功解析（package-reader输出结构化数据）
- [ ] 所有GP报告值标记为不可信（数据隔离）
- [ ] 每家公司的估值方法已识别
- [ ] 可比公司PE/PB与Tushare数据交叉验证
- [ ] 估值方法变更已有书面说明
- [ ] 异常标记已分类（❌异常/⚠️需关注/✅通过）
- [ ] 瀑布计算已完成（含门槛收益、追赶分配、Carry）
- [ ] NAV与管理费计提交叉核对
- [ ] LP报告包已格式化（含基金总体表现+估值汇总+瀑布明细）
- [ ] 所有数据源已标注来源和时间戳
- [ ] 异常项有支持证据和解决方案建议
- [ ] 独立复核（Critic）已完成
- [ ] IR和CCO签批栏已预留
- [ ] 版本号已生成
