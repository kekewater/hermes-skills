# 13F 季度对比分析模式

## 用途

实时获取一家机构（如伯克希尔）最新两期13F持仓，做环比对比分析（增持/减持/新进/清仓），生成中文分析表格，可用于GPT做图。

## 什么时候用

- 用户问"XX公司最新持仓有什么变化"
- 13F截止日（2/14, 5/15, 8/14, 11/14）过后，需要第一时间抓最新数据
- 做投资组合分析、基金跟踪

## 工作流

### Step 1: 确认最新两期13F

```python
from edgar import set_identity, Company
set_identity("YourApp (email@example.com)")

company = Company("BRK")  # 或 CIK
filings = list(company.get_filings(form="13F-HR"))
latest = filings[0]
prev = filings[1]

print(f"最新: {latest.filing_date}  数据截止: {latest.period_of_report}")
print(f"上期: {prev.filing_date}  数据截止: {prev.period_of_report}")
```

**注意**：`get_filings()` 返回的是生成器，要 `list()` 转列表再取索引。

### Step 2: 解析两期持仓

```python
import re
from collections import defaultdict

def parse_holdings(filing):
    txt = filing.full_text_submission()
    infotables = re.findall(r'<infoTable>.*?</infoTable>', txt, re.DOTALL)
    holdings = defaultdict(lambda: {'value': 0, 'shares': 0})
    
    for table in infotables:
        name = re.search(r'<nameOfIssuer>(.*?)</nameOfIssuer>', table)
        value = re.search(r'<value>(.*?)</value>', table)
        shares = re.search(r'<sshPrnamt>(.*?)</sshPrnamt>', table)
        if name and value and shares:
            n = name.group(1).strip()
            v = int(value.group(1))
            s = int(shares.group(1).replace(',', ''))
            holdings[n]['value'] += v
            holdings[n]['shares'] += s
    
    total = sum(h['value'] for h in holdings.values())
    sorted_h = sorted(holdings.items(), key=lambda x: -x[1]['value'])
    return sorted_h, total

latest_h, latest_total = parse_holdings(latest)
prev_h, prev_total = parse_holdings(prev)
```

### Step 3: 构建环比对比

```python
prev_dict = {n: d for n, d in prev_h}

print(f"{'股票':<28} {'本期市值($M)':<12} {'占比':<7} {'上期市值($M)':<12} {'变动($M)':<11} {'变动%':<8}")
for name, data in latest_h[:22]:
    cur_val = data['value'] / 1e6
    pct = data['value'] / latest_total * 100
    prev_val = prev_dict.get(name, {}).get('value', 0) / 1e6
    chg = cur_val - prev_val
    chg_pct = f"{(chg/prev_val*100):+.1f}%" if prev_val > 0 else "新进"
    print(f"{name:<28} {cur_val:>10,.0f}  {pct:>5.1f}% {prev_val:>10,.0f}  {chg:>+9,.0f}  {chg_pct:>7}")
```

### Step 4: 行业分布变化

```python
sectors = {
    '金融': ['AMERICAN EXPRESS CO', 'BANK AMERICA CORP', 'CAPITAL ONE FINL CORP', 'ALLY FINL INC', 'MOODYS CORP'],
    '科技': ['APPLE INC', 'ALPHABET INC', 'VERISIGN INC'],
    # ... 按实际情况分类
}
for sector, stocks in sectors.items():
    cur_val = sum(curr_dict.get(s,{}).get('value',0) for s in stocks) / 1e9
    prev_val = sum(prev_dict.get(s,{}).get('value',0) for s in stocks) / 1e9
    print(f"{sector:<12} {cur_val:>10.1f}B {prev_val:>10.1f}B")
```

### Step 5: 输出分析

生成中文分析包含：
1. **整体概览** — 总市值变化、持股数变化
2. **前20持仓对比** — 股票名+最新市值+占比+上期市值+增减金额+变动%
3. **行业分布** — 分行业Q1 vs Q4占比
4. **重大操作** — 买入TOP和新进、减持TOP和清仓
5. **集中度变化** — 前5/前10占比

格式为Markdown表格，可直接复制给GPT做图。

## 关键陷阱

1. **`<value>` 单位** — 2023年前后不一致！2013~2022年是千美元，2023年起是实际美元。如果最新数据对比看起来误差1000倍，需要做归一化处理。

2. **券商合并** — 伯克希尔旗下多家保险子公司各自申报13F，同一股票可能有多个 `<infoTable>` 条目（如GEICO, National Indemnity等），必须按 `nameOfIssuer` 合并。

3. **edgartools超时** — `full_text_submission()` 可能下载2MB+文件。提前执行：
   ```python
   from edgar import configure_http
   configure_http(timeout=120.0)
   ```

4. **13F截止日** — Q1→5/15, Q2→8/14, Q3→11/14, Q4→2/14。截止当天或第二天提交的文件最晚到美东时间下午5点，北京时间就是第二天早上。

5. **排名变化 ≠ 持仓变化** — 股价波动也会改变市值排名。务必对比 `shares` 数量来判断是主动买卖还是被动价格波动。

## 输出示例（伯克希尔 Q1 2026）

详见 `/home/ubuntu/伯克希尔_Q1_2026_持仓分析.md`（完整中文分析+数据表格）
