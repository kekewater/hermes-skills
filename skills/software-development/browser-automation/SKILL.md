---
name: browser-automation
description: >-
  Automated browser workflows using Playwright Python: login automation, Cloudflare-bypassed web scraping,
  cookie session management, and consent-banner handling. Use when a task requires programmatic browser
  interaction (form filling, authenticated scraping, screenshot capture) on headless servers.
triggers:
  - "Login to {website}"
  - "Automate browser to {action}"
  - "Bypass Cloudflare to {do_something}"
  - "Scrape {website} with authentication"
  - "Save browser cookies for session reuse"
tags: [playwright, chrome, headless, cloudflare, login-automation, cookies]
---

# Browser Automation (Playwright Python)

Use Playwright Python for headless browser automation. This is **more reliable than Camofox** on low-memory VPS (1GB RAM) — Camofox server mode + Chrome frequently freezes the Node process and consumes all available memory.

## Quick Start

### 1. Install Playwright Python + Chromium

```bash
# Install the Python package
pip3 install playwright

# Install Chromium browser via npx (Python's playwright install may expect different versions)
npx playwright install --with-deps chromium
```

### 2. Find Chrome Binary Path

```bash
ls /root/.cache/ms-playwright/chromium-*/chrome-linux*/chrome
# Example: /root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome
```

Always specify `executable_path` when launching — the pip-installed playwright may not find the npm-installed chromium binary automatically.

### 3. Playwright Stealth Configuration (Cloudflare Bypass)

Cloudflare's JS challenges identify headless Chrome by several fingerprints. Override these **before navigation**:

```python
# Anti-detection: must be set BEFORE any page navigation
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => false});
""")

# User agent: use a modern Chrome UA string
context = await browser.new_context(
    viewport={'width': 1280, 'height': 800},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
)
```

**Critical**: `add_init_script` must be called **before** `page.goto()`. If called after navigation, the override won't apply.

**IP region matters**: Even with stealth, Cloudflare is harder to bypass from Chinese datacenter IPs. Use a **US-based VPS** (Los Angeles works well) — the same Playwright script that gets Cloudflare-blocked from China works fine from a US IP.

**Camofox vs Playwright**: Camofox (`npx camofox-browser`) has stronger fingerprint spoofing and **can** bypass Cloudflare from any IP, but on a 1GB VPS it repeatedly freezes (Chrome process + Node.js = OOM). Playwright Python is more resource-stable on low-memory VPS but only works from friendly-region IPs.

### 4. Cookie Persistence (Session Reuse)

Save cookies after login to reuse across browser sessions:

```python
import json

# Save
cookies = await context.cookies()
json.dump(cookies, open('/tmp/cookies.json', 'w'))

# Load later
with open('/tmp/cookies.json') as f:
    cookies = json.load(f)
await context.add_cookies(cookies)
```

This avoids re-authentication on every script run. Cookies typically last hours to days depending on the site.

### 5. Handling Email Verification Codes

Some sites (ChatGPT, many banks) send a one-time code to the user's email after password entry:

```python
# After email + submit, the page shows a "Code" input
await page.fill('input:not([type="hidden"])', '123456')
await page.locator('button[type="submit"]').first.click()
```

Strategy: have the script **pause** (via `input()` or wait) and **tell the user to send the code**, then inject it dynamically. Alternatively, for known codes, hardcode them — but plan for expiry.

### 6. Basic Headless Launch

```python
import asyncio
from playwright.async_api import async_playwright

CHROME_PATH = '/root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        await page.goto('https://example.com', timeout=60000)
        print(await page.title())
        await browser.close()

asyncio.run(main())
```

## Login Automation Patterns

### Credential Entry

```python
await page.fill('input[name="username"]', 'user@example.com')
await page.fill('input[name="password"]', 'my_password')
```

To find input field selectors, use:
```python
await page.evaluate("""Array.from(document.querySelectorAll('input')).map(i => ({name: i.name, type: i.type, placeholder: i.placeholder}))""")
```

### Form Submission (Bypass Overlay)

When cookie consent banners or privacy overlays intercept pointer events, `page.click()` hangs endlessly. **Use JavaScript evaluation instead:**

```python
# Preferred: bypasses overlay interception
await page.evaluate("""document.querySelector('button[type="submit"]').click()""")
```

Or dismiss the overlay first:
```python
consent_btn = page.locator('button:has-text("I Understand")')
if await consent_btn.count() > 0:
    await consent_btn.click()
    await asyncio.sleep(1)
```

### Checking Current State

```python
url = page.url
title = await page.title()
```

### Saving Cookies for API Reuse

```python
cookies = await page.context.cookies()
cookie_str = '; '.join([f'{c["name"]}={c["value"]}' for c in cookies])
# Save to file for use with curl:
with open('/tmp/cookies.txt', 'w') as f:
    f.write(cookie_str)
```

## Cloudflare Bypass Strategy

Cloudflare Turnstile is almost impossible to bypass with headless Playwright locally (proxy/server IP matters):

1. **Use a VPS in a friendly region** (Singapore/US) — Cloudflare challenges are lighter from non-Chinese IPs
2. **Camofox browser** (`npx camofox-browser`) CAN bypass Cloudflare but is **unreliable on 1GB VPS** — the Chrome process freezes the Node.js server, requiring `pkill -9 -f camofox` and `pkill -9 -f chrome` to recover
3. **Playwright Python is more stable** for 1GB VPS — consumes fewer resources than Camofox
4. After login, save cookies and use them with `curl --cookie cookies.txt` for subsequent API calls

## Cookie Consent Banners

Many SaaS login pages (Vultr, etc.) have privacy consent overlays from vendors like Ketch/lanyard. These intercept pointer events. **Always plan for this**:

1. Try dismissing the consent banner first (`button:has-text("I Understand")`)
2. If dismissal fails or the overlay still intercepts, use `page.evaluate()` for clicks
3. For form filling (`page.fill`), consent banners generally don't block input fields — only clicks

## Quota and Cost Awareness (User Preference)

**IMPORTANT**: This user (Keke/江玉婷) has explicitly stated "先别乱生成哈，我让你生成你再生成" — do NOT trigger any paid/quota-limited action (AI generation, API calls that cost tokens, SMS verification) without first confirming with the user. 

Rules:
- **Free, unlimited actions** (browsing, reading, navigating) → OK to do autonomously
- **Limited quota actions** (DALL·E images, AI PPT generation, SMS verification code sends, API calls that cost money) → **MUST ask user first** before proceeding
- **Login-related actions** (typing credentials, clicking "get code") → OK since these don't consume user's paid quota, only their time

When in doubt, ask: "I need to do X, which will consume Y resource. OK to proceed?"

## Account Security Awareness (User Preference)

**CRITICAL**: The user is very concerned about getting accounts **blocked/banned** from services. After repeated failed login attempts, they explicitly said "别试千问了，又要被封" (don't try 千问 anymore, it'll get blocked/limited).

Rules:
- **Detect when you're being rate-limited or blocked**: Watch for messages like "获取次数已达上限", "系统繁忙", CAPTCHA/slider challenges that can't be solved automatically
- **Limit retries**: If a login attempt fails 2-3 times (wrong code, rate limit, CAPTCHA), do NOT keep retrying. Switch methods (SMS → QR → alt service) or ask the user what to do
- **Don't "burn" a service**: If a service has security restrictions (SMS rate limits, CAPTCHA escalation), further attempts make things worse. Know when to switch to a different service
- **Prefer the path of least resistance**: If service A is blocked and service B is available, switch to B rather than fighting A's security. Example from this session: 千问 hit SMS rate limit → switched to Baidu Wenku → succeeded on first attempt
- **QR code scanning with wrong app**: Before asking user to scan a QR code, verify they have the correct mobile app installed (e.g., 千问QR needs 千问APP, Baidu QR needs 百度App). Generic scanners will not work and will waste the user's time
- **When all approaches fail on one service**: Offer to generate the content locally with code (e.g., python-pptx for PPTs) instead of burning more accounts on web services

When a login approach fails repeatedly, report: "X is blocked/limited on this service. Switch to Y? Or I can generate locally without logging in."

## Pitfalls

### Camofox on Low-Memory VPS
- **Symptoms**: Health endpoint times out, SSH disconnects, `browserConnected: false`
- **Root cause**: Chrome process consumes 200-300MB RAM on a 1GB VPS; combined with Camofox Node.js process, the VPS runs out of memory
- **Fix**: Hard kill (`pkill -9 -f camofox; pkill -9 -f chrome`). Wait for memory to recover (`free -m` shows ~600MB available)
- **Alternative**: Use Playwright Python directly instead of Camofox

### Shell Quoting in Evaluated JavaScript
When embedding Python scripts in SSH heredocs, JavaScript strings with quotes break easily. Use triple-quotes in Python:
```python
# Works in heredocs:
await page.evaluate("""document.querySelector('button[type="submit"]').click()""")
```

### SCP Instead of Inline Scripts
For complex Python scripts, write the file locally and `scp` it to the server instead of embedding in SSH:
```bash
scp /tmp/myscript.py user@host:/tmp/myscript.py
ssh user@host "python3 /tmp/myscript.py"
```

### Playwright Version Mismatch
The pip-installed `playwright` Python package and npm-installed `playwright` browser binaries can have version mismatches. Install chromium via npm (`npx playwright install chromium`) and always use `executable_path` when launching.

## Vultr Login Reference

See `references/vultr-login.md` for the specific Vultr login automation pattern.

## Chinese Web Login Modals

See `references/chinese-login-modals.md` for patterns to handle Chinese web services (百度文库, 千问, etc.) that use cross-origin iframe login modals with SMS verification or QR code authentication.
