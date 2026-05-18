# monitor_usage.py 核心逻辑变更记录

## 2026-05-18 修复

### 修复1：当期时间窗口
**问题**：`get_all_stats()` 中 `block = (now.hour // 6) * 6` 取当前所在6小时区块的起点。06:34时 block=6，period_label="06:00-12:00"显示的是未来6小时。

**修复**：改为 `now - datetime.timedelta(hours=6)`，period_label="前6小时(00:36-06:36)"，始终显示过去6小时。

### 修复2：DeepSeek消耗计算
**问题**：Hermes核心层不自动调用 `log_deepseek()`，`usage_log.json` 中没有任何 `type="llm_chat"` 条目，因此今日和当期累计始终显示0。

**修复**：新增 `_calc_ds_by_balance(since_time)` 函数，通过比较同一时间范围内的 `ds_balance_snapshot` 余额差值推算消耗。

原理：
```
delta = 时间范围内最早快照的余额 - 最新快照的余额
```

注意：余额降低可能是充值+消耗的综合结果。如果充了钱，delta可能为负或偏小。函数中 `if delta < 0: delta = 0` 处理了充值情况。

### 关键代码位置
- `_calc_ds_by_balance(since_time)` — 约第169行
- `get_all_stats()` 中调用逻辑 — 约第200行
- `generate_report()` 中调用 `get_all_stats()` — 约第370行

### 测试验证
```bash
python3 ~/.hermes/scripts/monitor_usage.py report
```
输出中"当期(前6小时)"和"今日累计"的DeepSeek行应有具体数字而非"无消耗"。
