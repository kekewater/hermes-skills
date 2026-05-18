---
name: anthropic-finance-framework
description: Anthropic开源的金融分析框架，适配Hermes环境。覆盖10个金融Agent模板，涵盖投行/股权研究/财富管理/金融分析/私募五大领域。本地部署于~/financial-services/。
version: 1.1.0
related_skills: [pitch-agent, market-researcher, earnings-reviewer, meeting-prep-agent, model-builder, gl-reconciler, kyc-screener, valuation-reviewer, month-end-closer, statement-auditor]
---

# Anthropic 金融分析框架 ⚡

## 来源
Anthropic开源仓库 `financial-services`（⭐19k+），本地部署在 `~/financial-services/`
- 10个预置金融Agent模板（已全部适配为Hermes Skill）
- 50+个专业SKILL.md技能
- 7个垂直领域插件

## 10个Agent模板总览

| # | 技能名称 | 领域 | 一句话描述 | 安装状态 |
|---|---------|------|-----------|---------|
| 1 | `pitch-agent` | 🏦 投资银行 | 投标书制作(Comps/Precedents/LBO→PPT) | ✅ 已安装 |
| 2 | `market-researcher` | 📈 股权研究 | 行业概览→竞争格局→可比公司→研报 | ✅ 已安装 |
| 3 | `earnings-reviewer` | 📈 股权研究 | 财报审阅→模型更新→研报草稿 | ✅ 已安装 |
| 4 | **`meeting-prep-agent`** | 💼 财富管理 | 客户会前简报(持仓/市场/议程) | ✅ 已安装 |
| 5 | `model-builder` | 🔍 金融分析 | DCF/LBO/三表/Comps→Excel建模 | ✅ 已安装 |
| 6 | **`gl-reconciler`** | 🔍 金融分析 | 总账↔明细账差异追踪→异常报告 | ✅ 已安装 |
| 7 | **`kyc-screener`** | 🔍 金融分析 | KYC开户尽调→规则引擎→风险评级 | ✅ 已安装 |
| 8 | **`valuation-reviewer`** | 💰 私募股权 | GP估值审阅→瀑布计算→LP报告 | ✅ 已安装 |
| 9 | **`month-end-closer`** | 🔍 金融分析 | 月结：应计/滚动/差异分析→结账包 | ✅ 已安装 |
| 10 | **`statement-auditor`** | 💰 私募股权 | LP报表审计→NAV勾稽→签批建议 | ✅ 已安装 |

**粗体** = 本次新增的7个模板

## ⚠️ 数据源提示（重要）

**10个中文Agent模板**（pitch-agent/gl-reconciler等）→ 已适配Hermes数据源（Tushare MCP / us-stock-data / sec-filings / 腾讯财经 / AKShare），可直接使用。

**66个垂直技能**（3-statement-model/comps-analysis等）→ 纯方法论框架，不含Hermes数据源映射。需要你自己在使用时把原文的"CapIQ MCP / FactSet MCP"替换成实际可用的数据源（Tushare / yfinance / 腾讯财经等）。或者等Keke提供Claude API Key后，用Claude原生跑这些技能效果最好（Claude天然适配原版CapIQ/SEC指令）。

**一句话：10个模板开箱即用，66个框架需要搭数据桥。**

## 如何使用

每个模板都对应一个独立的Hermes Skill，加载方式：

```bash
# 加载对应的skill后按工作流执行
skill_view(name='pitch-agent')         # 投行投标书
skill_view(name='market-researcher')   # 行业研究
skill_view(name='earnings-reviewer')   # 财报审阅
skill_view(name='meeting-prep-agent')  # 客户简报
skill_view(name='model-builder')       # 估值建模
skill_view(name='gl-reconciler')       # 总账对账
skill_view(name='kyc-screener')        # 客户尽调
skill_view(name='valuation-reviewer')  # 私募估值
skill_view(name='month-end-closer')    # 月结
skill_view(name='statement-auditor')   # 报表审计
```

## 核心技能适配（4个基础框架）

### 1️⃣ 可比公司分析 (Comps)
- 目标：同业估值对比→Excel输出
- 步骤：确定可比群 → 收集经营/估值指标 → 计算统计基准
- 数据源：Tushare MCP / us-stock-data / 汇率

### 2️⃣ DCF估值模型
- 目标：现金流折现→内在价值
- 步骤：数据采集 → 收入/利润预测 → FCF → WACC → 终值 → 敏感性矩阵
- 原则：公式不硬编码，每步确认，5×5敏感性

### 3️⃣ 盈利分析 (Earnings Review)
- 目标：财报超/不及预期判断
- 步骤：数据收集 → 超预期分析 → 分部拆解 → 指引分析 → 论点更新
- 数据源：SEC EDGAR / yfinance / 巨潮 / Tushare report_rc

### 4️⃣ 行业概览 (Sector Overview)
- 目标：行业全景+竞争格局
- 步骤：定义范围 → 市场规模(TAM/CAGR) → 关键趋势 → 竞争格局 → 估值背景 → 投资启示

## 数据源统一规范

**A股：** 腾讯财经(实时) > Tushare MCP(财务) > 同花顺 > 通达信
**美股：** Finnhub > yfinance(需隧道) > Alpha Vantage(国内直连) > SEC EDGAR
**汇率：** exchangerate-api 或 中国银行中间价

## 安装路径
- 完整仓库: `~/financial-services/`
- 10个Agent源文件: `~/financial-services/plugins/agent-plugins/`
- 垂直插件: `~/financial-services/plugins/vertical-plugins/`
- Hermes Skills: `~/.hermes/skills/financial/`
