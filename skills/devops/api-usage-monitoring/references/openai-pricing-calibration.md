# OpenAI定价校准 — 从真实账单推导

## 重要原则

> **不要用网上查到的定价（OpenAI官网/社区论坛/第三方博客）。**
> Keke明确说过网上价格"五花八门的"不准确。
> **永远使用用户实际账单数据反推。**

## 数据来源

Keke从 platform.openai.com → Usage → Export → 导出两份数据：

| 文件 | 内容 | 
|------|------|
| Dashboard页面截图 | $3.38 (90天可能花费), $16.62 (贷方余额), $20.00 (总额度) |
| `completions_usage_2026-04-17_2026-05-17.csv` | 每日API完成调用明细(token粒度) |

## 推算过程

### 基础数字

- 总费用: **$3.38** (90天仪表盘)
- 总请求: **40次** (CSV计数: 37生图 + 3文本)
- 有活动的天数: **2天** (2026-05-16测试日, 2026-05-17日报测试日)
- 余额: **$16.62**

### 模型分布

| 模型 | 请求数 | 用途 | Output图像tokens |
|------|--------|------|-----------------|
| `gpt-image-2` | 20 | 日报图+测试 | 21,800 |
| `gpt-image-1.5-2025-12-16` | 15 | 质量对比测试(5L+5M+5H) | 67,488 |
| `gpt-image-1-2025-04-23` | 2 | 测试 | 10,400 |
| `gpt-4o-mini-2024-07-18` | 3 | 文本测试(几乎免费) | — |

### 各档价格估算

**平均每张生图: $3.38/37 = $0.0914**

从已知测试模式推算各档：
- 5月16日 (质量测试): gpt-image-2 3次(L+M+H各1) + gpt-image-1.5 15次(5L+5M+5H) + gpt-image-1 2次
- 5月17日 (日报测试): gpt-image-2 17次(全部Low)

估算各档价格(基于Token消耗量比例, L:M:H≈1:2.5:5):

| 模型 | Low | Medium | High |
|------|-----|--------|------|
| gpt-image-2 | **~$0.055** | ~$0.137 | ~$0.274 |
| gpt-image-1.5 | ~$0.073 | ~$0.183 | ~$0.365 |

**日报使用gpt-image-2 Low, 约$0.055/张**

### 脚本中的实现

在 `monitor_usage.py` 中：

```python
def _get_image_pricing():
    """从日志读取价格基准，无记录时用默认估算"""
    data = _load_data()
    for d in reversed(data):
        if d.get("type") == "openai_pricing_baseline":
            daily_est = d.get("daily_report_est_per_image", 0.055)
            return {
                "low": daily_est,
                "medium": round(daily_est * 2.5, 3),
                "high": round(daily_est * 5, 3),
                "default": d.get("avg_per_image", 0.09)
            }
    # 无账单记录时用默认估算
    return {"low": 0.055, "medium": 0.137, "high": 0.274, "default": 0.09}
```

定价基准存在 `usage_log.json` 的 `openai_pricing_baseline` 记录中。

## 校准周期

Keke每周导出一次最新账单，覆盖旧的 `openai_pricing_baseline` 记录即可更新定价。
