# 数据源审计报告 (2026-05-17)

> **⚠️ 2026-05-18重要更新：本文件部分内容已过时。以下变更适用于日报数据采集：**
> 
> | 项目 | 旧（本文件） | 新（当前使用） |
> |------|-------------|---------------|
> | 标普500 | usSPY(ETF) | **usINX**(指数) |
> | 纳指100 | usQQQ(ETF) | **usNDX**(指数) |
> | 美股个股 | usAAPL(苹果) | **usNVDA**(英伟达,市值最大) |
> | 原油 | usUSO(WTI ETF) | **web_search**(ICE布油) |
> | 黄金 | XAU+汇率/黄金ETF | **Au99.99**(上金所SGE) |
> | 港股个股 | 无 | hk00700(腾讯)+hk09988(阿里) |
> | 白银 | 无 | ak.spot_silver_benchmark_sge() |
> | 比特币 | 无 | web_search/Finnhub |
>
> 详细更新见 `SKILL.md` 中的"数据采集流程"和"五大板块"部分。
> 具体bug排查见 `references/brent-oil-data-source-bug.md`。

---

测试环境：本地服务器 (proxy: 127.0.0.1:8889)
测试方法：curl直连 + Python (AKShare环境下清掉代理env)

---