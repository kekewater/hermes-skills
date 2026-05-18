# Image Generation Proxy Setup

## Problem

The `image_generate` tool fails with "Connection error" or "OpenAI image generation failed" when running behind a proxy (common on China-based servers).

**Root cause**: The Python `openai` library does **not** pick up `http_proxy` / `https_proxy` environment variables. It makes direct connections, which fail when the server can't reach OpenAI directly.

**Symptoms**:
```
image_generate → error: "Connection error" (openai Python library)
curl → works fine with -x http://127.0.0.1:8889
```

## Fix

The `image_gen` toolset is configured through `config.yaml` but the actual API call goes through the Python `openai` library which ignores proxy env vars. There are two workarounds:

### Workaround 1: requests.post() with explicit proxies (recommended)

Use `requests` library directly with the `proxies` parameter:

```python
import requests, base64, json

resp = requests.post(
    'https://api.openai.com/v1/images/generations',
    headers={
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'gpt-image-2',       # NOT dall-e-3
        'prompt': 'your prompt here',
        'n': 1,
        'size': '1536x1024',           # landscape
        'quality': 'low'               # low/medium/high — low saves tokens
    },
    proxies={'https': 'http://127.0.0.1:8889'},  # ← critical
    timeout=120
)

data = resp.json()
b64 = data['data'][0]['b64_json']
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
```

### Workaround 2: curl via shell

```bash
curl -s -x http://127.0.0.1:8889 -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"prompt","n":1,"size":"1536x1024","quality":"low"}'
```

## Model Notes

| Model | Available? | Notes |
|-------|-----------|-------|
| `gpt-image-2` (low/medium/high) | ✅ Yes | OpenAI's latest image model. Different from DALL-E. |
| `dall-e-3` | ❌ Not found | Returns "model does not exist" on this key. |
| `dall-e-2` | ❌ Not found | Same error. |

The `gpt-image-2` model supports three quality tiers passed as `quality` parameter (not part of model name):
- `low`: fastest, ~15s, ~158 output tokens
- `medium`: ~40s (default)
- `high`: ~2min, highest fidelity

## Size Options

| Aspect | Size | Use case |
|--------|------|----------|
| Landscape | `1536x1024` | Infographics, reports, wide layouts |
| Square | `1024x1024` | General purpose |
| Portrait | `1024x1536` | Posters, mobile-friendly |

## Chinese Text Rendering

`gpt-image-2` handles Chinese text **well** — significantly better than diffusion-based models (通义万相, Stable Diffusion) which produce garbled Chinese characters. You can write detailed Chinese descriptions in the prompt and the model will render them legibly.

## Resource Management

- Approx **661 tokens** per image (1536x1024, `quality: low`)
- Must ask user for permission before generating (resource consumption rule)
- Check `OPENAI_API_KEY` in `.env` — this key works but API billing status is not visible via API (session key only)
