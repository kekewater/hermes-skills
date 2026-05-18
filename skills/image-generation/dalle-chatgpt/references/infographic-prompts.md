# Financial Infographic Prompts for GPT-image Model

> ⚠️ **DALL·E 3 retired March 4, 2026.** ChatGPT now uses **GPT-image** series models.
> All references to "DALL·E 3" below are legacy — the actual model served is GPT-image.

Tested prompt patterns for generating financial/earnings infographics via GPT-image model inside ChatGPT web.

## User's Preferred Style

- **Background**: Dark navy/slate (`#0f172a` style)
- **Accents**: Gold (#fbbf24), amber, warm metallic
- **Vibe**: Bloomberg terminal meets high-end annual report
- **Layout**: Clean data visualization, bar charts, key metrics highlighted
- **Branding**: Company name prominent at top

## The Berkshire Pattern (Tested ✅)

This approach was used successfully for Berkshire Hathaway 2026 Q1 earnings. The key insight: **paste the raw data as-is and append a simple instruction**. Don't reformat into a "prompt" — just paste + "请生成一张信息图".

### What Worked

User sent markdown-formatted financial data (table with metrics, balance sheet, segment results, key takeaways) and said "生成一张伯克希尔季报摘要图". This one-sentence instruction + raw data produced a good result.

### What Did NOT Work

- ❌ Sending the prompt through `generate.py` script with DALL·E-only URL → got 512x512 avatars instead of the real image
- ❌ Mentioning "DALL·E 3" explicitly — the model name is now GPT-image; just say "生成一张图片"
- ❌ Over-engineering the prompt into a complex DALL·E-style description → trust ChatGPT to interpret the data

### Guidance

- **Paste the raw data as-is**: Don't reformat, don't summarize, don't "optimize for DALL·E"
- **Keep the instruction simple**: "请根据以上数据生成一张信息图风格的中文图片" is enough
- **Do NOT mention DALL·E**: The model is now GPT-image; ChatGPT will use it automatically
- **Numbers in tables**: Markdown tables render fine in the prompt — let ChatGPT decide how to visualize them
