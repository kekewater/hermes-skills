---
name: dalle-chatgpt
description: Generate images via ChatGPT web interface (GPT-image model, free tier) through US proxy server
category: image-generation
---

# Image Generation via ChatGPT Web (Free Tier — GPT-image Model)

> ⚠️ **DALL·E 3 retired March 4, 2026.** The ChatGPT free tier now uses **GPT-image** series models.
> The skill is named `dalle-chatgpt` for legacy reasons but uses whatever image model ChatGPT serves.

Uses US VPS (66.42.97.175, Los Angeles) + Playwright to login to free ChatGPT and generate images via GPT-image model.

## When to use this skill

- User asks to **generate an image, infographic, chart, or financial visualization**
- User provides data (earnings, stats, tables) and wants a visual summary
- **PREFER this over Python PIL/matplotlib** — user explicitly prefers ChatGPT/DALL·E generated images over programmatic charts. If you use PIL/matplotlib instead, the user will notice and correct you.

## Quick Usage

```bash
python3 /home/ubuntu/.hermes/skills/image-generation/dalle-chatgpt/scripts/generate.py "your text + instruction here"
```

Returns JSON with `success`, `path`, and `dims`. Send the result via `MEDIA:{path}`.

## The Golden Rule: Paste Everything Directly

User's explicit preference: **"直接把给你的指令发给gpt就可以"** — paste the complete data + instruction into ChatGPT in one shot. Don't over-engineer the prompt, don't split into steps, don't write a separate script for each request. Just paste what the user gave you, add a simple "请生成一张信息图" at the end, and let ChatGPT figure it out.

## Prompt Crafting for Financial Infographics

The user prefers a specific style: dark navy/slate background, gold/amber accents, clean data visualization, Bloomberg-terminal meets annual report. See `references/infographic-prompts.md` for tested prompt patterns.

### The Berkshire Pattern (tested, user-approved)

When the user provides financial data (earnings, balance sheet, segment results):

1. **Paste the raw data as-is** from the user's message, don't reformat
2. **Append a simple instruction**: "请根据以上数据生成一张信息图风格的中文图片"
3. **Do NOT mention DALL·E 3 by name** — the model is now GPT-image; just say "生成一张图片"
4. **Key metrics**: Let ChatGPT figure out which numbers to highlight

## US VPS Status (2026-05-17)

**⚠️ KNOWN ISSUE: US VPS 66.42.97.175 is UNREACHABLE (connection timeout)**

As of May 17, 2026, the US VPS at 66.42.97.175 has been unreachable for over 24 hours. This affects:
- ✅ ChatGPT web-based image generation (via Playwright on remote server)
- ✅ SOCKS5 proxy for image API calls
- ✅ All yfinance/Yahoo Finance data queries

**Status:** Connection timed out on SSH. Possible reasons: VPS shut down, IP changed, or network issue.

## OpenAI Image Generation Methods (in priority order)

### Method 1: Direct API via Silicon Valley Proxy (PRIMARY — simplest, 2026-05-17 verified)
**Status: ✅ Works reliably.** The OpenAI API is accessible from China via the Tencent Cloud Silicon Valley proxy tunnel (port 8889).

**Prerequisites:**
- `OPENAI_API_KEY` set in `.env` (sk-proj-... key already exists)
- `openai` Python package installed (`pip install openai`)
- Silicon Valley SSH tunnel active (port 8889 → tinyproxy on 43.159.133.35)

**Python (recommended — use `requests` with explicit proxy, NOT the `openai` library):**
The `openai` Python library does NOT pick up proxy env vars correctly — use `requests` directly instead:
```python
import requests, base64, os

resp = requests.post(
    'https://api.openai.com/v1/images/generations',
    headers={
        'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'gpt-image-2',
        'prompt': '[detailed chinese/en prompt]',
        'n': 1,
        'size': '1536x1024',  # landscape: 1536x1024, square: 1024x1024, portrait: 1024x1536
        'quality': 'low'  # low (~15s) | medium (~40s) | high (~2min)
    },
    proxies={'https': 'http://127.0.0.1:8889', 'http': 'http://127.0.0.1:8889'},
    timeout=120
)

data = resp.json()
if 'data' in data:
    with open('/path/to/output.png', 'wb') as f:
        f.write(base64.b64decode(data['data'][0]['b64_json']))
```

**curl (alternative):**
```bash
curl -s -x http://127.0.0.1:8889 -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"...","n":1,"size":"1536x1024","quality":"low"}' \
  -o /tmp/res.json
python3 -c "import json,base64; d=json.load(open('/tmp/res.json')); open('/tmp/out.png','wb').write(base64.b64decode(d['data'][0]['b64_json']))"
```

**Model info:**
- **`gpt-image-2`** — Current model (NOT DALL-E 3, which is deprecated). Supports low/medium/high quality tiers.
- **Cost:** ~$0.02-0.10/image depending on quality and size. The OpenAI account has ~$16.62 balance (as of May 2026).
- **Chinese text rendering:** Excellent — handles Chinese characters, titles, labels perfectly. Much better than DashScope/通义万相 (which corrupts Chinese text).

**IMPORTANT: Resource consumption rule — must ask Keke before generating.** Every image costs API credits. Never generate without explicit approval.

### Method 2: ChatGPT Web via US VPS Playwright (LEGACY — use Method 1 instead)
The old approach using Vultr VPS (66.42.97.175) + Playwright to login to free ChatGPT. Still works if US VPS is reachable.

### Method 3: OpenAI API via Vultr VPS direct SSH (LEGACY FALLBACK — Vultr Singapore retired)
Previously used when proxy didn't work. Vultr Singapore (45.76.185.1) is now retired. Only useful if Tencent Silicon Valley tunnel is down.

**Alternative: Browser-AI-Bridge (local)** — Runs on China server port 3333, uses Playwright Chrome locally to access ChatGPT web. But requires **Keke to log in once via SSH tunnel** to save ChatGPT cookies. See `references/browser-ai-bridge-setup.md`.

**Not recommended: DashScope/通义万相** — Domestic Chinese API (Alibaba Cloud), no proxy needed. **Critical limitation: diffusion model cannot render Chinese text accurately** — characters will be gibberish (e.g. "科创50" → "利创50", "易方达" → "景方达"). Complete gibberish for titles/data labels. Only usable for visual-only images without text.

**Fallback: Matplotlib/Pillow charts** — For financial data visualization. Use `WenQuanYi Zen Hei` font for Chinese text (Noto Sans CJK SC doesn't resolve in matplotlib — the TTC registers as `Noto Sans CJK JP`, which lacks Simplified Chinese glyph clusters for some use cases; WQY works reliably).

## Infrastructure

- **US VPS**: `66.42.97.175` (Los Angeles, Ubuntu 24.04, 1vCPU/1GB)
- **SOCKS5 Proxy**: `66.42.97.175:1080` (microsocks, systemd auto-restart)
- **Playwright**: Chromium at `/root/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome`
- **ChatGPT Session**: Saved cookies at `/root/.chatgpt_cookies.json` on US server
- **SSH Key**: `/home/ubuntu/.ssh/id_vultr`

## Generation Parameters

- **Prompt**: Chinese or English (Chinese works well for financial data)
- **Wait Time**: ~20-90 seconds per image (free tier is slower; GPT-image model may take longer than old DALL·E)
- **Output**: 1024x1024 or larger PNG (NOT 512x512 — if you get 512x512 you're detecting the wrong element)
- **Limits**: Free ChatGPT allows ~5-10 image generations per day
- **User**: "keke water" (Free plan)

## Implementation Details

### Image Detection Bug (Critical!)

The Playwright script polls for images using `naturalWidth > 100` — this is TOO LOW. ChatGPT's UI has 512x512 avatar icons and thumbnails that get detected before the real generated image appears. **Always filter for `>= 800` pixels on both width and height**, and prefer images with `oaidalle` or long URLs.

### The Right Approach (vs the Script)

The `generate.py` script has known limitations (old DALL·E 3 URL, low image threshold). When the script fails to produce a proper image:

1. SSH into the US VPS directly
2. Write a fresh Playwright script that:
   - Goes to `https://chatgpt.com/` (NOT the old DALL·E GPT URL)
   - Pastes the full data into a new chat
   - Waits for images >= 800x800
3. SCP the result back

### How the Script Works

1. Connects to US server via SSH
2. Launches Playwright with ChatGPT cookies from `/root/.chatgpt_cookies.json`
3. Navigates to `https://chatgpt.com/` (NOT `.../g/g-pmuQfob8d-image-generator` — that URL was for the retired DALL·E 3 GPT)
4. Fills the prompt textarea and clicks Send
5. Polls for images (must filter for >= 800x800, NOT > 100 or > 200)
6. Downloads via `page.evaluate(fetch(...))` to get image as base64 through the authenticated session
7. SCPs the image file back to local cache directory

## Cookie Refresh

If cookies expire (login fails), the script will error. To refresh:

```bash
ssh -i /home/ubuntu/.ssh/id_vultr root@66.42.97.175
# Then re-login via Playwright: python3 to chatgpt.com/auth/login
# Fill email (1351712821@qq.com), click Continue
# Ask user for verification code from email
# Fill code, click submit
# Save cookies: copy /tmp/chatgpt_cookies.json to /root/.chatgpt_cookies.json
```

## User's Image Generation Stack (2026)

User now prefers **Flux** for image generation, and uses **Seedance/即梦AI/豆包** on their phone to create images (not through me). My avatar "墨渊·Flux" (机械义眼赛博国风) was made by them via Seedance.

| Tool | User Role | How I Use It |
|:----|:---------|:------------|
| **Flux (FLUX.2 Pro/Schnell)** | 首选文生图工具 | 通过我生成提示词，用户复制到 Flux 出图 |
| **ChatGPT DALL·E (GPT-image)** | 备选（免费版） | 通过 `scripts/generate.py` 用 Playwright 操控，或通过 **browser-ai-bridge** REST API（见 `references/browser-ai-bridge-setup.md`） |
| **Seedance/即梦AI/豆包** | 用户手机上用 | 用户直接在手机操作，不上服务器 |
| **DashScope 通义万相** | 我的视觉分析 | 看图（auxiliary.vision），不用来生图 |

See `references/flux-prompts.md` for full Flux prompt guide and "墨渊" character style references.

## Related Files

- `scripts/generate.py` — The generation script (call this, but beware its limitations)
- `references/infographic-prompts.md` — Tested prompt templates for financial infographics
- `references/flux-prompts.md` — Flux prompt guide and 墨渊 character style
- `references/browser-ai-bridge-setup.md` — Local REST API server for ChatGPT web access (alternative to direct Playwright)
