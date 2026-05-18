# Cloudflare Bypass Through Proxy Tunnel

## Problem

When accessing Cloudflare-protected websites (e.g., `chatgpt.com`, `platform.openai.com`) from a **datacenter VPS IP** (Vultr, DigitalOcean, AWS), curl returns **HTTP 403** — Cloudflare's JS Challenge blocks non-browser traffic.

## Root Cause

Cloudflare identifies datacenter IP ranges and serves a JavaScript challenge page. Simple HTTP clients like `curl` or `requests` cannot execute JavaScript, so they never get through.

## Solution: Playwright (Headless Chrome)

Playwright's headless Chromium can execute Cloudflare's JavaScript challenges and get through.

### Prerequisites

Node.js with Playwright installed:
```bash
npm install playwright
npx playwright install chromium
```

### Test Script

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    proxy: { server: 'http://127.0.0.1:8888' }  // your proxy endpoint
  });
  const page = await browser.newPage({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const resp = await page.goto('https://chatgpt.com', { 
    waitUntil: 'domcontentloaded', timeout: 30000 
  });
  console.log('Status:', resp?.status());
  console.log('Title:', await page.title());
  await browser.close();
})();
```

### Results (Vultr Singapore IP)

| Client | chatgpt.com | api.openai.com | auth0.openai.com |
|--------|-------------|----------------|-------------------|
| curl | 403 (blocked) | 401 (needs key) | 302 (redirect) |
| Playwright | **200** ✅ | N/A | N/A |

`api.openai.com` works fine with curl — only the web UI (`chatgpt.com`, `platform.openai.com`) is behind Cloudflare JS challenges.

## Limitations

- Playwright requires **Node.js + Chromium** (~500MB), not suitable for minimal environments
- Login credentials are needed to go beyond the landing page
- Session cookies expire — may need re-login periodically
- If Cloudflare updates their challenge mechanism, Playwright may break
