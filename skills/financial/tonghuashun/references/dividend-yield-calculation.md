# 股息率计算规范

## 核心原则

中国 A 股上市公司通常**一年分多次红**（常见上半年+下半年各一次），计算股息率必须使用 **近12个月的已实施分红总和**，而不是仅使用最近一次分红。

## 计算方法

```
全年每股分红(DPS) = 近2次已实施分红（每10股之和）÷ 10
股息率 = DPS ÷ 当前股价 × 100%
```

## 为什么不能用单次分红

错误示例（用户指出前的代码）：
```
只用最近一次: 每10股10.13元 → DPS=1.013元 → 股息率=1.013/37.90=2.67% ❌
```

正确计算：
```
近两次实施: 20.00 + 10.13 = 30.13元/10股 → DPS=3.013元 → 股息率=3.013/37.90=7.95% ✅
```

银行股股息率通常在 5%-8%，2.67% 明显偏低，这就是信号。

## 实现代码（add_dividend_yield 函数）

```python
impl = df[df['进度']=='实施']
total_per_10 = 0
count = 0
for _, row in impl.iterrows():
    d = float(row['派息']) if row['派息'] else 0
    total_per_10 += d
    count += 1
    if count >= 2:  # 最近2次已实施分红（覆盖~12个月）
        break
dps = total_per_10 / 10.0
dividend_yield = round(dps / price * 100, 3)
```

## 数据来源

- **分红数据**: AKShare `stock_history_dividend_detail(symbol=code)`
- **股价数据**: iFinD HTTP API `cmd_history_quotation`（优先）或 AKShare `stock_zh_a_spot()`
- 分红数据按 `公告日期` 倒序排列，`iloc[0]` 是最新一条

## 字段说明（返回给用户的 JSON）

| 字段 | 类型 | 说明 |
|------|------|------|
| `dividend_yield` | float | 股息率(%)，基于近12个月已实施分红 |
| `dividend_dps` | float | 每股全年分红(元) |
| `dividend_per_10` | float | 每10股全年分红合计(元) |
| `dividend_plan_per_10` | float or null | 预案分红(每10股)，尚未实施 |

## 注意事项

1. 刚上市不足1年的股票没有完整分红历史，返回 None
2. 有些公司一年只分一次红，此时最近1次就是全年
3. 取2次是通用策略：一年2次的公司覆盖全年，一年1次的公司覆盖最近+再往前一次（偏保守）
4. 历史分红 ≠ 未来分红承诺，需要在输出中注明
