# Cron Token Consumption Estimation

## Method

Each cron job consumes tokens per run. To estimate total daily/weekly cost:

### Cost Components per Run

| Component | Estimation | Notes |
|-----------|-----------|-------|
| System prompt | ~8-15K input tokens | Persona + memory + user profile + tool descriptions |
| Task prompt | len(prompt_text) ÷ 2 chars/token | From job config |
| Output | ~2-10K output tokens | Depends on task complexity |
| Tool calls | Variable | Each tool call + result adds to context |

### DeepSeek Pricing (confirmed from Keke's CSV, 2026-05-17)

| Item | Price |
|------|-------|
| Input cache miss | ¥1.0/百万tokens |
| Input cache hit | ¥0.02/百万tokens |
| Output | ¥2.0/百万tokens |
| Cache hit rate | ~94.3% |

### Rule of Thumb

For cron jobs on DeepSeek V4 Flash:
- **Light task** (backup, simple check): ~5-8K tokens/run → ~¥0.05
- **Medium task** (social check, reading): ~12-20K tokens/run → ~¥0.20
- **Heavy task** (novel writing, market report): ~25-33K tokens/run → ~¥0.56

For notification checks: these are the most frequent cron and dominate cron costs.
- Every-30min schedule: 28 runs/day × ~8K tokens = ~224K/day → ¥1.94/day
- Hourly schedule: 13 runs/day × ~8K tokens = ~104K/day → ¥0.90/day

### Example: Full Day Cost Breakdown (2026-05-17)

| Time | Task | Est. Tokens | Est. Cost |
|:---|:---|:---:|:---:|
| 06:30 | 投资日报 (含GPT生图$0.055) | ~33K | ¥0.56 + $0.055 |
| 08:00 | 读书《证券分析》 | ~21K | ¥0.28 |
| 09:00 | GitHub学习 | ~19K | ¥0.24 |
| 10:00 | CS50课程 | ~19K | ¥0.24 |
| 11:00 | 小说连载 | ~25K | ¥0.40 |
| 12:00 | 三平台社交 | ~16K | ¥0.20 |
| 13x/day | 通知检查(每小时) | ~104K | ¥0.90 |
| 18:00 | 用量监控 | ~10K | ¥0.08 |
| 20:00 | 晚间汇报 | ~20K | ¥0.30 |
| **Total** | | **~267K** | **¥3.30 + $0.055** |

Compare to Keke's actual daily DeepSeek cost of ¥13.91 — cron jobs account for only ~24% of consumption. The bulk is real-time chat.
