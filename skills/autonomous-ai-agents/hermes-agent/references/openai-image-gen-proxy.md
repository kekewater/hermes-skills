# OpenAI Image Generation via Proxy (Workaround)

## Problem

`image_generate` tool fails with "Connection error" when using OpenAI `gpt-image-2` model. The Python `openai` library doesn't pick up proxy environment variables (`http_proxy`/`https_proxy`), so direct API calls through the tool fail.

## Root Cause

The server is in China and must route OpenAI API calls through the Silicon Valley proxy tunnel (port 8889). The `openai` Python SDK's `httpx` transport doesn't respect system proxy env vars in Hermes' runtime context.

## Solution: requests library with explicit proxy

Use `requests.post()` with a `proxies` dict instead of the `openai` Python SDK:

```python
import base64, requests

resp = requests.post(
    'https://api.openai.com/v1/images/generations',
    headers={
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'gpt-image-2',
        'prompt': 'Your prompt here — Chinese text works great',
        'n': 1,
        'size': '1536x1024',  # landscape
        'quality': 'low'      # low/medium/high
    },
    proxies={'https': 'http://127.0.0.1:8889', 'http': 'http://127.0.0.1:8889'},
    timeout=120
)

data = resp.json()
if 'data' in data:
    b64 = data['data'][0]['b64_json']
    with open('/path/to/save.png', 'wb') as f:
        f.write(base64.b64decode(b64))
```

## Key Parameters

| Param | Options | Notes |
|-------|---------|-------|
| `model` | `gpt-image-2` | Latest OpenAI image model (not DALL-E 3) |
| `quality` | `low` / `medium` / `high` | low ≈15s, medium ≈40s, high ≈2min |
| `size` | `1024x1024` / `1536x1024` / `1024x1536` | square / landscape / portrait |
| `n` | 1 (only option with proxy) | Must be 1 |

## Cost

- ~500-700 input tokens + ~150-200 output tokens per image (with `low` quality)
- Each call costs roughly $0.02-0.03 USD
- OpenAI balance: ~$16.62 remaining (as of May 17, 2026)

## ⚠️ Must ask before generating

Per Keke's resource consumption rule: **any paid API operation (image generation, etc.) requires user approval first.** Always ask "Can I generate this?" before calling the API.

## Prompt Tips for Chinese Infographics

- Chinese prompts work very well — no need to translate to English
- Be very detailed about the layout, section ordering, color scheme
- Mention "dark navy background with gold accents" for premium financial feel
- Non-standard fonts/glyphs may appear differently — keep it simple
- The model renders Chinese text accurately (unlike DALL-E or FAL which garble it)
