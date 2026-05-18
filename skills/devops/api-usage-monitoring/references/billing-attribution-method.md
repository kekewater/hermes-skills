# Billing Attribution: Chat vs Cron Cost Breakdown

## Method

Cross-reference DeepSeek's billing CSV (from platform.deepseek.com → 用量管理 → 导出) with Hermes' local session database (`~/.hermes/state.db`) to attribute costs to different workflows.

## Data Sources

### 1. DeepSeek Billing CSV (cost-YYYY-M.csv)
Columns: `user_id, utc_date, model, wallet_type, cost, currency`
- Daily total cost per model
- Amount file: `user_id, utc_date, model, api_key_name, api_key, type, price, amount`
- Types: `output_tokens`, `input_cache_hit_tokens`, `input_cache_miss_tokens`, `request_count`

### 2. Hermes Sessions Table (`state.db → sessions`)
Key columns: `id, source, started_at, input_tokens, output_tokens, cache_read_tokens`
- `source = 'cron'` or id starts with `cron_` → cron job
- Everything else → chat (weixin/cli)
- `input_tokens` = user + tool input, `output_tokens` = assistant responses
- Tip: Today's session may not have token data until it ends

## Calculation Formula

Total Cost = (cache_hit × ¥0.02/M) + (cache_miss × ¥1.0/M) + (output × ¥2.0/M)

Cache hit rate is ~94.3% — most input tokens hit cache and cost nearly nothing.

## Chat vs Cron Attribution

```python
chat_tokens = sum(sessions where source != 'cron' and not id.startswith('cron_'))
cron_tokens = sum(sessions where source == 'cron' or id.startswith('cron_'))
chat_ratio = chat_tokens / total_tokens
cron_ratio = cron_tokens / total_tokens
chat_cost = total_cost × chat_ratio
cron_cost = total_cost × cron_ratio
```

Known limitation: session DB's `input_tokens` only counts user+tool input, NOT system prompt overhead (memory, persona, skills list). System prompt (~7.2K tokens/turn) is almost entirely cached (¥0.02/M). So the ratio is approximate but directionally accurate.

## Stable Period Estimates (2026-05-15~16)

| Category | Daily Tokens | Daily Cost | % |
|----------|-------------|-----------|--|
| Chat (weixin/cli) | ~3.8M | ¥15.24 | 84% |
| Cron (8 background jobs) | ~730K | ¥2.92 | 16% |

Cron breakdown for ~¥2.92/day:
- Notification checks (28x/day before optimize): ~¥1.20
- Novel (11:00 daily): ~¥0.50
- Reading/GitHub/CS50 (08-10:00): ~¥0.30 each
- Backup/monitoring: ~¥0.12

## Cost Drivers (from ¥69.57 over 5 days)

| Component | Tokens | Rate | Cost | % |
|-----------|--------|------|------|---|
| Cache hit (94.3%) | 777M | ¥0.02/M | ¥15.55 | 22% |
| Cache miss | 47M | ¥1.0/M | ¥46.96 | 68% |
| Output | 3.5M | ¥2.0/M | ¥7.06 | 10% |

68% of cost comes from **cache miss input** — unique user messages, tool call results, file reads. These can't be cached.

## Optimization Levers

1. **Reduce notification check frequency** → halves cron cost (already done)
2. **Limit large file reads** — reading 204KB files costs ~136K tokens
3. **Shorter tool outputs** — restrict terminal command output length
4. **Compress memory** — smaller memory = smaller system prompt (currently ~7.5K chars)

## Key Insight

Chat is 84% of cost; cron is 16%. Optimize chat patterns for real savings. Cron optimization is helpful but marginal — notification check optimization saved ~¥1.50/day out of ~¥18/day total.
