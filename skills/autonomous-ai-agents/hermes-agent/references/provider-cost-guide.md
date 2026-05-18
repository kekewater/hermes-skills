# Provider Cost Guide & Selection Strategy

> Last updated: 2026-05-16 (based on Keke's confirmed preferences)
> 
> This reference helps decide *which provider/model to use for which task* given cost and capability tradeoffs.

## Available Providers (Keke's Account)

| Provider | Model(s) | Cost | Status |
|----------|----------|------|--------|
| DeepSeek | V4 Flash | **Free** (no per-token charge) | ✅ Primary chat model |
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano | Pay-per-token (see below) | ✅ Configured, billing active |
| OpenAI | gpt-image-1.5, gpt-image-2, gpt-image-1 | Pay-per-image | ✅ Configured, billing active |
| DashScope (阿里) | qwen2.5-vl-72b-instruct | Free tier | ✅ Vision/backup |
| Tavily | Web search API | Free 1000/mo | ✅ Web search |
| OpenRouter | Various | Pass-through | ✅ Backup provider |

## OpenAI Pricing (for cost decisions)

### Chat Models (per 1M tokens)

| Model | Input | Output | Use When |
|-------|-------|--------|----------|
| **gpt-4o-mini** | $0.15 (¥1.1) | $0.60 (¥4.4) | DeepSeek fails / needs OpenAI compatibility |
| gpt-4.1-nano | $0.10 (¥0.7) | $0.40 (¥2.9) | Cheapest OpenAI option |
| gpt-4.1-mini | $0.40 (¥1.6) | $1.60 (¥6.4) | Better reasoning than mini |
| **gpt-4o** | $2.50 (¥18) | $10.00 (¥73) | Highest quality, expensive — only for critical tasks |
| gpt-4.1 | $2.00 (¥8) | $8.00 (¥32) | Similar to 4o, slightly cheaper |

### Image Generation (per image)

| Model | Cost/Image | Notes |
|-------|-----------|-------|
| **gpt-image-1.5** | **$0.009 (¥0.06)** | ✅ Best value — ~110 images per $1 |
| gpt-image-1 | ~$0.025 (¥0.18) | Older, more expensive |
| gpt-image-2 | ~$0.02-0.05 (est.) | Latest quality, ✅ handles Chinese text well, use low quality for speed |

### TTS (per 1M chars)

| Model | Cost |
|-------|------|
| tts-1 | $15/M chars |
| tts-1-hd | $30/M chars |

### Whisper (per minute)

| Model | Cost |
|-------|------|
| whisper-1 | $0.006/min |

## Decision Rules (Keke's Explicit Preferences)

### Rule 1: Default to DeepSeek
**Chat, analysis, coding, reading, writing → use DeepSeek V4 Flash**
- It's free, fast, and handles 95%+ of tasks well
- No need to burn OpenAI credits on routine work

### Rule 2: OpenAI for Image Generation Only
**"省着点花" — Always ask before generating:**
- `gpt-image-1.5` at ¥0.06/image is the default choice
- Only generate when Keke explicitly says "生成" or "做个图"
- Do NOT pre-generate images proactively

### Rule 3: OpenAI Chat as Emergency Backup
Use gpt-4o-mini (cheapest) when:
- DeepSeek gives wrong/incomplete results on a specific task
- Task requires OpenAI-specific compatibility (e.g., function calling quirks)
- User explicitly asks to use GPT

Use gpt-4o (expensive) only when:
- User explicitly requests highest quality
- Task justifies the premium (complex analysis, code review, etc.)

### Rule 4: Resource Consumption Must Be Approved
**Any operation that costs money must be pre-approved by Keke.**
This covers: image generation, paid API calls, publishing content to platforms, etc.
Exception: routine DeepSeek chat (free) and Tavily search (free tier) do not need approval.

## Testing a New Key

When Keke provides a new API key:

```bash
# 1. Save to ~/.openai/api_key + ~/.hermes/.env
echo "sk-proj-..." > ~/.openai/api_key
chmod 600 ~/.openai/api_key
sed -i 's|^OPENAI_API_KEY=.*|OPENAI_API_KEY=sk-proj-...|' ~/.hermes/.env

# 2. Update config.yaml provider section
# Edit ~/.hermes/config.yaml → add/modify openai provider

# 3. Test with cheapest model
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'

# 4. Also test list-models (free operation)
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Key Format Identification

| Prefix | Type | Notes |
|--------|------|-------|
| `sk-proj-` | Project key | Standard, has billing attached |
| `sk-svcacct-` | Service account key | Organization-level, may or may not have billing |
| `sk-` (bare) | Legacy user key | Older format, still works |
