# OpenAI API from China via Proxy

> Last updated: 2026-05-17

## The Problem

From mainland China, OpenAI API is not directly accessible. We have a proxy tunnel through Tencent Cloud Silicon Valley (port 8889 → tinyproxy on 43.159.133.35:8888).

## What Works and What Doesn't

### ✅ curl (works)
```bash
curl -s -x http://127.0.0.1:8889 https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### ✅ Python `requests` with explicit proxy (works)
```python
import requests
resp = requests.post(
    'https://api.openai.com/v1/images/generations',
    headers={'Authorization': f'Bearer {api_key}'},
    json={...},
    proxies={'https': 'http://127.0.0.1:8889', 'http': 'http://127.0.0.1:8889'},
    timeout=120
)
```

### ❌ Python `openai` library (does NOT use proxy env vars)
The `openai` Python package (v2.37.0) does not respect `HTTP_PROXY`/`HTTPS_PROXY` environment variables. Setting them has no effect. The `image_generate` builtin tool fails with "Connection error" because it uses this library internally.

### ❌ `http_proxy` env var (not picked up by openai package)
```bash
export http_proxy=http://127.0.0.1:8889
export https_proxy=http://127.0.0.1:8889
# These do NOT make the openai Python library route through the proxy
```

## Workaround

For any OpenAI API call from China, use `requests` (not the `openai` library) and pass `proxies=` explicitly:

```python
proxies = {
    'http': 'http://127.0.0.1:8889',
    'https': 'http://127.0.0.1:8889'
}
response = requests.post(url, headers=headers, json=payload, proxies=proxies, timeout=120)
```

## Image Generation Specifics

OpenAI `gpt-image-2` works well from China via proxy:
- Model: `gpt-image-2` (not `dall-e-3` or `dall-e-2`)
- Quality tiers: `low` (~15s, cheapest), `medium` (~40s), `high` (~2min)
- Chinese text rendering: excellent — handles complex infographics with Chinese text clearly
- Output: base64 PNG in response JSON
- The `image_generate` builtin tool will fail — use the requests workaround instead
