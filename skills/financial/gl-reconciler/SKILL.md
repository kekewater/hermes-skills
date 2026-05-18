---
name: gl-reconciler
description: 总账对账(GL Reconciler)——基金会计，负责总账与明细账对账。比对总账余额与各子账本(托管人/交易对手/资产类型)明细，识别差异、追溯根因、出具签批级异常报告。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [financial, reconciliation, fund-accounting, gl, audit]
    related_skills: [anthropic-finance-framework, sec-filings]
---

# 总账对账 (GL Reconciler)

## 概述

GL Reconciler 是基金会计的核心技能，负责**总账（General Ledger）与明细账（Sub-Ledger）** 之间的系统化对账。适用于月度/季度/年度结账周期的资产负债表科目对账、托管人报表验证、以及审计准备。

**安全隔离原则：** 托管人报表及外部数据源不可直接入账，仅作为对账参考输出报告。所有差异须经独立复核后，方可通过正式调账流程处理。

## 触发条件

- 月度/季度/年度结账前需要执行 GL 对账
- 托管人报表与内部总账余额不一致
- 审计过程中发现账务差异需要追踪根因
- 新基金成立或资产类别变更后的首次对账
- 系统迁移/升级后的平行运行对账

## 产出

### 1️⃣ 差异列表（Variance Report）

每个超阈值差异，格式：

| 字段 | 说明 |
|------|------|
| 账户编码 | GL 科目代码及名称 |
| 总账余额 | 系统总账余额（元） |
| 明细账余额 | 托管人/子账本余额（元） |
| 差异金额 | 绝对值差额 |
| 差异率 | 差异/总账余额（%） |
| 疑似原因 | 初步判断分类 |
| 阈值标记 | 是否超过预设容忍阈值 |

### 2️⃣ 根因追踪（Root Cause Trace）

每笔差异的交易级证据和分类：

- **时间差（Timing Difference）** — 交易日 vs 结算日差异，如 T+2 在途
- **系统漂移（System Drift）** — 系统间处理逻辑差异，如汇率应用规则
- **重新分类（Reclassification）** — 科目分类与实际归属不符
- **未知（Unknown）** — 无法追溯来源，需人工介入

### 3️⃣ 异常报告（Exception Report）

供财务总监/审计委员会签批，每项差异附：

- 差异概述
- 根因证据链
- 推荐解决方案
- 建议入账调整分录（Journal Entry）
- 风险等级（高/中/低）

## 工作流

### Step 1: 拉取余额（Pull Balances）

通过 MCP 接口连接以下数据源：

```
总账余额 ← 核心账务系统
明细账余额 ← 托管人报表 / 交易对手确认 / 各子账本系统
```

执行查询：
```sql
-- GL余额查询（示例）
SELECT account_code, account_name, SUM(debit - credit) AS balance
FROM gl_ledger
WHERE period = 'YYYYMM' AND account_type IN ('资产','负债')
GROUP BY account_code, account_name;
```

**调试技巧：** 如果 MCP 工具返回空结果，先检查 `trade_cal` 确认交易日历，再检查 `stk_premarket` 确认当日是否有股本/交易数据。

### Step 2: 对比并隔离差异（Compare & Isolate）

按资产类别分发 reader 并行处理：

| 资产类别 | 数据源 | 示例科目 |
|---------|--------|---------|
| 现金及货币基金 | 银行对账单 / 货币基金净值 | 银行存款、备用金 |
| 股票（A股） | 托管人持仓报表 / Tushare | 交易性金融资产 |
| 股票（港股） | 托管人持仓 / CCASS | 可供出售金融资产 |
| 债券及固收 | 中债估值 / 托管人 | 持有至到期投资 |
| 衍生品 | 交易对手确认函 | 衍生金融资产/负债 |
| 其他应收/应付 | 内部子账本 | 应收股利、应付管理费 |

**差异隔离策略：**
1. 设置阈值（如绝对值 > 1000元 或 差异率 > 0.1% 为超阈值）
2. 按账户逐一比对，只输超阈值差异
3. 对非超阈值差异做总量汇总备注

**Tushare MCP 数据获取示例：**
```
# 获取基金净值用于货币基金估值
mcp_tushare_fund_nav(ts_code='XXX.SH', start_date='...', end_date='...')

# 获取持仓股票收盘价用于市值重估
mcp_tushare_daily_basic(ts_code='XXX.SH', trade_date='YYYYMMDD')

# 获取债券估值参考
mcp_tushare_yc_cb(trade_date='YYYYMMDD', curve_term='10')
```

### Step 3: 追踪根因（Trace Root Cause）

对每笔超阈值差异，拉取底层交易并分类：

```python
# 伪代码：差异根因诊断逻辑
def classify_variance(gl_balance, sub_balance, transactions):
    # 1. 检查时间差：是否存在未结算交易
    unsettled = [tx for tx in transactions if tx.settlement_date > today]
    if abs(gl_balance - sub_balance) ≈ sum(unsettled):
        return "TimingDifference", unsettled

    # 2. 检查系统漂移：汇率/费率是否一致
    rate_diff = rate_gl - rate_sub
    if rate_diff * notional > threshold:
        return "SystemDrift", {"rate_gl": rate_gl, "rate_sub": rate_sub}

    # 3. 检查重新分类：科目映射是否正确
    misclassified = check_account_mapping(gl_balance, sub_balance)
    if misclassified:
        return "Reclassification", misclassified

    # 4. 未能匹配
    return "Unknown", None
```

**分类规则：**

| 分类 | 判断依据 | 证明材料 |
|------|---------|---------|
| 时间差 | 差异金额 ≈ 在途交易总额 | 交易流水 + 结算日期 |
| 系统漂移 | 计算逻辑差异可量化 | 系统参数截图 + 规则说明 |
| 重新分类 | 科目映射表存在偏差 | 科目对照表 + 入账凭证 |
| 未知 | 以上均不满足 | 全部交易流水 |

### Step 4: 独立复核（Critic Review）

启用 Critic 角色重新核实每条差异：

1. 核实总账余额查询是否正确（SQL 逻辑复核）
2. 核对明细账余额来源是否可信
3. 检查分类逻辑是否合理
4. 确认差异金额计算无误
5. 补充可能遗漏的根因或关联差异

**复核清单：** 每条差异必须经过至少 2 个数据源的交叉验证方可出具报告。

### Step 5: 草拟异常报告（Draft Exception Report）

格式化供财务总监签批：

```markdown
# 总账对账异常报告
## 对账期间：202X年M月
## 报告日期：YYYY-MM-DD

### 汇总统计
- 总科目数：50
- 差异科目数：N（超阈值：M）
- 差异总金额：¥XXX
- 差异率: X.XX%

### 差异明细

| # | 账户 | 总账 | 明细账 | 差额 | 根因分类 | 风险等级 |
|---|------|------|--------|------|---------|---------|
| 1 | 1101-银行存款 | 1,000,000 | 999,500 | 500 | 时间差 | 低 |
| 2 | 1501-股票投资 | 5,200,000 | 5,180,000 | 20,000 | 系统漂移 | 中 |

### 推荐调账分录

**分录 #1 — 银行存款时间差调整**
借：在途资金   500
贷：银行存款   500

**分录 #2 — 股票估值调整**
借：公允价值变动损益  20,000
贷：交易性金融资产    20,000

### 签批栏
- [ ] 财务总监确认
- [ ] 投资总监审阅
- [ ] 审计委员会备案
```

## 数据源映射

| 数据类型 | Hermes 适配工具 | 备注 |
|---------|---------------|------|
| A 股行情/估值 | Tushare Pro MCP (daily, daily_basic) | 需要 2000+ 积分 |
| 基金净值 | Tushare Pro MCP (fund_nav) | 场内场外均覆盖 |
| 债券收益率 | Tushare Pro MCP (yc_cb) | 中债国债收益率曲线 |
| 港股持仓 | Tushare Pro MCP (ccass_hold) | 中央结算系统 |
| 汇率 | Tushare Pro MCP (fx_daily) / exchange rate API | 实时 USD/CNY |
| SEC 持仓 | SEC EDGAR (sec-filings skill) | 美股基金 |
| 财务报表 | Tushare Pro MCP (fina_indicator, balancesheet) | 基本面参考 |

## 典型场景示例

### 场景 1：基金月结对账

1. 通过 `mcp_tushare_fund_nav` 获取所有持仓基金月末净值
2. 对比基金会计系统的估值数据
3. 输出差异列表，分类为时间差（T+2 估值 vs T+1）和系统漂移（不同估值源）
4. Critic 复核后出具月结报告

### 场景 2：托管人对账

1. 拉取托管人发送的持仓报表（CSV/PDF）
2. 提取 `ocr-and-documents` 技能解析 PDF 报表中的持仓数据
3. 与内部 GL 余额逐条比对
4. 对无法匹配的差异输出异常报告
5. 隔离托管人数据——仅出报告，不直接入账

## 常见陷阱

1. **交易日 vs 结算日混淆：** A股 T+1 结算、债券 T+0/T+1、衍生品 T+2。必须在对比前统一按结算日对齐。
2. **汇率口径不一致：** 中间价 vs 买入价 vs 卖出价，不同系统可能使用不同汇率。应在 GL 标准汇率表上统一。
3. **托管人数据不可直接入账：** 托管人报表和交易对手确认函仅作为核对参考。差异调整必须走正式调账审批流程。
4. **分红/拆股未复权：** 持仓比较时注意是否使用复权价格。建议使用 `adj_factor`（Tushare）或复权因子进行统一。
5. **忽略零余额科目：** 零余额科目也可能隐藏双向抵消后的差额。建议对零余额但历史有交易记录科目做抽样比对。
6. **阈值设置不合理：** 过紧产生过多差异，过松遗漏重大风险。建议按资产类别设定动态阈值（如权益类 0.5%，固收类 0.1%，现金类 0.01%）。
7. **MCP 工具返回数据延迟：** 基金净值、港股数据等可能 T+1 才更新。对账时需注意数据时效性说明。

## 验证清单

- [ ] 总账余额查询 SQL 逻辑复核通过
- [ ] 明细账数据来源可信（标注来源和时间戳）
- [ ] 所有超阈值差异已识别并分类
- [ ] 每笔差异的根因分类有交易级证据支持
- [ ] 独立复核（Critic）已完成
- [ ] 异常报告已格式化，含签批栏
- [ ] 托管人数据隔离原则已遵守（未直接入账）
- [ ] 差异金额计算经过交叉验证（2源核对）
