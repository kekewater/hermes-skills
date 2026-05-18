# 13F 多季度持仓对比工作流

> 用于分析机构投资者（如伯克希尔）连续季度的持仓变化。
> 工作流在 2026-05-16 伯克希尔 Q1 2026 13F 分析中验证通过。

## 核心流程

```
Step 1: 获取最新和前一期两份13F
Step 2: 解析XML infoTable → 合并同名股票
Step 3: 交叉比对两份持仓
Step 4: 计算变动（金额/股本/百分比）
Step 5: 统计分析（行业分布/集中度/增减持TOP）
Step 6: 输出结构化对比表
```

## Step-by-Step 代码模板

### 1. 获取两个季度的13F

```python
from edgar import set_identity, Company

set_identity('YourApp (email@example.com)')
company = Company('BRK')

all_filings = list(company.get_filings(form='13F-HR'))
latest = all_filings[0]          # 最新
previous = all_filings[1]        # 上一期

print(f"最新提交: {latest.filing_date}  数据截至: {latest.period_of_report}")
print(f"上期提交: {previous.filing_date}  数据截至: {previous.period_of_report}")
```

### 2. 解析持仓

```python
import re
from collections import defaultdict

def parse_holdings(filing):
    """解析单份13F的infoTable,返回排序后的持仓列表和总值"""
    txt = filing.full_text_submission()
    infotables = re.findall(r'<infoTable>.*?</infoTable>', txt, re.DOTALL)
    
    holdings = defaultdict(lambda: {'value': 0, 'shares': 0})
    
    for table in infotables:
        name = re.search(r'<nameOfIssuer>(.*?)</nameOfIssuer>', table)
        val = re.search(r'<value>(.*?)</value>', table)
        shares = re.search(r'<sshPrnamt>(.*?)</sshPrnamt>', table)
        
        if name and val and shares:
            n = name.group(1).strip()
            v = int(val.group(1))
            s = int(shares.group(1).replace(',', ''))
            holdings[n]['value'] += v
            holdings[n]['shares'] += s
    
    total = sum(h['value'] for h in holdings.values())
    sorted_h = sorted(holdings.items(), key=lambda x: -x[1]['value'])
    return sorted_h, total
```

### 3. 交叉比对

```python
curr_h, curr_total = parse_holdings(latest)
prev_h, prev_total = parse_holdings(previous)

prev_dict = {n: d for n, d in prev_h}
curr_dict = {n: d for n, d in curr_h}

# 逐个对比输出
print(f"{'Name':<30} {'Current($M)':<14} {'Prev($M)':<14} {'Change($M)':<12} {'Change%':<10} {'Shares':<12}")
print('-'*92)

for name, cd in curr_h:
    vm = cd['value'] / 1e6
    pv = prev_dict.get(name, {}).get('value', 0) / 1e6
    chg = vm - pv
    chg_pct = f"{(chg/pv*100):+.1f}%" if pv > 0 else "NEW"
    print(f"{name:<30} {vm:>10,.0f}  {pv:>10,.0f}  {chg:>+9,.0f}  {chg_pct:>8}  {cd['shares']:>10,}")
```

### 4. 识别增减持

```python
# 找出所有股票（含已清仓的）
all_stocks = set(list(curr_dict.keys()) + list(prev_dict.keys()))
changes = []

for name in all_stocks:
    cv = curr_dict.get(name, {}).get('value', 0) / 1e6
    pv = prev_dict.get(name, {}).get('value', 0) / 1e6
    cs = curr_dict.get(name, {}).get('shares', 0)
    ps = prev_dict.get(name, {}).get('shares', 0)
    changes.append((name, cv-pv, cs-ps, cv, cs, pv, ps))

changes.sort(key=lambda x: -x[1])

# 增持TOP
for item in [c for c in changes if c[1] > 0][:10]:
    print(f"+ {item[0]}: +${item[1]:.0f}M, shares: {item[2]:+}")

# 减持TOP（只显示有意义的大仓位）
for item in [c for c in changes if c[1] < 0 and c[5] > 100][:10]:
    print(f"- {item[0]}: {item[1]:+.0f}M, shares: {item[2]:+}")
```

### 5. 行业分类

```python
# 简单行业分类字典（以伯克希尔为例）
sectors = {
    '科技': ['APPLE INC', 'ALPHABET INC', 'VERISIGN INC'],
    '金融': ['AMERICAN EXPRESS CO', 'BANK AMERICA CORP', 'CAPITAL ONE FINL CORP', 'ALLY FINL INC', 'MOODYS CORP'],
    '消费': ['COCA COLA CO', 'KRAFT HEINZ CO', 'NEW YORK TIMES CO MTN BE', 'LIBERTY LIVE HOLDINGS INC'],
    '能源': ['CHEVRON CORPORATION', 'OCCIDENTAL PETE CORP'],
    '保险': ['CHUBB LTD SWITZ'],
    '医疗/其他': ['DAVITA INC', 'KROGER CO'],
    '交通': ['DELTA AIR LINES INC'],
    '传媒': ['SIRIUSXM HOLDINGS INC'],
}

for sector, stocks in sectors.items():
    c_val = sum(curr_dict.get(s, {}).get('value', 0) for s in stocks) / 1e9
    p_val = sum(prev_dict.get(s, {}).get('value', 0) for s in stocks) / 1e9
    print(f"{sector}: Q1=${c_val:.1f}B ({c_val/(curr_total/1e9)*100:.1f}%)"
          f" | Q4=${p_val:.1f}B ({p_val/(prev_total/1e9)*100:.1f}%)")
```

### 6. 集中度分析

```python
c_top5_val = sum(d['value'] for _, d in curr_h[:5])
p_top5_val = sum(prev_dict.get(n, {}).get('value', 0) for n, _ in curr_h[:5])
c_top10_val = sum(d['value'] for _, d in curr_h[:10])

print(f"前5占比: Q1 {c_top5_val/curr_total*100:.1f}% | Q4 {p_top5_val/prev_total*100:.1f}%")
print(f"持股数: Q1 {len(curr_h)} | Q4 {len(prev_h)}")
```

## 输出示例（伯克希尔Q1 2026）

```
最新13F: 2026-05-15  数据截至: 2026-03-31
上期13F: 2026-02-17  数据截至: 2025-12-31

总市值: Q1 $263.10B (26只) | Q4 $274.16B (39只) | 变化: -$11.06B

Top 5 占比: Q1 67.1% | Q4 63.6% (更集中)
Top 10 占比: Q1 91.1% | Q4 77.1%

增持TOP: Chevron +$17.5B(新进), Alphabet +$11.0B(+198%), Chubb +$11.2B(新进)
减持TOP: AmEx -$10.2B(-18%), BAC -$3.4B(-12%)

行业变化: 金融37%→32%, 科技25%→29%, 能源4%→13%
```

## 注意事项

1. **伯克希尔13F特殊处理**：旗下多家保险子公司各自申报，同名股票需合并
2. **单位归一化**：2023年前XML的`<value>`是千美元，2023年起是实际美元
3. **纯文本格式**：2013年前的13F无infoTable，需正则从文本表格解析
4. **SEC限频**：edgartools默认9 req/s，批量处理建议用`time.sleep(2.5)`
5. **User-Agent**：`set_identity()`必须在任何请求前调用
