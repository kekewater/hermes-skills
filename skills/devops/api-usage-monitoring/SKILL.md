---
name: api-usage-monitoring
description: 跨平台API用量监控 — DeepSeek余额查询、OpenAI生图追踪、本地日志、定时微信报告。支持多provider用量分平台显示。
---

# API用量监控

跨平台追踪API消耗、查询余额、生成格式化报告发微信。

## 监控脚本

脚本路径：`~/.hermes/scripts/monitor_usage.py`

```bash
python3 ~/.hermes/scripts/monitor_usage.py report    # 微信友好纯文本报告（推荐）
python3 ~/.hermes/scripts/monitor_usage.py status     # JSON完整状态
python3 ~/.hermes/scripts/monitor_usage.py summary 7  # 近7日汇总
python3 ~/.hermes/scripts/monitor_usage.py deepseek   # 仅DeepSeek余额
```

## 支持的平台

| 平台 | 余额查询 | 方式 | 真实成本 | 状态 |
|------|---------|------|---------|------|
| 🔵 DeepSeek | ✅ API直查 `/user/balance` | API Key即可 | **不是免费的！** 日均¥13.91(2026-05-13~17 CSV) | 实时余额+趋势推算 |
| 🟢 OpenAI | ⚠️ 基准+追踪估算法 | 手动登录一次平台存基准，后续自动减本地消耗 | $3.38/90天 | 见下文"余额基准" |
| 🟣 其他 | 有公开API则可扩展 | 需为每个provider实现 | — | — |

## OpenAI余额估算（余额基准法）

OpenAI账单API不能用API Key查，因此采用 **"一次基准 + 持续追踪"** 方案：

### 原理

1. 用户手动登录 `platform.openai.com` 看一眼剩多少（如$16.62）
2. 将余额写入 `usage_log.json` 作为 `balance_snapshot` 记录：
   ```json
   {"time": "2026-05-17T12:44:00", "type": "balance_snapshot", 
    "platform": "openai", "remaining": 16.62, "total_credit": 20.00}
   ```
3. 后续每次报告用 `_get_openai_remaining()` 函数自动计算：
   ```
   current_remaining = baseline_remaining - sum(consumption_after_baseline)
   ```
4. 用户只需要**登一次**，之后全部自动

### 设置命令

```bash
# 写入余额基准（manual_snapshot.py 或直接写库）
python3 -c "
import json
LOG = '~/.hermes/usage_log.json'
# 删旧的+写新的
data = [d for d in json.load(open(LOG)) if d.get('type') != 'balance_snapshot']
data.append({'time': '2026-05-17T12:44:00', 'type': 'balance_snapshot',
             'platform': 'openai', 'remaining': 16.62, 'total_credit': 20.00})
json.dump(data, open(LOG,'w'), ensure_ascii=False, indent=2)
"
```

### 注意事项
- 基准只需要设一次，除非有额外消耗不经过本地记账（比如用户自己在platform上投喂图片）
- 如果余额不准了，重新登录平台查一次，写入新基准覆盖旧的

## DeepSeek用量查询API限制

DeepSeek没有提供可通过API Key查询用量/历史的公开端点（2026-05-17实测）：

| 端点 | 结果 | 说明 |
|------|------|------|
| `GET /user/balance` | ✅ 200 (可查余额) | 唯一可用的查询端点 |
| `GET /v1/usage` | ❌ 403 `Missing scopes: api.usage.read` | 端点存在但API Key无权限 |
| `GET /usage` | ❌ 404 | 不存在 |
| `GET /billing/usage` | ❌ 404 | 不存在 |
| `GET /usage_records` | ❌ 404 | 不存在 |
| `GET /transactions` | ❌ 404 | 不存在 |

用量(usage)端点返回403而非404说明DeepSeek在API层面预留了用量查询功能，但默认API Key没有 `api.usage.read` scope。可能需要特定角色或组织级权限才能开启。

结论：跟OpenAI一样，用量历史只能通过网页 dashboard (platform.deepseek.com) 查看。本地只能通过余额快照趋势法估算日均消耗。

## OpenAI账单API限制（历史参考）

OpenAI的账单/用量接口 **不能用普通API Key查询**（已证实，2026-05-17实测）：

```
GET /v1/dashboard/billing/subscription  → 需要session key
GET /v1/dashboard/billing/usage         → 需要session key
```

返回：`"must be made with a session key (that is, it can only be made from the browser). You made it with the following key type: secret."`

与DeepSeek不同——DeepSeek有公开的 `/user/balance` 端点可API Key查询。

详见 `references/openai-billing-limitation.md`。

### DeepSeek 实际成本（重要！）

**DeepSeek V4 Flash 不是免费的！** 每次对话、每个任务都消耗账户余额。

### 真实定价（2026-05-17从Keke导出的CSV确认）

| 计费项 | 价格 | 说明 |
|-------|------|------|
| Output tokens | **¥2.0/百万tokens** | 主要成本项 |
| Input cache miss | **¥1.0/百万tokens** | 首次或长上下文命中 |
| Input cache hit | **¥0.02/百万tokens** | 重复上下文极便宜 |
| 缓存命中率 | **~94.3%** | 大部分input走缓存 |

**5日真实账本**（2026-05-13 ~ 2026-05-17，来自platform.deepseek.com导出CSV）：
| 日期 | 费用 | 请求 | Output tokens |
|------|------|------|--------------|
| 05-13 | ¥7.58 | 735 | 456,669 |
| 05-14 | ¥17.10 | 2,159 | 912,716 |
| 05-15 | ¥16.00 | 1,858 | 766,647 |
| 05-16 | ¥20.31 | 2,426 | 920,498 |
| 05-17 | ¥8.58 | 944 | 475,424 |
| **合计** | **¥69.57** | **8,122** | **3,531,954** |

- **日均：¥13.91/天**（之前估算的¥2.20严重低估！）
- **余额约撑9天**（¥129~130 ÷ ¥13.91）
- 对比GPT-4o-mini：¥4.10/百万输出tokens vs DeepSeek ¥2.00

### 缓存命中率意义
94.3%缓存命中意味着每100万input tokens中只有5.7万扣费
（¥0.057），其余94.3万走缓存几乎不花钱（¥0.0189）。若没有缓存，日均成本会
是现在的约17倍。

### v1/usage 端点发现
`GET https://api.deepseek.com/v1/usage` 返回 **403**（非404）：
```
"Missing scopes: api.usage.read"
```
说明DeepSeek在API层面预留了用量查询功能，但默认API Key没有此scope。可能需特定角色或组织级权限。详见 `references/deepseek-v1-usage-discovery.md`。
详见 `references/deepseek-caching-mechanics.md`（Keke研究的DeepSeek前缀缓存机制、64-token粒度、前4K黄金区域、优化策略）。

### 当日消耗计算（余额快照法 — 2026-05-18修复）

**重要：Hermes 核心层不会自动调用 `log_deepseek()` 函数。** 每次API调用的token消耗不会被记录到 `usage_log.json`。因此：

#### 原方案（已作废）
~~`get_all_stats()` 按时间过滤 `usage_log.json`，找出 `type="llm_chat"` 的条目统计token和费用。~~

Hermes不会自动写llm_chat条目，所以原方案永远显示0。

#### 新方案（余额快照法）
`get_all_stats()` 中的 `_calc_ds_by_balance(since_time)` 函数从 `ds_balance_snapshot` 的余额差值推断消耗。

原理：
```
今日消耗 = 今日第一笔快照余额 - 当前余额
前6小时消耗 = 6小时前最近快照余额 - 当前余额
```

每次 `generate_report()` 运行时会自动调用 `check_deepseek_balance()` 并写入一条 `ds_balance_snapshot`。下次运行时就能算出差值。

#### 时间窗口
- **当期**：改为 `前6小时(XX:XX-XX:XX)`（原来是未来6小时，已修复）
- **今日累计**：当天00:00至今
- **全部累计**：全部日志条目（不含balance差值的估算部分）

### CSV历史数据注入

除了实时快照，还可以从用户导出的CSV一次性写入历史数据：

将 `历史(5日¥13.91/天)` 作为 `ds_period_snapshot` 写入日志，让报告立刻显示准确的日均消耗。

报告显示效果：
```
  🔵 DeepSeek: ¥130.38
     日均 ¥13.91/天 · 缓存命中94.3%
     余额约撑 9 天
```

## 报告输出示例（用户确认的最终版 — 2026-05-17）

```
📊 用量监控报告
🕐 05-17 14:10

━━━ 账户余额 ━━━
  🔵 DeepSeek: ¥129.54
     日均 ¥13.91/天 · 缓存命中94.3%
     余额约撑 9 天
  🟢 OpenAI:    $16.62

━━━ 当期(前6小时(00:36-06:36)) ━━━
  🔵 DeepSeek:
      Token: 93,407,252
      费用: ¥8.58
  🟢 OpenAI:
      无消耗

━━━ 今日累计 ━━━
  🔵 DeepSeek:
      Token: 93,407,252
      费用: ¥8.58
      余额: ¥120.96
  🟢 OpenAI:
      生图: 7次
      费用: $0.3850 (¥2.63)
      余额: $16.62

━━━ 全部累计 ━━━
  🔵 DeepSeek:
      Token: 827,758,155
      费用: ¥69.57
  🟢 OpenAI:
      生图: 7次
      费用: $0.3850 (¥2.63)
      余额: $16.62

━━━ 历史累计(含未记录部分) ━━━
  🟢 OpenAI:    40次 · $3.38 (90天账单)
      日均 $0.0376 · 余额$16.62

⏰ 下次报告：18:00
```

要求：
- **DeepSeek和OpenAI必须分两栏显示**（用户明确要求"分开"）
- 时间维度：当期6小时 / 今日累计 / 全部累计
- 余额部分显示日均消耗和预估剩余天数
- DeepSeek费用用CNY（¥），OpenAI费用用USD（$）

## 定时报告

⚠️ **语言要求**：所有交付到微信（deliver: weixin）的cron输出必须是中文。对于cron任务中由模型生成自由文本（而非运行确定性脚本）的情况，prompt必须**明确写"用中文输出"**，否则DeepSeek等模型默认输出英文。（2026-05-18教训：三平台通知检查cron因prompt未明确指定语言，输出英文被Keke指出。）

- 频率：每6小时（00:00 / 06:00 / 12:00 / 18:00）
- 交付：微信
- cron名称："用量监控每6小时"
- 执行的命令：`python3 ~/.hermes/scripts/monitor_usage.py report`
- 代理：需硅谷隧道8889端口访问DeepSeek API（硅谷SSH隧道→43.159.133.35:8888）

## 本地日志

所有用量记录存于 `~/.hermes/usage_log.json`（JSON数组，按时间排序）。

### 记录方法

```python
from monitor_usage import log_gpt_image, log_deepseek

# GPT生图记录
log_gpt_image(size="1024x1536", quality="low", count=1)

# DeepSeek token记录
log_deepseek(prompt_tokens=100, completion_tokens=50, model="deepseek-v4-flash")
```

## 关键问题与修复

### 当期时间标签（2026-05-18修复）

**Bug**：`get_all_stats()` 中 `block = (now.hour // 6) * 6` 把 `period_start` 设为当前块起点（如06:00），显示"06:00-12:00"（未来6小时）。

**修复**：改为 `now - datetime.timedelta(hours=6)`，标签改为"前6小时(00:36-06:36)"，始终显示过去6小时的数据。

### DeepSeek消耗显示0（2026-05-18修复）

**Bug**：Hermes 核心层从不自动调用 `log_deepseek()`，导致 `usage_log.json` 中没有任何 `llm_chat` 记录，"今日累计"和"当期"的DeepSeek消耗一直显示0。

**修复**：新增 `_calc_ds_by_balance(since_time)` 函数，从 `ds_balance_snapshot` 的快照余额差值推算消耗：

```python
# 原理：取 since_time 之后的第一笔快照和最新快照
# delta = oldest_balance - newest_balance
# tokens_est = consumption_cny / 2 * 1,000,000 (按¥2/百万output估算)
```

在 `get_all_stats()` 中，如果日志条目没有 `llm_chat` 记录（ds_cost_cny=0），自动用余额快照差值补上。
在 `generate_report()` 中，每次查询余额后先写快照 `_record_ds_snapshot()`，后续计算基于最新快照。

**验证方法**：
- 余额快照链：`06:00=¥105.81 → 06:36(当前)=¥105.44` → 当期消耗 ¥0.37
- 今日首笔快照 `00:00=¥106.94` → 今日累计消耗 ¥1.50

## 汇率

USD→CNY = 6.83（2026-05-17实测exchangerate-api.com）

## 常见坑

1. **OpenAI billing不能API查** — 别浪费时间调 billing dashboard 接口。平台余额必须手动登录查看。
2. **DeepSeek balance API可用** — `GET https://api.deepseek.com/user/balance` 带Authorization header即可。
3. **报告要分平台显示** — 用户明确要求DeepSeek和OpenAI分两栏，不能混在一起。
4. **proxy环境变量** — DeepSeek API在国内走Vultr 8889代理；OpenAI API直接Vultr VPS直连(无代理)。
5. **金额格式化** — 美元< $0.001用6位小数，¥用CNY_RATE换算。
6. **"当期"不要显示未来时间** — 不要用 `(now.hour//6)*6` 算当前块起点，那会显示未来6小时。用 `now - 6h`。
7. **今日消耗不要依赖llm_chat日志** — Hermes不会自动写llm_chat日志。今日/当期的DeepSeek消耗必须从余额快照差值计算（`_calc_ds_by_balance()`）。
8. **余额快照链需要≥2笔才能算差值** — 如果只有1笔有效快照在时间区间内，`_calc_ds_by_balance()` 返回None。此时今日/当期会显示0。写快照 (`_record_ds_snapshot()`) 在 `generate_report()` 开头执行，确保当前快照存在。
